## Process this file with automake to produce Makefile.in
#
# data/cracklib/Makefile.am
#
# $Id$
#

dictdir		= $(datadir)/revelation
dict_DATA	= pwdict.hwm pwdict.pwd pwdict.pwi
CLEANFILES	= pwdict.hwm pwdict.pwd pwdict.pwi


pwdict.hwm pwdict.pwd pwdict.pwi: pwdict
	$(CRACK_FORMAT) pwdict | $(CRACK_PACKER) pwdict

