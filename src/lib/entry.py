#
# Revelation 0.4.7 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing entry information
#
#
# Copyright (c) 2003-2006 Erik Grinaker
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

from revelation import ui

import copy, gettext, time

_ = gettext.gettext


DATATYPE_FILE		= "file"
DATATYPE_EMAIL		= "email"
DATATYPE_PASSWORD	= "password"
DATATYPE_STRING		= "string"
DATATYPE_URL		= "url"



class EntryFieldError(Exception):
	"Exception for invalid entry fields"
	pass


class EntryTypeError(Exception):
	"Exception for invalid entry types"
	pass



class Entry(object):
	"An entry object"

	id		= None
	typename	= ""
	icon		= None

	def __init__(self):
		self.name		= ""
		self.description	= ""
		self.updated		= int(time.time())
		self.fields		= []


	def __getitem__(self, key):
		return self.get_field(key).value


	def __setitem__(self, key, value):
		self.get_field(key).value = value


	def convert_generic(self):
		"Creates a GenericEntry with the data from this entry"

		generic = GenericEntry()
		generic.name = self.name
		generic.description = self.description
		generic.updated = self.updated

		# do direct field copies
		for field in generic.fields:
			if self.has_field(type(field)):
				field.value = self[type(field)]

		# handle special conversions
		if type(self) == CreditcardEntry:
			generic[UsernameField] = self[CardnumberField]
			generic[PasswordField] = self[PINField]

		elif type(self) == CryptoKeyEntry:
			generic[UsernameField] = self[KeyfileField]

		elif type(self) == DatabaseEntry:
			if self[DatabaseField] != "":
				generic[HostnameField] = self[DatabaseField] + "@" + self[HostnameField]

		elif type(self) == DoorEntry:
			generic[PasswordField] = self[CodeField]
			generic[HostnameField] = self[LocationField]

		elif type(self) == FTPEntry:
			if self[PortField] not in ( "", "21" ):
				generic[HostnameField] += ":" + self[PortField]

		elif type(self) == PhoneEntry:
			generic[UsernameField] = self[PhonenumberField]
			generic[PasswordField] = self[PINField]

		elif type(self) == WebEntry:
			generic[HostnameField] = self[URLField]


		return generic


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


	def has_field(self, fieldtype):
		"Check if the entry has a field"

		try:
			self.get_field(fieldtype)
			return True

		except EntryFieldError:
			return False


	def mirror(self, entry):
		"Makes this entry mirror a different entry (same data)"

		if type(self) != type(entry):
			raise EntryTypeError

		self.name		= entry.name
		self.description	= entry.description
		self.updated		= entry.updated

		for field in entry.fields:
			self[type(field)] = field.value



class FolderEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "folder"
		self.typename	= _('Folder')
		self.icon	= ui.STOCK_ENTRY_FOLDER
		self.openicon	= ui.STOCK_ENTRY_FOLDER_OPEN



class CreditcardEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "creditcard"
		self.typename	= _('Creditcard')
		self.icon	= ui.STOCK_ENTRY_CREDITCARD

		self.fields = [
			CardtypeField(),
			CardnumberField(),
			ExpirydateField(),
			CCVField(),
			PINField()
		]



class CryptoKeyEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "cryptokey"
		self.typename	= _('Crypto Key')
		self.icon	= ui.STOCK_ENTRY_CRYPTOKEY

		self.fields = [
			HostnameField(),
			CertificateField(),
			KeyfileField(),
			PasswordField()
		]



class DatabaseEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "database"
		self.typename	= _('Database')
		self.icon	= ui.STOCK_ENTRY_DATABASE

		self.fields = [
			HostnameField(),
			UsernameField(),
			PasswordField(),
			DatabaseField()
		]



class DoorEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "door"
		self.typename	= _('Door lock')
		self.icon	= ui.STOCK_ENTRY_DOOR

		self.fields = [
			LocationField(),
			CodeField()
		]



class EmailEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "email"
		self.typename	= _('Email')
		self.icon	= ui.STOCK_ENTRY_EMAIL

		self.fields = [
			EmailField(),
			HostnameField(),
			UsernameField(),
			PasswordField()
		]



class FTPEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "ftp"
		self.typename	= _('FTP')
		self.icon	= ui.STOCK_ENTRY_FTP

		self.fields = [
			HostnameField(),
			PortField(),
			UsernameField(),
			PasswordField()
		]



class GenericEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "generic"
		self.typename	= _('Generic')
		self.icon	= ui.STOCK_ENTRY_GENERIC

		self.fields = [
			HostnameField(),
			UsernameField(),
			PasswordField()
		]



class PhoneEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "phone"
		self.typename	= _('Phone')
		self.icon	= ui.STOCK_ENTRY_PHONE

		self.fields = [
			PhonenumberField(),
			PINField()
		]



class ShellEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "shell"
		self.typename	= _('Shell')
		self.icon	= ui.STOCK_ENTRY_SHELL

		self.fields = [
			HostnameField(),
			DomainField(),
			UsernameField(),
			PasswordField()
		]



