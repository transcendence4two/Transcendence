#!/bin/sh

sleep 10

mc alias set myminio http://minio:9000 "${MINIO_ROOT_USER:-admin}" "${MINIO_ROOT_PASSWORD:-supersecret123}"
mc mb myminio/avatars || true
mc anonymous set download myminio/avatars

exit 0
