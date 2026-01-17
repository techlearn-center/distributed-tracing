#!/usr/bin/env python3
"""
Distributed Tracing Challenge - Progress Checker
=================================================
This script checks your progress through the distributed tracing challenge.
Run it anytime to see what you've completed and what's left to do.

Usage:
    python run.py          # Check all tasks
    python run.py --task 1 # Check specific task
"""

import subprocess
import sys
import re
import time
import os

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print the challenge header."""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  🔍 Distributed Tracing Challenge - Progress Checker{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_task(num, name, status, message=""):
    """Print task status."""
    if status == "pass":
        icon = "✅"
        color = Colors.GREEN
    elif status == "fail":
        icon = "❌"
        color = Colors.RED
    else:
        icon = "⏳"
        color = Colors.YELLOW

    print(f"{icon} {Colors.BOLD}Task {num}:{Colors.END} {name}")
    if message:
        print(f"   {color}{message}{Colors.END}")

def check_file_has_otel_imports(filepath):
    """Check if a file has OpenTelemetry imports (uncommented)."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for uncommented OTel imports
        required_imports = [
            r'^from opentelemetry import trace',
            r'^from opentelemetry\.sdk\.trace import TracerProvider',
            r'^from opentelemetry\.sdk\.resources import Resource',
        ]

        for pattern in required_imports:
            if not re.search(pattern, content, re.MULTILINE):
                return False

        return True
    except Exception:
        return False

def check_file_has_tracer_setup(filepath):
    """Check if a file has tracer provider setup (uncommented)."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for uncommented tracer setup
        patterns = [
            r'^resource\s*=\s*Resource\.create',
            r'^provider\s*=\s*TracerProvider',
            r'trace\.set_tracer_provider',
        ]

        for pattern in patterns:
            if not re.search(pattern, content, re.MULTILINE):
                return False

        return True
    except Exception:
        return False

def check_file_has_instrumentation(filepath, needs_requests=True):
    """Check if a file has Flask instrumentation."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for Flask instrumentation
        if not re.search(r'FlaskInstrumentor\(\)\.instrument_app', content):
            return False

        # Check for Requests instrumentation if needed
        if needs_requests:
            if not re.search(r'RequestsInstrumentor\(\)\.instrument', content):
                return False

        return True
    except Exception:
        return False

def check_docker_running():
    """Check if Docker is running."""
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False

