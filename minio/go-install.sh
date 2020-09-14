#! /bin/sh

srcdir=/home/user1/work/gfarm-s3-minio-web
GOPATH=$srcdir/minio/work/go

go_archive=go1.15.linux-amd64.tar.gz
go_url=https://dl.google.com/go/$go_archive
if [ ! -e $GOPATH ]; then
	mkdir -p $(dirname $GOPATH)
	(cd $(dirname $GOPATH) && curl $go_url | tar xfzp -)
fi
