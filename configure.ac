dnl
dnl configure.ac
dnl
dnl $Id$
dnl

dnl initialize autoconf/automake
AC_PREREQ(2.53)
AC_INIT(src/revelation.in)
AM_INIT_AUTOMAKE(revelation, 0.4.8)
ALL_LINGUAS="cs de fr sv zh"

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
RVL_PYTHON_MODULE(bonobo, yes)
RVL_PYTHON_MODULE(gconf, yes)
RVL_PYTHON_MODULE(gtk, yes)
RVL_PYTHON_MODULE(gnome, yes)
RVL_PYTHON_MODULE(gnomeapplet, yes)
RVL_PYTHON_MODULE(gnomevfs, yes)
RVL_PYTHON_MODULE(gobject, yes)
RVL_PYTHON_MODULE(pango, yes)


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

