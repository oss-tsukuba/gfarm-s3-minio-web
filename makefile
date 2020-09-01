install:
	(cd etc && make)
	(cd bin && make)
	sudo apachectl restart
	(cd minio && make)
