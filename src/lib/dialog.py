#
# Revelation 0.4.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module with dialogs
#
#
# Copyright (c) 2003-2005 Erik Grinaker
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

import config, datahandler, entry, io, ui, util

import gtk, gnome.ui



RESPONSE_NEXT		= 10
RESPONSE_PREVIOUS	= 11



##### EXCEPTIONS #####

class CancelError(Exception):
	"Exception for dialog cancellations"
	pass



##### BASE DIALOGS #####

class Dialog(gtk.Dialog):
	"Base class for dialogs"

	def __init__(self, parent, title, buttons = (), default = None):
		gtk.Dialog.__init__(
			self, title, parent,
			gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR
		)

		self.set_border_width(6)
		self.vbox.set_spacing(12)
		self.set_resizable(False)

		self.connect("key_press_event", self.__cb_keypress)

		for stock, response in buttons:
			self.add_button(stock, response)

		if default is not None:
			self.set_default_response(default)

		elif len(buttons) > 0:
			self.set_default_response(buttons[-1][1])


	def __cb_keypress(self, widget, data):
		"Callback for handling key presses"

		# close the dialog on Escape
		if data.keyval == 65307:
			self.response(gtk.RESPONSE_CLOSE)


	def get_button(self, index):
		"Get one of the dialog buttons"

		buttons = self.action_area.get_children()

		if index < len(buttons):
			return buttons[index]



class Utility(Dialog):
	"A utility dialog"

	def __init__(self, parent, title, buttons = ( ( gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ), ), default = None):
		Dialog.__init__(self, parent, title, buttons, default)

		self.set_border_width(12)
		self.vbox.set_spacing(18)

		self.sizegroup	= gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.tooltips	= gtk.Tooltips()


	def add_section(self, title, description = None):
		"Adds an input section to the dialog"

		section = ui.InputSection(title, description, self.sizegroup)
		self.vbox.pack_start(section)

		return section



class Message(Dialog):
	"A message dialog"

	def __init__(self, parent, title, text, stockimage, buttons = (), default = None):
		Dialog.__init__(self, parent, "", buttons, default)

		# hbox with image and contents
		hbox = ui.HBox()
		hbox.set_spacing(12)
		hbox.set_border_width(6)
		self.vbox.pack_start(hbox)

		# set up image
		if stockimage is not None:
			image = ui.Image(stockimage, gtk.ICON_SIZE_DIALOG)
			image.set_alignment(0.5, 0)
			hbox.pack_start(image, False, False)

		# set up message
		self.contents = ui.VBox()
		self.contents.set_spacing(10)
		hbox.pack_start(self.contents)

		label = ui.Label(
			"<span size=\"larger\" weight=\"bold\">%s</span>\n\n%s" %
			( util.escape_markup(title), text)
		)
		label.set_alignment(0, 0)
		label.set_selectable(True)
		self.contents.pack_start(label)


	def run(self):
		"Displays the dialog"

		self.show_all()
		response = Dialog.run(self)
		self.destroy()

		return response



class Error(Message):
	"Displays an error message"

	def __init__(self, parent, title, text, buttons = ( ( gtk.STOCK_OK, gtk.RESPONSE_OK), ), default = None):
		Message.__init__(self, parent, title, text, gtk.STOCK_DIALOG_ERROR, buttons, default)



class Info(Message):
	"Displays an info message"

	def __init__(self, parent, title, text, buttons = ( ( gtk.STOCK_OK, gtk.RESPONSE_OK ), ), default = None):
		Message.__init__(self, parent, title, text, gtk.STOCK_DIALOG_INFO, buttons, default)



class Question(Message):
	"Displays a question"

	def __init__(self, parent, title, text, buttons = ( ( gtk.STOCK_OK, gtk.RESPONSE_OK ), ), default = None):
		Message.__init__(self, parent, title, text, gtk.STOCK_DIALOG_QUESTION, buttons, default)



