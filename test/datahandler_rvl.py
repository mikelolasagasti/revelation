#!/usr/bin/env python

#
# Revelation 0.4.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for Revelation DataHandler module
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

import unittest, re, xml.dom.minidom

from revelation import data, datahandler, entry



class RevelationXML(unittest.TestCase):
	"RevelationXML"

	def test_attrs(self):
		"RevelationXML has sane attributes"

		self.assertNotEqual(datahandler.RevelationXML.name, "")
		self.assertEqual(datahandler.RevelationXML.importer, True)
		self.assertEqual(datahandler.RevelationXML.exporter, True)
		self.assertEqual(datahandler.RevelationXML.encryption, False)



class RevelationXML_check(unittest.TestCase):
	"RevelationXML.check()"

	def test_inv_dataversion(self):
		"RevelationXML.check() raises VersionError on invalid version"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="2">
</revelationdata>
"""

		self.assertRaises(datahandler.VersionError, handler.check, xml)


	def test_inv_docelement(self):
		"RevelationXML.check() rejects invalid document element"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" ?>
<revelation>
</revelation>
"""

		self.assertRaises(datahandler.FormatError, handler.check, xml)


	def test_inv_xmlheader(self):
		"RevelationXML.check() rejects invalid header"

		handler = datahandler.RevelationXML()

		xml = """
<xml version="1.0" ?>
<revelationdata dataversion="1">
</revelationdata>
"""

		self.assertRaises(datahandler.FormatError, handler.check, xml)


	def test_none(self):
		"RevelationXML.check() handles None"

		handler = datahandler.RevelationXML()

		self.assertRaises(datahandler.FormatError, handler.check, None)


	def test_valid(self):
		"RevelationXML.check() accepts valid input"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
</revelationdata>
"""

		self.assertEqual(handler.check(xml), None)



class RevelationXML_detect(unittest.TestCase):
	"RevelationXML.detect()"

	def test_inv(self):
		"RevelationXML.detect() rejects invalid input"

		handler = datahandler.RevelationXML()

		self.assertEqual(handler.detect("dummydata"), False)


	def test_inv_version(self):
		"RevelationXML.detect() rejects invalid version"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="2">
</revelationdata>

"""

		self.assertEquals(handler.detect(xml), False)


	def test_none(self):
		"RevelationXML.detect() handles None"

		handler = datahandler.RevelationXML()

		self.assertEquals(handler.detect(None), False)


	def test_valid(self):
		"RevelationXML.detect() detects valid input"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
