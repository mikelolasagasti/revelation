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

import revelation, gobject, copy


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
		"tooltip" 	: "A code used to provide access to something"
	},

	FIELD_GENERIC_CERTIFICATE	: {
		"name" 		: "Certificate",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A certificate, such as an X.509 SSL Certificate"
	},

	FIELD_GENERIC_DATABASE		: {
		"name"		: "Database",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A database name"
	},

	FIELD_GENERIC_DOMAIN		: {
		"name"		: "Domain",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "An Internet or logon domain, like amazon.com or a Windows logon domain"
	},

	FIELD_GENERIC_EMAIL		: {
		"name"		: "Email address",
		"type"		: FIELD_TYPE_EMAIL,
		"tooltip"	: "An email address"
	},

	FIELD_GENERIC_HOSTNAME		: {
		"name"		: "Hostname",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "The name of a computer, like computer.domain.com or MYCOMPUTER"
	},

	FIELD_GENERIC_KEYFILE		: {
		"name"		: "Key File",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A key file, used for authentication for example via ssh or to encrypt X.509 certificates"
	},

	FIELD_GENERIC_LOCATION		: {
		"name"		: "Location",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A physical location, like office entrance"
	},

	FIELD_GENERIC_PASSWORD		: {
		"name"		: "Password",
		"type"		: FIELD_TYPE_PASSWORD,
		"tooltip"	: "A secret word or character combination used for proving you have access"
	},

	FIELD_GENERIC_PIN		: {
		"name"		: "PIN",
		"type"		: FIELD_TYPE_PASSWORD,
		"tooltip"	: "A Personal Identification Number, a numeric code used for credit cards, phones etc"
	},

	FIELD_GENERIC_PORT		: {
		"name"		: "Port number",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A network port number, used to access network services directly"
	},

	FIELD_GENERIC_URL		: {
		"name"		: "URL",
		"type"		: FIELD_TYPE_URL,
		"tooltip"	: "A Uniform Resource Locator, such as a web-site address"
	},

	FIELD_GENERIC_USERNAME		: {
		"name"		: "Username",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A name or other identification used to identify yourself"
	},

	FIELD_CREDITCARD_CARDTYPE	: {
		"name"		: "Card type",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "The type of creditcard, like MasterCard or VISA"
	},

	FIELD_CREDITCARD_CARDNUMBER 	: {
		"name"		: "Card number",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "The number of a creditcard, usually a 16-digit number"
	},

	FIELD_CREDITCARD_CCV		: {
		"name"		: "CCV number",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A Credit Card Verification number, normally a 3-digit code found on the back of a card"
	},

	FIELD_CREDITCARD_EXPIRYDATE	: {
		"name"		: "Expiry date",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "The month that the credit card validity expires"
	},

	FIELD_PHONE_PHONENUMBER		: {
		"name"		: "Phone number",
		"type"		: FIELD_TYPE_TEXT,
		"tooltip"	: "A telephone number"
	}
}



class Entry(gobject.GObject):

	def __init__(self, type = ENTRY_FOLDER):
		gobject.GObject.__init__(self)

		self.name		= ""
		self.description	= ""
		self.type		= None
		self.updated		= 0
		self.icon		= None
		self.fields		= {}
		self.oldfields		= {}

		self.set_type(type)


	def copy(self):
		return copy.deepcopy(self)


	def set_type(self, type):

		# backwards-compatability
		if type == "usenet":
			type = ENTRY_ACCOUNT_GENERIC

		# convert entry to new type
		self.type	= type
		self.icon	= get_entry_data(type, "icon")

		# store current field values
		for field, value in self.fields.items():
			self.oldfields[field] = value

		# set up new fields
		self.fields = {}
		for field in get_entry_fields(type):
			if self.oldfields.has_key(field):
				self.fields[field] = self.oldfields[field]
			else:
				self.fields[field] = ""



def field_exists(type, field):
	return field in ENTRYDATA[type]["fields"]

def get_field_data(field, attr = None):
	return attr is None and FIELDDATA[field] or FIELDDATA[field][attr]

def get_field_type(field):
	return FIELDDATA[field]["type"]



def entry_exists(entry):
	return ENTRYDATA.has_key(entry)

def get_entry_fields(entry):
	return ENTRYDATA[entry]["fields"]

def get_entry_list():
	list = ENTRYDATA.keys()
	list.sort()
	return list

def get_entry_template(entry):
	data = {
		"name"		: "",
		"description"	: "",
		"type"		: entry,
		"icon"		: get_entry_data(entry, "icon"),
		"updated"	: 0,
		"fields"	: {}
	}

	for field in get_entry_fields(entry):
		data["fields"][entry] = ""

	return data

def get_entry_data(type, attr = None):
	return attr is None and ENTRYDATA[type] or ENTRYDATA[type][attr]

