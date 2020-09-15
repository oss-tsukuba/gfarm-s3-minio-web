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

# Checks for libraries.
AC_CHECK_LIB([gfarm], [gfarm_initialize],, [AC_MSG_ERROR([libgfarm not found])])
AC_CHECK_LIB([gfarm], [gfarm_get_global_username_by_url],, [AC_MSG_ERROR([Gfarm-2.4.2 or later is required])])

AC_CONFIG_FILES([
etc/gfarm-s3.conf
etc/makefile
makes/build-conf
bin/gfarm-s3-configtest
bin/gfarm-s3-diff-local-usermap
bin/gfarm-s3-login
bin/gfarm-s3-server
bin/gfarm-s3-sharedsecret-password
bin/gfarm-s3-update-reverse-proxy
bin/gfarm-s3-useradd
bin/gfarm-s3-viusermap
bin/makefile
minio/makefile
])
AC_OUTPUT
