#
# Revelation 0.3.0 - a password manager for GNOME 2
# $Id$
# http://oss.codepoet.no/revelation/
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

	def __init__(self, parent, title, buttons, default = None):
		gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR)

		self.set_border_width(6)
		self.vbox.set_spacing(12)
		self.set_resizable(gtk.FALSE)

		for stock, response in buttons:
			self.add_button(stock, response)

		if default is not None:
			self.set_default_response(default)
		else:
			self.set_default_response(buttons[-1][1])


	def get_button(self, index):
		buttons = self.action_area.get_children()
		return index < len(buttons) and buttons[index] or None



class Hig(Dialog):

	def __init__(self, parent, pritext, sectext, stockimage, buttons, default = None):
		Dialog.__init__(self, parent, "", buttons, default)

		# hbox separating dialog image and contents
		hbox = gtk.HBox()
		hbox.set_spacing(12)
		hbox.set_border_width(6)
		self.vbox.pack_start(hbox)

		# set up image
		if stockimage is not None:
			image = gtk.Image()
			image.set_from_stock(stockimage, gtk.ICON_SIZE_DIALOG)
			image.set_alignment(0.5, 0)
			hbox.pack_start(image, gtk.FALSE, gtk.FALSE)

		# set up main content area
		self.contents = gtk.VBox()
		self.contents.set_spacing(10)
		hbox.pack_start(self.contents)

		label = gtk.Label()
		label.set_markup("<span size=\"larger\" weight=\"bold\">" + revelation.misc.escape_markup(pritext) + "</span>\n\n" + sectext)
		label.set_line_wrap(gtk.TRUE)
		label.set_alignment(0, 0)
		self.contents.pack_start(label)


	def run(self):
		self.show_all()
		response = gtk.Dialog.run(self)
		self.destroy()

		return response



class Property(Dialog):

	def __init__(self, parent, title, buttons, default = None):
		Dialog.__init__(self, parent, title, buttons, default)

		self.set_border_width(12)
		self.vbox.set_spacing(18)

		self.sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.tooltips = gtk.Tooltips()


	def add_section(self, title, description = None):
		section = revelation.widget.InputSection(title, self.sizegroup, description)
		self.vbox.pack_start(section)
		return section



# the following classes may be subclassed from the bases above
class About(gnome.ui.About):

	def __init__(self):
		gnome.ui.About.__init__(
			self, revelation.APPNAME, revelation.VERSION, revelation.COPYRIGHT,
			"\"" + revelation.RELNAME + "\"\n\nRevelation is a password manager for the GNOME 2 desktop.",
			[ revelation.AUTHOR ], None, "",
			gtk.gdk.pixbuf_new_from_file(revelation.DATADIR + "/pixmaps/revelation.png")
		)


	def run(self):
		self.show_all()



class EditEntry(Property):

	def __init__(self, parent, title, data = None):
		Property.__init__(
			self, parent, title,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)

		if data is not None:
			self.data = data.copy()
			self.data["fields"] = self.data["fields"].copy()
		else:
			self.data = revelation.entry.get_entry_template(revelation.entry.ENTRY_FOLDER)

		section = self.add_section(title)

		entry = revelation.widget.Entry(self.data["name"])
		entry.set_width_chars(50)
		entry.connect("changed", self.__cb_entry_changed, "name")
		self.tooltips.set_tip(entry, "The name of the entry")
		section.add_inputrow("Name", entry)

		entry = revelation.widget.Entry(self.data["description"])
		self.tooltips.set_tip(entry, "A description of the entry")
		entry.connect("changed", self.__cb_entry_changed, "description")
		section.add_inputrow("Description", entry)

		self.dropdown = revelation.widget.EntryDropdown()
		self.tooltips.set_tip(self.dropdown, "The type of entry - folders can contain other entries")
		section.add_inputrow("Type", self.dropdown)

		self.dropdown.set_type(self.data["type"])
		self.dropdown.connect("changed", self.__cb_dropdown_changed)

		self.update()


	def __cb_entry_changed(self, widget, name):
		self.data[name] = widget.get_text()

	def __cb_entry_field_changed(self, widget, name):
		self.data["fields"][name] = widget.get_text()

	def __cb_dropdown_changed(self, object):
		type = self.dropdown.get_active_item().type

		if type != self.data["type"]:
			self.data["type"] = type
			self.data["icon"] = revelation.entry.get_entry_data(type, "icon")
			self.update()


	def run(self):
		if Property.run(self) == gtk.RESPONSE_OK:

			if self.data["name"] == "":
				Error(self, "No name given", "You need to enter a name for the entry.").run()
				return self.run()

			# normalize data
			self.data["updated"] = int(time.time())

			for field in self.data["fields"].keys():
				if not revelation.entry.field_exists(self.data["type"], field):
					del self.data["fields"][field]
			
			self.destroy()
			return self.data

		else:
			self.destroy()
			raise revelation.CancelError


	def set_typechange_allowed(self, allow):
		self.dropdown.set_sensitive(allow)


	def update(self, type = None):
		if len(self.vbox.get_children()) > 2:
			self.vbox.get_children().pop(1).destroy()

		fields = revelation.entry.get_entry_fields(self.data["type"])

		if len(fields) > 0:
			section = self.add_section("Account data")

		for field in fields:
			fielddata = revelation.entry.get_field_data(field)

			if field == revelation.entry.FIELD_GENERIC_PASSWORD:
				entry = revelation.widget.PasswordEntry()

			elif fielddata["type"] == revelation.entry.FIELD_TYPE_PASSWORD:
				entry = revelation.widget.PasswordEntry(None, gtk.FALSE)

			else:
				entry = revelation.widget.Entry()

			entry.set_text(self.data["fields"].get(field, ""))
			entry.connect("changed", self.__cb_entry_field_changed, field)
			self.tooltips.set_tip(entry, fielddata["tooltip"])
			section.add_inputrow(fielddata["name"], entry)

		self.show_all()



