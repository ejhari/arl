#!/bin/bash
# Build the ARL sandbox Docker image

set -e

echo "Building ARL sandbox Docker image..."
docker build \
    -f arl/integrations/sandbox/Dockerfile.sandbox \
    -t arl-sandbox:latest \
    arl/integrations/sandbox/

echo "✓ Sandbox image built successfully"

echo ""
echo "Verifying image..."
docker images arl-sandbox:latest

echo ""
echo "Testing image..."
docker run --rm arl-sandbox:latest python --version
