#!/bin/sh

echo "Waiting for MinIO to be ready..."
for i in $(seq 1 30); do
    if mc alias set myminio http://minio:9000 "${MINIO_ROOT_USER:-admin}" "${MINIO_ROOT_PASSWORD:-supersecret123}" > /dev/null 2>&1; then
        echo "MinIO is ready!"
        break
    fi
    echo "Attempt $i: MinIO not ready yet, sleeping..."
    sleep 1
done

mc mb myminio/avatars || true
mc anonymous set download myminio/avatars

exit 0
