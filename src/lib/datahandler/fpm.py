#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling Figaro's Password Manager data
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

import revelation, base
import gtk, math, re, time

from Crypto.Cipher import Blowfish
from Crypto.Hash import MD5


class FPM(base.DataHandler):
	"Data handler for Figaro's Password Manager data"

	name		= "Figaro's Password Manager"
	importer	= gtk.TRUE
	exporter	= gtk.TRUE
	encryption	= gtk.TRUE

	def __init__(self):
		base.DataHandler.__init__(self)

		self.blocksize = 8
		self.keysize = 0


	def __convert_entry(self, entry):
		"Converts an entry into an FPM entry dict"

		entry = revelation.entry.convert_entry_generic(entry)

		fpmdata = {
			"title"		: entry.name,
			"url"		: entry.get_field(revelation.entry.HostnameField).value,
			"user"		: entry.get_field(revelation.entry.UsernameField).value,
			"password"	: entry.get_field(revelation.entry.PasswordField).value,
			"notes"		: entry.description,
			"category"	: "",
			"launcher"	: ""
		}

		return fpmdata


	def __decode(self, data):
		"Decodes data"

		res = ""

		for i in range(len(data) / 2):
			high = ord(data[2 * i]) - ord("a")
			low = ord(data[2 * i + 1]) - ord("a")
			res += chr(high * 16 + low)

		return res


	def __decrypt_field(self, data):
		"Decrypts an entry field"

		data = self.__decode(data)
		data = self.cipher_decrypt(data)
		data = self.__unrotate_field(data)

		return data


	def __encode(self, data):
		"Encodes data with some weird algorithm"

		res = ""

		for i in range(len(data)):
			high = ord(data[i]) / 16
			low = ord(data[i]) - high * 16
			res += chr(ord('a') + high) + chr(ord('a') + low)

		return res


	def __encrypt_field(self, data):
		"Encrypts an entry field"

		# get data sizes
		blocks = (len(data) / (self.blocksize - 1)) + 1
		size = self.blocksize * blocks

		# add noise
		data += "\x00" + self.string_random(size - len(data) - 1)

		# rotate and encrypt field
		data = self.__rotate_field(data)
		data = self.cipher_encrypt(data)

		# ascii-armor data
		data = self.__encode(data)

		return data


	def __rotate_field(self, data):
		"Rotates field data"

		blocks = int(math.ceil(len(data) / float(self.blocksize)))

		scrambled = ""
		for block in range(blocks):
			for offset in range(self.blocksize):
				scrambled += data[offset * blocks + block]

		return scrambled


	def __unrotate_field(self, data):
		"Unrotates field data"

		blocks = int(math.ceil(len(data) / float(self.blocksize)))
		plain = ""

		try:
			for offset in range(self.blocksize):
				for block in range(blocks):
					char = data[block * self.blocksize + offset]
					
					if char == "\x00":
						raise "done"

					plain += char

		except "done":
			pass

		return plain


	def __xml_export_entries(self, entrystore, parent = None):
		"Converts entries to FPM XML format"

		xml = ""

		for i in range(entrystore.iter_n_children(parent)):

			iter = entrystore.iter_nth_child(parent, i)
			entry = entrystore.get_entry(iter)

			if type(entry) == revelation.entry.FolderEntry:
				xml += self.__xml_export_entries(entrystore, iter)

			else:
				fpmdata = self.__convert_entry(entry)

				# find the topmost folder containing the entry, and use it
				# as category name
				path = entrystore.get_path(iter)
				if len(path) > 1:
					fpmdata["category"] = entrystore.get_entry(entrystore.get_iter(path[0])).name


				xml += "<PasswordItem>"

				for field in ("title", "user", "url", "password", "notes", "category", "launcher"):
					xml += "<" + field + ">" + self.__encrypt_field(fpmdata[field]) + "</" + field + ">"

				xml += "</PasswordItem>"

		return xml


	def __xml_import_entries(self, basenode, entrystore):
		"Imports entries from the FPM data to an entrystore"

		folders = {}
		entrynode = basenode.children

		while entrynode is not None:

			if entrynode.type != "element" or entrynode.name != "PasswordItem":
				node = node.next
				continue

			parent = None
			entry = revelation.entry.GenericEntry()
			entry.updated = time.time()

			fieldnode = entrynode.children

			while fieldnode is not None:

				if fieldnode.type != "element":
					fieldnode = fieldnode.next
					continue


				content = self.__decrypt_field(fieldnode.content).strip()

				if fieldnode.name == "title":
					entry.name = content

				elif fieldnode.name == "user":
					entry.get_field(revelation.entry.UsernameField).value = content

				elif fieldnode.name == "url":
					entry.get_field(revelation.entry.HostnameField).value = content

				elif fieldnode.name == "password":
					entry.get_field(revelation.entry.PasswordField).value = content

				elif fieldnode.name == "notes":
					entry.description = content

				elif fieldnode.name == "category":
					foldername = content

					if foldername == "":
						pass

					elif folders.has_key(foldername):
						parent = folders[foldername]

					else:
						folderentry = revelation.entry.FolderEntry()
						folderentry.name = foldername
						folderentry.updated = time.time()

						parent = entrystore.add_entry(None, folderentry)
						folders[foldername] = parent

				fieldnode = fieldnode.next

			entrystore.add_entry(parent, entry)
			entrynode = entrynode.next


	def __xml_get_keyinfo(self, root):
		"Looks up the key info from the XML"

		keynode = self.xml_import_scan(root, "KeyInfo")
		if keynode is None:
			raise base.FormatError

		attrs = self.xml_import_attrs(keynode)
		if not attrs.has_key("salt") or not attrs.has_key("vstring"):
			raise base.FormatError

		return attrs["salt"], attrs["vstring"]


	def check_data(self, data):
		"Checks if the data is valid"

		if re.search("^<\?xml.*\?>\s*<FPM\s+", data) is None:
			raise base.FormatError


	def detect_type(self, header):
		"Checks if data can be handled by this datahandler"

		try:
			self.check_data(header)
			return gtk.TRUE

		except base.FormatError:
			return gtk.FALSE


	def export_data(self, entrystore, password):
		"Exports data from an entrystore into a data stream"

		salt = self.__encode(self.string_random(4))
		password = MD5.new(salt + password).digest()

		self.cipher_init(Blowfish, password)

		data = "<?xml version=\"1.0\"?>\n"
		data +=  "<FPM full_version=\"00.58.00\" min_version=\"00.58.00\" display_version=\"0.58\">"
		data += "<KeyInfo salt=\"" + salt + "\" vstring=\"" + self.__encrypt_field("FIGARO") + "\"/>"
		data += "<LauncherList><LauncherItem></LauncherItem></LauncherList>"
		data += "<PasswordList>"
		data += self.__xml_export_entries(entrystore)
		data += "</PasswordList>"
		data += "</FPM>"

		return data


	def import_data(self, data, password):
		"Imports data from a data stream into an entrystore"

		doc = self.xml_import_init(data)

		# fetch root node, and check validity
		root = doc.children
		if root.name != "FPM":
			raise base.FormatError

		# set up cipher and check if password is correct
		salt, vstring = self.__xml_get_keyinfo(root)
		password = MD5.new(salt + password).digest()

		self.cipher_init(Blowfish, password)

		if self.__decrypt_field(vstring) != "FIGARO":
			raise base.PasswordError

		# import entries into entrystore
		pwlist = self.xml_import_scan(root, "PasswordList")
		if pwlist == None:
			raise base.FormatError

		entrystore = revelation.data.EntryStore()
		self.__xml_import_entries(pwlist, entrystore)

		return entrystore

