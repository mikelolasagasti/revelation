librevelationdir	= $(pythondir)/revelation
librevelation_PYTHON	= \
	__init__.py \
	data.py \
	dialog.py \
	entry.py \
	io.py \
	misc.py \
	stock.py \
	widget.py

CLEANFILES		= \
	__init__.py


__init__.py: Makefile __init__.py.in
	sed \
		-e "s|\@GCONFTOOL\@|$(GCONFTOOL)|" \
		-e "s|\@VERSION\@|$(VERSION)|" \
		-e "s|\@datadir\@|$(pkgdatadir)|" \
		-e "s|\@schemadir\@|@GCONF_SCHEMA_FILE_DIR@|" \
		__init__.py.in > __init__.py

