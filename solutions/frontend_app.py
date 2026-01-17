#!/usr/bin/env python3
"""
SOLUTION: Frontend Service with OpenTelemetry Tracing
======================================================
This is the complete solution for the frontend service instrumentation.
Students should try to complete the TODO file first before looking here!
"""

import os
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
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8081")
SERVICE_NAME = os.getenv("SERVICE_NAME", "frontend")

# =============================================================================
# SOLUTION: Configure the Tracer Provider
# =============================================================================

# 1. Create a Resource with the service name
resource = Resource.create({
    "service.name": SERVICE_NAME,
    "service.version": "1.0.0",
})

# 2. Create a TracerProvider with the resource
provider = TracerProvider(resource=resource)

# 3. Create an OTLP exporter pointing to Jaeger
exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/traces"
)

# 4. Add a BatchSpanProcessor with the exporter
provider.add_span_processor(BatchSpanProcessor(exporter))

# 5. Set the global tracer provider
trace.set_tracer_provider(provider)

# 6. Get a tracer for this module
tracer = trace.get_tracer(__name__)

# =============================================================================
# SOLUTION: Instrument Flask and Requests
# =============================================================================

# Auto-instrument Flask to trace incoming requests
FlaskInstrumentor().instrument_app(app)

# Auto-instrument Requests to propagate trace context
RequestsInstrumentor().instrument()


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


@app.route("/api/users")
def get_users():
    """Get all users from the backend with custom span."""
    # SOLUTION: Custom span example
    with tracer.start_as_current_span("fetch_users_from_backend") as span:
        span.set_attribute("backend.url", BACKEND_URL)
        span.set_attribute("operation", "get_users")

        try:
            response = requests.get(f"{BACKEND_URL}/users", timeout=10)
            span.set_attribute("response.status_code", response.status_code)
            response.raise_for_status()

            data = response.json()
            span.set_attribute("users.count", len(data.get("data", {}).get("users", [])))

            return jsonify({
                "source": SERVICE_NAME,
                "data": data
            })
        except requests.RequestException as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            return jsonify({
                "error": str(e),
                "service": SERVICE_NAME
            }), 500


@app.route("/api/orders")
def get_orders():
    """Get all orders from the backend."""
    with tracer.start_as_current_span("fetch_orders_from_backend") as span:
        span.set_attribute("backend.url", BACKEND_URL)

        try:
            response = requests.get(f"{BACKEND_URL}/orders", timeout=10)
            span.set_attribute("response.status_code", response.status_code)
            response.raise_for_status()
            return jsonify({
                "source": SERVICE_NAME,
                "data": response.json()
            })
        except requests.RequestException as e:
            span.set_attribute("error", True)
            return jsonify({
                "error": str(e),
                "service": SERVICE_NAME
            }), 500


@app.route("/api/products")
def get_products():
    """Get all products from the backend."""
    with tracer.start_as_current_span("fetch_products_from_backend") as span:
        span.set_attribute("backend.url", BACKEND_URL)

        try:
            response = requests.get(f"{BACKEND_URL}/products", timeout=10)
            span.set_attribute("response.status_code", response.status_code)
            response.raise_for_status()
            return jsonify({
                "source": SERVICE_NAME,
                "data": response.json()
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
            "GET /api/users",
            "GET /api/orders",
            "GET /api/products"
        ]
    })


if __name__ == "__main__":
    print(f"Starting {SERVICE_NAME} on port 8080...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"OTLP Endpoint: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4318')}")
    app.run(host="0.0.0.0", port=8080, debug=False)
