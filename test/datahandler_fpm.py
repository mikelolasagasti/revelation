#!/usr/bin/env python

#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id: datahandler.py 168 2004-10-22 18:17:27Z erikg $
#
# Unit tests for FPM datahandler module
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

import unittest, xml.dom.minidom

from revelation import data, datahandler, entry, util


class FPM(unittest.TestCase):
	"FPM"

	def test_attrs(self):
		"FPM has sane attributes"

		self.assertNotEqual(datahandler.FPM.name, "")
		self.assertEqual(datahandler.FPM.importer, True)
		self.assertEqual(datahandler.FPM.exporter, True)
		self.assertEqual(datahandler.FPM.encryption, True)



class FPM_check(unittest.TestCase):
	"FPM.check()"


	def test_inv_baseattrs(self):
		"FPM.check() raises FormatError on missing base attributes"

		xml = """
<?xml version="1.0" ?>
<FPM>
</FPM>
"""

		handler = datahandler.FPM()
		self.assertRaises(datahandler.FormatError, handler.check, xml)



	def test_inv_root(self):
		"FPM.check() raises FormatError on wrong root element"

		xml = """
<?xml version="1.0" ?>
<FPMDATA full_version="00.58.00" min_version="00.58.00" display_version="00.58.00">
</FPMDATA>
"""

		handler = datahandler.FPM()
		self.assertRaises(datahandler.FormatError, handler.check, xml)


	def test_inv_version(self):
		"FPM.check() raises VersionError on invalid version"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.60.00" min_version="00.60.00" display_version="00.60.00">
</FPM>
"""

		handler = datahandler.FPM()
		self.assertRaises(datahandler.VersionError, handler.check, xml)


	def test_inv_version_format(self):
		"FPM.check() raises FormatError on invalid version format"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="jeje123" display_version="00.58.00">
</FPM>
"""

		handler = datahandler.FPM()
		self.assertRaises(datahandler.FormatError, handler.check, xml)


	def test_inv_xml(self):
		"FPM.check() raises FormatError on invalid XML"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="00.58.00" display_version="00.58.00">
</FPMDATA>
"""

		handler = datahandler.FPM()
		self.assertRaises(datahandler.FormatError, handler.check, xml)


	def test_none(self):
		"FPM.check() raises FormatError on None"

		handler = datahandler.FPM()
		self.assertRaises(datahandler.FormatError, handler.check, None)


	def test_valid(self):
		"FPM.check() accepts valid data"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="00.58.00" display_version="00.58.00">
</FPM>
"""

		handler = datahandler.FPM()
		handler.check(xml)


class FPM_detect(unittest.TestCase):
	"FPM.detect()"

	def test_inv(self):
		"FPM.detect() rejects invalid data"

		handler = datahandler.FPM()
		self.assertEqual(handler.detect("dummydata"), False)


	def test_inv_version(self):
		"FPM.detect() rejects invalid version"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.60.00" min_version="00.60.00" display_version="00.60.00">
</FPM>
"""

		handler = datahandler.FPM()
		self.assertEqual(handler.detect(xml), False)


	def test_none(self):
		"FPM.detect() rejects None"

		handler = datahandler.FPM()
		self.assertEqual(handler.detect(None), False)


	def test_valid(self):
		"FPM.detect() accepts valid data"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="00.58.00" display_version="00.58.00">
</FPM>
"""

		handler = datahandler.FPM()
		self.assertEqual(handler.detect(xml), True)



