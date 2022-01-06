#!/bin/bash

# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-

set -eu
set -o pipefail
#set -x

### from build args
: WORKDIR=${WORKDIR}

### from enviroment
: DJANGO_DEBUG=${DJANGO_DEBUG}
: SERVER_URL=${SERVER_URL}
: ALLOWED_HOSTS=${ALLOWED_HOSTS}
: CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
: MYPROXY_SERVER=${MYPROXY_SERVER}
: GFARM_S3_SHARED_DIR=${GFARM_S3_SHARED_DIR}
: GFARM_S3_BUILD_DIR=${GFARM_S3_BUILD_DIR}
: GFARM_S3_USERNAME=${GFARM_S3_USERNAME}
: GFARM_S3_GROUPNAME=${GFARM_S3_USERNAME}
# TODO GFARM_S3_LOCALTMP
: CACHE_DIR=${CACHE_DIR}
: CACHE_SIZE=${CACHE_SIZE}

TZ=${TZ:-Asia/Tokyo}
export TZ

GFARM_S3_HOMEDIR=/home/${GFARM_S3_USERNAME}

URL_REGEXP="^([^/:]+?)://([^/:]+?):?([[:digit:]]+)?(/.*)?"
[[ ${SERVER_URL} =~ ${URL_REGEXP} ]]
URL_SCHEME=${BASH_REMATCH[1]}
SERVER_NAME=${BASH_REMATCH[2]}
SERVER_PORT=${BASH_REMATCH[3]}
URL_PATH=${BASH_REMATCH[4]}

# update SERVER_URL
SERVER_URL="${URL_SCHEME}://${SERVER_NAME}"
if [ -n "${SERVER_PORT}" ]; then
    SERVER_URL="${SERVER_URL}:${SERVER_PORT}"
fi

# update when empty
ALLOWED_HOSTS=${ALLOWED_HOSTS:-${SERVER_NAME}}
# update when empty
CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS:-${SERVER_URL}}

HOME_BASE=/home
USERMAP=/gfarm-s3-usermap.conf

COPY_HOME_INITIALIZED_FILE="${HOME_BASE}/_copy_home_initialized"

#TODO gfarm branch
GFARM_S3_MINIO_BRANCH=gfarmmerge

WEBUI_ADDR="unix:/tmp/gfarm-s3-webui.sock"
ROUTER_ADDR="unix:/tmp/gfarm-s3-router.sock"

### cache files in GFARM_S3_BUILD_DIR to build.
install_gf_s3() {
    groupadd -K GID_MIN=100 ${GFARM_S3_GROUPNAME} && \
    useradd -K UID_MIN=100 -m ${GFARM_S3_USERNAME} -g ${GFARM_S3_GROUPNAME} -d ${GFARM_S3_HOMEDIR} -s /bin/bash

    MINIO_WORKDIR=${GFARM_S3_BUILD_DIR}/minio/work/build
    GFARM_S3_MINIO_DIR=${MINIO_WORKDIR}/gfarm-s3-minio
    if [ ! -d "${GFARM_S3_MINIO_DIR}" ]; then
        mkdir -p ${MINIO_WORKDIR} \
        && cd ${MINIO_WORKDIR} \
        && git clone https://github.com/oss-tsukuba/gfarm-s3-minio.git \
        && cd gfarm-s3-minio \
        && git checkout ${GFARM_S3_MINIO_BRANCH}
    fi

    PREFIX=/usr/local
    SYSCONFDIR=${PREFIX}/etc

    cd ${WORKDIR}/gfarm-s3-minio-web \
    && ./configure \
    --prefix=${PREFIX} \
    --sysconfdir=${SYSCONFDIR} \
    --with-gfarm=/usr/local \
    --with-globus=/usr \
    --with-myproxy=/usr \
    --with-gunicorn=/usr/local \
    --with-gfarm-s3-homedir=${GFARM_S3_HOMEDIR} \
    --with-gfarm-s3-user=${GFARM_S3_USERNAME} \
    --with-gfarm-s3-group=${GFARM_S3_GROUPNAME} \
    --with-cache-basedir=${CACHE_DIR} \
    --with-cache-size=${CACHE_SIZE} \
    --with-myproxy-server=${MYPROXY_SERVER} \
    --with-gfarm-shared-dir=${GFARM_S3_SHARED_DIR} \
    --with-minio-builddir=${GFARM_S3_BUILD_DIR} \
    --with-webui-addr=${WEBUI_ADDR} \
    --with-router-addr=${ROUTER_ADDR} \
    && make \
    && make install \
    && mkdir -p ${CACHE_DIR} \
    && chmod 1777 ${CACHE_DIR}

    #TODO in "make install"
    DJANGO_SECRET_KEY=${SYSCONFDIR}/django_secret_key.txt
    if [ ! -f ${DJANGO_SECRET_KEY} ]; then
        #pip install django-generate-secret-key
        #cd ${GFARM_S3_HOMEDIR}/gfarm-s3
        #python3 manage.py generate_secret_key "${DJANGO_SECRET_KEY}"
        python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > "${DJANGO_SECRET_KEY}"
        chmod 400 "${DJANGO_SECRET_KEY}"
        chown ${GFARM_S3_USERNAME}:root "${DJANGO_SECRET_KEY}"
    fi

    CONF_OVERWRITE=${SYSCONFDIR}/gfarm-s3-overwrite.conf
    cat <<EOF > "${CONF_OVERWRITE}"
#GFARM_S3_LOG_OUTPUT=stderr

DJANGO_DEBUG=${DJANGO_DEBUG}
ALLOWED_HOSTS=${ALLOWED_HOSTS}

# required by Django 4 or later
CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}

