FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

ARG BASEDIR=./docker/gfminio

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install \
    systemd \
    systemd-sysv \
    sudo \
    rsyslog \
    build-essential \
    libssl-dev \
    libglobus-gssapi-gsi-dev \
    pkg-config \
    postgresql-client \
    libacl1-dev \
    libfuse-dev \
    fuse \
    git \
    globus-gsi-cert-utils-progs \
    globus-proxy-utils \
    curl \
    git \
    nginx \
    ssl-cert \
    uuid \
    myproxy \
    python3 \
    python3-pip \
    python3-dev \
    npm \
    language-pack-ja \
    language-pack-en \
    vim
# RUN apt-get clean && rm -rf /var/lib/apt/lists/*

### from docker-compose.yml or docker-compose.override.yml
ARG GFARM_SRC_URL
ARG GFARM2FS_SRC_URL
ARG SHARED_DIR=/share
ARG MYPROXY_SERVER
ARG GFARM_S3_MINIO_WEB_HOST=gfarm-s3
ARG WORKDIR=/root
ARG MINIO_BUILD_DIR=/build_cache
ARG WSGI_USER=_gfarm_s3
ARG WSGI_GROUP=${WSGI_USER}
ARG WSGI_HOMEDIR=/home/${WSGI_USER}
ARG WSGI_PORT=8000
ARG CACHE_DIR=/var/cache/gfarm-s3
ARG CACHE_SIZE=1024
### XXX TODO MINIO_LOCALTMP

ARG HTTPD_DOCUMENT_ROOT=/var/www/html

### install gfarm

RUN mkdir -p ${WORKDIR} \
    && cd ${WORKDIR} \
    && curl -sLJO ${GFARM_SRC_URL} \
    && ARCH=`ls -1 gfarm-*.tar.gz` \
    && tar xf ${ARCH} \
    && DIRNAME=`echo ${ARCH} | sed 's/\.tar\.gz$//g'` \
    && cd ${DIRNAME} \
    && ./configure --with-globus --without-openldap --without-postgresql \
    && make -j \
    && make -j install \
    && ldconfig \
    && cd ${WORKDIR} \
    && curl -sLJO ${GFARM2FS_SRC_URL} \
    && ARCH=`ls -1 gfarm2fs-*.tar.gz` \
    && tar xf ${ARCH} \
    && DIRNAME=`echo ${ARCH} | sed 's/\.tar\.gz$//g'` \
    && cd ${DIRNAME} \
    && ./configure \
    && make -j \
    && make -j install

RUN python3 -m pip install Django gunicorn boto3

COPY ${BASEDIR}/nginx-gfarm-s3.conf /etc/nginx/sites-available/gfarm
RUN ln -s /etc/nginx/sites-available/gfarm /etc/nginx/sites-enabled/gfarm \
    && rm -f /etc/nginx/sites-enabled/default
RUN mkdir -p ${HTTPD_DOCUMENT_ROOT}
COPY ${BASEDIR}/index.html ${HTTPD_DOCUMENT_ROOT}/index.html

# ARG GFARM_S3_MINIO_WEB_BRANCH=router
# RUN cd ${WORKDIR} \
#    && git clone https://github.com/oss-tsukuba/gfarm-s3-minio-web.git \
#    && git checkout ${GFARM_S3_MINIO_WEB_BRANCH}
COPY ./ ${WORKDIR}/gfarm-s3-minio-web

COPY ${BASEDIR}/entrypoint.sh /entrypoint.sh

ENV SHARED_DIR=${SHARED_DIR}
ENV MYPROXY_SERVER=${MYPROXY_SERVER}
ENV GFARM_S3_MINIO_WEB_HOST=${GFARM_S3_MINIO_WEB_HOST}
ENV WORKDIR=${WORKDIR}
ENV MINIO_BUILD_DIR=${MINIO_BUILD_DIR}

### TODO WSGI_ -> GFARM_S3_
ENV WSGI_USER=${WSGI_USER}
ENV WSGI_GROUP=${WSGI_USER}
ENV WSGI_HOMEDIR=${WSGI_HOMEDIR}
ENV WSGI_PORT=${WSGI_PORT}
ENV CACHE_DIR=${CACHE_DIR}
ENV CACHE_SIZE=${CACHE_SIZE}
### XXX TODO MINIO_LOCALTMP

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/sbin/init"]
