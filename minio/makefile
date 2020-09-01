BUILDDIR=/home/user1/build
GOPATH=$(BUILDDIR)/go
GOBIN=$(GOPATH)/bin
GFARM_S3_PREFIX=/usr/local
MINIO_PATH=$(GFARM_S3_PREFIX)/bin/minio
MC_PATH=$(GFARM_S3_PREFIX)/bin/mc

all::
	./build

install::
	install -c -m 555 $(GOBIN)/mc "$(MC_PATH)"
	install -c -m 555 $(GOBIN)/minio "$(MINIO_PATH)"
