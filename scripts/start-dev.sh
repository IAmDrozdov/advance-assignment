#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

API_URL="${MOCK_PROVIDER_URL:-https://interview-mock-provider.r6zcf729z3zke.us-east-1.cs.amazonlightsail.com}"
API_KEY="${MOCK_PROVIDER_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "Error: MOCK_PROVIDER_API_KEY not set in .env"
    exit 1
fi

echo "==> Deleting existing webhooks..."
curl -s -X DELETE "$API_URL/api/v1/webhooks/payments" \
    -H "Authorization: Bearer $API_KEY" || true
curl -s -X DELETE "$API_URL/api/v1/webhooks/transactions" \
    -H "Authorization: Bearer $API_KEY" || true
echo "Done."

pkill -f "ngrok http" 2>/dev/null || true
sleep 1

echo "==> Starting ngrok..."
ngrok http 8000 > /dev/null 2>&1 &
NGROK_PID=$!

echo "Waiting for ngrok to start..."
sleep 3

NGROK_URL=""
for i in {1..10}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)
    if [ -n "$NGROK_URL" ]; then
        break
    fi
    sleep 1
done

if [ -z "$NGROK_URL" ]; then
    echo "Error: Could not get ngrok URL"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo "Ngrok URL: $NGROK_URL"

echo "==> Registering payments webhook..."
curl -s -X POST "$API_URL/api/v1/webhooks" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$NGROK_URL/webhooks/payments\", \"webhook_type\": \"payments\"}"
echo ""

echo "==> Registering transactions webhook..."
curl -s -X POST "$API_URL/api/v1/webhooks" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$NGROK_URL/webhooks/transactions\", \"webhook_type\": \"transactions\"}"
echo ""

echo ""
echo "=========================================="
echo "Setup complete!"
echo "Ngrok URL: $NGROK_URL"
echo "Ngrok PID: $NGROK_PID"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop ngrok and cleanup..."

cleanup() {
    echo ""
    echo "==> Cleaning up..."
    echo "Deleting webhooks..."
    curl -s -X DELETE "$API_URL/api/v1/webhooks/payments" \
        -H "Authorization: Bearer $API_KEY" || true
    curl -s -X DELETE "$API_URL/api/v1/webhooks/transactions" \
        -H "Authorization: Bearer $API_KEY" || true
    echo "Stopping ngrok..."
    kill $NGROK_PID 2>/dev/null || true
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM

wait $NGROK_PID
