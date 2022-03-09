# gfarm-s3-minio-web

## Overview

- gfarm-s3-minio-web is Web UI to manage gfarm-s3-minio.
- gfarm-s3-minio is an S3 compatible object storage server for Gfarm
  based on MinIO (gateway-gfarm is added).
    - https://github.com/oss-tsukuba/gfarm-s3-minio
    - branch name: gfarm
- Web UI:
    - Login with password of .gfarm_shared_key or grid-proxy-init or myproxy-logon .
    - Start MinIO by each user.
    - Display Access Key ID and Secret Access Key for S3 client.
    - Share files with other Gfarm users under dedicated directory.
    - Control ACL.
- Docker container:
    - Simple setup
    - Automatically copy Gfarm configuration and credential files from home directories on host OS to the container.

## Requirements

- Username mapping of Gfarm and My Proxy must be equal.
- RAM: 1GB or more per user (per minio process)
- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/)
    - v1 : https://docs.docker.com/compose/install/
    - v2 (Recommended): https://docs.docker.com/compose/cli-command/#install-on-linux
- GNU make
- Gfarm configuration file (gfarm2.conf)

## Quick start (Install using Docker Compose)

Users on host OS and their configuration files for Gfarm are copied
automatically in Docker container.

- install Docker
- install Docker Compose
- run `cd ./docker` in this source directory
- create and edit `config.env` (see details below)
    - specify Gfarm configuration
    - select Gfarm authentication method
    - server name
- ask Gfarm administrator to prepare the shared directory, and specify the Gfarm directory as GFARM_S3_SHARED_DIR in `config.env`
  ```
  # Example of preparation for shared directory:
  SHARED_DIR=/share
  gfsudo gfmkdir -p "${SHARED_DIR}"
  gfsudo gfchmod 0755 "${SHARED_DIR}"

  for u in $(gfuser); do
      NAME="$SHARED_DIR/$u"
      gfsudo gfmkdir -p "$NAME"
      gfsudo gfchmod 0755 "$NAME"
      gfsudo gfchown $u:gfarmadm "$NAME"
  done
  ```
- create and edit `gfarm-s3-usermap.conf` in GFARM_CONF_DIR directory to specify the available users
    - one user per line, separate by colons
    - Format:
        - `<Gfarm Username>:<Local Username>:<S3 Accesskey ID>`
    - Example:
      ```
      hpciXXXX01:user1:hpciXXXX01
      hpciXXXX02:user2:hpciXXXX02
      ```
- create `docker-compose.override.yml`
    - example: `ln -s docker-compose.override.yml.https docker-compose.override.yml` to use HTTPS
    - or use one of other `docker-compose.override.yml.*`
    - or write `docker-compose.override.yml` for your environment
- run `make config` to check configurations.
- run `make selfsigned-cert-generate` to activate HTTPS when using HTTPS.
- run `make reborn` to create and start containers.
    - If containers exist, these will be recreated.
    - Persistent data (coniguration files, build-cache and etc.) is not removed.
- copy the following files for HTTPS to `gfarm-s3-revproxy-1:/etc/nginx/certs` volume when using HTTPS and not using selfsigned certificate.
    - NOTE: HTTPS port is disabled when certificate files do not exist.
    - prepare the following files
        - ${SERVER_NAME}.key (SSL_KEY)
        - ${SERVER_NAME}.csr (SSL_CSR)
        - ${SERVER_NAME}.crt (SSL_CERT)
        - and use `sudo docker cp <filename> gfarm-s3-revproxy-1:/etc/nginx/certs/<filename>` to copy a file
        - and run `make restart@revproxy`
    - or (unsurveyed:) write new docker-compose.override.yml and use acme-companion for nginx-proxy to use Let's Encrypt certificate
        - https://github.com/nginx-proxy/acme-companion
        - https://github.com/nginx-proxy/acme-companion/blob/main/docs/Docker-Compose.md
- open the URL in a browser
   - Example: `https://<hostname>/`
- Web UI
    - login
        - username: `<Gfarm username>`
        - password: `<password>`
            - .gfarm_shared_key : output of gfarm-s3-sharedsecret-password command
                - or run `gfkey -l | openssl sha256 -r | awk '{ print $1 }'`
                - or run `cat .gfarm_shared_key | openssl sha256 -r | awk '{ print $1 }'`
            - grid-proxy-init : pass phrase
            - myproxy-logon : password
    - push `Start` button to start Gfarm S3 server per user
    - open `Sharing` page to share other users per bucket
- AWS CLI (S3 client)
     - Download and Install
         - https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
     - aws configure --profile <new profile name>
         - Access Key ID
         - Secret Access Key
     - export AWS_EC2_METADATA_DISABLED=true
     - set --profile for aws cli to specify the profile name
     - set --endpoint-url for aws cli to specify the Gfarm S3 server URL
     - Example: `aws --endpoint-url ... --profile ... s3 mb s3://abcdefg`
- Other S3 clients
     - path-style option is required