class Warning(Message):
	"Displays a warning message"

	def __init__(self, parent, title, text, buttons = ( ( gtk.STOCK_OK, gtk.RESPONSE_OK ), ), default = None):
		Message.__init__(self, parent, title, text, gtk.STOCK_DIALOG_WARNING, buttons, default)



##### QUESTION DIALOGS #####

class FileChanged(Warning):
	"Asks to save changes before proceeding"

	def __init__(self, parent, title, text):
		Warning.__init__(
			self, parent, title, text,
			( ( ui.STOCK_DISCARD, gtk.RESPONSE_ACCEPT ), ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ), ( gtk.STOCK_SAVE, gtk.RESPONSE_OK ) )
		)


	def run(self):
		"Displays the dialog"

		response = Warning.run(self)

		if response == gtk.RESPONSE_OK:	
			return True

		elif response == gtk.RESPONSE_ACCEPT:
			return False

		elif response in ( gtk.RESPONSE_CANCEL, gtk.RESPONSE_CLOSE ):
			raise CancelError



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



class FileOverwrite(Warning):
	"Asks for confirmation when overwriting a file"

	def __init__(self, parent, file):
		Warning.__init__(
			self, parent, "Overwrite existing file?",
			"The file '%s' already exists - do you wish to replace this file?" % file,
			( ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ), ( gtk.STOCK_OK, gtk.RESPONSE_OK ) )
		)


	def run(self):
		"Displays the dialog"

		if Warning.run(self) == gtk.RESPONSE_OK:
			return True

		else:
			raise CancelError



class FileSaveInsecure(Warning):
	"Asks for confirmation when exporting to insecure file"

	def __init__(self, parent):
		Warning.__init__(
			self, parent, "Save to insecure file?",
			"You have chosen to save your passwords to an insecure (unencrypted) file format - if anyone has access to this file, they will be able to see your passwords.",
			( ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ), ( gtk.STOCK_SAVE, gtk.RESPONSE_OK ) ), 0
		)


	def run(self):
		"Runs the dialog"

		if Warning.run(self) == gtk.RESPONSE_OK:
			return True

		else:
			raise CancelError



##### FILE SELECTION DIALOGS #####

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
			( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, stockbutton, gtk.RESPONSE_OK )
		)

		self.set_local_only(False)
		self.set_default_response(gtk.RESPONSE_OK)

		self.inputsection = None


	def add_widget(self, title, widget):
		"Adds a widget to the file selection"

		if self.inputsection == None:
			self.inputsection = ui.InputSection()
			self.set_extra_widget(self.inputsection)

		self.inputsection.append_widget(title, widget)


	def get_filename(self):
		"Returns the file URI"

		return io.file_normpath(self.get_uri())


	def run(self):
		"Displays and runs the file selector, returns the filename"

		self.show_all()
		response = gtk.FileChooserDialog.run(self)
		filename = self.get_filename()
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return filename

		else:
			raise CancelError



class ExportFileSelector(FileSelector):
	"A file selector for exporting files"

	def __init__(self, parent):
		FileSelector.__init__(
			self, parent, "Select File to Export to",
			gtk.FILE_CHOOSER_ACTION_SAVE, ui.STOCK_EXPORT
		)

		# set up filetype dropdown
		self.dropdown = ui.DropDown()
		self.add_widget("Filetype", self.dropdown)

		for handler in datahandler.get_export_handlers():
			self.dropdown.append_item(handler.name, None, handler)


	def run(self):
		"Displays the dialog"

		self.show_all()
		self.inputsection.show_all()

		if gtk.FileSelection.run(self) == gtk.RESPONSE_OK:
			filename = self.get_filename()
			handler = self.dropdown.get_active_item()[2]
			self.destroy()

			return filename, handler

		else:
			self.destroy()
			raise CancelError



