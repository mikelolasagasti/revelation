#!/usr/bin/env python

#
# Revelation 0.4.1 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for PlainText datahandler module
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

import unittest

from revelation import data, datahandler, entry


class PlainText(unittest.TestCase):
	"PlainText"

	def test_attrs(self):
		"PlainText has sane attrs"

		self.assertEquals(datahandler.PlainText.name, "Plain text")
		self.assertEquals(datahandler.PlainText.importer, False)
		self.assertEquals(datahandler.PlainText.exporter, True)
		self.assertEquals(datahandler.PlainText.encryption, False)



class Plaintext_export_data(unittest.TestCase):
	"PlainText.export_data()"

	def test_data(self):
		"PlainText.export_data() exports data"

		s = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1107348151
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		s.add_entry(e)

		text = datahandler.PlainText().export_data(s)

		self.assertEquals(e.typename in text, True)
		self.assertEquals("name" in text, True)
		self.assertEquals("description" in text, True)
		self.assertEquals("2005-02-02 13:42:31" in text, True)
		self.assertEquals("hostname" in text, True)
		self.assertEquals("username" in text, True)
		self.assertEquals("password" in text, True)


	def test_folder(self):
		"PlainText.export_data() ignores folders"

		s = data.EntryStore()
		e = entry.FolderEntry()
		e.name = "testfolder"
		s.add_entry(e)

		text = datahandler.PlainText().export_data(s)
		self.assertEquals(text, "")



if __name__ == "__main__":
	unittest.main()

