#
# Revelation 0.3.2 - a password manager for GNOME 2
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

import revelation, copy, gobject, gtk, time


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


FIELDDATA = {
	FIELD_GENERIC_CODE		: {
		"name"		: "Code",
		"type"		: FIELD_TYPE_PASSWORD,
		"description" 	: "A code used to provide access to something",
		"symbol"	: "c"
	},

	FIELD_GENERIC_CERTIFICATE	: {
		"name" 		: "Certificate",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A certificate, such as an X.509 SSL Certificate",
		"symbol"	: "x"
	},

	FIELD_GENERIC_DATABASE		: {
		"name"		: "Database",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A database name",
		"symbol"	: "D"
	},

	FIELD_GENERIC_DOMAIN		: {
		"name"		: "Domain",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "An Internet or logon domain, like amazon.com or a Windows logon domain",
		"symbol"	: "d"
	},

	FIELD_GENERIC_EMAIL		: {
		"name"		: "Email address",
		"type"		: FIELD_TYPE_EMAIL,
		"description"	: "An email address",
		"symbol"	: "e"
	},

	FIELD_GENERIC_HOSTNAME		: {
		"name"		: "Hostname",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The name of a computer, like computer.domain.com or MYCOMPUTER",
		"symbol"	: "h"
	},

	FIELD_GENERIC_KEYFILE		: {
		"name"		: "Key File",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A key file, used for authentication for example via ssh or to encrypt X.509 certificates",
		"symbol"	: "f"
	},

	FIELD_GENERIC_LOCATION		: {
		"name"		: "Location",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A physical location, like office entrance",
		"symbol"	: "L"
	},

	FIELD_GENERIC_PASSWORD		: {
		"name"		: "Password",
		"type"		: FIELD_TYPE_PASSWORD,
		"description"	: "A secret word or character combination used for proving you have access",
		"symbol"	: "p"
	},

	FIELD_GENERIC_PIN		: {
		"name"		: "PIN",
		"type"		: FIELD_TYPE_PASSWORD,
		"description"	: "A Personal Identification Number, a numeric code used for credit cards, phones etc",
		"symbol"	: "P"
	},

	FIELD_GENERIC_PORT		: {
		"name"		: "Port number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A network port number, used to access network services directly",
		"symbol"	: "o"
	},

	FIELD_GENERIC_URL		: {
		"name"		: "URL",
		"type"		: FIELD_TYPE_URL,
		"description"	: "A Uniform Resource Locator, such as a web-site address",
		"symbol"	: "U"
	},

	FIELD_GENERIC_USERNAME		: {
		"name"		: "Username",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A name or other identification used to identify yourself",
		"symbol"	: "u"
	},

	FIELD_CREDITCARD_CARDTYPE	: {
		"name"		: "Card type",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The type of creditcard, like MasterCard or VISA",
		"symbol"	: "C"
	},

	FIELD_CREDITCARD_CARDNUMBER 	: {
		"name"		: "Card number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The number of a creditcard, usually a 16-digit number",
		"symbol"	: "N"
	},

	FIELD_CREDITCARD_CCV		: {
		"name"		: "CCV number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A Credit Card Verification number, normally a 3-digit code found on the back of a card",
		"symbol"	: "V"
	},

	FIELD_CREDITCARD_EXPIRYDATE	: {
		"name"		: "Expiry date",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "The month that the credit card validity expires",
		"symbol"	: "E"
	},

	FIELD_PHONE_PHONENUMBER		: {
		"name"		: "Phone number",
		"type"		: FIELD_TYPE_TEXT,
		"description"	: "A telephone number",
		"symbol"	: "n"
	}
}



class EntryError(Exception):
	pass

class EntryFieldError(EntryError):
	pass

class EntryTypeError(EntryError):
	pass



class LaunchError(Exception):
	pass

class NoLaunchError(LaunchError):
	pass

class LaunchDataError(LaunchError):
	pass

class LaunchFormatError(LaunchError):
	pass



