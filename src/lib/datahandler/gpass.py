#
# Revelation 0.4.0 - a password manager for GNOME 2
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

import base
from revelation import data, entry

from Crypto.Cipher import Blowfish
from Crypto.Hash import SHA


IV	= "\x05\x17\x01\x7b\x0c\x03\x36\x5e"



class GPass(base.DataHandler):
	"Data handler for GNOME Password Manager data"

	name		= "GNOME Password Manager (gpass)"
	importer	= True
	exporter	= True
	encryption	= True


	def __init__(self):
		base.DataHandler.__init__(self)


	def export_data(self, entrystore, password):
		"Exports data to a data stream"

		# set up magic string
		data = "GNOME Password Manager\n"

		# serialize entries
		iter = entrystore.iter_nth_child(None, 0)

		while iter is not None:
			e = entrystore.get_entry(iter)

			# skip folders
			if type(e) != entry.FolderEntry:
				e = entry.convert_entry_generic(e)

				data += e.name + "\n"
				data += e[entry.UsernameField] + "\n"
				data += e[entry.PasswordField] + "\n"
				data += e[entry.HostnameField] + "\n"
				data += str(e.updated) + "\n"
				data += str(e.updated) + "\n"
				data += "0\n"
				data += str(len(e.description) + 1) + "\n"
				data += e.description + "\n"

			iter = entrystore.iter_traverse_next(iter)

		# pad data
		padlen = 8 - (len(data) % 8)
		if padlen == 0:
			padlen = 8

		data += chr(padlen) * padlen

		# encrypt data
		return Blowfish.new(SHA.new(password).digest(), Blowfish.MODE_CBC, IV).encrypt(data)


	def import_data(self, input, password):
		"Imports data from a data stream to an entrystore"

		# decrypt data
		plain = Blowfish.new(SHA.new(password).digest(), Blowfish.MODE_CBC, IV).decrypt(input)

		if plain[0:23] != "GNOME Password Manager\n":
			raise base.PasswordError

		plain = plain[23:]

		# remove padding
		padchar = plain[-1]

		if plain[-ord(padchar):] != padchar * ord(padchar):
			raise base.FormatError

		plain = plain[:-ord(padchar)]

		# deserialize data
		entrystore = data.EntryStore()
		lines = plain.splitlines()

		while len(lines) > 0:

			e = entry.GenericEntry()

			e.name			= lines[0]
			e[entry.UsernameField]	= lines[1]
			e[entry.PasswordField]	= lines[2]
			e[entry.HostnameField]	= lines[3]
			e.updated		= int(lines[5])
			desclen			= int(lines[7])

			del lines[:8]

			while len(e.description) + 1 < desclen and len(lines) > 0:
				e.description += lines[0]
				del lines[0]

			entrystore.add_entry(e)

		return entrystore

