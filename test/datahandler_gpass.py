#!/usr/bin/env python

#
# Revelation 0.4.2 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for GNOME Password Manager DataHandler module
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



TESTDATA	= "\x16\x43\x0e\x37\xde\xc3\xf3\x14\x4f\xec\xc3\xd4\xd9\xcc\x2a\x6e\xa9\x89\x6f\xd8\x3a\x34\x66\x61\x3c\xd4\x15\x3f\xe0\xd9\xa4\x5b\x5b\x8a\x87\x35\x26\x7d\x65\x09\x22\x1f\x08\xf5\xfb\x5e\x2b\x30\x2a\xec\xe4\x43\xb4\xa8\xae\x06\x48\xb7\xd7\x91\xbd\x8a\x17\x38\x9f\xee\xd1\x5e\xa4\xd6\xa0\x3d\xda\x0e\xd6\x59\x98\x29\x75\xcb\x68\x0a\x20\x79\xc3\x20\x30\x0d\xcf\x8b\x4f\xb6\xba\xd5\x2c\x49\xa9\x79\x6d\xc4\xee\x68\xf0\x6f\x35\xfd\x36\x54\x3b\xc0\x18\x99\xea\x5b\xb9\x48\x5f\xd3\x4a\x28\x7b\x3b\x1a\x91\x9d\x31\xa1\x0f\x24\x0c\x3e\x39\x61\x4e\x67\x88\x1b\x98\xd1\xa1\x64\x0d\x19\x0a\x02\x53\x2f\xf9\xfe\xf0\xf0\x0c"
TESTPASSWORD	= "test123"


class GPass(unittest.TestCase):
	"GPass"

	def test_attrs(self):
		"GPass has sane attrs"

		self.assertEquals(datahandler.GPass.name, "GNOME Password Manager (gpass)")
		self.assertEquals(datahandler.GPass.importer, True)
		self.assertEquals(datahandler.GPass.exporter, True)
		self.assertEquals(datahandler.GPass.encryption, True)



class GPass_export_data(unittest.TestCase):
	"GPass.export_data()"

	def test_export(self):
		"GPass.export_data() generates valid output"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1104863615
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		e[entry.HostnameField] = "hostname"
		entrystore.add_entry(e)

		f = entry.FolderEntry()
		f.name = "folder"
		fiter = entrystore.add_entry(f)

		e = entry.WebEntry()
		e.name = "website"
		e.description = "desc"
		e.updated = 1104863643
		e[entry.URLField] = "url"
		e[entry.UsernameField] = "user"
		e[entry.PasswordField] = "pass"
		entrystore.add_entry(e, fiter)

		self.assertEquals(datahandler.GPass().export_data(entrystore, TESTPASSWORD), TESTDATA)



class GPass_import_data(unittest.TestCase):
	"GPass.import_data"

	def test_data(self):
		"GPass.import_data() imports data correctly"

		entrystore = datahandler.GPass().import_data(TESTDATA, TESTPASSWORD)

		self.assertEquals(entrystore.iter_n_children(None), 2)

		e = entrystore.get_entry(entrystore.iter_nth_child(None, 0))
		self.assertEquals(type(e), entry.GenericEntry)
		self.assertEquals(e.name, "name")
		self.assertEquals(e.description, "description")
		self.assertEquals(e.updated, 1104863615)
		self.assertEquals(e[entry.HostnameField], "hostname")
		self.assertEquals(e[entry.UsernameField], "username")
		self.assertEquals(e[entry.PasswordField], "password")

		e = entrystore.get_entry(entrystore.iter_nth_child(None, 1))
		self.assertEquals(type(e), entry.GenericEntry)
		self.assertEquals(e.name, "website")
		self.assertEquals(e.description, "desc")
		self.assertEquals(e.updated, 1104863643)
		self.assertEquals(e[entry.HostnameField], "url")
		self.assertEquals(e[entry.UsernameField], "user")
		self.assertEquals(e[entry.PasswordField], "pass")


	def test_password(self):
		"GPass.import_data() raises PasswordError on wrong password"

		self.assertRaises(datahandler.PasswordError, datahandler.GPass().import_data, TESTDATA, "wrongpassword")



if __name__ == "__main__":
	unittest.main()

