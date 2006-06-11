## Process this file with automake to produce Makefile.in
#
# data/mime/Makefile.am
#
# $Id$
#

desktopdir		= $(datadir)/applications
dist_desktop_DATA	= revelation.desktop

mimedir			= $(datadir)/mime/packages
dist_mime_DATA		= revelation.xml


install-data-hook:
if HAVE_FDO_MIME
	$(UPDATE_MIME_DATABASE) "$(datadir)/mime"
endif

if HAVE_FDO_DESKTOP
	$(UPDATE_DESKTOP_DATABASE)
endif

