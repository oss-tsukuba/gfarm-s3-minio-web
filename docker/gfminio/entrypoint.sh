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
: DJANGO_DEBUG=${DJANGO_DEBUG}
: SERVER_NAME=${SERVER_NAME}
: HTTP_PORT=${HTTP_PORT}
: HTTPS_PORT=${HTTPS_PORT}
: ALLOWED_HOSTS=${ALLOWED_HOSTS}
: CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}
: GSI_PROXY_HOURS=${GSI_PROXY_HOURS}
: MYPROXY_SERVER=${MYPROXY_SERVER}
: GFARM_S3_WEBUI_THREADS=${GFARM_S3_WEBUI_THREADS}
: GFARM_S3_WEBUI_WORKERS=${GFARM_S3_WEBUI_WORKERS}
: GFARM_S3_ROUTER_THREADS=${GFARM_S3_ROUTER_THREADS}
: GFARM_S3_ROUTER_WORKERS=${GFARM_S3_ROUTER_WORKERS}
: GFARM_S3_SHARED_DIR=${GFARM_S3_SHARED_DIR}
: GFARM_S3_LOCALTMP_SIZE_MB=${GFARM_S3_LOCALTMP_SIZE_MB}
: GO_URL=${GO_URL}
: GFARM_S3_MINIO_SRC_GIT_URL=${GFARM_S3_MINIO_SRC_GIT_URL}
: GFARM_S3_MINIO_SRC_GIT_BRANCH=${GFARM_S3_MINIO_SRC_GIT_BRANCH}
: TZ=${TZ}

export TZ

GFARM_S3_USERNAME="_gfarm_s3"
GFARM_S3_GROUPNAME="_gfarm_s3"
GFARM_S3_HOMEDIR="/home/${GFARM_S3_USERNAME}"
GFARM_S3_LOCALTMP_DIR="/localtmp"
GO_BUILDDIR="/build"
GFARM_S3_WEBUI_BASE_URL="gf_s3/"

GFARM_S3_MINIO_SRC_DIR_ORIG=/gfarm-s3-minio

# URL_REGEXP="^([^/:]+?)://([^/:]+?):?([[:digit:]]+)?(/.*)?"
# [[ ${SERVER_URL} =~ ${URL_REGEXP} ]]
# URL_SCHEME=${BASH_REMATCH[1]}
# SERVER_NAME=${BASH_REMATCH[2]}
# SERVER_PORT=${BASH_REMATCH[3]}
# URL_PATH=${BASH_REMATCH[4]}
# update SERVER_URL
# SERVER_URL="${URL_SCHEME}://${SERVER_NAME}"
# if [ -n "${SERVER_PORT}" ]; then
#     SERVER_URL="${SERVER_URL}:${SERVER_PORT}"
# fi

TMP_CSRF_TRUSTED_ORIGINS=""

add_tmp_trusted() {
    VAL="$1"
    if [ -n "${TMP_CSRF_TRUSTED_ORIGINS}" ]; then
        TMP_CSRF_TRUSTED_ORIGINS="${TMP_CSRF_TRUSTED_ORIGINS},${VAL}"
    else
        TMP_CSRF_TRUSTED_ORIGINS="${VAL}"
    fi
}

HTTPS_URL=""
if [ -n "${HTTPS_PORT}" ]; then
    if [ "${HTTPS_PORT}" = 443 ]; then
        HTTPS_URL="https://${SERVER_NAME}"
    else
        HTTPS_URL="https://${SERVER_NAME}:${HTTPS_PORT}"
    fi
    add_tmp_trusted "${HTTPS_URL}"
fi

HTTP_URL=""
if [ -z "${HTTPS_PORT}" -a -n "${HTTP_PORT}" ]; then
#if [ -n "${HTTP_PORT}" ]; then
    if [ "${HTTP_PORT}" = 80 ]; then
        HTTP_URL="http://${SERVER_NAME}"
    else
        HTTP_URL="http://${SERVER_NAME}:${HTTP_PORT}"
    fi
    add_tmp_trusted "${HTTP_URL}"
fi

if [ -n "${HTTPS_URL}" ]; then  # prioritize HTTPS
    SERVER_URL="${HTTPS_URL}"
    SERVER_PORT="${HTTPS_PORT}"
    SERVER_SCHEME=https
else
    SERVER_URL="${HTTP_URL}"
    SERVER_PORT="${HTTP_PORT}"
    SERVER_SCHEME=http
fi

[ -n "${SERVER_URL}" ]

# (overridable) update when empty
ALLOWED_HOSTS=${ALLOWED_HOSTS:-${SERVER_NAME}}
# (overridable) update when empty
CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS:-${TMP_CSRF_TRUSTED_ORIGINS}}

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
    if [ ${DEBUG} -eq 1 ]; then
        sleep infinity
    else
        return 1
    fi
}