</revelationdata>
"""

		self.assertEqual(handler.detect(xml), True)



class RevelationXML_export_data(unittest.TestCase):
	"RevelationXML.export_data()"

	def test_entrydata(self):
		"RevelationXML.export_data() exports all entry data"

		handler = datahandler.RevelationXML()
		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "Generic entry"
		e.description = "A test entry"
		e.updated = 1098822251
		e.get_field(entry.HostnameField).value = "localhost"
		e.get_field(entry.UsernameField).value = "erikg"
		e.get_field(entry.PasswordField).value = "pwtest"

		entrystore.add_entry(e)

		entrystore2 = handler.import_data(handler.export_data(entrystore))

		e2 = entrystore2.get_entry(entrystore2.iter_nth_child(None, 0))

		self.assertEquals(e.name, e2.name)
		self.assertEquals(e.description, e2.description)
		self.assertEquals(e.updated, e2.updated)
		self.assertEquals(e.get_field(entry.HostnameField).value, e2.get_field(entry.HostnameField).value)
		self.assertEquals(e.get_field(entry.UsernameField).value, e2.get_field(entry.UsernameField).value)
		self.assertEquals(e.get_field(entry.PasswordField).value, e2.get_field(entry.PasswordField).value)


	def test_validxml(self):
		"RevelationXML.export_data() generates well-formed XML"

		handler = datahandler.RevelationXML()
		entrystore = data.EntryStore()

		e = entry.FolderEntry()
		e.name = "Folder"
		folderiter = entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "Generic entry"
		e.description = "A test entry"
		e.updated = 1098822251
		e.get_field(entry.HostnameField).value = "localhost"
		e.get_field(entry.UsernameField).value = "erikg"
		e.get_field(entry.PasswordField).value = "pwtest"
		entrystore.add_entry(e, folderiter)
		entrystore.add_entry(e)

		xmldata = handler.export_data(entrystore)
		xml.dom.minidom.parseString(xmldata)
		


class RevelationXML_import_data(unittest.TestCase):
	"RevelationXML.import_data()"

	def test_emptyentry(self):
		"RevelationXML.import_data() handles empty entries"
	
		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic" />
</revelationdata>
"""

		entrystore = handler.import_data(xml)
		e = entrystore.get_entry(entrystore.iter_nth_child(None, 0))

		self.assertNotEqual(e, None)
		self.assertEqual(e.name, "")
		self.assertEqual(e.description, "")
		self.assertNotEqual(e.updated, 0)
		self.assertEqual(type(e), entry.GenericEntry)
		self.assertEqual(e.get_field(entry.HostnameField).value, "")
		self.assertEqual(e.get_field(entry.UsernameField).value, "")
		self.assertEqual(e.get_field(entry.PasswordField).value, "")



	def test_entrydata(self):
		"RevelationXML.import_data() loads all entry data"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>1098738771</updated>
		<field id="generic-hostname">localhost</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		entrystore = handler.import_data(xml)
		e = entrystore.get_entry(entrystore.iter_nth_child(None, 0))

		self.assertEqual(e.name, "Generic entry")
		self.assertEqual(e.description, "A test entry")
		self.assertEqual(e.updated, 1098738771)
		self.assertEqual(type(e), entry.GenericEntry)
		self.assertEqual(e.get_field(entry.HostnameField).value, "localhost")
		self.assertEqual(e.get_field(entry.UsernameField).value, "erikg")
		self.assertEqual(e.get_field(entry.PasswordField).value, "pwtest")


	def test_entrydata(self):
		"RevelationXML.import_data() handles all entry types"

		handler = datahandler.RevelationXML()

		typedata = {
			"folder"	: [],
			"creditcard"	: [ "creditcard-cardtype", "creditcard-cardnumber", "creditcard-expirydate", "creditcard-ccv", "generic-pin" ],
			"cryptokey"	: [ "generic-hostname", "generic-certificate", "generic-keyfile", "generic-password" ],
			"database"	: [ "generic-hostname", "generic-username", "generic-password", "generic-database" ],
			"door"		: [ "generic-location", "generic-code" ],
			"email"		: [ "generic-email", "generic-hostname", "generic-username", "generic-password" ],
			"ftp"		: [ "generic-hostname", "generic-port", "generic-username", "generic-password" ],
			"generic"	: [ "generic-hostname", "generic-username", "generic-password" ],
			"phone"		: [ "phone-phonenumber", "generic-pin" ],
			"shell"		: [ "generic-hostname", "generic-domain", "generic-username", "generic-password" ],
			"website"	: [ "generic-url", "generic-username", "generic-password" ]
		}

		xml = """<?xml version="1.0" ?><revelationdata dataversion="1">"""

		for typename, fieldlist in typedata.items():
			xml += "<entry type=\"" + typename + "\">"

			for field in fieldlist:
				xml += "<field id=\"" + field + "\"></field>"

			xml += "</entry>"

		xml += "</revelationdata>"

		handler.import_data(xml)



	def test_inv_entryfield(self):
		"RevelationXML.import_data() raises DataError on invalid entry field"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>1098738771</updated>
		<field id="creditcard-cardnumber">invalid field type</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.DataError, handler.import_data, xml)



	def test_inv_entrytype(self):
		"RevelationXML.import_data() raises DataError on invalid entry type"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="invalid">
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>1098738771</updated>
		<field id="generic-hostname">localhost</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.DataError, handler.import_data, xml)


	def test_inv_fieldtype(self):
		"RevelationXML.import_data() raises DataError on invalid field type"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>1098738771</updated>
		<field id="invalid">localhost</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.DataError, handler.import_data, xml)


	def test_inv_node(self):
		"RevelationXML.import_data() raises FormatError on unknown nodes"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<dummy />
