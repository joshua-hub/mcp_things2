#!/bin/bash
echo "Testing /health"
curl -sf http://localhost:8081/health && echo "OK" || echo "FAIL" 