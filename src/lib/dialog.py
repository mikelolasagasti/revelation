#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing dialog classes
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

import gtk, gnome.ui, revelation, time, gconf

RESPONSE_NEXT			= 10
RESPONSE_PREVIOUS		= 11


# first we define a few base classes
class Dialog(gtk.Dialog):
	"Base class for dialogs"

	def __init__(self, parent, title, buttons, default = None):
		gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR)

		self.set_border_width(6)
		self.vbox.set_spacing(12)
		self.set_resizable(gtk.FALSE)
		self.connect("key-press-event", self.__cb_keypress)

		for stock, response in buttons:
			self.add_button(stock, response)

		if default is not None:
			self.set_default_response(default)
		else:
			self.set_default_response(buttons[-1][1])


	def __cb_keypress(self, widget, data):
		"Callback for handling keypresses"

		# close the dialog on Escape
		if data.keyval == 65307:
			self.response(gtk.RESPONSE_CLOSE)


	def get_button(self, index):
		"Get one of the dialogs buttons"

		buttons = self.action_area.get_children()

		if index < len(buttons):
			return buttons[index]

		else:
			return None



class Hig(Dialog):
	"A HIG-ified message dialog"

	def __init__(self, parent, pritext, sectext, stockimage, buttons, default = None):
		Dialog.__init__(self, parent, "", buttons, default)

		# hbox separating dialog image and contents
		hbox = revelation.widget.HBox()
		hbox.set_spacing(12)
		hbox.set_border_width(6)
		self.vbox.pack_start(hbox)

		# set up image
		if stockimage is not None:
			image = revelation.widget.Image(stockimage, gtk.ICON_SIZE_DIALOG)
			image.set_alignment(0.5, 0)
			hbox.pack_start(image, gtk.FALSE, gtk.FALSE)

		# set up main content area
		self.contents = revelation.widget.VBox()
		self.contents.set_spacing(10)
		hbox.pack_start(self.contents)

		label = revelation.widget.Label("<span size=\"larger\" weight=\"bold\">" + revelation.misc.escape_markup(pritext) + "</span>\n\n" + sectext)
		label.set_alignment(0, 0)
		self.contents.pack_start(label)


	def run(self):
		"Display the dialog"

		self.show_all()
		response = gtk.Dialog.run(self)
		self.destroy()

		return response



class Property(Dialog):
	"A property dialog"

	def __init__(self, parent, title, buttons, default = None):
		Dialog.__init__(self, parent, title, buttons, default)

		self.set_border_width(12)
		self.vbox.set_spacing(18)

		self.sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.tooltips = gtk.Tooltips()


	def add_section(self, title, description = None):
		"Adds an input section to the dialog"

		section = revelation.widget.InputSection(title, self.sizegroup, description)
		self.vbox.pack_start(section)
		return section




# simple message dialogs
class Error(Hig):
	"Displays an error message"

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_ERROR,
			[ [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)



class FileExportInsecure(Hig):
	"Dialog which warns about exporting to insecure data format"

	def __init__(self, parent):
		Hig.__init__(
			self, parent, "Export to insecure file?",
			"The file format you have chosen is not encrypted. If anyone has access to the file, they will be able to read your passwords.",
			gtk.STOCK_DIALOG_WARNING, [ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_EXPORT, gtk.RESPONSE_OK ] ]
		)


	def run(self):
		"Displays the dialog"

		response = Hig.run(self)

		if response == gtk.RESPONSE_OK:
			return gtk.TRUE

		else:
			raise revelation.CancelError



class FileOverwrite(Hig):
	"Asks for file overwrite confirmation"

	def __init__(self, parent, file):
		Hig.__init__(
			self, parent, "Overwrite existing file?",
			"The file '" + file + "' already exists. If you choose to overwrite the file, its contents will be lost.", gtk.STOCK_DIALOG_WARNING,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_OVERWRITE, gtk.RESPONSE_OK ] ],
			gtk.RESPONSE_CANCEL
		)


	def run(self):
		"Displays the dialog"

		response = Hig.run(self)

		if response == gtk.RESPONSE_OK:
			return gtk.TRUE

		else:
			raise revelation.CancelError



class RemoveEntry(Hig):
	"Asks for confirmation when removing entries"

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_WARNING,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_REMOVE, gtk.RESPONSE_OK ] ],
			gtk.RESPONSE_CANCEL
		)


	def run(self):
		"Displays the dialog"

		return Hig.run(self) == gtk.RESPONSE_OK



class SaveChanges(Hig):
	"Asks the user if she wants to save her changes"

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_WARNING,
			[ [ revelation.stock.STOCK_DISCARD, gtk.RESPONSE_CLOSE ], [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_SAVE, gtk.RESPONSE_OK ] ]
		)


	def run(self):
		"Displays the dialog"

		response = Hig.run(self)

		if response == gtk.RESPONSE_CANCEL:
			raise revelation.CancelError
		else:
			return response == gtk.RESPONSE_OK



