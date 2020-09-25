## Process this file with automake to produce Makefile.in
#
# data/Makefile.am
#
# $Id$
#

SUBDIRS	= icons schemas ui

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

CLEANFILES		= $(appdata_DATA) $(desktop_DATA)
EXTRA_DIST		= $(appdata_in_files) $(desktop_in_files)

install-data-hook:
if HAVE_FDO_MIME
	$(UPDATE_MIME_DATABASE) "$(datadir)/mime"
endif

if HAVE_FDO_DESKTOP
	$(UPDATE_DESKTOP_DATABASE)
endif