class ImportFileSelector(FileSelector):
	"A file selector for importing files"

	def __init__(self, parent):
		FileSelector.__init__(
			self, parent, "Select File to Import",
			gtk.FILE_CHOOSER_ACTION_OPEN, ui.STOCK_IMPORT
		)

		# set up filetype dropdown
		self.dropdown = ui.DropDown()
		self.add_widget("Filetype", self.dropdown)

		self.dropdown.append_item("Automatically detect")

		for handler in datahandler.get_import_handlers():
			self.dropdown.append_item(handler.name, None, handler)


	def run(self):
		"Displays the dialog"

		self.show_all()
		self.inputsection.show_all()

		if gtk.FileSelection.run(self) == gtk.RESPONSE_OK:
			filename = self.get_filename()
			handler = self.dropdown.get_active_item()[2]
			self.destroy()

			return filename, handler

		else:
			self.destroy()
			raise CancelError



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



##### PASSWORD DIALOGS #####

class Password(Message):
	"A base dialog for asking for passwords"

	def __init__(self, parent, title, text, stock = gtk.STOCK_OK):
		Message.__init__(
			self, parent, title, text, gtk.STOCK_DIALOG_AUTHENTICATION,
			( ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ), ( stock, gtk.RESPONSE_OK ))
		)

		self.entries = []

		self.sect_passwords = ui.InputSection()
		self.contents.pack_start(self.sect_passwords)


	def add_entry(self, name):
		"Adds a password entry to the dialog"

		entry = ui.Entry()
		entry.set_visibility(False)
		self.sect_passwords.append_widget(name, entry)

		self.entries.append(entry)

		return entry


	def run(self):
		"Displays the dialog"

		self.show_all()

		if len(self.entries) > 0:
			self.entries[0].grab_focus()

		return gtk.Dialog.run(self)



