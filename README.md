# Distributed Tracing Challenge

## Learn Request Tracing Across Microservices with Jaeger

Welcome to the **Distributed Tracing Challenge**! In this hands-on exercise, you'll learn how to trace requests as they flow through multiple microservices using **Jaeger**, a popular open-source distributed tracing system.

---

## 📚 Table of Contents

1. [What is Distributed Tracing?](#what-is-distributed-tracing)
2. [Why Do We Need It?](#why-do-we-need-it)
3. [Key Concepts](#key-concepts)
4. [The Three Pillars of Observability](#the-three-pillars-of-observability)
5. [Prerequisites](#prerequisites)
6. [Challenge Overview](#challenge-overview)
7. [Getting Started](#getting-started)
8. [Tasks](#tasks)
9. [Jaeger UI Guide](#jaeger-ui-guide)
10. [OpenTelemetry Basics](#opentelemetry-basics)
11. [Tracing Tools Comparison](#tracing-tools-comparison)
12. [Troubleshooting](#troubleshooting)
13. [Next Steps](#next-steps)

---

## What is Distributed Tracing?

**Distributed tracing** is a method of tracking a request as it travels through a distributed system (multiple services). It helps you understand:

- **Where** time is spent in a request
- **Which** services are involved
- **What** errors occur and where
- **How** services communicate with each other

### A Simple Analogy

Think of distributed tracing like **package tracking**:

```
📦 Your Package Journey:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Sender    │───▶│  Warehouse  │───▶│   Truck     │───▶│  Your Door  │
│  (Origin)   │    │  (Sorting)  │    │ (Transport) │    │ (Delivery)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     10:00             10:30              12:00              14:00
```

Just like you can track where your package is and how long each step takes, distributed tracing lets you track a request through your services!

---

## Why Do We Need It?

### The Microservices Problem

In a monolithic application, debugging is straightforward - everything is in one place:

```
Monolith:
┌────────────────────────────────────────┐
│            Single Application          │
│  ┌──────┐  ┌──────┐  ┌──────────────┐ │
│  │ Auth │──│ API  │──│   Database   │ │
│  └──────┘  └──────┘  └──────────────┘ │
└────────────────────────────────────────┘
         Easy to debug! 🎉
```

But in microservices, a single request can touch many services:

```
Microservices:
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Gateway │───▶│  Auth   │───▶│  Orders │───▶│ Payment │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                    │              │              │
                    ▼              ▼              ▼
              ┌─────────┐    ┌─────────┐    ┌─────────┐
              │  Users  │    │Inventory│    │ Notify  │
              │   DB    │    │   DB    │    │ Service │
              └─────────┘    └─────────┘    └─────────┘

         Where did the error happen? 🤔
         Why is it slow? 🤔
         Which service is the bottleneck? 🤔
```

### Without Tracing vs With Tracing

**Without Tracing:**
```
❌ "The checkout is slow"
❌ "Something failed somewhere"
❌ "I don't know which service caused the error"
❌ Hours of searching through logs
```

**With Tracing:**
```
✅ "The payment service took 2.3s - that's the bottleneck"
✅ "The inventory service returned a 500 error"
✅ "The request failed at the database connection step"
✅ Instant visibility into the entire request flow
```

---

## Key Concepts

### 1. Trace

A **trace** represents the entire journey of a request through your system.

```
Trace ID: abc123
┌──────────────────────────────────────────────────────────────┐
│                     Complete Request Journey                  │
│  Frontend ──▶ Backend ──▶ Database ──▶ Backend ──▶ Frontend  │
└──────────────────────────────────────────────────────────────┘
```

### 2. Span

A **span** represents a single operation within a trace. Each service creates one or more spans.

```
Trace: abc123
├── Span: Frontend (0ms - 500ms)
│   ├── Span: HTTP Request to Backend (10ms - 450ms)
│   │   ├── Span: Backend Processing (20ms - 400ms)
│   │   │   ├── Span: Database Query (50ms - 200ms)
│   │   │   └── Span: Cache Lookup (210ms - 220ms)
│   │   └── Span: Response Serialization (410ms - 440ms)
│   └── Span: Render Response (460ms - 490ms)
```

### 3. Span Attributes

Each span can have **attributes** (key-value pairs) that provide context:

```python
span.set_attribute("http.method", "GET")
span.set_attribute("http.url", "/api/users/123")
span.set_attribute("http.status_code", 200)
span.set_attribute("user.id", "user_123")
```

### 4. Context Propagation

**Context propagation** passes trace information between services, usually via HTTP headers:

```
Service A                           Service B
┌─────────────┐                    ┌─────────────┐
│ Create Span │                    │             │
│ trace_id=X  │────HTTP Request───▶│ Read Header │
│ span_id=Y   │   Headers:         │ trace_id=X  │
│             │   traceparent:     │ parent_id=Y │
│             │   X-Y-01-...       │ Create Span │
└─────────────┘                    └─────────────┘
```

### 5. Span Relationships

```
                    ┌───────────────────┐
                    │   Root Span       │
                    │   (No Parent)     │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
        │Child Span │   │Child Span │   │Child Span │
        │  (Auth)   │   │  (API)    │   │  (Cache)  │
        └───────────┘   └─────┬─────┘   └───────────┘
                              │
                        ┌─────▼─────┐
                        │Grandchild │
                        │   (DB)    │
                        └───────────┘
```

---

## The Three Pillars of Observability

Distributed tracing is one of three key observability tools:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE THREE PILLARS                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     METRICS     │      LOGS       │          TRACES             │
│   (Prometheus)  │     (Loki)      │         (Jaeger)            │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ "How many?"     │ "What happened?"│ "Where did it happen?"      │
│ "How fast?"     │ "Why?"          │ "How long did each          │
│ "How much?"     │                 │  step take?"                │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ request_count   │ ERROR: DB conn  │ Trace: abc123               │
│ latency_p99     │ failed at 10:23 │ ├─ Frontend: 50ms           │
│ error_rate      │ user=john       │ ├─ Backend: 120ms           │
│ cpu_usage       │ query=SELECT... │ └─ DB: 800ms ← bottleneck!  │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ Aggregated      │ Individual      │ Request-scoped              │
│ Time-series     │ Events          │ Causality                   │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

**When to use each:**
- **Metrics**: "Is something wrong?" (alerting, dashboards)
- **Logs**: "What exactly happened?" (debugging, audit)
- **Traces**: "Where is the problem?" (performance, dependencies)

---

## Prerequisites

Before starting this challenge, you should have:

### Required
- ✅ **Docker** and **Docker Compose** installed
- ✅ Basic understanding of **HTTP** and **REST APIs**
- ✅ Familiarity with **Python** (our sample services use Python)
- ✅ Command line basics

### Helpful (but not required)
- 📖 Understanding of microservices architecture
- 📖 Experience with the [monitoring-stack](https://github.com/techlearn-center/monitoring-stack) challenge
- 📖 Experience with the [logging-stack](https://github.com/techlearn-center/logging-stack) challenge

### Install Docker

If you don't have Docker installed:

```bash
# Check if Docker is installed
docker --version
docker-compose --version

# If not installed, visit:
# https://docs.docker.com/get-docker/
```

---

## Challenge Overview

### What You'll Build

```
┌──────────────────────────────────────────────────────────────────┐
│                    YOUR TRACING STACK                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐     ┌──────────┐     ┌──────────────────┐        │
│   │ Frontend │────▶│ Backend  │────▶│ Database Service │        │
│   │ :8080    │     │ :8081    │     │     :8082        │        │
│   └────┬─────┘     └────┬─────┘     └────────┬─────────┘        │
│        │                │                     │                  │
│        │    Traces      │      Traces         │    Traces        │
│        └────────────────┴─────────────────────┘                  │
│                         │                                        │
│                         ▼                                        │
│               ┌──────────────────┐                               │
│               │      Jaeger      │                               │
│               │  Collector:14268 │                               │
│               │     UI:16686     │                               │
│               └──────────────────┘                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 8080 | Entry point, calls Backend |
| Backend | 8081 | Business logic, calls Database Service |
| Database Service | 8082 | Data access layer |
| Jaeger UI | 16686 | Trace visualization |
| Jaeger Collector | 14268 | Receives traces |

### Learning Objectives

By completing this challenge, you will:

1. ✅ Understand distributed tracing concepts
2. ✅ Set up Jaeger for trace collection
3. ✅ Instrument Python services with OpenTelemetry
4. ✅ Propagate trace context between services
5. ✅ Use Jaeger UI to analyze traces
6. ✅ Identify performance bottlenecks
7. ✅ Add custom spans and attributes

---

## Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/techlearn-center/distributed-tracing.git
cd distributed-tracing
```

### Step 2: Explore the Structure

```
distributed-tracing/
├── docker-compose.yml       # Orchestrates all services
├── services/
│   ├── frontend/           # Frontend service (TODO)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── backend/            # Backend service (TODO)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── database-service/   # Database service (TODO)
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
├── jaeger/                 # Jaeger configuration
├── solutions/              # Reference solutions
└── run.py                  # Progress checker
```

### Step 3: Start the Stack

```bash
docker-compose up -d
```

### Step 4: Verify Services

```bash
# Check all containers are running
docker-compose ps

# Check Jaeger UI
# Open http://localhost:16686 in your browser
```

---

## Tasks

### Task 1: Understand the Sample Services

First, let's understand how the services communicate:

```
User Request
     │
     ▼
┌─────────────────┐
│    Frontend     │  GET /api/users
│    :8080        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Backend      │  GET /users
│    :8081        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Database Service│  GET /db/users
│    :8082        │
└─────────────────┘
```

**Your Task:** Read through the service code in `services/*/app.py` to understand:
- What endpoints each service exposes
- How services call each other
- Where tracing needs to be added

---

### Task 2: Add OpenTelemetry to Frontend Service

Open `services/frontend/app.py` and add tracing instrumentation.

**TODO Items:**

```python
# =============================================================================
# TODO 1: Import OpenTelemetry libraries
# =============================================================================
# You need to import:
# - trace from opentelemetry
# - TracerProvider, Resource from opentelemetry.sdk.trace
# - BatchSpanProcessor from opentelemetry.sdk.trace.export
# - OTLPSpanExporter from opentelemetry.exporter.otlp.proto.http.trace_exporter
# - FlaskInstrumentor from opentelemetry.instrumentation.flask
# - RequestsInstrumentor from opentelemetry.instrumentation.requests

# =============================================================================
# TODO 2: Configure the tracer provider
# =============================================================================
# Set up:
# - Resource with service.name attribute
# - TracerProvider with the resource
# - OTLP exporter pointing to Jaeger (http://jaeger:4318/v1/traces)
# - BatchSpanProcessor with the exporter
# - Set the global tracer provider

# =============================================================================
# TODO 3: Instrument Flask and Requests
# =============================================================================
# Use FlaskInstrumentor().instrument_app(app) to auto-instrument Flask
# Use RequestsInstrumentor().instrument() to auto-instrument HTTP calls
```

**Hints:**
- The OTLP endpoint for Jaeger is `http://jaeger:4318/v1/traces`
- Service name should be "frontend"
- Check `solutions/frontend/app.py` if you get stuck

---

### Task 3: Add OpenTelemetry to Backend Service

Open `services/backend/app.py` and add similar tracing instrumentation.

**Key Differences:**
- Service name should be "backend"
- Same OTLP endpoint configuration

---

### Task 4: Add OpenTelemetry to Database Service

Open `services/database-service/app.py` and add tracing.

**Key Differences:**
- Service name should be "database-service"
- This is the last service in the chain

---

### Task 5: Add Custom Spans

Once basic tracing works, add custom spans for specific operations.

**Example - Add a custom span for database simulation:**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def get_users():
    # Create a custom span for the "database query"
    with tracer.start_as_current_span("simulate_database_query") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.operation", "SELECT")
        span.set_attribute("db.table", "users")

        # Simulate database delay
        time.sleep(random.uniform(0.1, 0.3))

        users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        span.set_attribute("db.rows_returned", len(users))

        return users
```

---

### Task 6: Verify Tracing in Jaeger

1. Open Jaeger UI: http://localhost:16686

2. Generate some traces:
   ```bash
   # Make requests to the frontend
   curl http://localhost:8080/api/users
   curl http://localhost:8080/api/orders
   curl http://localhost:8080/health
   ```

3. In Jaeger UI:
   - Select "frontend" from the Service dropdown
   - Click "Find Traces"
   - Click on a trace to see the full request flow

4. Verify you can see:
   - All three services in the trace
   - Parent-child relationships between spans
   - Timing for each span

---

### Task 7: Analyze Performance

Use Jaeger to identify performance issues:

1. **Find the slowest traces:**
   - Sort traces by duration
   - Identify which service is the bottleneck

2. **Compare traces:**
   - Look at multiple traces for the same endpoint
   - Identify variance in timing

3. **Check for errors:**
   - Look for traces with error tags
   - Find where errors originated

---

## Jaeger UI Guide

### Main Search Page

```
┌────────────────────────────────────────────────────────────────┐
│ JAEGER                                              Search     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Service: [frontend    ▼]   Operation: [all ▼]                │
│                                                                │
│  Tags: [                                        ]              │
│                                                                │
│  Lookback: [Last Hour ▼]    Max Results: [20  ]              │
│                                                                │
│                        [Find Traces]                           │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│ Results:                                                       │
│ ┌────────────────────────────────────────────────────────────┐│
│ │ frontend: GET /api/users  │ 3 Spans │ 234ms │ 2 min ago   ││
│ │ ████████████████████████████████████                      ││
│ └────────────────────────────────────────────────────────────┘│
│ ┌────────────────────────────────────────────────────────────┐│
│ │ frontend: GET /api/orders │ 4 Spans │ 567ms │ 5 min ago   ││
│ │ ████████████████████████████████████████████████████████  ││
│ └────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

### Trace Detail View

```
┌────────────────────────────────────────────────────────────────┐
│ Trace: abc123def456                              Total: 234ms  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│ ▼ frontend: GET /api/users                           [234ms]  │
│   ├─────────────────────────────────────────────────────────│ │
│   │████████████████████████████████████████████████████████ │ │
│   └─────────────────────────────────────────────────────────│ │
│                                                                │
│   ▼ backend: GET /users                              [180ms]  │
│     ├───────────────────────────────────────────────────────│ │
│     │        ████████████████████████████████████████████   │ │
│     └───────────────────────────────────────────────────────│ │
│                                                                │
│     ▼ database-service: GET /db/users                [120ms]  │
│       ├─────────────────────────────────────────────────────│ │
│       │              ██████████████████████████████         │ │
│       └─────────────────────────────────────────────────────│ │
│                                                                │
│       ▼ simulate_database_query                       [95ms]  │
│         ├───────────────────────────────────────────────────│ │
│         │                  ███████████████████████          │ │
│         └───────────────────────────────────────────────────│ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Understanding the Waterfall

- **Horizontal bars** show duration
- **Indentation** shows parent-child relationships
- **Color coding** differentiates services
- **Gaps** between bars show network latency

---

## OpenTelemetry Basics

### What is OpenTelemetry?

**OpenTelemetry (OTel)** is a vendor-neutral standard for:
- Generating traces, metrics, and logs
- Collecting and exporting telemetry data
- Instrumenting applications

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenTelemetry                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   Traces    │    │   Metrics   │    │    Logs     │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                   │               │
│          └──────────────────┼───────────────────┘               │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │   OTel SDK      │                          │
│                    │   (Unified)     │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│          ┌──────────────────┼──────────────────┐               │
│          │                  │                  │               │
│   ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐       │
│   │   Jaeger    │    │ Prometheus  │    │    Loki     │       │
│   └─────────────┘    └─────────────┘    └─────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Basic Instrumentation Pattern

```python
# 1. Import required modules
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# 2. Create a resource (identifies your service)
resource = Resource.create({
    "service.name": "my-service",
    "service.version": "1.0.0",
})

# 3. Create and configure the tracer provider
provider = TracerProvider(resource=resource)

# 4. Add an exporter (sends traces to Jaeger)
exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
provider.add_span_processor(BatchSpanProcessor(exporter))

# 5. Set as global tracer provider
trace.set_tracer_provider(provider)

# 6. Get a tracer
tracer = trace.get_tracer(__name__)

# 7. Use the tracer to create spans
with tracer.start_as_current_span("my-operation") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### Auto-Instrumentation

OpenTelemetry provides automatic instrumentation for popular libraries:

```python
# Flask auto-instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor
FlaskInstrumentor().instrument_app(app)

# Requests auto-instrumentation
from opentelemetry.instrumentation.requests import RequestsInstrumentor
RequestsInstrumentor().instrument()

# SQLAlchemy auto-instrumentation
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
SQLAlchemyInstrumentor().instrument()
```

---

## Tracing Tools Comparison

| Feature | Jaeger | Zipkin | Tempo | AWS X-Ray |
|---------|--------|--------|-------|-----------|
| **License** | Apache 2.0 | Apache 2.0 | AGPL 3.0 | Proprietary |
| **Backed by** | CNCF | OpenZipkin | Grafana | AWS |
| **Storage** | Multiple | Multiple | Object Store | AWS |
| **UI** | Built-in | Built-in | Grafana | AWS Console |
| **Query Language** | Tags | Tags | TraceQL | Filter Expressions |
| **Best For** | General use | Simple setup | Grafana stack | AWS workloads |
| **Complexity** | Medium | Low | Low | Low (in AWS) |
| **Cost** | Free | Free | Free | Pay per trace |

### When to Use What

- **Jaeger**: Great all-around choice, CNCF project, excellent UI
- **Zipkin**: Simpler, good for getting started quickly
- **Tempo**: Best if you're already using Grafana ecosystem
- **AWS X-Ray**: Best if you're all-in on AWS

---

## Troubleshooting

### No Traces Appearing

```bash
# 1. Check if services are running
docker-compose ps

# 2. Check Jaeger is receiving data
docker logs jaeger

# 3. Check service logs for errors
docker logs frontend
docker logs backend
docker logs database-service

# 4. Verify OTLP endpoint is correct
# Should be: http://jaeger:4318/v1/traces

# 5. Generate test traffic
curl http://localhost:8080/api/users
```

### Traces Not Linked

If you see separate traces instead of one connected trace:

```bash
# Ensure context propagation headers are being passed
# Check that RequestsInstrumentor is enabled
# Verify all services use the same trace format
```

### Service Not Appearing in Jaeger

```bash
# 1. Verify service name is set correctly
# resource = Resource.create({"service.name": "your-service"})

# 2. Check the tracer provider is set globally
# trace.set_tracer_provider(provider)

# 3. Restart the service after changes
docker-compose restart <service-name>
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Jaeger not running | `docker-compose up -d jaeger` |
| `Module not found` | Missing dependency | Check `requirements.txt` |
| `No traces found` | Exporter misconfigured | Verify OTLP endpoint URL |
| `Broken trace` | Context not propagated | Enable RequestsInstrumentor |

---

## Checking Your Progress

Run the progress checker to see how you're doing:

```bash
python run.py
```

Expected output when complete:

```
==================================================
📊 Distributed Tracing Challenge - Progress Checker
==================================================

✅ Task 1: Frontend tracing configured
✅ Task 2: Backend tracing configured
✅ Task 3: Database service tracing configured
✅ Task 4: All services running
✅ Task 5: Traces appearing in Jaeger
✅ Task 6: Traces are properly linked

==================================================
🎉 Congratulations! Challenge Complete!
==================================================

Score: 100/100 points (100%)
```

---

## Next Steps

After completing this challenge, explore:

### 1. Add More Services
Create additional microservices and trace their interactions.

### 2. Integrate with Grafana
Connect Jaeger to Grafana for combined metrics and traces:
```yaml
# In Grafana, add Jaeger as a data source
# Type: Jaeger
# URL: http://jaeger:16686
```

### 3. Add Trace-Log Correlation
Link traces to logs using trace IDs:
```python
import logging
logging.info(f"Processing request trace_id={span.get_span_context().trace_id}")
```

### 4. Implement Sampling
For production, implement sampling to reduce overhead:
```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
sampler = TraceIdRatioBased(0.1)  # Sample 10% of traces
```

### 5. Explore Other Challenges
- [monitoring-stack](https://github.com/techlearn-center/monitoring-stack) - Prometheus & Grafana
- [logging-stack](https://github.com/techlearn-center/logging-stack) - Loki & Promtail

---

## Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Distributed Tracing in Practice](https://www.oreilly.com/library/view/distributed-tracing-in/9781492056621/)
- [CNCF Jaeger Project](https://www.cncf.io/projects/jaeger/)

---

## License

This challenge is part of the TechLearn Center curriculum.
Free to use for educational purposes.

---

**Happy Tracing! 🔍**

*Remember: Good observability = Happy developers + Reliable systems*
