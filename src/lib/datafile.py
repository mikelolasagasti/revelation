#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.wired-networks.net/revelation/
#
# Module for importing from / exporting to a datafile
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

import gobject, os, revelation, gtk, libxml2, zlib, random, math, time, binascii, re
from Crypto.Cipher import AES, Blowfish
from Crypto.Hash import MD5

TYPE_AUTO		= "autodetect"
TYPE_FPM		= "fpm"
TYPE_REVELATION		= "revelation"
TYPE_XML		= "xml"

CHECKBUFFER		= 4096

# data classes
class FileTypes(object):

	def __init__(self):

		self.filetypes = {
			TYPE_FPM	: {
				"name"		: "Figaro's Password Manager",
				"import"	: gtk.TRUE,
				"export"	: gtk.TRUE,
				"datahandler"	: FPMData,
				"defaultfile"	: "~/.fpm/fpm"
			},

			TYPE_REVELATION	: {
				"name"		: "Revelation",
				"import"	: gtk.TRUE,
				"export"	: gtk.FALSE,
				"datahandler"	: RevelationData,
				"defaultfile"	: None
			},

			TYPE_XML : {
				"name"		: "XML (eXtensible Markup Language)",
				"import"	: gtk.TRUE,
				"export"	: gtk.TRUE,
				"datahandler"	: RevelationXMLData,
				"defaultfile"	: None
			}
		}


	def get_export_types(self):
		types = []
		for type, data in self.filetypes.items():
			if data["export"] == gtk.TRUE:
				types.append(type)

		types.sort()
		return types


	def get_import_types(self):
		types = []
		for type, data in self.filetypes.items():
			if data["import"] == gtk.TRUE:
				types.append(type)

		types.sort()
		return types


	def get_data(self, type, attr = None):
		if attr == None:
			return self.filetypes[type]
		else:
			return self.filetypes[type][attr]


	def type_exists(self, type):
		return self.filetypes.has_key(type)




# a few exceptions
class FormatError(Exception):
	"""Exception for invalid file formats"""
	pass

class PasswordError(Exception):
	"""Exception for wrong password"""
	pass

class VersionError(Exception):
	"""Exception for unknown versions"""
	pass

class DetectError(Exception):
	"""Exception for failed autodetection"""
	pass

class EntryError(Exception):
	"""Base class for entry errors"""
	pass

class EntryFieldError(EntryError):
	"""Exception for invalid field type for an entry type"""
	pass

class EntryTypeError(EntryError):
	"""Exception for unknown entry type"""
	pass



class DataFile(gobject.GObject):

	def __init__(self, file = None, type = None):
		gobject.GObject.__init__(self)
		self.filetypes = FileTypes()
		self.handler = None

		self.type = type
		self.file = file


	# set up custom attribute handling, so that the data handlers can
	# be accessed through the datafile instance (for setting options etc)
	def __getattr__(self, name):
		if name == "handler":
			return None
		else:
			return getattr(self.handler, name)


	def __setattr__(self, name, value):
		if hasattr(self.handler, name):
			self.handler.password = value

		else:
			if name == "type" and value is not None:
				handler = self.filetypes.get_data(value, "datahandler")()
				self.handler = handler

			gobject.GObject.__setattr__(self, name, value)


	def __read(self, file, bytes = -1):
		if file == None:
			raise IOError

		fp = open(file, "rb", 0)
		data = fp.read(bytes)
		fp.close()

		return data


	def __write(self, file, data):
		if file == None:
			raise IOError

		fp = open(file, "wb", 0)
		fp.write(data)
		fp.flush()
		fp.close()


	def check_file(self):
		if self.file == None or os.access(self.file, os.R_OK) == 0:
			raise IOError


	def check_format(self):
		data = self.__read(self.file, CHECKBUFFER)
		self.handler.check_data(data)


	def detect_type(self):
		header = self.__read(self.file, CHECKBUFFER)

		for detecttype in self.filetypes.get_import_types():
			handler = self.filetypes.get_data(detecttype, "datahandler")()

			if handler.detect_type(header) == gtk.TRUE:
				self.type = detecttype
				return detecttype

		raise DetectError


	def load(self):
		self.check_file()
		self.check_format()

		entrystore = revelation.data.EntryStore()
		data = self.__read(self.file)
		self.handler.import_data(entrystore, data)

		return entrystore


	def save(self, entrystore):
		data = self.handler.export_data(entrystore)
		self.__write(self.file, data)



