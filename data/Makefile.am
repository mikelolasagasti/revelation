## Process this file with automake to produce Makefile.in
#
# data/Makefile.am
#
# $Id$
#

SUBDIRS	= gconf icons mime ui

if WITH_APPLET
SUBDIRS +=bonobo
endif

appdatadir = $(datadir)/appdata
appdata_in_files = $(PACKAGE_TARNAME).appdata.xml.in
appdata_DATA = $(appdata_in_files:.xml.in=.xml)

@INTLTOOL_XML_RULE@

CLEANFILES		= $(appdata_DATA)
EXTRA_DIST		= $(appdata_in_files)

