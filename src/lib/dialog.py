#
# Revelation 0.3.3 - a password manager for GNOME 2
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

import gtk, gnome.ui, revelation, time, gconf, pango

RESPONSE_NEXT			= 10
RESPONSE_PREVIOUS		= 11


# first we define a few base classes
class Dialog(gtk.Dialog):
	"Base class for dialogs"

	def __init__(self, parent, title, buttons, default = None):
		gtk.Dialog.__init__(
			self, title, parent,
			gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR
		)

		self.set_border_width(6)
		self.vbox.set_spacing(12)
		self.set_resizable(gtk.FALSE)
		self.connect("key_press_event", self.__cb_keypress)

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



class FileChanged(Hig):
	"Asks the user if she wants to save her changes"

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_WARNING,
			[ [ revelation.stock.STOCK_DISCARD, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE ], [ gtk.STOCK_SAVE, gtk.RESPONSE_OK ] ]
		)


	def run(self):
		"Displays the dialog"

		response = Hig.run(self)

		# Cancel == RESPONSE_CLOSE, Discard == RESPONSE_CANCEL (in order to have
		# Escape etc trigger Cancel instead of Discard)
		if response == gtk.RESPONSE_OK:
			return gtk.TRUE

		elif response == gtk.RESPONSE_CANCEL:
			return gtk.FALSE

		else:
			raise revelation.CancelError



class FileChangedNew(FileChanged):
	"Asks the user to save changes when creating a new file"

	def __init__(self, parent):
		FileChanged.__init__(
			self, parent, "Save changes to current file?",
			"You have made changes which have not been saved. If you create a new file without saving then these changes will be lost."
		)



class FileChangedOpen(FileChanged):
	"Asks the user to save changes when opening a different file"

	def __init__(self, parent):
		FileChanged.__init__(
			self, parent, "Save changes before opening?",
			"You have made changes which have not been saved. If you open a different file without saving then these changes will be lost."
		)



class FileChangedQuit(FileChanged):
	"Asks the user to save changes when quitting"

	def __init__(self, parent):
		FileChanged.__init__(
			self, parent, "Save changes before quitting?",
			"You have made changes which have not been saved. If you quit without saving, then these changes will be lost."
		)



class FileChangedRevert(Hig):
	"Alerts the user about unsaved changes when reverting"

	def __init__(self, parent):
		Hig.__init__(
			self, parent, "Ignore unsaved changes?",
			"You have made changes which have not yet been saved. If you revert to the saved file then these changes will be lost.",
			gtk.STOCK_DIALOG_WARNING, [ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_REVERT_TO_SAVED, gtk.RESPONSE_OK ] ], 0
		)


	def run(self):
		"Displays the dialog, emulates the return codes of the FileChanged dialog"

		response = Hig.run(self)

		if response == gtk.RESPONSE_OK:
			return gtk.FALSE

		else:
			raise revelation.CancelError



class FileExportInsecure(Hig):
	"Dialog which warns about exporting to insecure data format"

	def __init__(self, parent):
		Hig.__init__(
			self, parent, "Export to insecure file?",
			"The file format you have chosen is not encrypted. If anyone has access to the file, they will be able to read your passwords.",
			gtk.STOCK_DIALOG_WARNING, [ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_EXPORT, gtk.RESPONSE_OK ] ], 0
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



# file selectors
class FileSelector(gtk.FileChooserDialog):
	"A normal file selector"

	def __init__(self, parent, title = None, action = gtk.FILE_CHOOSER_ACTION_OPEN, stockbutton = None):

		if stockbutton is None:
			if action == gtk.FILE_CHOOSER_ACTION_OPEN:
				stockbutton = gtk.STOCK_OPEN

			elif action == gtk.FILE_CHOOSER_ACTION_SAVE:
				stockbutton = gtk.STOCK_SAVE


		gtk.FileChooserDialog.__init__(
			self, title, parent, action,
			( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, stockbutton, gtk.RESPONSE_OK)
		)


	def add_widget(self, title, widget):
		"Adds a widget to the file selector"

		hbox = revelation.widget.HBox()
		self.set_extra_widget(hbox)

		if title is not None:
			hbox.pack_start(revelation.widget.Label(title + ":"), gtk.FALSE, gtk.FALSE)

		hbox.pack_start(widget)


	def run(self):
		"Displays and runs the file selector, returns the filename"

		self.show_all()
		response = gtk.FileChooserDialog.run(self)
		filename = self.get_filename()
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return filename

		else:
			raise revelation.CancelError