class PasswordChange(Password):
	"A dialog for changing the password"

	def __init__(self, parent, password = None):
		Password.__init__(
			self, parent, "Enter new password",
			"Enter a new password for the current data file. The file must be saved before the new password is applied.",
			ui.STOCK_PASSWORD_CHANGE
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
					password = self.entry_new.get_text()
					self.destroy()
					return password

			else:
				self.destroy()
				raise CancelError



class PasswordLock(Password):
	"Asks for a password when the file is locked"

	def __init__(self, parent, password):
		Password.__init__(
			self, parent, "Enter password to unlock file",
			"The current file has been locked, please enter the file password to unlock it."
		)

		self.get_button(1).destroy()

		self.password = password
		self.entry_password = self.add_entry("Password")


	def run(self):
		"Displays the dialog"

		while 1:
			try:
				if Password.run(self) != gtk.RESPONSE_OK:
					continue

				elif self.entry_password.get_text() == self.password:
					break

				else:
					Error(self, "Incorrect password", "The password you entered was not correct, please try again.").run()

			except CancelError:
				continue

		self.destroy()



class PasswordOpen(Password):
	"Password dialog for opening files"

	def __init__(self, parent, filename):
		Password.__init__(
			self, parent, "Enter file password",
			"The file '%s' is encrypted. Please enter the file password to open it." % filename
		)

		self.entry_password = self.add_entry("Password")


	def run(self):
		"Displays the dialog"

		response = Password.run(self)
		password = self.entry_password.get_text()
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return password

		else:
			raise CancelError



class PasswordSave(Password):
	"Password dialog for saving data"

	def __init__(self, parent, filename):
		Password.__init__(
			self, parent, "Enter password for file",
			"Please enter a password for the file '%s'. You will need this password to open the file at a later time." % filename
		)

		self.entry_new		= self.add_entry("New password")
		self.entry_confirm	= self.add_entry("Confirm password")


	def run(self):
		"Displays the dialog"

		while 1:
			if Password.run(self) != gtk.RESPONSE_OK:
				self.destroy()
				raise CancelError

			elif self.entry_new.get_text() != self.entry_confirm.get_text():
				Error(self, "Passwords don't match", "The passwords you entered does not match.").run()

			elif len(self.entry_new.get_text()) == 0:
				Error(self, "No password entered", "You must enter a password for the new data file.").run()

			else:
				password = self.entry_new.get_text()
				self.destroy()

				return password



##### ENTRY DIALOGS #####

class EntryEdit(Utility):
	"A dialog for editing entries"

	def __init__(self, parent, cfg, title, e = None):
		Utility.__init__(
			self, parent, title,
			( ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ), ( gtk.STOCK_OK, gtk.RESPONSE_OK ) )
		)

		self.config		= cfg
		self.entry_field	= {}
		self.fielddata		= {}
		self.widgetdata		= {}

		# set up the ui
		self.sect_meta		= self.add_section(title)
		self.sect_fields	= None

		self.entry_name = ui.Entry()
		self.entry_name.set_width_chars(50)
		self.tooltips.set_tip(self.entry_name, "The name of the entry")
		self.sect_meta.append_widget("Name", self.entry_name)

		self.entry_desc = ui.Entry()
		self.tooltips.set_tip(self.entry_desc, "A description of the entry")
		self.sect_meta.append_widget("Description", self.entry_desc)

		self.dropdown = ui.EntryDropDown()
		self.dropdown.connect("changed", lambda w: self.__setup_fieldsect(self.dropdown.get_active_type()().fields))
		eventbox = ui.EventBox(self.dropdown)
		self.tooltips.set_tip(eventbox, "The type of entry - folders can contain other entries")
		self.sect_meta.append_widget("Type", eventbox)

		# populate the dialog with data
		self.set_entry(e)


	def __setup_fieldsect(self, fields):
		"Generates a field section based on a field list"

		# store current field values
		for fieldtype, fieldentry in self.entry_field.items():
			self.fielddata[fieldtype] = fieldentry.get_text()

		self.entry_field = {}

		# create or remove field section as needed
		if self.sect_fields is None and len(fields) > 0:
			self.sect_fields = self.add_section("Account data")

		elif self.sect_fields is not None and len(fields) > 0:
			self.sect_fields.clear()

		elif self.sect_fields is not None and len(fields) == 0:
			self.sect_fields.destroy()
			self.sect_fields = None

		# generate field entries
		for field in fields:

			if self.widgetdata.has_key(type(field)):
				userdata = self.widgetdata[type(field)]
			else:
				userdata = None

			fieldentry = ui.generate_field_edit_widget(type(field), self.config, userdata)
			fieldentry.set_text(field.value)
			self.entry_field[type(field)] = fieldentry

			if self.fielddata.has_key(type(field)):
				fieldentry.set_text(self.fielddata[type(field)])

			if (fieldentry.flags() & gtk.NO_WINDOW) == gtk.NO_WINDOW:
				eventbox = ui.EventBox(fieldentry)
				self.tooltips.set_tip(eventbox, field.description)
				self.sect_fields.append_widget(field.name, eventbox)

			else:
				self.tooltips.set_tip(fieldentry, field.description)
				self.sect_fields.append_widget(field.name, fieldentry)


		# show widgets
		if self.sect_fields is not None:
			self.sect_fields.show_all()


	def allow_typechange(self, allow):
		"Sets whether type changes are allowed"

		self.dropdown.set_sensitive(allow)


	def get_entry(self):
		"Generates an entry from the dialog contents"

		e = self.dropdown.get_active_type()()

		e.name = self.entry_name.get_text()
		e.description = self.entry_desc.get_text()

		for field in e.fields:
			field.value = self.entry_field[type(field)].get_text()

		return e


	def run(self):
		"Displays the dialog"

		while 1:
			self.show_all()

			if Utility.run(self) == gtk.RESPONSE_OK:
				e = self.get_entry()

				if e.name == "":
					Error(self, "Name not entered", "You must enter a name for the account").run()
					continue

				self.destroy()
				return e

			else:
				self.destroy()
				raise CancelError


	def set_entry(self, e):
		"Sets an entry for the dialog"

		e = e is not None and e.copy() or entry.GenericEntry()

		self.entry_name.set_text(e.name)
		self.entry_desc.set_text(e.description)
		self.dropdown.set_active_type(type(e))

		for field in e.fields:
			self.entry_field[type(field)].set_text(field.value)


	def set_fieldwidget_data(self, fieldtype, userdata):
		"Sets user data for fieldwidget"

		self.widgetdata[fieldtype] = userdata

		if fieldtype == entry.UsernameField and self.entry_field.has_key(entry.UsernameField):
			self.entry_field[entry.UsernameField].set_dropdown_values(userdata)