WEBUI_ADDR=${WEBUI_ADDR}
ROUTER_ADDR=${ROUTER_ADDR}
EOF

    if which systemctl > /dev/null 2>&1; then
        systemctl enable gfarm-s3-webui.service
        systemctl enable gfarm-s3-router.service
    fi
}

### runs only once

SPOOL_DIR=/var/spool
MINIO_INIT_FLAG_PATH=${SPOOL_DIR}/minio
if [ ! -f ${MINIO_INIT_FLAG_PATH} ]; then
    time install_gf_s3
    echo "gfarm s3 installation completed"

    sed -i -e 's/^NAME_COMPATIBILITY=STRICT_RFC2818$/NAME_COMPATIBILITY=HYBRID/' /etc/grid-security/gsi.conf

    mkdir -p ${SPOOL_DIR}
    touch ${MINIO_INIT_FLAG_PATH}
fi

### update everytime after restart

group_exist() {
    gid=$1
    grep -q ":x:${gid}:" /etc/group
}

# mksym() {
#     SRC="$1"
#     DST="$2"
#     [ -h "${DST}" ] || ln -s "${SRC}" "${DST}"
# }

wait_for_copy_home() {
    while [ ! -e $COPY_HOME_INITIALIZED_FILE ]; do
        echo "wait for initializing copy_home container"
        sleep 1
    done
}

wait_for_copy_home

SAVE_IFS="$IFS"
IFS=$'\n'
for line in $(cat "${USERMAP}"); do
    GFARM_USERNAME=$(echo "${line}" | awk -F : '{print $1}' | sed "s/\s//g")
    LOCAL_USERNAME=$(echo "${line}" | awk -F : '{print $2}' | sed "s/\s//g")
    ACCESSKEY_ID=$(echo "${line}" | awk -F : '{print $3}' | sed "s/\s//g")

    [ -z "${GFARM_USERNAME}" ] && continue
    [ "${GFARM_USERNAME:0:1}" = "#" ] && continue

    HOMEDIR="${HOME_BASE}/${LOCAL_USERNAME}"
    USER_UID=$(stat -c %u "${HOMEDIR}")
    USER_GID=$(stat -c %g "${HOMEDIR}")
    GROUP_NAME="gid${USER_GID}"

    if group_exist "${USER_GID}"; then
        :
    else
        groupadd -g "${USER_GID}" "${GROUP_NAME}"
    fi

    if id -u "${LOCAL_USERNAME}" > /dev/null 2>&1; then
        :
    else
        useradd -s /bin/bash -g "${USER_GID}" -b "${HOME_BASE}" \
                --no-create-home -u "${USER_UID}" "${LOCAL_USERNAME}"
        usermod -a -G "${GFARM_S3_GROUPNAME}" "${LOCAL_USERNAME}"
    fi

    ### create myproxy-logon script for the user
    if [ -n "${MYPROXY_SERVER}" ]; then
        MYPROXY_LOGON="${HOMEDIR}/myproxy-logon-${GFARM_USERNAME}"
        cat <<EOF > "${MYPROXY_LOGON}"
#/bin/sh
myproxy-logon -s "${MYPROXY_SERVER}" -l "${GFARM_USERNAME}" \$@
EOF
        chown "${LOCAL_USERNAME}" "${MYPROXY_LOGON}"
        chmod u+x "${MYPROXY_LOGON}"
    fi

    gfarm-s3-useradd "${GFARM_USERNAME}" "${LOCAL_USERNAME}" "${ACCESSKEY_ID}" || true  ## may fail

    ### resume minio
    sudo -u "${GFARM_S3_USERNAME}" gfarm-s3-login --quiet --authenticated "DUMMY_AUTH_METHOD" resume "${GFARM_USERNAME}" "DUMMY_PASSWORD" > /dev/null &
    ##### backgroud (may fail, ignore)
done
### wait for resuming minio
wait
IFS="$SAVE_IFS"

exec "$@"
