#
# Revelation 0.4.5 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling GNOME Password Manager data
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
from revelation import data, entry

import locale, re
from Crypto.Cipher import Blowfish
from Crypto.Hash import SHA


IV	= "\x05\x17\x01\x7b\x0c\x03\x36\x5e"



class GPass04(base.DataHandler):
	"Data handler for GPass 0.4.x data"

	name		= "GPass 0.4.x (or older)"
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



class GPass05(base.DataHandler):
	"Data handler for GPass 0.5.x data"

	name		= "GPass 0.5.x (or newer)"
	importer	= True
	exporter	= False
	encryption	= True


	def __init__(self):
		base.DataHandler.__init__(self)


	def __getint(self, input):
		"Fetches an integer from the input"

		if len(input) < 4:
			raise base.FormatError

		return ord(input[0]) << 0 | ord(input[1]) << 8 | ord(input[2]) << 16 | ord(input[3]) << 24


	def __getstr(self, input):
		"Fetches a string from the input"

		length = self.__getint(input[:4])

		if len(input) < (4 + length):
			raise base.FormatError

		string = input[4:4 + length]

		if len(string) != length:
			raise base.FormatError

		return string


	def __normstr(self, string):
		"Normalizes a string"

		string = re.sub("[\r\n]+", " ", string)
		string = string.decode(locale.getpreferredencoding(), "replace")
		string = string.encode("utf-8")

		return string


	def __unpackint(self, input):
		"Fetches a packed number from the input"

		value	= 0
		b	= 1

		for i in range(min(len(input), 6)):
			c = ord(input[i])

			if c & 0x80:
				value	+= b * (c & 0x7f)
				b	*= 0x80;

			else:
				value	+= b * c

				return i + 1, value

		# if we didn't return in the for-loop, the input is invalid
		else:
			raise base.FormatError


	def __unpackstr(self, input):
		"Unpacks a string from the input"

		cut, length = self.__unpackint(input[:6])

		if len(input) < cut + length:
			raise base.FormatError

		return cut + length, input[cut:cut + length]


	def import_data(self, input, password):
		"Imports data from a data stream to an entrystore"

		# decrypt data
		plain = Blowfish.new(SHA.new(password).digest(), Blowfish.MODE_CBC, self.IV).decrypt(input)

		if plain[0:23] != "GPassFile version 1.1.0":
			raise base.PasswordError

		plain = plain[23:]

		# remove padding
		padchar = plain[-1]

		if plain[-ord(padchar):] != padchar * ord(padchar):
			raise base.FormatError

		plain = plain[:-ord(padchar)]

		# deserialize data
		entrystore = data.EntryStore()
		foldermap = {}

		while len(plain) > 0:

			# parse data
			id		= self.__getint(plain[:4])
			plain		= plain[4:]

			parentid	= self.__getint(plain[:4])
			plain		= plain[4:]

			entrytype	= self.__getstr(plain)
			plain		= plain[4 + len(entrytype):]

			attrdata	= self.__getstr(plain)
			plain		= plain[4 + len(attrdata):]


			l, name		= self.__unpackstr(attrdata)
			attrdata	= attrdata[l:]

			l, desc		= self.__unpackstr(attrdata)
			attrdata	= attrdata[l:]

			l, ctime	= self.__unpackint(attrdata)
			attrdata	= attrdata[l:]

			l, mtime	= self.__unpackint(attrdata)
			attrdata	= attrdata[l:]

			l, expire	= self.__unpackint(attrdata)
			attrdata	= attrdata[l:]

			l, etime	= self.__unpackint(attrdata)
			attrdata	= attrdata[l:]

			if entrytype == "general":
				l, username	= self.__unpackstr(attrdata)
				attrdata	= attrdata[l:]

				l, password	= self.__unpackstr(attrdata)
				attrdata	= attrdata[l:]

				l, hostname	= self.__unpackstr(attrdata)
				attrdata	= attrdata[l:]

			else:
				username = password = hostname = ""


			# create entry
			if entrytype == "general":
				e = entry.GenericEntry()

				e.name			= self.__normstr(name)
				e.description		= self.__normstr(desc)
				e.updated		= mtime

				e[entry.HostnameField]	= self.__normstr(hostname)
				e[entry.UsernameField]	= self.__normstr(username)
				e[entry.PasswordField]	= self.__normstr(password)

			elif entrytype == "folder":
				e = entry.FolderEntry()

				e.name			= self.__normstr(name)
				e.description		= self.__normstr(desc)
				e.updated		= mtime

			else:
				continue


			# add entry to entrystore
			if foldermap.has_key(parentid):
				parent = foldermap[parentid]

			else:
				parent = None

			iter = entrystore.add_entry(e, parent)

			if type(e) == entry.FolderEntry:
				foldermap[id] = iter


		return entrystore

