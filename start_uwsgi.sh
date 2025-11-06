#!/bin/bash

# start_uwsgi.sh - Start Cellxgene Gateway with uWSGI
#
# PREREQUISITES:
# - uWSGI installed (pip install uwsgi)
# - Virtual environment activated or .venv present
# - .env file with CELLXGENE_LOCATION and CELLXGENE_DATA (or CELLXGENE_BUCKET)
#
# USAGE:
# ./start_uwsgi.sh

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

# uWSGI configuration
# WARNING: Multi-worker mode has cache synchronization issues (see plans/002-shared-cache-implementation.md)
# Each worker maintains its own in-memory cache, causing 404s for static assets when different
# workers handle requests for the same dataset. Use UWSGI_WORKERS=1 until shared cache is implemented.
WORKERS=${UWSGI_WORKERS:-1}
HOST=${GATEWAY_IP:-0.0.0.0}
PORT=${GATEWAY_PORT:-5005}
TIMEOUT=${UWSGI_TIMEOUT:-120}
THREADS=${UWSGI_THREADS:-1}

# Production optimization: enable backed mode to reduce memory usage
export GATEWAY_ENABLE_BACKED_MODE=${GATEWAY_ENABLE_BACKED_MODE:-true}

# Check if uwsgi is installed
if ! command -v uwsgi &> /dev/null; then
    echo "Error: uwsgi not found. Install with: pip install uwsgi"
    exit 1
fi

# Display configuration
echo "Starting Cellxgene Gateway with uWSGI..."
echo "Configuration:"
echo "  Data source: ${CELLXGENE_DATA:-$CELLXGENE_BUCKET}"
echo "  Binding to: $HOST:$PORT"
echo "  Workers: $WORKERS"
echo "  Threads: $THREADS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Backed mode: ${GATEWAY_ENABLE_BACKED_MODE}"
echo ""

cd "$SCRIPT_DIR"

# Start uWSGI with optimized settings
# Additional options you can add via environment variables:
# - UWSGI_MAX_REQUESTS: Restart worker after N requests (prevents memory leaks)
exec uwsgi \
    --http "$HOST:$PORT" \
    --module cellxgene_gateway.gateway:app \
    --workers "$WORKERS" \
    --threads "$THREADS" \
    --harakiri "$TIMEOUT" \
    --master \
    --enable-threads \
    --single-interpreter \
    --need-app \
    --die-on-term \
    --log-x-forwarded-for \
    ${UWSGI_MAX_REQUESTS:+--max-requests "$UWSGI_MAX_REQUESTS"} \
    "$@"
