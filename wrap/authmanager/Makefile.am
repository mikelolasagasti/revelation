## Process this file with automake to produce Makefile.in
#
# wrap/authmanager/Makefile.am
#
# $Id$
#

module_PROGRAMS	= authmanager.so
moduledir	= $(pyexecdir)/revelation
CLEANFILES	= authmanager.c

AM_LDFLAGS	= `pkg-config --libs gtk+-2.0 pygtk-2.0 libgnomeui-2.0 gnome-vfs-2.0 gnome-keyring-1`
AM_CFLAGS	= `pkg-config --cflags gtk+-2.0 pygtk-2.0 libgnomeui-2.0 gnome-vfs-2.0 gnome-keyring-1` -fPIC -I${PYTHON_INCLUDE} -I.


authmanager.c: authmanager.defs authmanager.override
	pygtk-codegen-2.0 --prefix authmanager \
		--override authmanager.override \
		authmanager.defs > $@

authmanager.so: authmanager.o authmanagermodule.o
	$(CC) $(AM_LDFLAGS) -shared $^ -o $@

