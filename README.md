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
- RAM: 1～2GB per user

## Quick start (Install using Docker Compose)

- install Docker
- install Docker Compose
- create and edit .env file (see below)
    - specify Gfarm configuration
    - select Gfarm authentication method
    - Gfarm and local user name mapping
    - server name
- create docker-compose.override.yml
    - example: `ln -s docker-compose.override.yml.https docker-compose.override.yml`
    - or use one of other docker-compose.override.yml.*
    - or write docker-compose.override.yml for your environment
- check `make config`
- run `make reborn-withlog`

TODO

## Install on real machine

Please refer to:

- docker/gfminio/Dockerfile
- docker/gfminio/entrypoint.sh

- Gfarm source: docker/dev/common/s3/setup.sh

## HTTPS and Certificates and Reverse proxy

docker-compose.override.yml.https is an example to setup
using a reverse proxy and using self signed certificates.

## Configuration file (.env)

example:

```
```
