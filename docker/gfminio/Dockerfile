FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

ARG BASEDIR=./docker/gfminio

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install \
    supervisor \
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
ARG WORKDIR=/root
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

RUN python3 -m pip install 'Django<=4' gunicorn boto3

RUN AWSCLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
    && AWSCLI_ZIP=awscliv2.zip \
    && apt-get -y update \
    && apt-get install -y unzip groff-base \
    && curl ${AWSCLI_URL} -o ${AWSCLI_ZIP} \
    && unzip -q -o ${AWSCLI_ZIP} \
    && ./aws/install --update \
    && /usr/local/bin/aws --version

COPY ${BASEDIR}/nginx-gfarm-s3-site.conf /usr/local/etc/nginx-gfarm-s3-site.conf
COPY ${BASEDIR}/nginx-gfarm-s3-include.conf /etc/nginx/sites-available/gfarm
RUN ln -s /etc/nginx/sites-available/gfarm /etc/nginx/sites-enabled/gfarm \
    && rm -f /etc/nginx/sites-enabled/default
RUN mkdir -p ${HTTPD_DOCUMENT_ROOT}
COPY ${BASEDIR}/index.html ${HTTPD_DOCUMENT_ROOT}/index.html

COPY ${BASEDIR}/entrypoint.sh /entrypoint.sh
COPY ${BASEDIR}/supervisord.conf /supervisord.conf

COPY ./ ${WORKDIR}/gfarm-s3-minio-web

ENV WORKDIR=${WORKDIR}
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/supervisord.conf"]