class ExportFileSelector(FileSelector):
	"A file selector for exporting files (with a filetype dropdown)"

	def __init__(self, parent):
		FileSelector.__init__(
			self, parent, "Select File to Export to",
			gtk.FILE_CHOOSER_ACTION_SAVE, revelation.stock.STOCK_EXPORT
		)

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
		FileSelector.__init__(
			self, parent, "Select File to Import",
			gtk.FILE_CHOOSER_ACTION_OPEN, revelation.stock.STOCK_IMPORT
		)

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



class OpenFileSelector(FileSelector):
	"A file selector for opening files"

	def __init__(self, parent):
		FileSelector.__init__(
			self, parent, "Select File to Open",
			gtk.FILE_CHOOSER_ACTION_OPEN, gtk.STOCK_OPEN
		)



class SaveFileSelector(FileSelector):
	"A file selector for saving files"

	def __init__(self, parent):
		FileSelector.__init__(
			self, parent, "Select File to Save to",
			gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
		)



# entry-related dialogs

class EntryEdit(Property):
	"A dialog for editing entries"

	def __init__(self, parent, title, entry = None):
		Property.__init__(
			self, parent, title,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)

		if entry is not None:
			self.entry = entry.copy()

		else:
			self.entry = revelation.entry.GenericEntry()

		self.sect_meta		= self.add_section(title)
		self.sect_fields	= None
		self.entry_field	= {}
		self.oldfields		= {}

		# entry name input
		self.entry_name = revelation.widget.Entry(self.entry.name)
		self.entry_name.set_width_chars(50)
		self.tooltips.set_tip(self.entry_name, "The name of the entry")
		self.sect_meta.add_inputrow("Name", self.entry_name)

		# entry description input
		self.entry_desc = revelation.widget.Entry(self.entry.description)
		self.tooltips.set_tip(self.entry_desc, "A description of the entry")
		self.sect_meta.add_inputrow("Description", self.entry_desc)

		# entry type dropdown
		self.dropdown = revelation.widget.EntryDropdown()
		self.tooltips.set_tip(self.dropdown, "The type of entry - folders can contain other entries")
		self.sect_meta.add_inputrow("Type", self.dropdown)

		self.dropdown.connect("changed", self.__cb_dropdown_changed)
		self.dropdown.set_type(type(self.entry))


	def __cb_dropdown_changed(self, object):
		"Updates the entry type"

		entrytype = self.dropdown.get_active_item().type

		if entrytype == type(self.entry) and self.sect_fields is not None:
			return

		# store current field values
		for field in self.entry.fields:
			self.oldfields[field.id] = field.value

		# convert the entry type
		oldentry = self.entry
		self.entry = entrytype()
		self.entry.import_data(oldentry)

		# restore any old field values
		for field in self.entry.fields:
			if self.oldfields.has_key(field.id):
				field.value = self.oldfields[field.id]

		# set up input entries
		self.entry_field = {}

		if self.sect_fields is not None:
			self.sect_fields.destroy()
			self.sect_fields = None

		if len(self.entry.fields) > 0:
			self.sect_fields = self.add_section("Account data")
			self.sect_fields.type = entrytype

		for field in self.entry.fields:
			entry = field.generate_edit_widget()
			self.tooltips.set_tip(entry, field.description)

			self.entry_field[field.id] = entry
			self.sect_fields.add_inputrow(field.name, entry)

		self.show_all()


	def run(self):
		"Displays the dialog"

		self.show_all()

		if Property.run(self) == gtk.RESPONSE_OK:

			if self.entry_name.get_text() == "":
				Error(self, "No name given", "You need to enter a name for the entry.").run()
				return self.run()

			self.entry.name = self.entry_name.get_text()
			self.entry.description = self.entry_desc.get_text()
			self.entry.updated = int(time.time())

			for id, entry in self.entry_field.items():
				self.entry.lookup_field(id).value = entry.get_text()

			self.destroy()
			return self.entry

		else:
			self.destroy()
			raise revelation.CancelError


	def set_typechange_allowed(self, allow):
		"Sets whether to allow type changes"

		self.dropdown.set_sensitive(allow)



