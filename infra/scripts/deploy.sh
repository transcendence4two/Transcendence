#!/bin/bash
# Production deploy script for Ubuntu 24.04 VPS
# Usage: CERTBOT_EMAIL=you@email.com bash infra/scripts/deploy.sh
set -euo pipefail

DOMAIN="transcendentes.space"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "==> Deploying Transcendence at https://$DOMAIN"
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
echo "[3/5] Generating SSL certificates for $DOMAIN..."
# certbot standalone needs port 80 free — stop nginx if already running
if $COMPOSE --env-file .env -f infra/docker/docker-compose.yml ps nginx 2>/dev/null | grep -q "Up"; then
    echo "  Stopping nginx temporarily for certbot..."
    $COMPOSE --env-file .env -f infra/docker/docker-compose.yml stop nginx
fi
DOMAIN="$DOMAIN" CERTBOT_EMAIL="$CERTBOT_EMAIL" bash infra/scripts/generate-certs.sh

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
    STATUS=$(curl -sk -o /dev/null -w "%{http_code}" "https://$DOMAIN/api/health" || true)
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
echo " Application: https://$DOMAIN"
echo " Kibana:      https://$DOMAIN/kibana/"
echo "============================================"
echo ""
echo "Certificate auto-renewal (Let's Encrypt expires in 90 days):"
echo "  Run once to configure cron:"
echo "  echo '0 3 * * * certbot renew --pre-hook \"docker stop nginx\" --post-hook \"docker start nginx\" --quiet' | crontab -"
