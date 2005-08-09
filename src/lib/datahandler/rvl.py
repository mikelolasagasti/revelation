#
# Revelation 0.4.4 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling Revelation data
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
from revelation import config, data, entry, util

import re, xml.dom.minidom, zlib

from xml.parsers.expat import ExpatError
from Crypto.Cipher import AES



class RevelationXML(base.DataHandler):
	"Handler for Revelation XML data"

	name		= "XML"
	importer	= True
	exporter	= True
	encryption	= False


	def __init__(self):
		base.DataHandler.__init__(self)


	def __lookup_entry(self, typename):
		"Looks up an entry type based on an identifier"

		for entrytype in entry.ENTRYLIST:
			if entrytype.id == typename:
				return entrytype

		else:
			raise entry.EntryTypeError


	def __lookup_field(self, fieldname):
		"Looks up an entry field based on an identifier"

		for fieldtype in entry.FIELDLIST:
			if fieldtype.id == fieldname:
				return fieldtype

		else:
			raise entry.EntryFieldError


	def __xml_import_node(self, entrystore, node, parent = None):
		"Imports a node into an entrystore"

		try:

			# check the node
			if node.nodeType == node.TEXT_NODE:
				return

			if node.nodeType != node.ELEMENT_NODE or node.nodeName != "entry":
				raise base.FormatError

			# create an entry, iter needed for children
			e = self.__lookup_entry(node.attributes["type"].value)()
			iter = entrystore.add_entry(e, parent)

			# handle child nodes
			for child in node.childNodes:

				if child.nodeType != child.ELEMENT_NODE:
					continue

				elif child.nodeName == "name":
					e.name = util.dom_text(child)

				elif child.nodeName == "description":
					e.description = util.dom_text(child)

				elif child.nodeName == "updated":
					e.updated = int(util.dom_text(child))

				elif child.nodeName == "field":
					e[self.__lookup_field(child.attributes["id"].nodeValue)] = util.dom_text(child)

				elif child.nodeName == "entry":
					if type(e) != entry.FolderEntry:
						raise base.DataError

					self.__xml_import_node(entrystore, child, iter)

				else:
					raise base.FormatError

			# update entry with actual data
			entrystore.update_entry(iter, e)


		except ( entry.EntryTypeError, entry.EntryFieldError ):
			raise base.DataError

		except KeyError:
			raise base.FormatError

		except ValueError:
			raise base.DataError


	def check(self, input):
		"Checks if the data is valid"

		if input is None:
			raise base.FormatError

		match = re.match("""
			\s*			# whitespace at beginning
			<\?xml(?:.*)\?>		# xml header
			\s*			# whitespace after xml header
			<revelationdata		# open revelationdata tag
			[^>]+			# any non-closing character
			dataversion="(\d+)"	# dataversion
			[^>]*			# any non-closing character
			>			# close revelationdata tag
		""", input, re.VERBOSE)

		if match is None:
			raise base.FormatError

		if int(match.group(1)) != 1:
			raise base.VersionError


	def detect(self, input):
		"Checks if this handler can guarantee to handle some data"

		try:
			self.check(input)
			return True

		except ( base.FormatError, base.VersionError ):
			return False


	def export_data(self, entrystore, password = None, parent = None, level = 0):
		"Serializes data into an XML stream"

		xml = ""
		tabs = "\t" * (level + 1)

		for i in range(entrystore.iter_n_children(parent)):
			iter = entrystore.iter_nth_child(parent, i)
			e = entrystore.get_entry(iter)

			xml += "\n"
			xml += tabs + "<entry type=\"%s\">\n" % e.id
			xml += tabs + "	<name>%s</name>\n" % util.escape_markup(e.name)
			xml += tabs + "	<description>%s</description>\n" % util.escape_markup(e.description)
			xml += tabs + "	<updated>%d</updated>\n" % e.updated

			for field in e.fields:
				xml += tabs + "	<field id=\"%s\">%s</field>\n" % ( field.id, util.escape_markup(field.value) )

			xml += RevelationXML.export_data(self, entrystore, password, iter, level + 1)
			xml += tabs + "</entry>\n"

		if level == 0:
			header = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
			header += "<revelationdata version=\"%s\" dataversion=\"1\">\n" % config.VERSION
			footer = "</revelationdata>\n"

			xml = header + xml + footer

		return xml


	def import_data(self, input, password = None):
		"Imports data from a data stream to an entrystore"

		# Workaround for incorrect encoding in files generated by version 0.4.0.
		# To be removed in version 0.5.0.
		if input[:44] == '<?xml version="1.0" encoding="iso-8859-1" ?>':
			input = '<?xml version="1.0" encoding="utf-8" ?>' + input[44:]

		RevelationXML.check(self, input)

		try:
			dom = xml.dom.minidom.parseString(input.strip())

		except ExpatError:
			raise base.FormatError


		if dom.documentElement.nodeName != "revelationdata":
			raise base.FormatError

		if not dom.documentElement.attributes.has_key("dataversion"):
			raise base.FormatError


		entrystore = data.EntryStore()

		for node in dom.documentElement.childNodes:
			self.__xml_import_node(entrystore, node)

		return entrystore



