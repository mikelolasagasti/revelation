## Process this file with automake to produce Makefile.in
#
# data/mime/Makefile.am
#
# $Id$
#

desktopdir 	 = $(datadir)/applications
desktop_in_files = revelation.desktop.in
desktop_DATA 	 = $(desktop_in_files:.desktop.in=.desktop)

revelation.desktop: $(desktop_in_files)
	$(AM_V_GEN)$(MSGFMT) --desktop --template $< -d $(top_srcdir)/po -o $@

mimedir			= $(datadir)/mime/packages
dist_mime_DATA		= revelation.xml

CLEANFILES		= $(desktop_DATA)
EXTRA_DIST		= $(desktop_in_files)


install-data-hook:
if HAVE_FDO_MIME
	$(UPDATE_MIME_DATABASE) "$(datadir)/mime"
endif

if HAVE_FDO_DESKTOP
	$(UPDATE_DESKTOP_DATABASE)
endif

