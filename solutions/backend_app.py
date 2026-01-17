#!/usr/bin/env python3
"""
SOLUTION: Backend Service with OpenTelemetry Tracing
=====================================================
This is the complete solution for the backend service instrumentation.
Students should try to complete the TODO file first before looking here!
"""

import os
import time
import random
import requests
from flask import Flask, jsonify

# =============================================================================
# SOLUTION: OpenTelemetry imports
# =============================================================================
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

# Configuration
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:8082")
SERVICE_NAME = os.getenv("SERVICE_NAME", "backend")

# =============================================================================
# SOLUTION: Configure the Tracer Provider
# =============================================================================

resource = Resource.create({
    "service.name": SERVICE_NAME,
    "service.version": "1.0.0",
})

provider = TracerProvider(resource=resource)

exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/traces"
)

provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# =============================================================================
# SOLUTION: Instrument Flask and Requests
# =============================================================================

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


# =============================================================================
# Helper Functions with Custom Spans
# =============================================================================

def simulate_processing(operation_name):
    """Simulate some business logic processing with custom span."""
    with tracer.start_as_current_span(f"process_{operation_name}") as span:
        span.set_attribute("operation", operation_name)
        delay = random.uniform(0.05, 0.15)
        span.set_attribute("simulated_delay_ms", delay * 1000)
        time.sleep(delay)


def validate_data(data, data_type):
    """Simulate data validation with custom span."""
    with tracer.start_as_current_span("validate_data") as span:
        span.set_attribute("data_type", data_type)
        delay = random.uniform(0.01, 0.05)
        span.set_attribute("validation_time_ms", delay * 1000)
        time.sleep(delay)
        span.set_attribute("validation_result", "success")
        return True


# =============================================================================
# Routes
# =============================================================================

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME
    })


@app.route("/users")
def get_users():
    """Get users from Database Service with business logic."""
    with tracer.start_as_current_span("get_users_business_logic") as span:
        span.set_attribute("database_service.url", DATABASE_SERVICE_URL)

        try:
            # Simulate business logic processing
            simulate_processing("user_lookup")

            # Call database service
            response = requests.get(f"{DATABASE_SERVICE_URL}/db/users", timeout=10)
            span.set_attribute("db_response.status_code", response.status_code)
            response.raise_for_status()
            data = response.json()

            # Validate data
            validate_data(data, "users")

            user_count = len(data.get("users", []))
            span.set_attribute("users.count", user_count)

            return jsonify({
                "source": SERVICE_NAME,
                "count": user_count,
                "data": data
            })
        except requests.RequestException as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            return jsonify({
                "error": str(e),
                "service": SERVICE_NAME
            }), 500


@app.route("/orders")
def get_orders():
    """Get orders from Database Service."""
    with tracer.start_as_current_span("get_orders_business_logic") as span:
        try:
            simulate_processing("order_lookup")

            response = requests.get(f"{DATABASE_SERVICE_URL}/db/orders", timeout=10)
            span.set_attribute("db_response.status_code", response.status_code)
            response.raise_for_status()
            data = response.json()

            validate_data(data, "orders")

            # Simulate order total calculation
            with tracer.start_as_current_span("calculate_order_totals") as calc_span:
                delay = random.uniform(0.02, 0.08)
                calc_span.set_attribute("calculation_time_ms", delay * 1000)
                time.sleep(delay)

            return jsonify({
                "source": SERVICE_NAME,
                "count": len(data.get("orders", [])),
                "data": data
            })
        except requests.RequestException as e:
            span.set_attribute("error", True)
            return jsonify({
                "error": str(e),
                "service": SERVICE_NAME
            }), 500


@app.route("/products")
def get_products():
    """Get products from Database Service."""
    with tracer.start_as_current_span("get_products_business_logic") as span:
        try:
            simulate_processing("product_lookup")

            response = requests.get(f"{DATABASE_SERVICE_URL}/db/products", timeout=10)
            span.set_attribute("db_response.status_code", response.status_code)
            response.raise_for_status()
            data = response.json()

            validate_data(data, "products")

            # Simulate inventory check
            with tracer.start_as_current_span("check_inventory") as inv_span:
                delay = random.uniform(0.03, 0.1)
                inv_span.set_attribute("inventory_check_time_ms", delay * 1000)
                time.sleep(delay)

            return jsonify({
                "source": SERVICE_NAME,
                "count": len(data.get("products", [])),
                "data": data
            })
        except requests.RequestException as e:
            span.set_attribute("error", True)
            return jsonify({
                "error": str(e),
                "service": SERVICE_NAME
            }), 500


@app.route("/")
def index():
    """Root endpoint with service info."""
    return jsonify({
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "endpoints": [
            "GET /health",
            "GET /users",
            "GET /orders",
            "GET /products"
        ]
    })


if __name__ == "__main__":
    print(f"Starting {SERVICE_NAME} on port 8081...")
    print(f"Database Service URL: {DATABASE_SERVICE_URL}")
    app.run(host="0.0.0.0", port=8081, debug=False)
