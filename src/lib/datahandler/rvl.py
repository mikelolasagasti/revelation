#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling Revelation data
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
import re, gtk

from Crypto.Cipher import AES


class RevelationXML(base.DataHandler):
	"Handler for the Revelation XML data"

	name		= "XML (eXtensible Markup Language)"
	importer	= gtk.TRUE
	exporter	= gtk.TRUE
	encryption	= gtk.FALSE


	def __xml_import_node(self, entrystore, node, parent = None):
		"Recursively converts XML nodes to entries, and adds them"

		# check if the XML node is valid
		if node.type == "text":
			return

		if node.type != "element" or node.name != "entry":
			raise base.FormatError

		# create a new entry for the XML node
		entry = revelation.entry.Entry(self.xml_import_attrs(node)["type"])

		# add the empty entry, iter needed as parent for any children
		iter = entrystore.add_entry(parent, entry)

		child = node.children
		while child is not None:

			if child.type != "element":
				child = child.next
				continue


			if child.name == "name":
				entry.name = child.content

			elif child.name == "description":
				entry.description = child.content

			elif child.name == "updated":
				entry.updated = int(child.content)

			elif child.name == "field":
				entry.set_field(self.xml_import_attrs(child)["id"], child.content)

			elif child.name == "entry":
				self.__xml_import_node(entrystore, child, iter)

			else:
				raise base.FormatError

			child = child.next

		# update entry with actual data
		entrystore.update_entry(iter, entry)


	def check_data(self, data):
		"Checks if the data is valid"

		match = re.search("^\s*<\?xml.*\?>\s*<revelationdata.+dataversion=\"(\S+)\"", data)

		if match is None:
			raise base.FormatError

		if int(match.group(1)) > revelation.DATAVERSION:
			raise base.VersionError


	def detect_type(self, data):
		"Checks if this handler can handle the data format"

		try:
			self.check_data(data)

		except base.FormatError, base.VersionError:
			return gtk.FALSE

		else:
			return gtk.TRUE


	def export_data(self, entrystore, parent = None, level = 0):
		"Serializes data from the entrystore into an XML stream"

		xml = ""
		tabs = "\t" * (level + 1)

		# process each child
		for i in range(entrystore.iter_n_children(parent)):

			iter = entrystore.iter_nth_child(parent, i)
			entry = entrystore.get_entry(iter)

			xml += "\n"
			xml += tabs + "<entry type=\"" + entry.type + "\">\n"
			xml += tabs + "	<name>" + revelation.misc.escape_markup(entry.name) + "</name>\n"
			xml += tabs + "	<description>" + revelation.misc.escape_markup(entry.description) + "</description>\n"
			xml += tabs + "	<updated>" + str(entry.updated) + "</updated>\n"

			for field in entry.get_fields():
				xml += tabs + "	<field id=\"" + field.id + "\">" + revelation.misc.escape_markup(field.value) + "</field>\n"

			# handle any children
			xml += RevelationXML.export_data(self, entrystore, iter, level + 1)

			xml += tabs + "</entry>\n"

		# generate header and footer if at level 0
		if level == 0:
			header = "<?xml version=\"1.0\" ?>\n"
			header += "<revelationdata version=\"" + revelation.VERSION + "\" dataversion=\"" + str(revelation.DATAVERSION) + "\">\n"
			footer = "</revelationdata>\n"
			xml = header + xml + footer

		return xml


	def import_data(self, data):
		"Imports data from a stream into an entrystore"

		doc = self.xml_import_init(data)

		# fetch and validate root
		root = doc.children
		if root.name != "revelationdata":
			raise base.FormatError

		attrs = self.xml_import_attrs(root)
		if attrs.has_key("dataversion") and int(attrs["dataversion"]) > revelation.DATAVERSION:
			raise base.VersionError

		# process entries
		entrystore = revelation.data.EntryStore()

		child = root.children
		while child is not None:
			self.__xml_import_node(entrystore, child)
			child = child.next

		return entrystore



