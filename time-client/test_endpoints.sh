#!/bin/bash
echo "Testing /health"
curl -sf http://localhost:8003/health && echo "OK" || echo "FAIL" 