### cache files in GO_BUILDDIR to build.
install_gf_s3() {
    groupadd -K GID_MIN=100 ${GFARM_S3_GROUPNAME} || true
    if id -u ${GFARM_S3_USERNAME} > /dev/null 2>&1; then
        :
    else
        useradd -K UID_MIN=100 -m ${GFARM_S3_USERNAME} -g ${GFARM_S3_GROUPNAME} -d ${GFARM_S3_HOMEDIR} -s /bin/bash
    fi

    GFARM_S3_MINIO_DIRNAME=gfarm-s3-minio
    GFARM_S3_MINIO_WORKDIR=${GO_BUILDDIR}/${GFARM_S3_MINIO_DIRNAME}
    mkdir -p ${GO_BUILDDIR}

    if [ -d "${GFARM_S3_MINIO_SRC_DIR_ORIG}" ]; then
        # from local directory (for developpers)
        rsync --delete -rlptD "${GFARM_S3_MINIO_SRC_DIR_ORIG}"/ "${GFARM_S3_MINIO_WORKDIR}"/
    else
        rm -rf "${GFARM_S3_MINIO_WORKDIR}"
        git clone --depth 1 -b "${GFARM_S3_MINIO_SRC_GIT_BRANCH}" "${GFARM_S3_MINIO_SRC_GIT_URL}" "${GFARM_S3_MINIO_WORKDIR}"
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
    NGINX_ACCESS_LOG=/dev/stdout \
    NGINX_ERROR_LOG=/dev/stderr \
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
    #DJANGO_SECRET_KEY_FILE=${SYSCONFDIR}/django_secret_key.txt
    DJANGO_SECRET_KEY_FILE=${GFARM_S3_LOCALTMP_DIR}/django_secret_key.txt
    if [ ! -s ${DJANGO_SECRET_KEY_FILE} ]; then
        #pip install django-generate-secret-key
        #cd ${GFARM_S3_HOMEDIR}/gfarm-s3
        #python3 manage.py generate_secret_key "${DJANGO_SECRET_KEY_FILE}"
        python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" > "${DJANGO_SECRET_KEY_FILE}"
        chmod 400 "${DJANGO_SECRET_KEY_FILE}"
        chown ${GFARM_S3_USERNAME}:root "${DJANGO_SECRET_KEY_FILE}"
    fi

    # edit addtional configurations
    CONF_OVERRIDE=${SYSCONFDIR}/gfarm-s3-override.conf
    cat <<EOF > "${CONF_OVERRIDE}"
DJANGO_TIME_ZONE=${TZ}
ALLOWED_HOSTS=${ALLOWED_HOSTS}

# required by Django 4 or later
CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS}

GFARM_S3_LOGIN_CHALLENGE_LOG=${GFARM_S3_LOCALTMP_DIR}/error_addr.log
DJANGO_SECRET_KEY_FILE=${DJANGO_SECRET_KEY_FILE}

GFARM_S3_LOG_OUTPUT=stderr
EOF

    if [ ${DEBUG} -eq 1 ]; then
        cat <<EOF >> "${CONF_OVERRIDE}"
GFARM_S3_LOG_LEVEL=debug
DJANGO_DEBUG=True
EOF
    else
        cat <<EOF >> "${CONF_OVERRIDE}"
#GFARM_S3_LOG_LEVEL=info
DJANGO_DEBUG=${DJANGO_DEBUG}
EOF
    fi

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

run_gfarm_s3_login() {
    ACTION="$1"
    GFARM_USERNAME="$2"

    sudo -u ${GFARM_S3_USERNAME} gfarm-s3-login --quiet --authenticated "DUMMY_AUTH_METHOD" $ACTION "${GFARM_USERNAME}" "DUMMY_PASSWORD" > /dev/null
}

ENABLED_USERS=()

SAVE_IFS="$IFS"
IFS=$'\n'
for line in $(cat "${GFARM_S3_USERMAP}"); do
    GFARM_USERNAME=$(echo "${line}" | awk -F : '{print $1}' | sed "s/\s//g")
    LOCAL_USERNAME=$(echo "${line}" | awk -F : '{print $2}' | sed "s/\s//g")
    ACCESSKEY_ID=$(echo "${line}" | awk -F : '{print $3}' | sed "s/\s//g")

    [ -z "${GFARM_USERNAME}" ] && continue
    [ "${GFARM_USERNAME:0:1}" = "#" ] && continue

    # add
    ENABLED_USERS+=("${GFARM_USERNAME}")

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

### revproxy container is required
SERVER_NAME=revproxy
SERVER_PORT=${SERVER_PORT}
SERVER_SCHEME=${SERVER_SCHEME}
SERVER_URL=\${SERVER_SCHEME}://\${SERVER_NAME}:\${SERVER_PORT}

PROF="gfarm_s3"
NO_VERIFY_SSL="--no-verify-ssl"
#NO_VERIFY_SSL=""
AWS="python3 /run_aws.py --profile \${PROF}"

export no_proxy=\${SERVER_NAME}
export AWS_EC2_METADATA_DISABLED=true

is_configured() {
  egrep -q ^\\\\[\${PROF}\\\\] \${HOME}/.aws/credentials
}

if ! is_configured; then
  ACCESS_KEY=\$(gfarm-s3-server --show-access-key)
  SECRET_KEY=\$(gfarm-s3-server --show-secret-key)

  \${AWS} configure set aws_access_key_id \${ACCESS_KEY}
  \${AWS} configure set aws_secret_access_key \${SECRET_KEY}
  #\${AWS} configure set s3.multipart_threshold 300MB
  #\${AWS} configure set s3.multipart_chunksize 300MB
  #\${AWS} configure set s3.max_concurrent_requests 2
fi

\${AWS} \${NO_VERIFY_SSL} --endpoint-url \${SERVER_URL} s3 \$@
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

    gfarm-s3-useradd "${GFARM_USERNAME}" "${LOCAL_USERNAME}" "${ACCESSKEY_ID}" > /dev/null || true  ## fail when the user already exists

    ### resume minio (start minio if it was previously started)
    run_gfarm_s3_login resume "${GFARM_USERNAME}" &
    ##### backgroud (may fail, ignore)
done
### wait for resuming minio
wait
IFS="$SAVE_IFS"

stop_all() {
    for gfarm_username in ${ENABLED_USERS[@]}; do
        run_gfarm_s3_login stop_to_resume "${gfarm_username}" &
    done
    wait
}

# ignore signal
trap "" 1 2 15

cd /
"$@"
stop_all