# file selectors
class FileSelector(gtk.FileSelection):
	"A normal file selector"

	def __init__(self, parent, title = None):
		gtk.FileSelection.__init__(self, title)

		if parent is not None:
			self.set_transient_for(parent)


	def add_widget(self, title, widget):
		"Adds a widget to the file selector"

		hbox = revelation.widget.HBox()
		self.main_vbox.pack_start(hbox)

		if title is not None:
			hbox.pack_start(revelation.widget.Label(title + ":"), gtk.FALSE, gtk.FALSE)

		hbox.pack_start(widget)


	def run(self):
		"Displays and runs the file selector, returns the filename"

		self.show_all()
		response = gtk.FileSelection.run(self)
		filename = self.get_filename()
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return filename

		else:
			raise revelation.CancelError



class ExportFileSelector(FileSelector):
	"A file selector for exporting files (with a filetype dropdown)"

	def __init__(self, parent):
		FileSelector.__init__(self, parent, "Select File to Export to")

		# set up a filetype dropdown
		self.dropdown = revelation.widget.OptionMenu()
		self.add_widget("Filetype", self.dropdown)

		for handler in revelation.datahandler.get_export_handlers():
			item = gtk.MenuItem(handler.name)
			item.handler = handler
			self.dropdown.append_item(item)


	def run(self):
		"Displays and runs the dialog, returns a filename and file handler tuple"

		self.show_all()
		response = gtk.FileSelection.run(self)
		filename = self.get_filename()
		handler = self.dropdown.get_active_item().handler
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return filename, handler

		else:
			raise revelation.CancelError



class ImportFileSelector(FileSelector):
	"A file selector for importing files (with a filetype dropdown)"

	def __init__(self, parent):
		FileSelector.__init__(self, parent, "Select File to Import")

		# set up a filetype dropdown
		self.dropdown = revelation.widget.OptionMenu()
		self.add_widget("Filetype", self.dropdown)

		item = gtk.MenuItem("Automatically detect")
		item.handler = None
		self.dropdown.append_item(item)

		self.dropdown.append_item(gtk.SeparatorMenuItem())

		for handler in revelation.datahandler.get_import_handlers():
			item = gtk.MenuItem(handler.name)
			item.handler = handler
			self.dropdown.append_item(item)


	def run(self):
		"Displays and runs the dialog, returns a filename and file handler tuple"

		self.show_all()
		response = gtk.FileSelection.run(self)
		filename = self.get_filename()
		handler = self.dropdown.get_active_item().handler
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return filename, handler

		else:
			raise revelation.CancelError
	


# more complex dialogs
class About(gnome.ui.About):
	"An about dialog"

	def __init__(self, parent):
		gnome.ui.About.__init__(
			self, revelation.APPNAME, revelation.VERSION, revelation.COPYRIGHT,
			"\"" + revelation.RELNAME + "\"\n\nRevelation is a password manager for the GNOME 2 desktop.",
			[ revelation.AUTHOR ], None, "",
			gtk.gdk.pixbuf_new_from_file(revelation.DATADIR + "/pixmaps/revelation.png")
		)

		if parent is not None:
			self.set_transient_for(parent)


	def run(self):
		"Displays the dialog"

		self.show_all()



