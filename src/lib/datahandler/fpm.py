#
# Revelation 0.4.1 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling Figaro's Password Manager data
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

import base
from revelation import data, entry, util

import math, random, string, xml.dom.minidom

from xml.parsers.expat import ExpatError
from Crypto.Cipher import Blowfish
from Crypto.Hash import MD5



class FPM(base.DataHandler):
	"Data handler for Figaro's Password Manager data"

	name		= "Figaro's Password Manager"
	importer	= True
	exporter	= True
	encryption	= True


	def __init__(self):
		base.DataHandler.__init__(self)


	def __decrypt(self, cipher, data):
		"Decrypts data"

		# decode ascii armoring
		decoded = ""

		for i in range(len(data) / 2):
			high = ord(data[2 * i]) - ord("a")
			low = ord(data[2 * i + 1]) - ord("a")
			decoded += chr(high * 16 + low)

		data = decoded

		# decrypt data
		data = cipher.decrypt(data)

		# unrotate field
		blocks = int(math.ceil(len(data) / float(8)))
		plain = ""

		for offset in range(8):
			for block in range(blocks):
				plain += data[block * 8 + offset]

		return plain.split("\x00")[0]


	def __encrypt(self, cipher, data):
		"Encrypts data"

		# get data sizes
		blocks = (len(data) / 7) + 1
		size = 8 * blocks

		# add noise
		data += "\x00" + util.random_string(size - len(data) - 1)

		# rotate data
		rotated = ""
		for block in range(blocks):
			for offset in range(8):
				rotated += data[offset * blocks + block]

		data = rotated

		# encrypt data
		data = cipher.encrypt(data)

		# ascii-armor data
		res = ""

		for i in range(len(data)):
			high = ord(data[i]) / 16
			low = ord(data[i]) - high * 16
			res += chr(ord("a") + high) + chr(ord("a") + low)

		data = res


		return data


	def check(self, input):
		"Checks if the data is valid"

		try:
			if input is None:
				raise base.FormatError

			dom = xml.dom.minidom.parseString(input.strip())

			if dom.documentElement.nodeName != "FPM":
				raise base.FormatError

			minversion = dom.documentElement.attributes["min_version"].nodeValue

			if int(minversion.split(".")[1]) > 58:
				raise base.VersionError


		except ExpatError:
			raise base.FormatError

		except ( KeyError, IndexError ):
			raise base.FormatError


	def detect(self, input):
		"Checks if this handler can handle the given data"

		try:
			self.check(input)
			return True

		except ( base.FormatError, base.VersionError, base.DataError ):
			return False


	def export_data(self, entrystore, password):
		"Exports data from an entrystore"

		# set up encryption engine
		salt = "".join( [ random.choice(string.ascii_lowercase) for i in range(8) ] )
		password = MD5.new(salt + password).digest()

		cipher = Blowfish.new(password)


		# generate data
		xml = "<?xml version=\"1.0\" ?>\n"
		xml += "<FPM full_version=\"00.58.00\" min_version=\"00.58.00\" display_version=\"00.58.00\">\n"
		xml += "	<KeyInfo salt=\"%s\" vstring=\"%s\" />\n" % ( salt, self.__encrypt(cipher, "FIGARO") )
		xml += "	<LauncherList></LauncherList>\n"
		xml += "	<PasswordList>\n"

		iter = entrystore.iter_children(None)

		while iter is not None:
			e = entrystore.get_entry(iter)

			if type(e) != entry.FolderEntry:
				e = entry.convert_entry_generic(e)

				xml += "		<PasswordItem>\n"
				xml += "			<title>%s</title>\n" % e.name
				xml += "			<url>%s</url>\n" % e.get_field(entry.HostnameField).value
				xml += "			<user>%s</user>\n" % e.get_field(entry.UsernameField).value
				xml += "			<password>%s</password>\n" % e.get_field(entry.PasswordField).value
				xml += "			<notes>%s</notes>\n" % e.description

				path = entrystore.get_path(iter)

				if len(path) > 1:
					xml += "			<category>%s</category>\n" % entrystore.get_entry(entrystore.get_iter(path[0])).name

				else:
					xml += "			<category></category>\n"

				xml += "			<launcher></launcher>\n"
				xml += "		</PasswordItem>\n"

			iter = entrystore.iter_traverse_next(iter)


		xml += "	</PasswordList>\n"
		xml += "</FPM>\n"


		return xml


	def import_data(self, input, password):
		"Imports data into an entrystore"

		try:

			# check and load data
			self.check(input)
			dom = xml.dom.minidom.parseString(input.strip())

			if dom.documentElement.nodeName != "FPM":
				raise base.FormatError


			# set up decryption engine, and check if password is correct
			keynode = dom.documentElement.getElementsByTagName("KeyInfo")[0]
			salt = keynode.attributes["salt"].nodeValue
			vstring = keynode.attributes["vstring"].nodeValue

			password = MD5.new(salt + password).digest()
			cipher = Blowfish.new(password)

			if self.__decrypt(cipher, vstring) != "FIGARO":
				raise base.PasswordError

		except ExpatError:
			raise base.FormatError


		except ( IndexError, KeyError ):
			raise base.FormatError


		# import entries into entrystore
		entrystore = data.EntryStore()
		folders = {}

		for node in dom.getElementsByTagName("PasswordItem"):

			parent = None
			e = entry.GenericEntry()

			for fieldnode in [ node for node in node.childNodes if node.nodeType == node.ELEMENT_NODE ]:

				content = self.__decrypt(cipher, util.dom_text(fieldnode))

				if content == "":
					continue

				elif fieldnode.nodeName == "title":
					e.name = content

				elif fieldnode.nodeName == "user":
					e.get_field(entry.UsernameField).value = content

				elif fieldnode.nodeName == "url":
					e.get_field(entry.HostnameField).value = content

				elif fieldnode.nodeName == "password":
					e.get_field(entry.PasswordField).value = content
	
				elif fieldnode.nodeName == "notes":
					e.description = content

				elif fieldnode.nodeName == "category":

					if folders.has_key(content):
						parent = folders[content]

					else:
						folderentry = entry.FolderEntry()
						folderentry.name = content

						parent = entrystore.add_entry(folderentry)
						folders[content] = parent

			entrystore.add_entry(e, parent)

		return entrystore



