#
# Revelation 0.4.5 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling PasswordSafe data
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
from revelation import data, entry, util

import re, struct
from Crypto.Cipher import Blowfish



# We need our own SHA1-implementation, because Password Safe does
# non-standard things we need to replicate. This implementation is
# written by J. Hallen and L. Creighton for the Pypy project, with
# slight modifications by Erik Grinaker.
class SHA:

	K = [
		0x5A827999L,
		0x6ED9EBA1L,
		0x8F1BBCDCL,
		0xCA62C1D6L
	]


	def __init__(self, input = None):
		self.count = [0, 0]
		self.init()

		if input != None:
			self.update(input)


	def __bytelist2longBigEndian(self, list):
		imax = len(list)/4
		hl = [0L] * imax
	
		j = 0
		i = 0
		while i < imax:
			b0 = long(ord(list[j])) << 24
			b1 = long(ord(list[j+1])) << 16
			b2 = long(ord(list[j+2])) << 8
			b3 = long(ord(list[j+3]))
			hl[i] = b0 | b1 | b2 | b3
			i = i+1
			j = j+4
	
		return hl


	def __long2bytesBigEndian(self, n, blocksize=0):
		s = ''
		pack = struct.pack
		while n > 0:
			s = pack('>I', n & 0xffffffffL) + s
			n = n >> 32
	
		for i in range(len(s)):
			if s[i] <> '\000':
				break
		else:
			s = '\000'
			i = 0
	
		s = s[i:]
	
		if blocksize > 0 and len(s) % blocksize:
			s = (blocksize - len(s) % blocksize) * '\000' + s
	
		return s


	def __rotateLeft(self, x, n):
		return (x << n) | (x >> (32-n))


	def __transform(self, W):
		for t in range(16, 80):
			W.append(self.__rotateLeft(
				W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1) & 0xffffffffL)

		A = self.H0
		B = self.H1
		C = self.H2
		D = self.H3
		E = self.H4

		for t in range(0, 20):
			TEMP = self.__rotateLeft(A, 5) + ((B & C) | ((~ B) & D)) + E + W[t] + self.K[0]
			E = D
			D = C
			C = self.__rotateLeft(B, 30) & 0xffffffffL
			B = A
			A = TEMP & 0xffffffffL

		for t in range(20, 40):
			TEMP = self.__rotateLeft(A, 5) + (B ^ C ^ D) + E + W[t] + self.K[1]
			E = D
			D = C
			C = self.__rotateLeft(B, 30) & 0xffffffffL
			B = A
			A = TEMP & 0xffffffffL

		for t in range(40, 60):
			TEMP = self.__rotateLeft(A, 5) + ((B & C) | (B & D) | (C & D)) + E + W[t] + self.K[2]
			E = D
			D = C
			C = self.__rotateLeft(B, 30) & 0xffffffffL
			B = A
			A = TEMP & 0xffffffffL

		for t in range(60, 80):
			TEMP = self.__rotateLeft(A, 5) + (B ^ C ^ D)  + E + W[t] + self.K[3]
			E = D
			D = C
			C = self.__rotateLeft(B, 30) & 0xffffffffL
			B = A
			A = TEMP & 0xffffffffL


		self.H0 = (self.H0 + A) & 0xffffffffL
		self.H1 = (self.H1 + B) & 0xffffffffL
		self.H2 = (self.H2 + C) & 0xffffffffL
		self.H3 = (self.H3 + D) & 0xffffffffL
		self.H4 = (self.H4 + E) & 0xffffffffL


	def digest(self):
		H0 = self.H0
		H1 = self.H1
		H2 = self.H2
		H3 = self.H3
		H4 = self.H4
		input = [] + self.input
		count = [] + self.count

		index = (self.count[1] >> 3) & 0x3fL

		if index < 56:
			padLen = 56 - index
		else:
			padLen = 120 - index

		padding = ['\200'] + ['\000'] * 63
		self.update(padding[:padLen])

		bits = self.__bytelist2longBigEndian(self.input[:56]) + count

		self.__transform(bits)

		digest = self.__long2bytesBigEndian(self.H0, 4) + \
				self.__long2bytesBigEndian(self.H1, 4) + \
				self.__long2bytesBigEndian(self.H2, 4) + \
				self.__long2bytesBigEndian(self.H3, 4) + \
				self.__long2bytesBigEndian(self.H4, 4)

		self.H0 = H0 
		self.H1 = H1 
		self.H2 = H2
		self.H3 = H3
		self.H4 = H4
		self.input = input 
		self.count = count 

		return digest


	def hexdigest(self):
		return ''.join(['%02x' % ord(c) for c in self.digest()])


	def init(self, H0 = 0x67452301L, H1 = 0xEFCDAB89L, H2 = 0x98BADCFEL, H3 = 0x10325476L, H4 = 0xC3D2E1F0L):
		self.length = 0L
		self.input = []

		self.H0 = H0
		self.H1 = H1
		self.H2 = H2
		self.H3 = H3
		self.H4 = H4


	def update(self, inBuf):
		leninBuf = long(len(inBuf))

		index = (self.count[1] >> 3) & 0x3FL

		self.count[1] = self.count[1] + (leninBuf << 3)
		if self.count[1] < (leninBuf << 3):
			self.count[0] = self.count[0] + 1
		self.count[0] = self.count[0] + (leninBuf >> 29)

		partLen = 64 - index

		if leninBuf >= partLen:
			self.input[index:] = list(inBuf[:partLen])
			self.__transform(self.__bytelist2longBigEndian(self.input))
			i = partLen
			while i + 63 < leninBuf:
				self.__transform(self.__bytelist2longBigEndian(list(inBuf[i:i+64])))
				i = i + 64
			else:
				self.input = list(inBuf[i:leninBuf])
		else:
			i = 0
			self.input = self.input + list(inBuf)