class EditEntry(Property):
	"A dialog for editing entries"

	def __init__(self, parent, title, entry = None):
		Property.__init__(
			self, parent, title,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)

		if entry is not None:
			self.entry = entry.copy()
		else:
			self.entry = revelation.entry.Entry(revelation.entry.ENTRY_ACCOUNT_GENERIC)

		section = self.add_section(title)

		entry = revelation.widget.Entry(self.entry.name)
		entry.set_width_chars(50)
		entry.connect("changed", self.__cb_entry_name_changed)
		self.tooltips.set_tip(entry, "The name of the entry")
		section.add_inputrow("Name", entry)

		entry = revelation.widget.Entry(self.entry.description)
		self.tooltips.set_tip(entry, "A description of the entry")
		entry.connect("changed", self.__cb_entry_description_changed)
		section.add_inputrow("Description", entry)

		self.dropdown = revelation.widget.EntryDropdown()
		self.tooltips.set_tip(self.dropdown, "The type of entry - folders can contain other entries")
		section.add_inputrow("Type", self.dropdown)

		self.dropdown.set_type(self.entry.type)
		self.dropdown.connect("changed", self.__cb_dropdown_changed)

		self.update()


	def __cb_entry_description_changed(self, widget, data = None):
		"Updates the description data"

		self.entry.description = widget.get_text()


	def __cb_entry_name_changed(self, widget, data = None):
		"Updates the name data"

		self.entry.name = widget.get_text()


	def __cb_entry_field_changed(self, widget, id):
		"Updates field data"

		self.entry.set_field(id, widget.get_text())


	def __cb_dropdown_changed(self, object):
		"Updates the entry type data"

		type = self.dropdown.get_active_item().type

		if type != self.entry.type:
			self.entry.set_type(type)
			self.update()


	def run(self):
		"Displays the dialog"

		if Property.run(self) == gtk.RESPONSE_OK:

			if self.entry.name == "":
				Error(self, "No name given", "You need to enter a name for the entry.").run()
				return self.run()

			self.entry.updated = int(time.time())

			self.destroy()
			return self.entry

		else:
			self.destroy()
			raise revelation.CancelError


	def set_typechange_allowed(self, allow):
		"Sets whether to allow type changes"

		self.dropdown.set_sensitive(allow)


	def update(self, type = None):
		"Updates the dialog to a given type"

		if len(self.vbox.get_children()) > 2:
			self.vbox.get_children().pop(1).destroy()

		fields = self.entry.get_fields()

		if len(fields) > 0:
			section = self.add_section("Account data")

		for field in fields:

			if field.type == revelation.entry.FIELD_TYPE_PASSWORD:
				entry = revelation.widget.PasswordEntry()

			else:
				entry = revelation.widget.Entry()

			entry.set_text(field.value)
			entry.connect("changed", self.__cb_entry_field_changed, field.id)
			self.tooltips.set_tip(entry, field.description)

			if field.id == revelation.entry.FIELD_GENERIC_PASSWORD:
				hbox = revelation.widget.HBox()
				section.add_inputrow(field.name, hbox)

				hbox.pack_start(entry)

				button = revelation.widget.Button("Generate", lambda w: entry.set_text(revelation.misc.generate_password()))
				hbox.pack_start(button, gtk.FALSE, gtk.FALSE)


			else:
				section.add_inputrow(field.name, entry)

		self.show_all()



class Find(Property):
	"A dialog for searching for entries"

	def __init__(self, parent, config):
		Property.__init__(
			self, parent, "Find an entry",
			[ [ gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ], [ revelation.stock.STOCK_PREVIOUS, RESPONSE_PREVIOUS ], [ revelation.stock.STOCK_NEXT, RESPONSE_NEXT ] ]
		)

		self.config = config

		section = self.add_section("Find an entry")

		# the search string entry
		self.entry_phrase = revelation.widget.Entry()
		self.tooltips.set_tip(self.entry_phrase, "The text to search for")
		self.entry_phrase.connect("changed", self.__cb_entry_changed)
		section.add_inputrow("Search for", self.entry_phrase)

		# the account type dropdown
		self.dropdown = revelation.widget.EntryDropdown()
		self.tooltips.set_tip(self.dropdown, "The account type to search for")
		item = self.dropdown.get_item(0)
		item.set_stock("gnome-stock-about")
		item.set_text("Any")
		item.type = None
		section.add_inputrow("Account type", self.dropdown)

		# folder search checkbutton
		check = revelation.widget.CheckButton("Search for folders as well")
		self.tooltips.set_tip(check, "When enabled, folder names and descriptions will also be searched")
		self.config.bind_widget("search/folders", check)
		section.add_inputrow(None, check)

		check = revelation.widget.CheckButton("Only search in name and description")
		self.tooltips.set_tip(check, "When enabled, only entry names and descriptions will be searched")
		self.config.bind_widget("search/namedesc", check)
		section.add_inputrow(None, check)

		check = revelation.widget.CheckButton("Case sensitive")
		self.tooltips.set_tip(check, "When enabled, searches will be case sensitive")
		self.config.bind_widget("search/casesens", check)
		section.add_inputrow(None, check)

		# set up initial states
		self.entry_phrase.emit("changed")


	def __cb_entry_changed(self, widget, data = None):
		"Sets the Find button sensitivity based on entry contents"

		active = len(self.entry_phrase.get_text()) > 0
		self.get_button(0).set_sensitive(active)
		self.get_button(1).set_sensitive(active)


	def run(self):
		"Displays the dialog"

		self.show_all()
		return Property.run(self)



