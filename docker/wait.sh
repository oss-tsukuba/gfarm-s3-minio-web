#!/bin/bash

set -eu
#set -x

eval $(cat config.env | egrep  '^(HTTP_PORT|HTTPS_PORT|SERVER_NAME)=')

if [ ${HTTPS_PORT:+HTTPS_PORT_IS_SET} = HTTPS_PORT_IS_SET ]; then
    PORT=$HTTPS_PORT
    PROTOCOL=https
else
    PORT=$HTTP_PORT
    PROTOCOL=http
fi

URL="${PROTOCOL}://${SERVER_NAME}:${PORT}/gf_s3/console/login/"

RESOLVE="--resolve ${SERVER_NAME}:${PORT}:127.0.0.1"

COMPOSE=$(make -s ECHO_COMPOSE)
CONT_NAME=gfminio

SILENT="-s"
#SILENT=""

container_exists()
{
    ${COMPOSE} exec ${CONT_NAME} true
}

echo -n "Waiting for Gfarm-S3 startup..."
while :; do
    if ! container_exists; then
        make stop ${CONT_NAME}
        make logs | tail -20
        exit 1
    fi
    if CODE=$(curl ${SILENT} -k -w '%{http_code}' ${RESOLVE} ${URL} -o /dev/null); then
        if [ "$CODE" = 200 ]; then
            break
        fi
    fi
    echo -n .
    sleep 1
done
echo

echo "Gfarm-S3 is ready."
