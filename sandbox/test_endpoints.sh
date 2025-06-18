#!/bin/bash
echo "Testing /health"
curl -sf http://localhost:8001/health && echo "OK" || echo "FAIL" 