class Password(Hig):
	"A dialog which asks for passwords"

	def __init__(self, parent, title, text, current = gtk.TRUE, new = gtk.FALSE):
		Hig.__init__(
			self, parent, title, text, revelation.stock.STOCK_PASSWORD,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)

		self.entry_password = None
		self.entry_new = None
		self.entry_confirm = None

		section = revelation.widget.InputSection()
		self.contents.pack_start(section)

		if current == gtk.TRUE or new == gtk.FALSE:
			self.entry_password = revelation.widget.Entry()
			self.entry_password.set_visibility(gtk.FALSE)
			self.entry_password.connect("changed", self.__cb_entry_changed)
			section.add_inputrow("Password", self.entry_password)

		if new == gtk.TRUE:
			self.entry_new = revelation.widget.Entry()
			self.entry_new.set_visibility(gtk.FALSE)
			self.entry_new.connect("changed", self.__cb_entry_changed)
			section.add_inputrow("New password", self.entry_new)

			self.entry_confirm = revelation.widget.Entry()
			self.entry_confirm.set_visibility(gtk.FALSE)
			self.entry_confirm.connect("changed", self.__cb_entry_changed)
			section.add_inputrow("Confirm new", self.entry_confirm)

		self.get_button(0).set_sensitive(gtk.FALSE)


	def __cb_entry_changed(self, widget, data = None):
		"Sets the OK button sensitivity based on the entries"

		if (
			(self.entry_password is None or self.entry_password.get_text() != "")
			and (self.entry_new is None or self.entry_new.get_text() != "")
			and (self.entry_confirm is None or self.entry_confirm.get_text() != "")
		):
			self.get_button(0).set_sensitive(gtk.TRUE)
		else:
			self.get_button(0).set_sensitive(gtk.FALSE)


	def run(self):
		"Displays the dialog"

		while 1:
			self.show_all()

			if self.entry_password is not None:
				self.entry_password.grab_focus()

			elif self.entry_new is not None:
				self.entry_new.grab_focus()

			if Dialog.run(self) == gtk.RESPONSE_OK:

				if self.entry_new is not None and self.entry_new.get_text() != self.entry_confirm.get_text():
					Error(self, "Passwords don't match", "The password and password confirmation you entered does not match.").run()

				else:
					break

			else:
				raise revelation.CancelError



class Preferences(Property):
	"The preference dialog"

	def __init__(self, parent, config):
		Property.__init__(self, parent, "Preferences", [ [ gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ] ])
		self.config = config

		self.__init_section_file()
		self.__init_section_pwgen()


	def __init_section_file(self):
		"Sets up the file section"

		self.section_file = self.add_section("File Handling")

		# check-button for autoloading a file
		self.check_autoload = revelation.widget.CheckButton("Open file on startup")
		self.section_file.add_inputrow(None, self.check_autoload)

		self.config.bind_widget("file/autoload", self.check_autoload)
		self.tooltips.set_tip(self.check_autoload, "When enabled, a file will be opened when the program is started")


		# entry for file to autoload
		self.entry_autoload_file = revelation.widget.FileEntry("Select File to Automatically Open")
		self.entry_autoload_file.set_sensitive(self.check_autoload.get_active())
		self.section_file.add_inputrow("File to open", self.entry_autoload_file)

		self.config.bind_widget("file/autoload_file", self.entry_autoload_file)
		self.tooltips.set_tip(self.entry_autoload_file, "A file to be opened when the program is started")


		# check-button for autosave
		self.check_autosave = revelation.widget.CheckButton("Autosave data when changed")
		self.section_file.add_inputrow(None, self.check_autosave)

		self.tooltips.set_tip(self.check_autosave, "Automatically saves the data file when an entry is added, modified or removed")
		self.config.bind_widget("file/autosave", self.check_autosave)


		self.check_autoload.connect("toggled", self.__cb_autoload)


	def __init_section_pwgen(self):
		"Sets up the password generator section"

		self.section_pwgen = self.add_section("Password Generator")

		# password length spinbutton
		self.spin_pwlen = revelation.widget.SpinButton()
		self.spin_pwlen.set_range(4, 32)
		self.section_pwgen.add_inputrow("Password length", self.spin_pwlen)

		self.config.bind_widget("passwordgen/length", self.spin_pwlen)
		self.tooltips.set_tip(self.spin_pwlen, "The number of characters in generated passwords - 8 or more are recommended")


		# checkbox for avoiding ambiguous characters in password
		self.check_ambiguous = revelation.widget.CheckButton("Avoid ambiguous characters")
		self.section_pwgen.add_inputrow(None, self.check_ambiguous)

		self.tooltips.set_tip(self.check_ambiguous, "When enabled, generated passwords will not contain ambiguous characters - like 0 (zero) and O (capital o)")
		self.config.bind_widget("passwordgen/avoid_ambiguous", self.check_ambiguous)


	def __cb_autoload(self, widget, data = None):
		"Sets the autoload file entry sensitivity based on the autoload checkbutton state"

		self.entry_autoload_file.set_sensitive(self.check_autoload.get_active())


	def run(self):
		"Runs the preference dialog"

		self.show_all()
		Property.run(self)
		self.destroy()