class Error(Hig):

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_ERROR,
			[ [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
		)



class FileOverwrite(Hig):

	def __init__(self, parent, file):
		Hig.__init__(
			self, parent, "Overwrite existing file?",
			"The file '" + file + "' already exists. If you choose to overwrite the file, its contents will be lost.", gtk.STOCK_DIALOG_WARNING,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_OVERWRITE, gtk.RESPONSE_OK ] ],
			gtk.RESPONSE_CANCEL
		)


	def run(self):
		return Hig.run(self) == gtk.RESPONSE_OK



class FileSelector(gtk.FileSelection):

	def __init__(self, title = None):
		gtk.FileSelection.__init__(self, title)


	def run(self):
		self.show()
		response = gtk.FileSelection.run(self)
		filename = self.get_filename()
		self.destroy()

		if response == gtk.RESPONSE_OK:
			return filename
		else:
			raise revelation.CancelError



class Find(Dialog):

	def __init__(self, parent):
		Dialog.__init__(
			self, parent, "Find an entry",
			[ [ gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ], [ revelation.stock.STOCK_PREVIOUS, RESPONSE_PREVIOUS ], [ revelation.stock.STOCK_NEXT, RESPONSE_NEXT ] ]
		)

		self.connect("key-press-event", self.__cb_keypress)
		self.tooltips = gtk.Tooltips()

		section = revelation.widget.InputSection("Find an entry")
		self.vbox.pack_start(section)

		self.entry_phrase = revelation.widget.Entry()
		self.tooltips.set_tip(self.entry_phrase, "The text to search for")
		self.entry_phrase.connect("changed", self.__cb_entry_changed)
		section.add_inputrow("Search for", self.entry_phrase)

		self.dropdown = revelation.widget.EntryDropdown()
		self.tooltips.set_tip(self.dropdown, "The account type to search for")
		item = self.dropdown.get_item(0)
		item.set_stock("gnome-stock-about")
		item.set_text("Any")
		item.type = None
		section.add_inputrow("Account type", self.dropdown)

		check = revelation.widget.CheckButton("Search for folders as well")
		self.tooltips.set_tip(check, "When enabled, folder names and descriptions will also be searched")
		check.gconf_bind("/apps/revelation/search/folders")
		section.add_inputrow(None, check)

		check = revelation.widget.CheckButton("Only search in name and description")
		self.tooltips.set_tip(check, "When enabled, only entry names and descriptions will be searched")
		check.gconf_bind("/apps/revelation/search/namedesc")
		section.add_inputrow(None, check)

		check = revelation.widget.CheckButton("Case sensitive")
		self.tooltips.set_tip(check, "When enabled, searches will be case sensitive")
		check.gconf_bind("/apps/revelation/search/casesens")
		section.add_inputrow(None, check)

		# set up initial states
		self.entry_phrase.emit("changed")


	def __cb_entry_changed(self, widget, data = None):
		active = len(self.entry_phrase.get_text()) > 0
		self.get_button(0).set_sensitive(active)
		self.get_button(1).set_sensitive(active)


	def __cb_keypress(self, widget, data):
		if data.keyval == 65307:
			self.response(gtk.RESPONSE_CLOSE)


	def run(self):
		self.show_all()
		return Dialog.run(self)



