## Process this file with automake to produce Makefile.in
#
# data/gconf/Makefile.am
#
# $Id$
#

schemadir	= @GCONF_SCHEMA_FILE_DIR@
schema_DATA	= revelation.schemas


install-data-hook:
if GCONF_SCHEMAS_INSTALL
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
	$(GCONFTOOL) --makefile-install-rule $(schema_DATA)
endif

