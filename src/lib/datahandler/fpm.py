#
# Revelation 0.3.0 - a password manager for GNOME 2
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
import random, math, re, time

from Crypto.Cipher import Blowfish
from Crypto.Hash import MD5


class FPM(base.Handler):

	def __init__(self):
		base.Handler.__init__(self)
		self.blocksize = 8
		self.keysize = 0
		self.password = None


	def __decrypt_field(self, data):
		data = self.__hex_to_bin(data)
		data = self.cipher_decrypt(data)
		data = self.__unrotate_field(data)
		return data


	def __encrypt_field(self, data):
		blocks = (len(data) / (self.blocksize - 1)) + 1
		size = self.blocksize * blocks

		# add noise
		data = data + "\x00"
		data = data + self.__generate_noise(size - len(data))

		# rotate and encrypt field
		data = self.__rotate_field(data)
		data = self.cipher_encrypt(data)

		# ascii-armor data
		data = self.__bin_to_hex(data)

		return data


	def __generate_noise(self, bytes):
		noise = ""
		for i in range(bytes):
			noise = noise + chr(int(random.random() * 255))

		return noise


	def __generate_salt(self):
		salt = ""
		for i in range(4):
			salt = salt + chr(int(random.random() * 255))

		salt = self.__bin_to_hex(salt)
		return salt


	def __bin_to_hex(self, data):
		hex = ""
		for i in range(len(data)):
			high = ord(data[i]) / 16
			low = ord(data[i]) - high * 16
			hex = hex + chr(ord('a') + high) + chr(ord('a') + low)

		return hex


	def __hex_to_bin(self, data):
		bin = ""
		for i in range(len(data) / 2):
			high = ord(data[2*i]) - ord("a")
			low = ord(data[2*i+1]) - ord("a")
			bin = bin + chr(high*16+low)

		return bin


	def __rotate_field(self, data):
		blocks = int(math.ceil(len(data) / float(self.blocksize)))

		scrambled = ""
		for block in range(blocks):
			for offset in range(self.blocksize):
				scrambled = scrambled + data[offset * blocks + block]

		return scrambled


	def __unrotate_field(self, data):
		blocks = int(math.ceil(len(data) / float(self.blocksize)))
		plain = ""

		try:
			for offset in range(self.blocksize):
				for block in range(blocks):
					char = data[block * self.blocksize + offset]
					
					if char == "\x00":
						raise "done"

					plain = plain + char

		except "done":
			pass


		return plain


	def __xml_export_convert_data(self, entry):

		user = password = url = ""

		# do special conversions
		if entry.type == revelation.entry.ENTRY_ACCOUNT_CREDITCARD:
			user		= entry.get_field(revelation.entry.FIELD_CREDITCARD_CARDNUMBER).value
			password	= entry.get_field(revelation.entry.FIELD_GENERIC_PIN).value

		elif entry.type == revelation.entry.ENTRY_ACCOUNT_CRYPTOKEY:
			user		= entry.get_field(revelation.entry.FIELD_GENERIC_KEYFILE).value

		elif entry.type == revelation.entry.ENTRY_ACCOUNT_DATABASE:
			url		= entry.get_field(revelation.entry.FIELD_GENERIC_DATABASE).value + "@" + entry.get_field(revelation.entry.FIELD_GENERIC_HOSTNAME).value

		elif entry.type == revelation.entry.ENTRY_ACCOUNT_DOOR:
			password	= entry.get_field(revelation.entry.FIELD_GENERIC_CODE).value
			url		= entry.get_field(revelation.entry.FIELD_GENERIC_LOCATION).value

		elif entry.type == revelation.entry.ENTRY_ACCOUNT_FTP:
			url		= "ftp://" + entry.get_field(revelation.entry.FIELD_GENERIC_HOSTNAME).value

			if entry.get_field(revelation.entry.FIELD_GENERIC_PORT).value != "":
				url	+= ":" + entry.get_field(revelation.entry.FIELD_GENERIC_PORT).value

		elif entry.type == revelation.entry.ENTRY_ACCOUNT_PHONE:
			user		= entry.get_field(revelation.entry.FIELD_PHONE_PHONENUMBER).value
			password	= entry.get_field(revelation.entry.FIELD_GENERIC_PIN).value

		elif entry.type == revelation.entry.ENTRY_ACCOUNT_WEBSITE:
			url		= entry.get_field(revelation.entry.FIELD_GENERIC_URL).value


		# do a normal entry conversion to generic, and apply special conversions
		entry.set_type(revelation.entry.ENTRY_ACCOUNT_GENERIC)

		fpmdata = {
			"title"		: entry.name,
			"url"		: entry.get_field(revelation.entry.FIELD_GENERIC_HOSTNAME).value,
			"user"		: entry.get_field(revelation.entry.FIELD_GENERIC_USERNAME).value,
			"password"	: entry.get_field(revelation.entry.FIELD_GENERIC_PASSWORD).value,
			"notes"		: entry.description,
			"category"	: "",
			"launcher"	: ""
		}

		print fpmdata

		if url != "":
			fpmdata["url"] = url

		if user != "":
			fpmdata["user"] = user

		if password != "":
			fpmdata["password"] = password

		return fpmdata


	def __xml_export_entries(self, entrystore, parent = None):
		xml = ""

		for i in range(entrystore.iter_n_children(parent)):
			child = entrystore.iter_nth_child(parent, i)
			entry = entrystore.get_entry(child)

			if entry.type == revelation.entry.ENTRY_FOLDER:
				xml += self.__xml_export_entries(entrystore, child)

			else:

				# convert data to fpm structure
				fpmdata = self.__xml_export_convert_data(entry)

				path = entrystore.get_path(child)
				if len(path) > 1:
					fpmdata["category"] = entrystore.get_entry(entrystore.get_iter(path[0])).name

				xml = xml + "<PasswordItem>"
				xml = xml + "<title>" + self.__encrypt_field(fpmdata["title"]) + "</title>"
				xml = xml + "<user>" + self.__encrypt_field(fpmdata["user"]) + "</user>"
				xml = xml + "<url>" + self.__encrypt_field(fpmdata["url"]) + "</url>"
				xml = xml + "<password>" + self.__encrypt_field(fpmdata["password"]) + "</password>"
				xml = xml + "<notes>" + self.__encrypt_field(fpmdata["notes"]) + "</notes>"
				xml = xml + "<category>" + self.__encrypt_field(fpmdata["category"]) + "</category>"
				xml = xml + "<launcher>" + self.__encrypt_field(fpmdata["launcher"]) + "</launcher>"
				xml = xml + "</PasswordItem>"

		return xml


	def __xml_import_entry(self, node, entrystore, foldercache):
		if node.type != "element" or node.name != "PasswordItem":
			return

		parent = None
		entry = revelation.entry.Entry(revelation.entry.ENTRY_ACCOUNT_GENERIC)

		childnode = node.children
		while childnode is not None:
			if childnode.type == "element":
				content = self.__decrypt_field(childnode.content)

				if childnode.name == "title":
					entry.name = content

				elif childnode.name == "user":
					entry.set_field(revelation.entry.FIELD_GENERIC_USERNAME, content)

				elif childnode.name == "url":
					entry.set_field(revelation.entry.FIELD_GENERIC_HOSTNAME, content)

				elif childnode.name == "password":
					entry.set_field(revelation.entry.FIELD_GENERIC_PASSWORD, content)

				elif childnode.name == "notes":
					entry.description = content

				elif childnode.name == "category":
					foldername = content.strip()

					if foldername == "":
						pass

					elif foldercache.has_key(foldername):
						parent = foldercache[foldername]

					else:
						folderentry = revelation.entry.Entry(revelation.entry.ENTRY_FOLDER)
						folderentry.name = foldername
						folderentry.updated = time.time()
						parent = entrystore.add_entry(None, folderentry)
						foldercache[foldername] = parent

			childnode = childnode.next

		entrystore.add_entry(parent, entry)


	def __xml_import_keyinfo(self, root):
		keynode = self.xml_import_scan(root, "KeyInfo")
		if keynode == None:
			raise base.FormatError

		attrs = self.xml_import_attrs(keynode)
		if not attrs.has_key("salt") or not attrs.has_key("vstring"):
			raise base.FormatError

		info = {
			"salt"		: attrs["salt"],
			"vstring"	: attrs["vstring"]
		}

		return info


	def check_data(self, data):
		if re.search("^<\?xml.*\?>\s*<FPM\s+", data, re.IGNORECASE) == None:
			raise base.FormatError


	def detect_type(self, header):
		try:
			self.check_data(header)
		except base.FormatError:
			return 0
		else:
			return 1


	def export_data(self, entrystore):
		salt = self.__generate_salt()
		self.cipher_init(Blowfish, MD5.new(salt + self.password).digest())

		data = "<?xml version=\"1.0\"?>\n"
		data = data + "<FPM full_version=\"00.58.00\" min_version=\"00.58.00\" display_version=\"0.58\">"
		data = data + "<KeyInfo salt=\"" + salt + "\" vstring=\"" + self.__encrypt_field("FIGARO") + "\"/>"
		data = data + "<LauncherList><LauncherItem></LauncherItem></LauncherList>"
		data = data + "<PasswordList>"
		data = data + self.__xml_export_entries(entrystore)
		data = data + "</PasswordList>"
		data = data + "</FPM>"

		return data


	def import_data(self, entrystore, data):
		doc = self.xml_import_init(data)

		# fetch root node, and check validity
		root = doc.children
		if root.name != "FPM":
			raise base.FormatError

		# set up cipher and check if password is correct
		keyinfo = self.__xml_import_keyinfo(root)
		self.cipher_init(Blowfish, MD5.new(keyinfo["salt"] + self.password).digest())

		if self.__decrypt_field(keyinfo["vstring"]) != "FIGARO":
			raise base.PasswordError

		# import entries into entrystore
		pwlist = self.xml_import_scan(root, "PasswordList")
		if pwlist == None:
			raise base.FormatError

		foldercache = {}
		node = pwlist.children
		while node is not None:
			self.__xml_import_entry(node, entrystore, foldercache)
			node = node.next

