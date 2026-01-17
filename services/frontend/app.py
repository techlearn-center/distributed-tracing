#!/usr/bin/env python3
"""
Frontend Service - Entry Point for User Requests
=================================================
This service receives user requests and forwards them to the Backend.

YOUR TASK: Add OpenTelemetry tracing to this service!

Endpoints:
  GET /health       - Health check
  GET /api/users    - Get all users (calls Backend)
  GET /api/orders   - Get all orders (calls Backend)
  GET /api/products - Get all products (calls Backend)
"""

import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8081")
SERVICE_NAME = os.getenv("SERVICE_NAME", "frontend")

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
# Set up OpenTelemetry with the following steps:
#
# 1. Create a Resource with the service name:
#    resource = Resource.create({"service.name": SERVICE_NAME})
#
# 2. Create a TracerProvider with the resource:
#    provider = TracerProvider(resource=resource)
#
# 3. Create an OTLP exporter pointing to Jaeger:
#    exporter = OTLPSpanExporter(
#        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318") + "/v1/traces"
#    )
#
# 4. Add a BatchSpanProcessor with the exporter:
#    provider.add_span_processor(BatchSpanProcessor(exporter))
#
# 5. Set the global tracer provider:
#    trace.set_tracer_provider(provider)
#
# 6. Get a tracer for this module:
#    tracer = trace.get_tracer(__name__)


# =============================================================================
# TODO 3: Instrument Flask and Requests
# =============================================================================
# Auto-instrument Flask to trace incoming requests:
#    FlaskInstrumentor().instrument_app(app)
#
# Auto-instrument Requests to propagate trace context:
#    RequestsInstrumentor().instrument()


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
    """
    Get all users from the backend.

    TODO 4 (Optional): Add a custom span for this operation
    Example:
        with tracer.start_as_current_span("fetch_users_from_backend") as span:
            span.set_attribute("backend.url", BACKEND_URL)
            response = requests.get(f"{BACKEND_URL}/users")
            span.set_attribute("response.status_code", response.status_code)
            return jsonify(response.json())
    """
    try:
        response = requests.get(f"{BACKEND_URL}/users", timeout=10)
        response.raise_for_status()
        return jsonify({
            "source": SERVICE_NAME,
            "data": response.json()
        })
    except requests.RequestException as e:
        return jsonify({
            "error": str(e),
            "service": SERVICE_NAME
        }), 500


@app.route("/api/orders")
def get_orders():
    """Get all orders from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/orders", timeout=10)
        response.raise_for_status()
        return jsonify({
            "source": SERVICE_NAME,
            "data": response.json()
        })
    except requests.RequestException as e:
        return jsonify({
            "error": str(e),
            "service": SERVICE_NAME
        }), 500


@app.route("/api/products")
def get_products():
    """Get all products from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/products", timeout=10)
        response.raise_for_status()
        return jsonify({
            "source": SERVICE_NAME,
            "data": response.json()
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
            "GET /api/users",
            "GET /api/orders",
            "GET /api/products"
        ]
    })


if __name__ == "__main__":
    print(f"Starting {SERVICE_NAME} on port 8080...")
    print(f"Backend URL: {BACKEND_URL}")
    app.run(host="0.0.0.0", port=8080, debug=False)