class Data(gobject.GObject):

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



class FPMData(Data):

	def __init__(self):
		Data.__init__(self)
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


	def __xml_export_convert_data(self, data):
		fpmdata = {
			"title"		: data["name"],
			"user"		: "",
			"url"		: "",
			"password"	: "",
			"notes"		: data["description"],
			"category"	: "",
			"launcher"	: ""
		}

		fields = data["fields"]

		if data["type"] == revelation.entry.ENTRY_ACCOUNT_CREDITCARD:
			fpmdata["user"]		= fields[revelation.entry.FIELD_CREDITCARD_CARDNUMBER]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PIN]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_CRYPTOKEY:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_KEYFILE]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]
			fpmdata["url"]		= fields[revelation.entry.FIELD_GENERIC_HOSTNAME]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_DATABASE:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_USERNAME]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]
			fpmdata["url"]		= fields[revelation.entry.FIELD_GENERIC_HOSTNAME] + ": " + fields[revelation.entry.FIELD_GENERIC_DATABASE]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_DOOR:
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_CODE]
			fpmdata["url"]		= fields[revelation.entry.FIELD_GENERIC_LOCATION]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_EMAIL:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_USERNAME]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]
			fpmdata["url"]		= fields[revelation.entry.FIELD_GENERIC_HOSTNAME]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_FTP:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_USERNAME]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]
			fpmdata["url"]		= "ftp://" + fields[revelation.entry.FIELD_GENERIC_HOSTNAME]
	
			if fields[revelation.entry.FIELD_GENERIC_PORT] != "":
				fpmdata["url"]	= fpmdata["url"] + ":" + fields[revelation.entry.FIELD_GENERIC_PORT]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_GENERIC:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_USERNAME]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_PHONE:
			fpmdata["user"]		= fields[revelation.entry.FIELD_PHONE_PHONENUMBER]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PIN]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_SHELL:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_USERNAME]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]
			fpmdata["url"]		= fields[revelation.entry.FIELD_GENERIC_HOSTNAME]

		elif data["type"] == revelation.entry.ENTRY_ACCOUNT_WEBSITE:
			fpmdata["user"]		= fields[revelation.entry.FIELD_GENERIC_USERNAME]
			fpmdata["password"]	= fields[revelation.entry.FIELD_GENERIC_PASSWORD]
			fpmdata["url"]		= fields[revelation.entry.FIELD_GENERIC_URL]

		return fpmdata


	def __xml_export_entries(self, entrystore, parent = None):
		xml = ""

		for i in range(entrystore.iter_n_children(parent)):
			child = entrystore.iter_nth_child(parent, i)
			data = entrystore.get_entry(child)

			if data["type"] == revelation.entry.ENTRY_FOLDER:
				xml = xml + self.__xml_export_entries(entrystore, child)

			else:

				# convert data to fpm structure
				fpmdata = self.__xml_export_convert_data(data)

				path = entrystore.get_path(child)
				if len(path) > 1:
					fpmdata["category"] = entrystore.get_entry(entrystore.get_iter(path[0]))["name"]

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


	def __xml_import_entry(self, entry, entrystore, foldercache):
		if entry.type != "element" or entry.name != "PasswordItem":
			return

		parent = None
		data = {
			"type"		: revelation.entry.ENTRY_ACCOUNT_GENERIC,
			"updated"	: time.time(),
			"fields"	: {}
		}

		field = entry.children
		while field is not None:
			if field.type == "element":
				content = self.__decrypt_field(field.content)

				if field.name == "title":
					data["name"] = content

				elif field.name == "user":
					data["fields"][revelation.entry.FIELD_GENERIC_USERNAME] = content

				elif field.name == "url":
					data["fields"][revelation.entry.FIELD_GENERIC_HOSTNAME] = content

				elif field.name == "password":
					data["fields"][revelation.entry.FIELD_GENERIC_PASSWORD] = content

				elif field.name == "notes":
					data["description"] = content

				elif field.name == "category":
					foldername = content.strip()

					if foldername == "":
						pass
					elif foldercache.has_key(foldername):
						parent = foldercache[foldername]
					else:
						parent = entrystore.add_entry(None, {"type": revelation.entry.ENTRY_FOLDER, "name": foldername, "updated": time.time()})
						foldercache[foldername] = parent

			field = field.next

		entrystore.add_entry(parent, data)


	def __xml_import_keyinfo(self, root):
		keynode = self.xml_import_scan(root, "KeyInfo")
		if keynode == None:
			raise FormatError

		attrs = self.xml_import_attrs(keynode)
		if not attrs.has_key("salt") or not attrs.has_key("vstring"):
			raise FormatError

		info = {
			"salt"		: attrs["salt"],
			"vstring"	: attrs["vstring"]
		}

		return info


	def check_data(self, data):
		if re.search("^<\?xml.*\?>\s*<FPM\s+", data, re.IGNORECASE) == None:
			raise FormatError


	def detect_type(self, header):
		try:
			self.check_data(header)
		except FormatError:
			return gtk.FALSE
		else:
			return gtk.TRUE


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
			raise FormatError

		# set up cipher and check if password is correct
		keyinfo = self.__xml_import_keyinfo(root)
		self.cipher_init(Blowfish, MD5.new(keyinfo["salt"] + self.password).digest())

		if self.__decrypt_field(keyinfo["vstring"]) != "FIGARO":
			raise PasswordError

		# import entries into entrystore
		pwlist = self.xml_import_scan(root, "PasswordList")
		if pwlist == None:
			raise FormatError

		foldercache = {}
		entry = pwlist.children
		while entry is not None:
			self.__xml_import_entry(entry, entrystore, foldercache)
			entry = entry.next



