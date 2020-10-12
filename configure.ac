#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)
AC_INIT([etc/gfarm-s3.conf.in], [0.0.0])
#AM_MAINTAINER_MODE
AC_CONFIG_SRCDIR([etc/gfarm-s3.conf.in])
#AC_CONFIG_HEADER([config.h])
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AC_CONFIG_MACRO_DIR([m4])
AC_SYS_LARGEFILE

# Checks for programs.
AC_PROG_CC
AC_PROG_LIBTOOL

### --with-gfarm=GFARM_ROOT
AC_MSG_CHECKING([for Gfarm file system])
AC_ARG_WITH([gfarm],
  AC_HELP_STRING([--with-gfarm=GFARM_ROOT], [Gfarm root directory [[/usr]]]))
case x$with_gfarm in
  x|xyes|xno) with_gfarm=/usr ;;
esac
if test x"$with_gfarm" != x/usr; then
  CPPFLAGS="$CPPFLAGS -I$with_gfarm/include"
  LDFLAGS="$LDFLAGS -L$with_gfarm/lib"
fi
AC_MSG_RESULT([$with_gfarm])
AC_SUBST(with_gfarm)

### --with-globus=GLOBUS_ROOT
AC_MSG_CHECKING([for Globus Toolkit])
AC_ARG_WITH([globus],
  AC_HELP_STRING([--with-globus=GLOBUS_ROOT], [Globus root directory [[/usr]]]))
case x$with_globus in
  x|xyes|xno) with_globus=/usr ;;
esac
AC_MSG_RESULT([$with_globus])
AC_SUBST(with_globus)

### --with-myproxy=MYPROXY_ROOT
AC_MSG_CHECKING([for MyProxy Credential Management Service])
AC_ARG_WITH([myproxy],
  AC_HELP_STRING([--with-myproxy=MYPROXY_ROOT], [Myproxy root directory [[/usr]]]))
case x$with_myproxy in
  x|xyes|xno) with_myproxy=/usr ;;
esac
AC_MSG_RESULT([$with_myproxy])
AC_SUBST(with_myproxy)

### --with-myproxy-server=MYPROXY_SERVER
AC_MSG_CHECKING([for myproxy server])
AC_ARG_WITH([myproxy-server],
  AC_HELP_STRING([--with-myproxy-server=MYPROXY_SERVER], [myproxy servername [[portal.hpci.nii.ac.jp]]]))
case x$with_myproxy_server in
  x|xyes|xno) with_myproxy_server=portal.hpci.nii.ac.jp ;;
esac
AC_MSG_RESULT([$with_myproxy_server])
AC_SUBST(with_myproxy_server)

### --with-proxy-lifetime=PROXY_LIFETIME
AC_MSG_CHECKING([for proxy lifetime])
AC_ARG_WITH([proxy-lifetime],
  AC_HELP_STRING([--with-proxy-lifetime=PROXY_LIFETIME], [proxy lifetime [[168]]]))
case x$with_proxy_lifetime in
  x|xyes|xno) with_proxy_lifetime=168 ;;
esac
AC_MSG_RESULT([$with_proxy_lifetime])
AC_SUBST(with_proxy_lifetime)

### --with-apache=APACHE_ROOT
AC_MSG_CHECKING([for Apache HTTP Server])
AC_ARG_WITH([apache],
  AC_HELP_STRING([--with-apache=APACHE_ROOT], [Apache root directory [[/usr]]]))
case x$with_apache in
  x|xyes|xno) with_apache=/usr ;;
esac
AC_MSG_RESULT([$with_apache])
AC_SUBST(with_apache)

### --with-gunicorn=GUNICORN_ROOT
AC_MSG_CHECKING([for Gunicorn - Python WSGI HTTP Server for UNIX])
AC_ARG_WITH([gunicorn],
  AC_HELP_STRING([--with-gunicorn=GUNICORN_ROOT], [gunicorn root directory [[/usr]]]))
case x$with_gunicorn in
  x|xyes|xno) with_gunicorn=/usr/local ;;
esac
AC_MSG_RESULT([$with_gunicorn])
AC_SUBST(with_gunicorn)

### --with-wsgi-homedir=WSGI_HOMEDIR
AC_MSG_CHECKING([for WSGI homedir])
AC_ARG_WITH([wsgi-homedir],
  AC_HELP_STRING([--with-wsgi-homedir=WSGI_HOMEDIR], [wsgi homedir [[/home/wsgi]]]))
case x$with_wsgi_homedir in
  x|xyes|xno) with_wsgi_homedir=/home/wsgi ;;
