#!/usr/bin/env python

#
# Revelation 0.4.2 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for NetRC datahandler module
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


class NetRC(unittest.TestCase):
	"NetRC"

	def test_attrs(self):
		"NetRC has sane attrs"

		self.assertEquals(datahandler.NetRC.name, "netrc")
		self.assertEquals(datahandler.NetRC.importer, True)
		self.assertEquals(datahandler.NetRC.exporter, True)
		self.assertEquals(datahandler.NetRC.encryption, False)



class NetRC_export_data(unittest.TestCase):
	"NetRC.export_data()"

	def setUp(self):
		"Sets up common facilities for testing"

		self.entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 12345678
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		self.entrystore.add_entry(e)

		e = entry.WebEntry()
		e.name = "website"
		e[entry.URLField] = "url"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		self.entrystore.add_entry(e)

		fiter = self.entrystore.add_entry(entry.FolderEntry())

		e = entry.GenericEntry()
		e.name = "name2"
		e.description = "description2"
		e.updated = 87654321
		e[entry.HostnameField] = "hostname2"
		e[entry.UsernameField] = "username2"
		e[entry.PasswordField] = "password2"
		self.entrystore.add_entry(e, fiter)

		e = entry.GenericEntry()
		e.name = "test"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		self.entrystore.add_entry(e)


		self.testdata = """\
# name
# description
machine hostname
	login username
	password password

# name2
# description2
machine hostname2
	login username2
	password password2

"""


	def test_data(self):
		"NetRC.export_data() generates correct data"

		self.assertEquals(datahandler.NetRC().export_data(self.entrystore), self.testdata)



class NetRC_import_data(unittest.TestCase):
	"NetRC.import_data()"

	def test_data(self):
		"NetRC.import_data() imports data correctly"

		netrc = """
# name
# description
machine hostname
	login username
	password password

# name2
# description2
machine hostname2
	login username2
	password password2
"""

		entrystore = datahandler.NetRC().import_data(netrc)

		self.assertEquals(entrystore.iter_n_children(None), 2)

		e = entrystore.get_entry(entrystore.iter_nth_child(None, 0))
		self.assertEquals(type(e), entry.GenericEntry)
		self.assertEquals(e.name, "hostname")
		self.assertNotEqual(e.updated, 0)
		self.assertEquals(e[entry.HostnameField], "hostname")
		self.assertEquals(e[entry.UsernameField], "username")
		self.assertEquals(e[entry.PasswordField], "password")

		e = entrystore.get_entry(entrystore.iter_nth_child(None, 1))
		self.assertEquals(type(e), entry.GenericEntry)
		self.assertEquals(e.name, "hostname2")
		self.assertNotEqual(e.updated, 0)
		self.assertEquals(e[entry.HostnameField], "hostname2")
		self.assertEquals(e[entry.UsernameField], "username2")
		self.assertEquals(e[entry.PasswordField], "password2")


	def test_format(self):
		"NetRC.import_data() raises FormatError on invalid format"

		netrc = """
# name
# description
machine hostname
	login username
	password password

oops
"""

		self.assertRaises(datahandler.FormatError, datahandler.NetRC().import_data, netrc)



if __name__ == "__main__":
	unittest.main()

