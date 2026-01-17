#!/usr/bin/env python3
"""
Database Service - Data Access Layer
=====================================
This service simulates database operations.

YOUR TASK: Add OpenTelemetry tracing to this service!

Endpoints:
  GET /health      - Health check
  GET /db/users    - Get users from "database"
  GET /db/orders   - Get orders from "database"
  GET /db/products - Get products from "database"
"""

import os
import time
import random
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "database-service")

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


# =============================================================================
# TODO 2: Configure the Tracer Provider
# =============================================================================
# Set up OpenTelemetry (same pattern, but with "database-service" as service name):
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
# TODO 3: Instrument Flask
# =============================================================================
# FlaskInstrumentor().instrument_app(app)
# Note: No RequestsInstrumentor needed here since this service doesn't make HTTP calls


# =============================================================================
# Simulated Database
# =============================================================================

# Simulated user data
USERS = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "user"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "role": "user"},
    {"id": 4, "name": "Diana Prince", "email": "diana@example.com", "role": "moderator"},
    {"id": 5, "name": "Eve Wilson", "email": "eve@example.com", "role": "user"},
]

# Simulated order data
ORDERS = [
    {"id": 101, "user_id": 1, "total": 99.99, "status": "completed", "items": 3},
    {"id": 102, "user_id": 2, "total": 149.50, "status": "pending", "items": 5},
    {"id": 103, "user_id": 1, "total": 29.99, "status": "shipped", "items": 1},
    {"id": 104, "user_id": 3, "total": 299.00, "status": "completed", "items": 2},
    {"id": 105, "user_id": 4, "total": 75.00, "status": "processing", "items": 4},
]

# Simulated product data
PRODUCTS = [
    {"id": 1001, "name": "Laptop", "price": 999.99, "stock": 50, "category": "electronics"},
    {"id": 1002, "name": "Headphones", "price": 149.99, "stock": 200, "category": "electronics"},
    {"id": 1003, "name": "Coffee Mug", "price": 12.99, "stock": 500, "category": "home"},
    {"id": 1004, "name": "Notebook", "price": 5.99, "stock": 1000, "category": "office"},
    {"id": 1005, "name": "Backpack", "price": 79.99, "stock": 75, "category": "accessories"},
]


# =============================================================================
# Database Simulation Functions
# =============================================================================

def simulate_db_query(table_name, query_type="SELECT"):
    """
    Simulate a database query with realistic delays.

    TODO 4: Wrap this in a custom span to show database operations
    Example:
        with tracer.start_as_current_span("db_query") as span:
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.operation", query_type)
            span.set_attribute("db.table", table_name)

            # Simulate query execution time
            delay = random.uniform(0.1, 0.3)
            span.set_attribute("db.query_time_ms", delay * 1000)
            time.sleep(delay)
    """
    # Simulate database query time (100-300ms)
    delay = random.uniform(0.1, 0.3)
    time.sleep(delay)


def simulate_connection_pool():
    """
    Simulate getting a connection from pool.

    TODO 5 (Optional): Add a span for connection pool operations
    """
    # Simulate connection acquisition (10-50ms)
    time.sleep(random.uniform(0.01, 0.05))


# =============================================================================
# Routes
# =============================================================================

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "database": "connected"
    })


@app.route("/db/users")
def get_users():
    """
    Get all users from the simulated database.
    """
    # Simulate connection pool
    simulate_connection_pool()

    # Simulate database query
    simulate_db_query("users", "SELECT")

    return jsonify({
        "source": SERVICE_NAME,
        "table": "users",
        "users": USERS
    })


@app.route("/db/orders")
def get_orders():
    """Get all orders from the simulated database."""
    simulate_connection_pool()
    simulate_db_query("orders", "SELECT")

    return jsonify({
        "source": SERVICE_NAME,
        "table": "orders",
        "orders": ORDERS
    })


@app.route("/db/products")
def get_products():
    """Get all products from the simulated database."""
    simulate_connection_pool()
    simulate_db_query("products", "SELECT")

    return jsonify({
        "source": SERVICE_NAME,
        "table": "products",
        "products": PRODUCTS
    })


@app.route("/db/user/<int:user_id>")
def get_user(user_id):
    """Get a specific user by ID."""
    simulate_connection_pool()
    simulate_db_query("users", "SELECT WHERE")

    user = next((u for u in USERS if u["id"] == user_id), None)
    if user:
        return jsonify({
            "source": SERVICE_NAME,
            "user": user
        })
    return jsonify({"error": "User not found"}), 404


@app.route("/")
def index():
    """Root endpoint with service info."""
    return jsonify({
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "database": "simulated",
        "endpoints": [
            "GET /health",
            "GET /db/users",
            "GET /db/orders",
            "GET /db/products",
            "GET /db/user/<id>"
        ]
    })


if __name__ == "__main__":
    print(f"Starting {SERVICE_NAME} on port 8082...")
    print("Database: Simulated (in-memory)")
    app.run(host="0.0.0.0", port=8082, debug=False)
