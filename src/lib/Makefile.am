SUBDIRS			= datahandler
CLEANFILES		= config.py
BUILT_SOURCES		= config.py


librevelationdir	= $(pythondir)/revelation
librevelation_PYTHON	= \
	__init__.py \
	config.py \
	data.py \
	dialog.py \
	entry.py \
	io.py \
	ui.py \
	util.py \
	widget.py


config.py: Makefile config.py.in
	sed \
		-e "s|\@GCONFTOOL\@|$(GCONFTOOL)|" \
		-e "s|\@VERSION\@|$(VERSION)|" \
		-e "s|\@datadir\@|$(datadir)|" \
		-e "s|\@pkgdatadir\@|$(pkgdatadir)|" \
		-e "s|\@pkgschemadir\@|@GCONF_SCHEMA_FILE_DIR@|" \
		config.py.in > config.py

