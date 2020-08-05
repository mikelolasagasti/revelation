## Process this file with automake to produce Makefile.in
#
# src/Makefile.am
#
# $Id$
#

SUBDIRS		= bundle lib
bin_SCRIPTS	= revelation
EXTRA_DIST	= revelation.py
CLEANFILES	= revelation


revelation: revelation.py
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		revelation.py > revelation
