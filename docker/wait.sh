#!/bin/bash

set -eu
#set -x

URL_PATH="/gf_s3/console/login/"
NAME="Gfarm-S3"
CONT_NAME="gfminio"
EXPECT_CODE='^20.*$'

SILENT="-s"
#SILENT=""

COMPOSE=$(make -s ECHO_COMPOSE)

eval $(egrep '^(PROTOCOL|HTTP_PORT|HTTPS_PORT|SERVER_NAME)=' config.env)

if [ "${PROTOCOL}" = "https" ]; then
    PORT=${HTTPS_PORT:-443}
else
    PORT=${HTTP_PORT:-80}
fi

URL="${PROTOCOL}://${SERVER_NAME}:${PORT}${URL_PATH}"
RESOLVE="--resolve ${SERVER_NAME}:${PORT}:127.0.0.1"

container_exists()
{
    ${COMPOSE} exec ${CONT_NAME} true
}

http_get_code()
{
    curl ${SILENT} -k --noproxy '*' -w '%{http_code}' \
         ${RESOLVE} ${URL} -o /dev/null
}

echo -n "Waiting for ${NAME} to start (it may take a few minutes)"
while :; do
    if ! container_exists; then
        make stop ${CONT_NAME}
        make logs | tail -20
        exit 1
    fi
    if CODE=$(http_get_code); then
        if [[ "$CODE" =~ ${EXPECT_CODE} ]]; then
            break
        fi
    fi
    echo -n .
    sleep 1
done
echo
echo "${NAME} is ready."
