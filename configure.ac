dnl
dnl configure.ac
dnl
dnl $Id$
dnl

dnl initialize autoconf/automake
AC_PREREQ(2.53)
AC_INIT([revelation],[0.4.12],[http://oss.codepoet.no/revelation/issues/new],[revelation],[http://oss.codepoet.no/revelation/])
AM_INIT_AUTOMAKE([1.11 tar-ustar dist-xz no-dist-gzip -Wno-portability])

dnl check for dependencies
AC_PROG_CC()

RVL_PYTHON_PATH(2.3)
RVL_PYGTK()
RVL_GETTEXT()
RVL_CRACKLIB()
RVL_MMAN()
RVL_GCONF()
RVL_FDO_MIME()

RVL_PYTHON_MODULE(Crypto, yes)
RVL_PYTHON_MODULE(gconf, yes)
RVL_PYTHON_MODULE(gtk, yes)
RVL_PYTHON_MODULE(gnome, yes)
RVL_PYTHON_MODULE(gio, yes)
RVL_PYTHON_MODULE(gobject, yes)
RVL_PYTHON_MODULE(pango, yes)


dnl Enable applet installation
AC_ARG_WITH(applet,
	AS_HELP_STRING([--with-applet],[Build with applet (default=no)]),
	,with_applet=no)
if test "x$with_applet" = "xyes" ; then
	RVL_PYTHON_MODULE(bonobo, yes)
	RVL_PYTHON_MODULE(gnomeapplet, yes)
fi
AM_CONDITIONAL([WITH_APPLET], [test "x$with_applet" = "xyes"])

dnl output files
AC_OUTPUT([
	Makefile
	data/Makefile
	data/bonobo/Makefile
	data/cracklib/Makefile
	data/gconf/Makefile
	data/icons/Makefile
	data/icons/16x16/Makefile
	data/icons/24x24/Makefile
	data/icons/32x32/Makefile
	data/icons/48x48/Makefile
	data/icons/scalable/Makefile
	data/mime/revelation.desktop.in
	data/mime/Makefile
	data/ui/Makefile
	po/Makefile.in
	src/Makefile
	src/bundle/Makefile
	src/lib/Makefile
	src/lib/datahandler/Makefile
	src/wrap/Makefile
	src/wrap/crack/Makefile
])

echo "

------------------------------------------------------------------
-- revelation compilation options

revelation version:        ${PACKAGE_VERSION}
With applet:               $with_applet
------------------------------------------------------------------
"

