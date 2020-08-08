## Process this file with automake to produce Makefile.in
#
# data/Makefile.am
#
# $Id$
#

SUBDIRS	= icons mime schemas ui

appdatadir = $(datadir)/appdata
appdata_in_files = $(PACKAGE_TARNAME).appdata.xml.in
appdata_DATA = $(appdata_in_files:.xml.in=.xml)

$(appdata_DATA): $(appdata_in_files)
	$(AM_V_GEN)$(MSGFMT) --xml --template $< -d $(top_srcdir)/po -o $@

CLEANFILES		= $(appdata_DATA)
EXTRA_DIST		= $(appdata_in_files)