def check_container_running(container_name):
    """Check if a specific container is running."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return container_name in result.stdout
    except Exception:
        return False

def check_jaeger_healthy():
    """Check if Jaeger is responding."""
    try:
        import urllib.request
        req = urllib.request.urlopen('http://localhost:16686', timeout=5)
        return req.status == 200
    except Exception:
        return False

def check_service_healthy(port):
    """Check if a service is responding on the given port."""
    try:
        import urllib.request
        req = urllib.request.urlopen(f'http://localhost:{port}/health', timeout=5)
        return req.status == 200
    except Exception:
        return False

def check_jaeger_has_traces(service_name):
    """Check if Jaeger has traces for a service."""
    try:
        import urllib.request
        import json
        url = f'http://localhost:16686/api/services'
        req = urllib.request.urlopen(url, timeout=5)
        data = json.loads(req.read().decode())
        services = data.get('data', [])
        return service_name in services
    except Exception:
        return False

def check_task_1_frontend():
    """Check Task 1: Frontend service instrumentation."""
    filepath = 'services/frontend/app.py'

    if not os.path.exists(filepath):
        return False, "File not found: services/frontend/app.py"

    if not check_file_has_otel_imports(filepath):
        return False, "OpenTelemetry imports are still commented out"

    if not check_file_has_tracer_setup(filepath):
        return False, "Tracer provider setup is still commented out"

    if not check_file_has_instrumentation(filepath, needs_requests=True):
        return False, "Flask/Requests instrumentation is still commented out"

    return True, "Frontend service is properly instrumented!"

def check_task_2_backend():
    """Check Task 2: Backend service instrumentation."""
    filepath = 'services/backend/app.py'

    if not os.path.exists(filepath):
        return False, "File not found: services/backend/app.py"

    if not check_file_has_otel_imports(filepath):
        return False, "OpenTelemetry imports are still commented out"

    if not check_file_has_tracer_setup(filepath):
        return False, "Tracer provider setup is still commented out"

    if not check_file_has_instrumentation(filepath, needs_requests=True):
        return False, "Flask/Requests instrumentation is still commented out"

    return True, "Backend service is properly instrumented!"

def check_task_3_database():
    """Check Task 3: Database service instrumentation."""
    filepath = 'services/database-service/app.py'

    if not os.path.exists(filepath):
        return False, "File not found: services/database-service/app.py"

    if not check_file_has_otel_imports(filepath):
        return False, "OpenTelemetry imports are still commented out"

    if not check_file_has_tracer_setup(filepath):
        return False, "Tracer provider setup is still commented out"

    if not check_file_has_instrumentation(filepath, needs_requests=False):
        return False, "Flask instrumentation is still commented out"

    return True, "Database service is properly instrumented!"

def check_task_4_stack_running():
    """Check Task 4: All services are running."""
    if not check_docker_running():
        return False, "Docker is not running"

    containers = ['jaeger', 'frontend', 'backend', 'database-service']
    not_running = []

    for container in containers:
        if not check_container_running(container):
            not_running.append(container)

    if not_running:
        return False, f"Containers not running: {', '.join(not_running)}"

    # Check health endpoints
    if not check_jaeger_healthy():
        return False, "Jaeger is not responding - check logs with: docker logs jaeger"

    services = [
        (8080, "Frontend"),
        (8081, "Backend"),
        (8082, "Database Service")
    ]

    for port, name in services:
        if not check_service_healthy(port):
            return False, f"{name} is not responding on port {port}"

    return True, "All services are running and healthy!"

def check_task_5_traces_in_jaeger():
    """Check Task 5: Traces appearing in Jaeger."""
    if not check_jaeger_healthy():
        return False, "Jaeger is not running - complete Task 4 first"

    # Generate some traffic first
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:8080/api/users', timeout=10)
        time.sleep(2)  # Wait for traces to be exported
    except Exception:
        pass

    # Check for traces
    services_found = []
    for service in ['frontend', 'backend', 'database-service']:
        if check_jaeger_has_traces(service):
            services_found.append(service)

    if len(services_found) == 0:
        return False, "No traces found in Jaeger - make sure instrumentation is working"

    if len(services_found) < 3:
        return False, f"Only found traces for: {', '.join(services_found)}. Missing some services."

    return True, f"Traces found for all services! Open Jaeger UI at http://localhost:16686"

def main():
    """Main function to run all checks."""
    print_header()

    results = []
    total_points = 0
    earned_points = 0

    # Task definitions
    tasks = [
        (1, "Instrument Frontend Service", check_task_1_frontend, 25),
        (2, "Instrument Backend Service", check_task_2_backend, 25),
        (3, "Instrument Database Service", check_task_3_database, 20),
        (4, "Start the Stack", check_task_4_stack_running, 15),
        (5, "Verify Traces in Jaeger", check_task_5_traces_in_jaeger, 15),
    ]

    # Check specific task if requested
    specific_task = None
    if len(sys.argv) > 2 and sys.argv[1] == '--task':
        try:
            specific_task = int(sys.argv[2])
        except ValueError:
            print(f"{Colors.RED}Invalid task number{Colors.END}")
            sys.exit(1)

    for num, name, check_func, points in tasks:
        if specific_task and num != specific_task:
            continue

        total_points += points
        try:
            passed, message = check_func()
            if passed:
                earned_points += points
                print_task(num, name, "pass", message)
            else:
                print_task(num, name, "fail", message)
        except Exception as e:
            print_task(num, name, "fail", f"Error checking: {str(e)}")
        print()

    # Print summary
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    percentage = (earned_points / total_points * 100) if total_points > 0 else 0

    if percentage >= 70:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 Congratulations! You passed the challenge!{Colors.END}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}Keep going! You're making progress.{Colors.END}")

    print(f"\n{Colors.BOLD}Score:{Colors.END} {earned_points}/{total_points} points ({percentage:.0f}%)")
    print(f"{Colors.BOLD}Passing Score:{Colors.END} 70%")

    if percentage < 100:
        print(f"\n{Colors.BLUE}💡 Hints:{Colors.END}")
        print("  • Uncomment the TODO sections in each service's app.py")
        print("  • Make sure to rebuild after changes: docker-compose build")
        print("  • Jaeger UI is at http://localhost:16686")
        print("  • Check service logs: docker-compose logs <service>")

    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}\n")

    return 0 if percentage >= 70 else 1

if __name__ == '__main__':
    sys.exit(main())
