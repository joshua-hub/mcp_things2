#!/bin/bash
echo "Testing /v1/health"
curl -sf http://localhost:8000/v1/health && echo "OK" || echo "FAIL" 