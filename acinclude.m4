AC_DEFUN([RVL_FDO_MIME], [
	AC_PATH_PROG(UPDATE_DESKTOP_DATABASE, update-desktop-database, no)
	AC_PATH_PROG(UPDATE_MIME_DATABASE, update-mime-database, no)

	AC_ARG_ENABLE(desktop-update, [AS_HELP_STRING(--disable-desktop-update, Disable the MIME desktop database update)], disable_desktop=yes, disable_desktop=no)
	AC_ARG_ENABLE(mime-update, [AS_HELP_STRING(--disable-mime-update, Disable the MIME database update)], disable_mime=yes, disable_mime=no)

	AM_CONDITIONAL(HAVE_FDO_DESKTOP, test "x$UPDATE_DESKTOP_DATABASE" != "xno" -a "x$disable_desktop" = "xno")
	AM_CONDITIONAL(HAVE_FDO_MIME, test "x$UPDATE_MIME_DATABASE" != "xno" -a "x$disable_mime" = "xno")
])

AC_DEFUN([RVL_GETTEXT], [
	GETTEXT_PACKAGE="revelation"

	AC_SUBST(GETTEXT_PACKAGE)
	AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])
])

AC_DEFUN([RVL_MMAN], [
	AC_CHECK_FUNCS(mlockall munlockall)
])

AC_DEFUN([RVL_PYGTK], [
	PKG_CHECK_MODULES([GTK], [gtk+-3.0 >= 3.22])
	PKG_CHECK_MODULES([PYGOBJECT], [pygobject-3.0])
])

AU_ALIAS([AC_PYTHON_MODULE], [AX_PYTHON_MODULE])
AC_DEFUN([AX_PYTHON_MODULE],[
    if test -z $PYTHON;
    then
        if test -z "$3";
        then
            PYTHON="python3"
        else
            PYTHON="$3"
        fi
    fi
    PYTHON_NAME=`basename $PYTHON`
    AC_MSG_CHECKING($PYTHON_NAME module: $1)
    $PYTHON -c "import $1" 2>/dev/null
    if test $? -eq 0;
    then
        AC_MSG_RESULT(yes)
        eval AS_TR_CPP(HAVE_PYMOD_$1)=yes
    else
        AC_MSG_RESULT(no)
        eval AS_TR_CPP(HAVE_PYMOD_$1)=no
        #
        if test -n "$2"
        then
            AC_MSG_ERROR(failed to find required module $1)
            exit 1
        fi
    fi
])


AC_DEFUN([AX_PYTHON_GI], [
    AC_MSG_CHECKING([for bindings for GObject Introspection])
    AX_PYTHON_MODULE([gi], [$2], [$3])
    AC_MSG_CHECKING([for version $2 of $1 GObject Introspection module])
    $PYTHON -c "import gi; gi.require_version('$1', '$2')" 2> /dev/null
    AS_IF([test $? -eq 0], [], [
        AC_MSG_RESULT([no])
        AC_MSG_ERROR([You need version $2 of the $1 GObject Introspection module.])
    ])
    AC_MSG_RESULT([yes])
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
	AC_ARG_WITH(python-include, [AS_HELP_STRING(--with-python-include=PATH, Path to Python include dir)], PYTHON_INCLUDE=$withval)

	if test -z "$PYTHON_INCLUDE" ; then
		PYTHON_INCLUDE=$PYTHON
		rvl_py_include_path=`echo $PYTHON_INCLUDE | sed -e "s/bin/include/"`
		rvl_py_version="`$PYTHON -c "import sys; print (sys.version[[0:3]])"`";
		PYTHON_INCLUDE="$rvl_py_include_path$rvl_py_version"
	fi

	AC_MSG_RESULT($PYTHON_INCLUDE)
	AC_SUBST(PYTHON_INCLUDE)
])

