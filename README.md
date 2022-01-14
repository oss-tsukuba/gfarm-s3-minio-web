# gfarm-s3-minio-web

## Overview

- Gfarm S3 is a S3 compatible object storage server for Gfarm.
- Based on gfarm-s3-minio (MinIO with gateway-gfarm).
- Web UI:
    - Login with password of .gfarm_shared_key or grid-proxy-init or myproxy-logon .
    - Start MinIO by each user.
    - Display Access Key ID and Secret Access Key for S3 client.
    - Share files with other Gfarm users under dedicated directory.
    - Control ACL.
- Docker container:
    - Automatically copy Gfarm configuration and credential files from home directories on host OS to the container.

## Requirements

- Username mapping of Gfarm and My Proxy must be equal.
