SUBDIRS		= icons mime ui

desktopdir	= $(datadir)/applications
desktop_DATA	= revelation.desktop

schemadir	= @GCONF_SCHEMA_FILE_DIR@
schema_DATA	= revelation.schemas

install-data-hook:
if GCONF_SCHEMAS_INSTALL
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
	$(GCONFTOOL) --makefile-install-rule $(schema_DATA)
endif

if HAVE_FDO_DESKTOP
	$(UPDATE_DESKTOP_DATABASE)
endif

