module_PROGRAMS	= crack.so
moduledir	= $(pythondir)/revelation
CLEANFILES	= crack.c


crack.c:
	sed \
		-e "s|\@CRACK_DICTPATH\@|@CRACK_DICTPATH@|" \
		crack.c.in >crack.c

crack.o: crack.c
	$(CC) -pthread -fno-strict-aliasing -fPIC -I${PYTHON_INCLUDE} -c crack.c -o crack.o

crack.so: crack.o
	$(CC) -Wl --export-dynamic -pthread -shared crack.o -lcrack -o crack.so

