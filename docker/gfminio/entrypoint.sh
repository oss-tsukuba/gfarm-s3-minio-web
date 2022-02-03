#!/bin/bash

# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-

set -eu
set -o pipefail

if [ ${DEBUG} -eq 1 ]; then
    set -x
fi

### from build args
: ${WORKDIR}

### from enviroment
: ${DJANGO_DEBUG}
: ${SERVER_URL}
: ${ALLOWED_HOSTS}
: ${CSRF_TRUSTED_ORIGINS}
: ${GSI_PROXY_HOURS}
: ${MYPROXY_SERVER}
: ${GFARM_S3_WEBUI_THREADS}
: ${GFARM_S3_WEBUI_WORKERS}
: ${GFARM_S3_ROUTER_THREADS}
: ${GFARM_S3_ROUTER_WORKERS}
: ${GFARM_S3_SHARED_DIR}
: ${GFARM_S3_LOCALTMP_SIZE_MB}
: ${GO_URL}
: ${GFARM_S3_MINIO_SRC_GIT_URL}
: ${GFARM_S3_MINIO_SRC_GIT_BRANCH}

TZ=${TZ:-Asia/Tokyo}
export TZ

GFARM_S3_USERNAME="_gfarm_s3"
GFARM_S3_GROUPNAME="_gfarm_s3"
GFARM_S3_HOMEDIR="/home/${GFARM_S3_USERNAME}"
GFARM_S3_LOCALTMP_DIR="/localtmp"
GO_BUILDDIR="/build"
GFARM_S3_WEBUI_BASE_URL="gf_s3/"

GFARM_S3_MINIO_SRC_DIR_ORIG=/gfarm-s3-minio

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

COPY_HOME_INITIALIZED_FILE="${HOME_BASE}/_copy_home_initialized"

GFARM_S3_WEBUI_ADDR="unix:/tmp/gfarm-s3-webui.sock"
GFARM_S3_ROUTER_ADDR="unix:/tmp/gfarm-s3-router.sock"

GFARM_CONF_DIR_ORIG="/gfarm_conf"
PREFIX="/usr/local"
SYSCONFDIR="${PREFIX}/etc"

GFARM2_CONF_ORIG="${GFARM_CONF_DIR_ORIG}/gfarm2.conf"
GFARM2_CONF="${PREFIX}/etc/gfarm2.conf"

### <Gfarm Username>:<Local Username>:<S3 Accesskey ID>
GFARM_S3_USERMAP_ORIG="${GFARM_CONF_DIR_ORIG}/gfarm-s3-usermap.conf"
GFARM_S3_USERMAP="/gfarm-s3-usermap.conf"

cp -fa "${GFARM2_CONF_ORIG}" "${GFARM2_CONF}"
cp -fa "${GFARM_S3_USERMAP_ORIG}" "${GFARM_S3_USERMAP}"

debug_sleep() {
    # TODO if [ $DEBUG -eq 1 ]; then
    sleep infinity
}

