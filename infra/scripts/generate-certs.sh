#!/bin/bash

CERTS_DIR="$(dirname "$0")/../certs"

mkdir -p "$CERTS_DIR"

# Check if mkcert is installed
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

if [ -f "$CERTS_DIR/server.crt" ] && [ -f "$CERTS_DIR/server.key" ]; then
    echo "Certificates already exist in $CERTS_DIR"
    exit 0
fi

echo "Checking if local CA is installed..."
if ! mkcert -CAROOT &> /dev/null || [ ! -f "$(mkcert -CAROOT)/rootCA.pem" ]; then
    echo "Installing local CA (may require sudo)..."
    mkcert -install
fi

echo "Generating locally-trusted SSL certificates with mkcert..."

cd "$CERTS_DIR"
mkcert -key-file server.key -cert-file server.crt localhost 127.0.0.1 ::1

chmod 600 "$CERTS_DIR/server.key"
chmod 644 "$CERTS_DIR/server.crt"

echo "SSL certificates generated successfully in $CERTS_DIR"