class RevelationXMLData(Data):

	def __xml_import_node(self, entrystore, node, parent = None):

		if node.type == "text":
			return

		if node.type != "element" or node.name != "entry":
			raise FormatError

		data = {
			"type"		: self.xml_import_attrs(node)["type"],
			"fields"	: {}
		}

		# convert obsolete types, for backwards-compatability
		if data["type"] == "usenet":
			data["type"] = revelation.entry.ENTRY_ACCOUNT_GENERIC

		if not revelation.entry.entry_exists(data["type"]):
			raise EntryTypeError

		# add empty entry, iter needed for any children
		iter = entrystore.add_entry(parent)

		child = node.children
		while child is not None:

			if child.type == "element":

				if child.name == "name":
					data["name"] = child.content

				elif child.name == "description":
					data["description"] = child.content

				elif child.name == "updated":
					data["updated"] = int(child.content)

				elif child.name == "field":
					field = self.xml_import_attrs(child)["id"]

					if not revelation.entry.field_exists(data["type"], field):
						raise EntryFieldError

					data["fields"][field] = child.content

				elif child.name == "entry":
					self.__xml_import_node(entrystore, child, iter)

				else:
					raise FormatError

			child = child.next

		# update entry with actual data
		entrystore.update_entry(iter, data)


	def check_data(self, data):
		match = re.search("^\s*<\?xml.*\?>\s*<revelationdata.+dataversion=\"(\S+)\"", data, re.IGNORECASE)

		if match == None:
			raise FormatError

		if int(match.group(1)) > revelation.DATAVERSION:
			raise VersionError


	def detect_type(self, data):
		try:
			self.check_data(data)
		except FormatError:
			return gtk.FALSE
		else:
			return gtk.TRUE


	def export_data(self, entrystore, parent = None, level = 0):
		xml = ""
		tabs = "\t" * (level + 1)

		# process each child
		for i in range(entrystore.iter_n_children(parent)):
			iter = entrystore.iter_nth_child(parent, i)
			data = entrystore.get_entry(iter)

			xml = xml + "\n"
			xml = xml + tabs + "<entry type=\"" + revelation.misc.escape_markup(data["type"]) + "\">\n"
			xml = xml + tabs + "	<name>" + revelation.misc.escape_markup(data["name"]) + "</name>\n"
			xml = xml + tabs + "	<description>" + revelation.misc.escape_markup(data["description"]) + "</description>\n"
			xml = xml + tabs + "	<updated>" + revelation.misc.escape_markup(str(data["updated"])) + "</updated>\n"

			for field, value in data["fields"].items():
				xml = xml + tabs + "	<field id=\"" + revelation.misc.escape_markup(field) + "\">" + revelation.misc.escape_markup(value) + "</field>\n"

			# handle any children
			xml = xml + RevelationXMLData.export_data(self, entrystore, iter, level + 1)

			xml = xml + tabs + "</entry>\n"

		# generate header and footer if at level 0
		if level == 0:
			header = "<?xml version=\"1.0\" ?>\n"
			header = header + "<revelationdata version=\"" + revelation.VERSION + "\" dataversion=\"" + str(revelation.DATAVERSION) + "\">\n"
			footer = "</revelationdata>\n"
			xml = header + xml + footer

		return xml


	def import_data(self, entrystore, data):
		doc = self.xml_import_init(data)

		# fetch and validate root
		root = doc.children
		if root.name != "revelationdata":
			raise FormatError

		attrs = self.xml_import_attrs(root)
		if attrs.has_key("dataversion") and int(attrs["dataversion"]) > revelation.DATAVERSION:
			raise VersionError

		# process entries
		child = root.children
		while child is not None:
			self.__xml_import_node(entrystore, child)
			child = child.next