class Revelation(RevelationXML):
	"Handler for Revelation data"

	name		= "Revelation"
	importer	= True
	exporter	= True
	encryption	= True


	def __init__(self):
		RevelationXML.__init__(self)


	def __generate_header(self):
		"Generates a header"

		header = "rvl\x00"		# magic string
		header += "\x01"		# data version
		header += "\x00"		# separator
		header += "\x00\x04\x05"	# application version TODO
		header += "\x00\x00\x00"	# separator

		return header


	def __parse_header(self, header):
		"Parses a data header, returns the data version"

		if header is None:
			raise base.FormatError

		match = re.match("""
			^			# start of header
			rvl\x00			# magic string
			(.)			# data version
			\x00			# separator
			(.{3})			# app version
			\x00\x00\x00		# separator
		""", header, re.VERBOSE)

		if match is None:
			raise base.FormatError

		return ord(match.group(1))


	def check(self, input):
		"Checks if the data is valid"

		if input is None:
			raise base.FormatError

		if len(input) < (12 + 16):
			raise base.FormatError

		dataversion = self.__parse_header(input[:12])

		if dataversion != 1:
			raise base.VersionError


	def detect(self, input):
		"Checks if the handler can guarantee to use the data"

		try:
			self.check(input)
			return True

		except ( base.FormatError, base.VersionError ):
			return False


	def export_data(self, entrystore, password):
		"Exports data from an entrystore"

		# check and pad password
		if password is None:
			raise base.PasswordError

		password = util.pad_right(password[:32], 32, "\0")

		# generate XML
		data = RevelationXML.export_data(self, entrystore)

		# compress data, and right-pad with the repeated ascii
		# value of the pad length
		data = zlib.compress(data)

		padlen = 16 - (len(data) % 16)
		if padlen == 0:
			padlen = 16

		data += chr(padlen) * padlen

		# generate an initial vector for the CBC encryption
		iv = util.random_string(16)

		# encrypt data
		AES.block_size = 16
		AES.key_size = 32

		data = AES.new(password, AES.MODE_CBC, iv).encrypt(data)

		# encrypt the iv, and prepend it to the data with a header
		data = self.__generate_header() + AES.new(password).encrypt(iv) + data

		return data


	def import_data(self, input, password):
		"Imports data into an entrystore"

		# check and pad password
		if password is None:
			raise base.PasswordError

		password = util.pad_right(password[:32], 32, "\0")

		# check the data
		self.check(input)
		dataversion = self.__parse_header(input[:12])

		# handle only version 1 data files
		if dataversion != 1:
			raise base.VersionError


		# fetch and decrypt the initial vector for CBC decryption
		AES.block_size = 16
		AES.key_size = 32

		cipher = AES.new(password)
		iv = cipher.decrypt(input[12:28])


		# decrypt the data
		input = input[28:]

		if len(input) % 16 != 0:
			raise base.FormatError

		cipher = AES.new(password, AES.MODE_CBC, iv)
		input = cipher.decrypt(input)


		# decompress data
		padlen = ord(input[-1])
		for i in input[-padlen:]:
			if ord(i) != padlen:
				raise base.PasswordError

		input = zlib.decompress(input[0:-padlen])


		# check and import data
		if input.strip()[:5] != "<?xml":
			raise base.PasswordError

		entrystore = RevelationXML.import_data(self, input)

		return entrystore

