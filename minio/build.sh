#! /bin/sh

##gfarm2fs の configure
##--with-gfarm=/usr/local
##--prefix=/usr/local

with_gfarm=/usr/local
prefix=/usr/local

srcdir=/home/user1/work/gfarm-s3-minio-web
export GOPATH=$srcdir/minio/work/go
export GOBIN=$GOPATH/bin
BUILDDIR=$srcdir/minio/work/build

. /usr/local/etc/gfarm-s3.conf

mc_git=https://github.com/minio/mc.git
minio_git=git@github.com:oss-tsukuba/gfarm-s3-minio.git

[ -d $BUILDDIR ] || mkdir -p $BUILDDIR

[ -d $BUILDDIR/mc ] || (cd $BUILDDIR && git clone $mc_git)

[ -d $BUILDDIR/gfarm-s3-minio ] || (cd $BUILDDIR && git clone $minio_git &&
	cd gfarm-s3-minio && git checkout gatewaygfarm)

(cd $BUILDDIR/mc && $GOPATH/bin/go install)

if [ x"$with_gfarm" = x"/usr" ]; then with_gfarm=; fi

set -o xtrace
if [ -n "$with_gfarm" ]; then
	export CGO_LDFLAGS="-Wl,-rpath,$with_gfarm/lib"
	export PKG_CONFIG_PATH="$with_gfarm/lib/pkgconfig"
	(cd $BUILDDIR/gfarm-s3-minio && $GOPATH/bin/go install)
fi