class EntryRemove(Hig):
	"Asks for confirmation when removing entries"

	def __init__(self, parent, entries):

		if len(entries) > 1:
			pritext = "Really remove the " + str(len(entries)) + " selected entries?"
			sectext = "By removing these entries you will also remove any entries they may contain."

		elif type(entries[0]) == revelation.entry.FolderEntry:
			pritext = "Really remove folder '" + entries[0].name + "'?"
			sectext = "By removing this folder you will also remove all accounts and folders it contains."

		else:
			pritext = "Really remove account '" + entries[0].name + "'?"
			sectext = "Please confirm that you wish to remove this account."


		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_WARNING,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_REMOVE, gtk.RESPONSE_OK ] ],
			gtk.RESPONSE_CANCEL
		)


	def run(self):
		"Displays the dialog"

		if Hig.run(self) == gtk.RESPONSE_OK:
			return gtk.TRUE

		else:
			raise revelation.CancelError



# password entry dialogs

class Password(Hig):
	"A base dialog for asking for passwords"

	def __init__(self, parent, title, text, stock = gtk.STOCK_OK):
		Hig.__init__(
			self, parent, title, text, gtk.STOCK_DIALOG_AUTHENTICATION,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ stock, gtk.RESPONSE_OK ] ]
		)

		self.entries = []

		self.sect_passwords = revelation.widget.InputSection()
		self.contents.pack_start(self.sect_passwords)

		self.set_default_size(300, -1)
		self.get_button(0).set_sensitive(gtk.FALSE)


	def __cb_entry_changed(self, widget, data = None):
		"Sets the OK button sensitivity based on the entries"

		for entry in self.entries:
			if entry.get_text() == "":
				self.get_button(0).set_sensitive(gtk.FALSE)
				break

		else:
			self.get_button(0).set_sensitive(gtk.TRUE)


	def add_entry(self, name):
		"Adds a password entry to the dialog"

		entry = revelation.widget.Entry()
		entry.set_visibility(gtk.FALSE)
		entry.set_max_length(32)
		entry.connect("changed", self.__cb_entry_changed)
		self.sect_passwords.add_inputrow(name, entry)

		self.entries.append(entry)

		return entry


	def run(self):
		"Displays the dialog"

		self.show_all()

		if len(self.entries) > 0:
			self.entries[0].grab_focus()

		if gtk.Dialog.run(self) == gtk.RESPONSE_OK:
			return gtk.RESPONSE_OK

		else:
			raise revelation.CancelError



class PasswordChange(Password):
	"Lets the user change a password"

	def __init__(self, parent, password = None):
		Password.__init__(
			self, parent, "Enter new password",
			"Enter a new password for the current data file. The file must be saved before the new password is applied.",
			revelation.stock.STOCK_PASSWORD_CHANGE
		)

		self.password = password

		if password is not None:	
			self.entry_current = self.add_entry("Current password")

		self.entry_new = self.add_entry("New password")
		self.entry_confirm = self.add_entry("Confirm password")


	def run(self):
		"Displays the dialog"

		while 1:
			if Password.run(self) == gtk.RESPONSE_OK:
				if self.password is not None and self.entry_current.get_text() != self.password:
					Error(self, "Incorrect password", "The password you entered as the current file password is incorrect.").run()

				elif self.entry_new.get_text() != self.entry_confirm.get_text():
					Error(self, "Passwords don't match", "The password and password confirmation you entered does not match.").run()

				else:
					return self.entry_new.get_text()



