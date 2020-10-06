PREFIX=/usr/local
WSGI_USER=wsgi
MKDIR=mkdir
WSGI_HOMEDIR=/home/wsgi

all::
	mkdir -p gfarm-s3/console/static/console
	(cd gfarm-s3/console/static/console && npm -y init)
	(cd gfarm-s3/console/static/console && \
	 npm install jquery@3.4.1 && \
	 npm install popper.js@1.16.1 && \
	 npm install bootstrap@4.5.2 && \
	 npm install select2@4.0.13)

#	npm install popper.js && \

clean:
	rm -r gfarm-s3/console/static/console/node_modules
	rm -r gfarm-s3/console/static/console/package.json

install:
	tar cf - gfarm-s3 rungunicorn runserver | (cd $(WSGI_HOMEDIR) && tar xfp -)
	(cd gfarm-s3/console && tar cf - static) | (cd $(WSGI_HOMEDIR) && tar xfp -)
	chown -R $(WSGI_USER) $(WSGI_HOMEDIR)/gfarm-s3
	chmod +x $(WSGI_HOMEDIR)/rungunicorn $(WSGI_HOMEDIR)/runserver
	chmod og+rX $(WSGI_HOMEDIR)
	chmod -R og+rX $(WSGI_HOMEDIR)/static
