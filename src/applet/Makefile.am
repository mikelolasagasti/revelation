libexec_SCRIPTS	= revelation-applet
EXTRA_DIST	= revelation-applet.py
CLEANFILES	= revelation-applet


revelation-applet:	revelation-applet.py
	sed \
		-e "s|\@pyexecdir\@|$(pyexecdir)|" \
		-e "s|\@bindir\@|$(bindir)|" \
		revelation-applet.py > revelation-applet
