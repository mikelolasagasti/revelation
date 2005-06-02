## Process this file with automake to produce Makefile.in
#
# src/lib/Makefile.am
#
# $Id$
#

SUBDIRS			= datahandler
CLEANFILES		= config.py

librevelationdir	= $(pyexecdir)/revelation
librevelation_PYTHON	= \
	__init__.py \
	config.py \
	data.py \
	dialog.py \
	entry.py \
	io.py \
	ui.py \
	util.py


config.py: config.py.in
	sed \
		-e "s|\@GCONFTOOL\@|$(GCONFTOOL)|" \
		-e "s|\@VERSION\@|$(VERSION)|" \
		-e "s|\@datadir\@|$(datadir)|" \
		-e "s|\@pkgdatadir\@|$(pkgdatadir)|" \
		-e "s|\@pkgschemadir\@|@GCONF_SCHEMA_FILE_DIR@|" \
		config.py.in > config.py

