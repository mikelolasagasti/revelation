SUBDIRS			= datahandler
CLEANFILES		= __init__.py
BUILT_SOURCES		= __init__.py


librevelationdir	= $(pythondir)/revelation
librevelation_PYTHON	= \
	__init__.py \
	config.py \
	data.py \
	dialog.py \
	entry.py \
	io.py \
	stock.py \
	util.py \
	widget.py


__init__.py: Makefile __init__.py.in
	sed \
		-e "s|\@GCONFTOOL\@|$(GCONFTOOL)|" \
		-e "s|\@VERSION\@|$(VERSION)|" \
		-e "s|\@datadir\@|$(datadir)|" \
		-e "s|\@pkgdatadir\@|$(pkgdatadir)|" \
		-e "s|\@pkgschemadir\@|@GCONF_SCHEMA_FILE_DIR@|" \
		__init__.py.in > __init__.py