</revelationdata>
"""

		xml2 = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<dummy />
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.FormatError, handler.import_data, xml)
		self.assertRaises(datahandler.FormatError, handler.import_data, xml2)


	def test_missing_entrytype(self):
		"RevelationXML.import_data() raises FormatError on missing entrytype"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry>
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>1098738771</updated>
		<field id="generic-hostname">localhost</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.FormatError, handler.import_data, xml)

	def test_missing_fieldid(self):
		"RevelationXML.import_data() raises FormatError on missing fieldid"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>1098738771</updated>
		<field>localhost</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.FormatError, handler.import_data, xml)


	def test_parentfolder(self):
		"RevelationXML.import_data() raises DataError when non-folder has children"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<name>Non-folder</name>
		<description>An invalid parent</description>
		<updated>1098738862</updated>

		<entry type="generic">
			<name>Generic entry</name>
			<description>A test entry</description>
			<updated>1098738771</updated>
			<field id="generic-hostname">localhost</field>
			<field id="generic-username">erikg</field>
			<field id="generic-password">pwtest</field>
		</entry>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.DataError, handler.import_data, xml)


	def test_inv_updated(self):
		"RevelationXML.import_data() raises DataError on invalid updatetime"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="generic">
		<name>Generic entry</name>
		<description>A test entry</description>
		<updated>dummy123</updated>
		<field id="generic-hostname">localhost</field>
		<field id="generic-username">erikg</field>
		<field id="generic-password">pwtest</field>
	</entry>
</revelationdata>
"""

		self.assertRaises(datahandler.DataError, handler.import_data, xml)


	def test_valid(self):
		"RevelationXML.import_data() accepts valid input"

		handler = datahandler.RevelationXML()

		xml = """
<?xml version="1.0" encoding="iso-8859-1" ?>
<revelationdata dataversion="1">
	<entry type="folder">
		<name>Folder</name>
		<description>A test folder</description>
		<updated>1098738862</updated>

		<entry type="generic">
			<name>Generic entry</name>
			<description>A test entry</description>
			<updated>1098738771</updated>
			<field id="generic-hostname">localhost</field>
			<field id="generic-username">erikg</field>
			<field id="generic-password">pwtest</field>
		</entry>
	</entry>
</revelationdata>
"""

		self.assertEqual(type(handler.import_data(xml)), data.EntryStore)



class Revelation(unittest.TestCase):
	"Revelation"

	def test_attrs(self):
		"Revelation has sane attributes"

		self.assertNotEqual(datahandler.Revelation.name, "")
		self.assertEqual(datahandler.Revelation.importer, True)
		self.assertEqual(datahandler.Revelation.exporter, True)
		self.assertEqual(datahandler.Revelation.encryption, True)



class Revelation_check(unittest.TestCase):
	"Revelation.check()"

	def test_invalid(self):
		"Revelation.check() raises FormatError on invalid data"

		handler = datahandler.Revelation()

		data = "xxx\x00\x01\x00\x00\x04\x00\x00\x00\x00" + ("\0" * 32)
		self.assertRaises(datahandler.FormatError, handler.check, data)

		data = "rvl\x00\x01\x00\x00\x00\x00jej" + ("\0" * 32)
		self.assertRaises(datahandler.FormatError, handler.check, data)


	def test_none(self):
		"Revelation.check() raises FormatError on None"

		handler = datahandler.Revelation()
		self.assertRaises(datahandler.FormatError, handler.check, None)


	def test_short(self):
		"Revelation.check() raises FormatError on short data"

		handler = datahandler.Revelation()
		data = "rvl\x00\x01\x00\x00\x04\x00\x00\x00\x00"
		self.assertRaises(datahandler.FormatError, handler.check, data)


	def test_valid(self):
		"Revelation.check() handles valid data"

		handler = datahandler.Revelation()
		data = "rvl\x00\x01\x00\x00\x04\x00\x00\x00\x00" + ("\0" * 32)

		handler.check(data)



	def test_version(self):
		"Revelation.check() raises VersionError on unknown version"

		handler = datahandler.Revelation()
		data = "rvl\x00\x02\x00\x00\x04\x00\x00\x00\x00" + ("\0" * 32)
		self.assertRaises(datahandler.VersionError, handler.check, data)



