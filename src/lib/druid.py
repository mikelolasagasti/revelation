#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing druid classes
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

import gtk, gnome.ui, revelation, os

class Page(gnome.ui.DruidPageStandard):

	def __init__(self, title, logo = None):
		gnome.ui.DruidPageStandard.__init__(self)
		self.set_title(title)

		if logo == None:
			logo = self.render_icon(revelation.stock.STOCK_APPLICATION, revelation.stock.ICON_SIZE_DRUID)

		self.set_logo(logo)


	def append_item(self, text, widget, extratext = None):
		vbox = gtk.VBox()
		vbox.set_spacing(18)
		vbox.set_border_width(6)
		gnome.ui.DruidPageStandard.append_item(self, "", vbox, "")

		if text != None:
			vbox.pack_start(revelation.widget.Label(text, gtk.JUSTIFY_CENTER))

		vbox.pack_start(widget, gtk.FALSE, gtk.FALSE)

		if extratext != None:
			vbox.pack_start(revelation.widget.Label("<span size=\"small\">" + extratext + "</span>", gtk.JUSTIFY_CENTER))



class PageEdge(gnome.ui.DruidPageEdge):

	def __init__(self, position, title, text = None, logo = None):
		gnome.ui.DruidPageEdge.__init__(self, position)
		self.set_title(title)
		self.pagepos = position

		if text != None:
			self.set_text(text)

		if logo == None:
			logo = self.render_icon(revelation.stock.STOCK_APPLICATION, revelation.stock.ICON_SIZE_DRUID, None)

		self.set_logo(logo)



class Druid(gnome.ui.Druid):

	def __init__(self, parent, title):
		gnome.ui.Druid.__init__(self)
		self.connect("cancel", self.__cb_cancel)

		self.dialog = gtk.Dialog(title, parent, (gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR))
		self.dialog.action_area.destroy()
		self.dialog.vbox.pack_start(self)


	def __cb_cancel(self, object):
		self.dialog.response(gtk.RESPONSE_CANCEL)

	def __cb_finish(self, object, data):
		self.dialog.response(gtk.RESPONSE_OK)

	def __cb_destroy_page(self, page, data):
		page.destroy()


	def append_page(self, page):
		if hasattr(page, "pagepos") and page.pagepos == gnome.ui.EDGE_FINISH:
			page.connect("finish", self.__cb_finish)
		gnome.ui.Druid.append_page(self, page)


	def insert_page(self, prevpage, page):
		gnome.ui.Druid.insert_page(self, prevpage, page)
		page.connect("back", self.__cb_destroy_page)
		page.show_all()


	def run(self):
		self.dialog.show_all()
		response = self.dialog.run()
		self.destroy()
		self.dialog.destroy()

		return response



class ExportFile(Druid):

	def __init__(self, parent):
		Druid.__init__(self, parent, "Export File")
		self.filetypes = revelation.datafile.FileTypes()
		self.datafile = revelation.datafile.DataFile()

		self.append_page(self.__page_start())
		self.append_page(self.__page_file())
		self.append_page(self.__page_finish())


	def __page_file(self):
		page = Page("Select File to Export to")
		page.connect("next", self.__cb_page_file)

		section = revelation.widget.InputSection()
		page.append_item("Select the file you wish to export data to, and the file type:", section)

		page.entry_file = revelation.widget.FileEntry("Select File to Export to")
		section.add_inputrow("File", page.entry_file)

		page.dropdown = revelation.widget.OptionMenu()
		section.add_inputrow("Filetype", page.dropdown)

		for type in self.filetypes.get_export_types():
			item = gtk.MenuItem(self.filetypes.get_data(type, "name"))
			item.filetype = type
			page.dropdown.append_item(item)

		page.dropdown.connect("changed", self.__cb_filetype_changed, page.entry_file)

		return page


	def __page_start(self):
		return PageEdge(gnome.ui.EDGE_START, "File Export Assistant", "Welcome to the Revelation file export assistant, which will guide you through exporting accounts into a foreign file format.")


	def __page_finish(self):
		return PageEdge(gnome.ui.EDGE_FINISH, "Export File", "You have now provided all information needed to export the data. Press \"Apply\" to start the export.")


	def __page_password(self):
		page = Page("Enter Password")
		page.connect("next", self.__cb_page_password)

		section = revelation.widget.InputSection()
		page.append_item("Please enter a password to encrypt the file with:", section)

		page.entry_password = revelation.widget.Entry()
		page.entry_confirm = revelation.widget.Entry()

		for entry, name in zip((page.entry_password, page.entry_confirm), ("Password", "Confirm password")):
			entry.set_visibility(gtk.FALSE)
			entry.set_text(self.datafile.password)
			section.add_inputrow(name, entry)

		return page


	def __cb_filetype_changed(self, dropdown, entry):
		type = dropdown.get_active_item().filetype
		default = self.filetypes.get_data(type, "defaultfile")

		if default != None and entry.gtk_entry().get_text() == "":
			entry.set_filename(default)


	def __cb_page_file(self, page, data):
		self.datafile.type = page.dropdown.get_active_item().filetype
		file = page.entry_file.get_filename()

		if file == None:
			revelation.dialog.Error(self.dialog, "Filename not entered", "You need to enter a file to export the data to.").run()
			return gtk.TRUE

		if os.access(file, os.F_OK) == 1 and revelation.dialog.FileOverwrite(self.dialog, file).run() == gtk.FALSE:
			return gtk.TRUE

		self.datafile.file = file

		# check if file format is insecure
		if not hasattr(self.datafile, "password"):
			if revelation.dialog.Hig(
				self.dialog, "Export to insecure file?", "The file format you have chosen is not encrypted. If anyone has access to the file, they will be able to read your passwords.",
				gtk.STOCK_DIALOG_WARNING, [ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_EXPORT, gtk.RESPONSE_OK ] ]
			).run() == gtk.RESPONSE_CANCEL:
				return gtk.TRUE

		else:
			# set up password page if a password is needed
			self.insert_page(page, self.__page_password())


	def __cb_page_password(self, page, data):

		# fetch passwords
		password = page.entry_password.get_text()
		confirm = page.entry_confirm.get_text()

		if len(password) == 0:
			revelation.dialog.Error(self.dialog, "No password given", "You must enter a password to encrypt the file with.").run()
			return gtk.TRUE

		if password != confirm:
			revelation.dialog.Error(self.dialog, "Passwords don't match", "The passwords you entered do not match each other. Make sure that you enter the same password in both input fields.").run()
			return gtk.TRUE

		self.datafile.password = password


	def run(self):
		if Druid.run(self) == gtk.RESPONSE_OK:
			return self.datafile
		else:
			raise revelation.CancelError