class Password(Hig):

	def __init__(self, parent, title, text, pwlen = 32, current = gtk.TRUE, new = gtk.FALSE):
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
			self.entry_password.set_max_length(pwlen)
			section.add_inputrow("Password", self.entry_password)

		if new == gtk.TRUE:
			self.entry_new = revelation.widget.Entry()
			self.entry_new.set_visibility(gtk.FALSE)
			self.entry_new.set_max_length(pwlen)
			section.add_inputrow("New password", self.entry_new)

			self.entry_confirm = revelation.widget.Entry()
			self.entry_confirm.set_visibility(gtk.FALSE)
			self.entry_confirm.set_max_length(pwlen)
			section.add_inputrow("Confirm new", self.entry_confirm)


	def run(self):
		while 1:
			self.show_all()

			if self.entry_password != None:
				self.entry_password.grab_focus()
			elif self.entry_new != None:
				self.entry_new.grab_focus()

			if Dialog.run(self) == gtk.RESPONSE_OK:

				if self.entry_new != None and self.entry_new.get_text() == "":
					Error(self, "New password not given", "You need to enter a new password.").run()

				elif self.entry_new != None and self.entry_new.get_text() != self.entry_confirm.get_text():
					Error(self, "Passwords don't match", "The password and password confirmation you entered does not match.").run()

				else:
					break

			else:
				raise revelation.CancelError



class Preferences(Property):

	def __init__(self, parent):
		Property.__init__(self, parent, "Preferences", [ [ gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE ] ])

		self.__init_section_file()
		self.__init_section_pwgen()


	def __init_section_file(self):
		self.section_file = self.add_section("File Handling")

		self.check_autoload = revelation.widget.CheckButton("Open file on startup")
		self.check_autoload.gconf_bind("/apps/revelation/file/autoload")
		self.check_autoload.connect("toggled", self.__cb_file_autoload)
		self.tooltips.set_tip(self.check_autoload, "When enabled, a file will be opened when the program is started")
		self.section_file.add_inputrow(None, self.check_autoload)

		self.entry_autoload_file = revelation.widget.FileEntry("revelation-autoload", "Select File to Automatically Open")
		self.entry_autoload_file.gconf_bind("/apps/revelation/file/autoload_file")
		self.entry_autoload_file.set_sensitive(self.check_autoload.get_active())
		self.tooltips.set_tip(self.entry_autoload_file, "A file to be opened when the program is started")
		self.section_file.add_inputrow("File to open", self.entry_autoload_file)


	def __init_section_pwgen(self):
		self.section_pwgen = self.add_section("Password Generator")

		self.spin_pwlen = revelation.widget.SpinButton()
		self.spin_pwlen.set_range(4, 32)
		self.spin_pwlen.gconf_bind("/apps/revelation/passwordgen/length")
		self.tooltips.set_tip(self.spin_pwlen, "The number of characters in generated passwords - 8 or more are recommended")
		self.section_pwgen.add_inputrow("Password length", self.spin_pwlen)

		self.check_ambiguous = revelation.widget.CheckButton("Avoid ambiguous characters")
		self.check_ambiguous.gconf_bind("/apps/revelation/passwordgen/avoid_ambiguous")
		self.tooltips.set_tip(self.check_ambiguous, "When enabled, generated passwords will not contain ambiguous characters - like 0 (zero) and O (capital o)")
		self.section_pwgen.add_inputrow(None, self.check_ambiguous)


	def __cb_file_autoload(self, object, data = None):
		self.entry_autoload_file.set_sensitive(self.check_autoload.get_active())


	def run(self):
		self.show_all()
		Property.run(self)
		self.destroy()



class RemoveEntry(Hig):

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_WARNING,
			[ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ revelation.stock.STOCK_REMOVE, gtk.RESPONSE_OK ] ],
			gtk.RESPONSE_CANCEL
		)


	def run(self):
		return Hig.run(self) == gtk.RESPONSE_OK


class SaveChanges(Hig):

	def __init__(self, parent, pritext, sectext):
		Hig.__init__(
			self, parent, pritext, sectext, gtk.STOCK_DIALOG_WARNING,
			[ [ revelation.stock.STOCK_DISCARD, gtk.RESPONSE_CLOSE ], [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_SAVE, gtk.RESPONSE_OK ] ]
		)

	def run(self):
		response = Hig.run(self)

		if response == gtk.RESPONSE_CANCEL:
			raise revelation.CancelError
		else:
			return response == gtk.RESPONSE_OK