esac
AC_MSG_RESULT([$with_wsgi_homedir])
AC_SUBST(with_wsgi_homedir)

### --with-wsgi-user=WSGI_USER
AC_MSG_CHECKING([for WSGI user])
AC_ARG_WITH([wsgi-user],
  AC_HELP_STRING([--with-wsgi-user=WSGI_USER], [wsgi username [[wsgi]]]))
case x$with_wsgi_user in
  x|xyes|xno) with_wsgi_user=wsgi ;;
esac
AC_MSG_RESULT([$with_wsgi_user])
AC_SUBST(with_wsgi_user)

### --with-wsgi-group=WSGI_GROUP
AC_MSG_CHECKING([for WSGI group])
AC_ARG_WITH([wsgi-group],
  AC_HELP_STRING([--with-wsgi-group=WSGI_GROUP], [wsgi groupname [[wsgi]]]))
case x$with_wsgi_group in
  x|xyes|xno) with_wsgi_group=wsgi ;;
esac
AC_MSG_RESULT([$with_wsgi_group])
AC_SUBST(with_wsgi_group)

### --with-wsgi-port=WSGI_PORT
AC_MSG_CHECKING([for WSGI port])
AC_ARG_WITH([wsgi-port],
  AC_HELP_STRING([--with-wsgi-port=WSGI_PORT], [wsgi port [[8000]]]))
case x$with_wsgi_port in
  x|xyes|xno) with_wsgi_port=8000 ;;
esac
AC_MSG_RESULT([$with_wsgi_port])
AC_SUBST(with_wsgi_port)

### --with-minio-builddir=MINIO_BUILDDIR
AC_MSG_CHECKING([minio-builddir for build s3 server (MinIO)])
AC_ARG_WITH([minio-builddir],
  AC_HELP_STRING([--with-minio-builddir=MINIO_BUILDDIR], [work directory [[$HOME/tmp]]]))
case x$with_minio_builddir in
  x|xyes|xno) with_minio_builddir=$HOME/tmp ;;
esac
AC_MSG_RESULT([$with_minio_builddir])
AC_SUBST(with_minio_builddir)

### --with-gfarm-shared-dir=SHARED_DIR
AC_MSG_CHECKING([gfarm_shared_dir])
AC_ARG_WITH([gfarm-shared-dir],
  AC_HELP_STRING([--with-gfarm-shared-dir=SHARED_DIR], [work directory [[/share]]]))
case x$with_gfarm_shared_dir in
  x|xyes|xno) with_gfarm_shared_dir=/share ;;
esac
AC_MSG_RESULT([$with_gfarm_shared_dir])
AC_SUBST(with_gfarm_shared_dir)

### --with-cache-basedir=CACHE_BASEDIR
AC_MSG_CHECKING([minio cache basedir])
AC_ARG_WITH([cache-basedir],
  AC_HELP_STRING([--with-cache-basedir=CACHE_BASEDIR], [cache directory [[/var/tmp]]]))
case x$with_cache_basedir in
  x|xyes|xno) with_cache_basedir=/var/tmp ;;
esac
AC_MSG_RESULT([$with_cache_basedir])
AC_SUBST(with_cache_basedir)

### --with-cache-size=CACHE_SIZE (MB)
AC_MSG_CHECKING([minio cache size])
AC_ARG_WITH([cache-size],
  AC_HELP_STRING([--with-cache-size=CACHE_SIZE], [cache size [[4096]]]))
case x$with_cache_size in
  x|xyes|xno) with_cache_size=4096 ;;
esac
AC_MSG_RESULT([$with_cache_size])
AC_SUBST(with_cache_size)

# Checks for libraries.
AC_CHECK_LIB([gfarm], [gfarm_initialize],, [AC_MSG_ERROR([libgfarm not found])])
AC_CHECK_LIB([gfarm], [gfarm_get_global_username_by_url],, [AC_MSG_ERROR([Gfarm-2.4.2 or later is required])])

AC_CONFIG_FILES([makefile
bin/gfarm-s3-configtest
bin/gfarm-s3-diff-local-usermap
bin/gfarm-s3-login
bin/gfarm-s3-server
bin/gfarm-s3-sharedsecret-password
bin/gfarm-s3-update-reverse-proxy
bin/gfarm-s3-useradd
bin/gfarm-s3-viusermap
bin/makefile
etc/apache-gfarm-s3.conf
etc/gfarm-s3.conf
etc/gunicorn.service
etc/makefile
etc/sudoers
minio/makefile
webui/makefile
webui/rungunicorn
webui/runserver
])
AC_OUTPUT