class Entry(gobject.GObject):
	"An entry object"

	id		= None
	typename	= ""
	icon		= None

	def __init__(self):
		gobject.GObject.__init__(self)

		self.name		= ""
		self.description	= ""
		self.updated		= 0
		self.fields		= []


	def can_launch(self):
		"Checks if the entry can be launched"

		try:
			self.get_launcher()

		except NoLaunchError:
			return gtk.FALSE

		except LaunchError:
			return gtk.TRUE

		else:
			return gtk.TRUE


	def copy(self):
		"Create a copy of the entry"

		return copy.deepcopy(self)


	def get_field(self, id):
		"Get one of the entrys fields"

		try:
			return self.fields[id]

		except KeyError:
			raise EntryFieldError


	def get_launcher(self):
		"Returns the launcher for the entry"

		try:
			launcher = revelation.data.config_get("launcher/" + self.id)

			if launcher in [ "", None ]:
				raise NoLaunchError

		except revelation.data.ConfigError:
			raise NoLaunchError


		return launcher


	def get_launcher_parsed(self):
		"Returns the parsed launcher for an entry"

		launcher = self.get_launcher()

		subst = {}

		for field in self.fields:
			subst[field.symbol] = field.value

		try:
			command = revelation.misc.parse_subst(launcher, subst)

		except revelation.misc.SubstValueError:
			raise LaunchDataError

		except revelation.misc.SubstFormatError:
			raise LaunchFormatError

		return command


	def get_updated_age(self):
		"Get the age of an entry"

		return revelation.misc.timediff_simple(self.updated)


	def get_updated_iso(self):
		"Get the update time in ISO format"

		return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.updated))


	def has_field(self, id):
		"Checks if the entry has a particular field"

		for field in self.fields:
			if field.id == id:
				return gtk.TRUE

		else:
			return gtk.FALSE


	def import_data(self, entry):
		"Imports data from a different entry"

		self.name		= entry.name
		self.description	= entry.description
		self.updated		= entry.updated

		for field in entry.fields:
			if self.has_field(field.id):
				self.set_field(field.id, field.value)


	def launch(self):
		"Attempts to launch the entry"

		revelation.io.execute_child(self.get_launcher_parsed())


	def set_field(self, id, value):
		"Sets one of the entries fields to a value"

		for field in self.fields:
			if field.id == id:
				field.value = value
				break

		else:
			raise EntryFieldError



class FolderEntry(Entry):

	id		= "folder"
	typename	= "Folder"
	icon		= revelation.stock.STOCK_FOLDER

	def __init__(self):
		Entry.__init__(self)



class CreditcardEntry(Entry):

	id		= "creditcard"
	typename	= "Creditcard"
	icon		= revelation.stock.STOCK_ACCOUNT_CREDITCARD

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_CREDITCARD_CARDTYPE),
			Field(FIELD_CREDITCARD_CARDNUMBER),
			Field(FIELD_CREDITCARD_EXPIRYDATE),
			Field(FIELD_CREDITCARD_CCV),
			Field(FIELD_GENERIC_PIN)
		]



class CryptoKeyEntry(Entry):

	id		= "cryptokey"
	typename	= "Crypto Key"
	icon		= revelation.stock.STOCK_ACCOUNT_CRYPTOKEY

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_HOSTNAME),
			Field(FIELD_GENERIC_CERTIFICATE),
			Field(FIELD_GENERIC_KEYFILE),
			Field(FIELD_GENERIC_PASSWORD)
		]



class DatabaseEntry(Entry):

	id		= "database"
	typename	= "Database"
	icon		= revelation.stock.STOCK_ACCOUNT_DATABASE

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_HOSTNAME),
			Field(FIELD_GENERIC_USERNAME),
			Field(FIELD_GENERIC_PASSWORD),
			Field(FIELD_GENERIC_DATABASE)
		]



class DoorEntry(Entry):

	id		= "door"
	typename	= "Door lock"
	icon		= revelation.stock.STOCK_ACCOUNT_DOOR

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_LOCATION),
			Field(FIELD_GENERIC_CODE)
		]



class EmailEntry(Entry):

	id		= "email"
	typename	= "Email"
	icon		= revelation.stock.STOCK_ACCOUNT_EMAIL

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_EMAIL),
			Field(FIELD_GENERIC_HOSTNAME),
			Field(FIELD_GENERIC_USERNAME),
			Field(FIELD_GENERIC_PASSWORD)
		]



class FTPEntry(Entry):

	id		= "ftp"
	typename	= "FTP"
	icon		= revelation.stock.STOCK_ACCOUNT_FTP

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_HOSTNAME),
			Field(FIELD_GENERIC_PORT),
			Field(FIELD_GENERIC_USERNAME),
			Field(FIELD_GENERIC_PASSWORD)
		]



class GenericEntry(Entry):

	id		= "generic"
	typename	= "Generic"
	icon		= revelation.stock.STOCK_ACCOUNT_GENERIC

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_HOSTNAME),
			Field(FIELD_GENERIC_USERNAME),
			Field(FIELD_GENERIC_PASSWORD)
		]



class PhoneEntry(Entry):

	id		= "phone"
	typename	= "Phone"
	icon		= revelation.stock.STOCK_ACCOUNT_PHONE

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_PHONE_PHONENUMBER),
			Field(FIELD_GENERIC_PIN)
		]