### cache files in GO_BUILDDIR to build.
install_gf_s3() {
    groupadd -K GID_MIN=100 ${GFARM_S3_GROUPNAME}
    useradd -K UID_MIN=100 -m ${GFARM_S3_USERNAME} -g ${GFARM_S3_GROUPNAME} -d ${GFARM_S3_HOMEDIR} -s /bin/bash

    GFARM_S3_MINIO_DIRNAME=gfarm-s3-minio
    GFARM_S3_MINIO_WORKDIR=${GO_BUILDDIR}/${GFARM_S3_MINIO_DIRNAME}
    mkdir -p ${GO_BUILDDIR}
    if [ ! -d "${GFARM_S3_MINIO_WORKDIR}" ]; then
        if [ -d "${GFARM_S3_MINIO_SRC_DIR_ORIG}" ]; then
            mkdir -p "${GFARM_S3_MINIO_WORKDIR}"
        else
            git clone "${GFARM_S3_MINIO_SRC_GIT_URL}" "${GFARM_S3_MINIO_WORKDIR}"
        fi
    fi

    if [ -d "${GFARM_S3_MINIO_SRC_DIR_ORIG}" ]; then
        # from local directory (for developpers)
        rsync --delete -rlptD "${GFARM_S3_MINIO_SRC_DIR_ORIG}"/ "${GFARM_S3_MINIO_WORKDIR}"/
    else
        cd "${GFARM_S3_MINIO_WORKDIR}"
        git pull
        git checkout ${GFARM_S3_MINIO_SRC_GIT_BRANCH}
    fi

    cd ${WORKDIR}/gfarm-s3-minio-web
    GSI_PROXY_HOURS=${GSI_PROXY_HOURS} \
    MYPROXY_SERVER=${MYPROXY_SERVER} \
    GFARM_S3_HOMEDIR=${GFARM_S3_HOMEDIR} \
    GFARM_S3_USERNAME=${GFARM_S3_USERNAME} \
    GFARM_S3_GROUPNAME=${GFARM_S3_GROUPNAME} \
    GFARM_S3_WEBUI_ADDR=${GFARM_S3_WEBUI_ADDR} \
    GFARM_S3_ROUTER_ADDR=${GFARM_S3_ROUTER_ADDR} \
    GFARM_S3_WEBUI_THREADS=${GFARM_S3_WEBUI_THREADS} \
    GFARM_S3_WEBUI_WORKERS=${GFARM_S3_WEBUI_WORKERS} \
    GFARM_S3_ROUTER_THREADS=${GFARM_S3_ROUTER_THREADS} \
    GFARM_S3_ROUTER_WORKERS=${GFARM_S3_ROUTER_WORKERS} \
    GFARM_S3_SHARED_DIR=${GFARM_S3_SHARED_DIR} \
    GFARM_S3_LOCALTMP_DIR=${GFARM_S3_LOCALTMP_DIR} \
    GFARM_S3_LOCALTMP_SIZE_MB=${GFARM_S3_LOCALTMP_SIZE_MB} \
    GFARM_S3_WEBUI_BASE_URL=${GFARM_S3_WEBUI_BASE_URL} \
    GO_URL=${GO_URL} \
    GO_BUILDDIR=${GO_BUILDDIR} \
    ./configure \
    --prefix=${PREFIX} \
    --sysconfdir=${SYSCONFDIR} \
    --with-gfarm=/usr/local \
    --with-globus=/usr \
    --with-myproxy=/usr \
    --with-gunicorn=/usr/local
    make || debug_sleep
    make install

    mkdir -p ${GFARM_S3_LOCALTMP_DIR}
    chmod 1777 ${GFARM_S3_LOCALTMP_DIR}

    # generate DJANGO_SECRET_KEY
    DJANGO_SECRET_KEY=${SYSCONFDIR}/django_secret_key.txt
    if [ ! -f ${DJANGO_SECRET_KEY} ]; then
        #pip install django-generate-secret-key
        #cd ${GFARM_S3_HOMEDIR}/gfarm-s3
        #python3 manage.py generate_secret_key "${DJANGO_SECRET_KEY}"
        python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > "${DJANGO_SECRET_KEY}"
        chmod 400 "${DJANGO_SECRET_KEY}"
        chown ${GFARM_S3_USERNAME}:root "${DJANGO_SECRET_KEY}"
    fi

    # edit addtional configurations
    CONF_OVERWRITE=${SYSCONFDIR}/gfarm-s3-overwrite.conf
    cat <<EOF > "${CONF_OVERWRITE}"
#GFARM_S3_LOG_LEVEL=debug
GFARM_S3_LOG_OUTPUT=stderr

DJANGO_DEBUG=${DJANGO_DEBUG}
ALLOWED_HOSTS=${ALLOWED_HOSTS}

# required by Django 4 or later
CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
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
    #grep -q ":x:${gid}:" /etc/group
    getent group ${gid} > /dev/null
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
for line in $(cat "${GFARM_S3_USERMAP}"); do
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

        # restrict gfarm_s3-access only to users in one specific group
        # (SEE ALSO: gfarm-s3-minio-web/etc/sudoers.in)
        #usermod -a -G "${GFARM_S3_GROUPNAME}" "${LOCAL_USERNAME}"
    fi

    HOMEBIN="${HOMEDIR}/bin"
    mkdir -p ${HOMEBIN}

    ### create myproxy-logon script for the user
    if [ -n "${MYPROXY_SERVER}" ]; then
        MYPROXY_LOGON="${HOMEBIN}/myproxy-logon-${GFARM_USERNAME}.sh"
        cat <<EOF > "${MYPROXY_LOGON}"
#/bin/sh
myproxy-logon -s "${MYPROXY_SERVER}" -l "${GFARM_USERNAME}" \$@
EOF
        chown "${LOCAL_USERNAME}" "${MYPROXY_LOGON}"
        chmod u+x "${MYPROXY_LOGON}"
    fi

    AWS_S3="${HOMEBIN}/aws-s3.sh"
    cat <<EOF > "${AWS_S3}"
#!/bin/bash

set -eu

GFARM_USERNAME=${GFARM_USERNAME}

SERVER_NAME=proxy
SERVER_PORT=${SERVER_PORT}
SERVER_URL=https://\${SERVER_NAME}:\${SERVER_PORT}

PROF="gfarm_s3"
SECRET=\$(gfarm-s3-server --show-secret-key)

NO_VERIFY_SSL="--no-verify-ssl"
#NO_VERIFY_SSL=""

AWS="aws --profile \${PROF}"

\${AWS} configure set aws_access_key_id \${GFARM_USERNAME} &
p1=\$!
\${AWS} configure set aws_secret_access_key \${SECRET} &
p2=\$!
#\${AWS} configure set s3.multipart_threshold 300MB &
#p3=\$!
#\${AWS} configure set s3.multipart_chunksize 300MB &
#p4=\$!
#\${AWS} configure set s3.max_concurrent_requests 2 &
#p5=\$!

wait \$p1
wait \$p2
#wait \$p3
#wait \$p4
#wait \$p5

no_proxy=\${SERVER_NAME} \
AWS_EC2_METADATA_DISABLED=true \
\${AWS} \${NO_VERIFY_SSL} \
--endpoint-url \${SERVER_URL} s3 \$@
EOF
    chown "${LOCAL_USERNAME}" "${AWS_S3}"
    chmod u+x "${AWS_S3}"

    # copy skel
    SKEL=/etc/skel/
    for f in $(find ${SKEL} -type f); do
        dst=${HOMEDIR}/$(basename $f)
        if [ ! -e "$dst" ]; then
            cp -f "$f" "$dst"
            chown "${LOCAL_USERNAME}" "$dst"
        fi
    done

    gfarm-s3-useradd "${GFARM_USERNAME}" "${LOCAL_USERNAME}" "${ACCESSKEY_ID}" || true  ## fail when the user already exists

    ### resume minio (start minio if it was previously started)
    sudo -u "${GFARM_S3_USERNAME}" gfarm-s3-login --quiet --authenticated "DUMMY_AUTH_METHOD" resume "${GFARM_USERNAME}" "DUMMY_PASSWORD" > /dev/null &
    ##### backgroud (may fail, ignore)
done
### wait for resuming minio
wait
IFS="$SAVE_IFS"

exec "$@"
