#!/usr/bin/env python

#
# Revelation 0.2.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for entry module
#
#
# Copyright (c) 2003-2004 Erik Grinaker
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

import time, unittest

from revelation import entry



class Entry(unittest.TestCase):
	"Required entries exists"

	def test_entries(self):
		"entries are successfully init'ed"

		for e in entry.ENTRYLIST:
			e()


	def test_entrylist(self):
		"entry.ENTRYLIST contains all required entry types"

		entries = [
			entry.FolderEntry,
			entry.CreditcardEntry,
			entry.CryptoKeyEntry,
			entry.DatabaseEntry,
			entry.DoorEntry,
			entry.EmailEntry,
			entry.FTPEntry,
			entry.GenericEntry,
			entry.PhoneEntry,
			entry.ShellEntry,
			entry.WebEntry
		]

		for e in entries:
			self.assertEquals(e in entry.ENTRYLIST, True)



class Entry__init(unittest.TestCase):
	"Entry.__init__()"

	def test_updated(self):
		"Entry.__init__() sets update-time to now"

		self.assertEquals(entry.GenericEntry().updated, int(time.time()))



class Entry__getitem(unittest.TestCase):
	"Entry.__getitem__()"

	def test_inv_field(self):
		"Entry.__getitem__() raises EntryFieldError on invalid field"

		e = entry.GenericEntry()
		self.assertRaises(entry.EntryFieldError, e.__getitem__, entry.URLField)


	def test_value(self):
		"Entry.__getitem__() returns the field value"

		e = entry.GenericEntry()
		e.get_field(entry.HostnameField).value = "test123"

		self.assertEquals(e[entry.HostnameField], "test123")



class Entry__setitem(unittest.TestCase):
	"Entry.__setitem__()"

	def test_inv_field(self):
		"Entry.__setitem__() raises EntryFieldError in invalid field"

		e = entry.GenericEntry()
		self.assertRaises(entry.EntryFieldError, e.__setitem__, entry.URLField, "test123")


	def test_value(self):
		"Entry.__setitem__() sets the field value"

		e = entry.GenericEntry()
		e[entry.HostnameField] = "test123"

		self.assertEquals(e[entry.HostnameField], "test123")



class Entry_copy(unittest.TestCase):
	"Entry.copy()"

	def test_copy(self):
		"Entry.copy() copies all attributes"

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"

		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"

		e2 = e.copy()

		self.assertEqual(e.name, e2.name)
		self.assertEqual(e.description, e2.description)
		self.assertEqual(e.updated, e2.updated)
		self.assertEqual(e[entry.HostnameField], e2[entry.HostnameField])
		self.assertEqual(e[entry.UsernameField], e2[entry.UsernameField])
		self.assertEqual(e[entry.PasswordField], e2[entry.PasswordField])

		e2[entry.HostnameField] = "changetest"

		self.assertNotEqual(e[entry.HostnameField], e2[entry.HostnameField])



class Entry_get_field(unittest.TestCase):
	"Entry.get_field()"

	def test_inv_field(self):
		"Entry.get_field() raises EntryFieldError on invalid field"

		e = entry.GenericEntry()
		self.assertRaises(entry.EntryFieldError, e.get_field, entry.URLField)


	def test_valid(self):
		"Entry.get_field() returns the field object"

		e = entry.GenericEntry()
		field = e.get_field(entry.HostnameField)
		field.value = "test123"

		self.assertEqual(type(field), entry.HostnameField)
		self.assertEqual(e[entry.HostnameField], "test123")



class Entry_has_field(unittest.TestCase):
	"Entry.has_field()"

	def test_invalid(self):
		"Entry.has_field() returns False when field doesn't exist"

		e = entry.GenericEntry()
		self.assertEqual(e.has_field(entry.URLField), False)


	def test_valid(self):
		"Entry.has_field() returns True when field exists"

		e = entry.GenericEntry()
		self.assertEqual(e.has_field(entry.HostnameField), True)



