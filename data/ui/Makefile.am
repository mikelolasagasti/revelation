## Process this file with automake to produce Makefile.in
#
# data/ui/Makefile.am
#
# $Id$
#

uidir		= $(pkgdatadir)/ui
dist_ui_DATA	= menubar.ui popup-tree.ui revelation.gresource

revelation.gresource: revelation.gresource.xml Makefile $(shell $(GLIB_COMPILE_RESOURCES) --generate-dependencies $(srcdir)/revelation.gresource.xml)
	$(GLIB_COMPILE_RESOURCES) --target $@ --sourcedir=$(srcdir) --generate $< 

EXTRA_DIST  = revelation.gresource.xml help-overlay.ui
CLEANFILES  = revelation.gresource
