## Process this file with automake to produce Makefile.in
#
# data/Makefile.am
#
# $Id$
#

SUBDIRS	= icons

appdatadir = $(datadir)/metainfo
appdata_in_files = info.olasagasti.revelation.appdata.xml.in
appdata_DATA = $(appdata_in_files:.xml.in=.xml)

$(appdata_DATA): $(appdata_in_files)
	$(AM_V_GEN)$(MSGFMT) --xml --template $< -d $(top_srcdir)/po -o $@

desktopdir 	 = $(datadir)/applications
desktop_in_files = info.olasagasti.revelation.desktop.in
desktop_DATA 	 = $(desktop_in_files:.desktop.in=.desktop)

info.olasagasti.revelation.desktop: $(desktop_in_files)
	$(AM_V_GEN)$(MSGFMT) --desktop --template $< -d $(top_srcdir)/po -o $@

mimedir			= $(datadir)/mime/packages
dist_mime_DATA		= revelation.xml

gsettings_SCHEMAS = info.olasagasti.revelation.gschema.xml

gschemas.compiled: $(gsettings_SCHEMAS) Makefile
	$(AM_V_GEN) $(GLIB_COMPILE_SCHEMAS) $(builddir)

@GSETTINGS_RULES@

gresourcedir   = $(pkgdatadir)
gresource_DATA	= revelation.gresource

revelation.gresource: revelation.gresource.xml Makefile $(shell $(GLIB_COMPILE_RESOURCES) --generate-dependencies $(srcdir)/revelation.gresource.xml)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target $@ --sourcedir=$(srcdir) --generate $<

CLEANFILES		= \
	$(appdata_DATA) \
	$(desktop_DATA) \
	gschemas.compiled \
	$(gresource_DATA)

EXTRA_DIST		= \
	$(appdata_in_files) \
	$(desktop_in_files) \
	$(gsettings_SCHEMAS) \
	revelation.gresource.xml \
	ui/help-overlay.ui \
	ui/menubar.ui \
	ui/popup-tree.ui

install-data-hook:
if HAVE_FDO_MIME
	$(UPDATE_MIME_DATABASE) "$(datadir)/mime"
endif

if HAVE_FDO_DESKTOP
	$(UPDATE_DESKTOP_DATABASE)
endif

all-local: gschemas.compiled
