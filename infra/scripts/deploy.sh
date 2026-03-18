#!/bin/bash
# Production deploy script for Ubuntu 24.04 VPS
set -euo pipefail

SERVER_IP="157.230.58.126"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> Deploying Transcendence on $SERVER_IP"
echo "    Repo root: $REPO_ROOT"
cd "$REPO_ROOT"

echo ""
echo "[1/5] Checking dependencies..."
for cmd in docker openssl; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "ERROR: '$cmd' is required but not installed."
        exit 1
    fi
done

if docker compose version &>/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
else
    echo "ERROR: neither 'docker compose' nor 'docker-compose' found."
    exit 1
fi

# ── 2. .env ────────────────────────────────────────────────────────────────
echo ""
echo "[2/5] Checking .env..."
if [ ! -f ".env" ]; then
    echo "  .env not found — copying from .env.example"
    cp .env.example .env
    echo ""
    echo "  !! STOP: fill in the required secrets in .env before continuing !!"
    echo "  Required fields (empty in .env.example):"
    grep -E '^[A-Z_]+=\s*$' .env | sed 's/^/    /'
    echo ""
    echo "  After editing .env, re-run this script."
    exit 1
fi

for var in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD JWT_SECRET ELASTIC_PASSWORD ELASTICSEARCH_PASSWORD; do
    value=$(grep -E "^${var}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
    if [ -z "$value" ]; then
        echo "ERROR: $var is not set in .env"
        exit 1
    fi
done
echo "  .env OK"

# ── 3. SSL certificates ────────────────────────────────────────────────────
echo ""
echo "[3/5] Generating SSL certificates for $SERVER_IP..."
SERVER_IP="$SERVER_IP" bash infra/scripts/generate-certs.sh

# ── 4. Build & start ───────────────────────────────────────────────────────
echo ""
echo "[4/5] Building and starting all services..."
$COMPOSE --env-file .env -f infra/docker/docker-compose.yml up --build -d

# ── 5. Health check ────────────────────────────────────────────────────────
echo ""
echo "[5/5] Waiting for services to be healthy (up to 120s)..."
sleep 10

MAX=24
for i in $(seq 1 $MAX); do
    STATUS=$(curl -sk -o /dev/null -w "%{http_code}" "https://$SERVER_IP/api/health" || true)
    if [ "$STATUS" = "200" ]; then
        echo "  ✓  /api/health returned 200"
        break
    fi
    echo "  ... attempt $i/$MAX — status: $STATUS"
    sleep 5
done

echo ""
echo "============================================"
echo " Deploy complete!"
echo " Application: https://$SERVER_IP"
echo " Kibana:      https://$SERVER_IP/kibana/"
echo "============================================"
echo ""
echo "NOTE: The SSL certificate is self-signed."
echo "Browsers will show a security warning — this is expected when using a raw IP."
echo "To eliminate the warning, point a domain at this IP and use Let's Encrypt:"
echo "  apt install certbot && certbot certonly --standalone -d yourdomain.com"
