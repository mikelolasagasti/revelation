## Process this file with automake to produce Makefile.in
#
# data/bonobo/Makefile.am
#
# $Id$
#

serverdir		= $(libdir)/bonobo/servers
server_DATA		= GNOME_RevelationApplet.server
CLEANFILES		= GNOME_RevelationApplet.server
EXTRA_DIST		= GNOME_RevelationApplet.server.in

GNOME_RevelationApplet.server: GNOME_RevelationApplet.server.in
	sed \
		-e "s|\@libexecdir\@|$(libexecdir)|" \
		GNOME_RevelationApplet.server.in >GNOME_RevelationApplet.server

