#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)
AC_INIT([etc/gfarm-s3.conf.in], [1.0.0])
AC_CONFIG_SRCDIR([etc/gfarm-s3.conf.in])
AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIR([m4])
AC_SYS_LARGEFILE

# Checks for programs.
AC_PROG_CC
AC_PROG_LIBTOOL

### --with-gfarm=GFARM_ROOT
AC_MSG_CHECKING([for Gfarm file system])
AC_ARG_WITH([gfarm],
  AC_HELP_STRING([--with-gfarm=GFARM_ROOT], [Gfarm root directory [/usr]]))
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
  AC_HELP_STRING([--with-globus=GLOBUS_ROOT], [Globus root directory [/usr]]))
case x$with_globus in
  x|xyes|xno) with_globus=/usr ;;
esac
AC_MSG_RESULT([$with_globus])
AC_SUBST(with_globus)

### --with-myproxy=MYPROXY_ROOT
AC_MSG_CHECKING([for MyProxy Credential Management Service])
AC_ARG_WITH([myproxy],
  AC_HELP_STRING([--with-myproxy=MYPROXY_ROOT], [Myproxy root directory [/usr]]))
case x$with_myproxy in
  x|xyes|xno) with_myproxy=/usr ;;
esac
AC_MSG_RESULT([$with_myproxy])
AC_SUBST(with_myproxy)

### --with-gunicorn=GUNICORN_ROOT
AC_MSG_CHECKING([for Gunicorn - Python WSGI HTTP Server for UNIX])
AC_ARG_WITH([gunicorn],
  AC_HELP_STRING([--with-gunicorn=GUNICORN_ROOT], [gunicorn root directory [/usr]]))
case x$with_gunicorn in
  x|xyes|xno) with_gunicorn=/usr/local ;;
esac
AC_MSG_RESULT([$with_gunicorn])
AC_SUBST(with_gunicorn)

### MYPROXY_SERVER
AC_ARG_VAR(MYPROXY_SERVER, [myproxy server name [<not specified (disabled)>]])
case x$MYPROXY_SERVER in
  x) MYPROXY_SERVER= ;;
esac
AC_SUBST(MYPROXY_SERVER)

### GSI_PROXY_HOURS
AC_ARG_VAR(GSI_PROXY_HOURS, [GSI proxy certificate lifetime [168] hours])
case x$GSI_PROXY_HOURS in
  x) GSI_PROXY_HOURS=168 ;;
esac
AC_SUBST(GSI_PROXY_HOURS)

### GFARM_S3_HOMEDIR
AC_ARG_VAR(GFARM_S3_HOMEDIR, [Gfarm S3 homedir [/home/_gfarm_s3]])
case x$GFARM_S3_HOMEDIR in
  x) GFARM_S3_HOMEDIR=/home/_gfarm_s3 ;;
esac
AC_SUBST(GFARM_S3_HOMEDIR)

### GFARM_S3_USERNAME
AC_ARG_VAR(GFARM_S3_USERNAME, [Gfarm S3 user name [_gfarm_s3]])
case x$ in
  x) GFARM_S3_USERNAME= ;;
esac
AC_SUBST(GFARM_S3_USERNAME)

### GFARM_S3_GROUPNAME
AC_ARG_VAR(GFARM_S3_GROUPNAME, [Gfarm S3 group name [_gfarm_s3]])
case x$GFARM_S3_GROUPNAME in
  x) GFARM_S3_GROUPNAME= ;;
esac
AC_SUBST(GFARM_S3_GROUPNAME)

### GFARM_S3_WEBUI_ADDR
AC_ARG_VAR(GFARM_S3_WEBUI_ADDR, [Gfarm S3 WebUI address [unix:/tmp/gfarm-s3-webui.sock]])
case x$GFARM_S3_WEBUI_ADDR in
  x) GFARM_S3_WEBUI_ADDR=unix:/tmp/gfarm-s3-webui.sock ;;
esac
AC_SUBST(GFARM_S3_WEBUI_ADDR)

### GFARM_S3_ROUTER_ADDR
AC_ARG_VAR(GFARM_S3_ROUTER_ADDR, [Gfarm S3 router address [unix:/tmp/gfarm-s3-router.sock]])
case x$GFARM_S3_ROUTER_ADDR in
  x) GFARM_S3_ROUTER_ADDR=unix:/tmp/gfarm-s3-router.sock ;;
esac
AC_SUBST(GFARM_S3_ROUTER_ADDR)

### --with-router-nthreads=ROUTER_NTHREADS
AC_MSG_CHECKING([number of router threads])
AC_ARG_WITH([router-nthreads],
  AC_HELP_STRING([--with-router-nthreads=ROUTER_NTHREADS], [number of threads [10]]))
