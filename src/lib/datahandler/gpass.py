#
# Revelation 0.3.0 - a password manager for GNOME 2
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
from Crypto.Hash import SHA, MD5


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


	def import_data(self, data, password):
		"Imports data from a data stream into an entrystore"

		iv = chr(5) + chr(23) + chr(1) + chr(123) + chr(12) + chr(3) + chr(54) + chr(94)
		password = SHA.new(password).digest()

		self.cipher_init(Blowfish, password, iv, 16, 20)
		plain = self.cipher_decrypt(data)

		if plain[0:23] != "GNOME Password Manager\n":
			raise base.PasswordError

		# import entries into entrystore
		entrystore = revelation.data.EntryStore()
		lines = plain[23:].splitlines()

		for index, line in zip(range(len(lines)), lines):
			print index % 9, line

