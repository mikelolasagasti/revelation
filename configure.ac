dnl
dnl configure.ac
dnl
dnl $Id$
dnl

dnl initialize autoconf/automake
AC_PREREQ(2.53)
AC_INIT([revelation],[0.4.14],[https://bitbucket.org/erikg/revelation/issues/new],[revelation],[https://revelation.olasagasti.info/])
AM_INIT_AUTOMAKE([1.11 tar-ustar dist-xz no-dist-gzip -Wno-portability])

RVL_PYTHON_PATH(2.3)
RVL_PYGTK()
RVL_GETTEXT()
RVL_MMAN()
RVL_GCONF()
RVL_FDO_MIME()

RVL_PYTHON_MODULE(Crypto, yes)
RVL_PYTHON_MODULE(gtk, yes)
RVL_PYTHON_MODULE(gnome, yes)
RVL_PYTHON_MODULE(gio, yes)
RVL_PYTHON_MODULE(gobject, yes)
RVL_PYTHON_MODULE(pango, yes)
RVL_PYTHON_MODULE(dbus, yes)
RVL_PYTHON_MODULE(cracklib, yes)


dnl Enable applet installation
AC_ARG_WITH(applet,
	AS_HELP_STRING([--with-applet],[Build with applet (default=no)]),
	,with_applet=no)
if test "x$with_applet" = "xyes" ; then
	RVL_PYTHON_MODULE(bonobo, yes)
	RVL_PYTHON_MODULE(gnomeapplet, yes)
	PKG_CHECK_MODULES(GNOME_PYTHON_EXTRAS, [gnome-python-extras-2.0 >= 2.10.0])
fi
AM_CONDITIONAL([WITH_APPLET], [test "x$with_applet" = "xyes"])

dnl output files
AC_OUTPUT([
	Makefile
	data/Makefile
	data/bonobo/Makefile
	data/icons/Makefile
	data/icons/16x16/Makefile
	data/icons/24x24/Makefile
	data/icons/32x32/Makefile
	data/icons/48x48/Makefile
	data/icons/256x256/Makefile
	data/icons/scalable/Makefile
	data/mime/revelation.desktop.in
	data/mime/Makefile
	data/ui/Makefile
	po/Makefile.in
	src/Makefile
	src/applet/Makefile
	src/bundle/Makefile
	src/lib/Makefile
	src/lib/datahandler/Makefile
])

echo "

------------------------------------------------------------------
-- revelation compilation options

revelation version:        ${PACKAGE_VERSION}
With applet:               $with_applet
------------------------------------------------------------------
"