class FPM_export_data(unittest.TestCase):
	"FPM.export_data()"

	def test_valid(self):
		"FPM.export_data() generates valid data"

		# set up data
		entrystore = data.EntryStore()

		e = entry.FolderEntry()
		e.name = "Testfolder"
		e.description = "Just a test folder"

		folderiter = entrystore.add_entry(None, e)

		e = entry.GenericEntry()
		e.name = "Generic child"
		e.description = "Child-entry"
		e.get_field(entry.HostnameField).value = "www.slashdot.org"
		e.get_field(entry.UsernameField).value = "erikg"
		e.get_field(entry.PasswordField).value = "test123"

		entrystore.add_entry(folderiter, e)

		e = entry.WebEntry()
		e.name = "A website entry"
		e.get_field(entry.URLField).value = "http://www.kuro5hin.org/"
		e.get_field(entry.UsernameField).value = "egrinake"
		e.get_field(entry.PasswordField).value = "pwtest"
		entrystore.add_entry(None, e)


		# test the export
		handler = datahandler.FPM()
		fpmdata = handler.export_data(entrystore, "test")

		dom = xml.dom.minidom.parseString(fpmdata)
		itemnodes = dom.getElementsByTagName("PasswordItem")

		entrydata = {}
		for childnode in [ node for node in itemnodes[0].childNodes if node.nodeType == node.ELEMENT_NODE ]:
			entrydata[childnode.nodeName] = util.dom_text(childnode)

		fe = entrystore.get_entry(folderiter)
		e = entrystore.get_entry(entrystore.iter_nth_child(folderiter, 0))

		self.assertEqual(e.name, entrydata["title"])
		self.assertEqual(e.description, entrydata["notes"])
		self.assertEqual(fe.name, entrydata["category"])
		self.assertEqual(e.get_field(entry.HostnameField).value, entrydata["url"])
		self.assertEqual(e.get_field(entry.UsernameField).value, entrydata["user"])
		self.assertEqual(e.get_field(entry.PasswordField).value, entrydata["password"])


		entrydata = {}
		for childnode in [ node for node in itemnodes[1].childNodes if node.nodeType == node.ELEMENT_NODE ]:
			entrydata[childnode.nodeName] = util.dom_text(childnode)

		e = entrystore.get_entry(entrystore.iter_nth_child(None, 1))

		self.assertEqual(e.name, entrydata["title"])
		self.assertEqual(e.description, entrydata["notes"])
		self.assertEqual("", entrydata["category"])
		self.assertEqual(e.get_field(entry.URLField).value, entrydata["url"])
		self.assertEqual(e.get_field(entry.UsernameField).value, entrydata["user"])
		self.assertEqual(e.get_field(entry.PasswordField).value, entrydata["password"])




class FPM_import_data(unittest.TestCase):
	"FPM.import_data()"

	def test_inv_password(self):
		"FPM.import_data() raises PasswordError on invalid password"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="00.58.00" display_version="0.58">
	<KeyInfo salt="imljjkpg" vstring="ofnabdkjbmopgaha"/>
