dnl initialize autoconf/automake
AC_PREREQ(2.53)
AC_INIT(src/revelation.in)
AM_INIT_AUTOMAKE(revelation, 0.4.0)


dnl some macros
AC_DEFUN([AC_PYTHON_MODULE],[
	AC_MSG_CHECKING(python module: $1)
	python -c "import $1" 2>/dev/null

	if test $? -eq 0; then
		AC_MSG_RESULT(yes)
		eval AS_TR_CPP(HAVE_PYMOD_$1)=yes
	else
		AC_MSG_RESULT(no)
		eval AS_TR_CPP(HAVE_PYMOD_$1)=no

		if test -n "$2"; then
			AC_MSG_ERROR(failed to find required module $1)
			exit 1
		fi
	fi
])


dnl check for dependencies
AM_PATH_PYTHON(2.3)
PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= 2.3.90)
PKG_CHECK_MODULES(GNOME_PYTHON, gnome-python-2.0 >= 2.5.90)
AC_PYTHON_MODULE(Crypto, yes)

AC_PATH_PROG(GCONFTOOL, gconftool-2, no)
if test x"$GCONFTOOL" = xno; then
	AC_MSG_ERROR([gconftool-2 executable not found in your path - should be installed with GConf])
fi
AM_GCONF_SOURCE_2


dnl output files
AC_OUTPUT([
	Makefile
	data/Makefile
	data/icons/Makefile
	data/icons/16x16/Makefile
	data/icons/48x48/Makefile
	data/ui/Makefile
	src/Makefile
	src/lib/Makefile
	src/lib/datahandler/Makefile
])

