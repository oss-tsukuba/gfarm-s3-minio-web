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

SILENT="-s"
#SILENT=""

while :; do
    if CODE=$(curl ${SILENT} -k -w '%{http_code}' ${RESOLVE} ${URL} -o /dev/null); then
        if [ "$CODE" = 200 ]; then
            break
        fi
    fi
    echo "Waiting for Gfarm-S3 startup..."
    sleep 1
done

echo "Gfarm-S3 is ready."
