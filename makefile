srcdir=/home/user1/work/gfarm-s3-minio-web
GOPATH=$(srcdir)/minio/tmp/go
go_archive=go1.15.linux-amd64.tar.gz
go_url=https://dl.google.com/go/$(go_archive)
MKDIR=mkdir

all:
	(cd etc && make)
	(cd minio && make)

install-go:
	$(MKDIR) -p $$(dirname $(GOPATH))
	(cd $$(dirname $(GOPATH)) && curl $(go_url) | tar xfzp -)

install:
	(cd etc && make install)
	(cd bin && make install)
	(cd minio && make install)
