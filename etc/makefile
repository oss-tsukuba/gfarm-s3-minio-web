PREFIX=/usr/local

SYS_HTTPD_CONF=/etc/httpd/conf/httpd.conf
SYS_HTTPD_CONF_D=/etc/httpd/conf.d
HTTPD_USER=apache
#######$$(sed -n '/^User /s///p' /etc/httpd/conf/httpd.conf)

MOD_WSGI_EXPRESS=mod_wsgi-express

APACHE_DOCUMENTROOT=$(PREFIX)/share/www
GFARMS3_CONF=$(PREFIX)/etc/gfarm-s3.conf
GFARMS3_LOCAL_USER_MAP=$(PREFIX)/etc/gfarm_s3_local_user_map
GFARMS3_USER_PORT_MAP=$(GFARM_S3_VAR)/gfarm_s3_user_port_map
GFARMS3_APACHE_REWRITE_CONF=$(GFARM_S3_VAR)/rewrite.conf
GFARMS3_APACHE_REWRITE_MASTER_CONF=$(SYS_HTTPD_CONF_D)/gfarm-s3.conf
GFARMS3_APACHE_REWRITE_WSGI_CONF=$(SYS_HTTPD_CONF_D)/gfarm-s3-wsgi.conf
GFARM_S3_VAR=$(PREFIX)/var/gfarm-s3

INSTALL=install -c -m 555
MKDIR=mkdir

all: gfarm-s3.conf sudoers apache-gfarm-s3.conf apache-gfarm-s3-wsgi.conf

gfarm-s3.conf: gfarm-s3.conf.in
	../makes/build-conf < $^ > $@

sudoers: sudoers.in
	../makes/build-conf < $^ > $@

apache-gfarm-s3.conf: apache-gfarm-s3.conf.in
	../makes/build-conf < $^ > $@

apache-gfarm-s3-wsgi.conf: apache-gfarm-s3-wsgi.conf.in
	($(MOD_WSGI_EXPRESS) module-config; ../makes/build-conf < $^) > $@

clean:
	rm -f gfarm-s3.conf sudoers apache-gfarm-s3.conf apache-gfarm-s3-wsgi.conf

install:
	$(INSTALL) -c gfarm-s3.conf $(GFARMS3_CONF)

	touch $(GFARMS3_LOCAL_USER_MAP)
	chown $(HTTPD_USER) $(GFARMS3_LOCAL_USER_MAP)

	$(INSTALL) sudoers /etc/sudoers.d/gfarm-s3

	$(MKDIR) -p $$(dirname $(GFARMS3_USER_PORT_MAP))
	chown $(HTTPD_USER) $$(dirname $(GFARMS3_USER_PORT_MAP))
	touch $(GFARMS3_USER_PORT_MAP)
	chown $(HTTPD_USER) $(GFARMS3_USER_PORT_MAP)

	if ! grep -q '^gfarms3:' /etc/group; then sudo groupadd gfarms3; fi

	$(MKDIR) -p $$(dirname $(GFARMS3_APACHE_REWRITE_CONF))
	chown $(HTTPD_USER) $$(dirname $(GFARMS3_APACHE_REWRITE_CONF))
	touch $(GFARMS3_APACHE_REWRITE_CONF)
	chown $(HTTPD_USER) $(GFARMS3_APACHE_REWRITE_CONF)

	$(MKDIR) -p $(APACHE_DOCUMENTROOT)
	touch $(APACHE_DOCUMENTROOT)/index.html
	$(INSTALL) apache-gfarm-s3.conf $(GFARMS3_APACHE_REWRITE_MASTER_CONF)
	$(INSTALL) apache-gfarm-s3-wsgi.conf $(GFARMS3_APACHE_REWRITE_WSGI_CONF)
	systemctl enable httpd
	@echo please restart httpd
