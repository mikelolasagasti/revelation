AC_DEFUN([RVL_CRACKLIB], [
	AC_CHECK_LIB(crack, FascistCheck, [], AC_MSG_ERROR(cracklib2 not found))

	RVL_CRACKLIB_DICTPATH

	AC_PATH_PROGS(CRACK_FORMAT, mkdict crack_mkdict cracklib-format, no, $PATH:/sbin:/usr/sbin)
	if test x"$CRACK_FORMAT" = xno; then
		AC_MSG_ERROR([mkdict or cracklib-format from cracklib not found in your path])
	fi
	AC_PATH_PROGS(CRACK_PACKER, packer crack_packer cracklib-packer, no, $PATH:/sbin:/usr/sbin)
	if test x"$CRACK_PACKER" = xno; then
		AC_MSG_ERROR([packer or cracklib-packer from cracklib not found in your path])
	fi
])

AC_DEFUN([RVL_CRACKLIB_DICTPATH], [
	AC_MSG_CHECKING([cracklib dictionary database])
	AC_ARG_WITH(cracklib-dict, [  --with-cracklib-dict=PATH  path to cracklib dictionary database], CRACK_DICTPATH=$withval)

	if test -z "$CRACK_DICTPATH"; then
		cat > dictpath-test.c << EOF
#include <crack.h>

int main()
{
	printf(CRACKLIB_DICTPATH);
	return 0;
}
EOF

		${CC-cc} -o dictpath-test $CFLAGS dictpath-test.c >/dev/null 2>&1

		if test -e dictpath-test; then
			CRACK_DICTPATH=`./dictpath-test`
			AC_MSG_RESULT($CRACK_DICTPATH)
		else
			CRACK_DICTPATH="$datadir/revelation/pwdict"
			AC_MSG_RESULT(using builtin)
		fi

		rm -f dictpath-test* core core.dictpath-test
	else
		AC_MSG_RESULT($CRACK_DICTPATH)
	fi

	AC_SUBST(CRACK_DICTPATH)
])

AC_DEFUN([RVL_FDO_MIME], [
	AC_PATH_PROG(UPDATE_DESKTOP_DATABASE, update-desktop-database, no)
	AC_PATH_PROG(UPDATE_MIME_DATABASE, update-mime-database, no)

	AC_ARG_ENABLE(desktop-update, [AC_HELP_STRING(--disable-desktop-update, Disable the MIME desktop database update)], disable_desktop=yes, disable_desktop=no)
	AC_ARG_ENABLE(mime-update, [AC_HELP_STRING(--disable-mime-update, Disable the MIME database update)], disable_mime=yes, disable_mime=no)

	AM_CONDITIONAL(HAVE_FDO_DESKTOP, test "x$UPDATE_DESKTOP_DATABASE" != "xno" -a "x$disable_desktop" = "xno")
	AM_CONDITIONAL(HAVE_FDO_MIME, test "x$UPDATE_MIME_DATABASE" != "xno" -a "x$disable_mime" = "xno")
])

AC_DEFUN([RVL_GCONF], [
	AC_PATH_PROG(GCONFTOOL, gconftool-2, no)

	if test "x$GCONFTOOL" = "xno"; then
		AC_MSG_ERROR(gconftool-2 not found in your path)
	fi

	AM_GCONF_SOURCE_2
])

AC_DEFUN([RVL_PYGTK], [
	PKG_CHECK_MODULES(PYGTK, [pygtk-2.0 >= 2.8.0])
	PKG_CHECK_MODULES(GNOME_PYTHON, [gnome-python-2.0 >= 2.10.0])
	PKG_CHECK_MODULES(GNOME_PYTHON_EXTRAS, [gnome-python-extras-2.0 >= 2.10.0])

	AC_PATH_PROG(PYGTK_CODEGEN, pygtk-codegen-2.0, no)

	if test "x$PYGTK_CODEGEN" = "xno"; then
		AC_MSG_ERROR(pygtk-codegen-2.0 not found in your path)
	fi

	AC_MSG_CHECKING(path to pygtk defs)
	PYGTK_DEFSDIR=`$PKG_CONFIG --variable=defsdir pygtk-2.0`
	AC_SUBST(PYGTK_DEFSDIR)
	AC_MSG_RESULT($PYGTK_DEFSDIR)
])

AC_DEFUN([RVL_PYTHON_MODULE], [
	AC_MSG_CHECKING(python module $1)

	$PYTHON -c "import imp; imp.find_module('$1')" 2>/dev/null

	if test $? -eq 0; then
		AC_MSG_RESULT(yes)
		eval AS_TR_CPP(HAVE_PYMOD_$1)=yes
	else
		AC_MSG_RESULT(no)
		AC_MSG_ERROR(failed to find module $1)
		exit 1
	fi
])

AC_DEFUN([RVL_PYTHON_PATH], [
	AM_PATH_PYTHON($1)

	AC_MSG_CHECKING(Python include path)
	AC_ARG_WITH(python-include, [AC_HELP_STRING(--with-python-include=PATH, Path to Pyton include dir)], PYTHON_INCLUDE=$withval)

	if test -z "$PYTHON_INCLUDE" ; then
		PYTHON_INCLUDE=$PYTHON
		rvl_py_include_path=`echo $PYTHON_INCLUDE | sed -e "s/bin/include/"`
		rvl_py_version="`$PYTHON -c "import sys; print sys.version[[0:3]]"`";
		PYTHON_INCLUDE="$rvl_py_include_path$rvl_py_version"
	fi

	AC_MSG_RESULT($PYTHON_INCLUDE)
	AC_SUBST(PYTHON_INCLUDE)
])

