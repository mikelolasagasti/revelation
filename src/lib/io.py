#
# Revelation 0.3.0 - a password manager for GNOME 2
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

import revelation, gobject, os, os.path


class DetectError(Exception):
	"Error for failed filetype detection"



class DataFile(gobject.GObject):
	"Processes data files"

	def __init__(self, file = None, handler = revelation.datahandler.Revelation, password = None):
		gobject.GObject.__init__(self)

		self.file	= file
		self.password	= password

		if handler is None:
			self.handler = None

		else:
			self.handler = handler()


	def check_file(self):
		"Checks if a file is valid for loading"

		if not file_exists(self.file):
			raise IOError

		data = file_read(self.file, 4096)
		self.handler.check_data(data)


	def detect_type(self):
		"Attempts to find a suitable handler for the file"

		data = file_read(self.file, 4096)

		for handler in revelation.datahandler.get_import_handlers():
			handler = handler()

			if handler.detect_type(data):
				self.handler = handler
				return handler

		raise DetectError


	def load(self):
		"Loads data from a file into an entrystore"

		self.check_file()

		data = file_read(self.file)

		if self.needs_password():
			entrystore = self.handler.import_data(data, self.password)

		else:
			entrystore = self.handler.import_data(data)

		entrystore.set_file(self.file, self.password)

		return entrystore


	def needs_password(self):
		"Checks if the current data handler requires a password"

		return self.handler.encryption


	def save(self, entrystore):
		"Saves data from an entrystore to a file"

		if self.needs_password():
			data = self.handler.export_data(entrystore, self.password)

		else:
			data = self.handler.export_data(entrystore)

		file_write(self.file, data)



def dir_create(dir):
	"Creates a directory, and parents if needed"

	try:
		if dir is None:
			raise IOError

		dir = os.path.abspath(dir)

		if not file_exists(dir):
			os.makedirs(dir)

	except OSError:
		raise IOError


def execute(command, input = None):
	"Runs a command, returns its status code and output"

	p = os.popen(command)

	if input is not None:
		p.write(input)

	output = p.read()
	status = p.close()

	return output, status


def file_exists(file):
	"Checks if a file exists"

	file = os.path.abspath(file)
	return os.access(file, os.F_OK)


def file_read(file, bytes = -1):
	"Reads data from a file"

	if file is None:
		raise IOError

	file = os.path.abspath(file)

	fp = open(file, "rb", 0)
	data = fp.read(bytes)
	fp.close()

	return data


def file_write(file, data):
	"Writes data to a file"

	if file is None:
		raise IOError

	file = os.path.abspath(file)

	# create directory if needed
	dir_create(os.path.dirname(file))

	fp = open(file, "wb", 0)
	fp.write(data)
	fp.flush()
	fp.close()

