## Process this file with automake to produce Makefile.in
#
# src/Makefile.am
#
# $Id$
#

SUBDIRS		= lib
bin_SCRIPTS	= revelation
CLEANFILES	= revelation


revelation: revelation.in
	sed \
		-e "s|\@pythondir\@|$(pythondir)|" \
		revelation.in > revelation