</FPM>
"""

		handler = datahandler.FPM()
		self.assertRaises(datahandler.PasswordError, handler.import_data, xml, "wrongpw")


	def test_nodata(self):
		"FPM.import_data() handles empty data"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="00.58.00" display_version="0.58">
	<KeyInfo salt="imljjkpg" vstring="ofnabdkjbmopgaha"/>
</FPM>
"""

		handler = datahandler.FPM()
		handler.import_data(xml, "test")


	def test_none(self):
		"FPM.import_data() raises FormatError on None"

		handler = datahandler.FPM()
		self.assertRaises(datahandler.FormatError, handler.import_data, None, "test")


	def test_valid(self):
		"FPM.import_data() accepts valid data"

		xml = """
<?xml version="1.0" ?>
<FPM full_version="00.58.00" min_version="00.58.00" display_version="0.58">
	<KeyInfo salt="ncppipdn" vstring="poadhodhplbegpjm"/>
	<LauncherList>
		<LauncerItem><title>Web</title><cmdline>gnome-moz-remote "$a"</cmdline><copy_user>2</copy_user><copy_password>1</copy_password></LauncerItem>
		<LauncerItem><title>ssh</title><cmdline>gnome-terminal -e 'ssh $a -l $u'</cmdline><copy_user>0</copy_user><copy_password>1</copy_password></LauncerItem>
		<LauncerItem><title>Generic Command</title><cmdline>$a</cmdline><copy_user>0</copy_user><copy_password>0</copy_password></LauncerItem>
	</LauncherList>
	<PasswordList>
		<PasswordItem><title>noogeghgacbjkembbkcndhfmnpomakao</title><user>lidannbdlfpgbbhmhcfkjcnegceimapi</user><url>nhdlpgkdickpaoafapcflihmlfopckkapnaolgoglkfmkpjg</url><password>dnijaohfckjnddgpggjhfiienhgccmejnpbgddffgkiflhocilchedanbdecjfpnpmmjapijikapecnjfgaheppnjkhiacdmkndocanomelohfhadcmhcdddcjdmghaoicogbopbgchbnakiombpmbmlgkillcebkcpjpdcpdmalcgkccmmfbpeikhlfbacmlogopgdilpndajkbhhiflmbgblkonhpldfihmooajlodnogikgiehkaneeecfblaclikhedihkfhcpdalmaphohijmfaagliladeecchlbfbokfeikjbbpcgaegcjplpcalembmigjppbjlolbcempdpoibgiblhgmcbpmidbnickamieedfgigeenpmaoflmaddhoemmpbiplpgnnfamcebhompngcdpfonpkgnfkpgdognneongealocmfimfdnpcgjppmndhcfcnabjfmpehlfpfjanmjccfelbjfdlgldiimnahjjhfcmlgbjnpk</password><notes>iihkgjebgnghghhm</notes><category>gjnkbgnchgehiajb</category><launcher>dnajoaniehgnljed</launcher></PasswordItem>
		<PasswordItem><title>kofckpmcobmpoiamdhhogkdinpkihfkh</title><user>paljgfjdncoelohf</user><url>iamoledhnphfppocmccppepcflkinibbhlfpbfgifpijdceeohkacpbdkjcpmlnj</url><password>jpcdkgikeoojckbahdjdnhfpebmbndmbcajnajpfgdpfjemjnmeleaenkmmnonpelajpempdacmgmflnpcccafgagacmnkkiknbdkcfmbelgpdemcpojgibjoiiaccncjhleebhfgodknfajemlmidcnicppfkhkmbacmfpgkheplcjaejgmkokilfcclenfjinmlaijnahjbhiafjkcjnfffknahgifjhcmdlmgjggjdcojnhoadjaeobjjgpgicopmkckkaonbccopcocdbemdocingpeiehaocdmkkclpklegabpobjalijehnmfklicldndpcenbklnobjcjeeigknodicmlffnejfgcbhedmogipbfbfobmcaeoodpgnojbjfcpjdljgmbdingphkjeibpcomgfdgknigejailonledhgnmopcpocaiammlldkfgankgjheioaaejffmohhefgiagkflaednjogjogknchnjgfjkidkhheclllh</password><notes>njpmfmbdaohdckpgapbgmkjpbpibfnkfakckalefcipcmfahhljcdkmdppdnbkaefcdlpcjjhhmlcgin</notes><category>kgalgbjejfamgdbo</category><launcher>phmnfgmbhmnjanbc</launcher></PasswordItem>
	</PasswordList>
</FPM>
"""

		handler = datahandler.FPM()
		entrystore = handler.import_data(xml, "test")

		folderiter = entrystore.iter_nth_child(None, 0)
		folderentry = entrystore.get_entry(folderiter)

		self.assertEqual(type(folderentry), entry.FolderEntry)
		self.assertEqual(folderentry.name, "web")
		self.assertNotEqual(folderentry.updated, 0)

		e = entrystore.get_entry(entrystore.iter_nth_child(folderiter, 0))
		self.assertEqual(type(e), entry.GenericEntry)
		self.assertEqual(e.name, "kuro5hin")
		self.assertEqual(e.description, "")
		self.assertNotEqual(e.updated, 0)
		self.assertEqual(e.get_field(entry.UsernameField).value, "egrinake")
		self.assertEqual(e.get_field(entry.HostnameField).value, "www.kuro5hin.org")
		self.assertEqual(e.get_field(entry.PasswordField).value, "jeje")

		e = entrystore.get_entry(entrystore.iter_nth_child(folderiter, 1))
		self.assertEqual(type(e), entry.GenericEntry)
		self.assertEqual(e.name, "slashdot")
		self.assertEqual(e.description, "Username and password for /.")
		self.assertNotEqual(e.updated, 0)
		self.assertEqual(e.get_field(entry.UsernameField).value, "erikg")
		self.assertEqual(e.get_field(entry.HostnameField).value, "http://www.slashdot.org/")
		self.assertEqual(e.get_field(entry.PasswordField).value, "test")



if __name__ == "__main__":
	unittest.main()
