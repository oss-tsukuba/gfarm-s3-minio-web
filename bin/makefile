PREFIX=/usr/local

BINDIR=$(PREFIX)/bin
INSTALL=install -c -m 555

scripts= \
	gfarm-s3-configtest \
	gfarm-s3-diff-local-usermap \
	gfarm-s3-generate-usermap-hpci \
	gfarm-s3-getfacl \
	gfarm-s3-login \
	gfarm-s3-server \
	gfarm-s3-sharedsecret-password \
	gfarm-s3-subr \
	gfarm-s3-update-reverse-proxy \
	gfarm-s3-useradd \
	gfarm-s3-viusermap

all:

install:
	for i in $(scripts); do $(INSTALL) $$i $(BINDIR); done