class Revelation(RevelationXML):
	"Datahandler for normal Revelation data files, uses RevelationXML to handle the XML"

	name		= "Revelation"
	importer	= gtk.TRUE
	exporter	= gtk.TRUE
	encryption	= gtk.TRUE


	def __init__(self):
		RevelationXML.__init__(self)

		self.blocksize = 16
		self.keysize = 32


	def __decrypt(self, data, password, iv = None):
		"Decrypts data"

		self.cipher_init(AES, password, iv, self.blocksize, self.keysize)
		return self.cipher_decrypt(data)


	def __encrypt(self, data, password, iv = None):
		"Encrypts data"

		self.cipher_init(AES, password, iv, self.blocksize, self.keysize)
		return self.cipher_encrypt(data)


	def __generate_header(self):
		"Generates a data header"

		header = "rvl\x00" + chr(revelation.DATAVERSION) + "\x00"

		for part in revelation.VERSION.split("."):
			header += chr(int(part))

		header += "\x00\x00\x00"

		return header


	def __parse_header(self, header):
		"Parses a data header"

		if len(header) != 12 or header[0:3] != "rvl":
			raise base.FormatError

		dataversion = ord(header[4])
		appversion = str(ord(header[6])) + "." + str(ord(header[7])) + "." + str(ord(header[8]))

		return dataversion, appversion


	def check_data(self, data):
		"Checks if the passed data is valid"

		try:
			dataversion, version = self.__parse_header(data[0:12])

			if dataversion > revelation.DATAVERSION:
				raise base.VersionError

		# ignore version 0 data files (deprecated, remove in future version)
		except base.FormatError:
			return


	def detect_type(self, data):
		"Checks if the handler can handle the data type"

		try:
			self.__parse_header(data[:12])

		except base.FormatError:
			return gtk.FALSE

		else:
			return gtk.TRUE


	def export_data(self, entrystore, password):
		"Serializes the entrystore into a data stream"

		# first, generate XML data from the entrystore
		data = RevelationXML.export_data(self, entrystore)

		# next, compress the data and right-pad it, using
		# the repeated ascii value of the pad length
		data = self.compress_zlib(data)

		padlen = 16 - (len(data) % 16)
		if padlen == 0:
			padlen = 16

		data += (chr(padlen) * padlen)

		# generate an initial vector for CBC encryption mode
		iv = self.string_random(16)

		# encrypt the data
		data = self.__encrypt(data, password, iv)

		# encrypt the iv, and prepend it to the data along with a header
		data = self.__generate_header() + self.__encrypt(iv, password) + data

		return data


	def import_data(self, data, password):
		"Imports data from a data stream into an entrystore"

		# get the version numbers from the header
		try:
			dataversion, appversion = self.__parse_header(data[0:12])

		# if no valid header was found, assume version 0 (0.1.x series).
		# this is deprecated, and support will be removed in a future version
		except base.FormatError:

			data = self.__decrypt(data, password)

			# if not xml file, assume wrong password (could be invalid file
			# as well, but in most cases it will be a wrong password)
			if data[0:5] != "<?xml":
				raise base.PasswordError

			entrystore = RevelationXML.import_data(self, data)
			return entrystore


		# handle version 1 data file
		if dataversion == 1:

			# fetch and decrypt the initial vector for CBC mode decryption
			iv = self.__decrypt(data[12:28], password)

			# decrypt the data
			data = self.__decrypt(data[28:], password, iv)

			# get and check the pad length
			padlen = ord(data[-1])
			for i in data[-padlen:]:
				if ord(i) != padlen:
					raise base.PasswordError

			# decompress data
			data = self.decompress_zlib(data[0:-padlen])

			if data[0:5] != "<?xml":
				raise base.PasswordError

			# import xml into entrystore
			entrystore = RevelationXML.import_data(self, data)


		# future file version, raise exception
		else:
			raise base.VersionError


		return entrystore

