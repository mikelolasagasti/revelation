## Process this file with automake to produce Makefile.in
#
# Makefile.am
#
# $Id$
#

AUTOMAKE_OPTIONS	= dist-bzip2 no-dist-gzip
SUBDIRS			= data po src

dist-hook:
	hg log --style changelog > $(top_distdir)/ChangeLog
