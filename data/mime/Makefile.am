mime_DATA	= revelation.xml
mimedir		= $(datadir)/mime/packages

install-data-hook:
if FDO_MIME
	@if test -z "$(DESTDIR)"; then \
		$(UPDATE_MIME_DATABASE) "$(datadir)/mime"; \
	fi
endif

