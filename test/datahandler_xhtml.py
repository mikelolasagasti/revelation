#!/usr/bin/env python

#
# Revelation 0.4.1 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for XHTML datahandler module
#
#
# Copyright (c) 2003-2005 Erik Grinaker
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import unittest, xml.dom.minidom

from revelation import data, datahandler, entry



class XHTML(unittest.TestCase):
	"XHTML()"

	def test_attrs(self):
		"XHTML has sane attrs"

		self.assertEquals(datahandler.XHTML.name, "XHTML / CSS")
		self.assertEquals(datahandler.XHTML.importer, False)
		self.assertEquals(datahandler.XHTML.exporter, True)
		self.assertEquals(datahandler.XHTML.encryption, False)



class XHTML_export_data(unittest.TestCase):
	"XHTML.export_data()"

	def setUp(self):
		"set up common facilities for tests"

		self.entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "Generic entry"
		e.description = "A test entry"
		e.updated = 1098822251
		e[entry.HostnameField] = "localhost"
		e[entry.UsernameField] = "erikg"
		e[entry.PasswordField] = "pwtest"
		self.entrystore.add_entry(e)

		f = entry.FolderEntry()
		f.name = "Folder"
		fiter = self.entrystore.add_entry(f)

		e = entry.WebEntry()
		e.name = "Web entry"
		e.description = "A test web entry"
		e.updated = 123456789
		e[entry.URLField] = "http://www.slashdot.org/"
		e[entry.UsernameField] = "erikg"
		e[entry.PasswordField] = "pwtest"
		self.entrystore.add_entry(e, fiter)


	def test_wellformed(self):
		"XHTML.export_data() generates well-formed XML"

		xml.dom.minidom.parseString(datahandler.XHTML().export_data(self.entrystore))



if __name__ == "__main__":
	unittest.main()

