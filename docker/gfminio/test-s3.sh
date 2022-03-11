#!/bin/bash

set -eu
set -x

AWS_S3=~/bin/aws-s3.sh

BUCKET_NAME="s3://test-bkt1"

TESTFILE_S3_1=${BUCKET_NAME}/testfile1
TESTFILE_S3_2=${BUCKET_NAME}/testfile2

TESTFILE_LOCAL_TMP=$(mktemp tmpfile.XXXXXXXXXX)
TESTFILE_LOCAL_SMALL=$(mktemp tmpfile-small.XXXXXXXXXX)
TESTFILE_LOCAL_LARGE=$(mktemp tmpfile-large.XXXXXXXXXX)

date +%s > ${TESTFILE_LOCAL_SMALL}
dd if=/dev/urandom of=${TESTFILE_LOCAL_LARGE} bs=1M count=50

RESULT=FAIL

cleanup() {
    rm -f ${TESTFILE_LOCAL_TMP} ${TESTFILE_LOCAL_SMALL} ${TESTFILE_LOCAL_LARGE}
    ${AWS_S3} rm ${TESTFILE_S3_1} || true
    ${AWS_S3} rm ${TESTFILE_S3_2} || true
    ${AWS_S3} rb ${BUCKET_NAME} || true
    echo $RESULT
}
trap cleanup EXIT

${AWS_S3} ls s3://
${AWS_S3} mb ${BUCKET_NAME}

# copy small file (single part upload)
${AWS_S3} cp ${TESTFILE_LOCAL_SMALL} ${TESTFILE_S3_1}
${AWS_S3} cp ${TESTFILE_S3_1} ${TESTFILE_LOCAL_TMP}
cmp ${TESTFILE_LOCAL_SMALL} ${TESTFILE_LOCAL_TMP}

# copy large file (multipart upload) and overwrite
${AWS_S3} cp ${TESTFILE_LOCAL_LARGE} ${TESTFILE_S3_1}
${AWS_S3} cp ${TESTFILE_S3_1} ${TESTFILE_LOCAL_TMP}
cmp ${TESTFILE_LOCAL_LARGE} ${TESTFILE_LOCAL_TMP}

# copy on s3
# "--copy-props none" for:
#   (NotImplemented) when calling the GetObjectTagging operation
${AWS_S3} cp --copy-props none ${TESTFILE_S3_1} ${TESTFILE_S3_2}

${AWS_S3} ls ${BUCKET_NAME}
${AWS_S3} ls ${TESTFILE_S3_1}
${AWS_S3} ls ${TESTFILE_S3_2}

${AWS_S3} rm ${TESTFILE_S3_1}
${AWS_S3} rm ${TESTFILE_S3_2}
${AWS_S3} rb ${BUCKET_NAME}

RESULT=PASS