class EntryRemove(Warning):
	"Asks for confirmation when removing entries"

	def __init__(self, parent, entries):

		if len(entries) > 1:
			title	= "Really remove the %i selected entries?" % len(entries)
			text	= "By removing these entries you will also remove any entries they may contain."

		elif type(entries[0]) == entry.FolderEntry:
			title	= "Really remove folder '%s'?" % entries[0].name
			text	= "By removing this folder you will also remove all accounts and folders it contains."

		else:
			title	= "Really remove account '%s'?" % entries[0].name
			text	= "Please confirm that you wish to remove this account."


		Warning.__init__(
			self, parent, title, text,
			( ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ), ( ui.STOCK_REMOVE, gtk.RESPONSE_OK ) ),
			0
		)


	def run(self):
		"Displays the dialog"

		if Warning.run(self) == gtk.RESPONSE_OK:
			return True

		else:
			raise CancelError



##### MISCELLANEOUS DIALOGS #####

class About(gnome.ui.About):
	"About dialog"

	def __init__(self, parent):
		gnome.ui.About.__init__(
			self, config.APPNAME, config.VERSION, config.COPYRIGHT,
			""""%s"\n\nRevelation is a password manager for the GNOME 2 desktop""" % config.RELNAME,
			( config.AUTHOR, ), None, "",
			gtk.icon_theme_get_default().load_icon("revelation", 48, 0)
		)

		if parent is not None:
			self.set_transient_for(parent)


	def run(self):
		"Displays the dialog"

		self.show_all()



class Exception(Error):
	"Displays a traceback for an unhandled exception"

	def __init__(self, parent, traceback):
		Error.__init__(
			self, parent, "Unknown error",
			"An unknown error occured. Please report the text below to the Revelation developers, along with what you were doing that may have caused the error. You may attempt to continue running Revelation, but it may behave unexpectedly.",
			( ( gtk.STOCK_QUIT, gtk.RESPONSE_CANCEL ), ( "Continue", gtk.RESPONSE_OK ) )
		)

		textview = ui.TextView(None, traceback)
		scrolledwindow = ui.ScrolledWindow(textview)
		scrolledwindow.set_size_request(-1, 120)

		self.contents.pack_start(scrolledwindow)


	def run(self):
		"Runs the dialog"

		return Error.run(self) == gtk.RESPONSE_OK