class RevelationData(RevelationXMLData):

	def __init__(self):
		RevelationXMLData.__init__(self)
		self.blocksize = 16
		self.keysize = 32
		self.password = None


	def __decrypt(self, data, password, iv = None):
		self.cipher_init(AES, password, iv, self.blocksize, self.keysize)
		return self.cipher_decrypt(data)


	def __encrypt(self, data, password, iv = None):
		self.cipher_init(AES, password, iv, self.blocksize, self.keysize)
		return self.cipher_encrypt(data)


	def __generate_header(self):
		header = "rvl\x00" + chr(revelation.DATAVERSION) + "\x00"
		for part in revelation.VERSION.split("."):
			header = header + chr(int(part))
		header = header + "\x00\x00\x00"

		return header


	def __parse_header(self, header):
		if len(header) != 12 or header[0:3] != "rvl":
			return None

		dataversion = ord(header[4])
		appversion = str(ord(header[6])) + "." + str(ord(header[7])) + "." + str(ord(header[8]))

		return dataversion, appversion


	def check_data(self, data):
		headerdata = self.__parse_header(data[0:12])

		# ignore version 0 data files (deprecated, remove in future version)
		if headerdata == None:
			return

		if headerdata[0] > revelation.DATAVERSION:
			raise VersionError


	def detect_type(self, header):
		return self.__parse_header(header[0:12]) != None


	def export_data(self, entrystore):

		# first, generate XML data from the entrystore
		data = RevelationXMLData.export_data(self, entrystore)

		# next, compress the data and right-pad it
		# (the pad is the repeated ascii value of the pad length)
		data = zlib.compress(data)

		padlen = 16 - (len(data) % 16)
		if padlen == 0:
			padlen = 16

		data = data + (chr(padlen) * padlen)

		# generate an initial vector for CBC encryption mode
		iv = ""
		for i in range(16):
			iv = iv + chr(int(random.random() * 255))

		# encrypt the data
		data = self.__encrypt(data, self.password, iv)

		# encrypt the iv, and prepend it to the data along with a header
		data = self.__generate_header() + self.__encrypt(iv, self.password) + data

		return data


	def import_data(self, entrystore, data):

		# get the version numbers from the header
		headerdata = self.__parse_header(data[0:12])

		# if no valid header was found, assume version 0 (0.1.x series).
		# this is deprecated, and support will be removed in a future version
		if headerdata == None:

			data = self.__decrypt(data, self.password)

			# if not xml file, assume wrong password (could be invalid file
			# as well, but in most cases it will be a wrong password)
			if data[0:5] != "<?xml":
				raise PasswordError

			RevelationXMLData.import_data(self, entrystore, data)


		# handle version 1 data file
		elif headerdata[0] == 1:

			# fetch and decrypt the initial vector for CBC mode decryption
			iv = self.__decrypt(data[12:28], self.password)

			# decrypt the data
			data = self.__decrypt(data[28:], self.password, iv)

			# get and check the pad length
			padlen = ord(data[-1])
			for i in data[-padlen:]:
				if ord(i) != padlen:
					raise PasswordError

			# decompress data
			data = zlib.decompress(data[0:-padlen])

			if data[0:5] != "<?xml":
				raise PasswordError

			# import xml into entrystore
			RevelationXMLData.import_data(self, entrystore, data)


		# future file version, raise exception
		else:
			raise VersionError