## Install on real machine (not recommended, no details)

Please refer to:

- gfarm-s3-minio-web
    - docker/gfminio/Dockerfile
    - docker/gfminio/entrypoint.sh
- gfarm
    - docker/dev/common/s3/setup.sh

## HTTPS (SSL/TLS) and Certificates and Reverse proxy

docker-compose.override.yml.https is an example to setup
using a reverse proxy and using self signed certificates.

You can use other reverse proxy and describe
docker-compose.override.yml for the environment.

## Configuration file (docker/config.env)

Example:

```
SERVER_NAME=client1.local
#HTTP_PORT=61080
HTTPS_PORT=61443
MYPROXY_SERVER=portal.hpci.nii.ac.jp:7512
GSI_PROXY_HOURS=168
#GFARM_S3_SHARED_DIR=/home/hpXXXXXXX/hpciXXXXXX/minio-share
GFARM_S3_SHARED_DIR=/share
GFARM_CONF_DIR=/work/gfarm-conf/
GSI_CERTIFICATES_DIR=/etc/grid-security/certificates
```

configuration format:

```
KEY=VALUE
```

mandatory parameters:

### mandatory
- SERVER_NAME: server name (without port number, not URL)
- GFARM_S3_SHARED_DIR: Gfarm directory to share files
- GFARM_CONF_DIR : path to parent directory on host OS for the following files
    - gfarm2.conf: Gfarm configuration file
    - gfarm-s3-usermap.conf

Gfarm parameters (if necessary)
(default values are listed in docker-compose.yml):

- GSI_CERTIFICATES_DIR: `/etc/grid-security/certificates/` on host OS
- MYPROXY_SERVER: myproxy server (hostname:port)
- GSI_PROXY_HOUR: hours for grid-proxy-init or myproxy-logon

optional parameters (default values are listed in docker-compose.yml):

- HTTP_PORT: http port
- HTTPS_PORT: https port
- DEBUG: debug mode (1: enable)
- DJANGO_DEBUG: debug mode of Django (True or False)
- TZ: TZ environment variable
- http_proxy: http_proxy environment variable
- https_proxy: http_proxy environment variable
- GFARM_S3_MINIO_SRC_GIT_URL: gfarm-s3-minio URL (git repository)
- GFARM_S3_MINIO_SRC_GIT_BRANCH: gfarm-s3-minio branch
- GFARM_S3_MINIO_SRC_DIR: local gfarm-s3-minio instead of downloading
- GFARM_S3_WEBUI_THREADS: the number of threads of Web UI
- GFARM_S3_WEBUI_WORKERS: the number of workers of Web UI
- GFARM_S3_ROUTER_THREADS: the number of threads of S3 router
- GFARM_S3_ROUTER_WORKERS: the number of workers of S3 router
- GFARM_S3_LOCALTMP_SIZE_MB: size of local temp file directory per user
- ALLOWED_HOSTS: ALLOWED_HOSTS for Django
- CSRF_TRUSTED_ORIGINS: CSRF_TRUSTED_ORIGINS for Django
- GO_URL: Golang binary package URL
- HOMEDIR_BASE: parent directory for local (host OS) home directories
- SHARE_HOSTDIR: shared directory between host OS and containers

## Shared directory (GFARM_S3_SHARED_DIR)

GFARM_S3_SHARED_DIR looks like the following via S3 client.

- sss (virtual bucket to other users)
    - username1
        - bucket
           - object
           - ...
        - ....
    - username2
    - ...
- your_bucket1
    - object
    - ...
- your_bucket2
- ...

## Stop and Start

prepare:

```
cd ./docker
```

stop:

```
make stop
```

start:

```
make restart
```

## After updating configurations

```
make reborn
```

or

```
make reborn-withlog
```

## Use shell

```
make shell
```

## Update Gfarm credential

Normally, when Gfarm credential and configuration files
(.gfarm_shared_key, .globus, .gfarm2rc) for users are updated, the
files will be copied automatically from home directories to
containers.

If the files are not copied automatically, run the following:

```
make copy-home
```

## Update containers

- update gfarm-s3-minio-web source
- or, update `./docker/config.env`
- or, update `docker-compose.yml`
- or, run `make build-nocache` to update packages forcibly
- and run `make reborn`

## Backup

Please keep configuration files and passwords of Gfarm S3 in a safe space.
gfarm-s3-minio-web does not use data like a database.
Files of Gfarm will be stored carefully on Gfarm.

## Logging

- run `make logs@<container name>` for containers to show
    - NOTE: These logs are removed when running `make reborn` or `make down`

You can describe docker-compose.override.yml to change logging driver.

- https://docs.docker.com/compose/compose-file/compose-file-v3/#logging
- https://docs.docker.com/config/containers/logging/configure/

## for developers

- create Gfarm docker/dev environment
- and see `config.env-docker_dev`
- and merge the file into `config.env`
- and run `ln -s <path to gfarm/docker/dev/mnt/COPY_DIR> /work/gfarm-dev`
