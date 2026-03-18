#!/bin/bash

# Usage:
#   Dev   (localhost):                        ./generate-certs.sh
#   Prod  (Let's Encrypt):                    DOMAIN=transcendentes.space CERTBOT_EMAIL=you@email.com ./generate-certs.sh
#   Prod  (self-signed fallback, IP only):    SERVER_IP=157.230.58.126 ./generate-certs.sh

CERTS_DIR="$(dirname "$0")/../certs"
DOMAIN="${DOMAIN:-}"
SERVER_IP="${SERVER_IP:-}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"

mkdir -p "$CERTS_DIR"

if [ -f "$CERTS_DIR/server.crt" ] && [ -f "$CERTS_DIR/server.key" ]; then
    echo "Certificates already exist in $CERTS_DIR"
    exit 0
fi

if [ -n "$DOMAIN" ]; then
    # Production: trusted certificate via Let's Encrypt (certbot)
    echo "Requesting Let's Encrypt certificate for: $DOMAIN ..."

    if ! command -v certbot &>/dev/null; then
        echo "  certbot not found — installing..."
        apt-get update -qq && apt-get install -y -qq certbot
    fi

    if [ -z "$CERTBOT_EMAIL" ]; then
        echo "ERROR: CERTBOT_EMAIL is required for Let's Encrypt."
        echo "  Export it before running:"
        echo "  CERTBOT_EMAIL=you@email.com DOMAIN=$DOMAIN ./generate-certs.sh"
        exit 1
    fi

    # certbot standalone uses port 80 — must be free before calling this
    certbot certonly --standalone --non-interactive --agree-tos \
        --email "$CERTBOT_EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN"

    # symlink into our certs dir so nginx picks them up
    ln -sf "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$CERTS_DIR/server.crt"
    ln -sf "/etc/letsencrypt/live/$DOMAIN/privkey.pem"   "$CERTS_DIR/server.key"

    echo "Let's Encrypt certificate installed."
    echo "Remember to set up auto-renewal (see deploy.sh output)."

elif [ -n "$SERVER_IP" ]; then
    # Fallback: self-signed cert for a raw IP
    echo "Generating self-signed SSL certificate for IP: $SERVER_IP ..."

    cat > /tmp/openssl-san.cnf <<EOF
[req]
default_bits       = 4096
prompt             = no
default_md         = sha256
distinguished_name = dn
x509_extensions    = v3_req

[dn]
CN = $SERVER_IP

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = $SERVER_IP
EOF

    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$CERTS_DIR/server.key" \
        -out    "$CERTS_DIR/server.crt" \
        -days   365 \
        -config /tmp/openssl-san.cnf

    rm /tmp/openssl-san.cnf
else
    # Development: locally-trusted cert for localhost using mkcert
    if ! command -v mkcert &> /dev/null; then
        echo "ERROR: mkcert is not installed."
        echo ""
        echo "Install mkcert:"
        echo "  Ubuntu/Debian: sudo apt install mkcert"
        echo "  Arch:          sudo pacman -S mkcert"
        echo "  macOS:         brew install mkcert"
        echo ""
        echo "Then install the local CA:"
        echo "  mkcert -install"
        exit 1
    fi

    echo "Checking if local CA is installed..."
    if ! mkcert -CAROOT &> /dev/null || [ ! -f "$(mkcert -CAROOT)/rootCA.pem" ]; then
        echo "Installing local CA (may require sudo)..."
        mkcert -install
    fi

    echo "Generating locally-trusted SSL certificates with mkcert..."
    cd "$CERTS_DIR"
    mkcert -key-file server.key -cert-file server.crt localhost 127.0.0.1 ::1
fi

# chmod only applies to files we own (not Let's Encrypt managed files)
if [ -z "$DOMAIN" ]; then
    chmod 600 "$CERTS_DIR/server.key"
    chmod 644 "$CERTS_DIR/server.crt"
fi

echo "SSL certificates generated successfully in $CERTS_DIR"
