## Process this file with automake to produce Makefile.in
#
# src/Makefile.am
#
# $Id$
#

SUBDIRS		= lib
bin_SCRIPTS	= revelation
libexec_SCRIPTS	= revelation-applet
CLEANFILES	= revelation revelation-applet


revelation: revelation.in
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		revelation.in > revelation

revelation-applet: revelation-applet.in
	sed \
		-e "s|\@pythondir\@|$(pythondir)|" \
		revelation-applet.in > revelation-applet