case x$router_nthreads in
  x|xyes|xno) router_nthreads=10 ;;
esac
AC_MSG_RESULT([$router_nthreads])
AC_SUBST(router_nthreads)

### --with-router-nworkers=ROUTER_NWORKERS
AC_MSG_CHECKING([number of router workers])
AC_ARG_WITH([router-nworkers],
  AC_HELP_STRING([--with-router-nworkers=ROUTER_NWORKERS], [number of workers [10]]))
case x$router_nworkers in
  x|xyes|xno) router_nworkers=1 ;;
esac
AC_MSG_RESULT([$router_nworkers])
AC_SUBST(router_nworkers)

### --with-go-archive=GO_ARCHIVE
AC_MSG_CHECKING([go-archive that fetched from https://dl.google.com/go for build s3 server (MinIO)])
AC_ARG_WITH([go-archive],
  AC_HELP_STRING([--with-go-archive=GO_ARCHIVE], [go archive [go1.16.linux-amd64.tar.gz]]))
case x$with_go_archive in
  x|xyes|xno) with_go_archive=go1.16.linux-amd64.tar.gz ;;
esac
AC_MSG_RESULT([$with_go_archive])
AC_SUBST(with_go_archive)

### --with-minio-builddir=MINIO_BUILDDIR
AC_MSG_CHECKING([minio-builddir for build s3 server (MinIO)])
AC_ARG_WITH([minio-builddir],
  AC_HELP_STRING([--with-minio-builddir=MINIO_BUILDDIR], [work directory [$HOME/tmp]]))
case x$with_minio_builddir in
  x|xyes|xno) with_minio_builddir=$HOME/tmp ;;
esac
AC_MSG_RESULT([$with_minio_builddir])
AC_SUBST(with_minio_builddir)

### --with-gfarm-shared-dir=SHARED_DIR
AC_MSG_CHECKING([gfarm_shared_dir])
AC_ARG_WITH([gfarm-shared-dir],
  AC_HELP_STRING([--with-gfarm-shared-dir=SHARED_DIR], [work directory [/share]]))
case x$with_gfarm_shared_dir in
  x|xyes|xno) with_gfarm_shared_dir=/share ;;
esac
AC_MSG_RESULT([$with_gfarm_shared_dir])
AC_SUBST(with_gfarm_shared_dir)

### MINIO_LOCALTEMP_DIR
AC_ARG_VAR(MINIO_LOCALTEMP_DIR, [Gfarm S3 MinIO local tempfile directory [/var/tmp]])
case x$MINIO_LOCALTEMP_DIR in
  x) MINIO_LOCALTEMP_DIR=/var/tmp ;;
esac
AC_SUBST(MINIO_LOCALTEMP_DIR)

### MINIO_LOCALTEMP_SIZE_MB
AC_ARG_VAR(MINIO_LOCALTEMP_SIZE_MB, [Gfarm S3 MinIO local tempfile size (MiB) [4096]])
case x$MINIO_LOCALTEMP_SIZE_MB in
  x) MINIO_LOCALTEMP_SIZE_MB=4096 ;;
esac
AC_SUBST(MINIO_LOCALTEMP_SIZE_MB)

### WEBUI_BASE_URL
AC_ARG_VAR(WEBUI_BASE_URL, [WebUI base URL [gfarm_s3/]])
case x$WEBUI_BASE_URL in
  x) WEBUI_BASE_URL=gfarm_s3/ ;;
esac
AC_SUBST(WEBUI_BASE_URL)

# Checks for libraries.
AC_CHECK_LIB([gfarm], [gfarm_initialize],, [AC_MSG_ERROR([libgfarm not found])])
AC_CHECK_LIB([gfarm], [gfarm_get_global_username_by_url],, [AC_MSG_ERROR([Gfarm-2.4.2 or later is required])])

AC_CONFIG_FILES([makefile
bin/gfarm-s3-configtest
bin/gfarm-s3-diff-local-usermap
bin/gfarm-s3-generate-usermap-hpci
bin/gfarm-s3-login
bin/gfarm-s3-server
bin/gfarm-s3-minio
bin/gfarm-s3-readconf
bin/gfarm-s3-sharedsecret-password
bin/gfarm-s3-update-reverse-proxy
bin/gfarm-s3-useradd
bin/gfarm-s3-viusermap
bin/makefile
etc/gfarm-s3.conf
etc/gfarm-s3-webui.service
etc/gfarm-s3-router.service
etc/makefile
etc/nginx-gfarm-s3-generated.conf
etc/sudoers
minio/makefile
web/makefile
web/gfarm-s3/gfarms3/conf.py
])
AC_OUTPUT
