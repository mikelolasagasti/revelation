#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing entry information
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

import revelation, gobject, copy, time


ENTRY_FOLDER			= "folder"
ENTRY_ACCOUNT_CREDITCARD	= "creditcard"
ENTRY_ACCOUNT_CRYPTOKEY		= "cryptokey"
ENTRY_ACCOUNT_DATABASE		= "database"
ENTRY_ACCOUNT_DOOR		= "door"
ENTRY_ACCOUNT_EMAIL		= "email"
ENTRY_ACCOUNT_FTP		= "ftp"
ENTRY_ACCOUNT_GENERIC		= "generic"
ENTRY_ACCOUNT_PHONE		= "phone"
ENTRY_ACCOUNT_SHELL		= "shell"
ENTRY_ACCOUNT_WEBSITE		= "website"


FIELD_GENERIC_CERTIFICATE	= "generic-certificate"
FIELD_GENERIC_CODE		= "generic-code"
FIELD_GENERIC_DATABASE		= "generic-database"
FIELD_GENERIC_DOMAIN		= "generic-domain"
FIELD_GENERIC_EMAIL		= "generic-email"
FIELD_GENERIC_HOSTNAME		= "generic-hostname"
FIELD_GENERIC_KEYFILE		= "generic-keyfile"
FIELD_GENERIC_LOCATION		= "generic-location"
FIELD_GENERIC_PASSWORD		= "generic-password"
FIELD_GENERIC_PIN		= "generic-pin"
FIELD_GENERIC_PORT		= "generic-port"
FIELD_GENERIC_URL		= "generic-url"
FIELD_GENERIC_USERNAME		= "generic-username"

FIELD_CREDITCARD_CARDTYPE	= "creditcard-cardtype"
FIELD_CREDITCARD_CARDNUMBER	= "creditcard-cardnumber"
FIELD_CREDITCARD_CCV		= "creditcard-ccv"
FIELD_CREDITCARD_EXPIRYDATE	= "creditcard-expirydate"

FIELD_PHONE_PHONENUMBER		= "phone-phonenumber"


FIELD_TYPE_EMAIL		= "email"
FIELD_TYPE_PASSWORD		= "password"
FIELD_TYPE_TEXT			= "text"
FIELD_TYPE_URL			= "url"


ENTRYDATA = {
	ENTRY_FOLDER			: {
		"name"		: "Folder",
		"icon"		: revelation.stock.STOCK_FOLDER,
		"fields"	: []
	},

	ENTRY_ACCOUNT_CREDITCARD	: {
		"name"		: "Creditcard",
		"icon"		: revelation.stock.STOCK_ACCOUNT_CREDITCARD,
		"fields"	: [ FIELD_CREDITCARD_CARDTYPE, FIELD_CREDITCARD_CARDNUMBER, FIELD_CREDITCARD_EXPIRYDATE, FIELD_CREDITCARD_CCV, FIELD_GENERIC_PIN ]
	},

	ENTRY_ACCOUNT_CRYPTOKEY		: {
		"name"		: "Crypto Key",
		"icon"		: revelation.stock.STOCK_ACCOUNT_CRYPTOKEY,
		"fields"	: [ FIELD_GENERIC_HOSTNAME, FIELD_GENERIC_CERTIFICATE, FIELD_GENERIC_KEYFILE, FIELD_GENERIC_PASSWORD ]
	},

	ENTRY_ACCOUNT_DATABASE		: {
		"name"		: "Database",
		"icon"		: revelation.stock.STOCK_ACCOUNT_DATABASE,
		"fields"	: [ FIELD_GENERIC_HOSTNAME, FIELD_GENERIC_USERNAME, FIELD_GENERIC_PASSWORD, FIELD_GENERIC_DATABASE ]
	},

	ENTRY_ACCOUNT_DOOR		: {
		"name"		: "Door lock",
		"icon"		: revelation.stock.STOCK_ACCOUNT_DOOR,
		"fields"	: [ FIELD_GENERIC_LOCATION, FIELD_GENERIC_CODE ]
	},

	ENTRY_ACCOUNT_EMAIL		: {
		"name"		: "Email",
		"icon"		: revelation.stock.STOCK_ACCOUNT_EMAIL,
		"fields"	: [ FIELD_GENERIC_EMAIL, FIELD_GENERIC_HOSTNAME, FIELD_GENERIC_USERNAME, FIELD_GENERIC_PASSWORD ]
	},

	ENTRY_ACCOUNT_FTP		: {
		"name"		: "FTP",
		"icon"		: revelation.stock.STOCK_ACCOUNT_FTP,
		"fields"	: [ FIELD_GENERIC_HOSTNAME, FIELD_GENERIC_PORT, FIELD_GENERIC_USERNAME, FIELD_GENERIC_PASSWORD ]
	},

	ENTRY_ACCOUNT_GENERIC		: {
		"name"		: "Generic",
		"icon"		: revelation.stock.STOCK_ACCOUNT,
		"fields"	: [ FIELD_GENERIC_HOSTNAME, FIELD_GENERIC_USERNAME, FIELD_GENERIC_PASSWORD ]
	},

	ENTRY_ACCOUNT_PHONE		: {
		"name"		: "Phone",
		"icon"		: revelation.stock.STOCK_ACCOUNT_PHONE,
		"fields"	: [ FIELD_PHONE_PHONENUMBER, FIELD_GENERIC_PIN ]
	},

	ENTRY_ACCOUNT_SHELL		: {
		"name"		: "Shell",
		"icon"		: revelation.stock.STOCK_ACCOUNT_SHELL,
		"fields"	: [ FIELD_GENERIC_HOSTNAME, FIELD_GENERIC_DOMAIN, FIELD_GENERIC_USERNAME, FIELD_GENERIC_PASSWORD ]
	},

	ENTRY_ACCOUNT_WEBSITE		: {
		"name"		: "Website",
		"icon"		: revelation.stock.STOCK_ACCOUNT_WEBSITE,
		"fields"	: [ FIELD_GENERIC_URL, FIELD_GENERIC_USERNAME, FIELD_GENERIC_PASSWORD ]
	}
}


