# Solutions - Distributed Tracing Challenge

> **Warning**: Only look at these solutions if you're stuck! Try to complete the challenge yourself first.

This folder contains complete solution files for reference.

## Solution Files

| File | Description |
|------|-------------|
| `frontend_app.py` | Complete frontend service with tracing |
| `backend_app.py` | Complete backend service with tracing |
| `database_service_app.py` | Complete database service with tracing |

## How to Use Solutions

If you're stuck on a particular task:

1. First, re-read the README.md in the parent folder
2. Try to understand what the instrumentation should do
3. Look at the solution for hints, not to copy directly
4. Understand WHY the solution works

## Applying Solutions

To test with solutions (for debugging only):

```bash
# Copy solution files
cp solutions/frontend_app.py services/frontend/app.py
cp solutions/backend_app.py services/backend/app.py
cp solutions/database_service_app.py services/database-service/app.py

# Rebuild and restart
docker-compose build
docker-compose up -d

# Generate traffic
curl http://localhost:8080/api/users

# View traces at http://localhost:16686
```

## Key Learning Points

### 1. OpenTelemetry Setup Pattern

Every service follows the same pattern:

```python
# 1. Create Resource (identifies your service)
resource = Resource.create({"service.name": "my-service"})

# 2. Create TracerProvider
provider = TracerProvider(resource=resource)

# 3. Add Exporter (where to send traces)
exporter = OTLPSpanExporter(endpoint="http://jaeger:4318/v1/traces")
provider.add_span_processor(BatchSpanProcessor(exporter))

# 4. Set globally
trace.set_tracer_provider(provider)

# 5. Get tracer for your module
tracer = trace.get_tracer(__name__)
```

### 2. Auto-Instrumentation

Auto-instrumentation does the heavy lifting:

```python
# Flask: Traces all incoming HTTP requests
FlaskInstrumentor().instrument_app(app)

# Requests: Propagates trace context in outgoing calls
RequestsInstrumentor().instrument()
```

### 3. Custom Spans

Add custom spans for visibility into specific operations:

```python
with tracer.start_as_current_span("my_operation") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### 4. Context Propagation

- `RequestsInstrumentor` automatically adds trace headers to HTTP calls
- Child services receive these headers and continue the trace
- This creates the parent-child relationship in Jaeger

## Common Issues and Solutions

### No Traces in Jaeger

1. Check OTLP endpoint URL (should be `http://jaeger:4318/v1/traces`)
2. Verify tracer provider is set globally
3. Check service logs for errors
4. Make sure services are on the same Docker network

### Traces Not Linked

1. Ensure `RequestsInstrumentor().instrument()` is called
2. Verify both services have tracing configured
3. Check that the HTTP call is using the `requests` library

### Service Not Appearing

1. Verify `service.name` is set in Resource
2. Check that the service has received at least one request
3. Wait a few seconds for traces to be exported

## Understanding the Trace Flow

```
Frontend Request Received
    │
    ├── FlaskInstrumentor creates span
    │
    ├── Your code runs (custom spans optional)
    │
    ├── requests.get() called
    │   │
    │   └── RequestsInstrumentor adds trace headers
    │
    └── Backend receives request
        │
        ├── FlaskInstrumentor creates child span
        │
        ├── Your code runs
        │
        ├── requests.get() called (to DB service)
        │   │
        │   └── RequestsInstrumentor adds trace headers
        │
        └── Database Service receives request
            │
            └── FlaskInstrumentor creates grandchild span
```

Each arrow represents context being passed, creating the trace hierarchy.
