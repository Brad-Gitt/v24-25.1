#!/bin/bash

# Verify script for Allpodd system (person 5)

echo "Starting verification of Allpodd system..."

# Check if pod is running
if podman pod ps | grep -q allpodd; then
    echo "✓ Pod 'allpodd' is running"
else
    echo "✗ Pod 'allpodd' is not running"
    exit 1
fi

# Check containers
containers=("web" "app" "bidrag-db" "pseudonym-db")
for c in "${containers[@]}"; do
    if podman ps | grep -q "$c"; then
        echo "✓ Container '$c' is running"
    else
        echo "✗ Container '$c' is not running"
        exit 1
    fi
done

# Test web accessibility
if curl -s http://localhost:8080 | grep -q "BIDRAG"; then
    echo "✓ Web interface is accessible"
else
    echo "✗ Web interface is not accessible"
fi

# Test app endpoint
if curl -s http://localhost:8081 | grep -q "text/plain"; then
    echo "✓ App endpoint responds"
else
    echo "✗ App endpoint does not respond"
fi

# Check database files (if mounted)
# Note: In K8s, check PVC status instead

echo "Verification complete."

# start: QA-skript lagt til (person 5)
# slutt: QA-skript lagt til (person 5)