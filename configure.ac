dnl
dnl configure.ac
dnl
dnl $Id$
dnl

dnl initialize autoconf/automake
AC_PREREQ([2.69])
AC_INIT([revelation],[0.5.3],[https://github.com/mikelolasagasti/revelation/issues],[revelation],[https://revelation.olasagasti.info/])
AM_INIT_AUTOMAKE([1.11 tar-ustar dist-xz no-dist-gzip -Wno-portability])

AM_GNU_GETTEXT_VERSION([0.19.8])
AM_GNU_GETTEXT_REQUIRE_VERSION([0.19.8])
AM_GNU_GETTEXT([external])

RVL_PYTHON_PATH(3.0)
RVL_PYGTK()
RVL_GETTEXT()
RVL_MMAN()
RVL_FDO_MIME()

GLIB_GSETTINGS

RVL_PYTHON_MODULE(Cryptodome, yes)
AX_PYTHON_GI(Gtk, 3.0)
AX_PYTHON_GI(Gio, 2.0)
AX_PYTHON_GI(Pango, 1.0)
AX_PYTHON_GI(Gdk, 3.0)
RVL_PYTHON_MODULE(pwquality, yes)

AC_ARG_VAR([GLIB_COMPILE_RESOURCES],[the glib-compile-resources programme])
AC_PATH_PROG([GLIB_COMPILE_RESOURCES],[glib-compile-resources],[])
if test -z "$GLIB_COMPILE_RESOURCES"; then
  AC_MSG_ERROR([glib-compile-resources not found])
fi

dnl output files
AC_CONFIG_FILES([
	Makefile
	data/Makefile
	data/icons/Makefile
	data/icons/16x16/Makefile
	data/icons/24x24/Makefile
	data/icons/32x32/Makefile
	data/icons/48x48/Makefile
	data/icons/128x128/Makefile
	data/icons/256x256/Makefile
	data/icons/scalable/Makefile
	data/info.olasagasti.revelation.desktop.in
	po/Makefile.in
	po/Makefile
	src/Makefile
	src/bundle/Makefile
	src/lib/Makefile
	src/lib/datahandler/Makefile
])
AC_OUTPUT

echo "

------------------------------------------------------------------
-- revelation compilation options

revelation version:        ${PACKAGE_VERSION}
------------------------------------------------------------------
"