class Revelation_detect(unittest.TestCase):
	"Revelation.detect()"

	def test_invalid(self):
		"Revelation.detect() rejects invalid data"

		handler = datahandler.Revelation()

		data = "xxx\x00\x01\x00\x00\x04\x00\x00\x00\x00" + ("\0" * 32)
		self.assertEquals(handler.detect(data), False)

		data = "rvl\x00\x01\x00\x00\x00\x00jej" + ("\0" * 32)
		self.assertEquals(handler.detect(data), False)


	def test_none(self):
		"Revelation.detect() rejects None"

		handler = datahandler.Revelation()
		self.assertEquals(handler.detect(None), False)


	def test_short(self):
		"Revelation.detect() rejects short data"

		handler = datahandler.Revelation()
		data = "rvl\x00\x01\x00\x00\x04\x00\x00\x00\x00"
		self.assertEquals(handler.detect(data), False)


	def test_valid(self):
		"Revelation.detect() handles valid data"

		handler = datahandler.Revelation()
		data = "rvl\x00\x01\x00\x00\x04\x00\x00\x00\x00" + ("\0" * 32)
		self.assertEquals(handler.detect(data), True)


	def test_version(self):
		"Revelation.detect() rejects unknown versions"

		handler = datahandler.Revelation()
		data = "rvl\x00\x02\x00\x00\x04\x00\x00\x00\x00" + ("\0" * 32)
		self.assertEquals(handler.detect(data), False)


class Revelation_export_data(unittest.TestCase):
	"Revelation.export_data()"

	def setUp(self):

		# set up a common password
		self.password = "test123"

		# set up an entrystore for tests
		self.entrystore = data.EntryStore()

		e = entry.FolderEntry()
		e.name = "Testfolder"
		e.description = "Just a test folder"

		folderiter = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "Generic child"
		e.description = "Child-entry"

		self.entrystore.add_entry(e, folderiter)

		e = entry.GenericEntry()
		e.name = "Another test-entry"
		self.entrystore.add_entry(e)


	def test_header(self):
		"Revelation.export_data() generates a valid header"

		handler = datahandler.Revelation()
		data = handler.export_data(self.entrystore, self.password)

		match = re.match("""
			^		# start of line
			rvl\x00		# magic string
			(.)		# data version
			\x00		# separator
			(.{3})		# app version
			\x00\x00\x00	# separator
		""", data, re.VERBOSE)

		self.assertNotEqual(match, None)
		self.assertEqual(ord(match.group(1)), 1)
		self.assertEqual(ord(match.group(2)[0]) < 10, True)
		self.assertEqual(ord(match.group(2)[1]) < 10, True)
		self.assertEqual(ord(match.group(2)[2]) < 10, True)


	def test_length(self):
		"Revelation.export_data() generates data of correct length"

		handler = datahandler.Revelation()
		data = handler.export_data(self.entrystore, self.password)

		self.assertEqual(len(data) >= 28, True)
		self.assertEqual((len(data) - 12) % 16, 0)


	def test_password_none(self):
		"Revelation.export_data() raises PasswordError on None password"

		handler = datahandler.Revelation()

		self.assertRaises(datahandler.PasswordError, handler.export_data, self.entrystore, None)


	def test_random(self):
		"Revelation.export_data() gives different results each run"

		handler = datahandler.Revelation()

		self.assertNotEqual(
			handler.export_data(self.entrystore, self.password),
			handler.export_data(self.entrystore, self.password)
		)


	def test_valid(self):
		"Revelation.export_data() generates valid data"

		handler = datahandler.Revelation()
		encdata = handler.export_data(self.entrystore, self.password)
		entrystore = handler.import_data(encdata, self.password)

		self.assertEqual(type(entrystore), type(self.entrystore))

		e1 = self.entrystore.get_entry(self.entrystore.iter_nth_child(None, 1))
		e2 = entrystore.get_entry(entrystore.iter_nth_child(None, 1))

		self.assertEqual(type(e1), type(e2))
		self.assertEqual(e1.name, e2.name)
		self.assertEqual(e1.description, e2.description)
		self.assertEqual(e1.updated, e2.updated)

		for f1, f2 in zip(e1.fields, e2.fields):
			self.assertEqual(f1.value, f2.value)