class Entry_mirror(unittest.TestCase):
	"Entry.mirror()"

	def test_copy(self):
		"Entry.mirror() copies all data"

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"

		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"

		e2 = entry.GenericEntry()
		e2.mirror(e)

		self.assertEqual(e.name, e2.name)
		self.assertEqual(e.description, e2.description)
		self.assertEqual(e.updated, e2.updated)
		self.assertEqual(e[entry.HostnameField], e2[entry.HostnameField])
		self.assertEqual(e[entry.UsernameField], e2[entry.UsernameField])
		self.assertEqual(e[entry.PasswordField], e2[entry.PasswordField])


	def test_inv_type(self):
		"Entry.mirror() raises EntryTypeError on other source type"

		e = entry.GenericEntry()
		e2 = entry.WebEntry()

		self.assertRaises(entry.EntryTypeError, e.mirror, e2)



class Field(unittest.TestCase):
	"field module"

	def test_entrylist(self):
		"entry.ENTRYLIST contains all required entry types"

		fields = [
			entry.CardnumberField,
			entry.CardtypeField,
			entry.CCVField,
			entry.CertificateField,
			entry.CodeField,
			entry.DatabaseField,
			entry.DomainField,
			entry.EmailField,
			entry.ExpirydateField,
			entry.HostnameField,
			entry.KeyfileField,
			entry.LocationField,
			entry.PasswordField,
			entry.PhonenumberField,
			entry.PINField,
			entry.PortField,
			entry.URLField,
			entry.UsernameField
		]

		for f in fields:
			self.assertEquals(f in entry.FIELDLIST, True)


	def test_fieldtypes(self):
		"all field types exist"

		fields = [
			entry.CardnumberField,
			entry.CardtypeField,
			entry.CCVField,
			entry.CertificateField,
			entry.CodeField,
			entry.DatabaseField,
			entry.DomainField,
			entry.EmailField,
			entry.ExpirydateField,
			entry.HostnameField,
			entry.KeyfileField,
			entry.LocationField,
			entry.PasswordField,
			entry.PhonenumberField,
			entry.PINField,
			entry.PortField,
			entry.URLField,
			entry.UsernameField
		]

		for f in fields:
			f()



class Field__init(unittest.TestCase):
	"Field()"

	def test_attrs(self):
		"Field.__init__() sets proper attributes"

		f = entry.Field()

		f.id
		f.name
		f.description
		f.symbol
		f.datatype
		f.value


	def test_value(self):
		"Field.__init__() properly sets a value"

		f = entry.Field("jeje")
		self.assertEquals(f.value, "jeje")



class Field__str(unittest.TestCase):
	"Field.__str__()"


	def test_none(self):
		"Field.__str__() returns '' instead of None"

		f = entry.Field(None)
		self.assertEquals(str(f), "")

		
	def test_value(self):
		"Field.__str__() returns the value"

		f = entry.Field("test")
		self.assertEquals(str(f), "test")



class convert_entry_generic(unittest.TestCase):
	"convert_entry_generic()"

	def test_generic(self):
		"convert_entry_generic() returns an identical generic entry"

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"

		c = entry.convert_entry_generic(e)

		self.assertEquals(c.name, e.name)
		self.assertEquals(c.description, e.description)
		self.assertEquals(c.updated, e.updated)
		self.assertEquals(c[entry.HostnameField], e[entry.HostnameField])
		self.assertEquals(c[entry.UsernameField], e[entry.UsernameField])
		self.assertEquals(c[entry.PasswordField], e[entry.PasswordField])


	def test_generic_always(self):
		"convert_entry_generic() returns GenericEntry for all entry types"

		for entrytype in entry.ENTRYLIST:
			generic = entry.convert_entry_generic(entrytype())
			self.assertEquals(type(generic), entry.GenericEntry)



if __name__ == "__main__":
	unittest.main()

