#!/bin/bash

set -eux -o pipefail

### from build args
: WORKDIR=${WORKDIR}

### from enviroment
: MYPROXY_SERVER=${MYPROXY_SERVER}
: GFARM_S3_SHARED_DIR=${GFARM_S3_SHARED_DIR}
: GFARM_S3_BUILD_DIR=${GFARM_S3_BUILD_DIR}
: GFARM_S3_USERNAME=${GFARM_S3_USERNAME}
: GFARM_S3_GROUPNAME=${GFARM_S3_USERNAME}
# TODO GFARM_S3_LOCALTMP
: CACHE_DIR=${CACHE_DIR}
: CACHE_SIZE=${CACHE_SIZE}

GFARM_S3_HOMEDIR=/home/${GFARM_S3_USERNAME}

HOME_BASE=/home
HOST_HOME_BASE=/host_home
USERMAP=/gfarm-s3-usermap.conf
SECRET_VOLUME=/s3secret

#TODO gfarm branch
GFARM_S3_MINIO_BRANCH=gfarmmerge

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

    cd ${WORKDIR}/gfarm-s3-minio-web \
    && ./configure \
    --prefix=/usr/local \
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
    && make \
    && make install \
    && mkdir -p ${CACHE_DIR} \
    && chmod 1777 ${CACHE_DIR}

    # TODO RUN systemctl enable gfarm-s3-web.service
    systemctl enable gunicorn \
    && systemctl enable gfarm-s3-router.service
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

mksym() {
    SRC="$1"
    DST="$2"
    [ -h "${DST}" ] || ln -s "${SRC}" "${DST}"
}

SAVE_IFS="$IFS"
IFS=$'\n'
for line in $(cat "${USERMAP}"); do
    GFARM_USERNAME=$(echo "${line}" | awk -F : '{print $1}' | sed "s/\s//g")
    LOCAL_USERNAME=$(echo "${line}" | awk -F : '{print $2}' | sed "s/\s//g")
    ACCESSKEY_ID=$(echo "${line}" | awk -F : '{print $3}' | sed "s/\s//g")

    [ -z "${LOCAL_USERNAME}" ] && continue
    [ "${LOCAL_USERNAME:0:1}" = "#" ] && continue

    HOST_HOMEDIR="${HOST_HOME_BASE}/${LOCAL_USERNAME}"
    if [ ! -d "${HOST_HOMEDIR}" ]; then
       echo "WARNING: ${HOST_HOMEDIR} not found" >&2
       continue
    fi

    HOMEDIR="${HOME_BASE}/${LOCAL_USERNAME}"
    if [ ! -d "${HOMEDIR}" ]; then
        USER_UID=$(stat -c %u "${HOST_HOMEDIR}")
        USER_GID=$(stat -c %g "${HOST_HOMEDIR}")

        if group_exist "${USER_GID}"; then
            :
        else
            groupadd -g ${USER_GID} "gid${USER_GID}"
        fi
        useradd -m -s /bin/bash -g ${USER_GID} -b "${HOME_BASE}" -u "${USER_UID}" "${LOCAL_USERNAME}"
        echo "INFO: create ${HOMEDIR}" >&2
    fi
    sudo usermod -a -G "${GFARM_S3_GROUPNAME}" "${LOCAL_USERNAME}"

    ### .globus
    DOTGLOBUS="${HOMEDIR}/.globus"
    HOST_DOTGLOBUS="${HOST_HOMEDIR}/.globus"
    mksym "${HOST_DOTGLOBUS}" "${DOTGLOBUS}"

    ### .gfarm_shared_key
    GFARM_SHARED_KEY="${HOMEDIR}/.gfarm_shared_key"
    HOST_GFARM_SHARED_KEY="${HOST_HOMEDIR}/.gfarm_shared_key"
    mksym "${HOST_GFARM_SHARED_KEY}" "${GFARM_SHARED_KEY}"

    ### .gfarm2rc
    GFARM2RC="${HOMEDIR}/.gfarm2rc"
    HOST_GFARM2RC="${HOST_HOMEDIR}/.gfarm2rc"
    mksym "${HOST_GFARM2RC}" "${GFARM2RC}"

    ### .gfarm-s3/
    SECRET_DIR="${HOMEDIR}/.gfarm-s3"
    SECRET_DIR_VOLUME="${SECRET_VOLUME}/${LOCAL_USERNAME}"
    mkdir -p "${SECRET_DIR_VOLUME}"
    chmod 700 "${SECRET_DIR_VOLUME}"
    [ -d "${SECRET_DIR_VOLUME}" ] || echo "WARNING: ${SECRET_DIR_VOLUME} is not a directory"
    chown "${LOCAL_USERNAME}":root "${SECRET_DIR_VOLUME}"
    mksym "${SECRET_DIR_VOLUME}" "${SECRET_DIR}"

    ### create myproxy-logon script
    if [ -n "${MYPROXY_SERVER}" ]; then
        MYPROXY_LOGON="${HOMEDIR}/myproxy-logon"
        cat <<EOF > "${MYPROXY_LOGON}"
#/bin/sh
myproxy-logon -s "${MYPROXY_SERVER}" -l "${GFARM_USERNAME}" \$@
EOF
        chown "${LOCAL_USERNAME}" "${MYPROXY_LOGON}"
        chmod u+x "${MYPROXY_LOGON}"
    fi

    gfarm-s3-useradd "${GFARM_USERNAME}" "${LOCAL_USERNAME}" "${ACCESSKEY_ID}" || true  ## may fail

    ### resume minio
    sudo -u "${GFARM_S3_GROUPNAME}" gfarm-s3-login --quiet --authenticated "DUMMY_AUTH_METHOD" resume "${GFARM_USERNAME}" "DUMMY_PASSWORD" > /dev/null &
    ##### backgroud
done
### wait for resuming minio
wait
IFS="$SAVE_IFS"

exec "$@"
