#!/bin/bash

# start_gunicorn.sh - Start Cellxgene Gateway with Gunicorn
#
# PREREQUISITES:
# - Gunicorn installed (included with cellxgene 1.3.0, or: pip install gunicorn)
# - Virtual environment activated or .venv present
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

cellxgene-gateway