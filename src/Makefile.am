SUBDIRS		= lib
bin_SCRIPTS	= revelation
CLEANFILES	= revelation

revelation: Makefile revelation.in
	sed \
		-e "s|\@pythondir\@|$(pythondir)|" \
		revelation.in > revelation

