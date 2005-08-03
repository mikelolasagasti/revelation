## Process this file with automake to produce Makefile.in
#
# src/wrap/crack/Makefile.am
#
# $Id$
#

module_PROGRAMS	= crack.so
moduledir	= $(pyexecdir)/revelation
CLEANFILES	= crack.c

crack.c: crack.c.in
	sed \
		-e "s|\@CRACK_DICTPATH\@|@CRACK_DICTPATH@|" \
		crack.c.in >crack.c

crack.o: crack.c
	$(CC) -pthread -fno-strict-aliasing -fPIC -I${PYTHON_INCLUDE} -c crack.c -o crack.o

crack.so: crack.o
	$(CC) -Wl --export-dynamic -pthread -shared crack.o -lcrack -o crack.so