class PasswordLoad(Password):
	"Asks for a password when opening a file"

	def __init__(self, parent, filename):
		Password.__init__(
			self, parent, "Enter file password",
			"The file '" + filename + "' is encrypted. Please enter the file password to open it."
		)

		self.entry_password = self.add_entry("Password")


	def run(self):
		"Displays the dialog"

		if Password.run(self) == gtk.RESPONSE_OK:
			return self.entry_password.get_text()



class PasswordLock(Password):
	"Asks for a password when a file is locked"

	def __init__(self, parent):
		Password.__init__(
			self, parent, "Enter password to unlock file",
			"The current file has been locked. Please enter the file password to unlock it."
		)

		self.entry_password = self.add_entry("Password")

		self.get_button(1).destroy()


	def run(self):
		"Displays the dialog"

		try:
			if Password.run(self) == gtk.RESPONSE_OK:
				return self.entry_password.get_text()

		# do not respect cancel errors etc
		except revelation.CancelError:
			pass



class PasswordSave(Password):
	"Asks for a new password when saving a file"

	def __init__(self, parent, filename):
		Password.__init__(
			self, parent, "Enter new file password",
			"Please enter a new password for the file '" + filename + "'. You will need this password to open the file at a later time."
		)

		self.entry_new = self.add_entry("New password")
		self.entry_confirm = self.add_entry("Confirm password")


	def run(self):
		"Displays the dialog"

		while 1:
			if Password.run(self) != gtk.RESPONSE_OK:
				continue

			if self.entry_new.get_text() != self.entry_confirm.get_text():
				Error(self, "Passwords don't match", "The password and password confirmation you entered does not match.").run()

			else:
				return self.entry_new.get_text()



# other dialogs
class About(gnome.ui.About):
	"An about dialog"

	def __init__(self, parent):
		gnome.ui.About.__init__(
			self, revelation.APPNAME, revelation.VERSION, revelation.COPYRIGHT,
			"\"" + revelation.RELNAME + "\"\n\nRevelation is a password manager for the GNOME 2 desktop.",
			[ revelation.AUTHOR ], None, "",
			gtk.icon_theme_get_default().load_icon("revelation", 48, 0)
		)

		if parent is not None:
			self.set_transient_for(parent)


	def run(self):
		"Displays the dialog"

		self.show_all()



class Exception(Hig):
	"A dialog for displaying unhandled errors (exceptions)"

	def __init__(self, parent, traceback):
		Hig.__init__(
			self, parent, "Unknown error",
			"An unknown error occured. Please report the text below to the Revelation developers, along with what you were doing that may have caused the error. You may attempt to continue running Revelation, but it may behave unexpectedly.",
			gtk.STOCK_DIALOG_ERROR,
			[ [ gtk.STOCK_QUIT, gtk.RESPONSE_CANCEL ], [ "Continue", gtk.RESPONSE_OK ] ], gtk.RESPONSE_CANCEL
		)

		textview = revelation.widget.TextView(None, traceback)
		textview.modify_font(pango.FontDescription("Monospace"))

		scrolledwindow = revelation.widget.ScrolledWindow(textview)
		scrolledwindow.set_size_request(-1, 120)

		self.contents.pack_start(scrolledwindow)


	def run(self):
		"Runs the dialog"

		return Hig.run(self) == gtk.RESPONSE_OK



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
		self.entry_phrase.grab_focus()

		return Property.run(self)



