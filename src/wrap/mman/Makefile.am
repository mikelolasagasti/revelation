## Process this file with automake to produce Makefile.in
#
# src/wrap/mman/Makefile.am
#
# $Id$
#

module_PROGRAMS	= mman.so
moduledir	= $(pyexecdir)/revelation

mman.o: mman.c
	$(CC) -pthread -fno-strict-aliasing -fPIC -I${PYTHON_INCLUDE} -c mman.c -o mman.o

mman.so: mman.o
	$(CC) -Wl --export-dynamic -pthread -shared mman.o -o mman.so