class WebEntry(Entry):

	def __init__(self):
		Entry.__init__(self)

		self.id		= "website"
		self.typename	= _('Website')
		self.icon	= ui.STOCK_ENTRY_WEBSITE

		self.fields = [
			URLField(),
			UsernameField(),
			PasswordField()
		]



ENTRYLIST = [
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



class Field(object):
	"An entry field object"

	id		= None
	name		= ""
	description	= ""
	symbol		= None

	datatype	= None
	value		= None

	def __init__(self, value = ""):
		self.value = value


	def __str__(self):
		return self.value is not None and self.value or ""



class CardnumberField(Field):

	id		= "creditcard-cardnumber"
	name		= _('Card number')
	description	= _('The number of a creditcard, usually a 16-digit number')
	symbol		= "N"
	datatype	= DATATYPE_STRING



class CardtypeField(Field):

	id		= "creditcard-cardtype"
	name		= _('Card type')
	description	= _('The type of creditcard, like MasterCard or VISA')
	symbol		= "C"
	datatype	= DATATYPE_STRING



class CCVField(Field):

	id		= "creditcard-ccv"
	name		= _('CCV number')
	description	= _('A Credit Card Verification number, normally a 3-digit code found on the back of a card')
	symbol		= "V"
	datatype	= DATATYPE_STRING



class CertificateField(Field):

	id		= "generic-certificate"
	name		= _('Certificate')
	description	= _('A certificate, such as an X.509 SSL Certificate')
	symbol		= "x"
	datatype	= DATATYPE_FILE



class CodeField(Field):

	id		= "generic-code"
	name		= _('Code')
	description	= _('A code used to provide access to something')
	symbol		= "c"
	datatype	= DATATYPE_PASSWORD



class DatabaseField(Field):

	id		= "generic-database"
	name		= _('Database')
	description	= _('A database name')
	symbol		= "D"
	datatype	= DATATYPE_STRING



class DomainField(Field):

	id		= "generic-domain"
	name		= _('Domain')
	description	= _('An Internet or logon domain, like organization.org or a Windows logon domain')
	symbol		= "d"
	datatype	= DATATYPE_STRING



class EmailField(Field):

	id		= "generic-email"
	name		= _('Email')
	description	= _('An email address')
	symbol		= "e"
	datatype	= DATATYPE_EMAIL



class ExpirydateField(Field):

	id		= "creditcard-expirydate"
	name		= _('Expiry date')
	description	= _('The month that the credit card validity expires')
	symbol		= "E"
	datatype	= DATATYPE_STRING



class HostnameField(Field):

	id		= "generic-hostname"
	name		= _('Hostname')
	description	= _('The name of a computer, like computer.domain.com or MYCOMPUTER')
	symbol		= "h"
	datatype	= DATATYPE_STRING



class KeyfileField(Field):

	id		= "generic-keyfile"
	name		= _('Key File')
	description	= _('A key file, used for authentication for example via ssh or to encrypt X.509 certificates')
	symbol		= "f"
	datatype	= DATATYPE_FILE



class LocationField(Field):

	id		= "generic-location"
	name		= _('Location')
	description	= _('A physical location, like office entrance')
	symbol		= "L"
	datatype	= DATATYPE_STRING



class PasswordField(Field):

	id		= "generic-password"
	name		= _('Password')
	description	= _('A secret word or character combination used for proving you have access')
	symbol		= "p"
	datatype	= DATATYPE_PASSWORD



class PhonenumberField(Field):

	id		= "phone-phonenumber"
	name		= _('Phone number')
	description	= _('A telephone number')
	symbol		= "n"
	datatype	= DATATYPE_STRING



class PINField(Field):

	id		= "generic-pin"
	name		= _('PIN')
	description	= _('A Personal Identification Number, a numeric code used for credit cards, phones etc')
	symbol		= "P"
	datatype	= DATATYPE_PASSWORD



class PortField(Field):

	id		= "generic-port"
	name		= _('Port number')
	description	= _('A network port number, used to access network services directly')
	symbol		= "o"
	datatype	= DATATYPE_STRING



class URLField(Field):

	id		= "generic-url"
	name		= _('URL')
	description	= _('A Uniform Resource Locator, such as a web-site address')
	symbol		= "U"
	datatype	= DATATYPE_URL



class UsernameField(Field):

	id		= "generic-username"
	name		= _('Username')
	description	= _('A name or other identification used to identify yourself')
	symbol		= "u"
	datatype	= DATATYPE_STRING



FIELDLIST = [
	CardnumberField,
	CardtypeField,
	CCVField,
	CertificateField,
	CodeField,
	DatabaseField,
	DomainField,
	EmailField,
	ExpirydateField,
	HostnameField,
	KeyfileField,
	LocationField,
	PasswordField,
	PhonenumberField,
	PINField,
	PortField,
	URLField,
	UsernameField
]

