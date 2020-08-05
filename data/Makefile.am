## Process this file with automake to produce Makefile.in
#
# data/Makefile.am
#
# $Id$
#

SUBDIRS	= icons mime ui

appdatadir = $(datadir)/appdata
appdata_in_files = $(PACKAGE_TARNAME).appdata.xml.in
appdata_DATA = $(appdata_in_files:.xml.in=.xml)

@INTLTOOL_XML_RULE@

CLEANFILES		= $(appdata_DATA)
EXTRA_DIST		= $(appdata_in_files)

