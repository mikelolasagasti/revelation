#
# Revelation 0.3.2 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling GNOME Password Manager data
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
import gtk

from Crypto.Cipher import Blowfish
from Crypto.Hash import SHA


INDEX_NAME	= 0
INDEX_USERNAME	= 1
INDEX_PASSWORD	= 2
INDEX_URL	= 3
INDEX_CREATED	= 4
INDEX_UPDATED	= 5
INDEX_EXPIRE	= 6
INDEX_DESCLEN	= 7
INDEX_DESC	= 8


class GPass(base.DataHandler):
	"Data handler for GNOME Password Manager data"

	name		= "GNOME Password Manager (gpass)"
	importer	= gtk.TRUE
	exporter	= gtk.TRUE
	encryption	= gtk.TRUE

	def __init__(self):
		base.DataHandler.__init__(self)


	def __parse(self, data):
		"Parses the data, returns an entrystore"

		entrystore = revelation.data.EntryStore()

		index = 0
		for line in data.splitlines():

			id = index % 9

			# new entry
			if id == 0:
				entry = revelation.entry.GenericEntry()
				desclen = None


			# handle normal fields
			if id == INDEX_NAME:
				entry.name = line

			elif id == INDEX_USERNAME:
				entry.set_field(revelation.entry.FIELD_GENERIC_USERNAME, line)

			elif id == INDEX_PASSWORD:
				entry.set_field(revelation.entry.FIELD_GENERIC_PASSWORD, line)

			elif id == INDEX_URL:
				entry.set_field(revelation.entry.FIELD_GENERIC_HOSTNAME, line)

			elif id == INDEX_CREATED:
				pass

			elif id == INDEX_UPDATED:
				entry.updated = int(line)

			elif id == INDEX_EXPIRE:
				pass

			elif id == INDEX_DESCLEN:
				desclen = int(line)

			elif id == INDEX_DESC:

				if desclen is None:
					raise base.FormatError

				entry.description += line + " "

				# add entry if complete
				if len(entry.description) >= desclen:
					entry.description = entry.description.strip()
					entrystore.add_entry(None, entry)

				# otherwise don't increment index, since next line
				# will be description too
				else:
					continue

			index += 1


		return entrystore


	def __serialize(self, entrystore):
		"Serializes an entrystore into a data stream"

		data = ""
		iter = entrystore.iter_nth_child(None, 0)

		while iter is not None:
			entry = entrystore.get_entry(iter)

			# skip folders
			if type(entry) != revelation.entry.FolderEntry:
				entry.convert_generic()

				data += entry.name + "\n"
				data += entry.get_field(revelation.entry.FIELD_GENERIC_USERNAME).value + "\n"
				data += entry.get_field(revelation.entry.FIELD_GENERIC_PASSWORD).value + "\n"
				data += entry.get_field(revelation.entry.FIELD_GENERIC_HOSTNAME).value + "\n"
				data += str(entry.updated) + "\n"
				data += str(entry.updated) + "\n"
				data += "0\n"
				data += str(len(entry.description) + 1) + "\n"
				data += entry.description + "\n"

			iter = entrystore.iter_traverse_next(iter)

		return data


	def export_data(self, entrystore, password):
		"Exports data to a data stream"

		# serialize data
		data = self.__serialize(entrystore)


		# prepend magic string
		data = "GNOME Password Manager\n" + data


		# pad the data
		padlen = 8 - (len(data) % 8)
		if padlen == 0:
			padlen = 8

		data += chr(padlen) * padlen


		# encrypt the data
		self.cipher_init(
			Blowfish, SHA.new(password).digest(),
			"\x05\x17\x01\x7b\x0c\x03\x36\x5e", 8
		)

		return self.cipher_encrypt(data)


	def import_data(self, data, password):
		"Imports data from a data stream into an entrystore"

		# decrypt data
		self.cipher_init(
			Blowfish, SHA.new(password).digest(),
			"\x05\x17\x01\x7b\x0c\x03\x36\x5e", 8
		)

		plain = self.cipher_decrypt(data)


		# check for magic string
		if plain[0:23] != "GNOME Password Manager\n":
			raise base.PasswordError

		plain = plain[23:]


		# check and remove padding
		padchar = plain[-1]

		if plain[-ord(padchar):] != padchar * ord(padchar):
			raise base.FormatError

		plain = plain[:-ord(padchar)]


		# deserialize data
		return self.__parse(plain)

