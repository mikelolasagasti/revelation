## Process this file with automake to produce Makefile.in
#
# data/schemas/Makefile.am
#
# $Id$
#

gsettings_SCHEMAS = org.revelation.gschema.xml

gschemas.compiled: $(gsettings_SCHEMAS) Makefile
	$(AM_V_GEN) $(GLIB_COMPILE_SCHEMAS) $(builddir)

@GSETTINGS_RULES@

EXTRA_DIST = \
	org.gnome.Music.gschema.xml

CLEANFILES = \
	gschemas.compiled

all-local: gschemas.compiled

