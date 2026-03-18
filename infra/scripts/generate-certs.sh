#!/bin/bash

# Usage:
#   Dev  (localhost):  ./generate-certs.sh
#   Prod (VPS IP):     SERVER_IP=157.230.58.126 ./generate-certs.sh

CERTS_DIR="$(dirname "$0")/../certs"
SERVER_IP="${SERVER_IP:-}"

mkdir -p "$CERTS_DIR"

if [ -f "$CERTS_DIR/server.crt" ] && [ -f "$CERTS_DIR/server.key" ]; then
    echo "Certificates already exist in $CERTS_DIR"
    exit 0
fi

if [ -n "$SERVER_IP" ]; then
    # Production: self-signed cert for a public IP using openssl
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

chmod 600 "$CERTS_DIR/server.key"
chmod 644 "$CERTS_DIR/server.crt"

echo "SSL certificates generated successfully in $CERTS_DIR"
