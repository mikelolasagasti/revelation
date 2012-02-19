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
libexec_SCRIPTS	= revelation-applet
EXTRA_DIST	+= revelation-applet.py
CLEANFILES	+= revelation-applet
endif

revelation: revelation.py
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		revelation.py > revelation

revelation-applet: revelation-applet.in
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		-e "s|\@bindir\@|$(bindir)|" \
		revelation-applet.py > revelation-applet

