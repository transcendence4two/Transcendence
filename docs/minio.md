# MinIO Object Storage

MinIO is used in this project as an S3-compatible object storage service. Its primary role is to store and serve user avatars.

## Role in the Project

- **Avatar Storage**: All user profile pictures are stored in a dedicated bucket named `avatars`.
- **Public Access**: The `avatars` bucket is configured for anonymous download access, allowing the frontend to serve images directly using MinIO URLs.

## Access and Configuration

### Web Console

You can access the MinIO Web Console to manage buckets and objects through your browser:

- **URL**: [http://localhost:9001](http://localhost:9001)
- **API Endpoint**: [http://localhost:9000](http://localhost:9000)

### Credentials

The default credentials (controlled via `.env`) are:

- **Root User**: `admin`
- **Root Password**: `supersecret123`

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `MINIO_ROOT_USER` | Admin username for MinIO | `admin` |
| `MINIO_ROOT_PASSWORD` | Admin password for MinIO | `supersecret123` |
| `MINIO_ENDPOINT` | Internal endpoint for services | `minio:9000` |
| `MINIO_PUBLIC_URL` | Public URL for browser access | `http://localhost:9000` |

## Infrastructure Details

### Docker Services

- **`minio`**: The main storage server.
- **`minio-setup`**: A short-lived container that runs a setup script (`infra/scripts/setup-minio.sh`) to:
    1. Wait for MinIO to be ready.
    2. Create the `avatars` bucket if it doesn't exist.
    3. Set the `avatars` bucket policy to `download` (publicly readable).

### Volumes

- **`minio_data`**: Persistent volume used to store the actual objects and MinIO configuration.

## Development Usage

In the `usermanagement-service`, the `StorageService` (located in `src/infrastructure/storage.py`) handles communication with MinIO using the Python MinIO client.

When an avatar is uploaded:
1. A unique filename (UUID) is generated.
2. The file is uploaded to the `avatars` bucket.
3. A public URL is returned in the format: `${MINIO_PUBLIC_URL}/avatars/${filename}`.
