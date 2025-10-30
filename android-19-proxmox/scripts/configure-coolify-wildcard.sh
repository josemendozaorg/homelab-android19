#!/bin/bash
# Configure Coolify wildcard domain via API
# This enables automatic subdomain generation for deployed applications

set -e

COOLIFY_URL="http://192.168.0.160:8000"
COOLIFY_EMAIL="josephrichard7@gmail.com"
COOLIFY_PASSWORD="8n@~v#Pc5:0QE1ri<,0sVX:Z3QnK,sMa"
WILDCARD_DOMAIN="coolify.homelab"

echo "======================================"
echo "Coolify Wildcard Domain Configuration"
echo "======================================"
echo "URL: $COOLIFY_URL"
echo "Wildcard Domain: $WILDCARD_DOMAIN"
echo ""

# Step 1: Get server UUID
echo "[1/3] Fetching server information..."
SERVER_RESPONSE=$(curl -s \
  -u "$COOLIFY_EMAIL:$COOLIFY_PASSWORD" \
  "$COOLIFY_URL/api/v1/servers")

echo "Server API Response:"
echo "$SERVER_RESPONSE" | jq '.' 2>/dev/null || echo "$SERVER_RESPONSE"
echo ""

# Extract server UUID (first server)
SERVER_UUID=$(echo "$SERVER_RESPONSE" | jq -r '.[0].uuid // .uuid // empty' 2>/dev/null)

if [ -z "$SERVER_UUID" ]; then
    echo "❌ ERROR: Could not get server UUID"
    echo "Response: $SERVER_RESPONSE"
    exit 1
fi

echo "✅ Server UUID: $SERVER_UUID"
echo ""

# Step 2: Update wildcard domain
echo "[2/3] Configuring wildcard domain..."
UPDATE_RESPONSE=$(curl -s -X PATCH \
  -u "$COOLIFY_EMAIL:$COOLIFY_PASSWORD" \
  -H "Content-Type: application/json" \
  -d "{\"wildcard_domain\": \"$WILDCARD_DOMAIN\"}" \
  "$COOLIFY_URL/api/v1/servers/$SERVER_UUID")

echo "Update API Response:"
echo "$UPDATE_RESPONSE" | jq '.' 2>/dev/null || echo "$UPDATE_RESPONSE"
echo ""

# Step 3: Verify configuration
echo "[3/3] Verifying configuration..."
VERIFY_RESPONSE=$(curl -s \
  -u "$COOLIFY_EMAIL:$COOLIFY_PASSWORD" \
  "$COOLIFY_URL/api/v1/servers/$SERVER_UUID")

CONFIGURED_DOMAIN=$(echo "$VERIFY_RESPONSE" | jq -r '.wildcard_domain // empty' 2>/dev/null)

if [ "$CONFIGURED_DOMAIN" = "$WILDCARD_DOMAIN" ]; then
    echo "✅ SUCCESS: Wildcard domain configured!"
    echo ""
    echo "======================================"
    echo "Configuration Summary"
    echo "======================================"
    echo "Server UUID: $SERVER_UUID"
    echo "Wildcard Domain: $CONFIGURED_DOMAIN"
    echo ""
    echo "Applications will be accessible via:"
    echo "  <app-name>.<random-hash>.<env>.$WILDCARD_DOMAIN"
    echo ""
    echo "Example:"
    echo "  my-app.abc123.prod.$WILDCARD_DOMAIN"
    echo "======================================"
else
    echo "⚠️  WARNING: Wildcard domain may not be configured correctly"
    echo "Expected: $WILDCARD_DOMAIN"
    echo "Got: $CONFIGURED_DOMAIN"
    echo ""
    echo "Full server response:"
    echo "$VERIFY_RESPONSE" | jq '.' 2>/dev/null || echo "$VERIFY_RESPONSE"
fi
