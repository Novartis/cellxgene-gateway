#!/bin/bash

# start_gunicorn.sh - Start Cellxgene Gateway with Gunicorn
#
# PREREQUISITES:
# - Gunicorn installed (included with cellxgene 1.3.0, or: pip install gunicorn)
# - Virtual environment activated
# - .env file with CELLXGENE_LOCATION and CELLXGENE_DATA (or CELLXGENE_BUCKET)
#
# USAGE:
# ./start_gunicorn.sh

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source environment variables
echo "Loading environment variables..."
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
else
    echo "Error: .env file not found at $SCRIPT_DIR/.env"
    echo "Please create it with required environment variables"
    exit 1
fi

# Verify required environment variables
if [ -z "$CELLXGENE_LOCATION" ]; then
    echo "Error: CELLXGENE_LOCATION not set"
    exit 1
fi

if [ -z "$CELLXGENE_DATA" ] && [ -z "$CELLXGENE_BUCKET" ]; then
    echo "Error: Either CELLXGENE_DATA or CELLXGENE_BUCKET must be set"
    exit 1
fi

# Gunicorn configuration
# WARNING: Multi-worker mode has cache synchronization issues (see plans/002-shared-cache-implementation.md)
# Each worker maintains its own in-memory cache, causing 404s for static assets when different
# workers handle requests for the same dataset. Use GUNICORN_WORKERS=1 until shared cache is implemented.
WORKERS=${GUNICORN_WORKERS:-1}
BIND=${GATEWAY_IP:-0.0.0.0}:${GATEWAY_PORT:-5005}
TIMEOUT=${GUNICORN_TIMEOUT:-120}
WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}
KEEPALIVE=${GUNICORN_KEEPALIVE:-5}
LOG_LEVEL=${GUNICORN_LOG_LEVEL:-info}

# Production optimization: enable backed mode to reduce memory usage
export GATEWAY_ENABLE_BACKED_MODE=${GATEWAY_ENABLE_BACKED_MODE:-true}

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Error: gunicorn not found. Install with: pip install gunicorn"
    exit 1
fi

# Display configuration
echo "Starting Cellxgene Gateway with Gunicorn..."
echo "Configuration:"
echo "  Data source: ${CELLXGENE_DATA:-$CELLXGENE_BUCKET}"
echo "  Binding to: $BIND"
echo "  Workers: $WORKERS"
echo "  Worker class: $WORKER_CLASS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Keepalive: ${KEEPALIVE}s"
echo "  Log level: $LOG_LEVEL"
echo "  Backed mode: ${GATEWAY_ENABLE_BACKED_MODE}"
echo ""

cd "$SCRIPT_DIR"

# Start Gunicorn with optimized settings
# Additional options you can add via environment variables:
# - GUNICORN_MAX_REQUESTS: Restart worker after N requests (prevents memory leaks)
# - GUNICORN_MAX_REQUESTS_JITTER: Add randomness to max-requests
exec gunicorn cellxgene_gateway.gateway:app \
    --workers "$WORKERS" \
    --worker-class "$WORKER_CLASS" \
    --bind "$BIND" \
    --timeout "$TIMEOUT" \
    --keep-alive "$KEEPALIVE" \
    --access-logfile - \
    --error-logfile - \
    --log-level "$LOG_LEVEL" \
    --preload \
    ${GUNICORN_MAX_REQUESTS:+--max-requests "$GUNICORN_MAX_REQUESTS"} \
    ${GUNICORN_MAX_REQUESTS_JITTER:+--max-requests-jitter "$GUNICORN_MAX_REQUESTS_JITTER"} \
    "$@"
