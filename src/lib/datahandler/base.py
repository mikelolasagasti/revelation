#
# Revelation 0.3.0 - a password manager for GNOME 2
# $Id$
# http://oss.codepoet.no/revelation/
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

import gobject, libxml2


class EntryError(Exception):
	"""Base class for entry errors"""
	pass

class FormatError(Exception):
	"""Exception for invalid file formats"""
	pass

class PasswordError(Exception):
	"""Exception for wrong password"""
	pass

class VersionError(Exception):
	"""Exception for unknown versions"""
	pass



class Handler(gobject.GObject):

	def __init__(self):
		gobject.GObject.__init__(self)


	def cipher_decrypt(self, data):
		if len(data) % self.cipher.block_size != 0:
			raise FormatError

		return self.cipher.decrypt(data)


	def cipher_encrypt(self, data):
		if len(data) % self.cipher.block_size != 0:
			raise FormatError

		return self.cipher.encrypt(data)


	def cipher_init(self, engine, password, iv = None, blocksize = None, keysize = None, keypad = chr(0)):
		if blocksize != None:
			engine.block_size = blocksize

		if keysize != None:
			engine.key_size = keysize

			if len(password) > keysize:
				raise PasswordError

			padlen = keysize - (len(password) % keysize)
			if padlen == 32:
				padlen = 0

			password = password + (keypad * padlen)

		if iv == None:
			self.cipher = engine.new(password)
		else:
			self.cipher = engine.new(password, engine.MODE_CBC, iv)


	def xml_import_attrs(self, node):
		attrs = {}

		attr = node.properties
		while attr is not None:
			attrs[attr.name] = attr.content
			attr = attr.next

		return attrs


	def xml_import_init(self, xml):
		try:
			doc = libxml2.parseDoc(xml)
		except (libxml2.parserError, TypeError):
			raise FormatError

		return doc


	def xml_import_scan(self, node, childname):
		child = node.children
		while child is not None and child.name != childname:
			child = child.next

		if child is not None and child.name == childname:
			return child
		else:
			return None

