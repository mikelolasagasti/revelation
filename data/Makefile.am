SUBDIRS		= images ui

desktopdir	= $(datadir)/applications
desktop_DATA	= revelation.desktop

schemadir	= @GCONF_SCHEMA_FILE_DIR@
schema_DATA	= revelation.schemas

install-schemas:
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
	$(GCONFTOOL) --makefile-install-rule $(schema_DATA)

