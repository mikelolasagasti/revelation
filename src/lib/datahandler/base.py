#
# Revelation 0.3.1 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for basic datahandler functionality
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

import gobject, gtk, libxml2, random, zlib


class FormatError(Exception):
	"Exception for invalid file formats"
	pass

class PasswordError(Exception):
	"Exception for wrong password"
	pass

class VersionError(Exception):
	"Exception for unknown versions"
	pass



class DataHandler(gobject.GObject):
	"A datahandler base class, real datahandlers are subclassed from this"

	name		= None
	importer	= gtk.FALSE
	exporter	= gtk.FALSE
	encryption	= gtk.FALSE


	def __init__(self):
		gobject.GObject.__init__(self)

		self.cipher	= None


	def compress_zlib(self, data):
		"Compresses data using zlib"

		return zlib.compress(data, 6)


	def check_data(self, data):
		"Dummy check_data() method, subclasses should override this"

		pass


	def cipher_decrypt(self, data):
		"Decrypts data with the current cipher"

		if self.cipher is None:
			return

		if len(data) % self.cipher.block_size != 0:
			raise FormatError

		return self.cipher.decrypt(data)


	def cipher_encrypt(self, data):
		"Encrypts data with the current cipher"

		if self.cipher is None:
			return

		if len(data) % self.cipher.block_size != 0:
			raise FormatError

		return self.cipher.encrypt(data)


	def cipher_init(self, engine, password, iv = None, blocksize = None, keysize = None, keypad = chr(0)):
		"Initializes a cipher"

		if blocksize is not None:
			engine.block_size = blocksize

		if keysize is not None:
			engine.key_size = keysize

			if len(password) > keysize:
				password = password[:keysize]

			# right-pad the key
			padlen = keysize - (len(password) % keysize)
			if padlen == keysize:
				padlen = 0

			password = password + (keypad * padlen)


		if iv is None:
			self.cipher = engine.new(password)

		else:
			self.cipher = engine.new(password, engine.MODE_CBC, iv)


	def decompress_zlib(self, data):
		"Decompresses zlib data"

		return zlib.decompress(data, 15, 32768)


	def detect_type(self, data):
		"Dummy detect_type() method, subclasses should override this"

		return gtk.FALSE


	def export_data(self, entrystore):
		"Dummy export_data() method, subclasses should override this"

		return ""


	def import_data(self, data, entrystore):
		"Dummy import_data() method, subclasses should override this"

		pass


	def string_random(self, length):
		"Generates a random string"

		s = ""
		for i in range(length):
			s += chr(int(random.random() * 255))

		return s


	def xml_import_attrs(self, node):
		"Returns a dictionary with attributes of an XML node"

		attrs = {}
		attr = node.properties

		while attr is not None:
			attrs[attr.name] = attr.content
			attr = attr.next

		return attrs


	def xml_import_init(self, xml):
		"Initializes an XML importer"

		try:
			doc = libxml2.parseDoc(xml)

		except (libxml2.parserError, TypeError):
			raise FormatError

		return doc


	def xml_import_scan(self, node, childname):
		"Scans an XML node for a named child"

		child = node.children
		while child is not None and child.name != childname:
			child = child.next

		if child is not None and child.name == childname:
			return child

		else:
			return None

