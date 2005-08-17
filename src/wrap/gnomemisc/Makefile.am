## Process this file with automake to produce Makefile.in
#
# src/wrap/gnomemisc/Makefile.am
#
# $Id$
#

module_PROGRAMS	= gnomemisc.so
moduledir	= $(pyexecdir)/revelation
CLEANFILES	= gnomemisc.c

AM_LDFLAGS	= `pkg-config --libs gtk+-2.0 pygtk-2.0 libgnomeui-2.0 gnome-vfs-2.0 gnome-keyring-1 libpanelapplet-2.0`
AM_CFLAGS	= `pkg-config --cflags gtk+-2.0 pygtk-2.0 libgnomeui-2.0 gnome-vfs-2.0 gnome-keyring-1 libpanelapplet-2.0` -fPIC -I${PYTHON_INCLUDE} -I.


gnomemisc.c: gnomemisc.defs gnomemisc.override
	$(PYGTK_CODEGEN) --prefix gnomemisc \
		$(DEFS) \
		--register $(PYGTK_DEFSDIR)/applet.defs \
		--register $(PYGTK_DEFSDIR)/bonobo-types.defs \
		--override gnomemisc.override \
		gnomemisc.defs > $@

gnomemisc.so: gnomemisc.o gnomemiscmodule.o
	$(CC) $(AM_LDFLAGS) -shared $^ -o $@

