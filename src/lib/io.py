#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for IO-related functionality
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

import gobject, gnome.vfs, os.path, re



class DataFile(gobject.GObject):
	"Handles data files"

	def __init__(self, handler):
		gobject.GObject.__init__(self)

		self.__uri		= None
		self.__handler		= None
		self.__password		= None

		self.set_handler(handler)


	def __str__(self):
		return self.get_file() or ""


	def close(self):
		"Closes the current file"

		self.set_password(None)
		self.set_file(None)


	def get_file(self):
		"Gets the current file"

		return self.__uri and re.sub("^file://", "", str(self.__uri)) or None


	def get_handler(self):
		"Gets the current handler"

		return self.__handler


	def get_password(self):
		"Gets the current password"

		return self.__password


	def load(self, file, password = None, pwgetter = None):
		"Loads a file"

		file = file_normpath(file)
		data = file_read(file)

		if self.__handler.encryption == True and password is None:
			password = pwgetter()

		entrystore = self.__handler.import_data(data, password)

		self.set_password(password)
		self.set_file(file)

		return entrystore


	def save(self, entrystore, file, password = None):
		"Saves an entrystore to a file"

		file_write(file, self.__handler.export_data(entrystore, password))

		self.set_password(password)
		self.set_file(file)


	def set_file(self, file):
		"Sets the current file"

		if file is None:
			uri = None

		else:
			uri = gnome.vfs.URI(file_normpath(file))


		if self.__uri != uri:
			self.__uri = uri
			self.emit("changed", file)


	def set_handler(self, handler):
		"Sets and initializes the current data handler"

		self.__handler = handler is not None and handler() or None


	def set_password(self, password):
		"Sets the password for the current file"

		self.__password = password


gobject.type_register(DataFile)
gobject.signal_new("changed", DataFile, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (str,))



def file_exists(file):
	"Checks if a file exists"

	if file is None:
		return False

	return gnome.vfs.exists(file)


def file_is_local(file):
	"Checks if a file is on a local filesystem"

	if file is None:
		return False

	uri = gnome.vfs.URI(file)

	return uri.is_local


def file_normpath(file):
	"Normalizes a file path"

	if file in ( None, "" ):
		return None

	file = re.sub("^file:/{,2}", "", file)

	if not re.match("^[a-zA-Z]+://", file) and file[0] != "/":
		file = os.path.abspath(file)

	return re.sub("^file:/{,2}", "", str(gnome.vfs.URI(file)))


def file_read(file):
	"Reads data from a file"

	if file is None:
		raise IOError

	try:
		return gnome.vfs.read_entire_file(file)

	except ( gnome.vfs.AccessDeniedError, gnome.vfs.NotFoundError ):
		raise IOError


def file_write(file, data):
	"Writes data to file"

	if file is None:
		raise IOError

	if data is None:
		data = ""


	try:
		f = gnome.vfs.create(file, gnome.vfs.OPEN_WRITE)
		f.write(data)
		f.close()

	except gnome.vfs.AccessDeniedError:
		raise IOError

