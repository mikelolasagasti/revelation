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


DATATYPE_EMAIL		= "email"
DATATYPE_PASSWORD	= "password"
DATATYPE_TEXT		= "text"
DATATYPE_URL		= "url"



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


	def get_field(self, fieldtype):
		"Get one of the entrys fields"

		for field in self.fields:
			if type(field) == fieldtype:
				return field

		else:
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


	def has_field(self, fieldtype):
		"Checks if the entry has a particular field"

		for field in self.fields:
			if type(field) == fieldtype:
				return gtk.TRUE

		else:
			return gtk.FALSE


	def import_data(self, entry):
		"Imports data from a different entry"

		self.name		= entry.name
		self.description	= entry.description
		self.updated		= entry.updated

		for field in entry.fields:
			if self.has_field(type(field)):
				self.get_field(type(field)).value = field.value


	def launch(self):
		"Attempts to launch the entry"

		revelation.io.execute_child(self.get_launcher_parsed())


	def lookup_field(self, id):
		"Looks up a field based on an id"

		for field in self.fields:
			if field.id == id:
				return field

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
			CardtypeField(),
			CardnumberField(),
			ExpirydateField(),
			CCVField(),
			PINField()
		]



class CryptoKeyEntry(Entry):

	id		= "cryptokey"
	typename	= "Crypto Key"
	icon		= revelation.stock.STOCK_ACCOUNT_CRYPTOKEY

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			HostnameField(),
			CertificateField(),
			KeyfileField(),
			PasswordField()
		]



class DatabaseEntry(Entry):

	id		= "database"
	typename	= "Database"
	icon		= revelation.stock.STOCK_ACCOUNT_DATABASE

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			HostnameField(),
			UsernameField(),
			PasswordField(),
			DatabaseField()
		]



class DoorEntry(Entry):

	id		= "door"
	typename	= "Door lock"
	icon		= revelation.stock.STOCK_ACCOUNT_DOOR

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			LocationField(),
			CodeField()
		]



class EmailEntry(Entry):

	id		= "email"
	typename	= "Email"
	icon		= revelation.stock.STOCK_ACCOUNT_EMAIL

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			EmailField(),
			HostnameField(),
			UsernameField(),
			PasswordField()
		]



class FTPEntry(Entry):

	id		= "ftp"
	typename	= "FTP"
	icon		= revelation.stock.STOCK_ACCOUNT_FTP

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			HostnameField(),
			PortField(),
			UsernameField(),
			PasswordField()
		]



class GenericEntry(Entry):

	id		= "generic"
	typename	= "Generic"
	icon		= revelation.stock.STOCK_ACCOUNT_GENERIC

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			HostnameField(),
			UsernameField(),
			PasswordField()
		]



class PhoneEntry(Entry):

	id		= "phone"
	typename	= "Phone"
	icon		= revelation.stock.STOCK_ACCOUNT_PHONE

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			PhonenumberField(),
			PINField()
		]



class ShellEntry(Entry):

	id		= "shell"
	typename	= "Shell"
	icon		= revelation.stock.STOCK_ACCOUNT_SHELL

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			HostnameField(),
			DomainField(),
			UsernameField(),
			PasswordField()
		]



class WebEntry(Entry):

	id		= "website"
	typename	= "Website"
	icon		= revelation.stock.STOCK_ACCOUNT_WEBSITE

	def __init__(self):
		Entry.__init__(self)

		self.fields = [
			URLField(),
			UsernameField(),
			PasswordField()
		]



class Field(gobject.GObject):
	"An entry field object"

	id		= None
	name		= ""
	description	= ""
	symbol		= None

	datatype	= None
	value		= None

	def __init__(self, value = ""):
		gobject.GObject.__init__(self)

		self.value = value


	def generate_display_widget(self):
		"Generates a widget for displaying the field"

		if self.datatype == DATATYPE_EMAIL:
			widget = revelation.widget.HRef("mailto:" + self.value, revelation.misc.escape_markup(self.value))

		elif self.datatype == DATATYPE_PASSWORD:
			widget = revelation.widget.PasswordLabel(revelation.misc.escape_markup(self.value))

		elif self.datatype == DATATYPE_URL:
			widget = revelation.widget.HRef(self.value, revelation.misc.escape_markup(self.value))

		else:
			widget = revelation.widget.Label(revelation.misc.escape_markup(self.value))
			widget.set_selectable(gtk.TRUE)

		return widget


	def generate_edit_widget(self):
		"Generates a widget for editing the field"

		if type(self) == PasswordField:
			entry = revelation.widget.PasswordEntryGenerate()

		elif self.datatype == DATATYPE_PASSWORD:
			entry = revelation.widget.PasswordEntry()

		else:
			entry = revelation.widget.Entry()

		entry.set_text(self.value)

		return entry



class CardnumberField(Field):

	id		= "creditcard-cardnumber"
	name		= "Card number"
	description	= "The number of a creditcard, usually a 16-digit number"
	symbol		= "N"
	datatype	= DATATYPE_TEXT