class Find(Utility):
	"A find dialog"

	def __init__(self, parent, cfg):
		Utility.__init__(
			self, parent, "Find an entry",
			( ( gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ), ( ui.STOCK_PREVIOUS, RESPONSE_PREVIOUS ), ( ui.STOCK_NEXT, RESPONSE_NEXT ) )
		)

		self.config = cfg

		section = self.add_section("Find an entry")

		# search string entry
		self.entry_string = ui.Entry()
		self.entry_string.connect("changed", lambda w: self.__state_buttons(self.entry_string.get_text() != ""))

		section.append_widget("Search for", self.entry_string)
		self.tooltips.set_tip(self.entry_string, "The text to search for")

		# account type dropdown
		self.dropdown = ui.EntryDropDown()
		self.dropdown.delete_item(0)
		self.dropdown.insert_item(0, "Any", "gnome-stock-about")

		eventbox = ui.EventBox(self.dropdown)
		section.append_widget("Account type", eventbox)
		self.tooltips.set_tip(eventbox, "The account type to search for")

		# folders checkbutton
		self.check_folders = ui.CheckButton("Search for folders as well")
		ui.config_bind(self.config, "search/folders", self.check_folders)

		section.append_widget(None, self.check_folders)
		self.tooltips.set_tip(self.check_folders, "When enabled, folder names and descriptions will also be searched")

		# namedesc checkbutton
		self.check_namedesc = ui.CheckButton("Only search in name and description")
		ui.config_bind(self.config, "search/namedesc", self.check_namedesc)

		section.append_widget(None, self.check_namedesc)
		self.tooltips.set_tip(self.check_namedesc, "When enabled, only entry names and descriptions will be searched")

		# case sensitive checkbutton
		self.check_casesensitive = ui.CheckButton("Case sensitive")
		ui.config_bind(self.config, "search/casesens", self.check_casesensitive)

		section.append_widget(None, self.check_casesensitive)
		self.tooltips.set_tip(self.check_casesensitive, "When enabled, searches will be case sensitive")

		# set initial state
		self.__state_buttons(False)


	def __state_buttons(self, active):
		"Sets button sensitivity based on entry contents"

		self.get_button(0).set_sensitive(active)
		self.get_button(1).set_sensitive(active)


	def run(self):
		"Displays the dialog"

		self.show_all()
		self.entry_string.grab_focus()

		return Utility.run(self)



class PasswordGenerator(Utility):
	"A password generator dialog"

	def __init__(self, parent, cfg):
		Utility.__init__(
			self, parent, "Password Generator",
			( ( gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ), ( ui.STOCK_GENERATE, gtk.RESPONSE_OK ) )
		)

		self.config = cfg
		self.section = self.add_section("Password Generator")

		self.entry = ui.Entry()
		self.entry.set_editable(False)
		self.tooltips.set_tip(self.entry, "The generated password")
		self.section.append_widget("Password", self.entry)

		self.spin_pwlen = ui.SpinEntry()
		self.spin_pwlen.set_range(4, 256)
		self.spin_pwlen.set_value(self.config.get("passwordgen/length"))
		self.tooltips.set_tip(self.spin_pwlen, "The number of characters in generated passwords - 8 or more are recommended")
		self.section.append_widget("Length", self.spin_pwlen)

		self.check_ambiguous = ui.CheckButton("Avoid ambiguous characters")
		self.check_ambiguous.set_active(self.config.get("passwordgen/avoid_ambiguous"))
		self.tooltips.set_tip(self.check_ambiguous, "When enabled, generated passwords will not contain ambiguous characters - like 0 (zero) and O (capital o)")
		self.section.append_widget(None, self.check_ambiguous)


	def run(self):
		"Displays the dialog"

		self.show_all()
		self.get_button(0).grab_focus()

		while 1:
			if Utility.run(self) == gtk.RESPONSE_OK:
				self.entry.set_text(util.generate_password(
					self.spin_pwlen.get_value(),
					self.check_ambiguous.get_active()
				))

			else:
				self.destroy()
				break