class ImportFile(Druid):

	def __init__(self, parent):
		Druid.__init__(self, parent, "Import File")
		self.datafile = revelation.datafile.DataFile()

		self.append_page(self.__page_start())
		self.append_page(self.__page_file())
		self.append_page(self.__page_finish())


	def __page_file(self):
		page = Page("Select File to Import")
		page.connect("next", self.__cb_page_file)

		section = revelation.widget.InputSection()
		page.append_item("Select the file you wish to import, and the type of file:", section, "You can select \"Autodetect\" to make Revelation attempt to find the filetype itself.")

		page.entry_file = revelation.widget.FileEntry("Select File to Import")
		section.add_inputrow("File", page.entry_file)

		page.dropdown = revelation.widget.OptionMenu()
		section.add_inputrow("Filetype", page.dropdown)

		item = gtk.MenuItem("Autodetect")
		item.handler = None
		page.dropdown.append_item(item)

		page.dropdown.append_item(gtk.SeparatorMenuItem())

		for handler in revelation.datahandler.get_import_handlers():
			item = gtk.MenuItem(handler.name)
			item.handler = handler
			page.dropdown.append_item(item)

		return page


	def __page_finish(self):
		return PageEdge(gnome.ui.EDGE_FINISH, "Import File", "You have now provided all required information to import the data. Press \"Apply\" to start the import.")


	def __page_password(self):
		page = Page("Enter Password")
		page.connect("next", self.__cb_page_password)

		section = revelation.widget.InputSection()
		page.append_item("This file is encrypted - please enter a password to decrypt it:", section)

		page.entry_password = revelation.widget.Entry()
		page.entry_password.set_visibility(gtk.FALSE)
		section.add_inputrow("Password", page.entry_password)

		if self.datafile.password != None:
			page.entry_password.set_text(self.datafile.password)

		return page


	def __page_start(self):
		return PageEdge(gnome.ui.EDGE_START, "File Import Assistant", "Welcome to the Revelation file import assistant, which will guide you through importing accounts from other password managers.")


	# callbacks
	def __cb_page_file(self, page, widget):
		try:
			self.datafile.file = page.entry_file.get_filename()
			self.datafile.check_file()

			type = page.dropdown.get_active_item().filetype

			if type == revelation.datafile.TYPE_AUTO:
				self.datafile.detect_type()
			else:
				self.datafile.type = type

			self.datafile.check_format()

		except IOError:
			revelation.dialog.Error(self.dialog, "Unable to open file", "The file you selected could not be opened. Please make sure the file exists, and that you have the proper permissions to open it.").run()
			return gtk.TRUE

		except revelation.datahandler.FormatError:
			revelation.dialog.Error(self.dialog, "Invalid file format", "The file '" + self.datafile.file + "' is not a valid " + self.filetypes.get_data(self.datafile.type, "name") + " file.").run()
			return gtk.TRUE

		except revelation.datahandler.VersionError:
			revelation.dialog.Error(self.dialog, "Future file version", "The file '" + self.datafile.file + "' is from an unknown version. Please upgrade Revelation to a newer version to import it.").run()
			return gtk.TRUE

		except revelation.datafile.DetectError:
			revelation.dialog.Error(self.dialog, "Autodetection failed", "Revelation was not able to autodetect the format of the file '" + self.datafile.file + "'. It may still be able to load the file, try specifying the file type manually.").run()
			return gtk.TRUE

		# set up password page if needed
		if hasattr(self.datafile, "password"):
			self.insert_page(page, self.__page_password())


	def __cb_page_password(self, page, widget):
		password = page.entry_password.get_text()

		if len(password) > 0:
			self.datafile.password = password
		else:
			revelation.dialog.Error(self.dialog, "No password given", "You must enter a password to decrypt the file.").run()
			return gtk.TRUE


	def run(self):
		if Druid.run(self) == gtk.RESPONSE_OK:
			return self.datafile
		else:
			raise revelation.CancelError

