#!/bin/bash
# Test CORS configuration

BACKEND_URL="http://localhost:5000"
FRONTEND_URL="https://precision-farming-ihij.onrender.com"

echo "Testing CORS Configuration..."
echo "================================"

# Test OPTIONS preflight request
echo ""
echo "1. Testing OPTIONS preflight request:"
curl -X OPTIONS "$BACKEND_URL/api/predict" \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v 2>&1 | grep -E "< HTTP|Access-Control"

# Test actual POST request
echo ""
echo "2. Testing POST request with CORS headers:"
curl -X POST "$BACKEND_URL/api/health" \
  -H "Origin: $FRONTEND_URL" \
  -H "Content-Type: application/json" \
  -v 2>&1 | grep -E "< HTTP|Access-Control"

# Test health endpoint
echo ""
echo "3. Testing /api/health endpoint:"
curl -X GET "$BACKEND_URL/api/health" \
  -H "Origin: $FRONTEND_URL" \
  -H "Content-Type: application/json" \
  -s | jq .

echo ""
echo "================================"
echo "CORS test complete!"