class Preferences(Utility):
	"A preference dialog"

	def __init__(self, parent, cfg):
		Utility.__init__(self, parent, "Preferences")
		self.config = cfg

		self.notebook = ui.Notebook()
		self.vbox.pack_start(self.notebook)

		self.page_general = self.notebook.create_page("General")
		self.__init_section_file(self.page_general)
		self.__init_section_pwgen(self.page_general)
		self.__init_section_launching(self.page_general)

		self.page_launchers = self.notebook.create_page("Launchers")
		self.__init_section_launchers(self.page_launchers)


	def __init_section_file(self, page):
		"Sets up the file section"

		self.section_file = page.add_section("File handling")

		# check-button for autosave
		self.check_autosave = ui.CheckButton("Autosave data when changed")
		ui.config_bind(self.config, "file/autosave", self.check_autosave)

		self.tooltips.set_tip(self.check_autosave, "Automatically saves the data file when an entry is added, modified or removed")
		self.section_file.append_widget(None, self.check_autosave)

		# check-button for autoloading a file
		self.check_autoload = ui.CheckButton("Open file on startup")
		ui.config_bind(self.config, "file/autoload", self.check_autoload)
		self.check_autoload.connect("toggled", lambda w: self.entry_autoload_file.set_sensitive(w.get_active()))

		self.tooltips.set_tip(self.check_autoload, "When enabled, a file will be opened when the program is started")
		self.section_file.append_widget(None, self.check_autoload)

		# entry for file to autoload
		self.entry_autoload_file = ui.FileEntry("Select File to Automatically Open")
		ui.config_bind(self.config, "file/autoload_file", self.entry_autoload_file)
		self.entry_autoload_file.set_sensitive(self.check_autoload.get_active())

		eventbox = ui.EventBox(self.entry_autoload_file)
		self.tooltips.set_tip(eventbox, "A file to be opened when the program is started")
		self.section_file.append_widget("File to open", eventbox)


	def __init_section_launchers(self, page):
		"Sets up the launcher section"

		self.section_launchers = page.add_section("Launcher Commands")

		for entrytype in entry.ENTRYLIST:
			if entrytype == entry.FolderEntry:
				continue

			e = entrytype()

			widget = ui.Entry()
			ui.config_bind(self.config, "launcher/%s" % e.id, widget)

			tooltip = "Launcher command for %s accounts. The following expansion variables can be used:\n\n" % e.typename

			for field in e.fields:
				tooltip += "%%%s: %s\n" % ( field.symbol, field.name )

			tooltip += "\n"
			tooltip += "%%: a % sign\n"
			tooltip += "%?x: optional expansion variable\n"
			tooltip += "%(...%): optional substring expansion"

			self.tooltips.set_tip(widget, tooltip)
			self.section_launchers.append_widget(e.typename, widget)


	def __init_section_launching(self, page):
		"Sets up the launching section"

		self.section_launching = page.add_section("Launching")

		# doubleclick action
		self.check_doubleclick = ui.CheckButton("Launch entry on double-click")
		ui.config_bind(self.config, "launching/doubleclick", self.check_doubleclick)

		self.tooltips.set_tip(self.check_doubleclick, "When enabled, doubleclicking an entry will launch it instead of edit it")
		self.section_launching.append_widget(None, self.check_doubleclick)


	def __init_section_pwgen(self, page):
		"Sets up the password generator section"

		self.section_pwgen = page.add_section("Password Generator")

		# password length spinbutton
		self.spin_pwlen = ui.SpinEntry()
		self.spin_pwlen.set_range(4, 32)
		ui.config_bind(self.config, "passwordgen/length", self.spin_pwlen)

		self.tooltips.set_tip(self.spin_pwlen, "The number of characters in generated passwords - 8 or more are recommended")
		self.section_pwgen.append_widget("Password length", self.spin_pwlen)

		# checkbox for avoiding ambiguous characters
		self.check_ambiguous = ui.CheckButton("Avoid ambiguous characters")
		ui.config_bind(self.config, "passwordgen/avoid_ambiguous", self.check_ambiguous)

		self.tooltips.set_tip(self.check_ambiguous, "When enabled, generated passwords will not contain ambiguous characters - like 0 (zero) and O (capital o)")
		self.section_pwgen.append_widget(None, self.check_ambiguous)


	def run(self):
		"Runs the preference dialog"

		self.show_all()
		Utility.run(self)
		self.destroy()

