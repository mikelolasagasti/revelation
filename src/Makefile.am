## Process this file with automake to produce Makefile.in
#
# src/Makefile.am
#
# $Id$
#

SUBDIRS		= bundle lib wrap
bin_SCRIPTS	= revelation
EXTRA_DIST	= revelation.in
CLEANFILES	= revelation


if WITH_APPLET
libexec_SCRIPTS	= revelation-applet
EXTRA_DIST	+= revelation-applet.in
CLEANFILES	+= revelation-applet
endif

revelation: revelation.in
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		revelation.in > revelation

revelation-applet: revelation-applet.in
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		-e "s|\@bindir\@|$(bindir)|" \
		revelation-applet.in > revelation-applet

