# initialize autoconf/automake
AC_PREREQ(2.53)
AC_INIT(src/revelation.in)
AM_INIT_AUTOMAKE(revelation, 0.4.0)


dnl check for dependencies
AM_PATH_PYTHON(2.3)
PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= 2.3.90)
PKG_CHECK_MODULES(GNOME_PYTHON, gnome-python-2.0 >= 2.5.90)

AC_PATH_PROG(GCONFTOOL, gconftool-2, no)
if test x"$GCONFTOOL" = xno; then
	AC_MSG_ERROR([gconftool-2 executable not found in your path - should be installed with GConf])
fi
AM_GCONF_SOURCE_2


dnl output files
AC_OUTPUT([
	Makefile
	data/Makefile
	data/images/Makefile
	src/Makefile
	src/lib/Makefile
	src/lib/datahandler/Makefile
])