class CardtypeField(Field):

	id		= "creditcard-cardtype"
	name		= "Card type"
	description	= "The type of creditcard, like MasterCard or VISA"
	symbol		= "C"
	datatype	= DATATYPE_TEXT



class CCVField(Field):

	id		= "creditcard-ccv"
	name		= "CCV number"
	description	= "A Credit Card Verification number, normally a 3-digit code found on the back of a card"
	symbol		= "V"
	datatype	= DATATYPE_TEXT



class CertificateField(Field):

	id		= "generic-certificate"
	name		= "Certificate"
	description	= "A certificate, such as an X.509 SSL Certificate"
	symbol		= "x"
	datatype	= DATATYPE_TEXT



class CodeField(Field):

	id		= "generic-code"
	name		= "Code"
	description	= "A code used to provide access to something"
	symbol		= "c"
	datatype	= DATATYPE_PASSWORD



class DatabaseField(Field):

	id		= "generic-database"
	name		= "Database"
	description	= "A database name"
	symbol		= "D"
	datatype	= DATATYPE_TEXT



class DomainField(Field):

	id		= "generic-domain"
	name		= "An Internet or logon domain, like amazon.com or a Windows logon domain"
	description	= "A certificate, such as an X.509 SSL Certificate"
	symbol		= "d"
	datatype	= DATATYPE_TEXT



class EmailField(Field):

	id		= "generic-email"
	name		= "Email"
	description	= "An email address"
	symbol		= "e"
	datatype	= DATATYPE_EMAIL



class ExpirydateField(Field):

	id		= "creditcard-expirydate"
	name		= "Expiry date"
	description	= "The month that the credit card validity expires"
	symbol		= "E"
	datatype	= DATATYPE_TEXT



class HostnameField(Field):

	id		= "generic-hostname"
	name		= "Hostname"
	description	= "The name of a computer, like computer.domain.com or MYCOMPUTER"
	symbol		= "h"
	datatype	= DATATYPE_TEXT



class KeyfileField(Field):

	id		= "generic-keyfile"
	name		= "Key File"
	description	= "A key file, used for authentication for example via ssh or to encrypt X.509 certificates"
	symbol		= "f"
	datatype	= DATATYPE_TEXT



class LocationField(Field):

	id		= "generic-location"
	name		= "Location"
	description	= "A physical location, like office entrance"
	symbol		= "L"
	datatype	= DATATYPE_TEXT



class PasswordField(Field):

	id		= "generic-password"
	name		= "Password"
	description	= "A secret word or character combination used for proving you have access"
	symbol		= "p"
	datatype	= DATATYPE_PASSWORD



class PhonenumberField(Field):

	id		= "phone-phonenumber"
	name		= "Phone number"
	description	= "A telephone number"
	symbol		= "n"
	datatype	= DATATYPE_TEXT



class PINField(Field):

	id		= "generic-pin"
	name		= "PIN"
	description	= "A Personal Identification Number, a numeric code used for credit cards, phones etc"
	symbol		= "P"
	datatype	= DATATYPE_PASSWORD



class PortField(Field):

	id		= "generic-port"
	name		= "Port number"
	description	= "A network port number, used to access network services directly"
	symbol		= "o"
	datatype	= DATATYPE_TEXT



class URLField(Field):

	id		= "generic-url"
	name		= "URL"
	description	= "A Uniform Resource Locator, such as a web-site address"
	symbol		= "U"
	datatype	= DATATYPE_URL



class UsernameField(Field):

	id		= "generic-username"
	name		= "Username"
	description	= "A name or other identification used to identify yourself"
	symbol		= "u"
	datatype	= DATATYPE_TEXT




def convert_entry_generic(entry):
	"Converts to a generic account, tries to keep as much data as possible"

	# set up the initial generic entry
	generic = GenericEntry()
	generic.import_data(entry)

	# do direct field copies
	for field in generic:
		if entry.has_field(type(field)):
			field.value = entry.get_field(field.id).value


	# handle special conversions
	field_hostname = generic.get_field(HostnameField)
	field_username = generic.get_field(UsernameField)
	field_password = generic.get_field(PasswordField)

	if type(entry) == CreditcardEntry:
		field_username.value = entry.get_field(CardnumberField.value)
		field_password.value = entry.get_field(PINField).value

	elif type(entry) == CryptoKeyEntry:
		field_username.value = entry.get_field(KeyfileField).value

	elif type(entry) == DatabaseEntry:
		if entry.get_field(DatabaseField).value != "":
			field_hostname.value = entry.get_field(DatabaseField).value + "@" + field_hostname.value

	elif type(entry) == DoorEntry:
		field_password.value = entry.get_field(CodeField).value
		field_hostname.value = entry.get_field(LocationField).value

	elif type(entry) == FTPEntry:
		
		field_hostname.value = "ftp://" + entry.get_field(HostnameField).value

		if entry.get_field(PostField).value != "":
			field_hostname.value += ":" + entry.get_field(PortField).value

	elif type(entry) == PhoneEntry:
		field_username.value = entry.get_field(PhonenumberField).value
		field_password.value = entry.get_field(PINField).value

	elif type(entry) == WebEntry:
		field_hostname.value  = entry.get_field(URLField).value



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

