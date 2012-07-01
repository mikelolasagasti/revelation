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


if WITH_APPLET
SUBDIRS		+= applet
endif

revelation: revelation.py
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		revelation.py > revelation