class PasswordSafe1(base.DataHandler):
	"Data handler for PasswordSafe 1.x data"

	name		= "Password Safe 1.x"
	importer	= True
	exporter	= True
	encryption	= True


	def __init__(self):
		base.DataHandler.__init__(self)


	def __create_field(self, value):
		"Creates a field"

		field = "".join([ chr(len(value) >> i * 8) for i in range(8) ]) + value

		if len(value) == 0 or len(value) % 8 != 0:
			field += "\x00" * (8 - len(value) % 8)

		return field


	def __decrypt(self, key, ciphertext, iv = None):
		"Decrypts data"

		if len(ciphertext) % 8 != 0:
			raise base.FormatError

		cipher		= Blowfish.new(key)
		cbc		= iv
		plaintext	= ""

		for cipherblock in [ ciphertext[i * 8 : (i + 1) * 8] for i in range(len(ciphertext) / 8) ]:

			plainblock = self.__decrypt_block(cipher, cipherblock)

			if cbc != None:
				plainblock = "".join([ chr(ord(plainblock[i]) ^ ord(cbc[i])) for i in range(len(plainblock)) ])
				cbc = cipherblock

			plaintext += plainblock

		return plaintext


	def __decrypt_block(self, cipher, block):
		"Decrypts a block with the given cipher"

		block = block[3] + block[2] + block[1] + block[0] + block[7] + block[6] + block[5] + block[4]
		block = cipher.decrypt(block)
		block = block[3] + block[2] + block[1] + block[0] + block[7] + block[6] + block[5] + block[4]

		return block


	def __encrypt(self, key, plaintext, iv = None):
		"Encrypts data"

		if len(plaintext) % 8 != 0:
			raise base.FormatError

		cipher		= Blowfish.new(key)
		cbc		= iv
		ciphertext	= ""

		for plainblock in [ plaintext[i * 8 : (i + 1) * 8] for i in range(len(plaintext) / 8) ]:

			if cbc != None:
				plainblock = "".join([ chr(ord(plainblock[i]) ^ ord(cbc[i])) for i in range(len(plainblock)) ])

			cipherblock = self.__encrypt_block(cipher, plainblock)
			ciphertext += cipherblock

			if cbc != None:
				cbc = cipherblock


		return ciphertext


	def __encrypt_block(self, cipher, block):
		"Encrypts a block with the given cipher"

		block = block[3] + block[2] + block[1] + block[0] + block[7] + block[6] + block[5] + block[4]
		block = cipher.encrypt(block)
		block = block[3] + block[2] + block[1] + block[0] + block[7] + block[6] + block[5] + block[4]

		return block


	def __generate_testhash(self, password, random):
		"Generates a testhash based on a password and a random string"

		key	= SHA(random + "\x00\x00" + password).digest()
		cipher	= Blowfish.new(key)

		for i in range(1000):
			random = self.__encrypt_block(cipher, random)

		h = SHA()
		h.init(0L, 0L, 0L, 0L, 0L)
		h.update(random)
		h.update("\x00\x00")
		testhash = h.digest()

		return testhash


	def __get_field(self, input):
		"Reads the next field from a data stream"

		if len(input) < 4:
			raise base.FormatError

		fieldlen = ord(input[0]) << 0 | ord(input[1]) << 8 | ord(input[2]) << 16 | ord(input[3]) << 24

		if fieldlen == 0 or fieldlen % 8 != 0:
			fieldlen += 8 - fieldlen % 8

		return input[8:8 + fieldlen]


	def __normalize_field(self, field):
		"Normalizes a field value"

		field = field.replace("\x00", "")
		field = re.sub("\s+", " ", field)
		field = field.strip()
		field = field.decode("iso-8859-1")
		field = field.encode("utf-8")

		return field


	def check(self, input):
		"Checks if the data is valid"

		if input is None:
			raise base.FormatError

		if len(input) < 56:
			raise base.FormatError

		if (len(input) - 56) % 8 != 0:
			raise base.FormatError


	def export_data(self, entrystore, password):
		"Exports data from an entrystore"

		# serialize data
		db = ""
		iter = entrystore.iter_children(None)

		while iter is not None:
			e = entrystore.get_entry(iter)

			if type(e) != entry.FolderEntry:
				e = entry.convert_entry_generic(e)

				try:
					edata = ""
					edata += self.__create_field(e.name.encode("iso-8859-1") + "\xAD" + e[entry.UsernameField].encode("iso-8859-1"))
					edata += self.__create_field(e[entry.PasswordField].encode("iso-8859-1"))
					edata += self.__create_field(e.description.encode("iso-8859-1"))

					db += edata

				except UnicodeEncodeError:
					pass

			iter = entrystore.iter_traverse_next(iter)


		# encrypt data
		random		= util.random_string(8)
		salt		= util.random_string(20)
		iv		= util.random_string(8)

		testhash	= self.__generate_testhash(password, random)
		ciphertext	= self.__encrypt(SHA(password + salt).digest(), db, iv)

		return random + testhash + salt + iv + ciphertext

	
	def import_data(self, input, password):
		"Imports data into an entrystore"

		# read header and test password
		if password is None:
			raise base.PasswordError

		random		= input[0:8]
		testhash	= input[8:28]
		salt		= input[28:48]
		iv		= input[48:56]

		if testhash != self.__generate_testhash(password, random):
			raise base.PasswordError

		# load data
		db		= self.__decrypt(SHA(password + salt).digest(), input[56:], iv)
		entrystore	= data.EntryStore()

		while len(db) > 0:
			name = self.__get_field(db)
			db = db[8 + len(name):]

			username = ""

			if "\xAD" in name:
				name, username = name.split("\xAD", 1)

			password = self.__get_field(db)
			db = db[8 + len(password):]

			note = self.__get_field(db)
			db = db[8 + len(note):]

			e = entry.GenericEntry()
			e.name			= self.__normalize_field(name)
			e.description		= self.__normalize_field(note)
			e[entry.UsernameField]	= self.__normalize_field(username)
			e[entry.PasswordField]	= self.__normalize_field(password)

			entrystore.add_entry(e)

		return entrystore