FIELDDATA = {
	FIELD_GENERIC_CODE		: {
		"name"		: "Code",
		"type"		: FIELD_TYPE_PASSWORD,
		"description" 	: "A code used to provide access to something"
	},

	FIELD_GENERIC_CERTIFICATE	: {
		"name" 		: "Certificate",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A certificate, such as an X.509 SSL Certificate"
	},

	FIELD_GENERIC_DATABASE		: {
		"name"		: "Database",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A database name"
	},

	FIELD_GENERIC_DOMAIN		: {
		"name"		: "Domain",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "An Internet or logon domain, like amazon.com or a Windows logon domain"
	},

	FIELD_GENERIC_EMAIL		: {
		"name"		: "Email address",
		"type"		: FIELD_TYPE_EMAIL,
		"description"	: "An email address"
	},

	FIELD_GENERIC_HOSTNAME		: {
		"name"		: "Hostname",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The name of a computer, like computer.domain.com or MYCOMPUTER"
	},

	FIELD_GENERIC_KEYFILE		: {
		"name"		: "Key File",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A key file, used for authentication for example via ssh or to encrypt X.509 certificates"
	},

	FIELD_GENERIC_LOCATION		: {
		"name"		: "Location",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A physical location, like office entrance"
	},

	FIELD_GENERIC_PASSWORD		: {
		"name"		: "Password",
		"type"		: FIELD_TYPE_PASSWORD,
		"description"	: "A secret word or character combination used for proving you have access"
	},

	FIELD_GENERIC_PIN		: {
		"name"		: "PIN",
		"type"		: FIELD_TYPE_PASSWORD,
		"description"	: "A Personal Identification Number, a numeric code used for credit cards, phones etc"
	},

	FIELD_GENERIC_PORT		: {
		"name"		: "Port number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A network port number, used to access network services directly"
	},

	FIELD_GENERIC_URL		: {
		"name"		: "URL",
		"type"		: FIELD_TYPE_URL,
		"description"	: "A Uniform Resource Locator, such as a web-site address"
	},

	FIELD_GENERIC_USERNAME		: {
		"name"		: "Username",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A name or other identification used to identify yourself"
	},

	FIELD_CREDITCARD_CARDTYPE	: {
		"name"		: "Card type",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The type of creditcard, like MasterCard or VISA"
	},

	FIELD_CREDITCARD_CARDNUMBER 	: {
		"name"		: "Card number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The number of a creditcard, usually a 16-digit number"
	},

	FIELD_CREDITCARD_CCV		: {
		"name"		: "CCV number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A Credit Card Verification number, normally a 3-digit code found on the back of a card"
	},

	FIELD_CREDITCARD_EXPIRYDATE	: {
		"name"		: "Expiry date",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The month that the credit card validity expires"
	},

	FIELD_PHONE_PHONENUMBER		: {
		"name"		: "Phone number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A telephone number"
	}
}


class EntryError(Exception):
	pass

class EntryFieldError(EntryError):
	pass

class EntryTypeError(EntryError):
	pass



class Entry(gobject.GObject):

	def __init__(self, type = ENTRY_FOLDER):
		gobject.GObject.__init__(self)

		self.name		= ""
		self.description	= ""
		self.type		= None
		self.typename		= ""
		self.updated		= 0
		self.icon		= None
		self.fields		= {}
		self.oldfields		= {}

		self.set_type(type)


	def copy(self):
		return copy.deepcopy(self)


	def get_field(self, id):
		try:
			return self.fields[id]

		except KeyError:
			raise EntryFieldError


	def get_fields(self):
		fields = []
		for id in ENTRYDATA[self.type]["fields"]:
			fields.append(self.get_field(id))

		return fields


	def get_updated_age(self):
		return revelation.misc.timediff_simple(self.updated)


	def get_updated_iso(self):
		return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.updated))


	def has_field(self, id):
		return self.fields.has_key(id)


	def set_field(self, id, value):
		if not self.fields.has_key(id):
			raise EntryFieldError

		self.fields[id] = Field(id, value)


	def set_type(self, type):

		# backwards-compatability
		if type == "usenet":
			type = ENTRY_ACCOUNT_GENERIC

		if not ENTRYDATA.has_key(type):
			raise EntryTypeError

		# convert entry to new type
		self.type	= type
		self.typename	= ENTRYDATA[type]["name"]
		self.icon	= ENTRYDATA[type]["icon"]

		# store current field values
		for id, field in self.fields.items():
			self.oldfields[id] = field

		# set up new fields
		self.fields = {}
		for id in ENTRYDATA[self.type]["fields"]:
			if self.oldfields.has_key(id):
				self.fields[id] = self.oldfields[id]
			else:
				self.fields[id] = Field(id)



class Field(gobject.GObject):

	def __init__(self, id = None, value = ""):
		gobject.GObject.__init__(self)

		self.id			= id
		self.value		= value
		self.type		= FIELDDATA[id]["type"]
		self.name		= FIELDDATA[id]["name"]
		self.description	= FIELDDATA[id]["description"]

