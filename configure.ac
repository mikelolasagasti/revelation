dnl
dnl configure.ac
dnl
dnl $Id$
dnl

dnl initialize autoconf/automake
AC_PREREQ(2.53)
AC_INIT(src/revelation.in)
AM_INIT_AUTOMAKE(revelation, 0.4.4)


dnl check for dependencies
AC_PROG_CC()

RVL_PYTHON_PATH(2.3)
RVL_PYTHON_MODULE(Crypto, yes)

RVL_PYGTK()
RVL_CRACKLIB()
RVL_GCONF()
RVL_FDO_MIME()


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
	data/mime/Makefile
	data/ui/Makefile
	src/Makefile
	src/lib/Makefile
	src/lib/datahandler/Makefile
	src/wrap/Makefile
	src/wrap/crack/Makefile
	src/wrap/gnomemisc/Makefile
])

