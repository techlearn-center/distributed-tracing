#!/usr/bin/env python3
"""
Backend Service - Business Logic Layer
=======================================
This service handles business logic and calls the Database Service.

YOUR TASK: Add OpenTelemetry tracing to this service!

Endpoints:
  GET /health    - Health check
  GET /users     - Get users (calls Database Service)
  GET /orders    - Get orders (calls Database Service)
  GET /products  - Get products (calls Database Service)
"""

import os
import time
import random
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:8082")
SERVICE_NAME = os.getenv("SERVICE_NAME", "backend")

# =============================================================================
# TODO 1: Import OpenTelemetry libraries
# =============================================================================
# Uncomment and complete the imports:
#
# from opentelemetry import trace
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.instrumentation.flask import FlaskInstrumentor
# from opentelemetry.instrumentation.requests import RequestsInstrumentor


# =============================================================================
# TODO 2: Configure the Tracer Provider
# =============================================================================
# Set up OpenTelemetry (same pattern as frontend, but with "backend" as service name):
#
# resource = Resource.create({"service.name": SERVICE_NAME})
# provider = TracerProvider(resource=resource)
# exporter = OTLPSpanExporter(
#     endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/traces"
# )
# provider.add_span_processor(BatchSpanProcessor(exporter))
# trace.set_tracer_provider(provider)
# tracer = trace.get_tracer(__name__)


# =============================================================================
# TODO 3: Instrument Flask and Requests
# =============================================================================
# FlaskInstrumentor().instrument_app(app)
# RequestsInstrumentor().instrument()


# =============================================================================
# Helper Functions
# =============================================================================

def simulate_processing(operation_name):
    """
    Simulate some business logic processing.

    TODO 4 (Optional): Wrap this in a custom span
    Example:
        with tracer.start_as_current_span(f"process_{operation_name}") as span:
            span.set_attribute("operation", operation_name)
            delay = random.uniform(0.05, 0.15)
            span.set_attribute("simulated_delay_ms", delay * 1000)
            time.sleep(delay)
    """
    delay = random.uniform(0.05, 0.15)
    time.sleep(delay)


def validate_data(data, data_type):
    """
    Simulate data validation.

    TODO 5 (Optional): Add a validation span
    """
    # Simulate validation processing
    time.sleep(random.uniform(0.01, 0.05))
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
    """
    Get users from Database Service with business logic.
    """
    try:
        # Simulate business logic processing
        simulate_processing("user_lookup")

        # Call database service
        response = requests.get(f"{DATABASE_SERVICE_URL}/db/users", timeout=10)
        response.raise_for_status()
        data = response.json()

        # Validate data
        validate_data(data, "users")

        return jsonify({
            "source": SERVICE_NAME,
            "count": len(data.get("users", [])),
            "data": data
        })
    except requests.RequestException as e:
        return jsonify({
            "error": str(e),
            "service": SERVICE_NAME
        }), 500


@app.route("/orders")
def get_orders():
    """Get orders from Database Service."""
    try:
        simulate_processing("order_lookup")

        response = requests.get(f"{DATABASE_SERVICE_URL}/db/orders", timeout=10)
        response.raise_for_status()
        data = response.json()

        validate_data(data, "orders")

        # Simulate order total calculation
        time.sleep(random.uniform(0.02, 0.08))

        return jsonify({
            "source": SERVICE_NAME,
            "count": len(data.get("orders", [])),
            "data": data
        })
    except requests.RequestException as e:
        return jsonify({
            "error": str(e),
            "service": SERVICE_NAME
        }), 500


@app.route("/products")
def get_products():
    """Get products from Database Service."""
    try:
        simulate_processing("product_lookup")

        response = requests.get(f"{DATABASE_SERVICE_URL}/db/products", timeout=10)
        response.raise_for_status()
        data = response.json()

        validate_data(data, "products")

        # Simulate inventory check
        time.sleep(random.uniform(0.03, 0.1))

        return jsonify({
            "source": SERVICE_NAME,
            "count": len(data.get("products", [])),
            "data": data
        })
    except requests.RequestException as e:
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
