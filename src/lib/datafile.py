#
# Revelation 0.3.0 - a password manager for GNOME 2
# $Id$
# http://oss.codepoet.no/revelation/
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

import revelation, gobject, gtk, os

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
				"datahandler"	: revelation.datahandler.FPM,
				"defaultfile"	: "~/.fpm/fpm"
			},

			TYPE_REVELATION	: {
				"name"		: "Revelation",
				"import"	: gtk.TRUE,
				"export"	: gtk.FALSE,
				"datahandler"	: revelation.datahandler.Revelation,
				"defaultfile"	: None
			},

			TYPE_XML : {
				"name"		: "XML (eXtensible Markup Language)",
				"import"	: gtk.TRUE,
				"export"	: gtk.TRUE,
				"datahandler"	: revelation.datahandler.RevelationXML,
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
class DetectError(Exception):
	"""Exception for failed autodetection"""
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