class ShellEntry(Entry):

	id		= "shell"
	typename	= "Shell"
	icon		= revelation.stock.STOCK_ACCOUNT_SHELL

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_HOSTNAME),
			Field(FIELD_GENERIC_DOMAIN),
			Field(FIELD_GENERIC_USERNAME),
			Field(FIELD_GENERIC_PASSWORD)
		]



class WebEntry(Entry):

	id		= "website"
	typename	= "Website"
	icon		= revelation.stock.STOCK_ACCOUNT_WEBSITE

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			Field(FIELD_GENERIC_URL),
			Field(FIELD_GENERIC_USERNAME),
			Field(FIELD_GENERIC_PASSWORD)
		]



class Field(gobject.GObject):
	"An entry field object"

	def __init__(self, id = None, value = ""):
		gobject.GObject.__init__(self)

		self.id			= id
		self.value		= value
		self.type		= FIELDDATA[id]["type"]
		self.name		= FIELDDATA[id]["name"]
		self.description	= FIELDDATA[id]["description"]
		self.symbol		= FIELDDATA[id]["symbol"]


	def generate_display_widget(self):
		"Generates a widget for displaying the field"

		if self.type == FIELD_TYPE_EMAIL:
			widget = revelation.widget.HRef("mailto:" + self.value, revelation.misc.escape_markup(self.value))

		elif self.type == FIELD_TYPE_PASSWORD:
			widget = revelation.widget.PasswordLabel(revelation.misc.escape_markup(self.value))

		elif self.type == FIELD_TYPE_URL:
			widget = revelation.widget.HRef(self.value, revelation.misc.escape_markup(self.value))

		else:
			widget = revelation.widget.Label(revelation.misc.escape_markup(self.value))
			widget.set_selectable(gtk.TRUE)

		return widget


	def generate_edit_widget(self):
		"Generates a widget for editing the field"

		if self.id == FIELD_GENERIC_PASSWORD:
			entry = revelation.widget.PasswordEntryGenerate()

		elif self.type == FIELD_TYPE_PASSWORD:
			entry = revelation.widget.PasswordEntry()

		else:
			entry = revelation.widget.Entry()

		entry.set_text(self.value)

		return entry



def convert_entry_generic(entry):
	"Converts to a generic account, tries to keep as much data as possible"

	# set up the initial generic entry
	generic = GenericEntry()
	generic.import_data(entry)

	# do direct field copies
	for field in generic:
		if entry.has_field(field.id):
			field.value = entry.get_field(field.id).value


	# handle special conversions
	field_hostname = generic.get_field(FIELD_GENERIC_HOSTNAME)
	field_username = generic.get_field(FIELD_GENERIC_USERNAME)
	field_password = generic.get_field(FIELD_GENERIC_PASSWORD)

	if type(entry) == CreditcardEntry:
		field_username.value = entry.get_field(FIELD_CREDITCARD_CARDNUMBER.value)
		field_password.value = entry.get_field(FIELD_GENERIC_PIN).value

	elif type(entry) == CryptoKeyEntry:
		field_username.value = entry.get_field(FIELD_GENERIC_KEYFILE).value

	elif type(entry) == DatabaseEntry:
		if entry.get_field(FIELD_GENERIC_DATABASE).value != "":
			field_hostname.value = entry.get_field(FIELD_GENERIC_DATABASE).value + "@" + field_hostname.value

	elif type(entry) == DoorEntry:
		field_password.value = entry.get_field(FIELD_GENERIC_CODE).value
		field_hostname.value = entry.get_field(FIELD_GENERIC_LOCATION).value

	elif type(entry) == FTPEntry:
		
		field_hostname.value = "ftp://" + entry.get_field(FIELD_GENERIC_HOSTNAME).value

		if entry.get_field(FIELD_GENERIC_PORT).value != "":
			field_hostname.value += ":" + entry.get_field(FIELD_GENERIC_PORT).value

	elif type(entry) == PhoneEntry:
		field_username.value = entry.get_field(FIELD_PHONE_PHONENUMBER).value
		field_password.value = entry.get_field(FIELD_GENERIC_PIN).value

	elif type(entry) == WebEntry:
		field_hostname.value  = entry.get_field(FIELD_GENERIC_URL).value



def get_entry_list():
	"Returns a sorted list of all available entry types"

	return [
		FolderEntry,
		CreditcardEntry,
		CryptoKeyEntry,
		DatabaseEntry,
		DoorEntry,
		EmailEntry,
		FTPEntry,
		GenericEntry,
		PhoneEntry,
		ShellEntry,
		WebEntry
	]



def lookup_entry(id):
	"Looks up an entry based on an id"

	for entry in get_entry_list():
		if entry.id == id:
			return entry

	else:
		return None

