mime_DATA	= revelation.xml
mimedir		= $(datadir)/mime/packages

install-data-hook:
if HAVE_FDO_MIME
	$(UPDATE_MIME_DATABASE) "$(datadir)/mime"
endif

