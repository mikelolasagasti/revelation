## Process this file with automake to produce Makefile.in
#
# Makefile.am
#
# $Id$
#

AUTOMAKE_OPTIONS	= dist-bzip2 no-dist-gzip
SUBDIRS			= data po src

dist-hook:
	svn2cl.sh\
		--authors=$(top_srcdir)/authors.xml \
		--group-by-day \
		--separate-daylogs \
		--include-rev \
		--file=$(top_distdir)/ChangeLog \
		https://oss.codepoet.no/svn/revelation/tags/$(PACKAGE)-$(VERSION)