class Revelation_import_data(unittest.TestCase):
	"Revelation.import_data()"

	def setUp(self):

		# set up a common password
		self.password = "test123"

		# set up an entrystore for tests
		self.entrystore = data.EntryStore()

		e = entry.FolderEntry()
		e.name = "Testfolder"
		e.description = "Just a test folder"

		folderiter = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "Generic child"
		e.description = "Child-entry"

		self.entrystore.add_entry(e, folderiter)

		e = entry.GenericEntry()
		e.name = "Another test-entry"
		self.entrystore.add_entry(e)

		handler = datahandler.Revelation()
		self.data = handler.export_data(self.entrystore, self.password)


	def test_inv_header(self):
		"Revelation.import_data() raises FormatError on invalid header"

		handler = datahandler.Revelation()
		self.assertRaises(datahandler.FormatError, handler.import_data, "123" + self.data[3:], self.password)


	def test_inv_length(self):
		"Revelation.import_data() raises FormatError on invalid length"

		handler = datahandler.Revelation()
		self.assertRaises(datahandler.FormatError, handler.import_data, self.data + "123", self.password)


	def test_inv_password(self):
		"Revelation.import_data() raises PasswordError on invalid password"

		handler = datahandler.Revelation()
		self.assertRaises(datahandler.PasswordError, handler.import_data, self.data, "dummypassword")


	def test_inv_version(self):
		"Revelation.import_data() raises VersionError on invalid version"

		handler = datahandler.Revelation()
		self.assertRaises(datahandler.VersionError, handler.import_data, "rvl\x00\x00" + self.data[5:], self.password)
		self.assertRaises(datahandler.VersionError, handler.import_data, "rvl\x00\x02" + self.data[5:], self.password)


	def test_password_long(self):
		"Revelation.import_data() handles long (>32 chars) passwords"

		handler = datahandler.Revelation()
		data = handler.export_data(self.entrystore, "abcdefgh12345678abcdefgh12345678abcdefgh")
		entrystore = handler.import_data(data, "abcdefgh12345678abcdefgh12345678abcdefgh")


	def test_password_none(self):
		"Revelation.import_data() raises PasswordError on None password"

		handler = datahandler.Revelation()
		self.assertRaises(datahandler.PasswordError, handler.import_data, self.data, None)


	def test_valid(self):
		"Revelation.import_data() accepts valid data"

		handler = datahandler.Revelation()
		entrystore = handler.import_data(self.data, self.password)

		self.assertEqual(type(entrystore), type(self.entrystore))

		e1 = self.entrystore.get_entry(self.entrystore.iter_nth_child(None, 1))
		e2 = entrystore.get_entry(entrystore.iter_nth_child(None, 1))

		self.assertEqual(type(e1), type(e2))
		self.assertEqual(e1.name, e2.name)
		self.assertEqual(e1.description, e2.description)
		self.assertEqual(e1.updated, e2.updated)

		for f1, f2 in zip(e1.fields, e2.fields):
			self.assertEqual(f1.value, f2.value)



if __name__ == "__main__":
	unittest.main()