class PasswordGenerator(Property):
	"A password generator dialog"

	def __init__(self, parent, config):
		Property.__init__(
			self, parent, "Password Generator",
			[ [ gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ], [ revelation.stock.STOCK_GENERATE, gtk.RESPONSE_OK ] ]
		)

		self.config = config
		self.section = self.add_section("Password Generator")

		self.entry = revelation.widget.Entry()
		self.entry.set_editable(gtk.FALSE)
		self.section.add_inputrow("Password", self.entry)

		self.spin_pwlen = revelation.widget.SpinButton()
		self.spin_pwlen.set_range(4, 256)
		self.spin_pwlen.set_value(self.config.get("passwordgen/length"))
		self.section.add_inputrow("Length", self.spin_pwlen)

		self.check_ambiguous = revelation.widget.CheckButton("Avoid ambiguous characters")
		self.check_ambiguous.set_active(self.config.get("passwordgen/avoid_ambiguous"))
		self.section.add_inputrow(None, self.check_ambiguous)


	def run(self):
		"Runs the dialog"

		self.show_all()
		self.get_button(0).grab_focus()

		while 1:
			if Property.run(self) == gtk.RESPONSE_OK:
				self.entry.set_text(revelation.misc.generate_password(
					self.spin_pwlen.get_value(),
					self.check_ambiguous.get_active()
				))

			else:
				self.destroy()
				break



class Preferences(Property):
	"The preference dialog"

	def __init__(self, parent, config):
		Property.__init__(self, parent, "Preferences", [ [ gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ] ])
		self.config		= config
		self.notebook		= revelation.widget.Notebook()

		self.page_general	= self.notebook.create_page("General")
		self.__init_section_file(self.page_general)
		self.__init_section_pwgen(self.page_general)

		self.page_launchers	= self.notebook.create_page("Launchers")
		self.__init_section_launchers(self.page_launchers)

		self.vbox.pack_start(self.notebook)


	def __init_section_file(self, page):
		"Sets up the file section"

		self.section_file = page.add_section("File Handling")

		# check-button for autosave
		self.check_autosave = revelation.widget.CheckButton("Autosave data when changed")
		self.section_file.add_inputrow(None, self.check_autosave)

		self.tooltips.set_tip(self.check_autosave, "Automatically saves the data file when an entry is added, modified or removed")
		self.config.bind_widget("file/autosave", self.check_autosave)


		# check-button for autoloading a file
		self.check_autoload = revelation.widget.CheckButton("Open file on startup")
		self.section_file.add_inputrow(None, self.check_autoload)

		self.config.bind_widget("file/autoload", self.check_autoload)
		self.tooltips.set_tip(self.check_autoload, "When enabled, a file will be opened when the program is started")
		self.check_autoload.connect("toggled", self.__cb_autoload)


		# entry for file to autoload
		self.entry_autoload_file = revelation.widget.FileEntry("Select File to Automatically Open")
		self.entry_autoload_file.set_sensitive(self.check_autoload.get_active())
		self.section_file.add_inputrow("File to open", self.entry_autoload_file)

		self.config.bind_widget("file/autoload_file", self.entry_autoload_file)
		self.tooltips.set_tip(self.entry_autoload_file, "A file to be opened when the program is started")


	def __init_section_launchers(self, page):
		"Sets up the launchers section"

		self.section_launchers = page.add_section("Launcher Commands")

		for entry in revelation.entry.get_entry_list():

			if entry == revelation.entry.FolderEntry:
				continue

			entry = entry()

			widget = revelation.widget.Entry()
			self.config.bind_widget("launcher/" + entry.id, widget)

			tooltip = "Launcher command for " + entry.typename + " accounts. The following expansion variables can be used:\n\n"

			for field in entry.fields:
				tooltip += "%" + field.symbol + ": " + field.name + "\n"

			tooltip += "\n"
			tooltip += "%%: a % sign\n"
			tooltip += "%?x: optional expansion variable\n"
			tooltip += "%(...%): optional substring expansion"

			self.tooltips.set_tip(widget, tooltip)
			self.section_launchers.add_inputrow(entry.typename, widget)


	def __init_section_pwgen(self, page):
		"Sets up the password generator section"

		self.section_pwgen = page.add_section("Password Generator")

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

