#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing custom widgets
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

import gobject, gtk, gtk.gdk, gnome.ui, revelation, gconf, os.path


class GConfHandler:
	"""Abstract class which handles synchronization between
	   a widget and a gconf key"""

	def __cb_get(self, client, id, entry, data):
		self.gconf_cb_get(self.gconf, self.gconf_key)

	def __cb_set(self, object, data = None):
		self.gconf_cb_set(self.gconf, self.gconf_key)

	def __cb_unrealize(self, object, data = None):
		self.gconf.notify_remove(self.gconf_conn)

	def gconf_bind(self, key, cb_get, cb_set, setsignal):
		self.gconf = gconf.client_get_default()
		self.gconf_key = key
		self.gconf_cb_get = cb_get
		self.gconf_cb_set = cb_set

		cb_get(self.gconf, self.gconf_key)
		self.gconf_conn = self.gconf.notify_add(key, self.__cb_get)
		self.connect("unrealize", self.__cb_unrealize)

		if cb_set != None and setsignal != None:
			self.connect(setsignal, self.__cb_set)


# first, some simple subclasses - replacements for gtk widgets
class CheckButton(gtk.CheckButton, GConfHandler):

	def __init__(self, label = None):
		gtk.CheckButton.__init__(self, label)

	def __cb_gconf_get(self, client, key):
		self.set_active(client.get_bool(key))

	def __cb_gconf_set(self, client, key):
		client.set_bool(key, self.get_active())

	def gconf_bind(self, key):
		GConfHandler.gconf_bind(self, key, self.__cb_gconf_get, self.__cb_gconf_set, "toggled")



class Entry(gtk.Entry):

	def __init__(self, text = None):
		gtk.Entry.__init__(self)
		self.set_activates_default(gtk.TRUE)
		self.set_text(text)

	def set_text(self, text):
		if text == None:
			text = ""

		gtk.Entry.set_text(self, text)



class FileEntry(gnome.ui.FileEntry, GConfHandler):

	def __init__(self, history, title):
		gnome.ui.FileEntry.__init__(self, history, title)
		self.set_modal(gtk.TRUE)

	def __cb_gconf_get(self, client, key):
		self.gtk_entry().set_text(client.get_string(key))

	def __cb_gconf_set(self, client, key):
		client.set_string(key, self.gtk_entry().get_text())

	def gconf_bind(self, key):
		GConfHandler.gconf_bind(self, key, self.__cb_gconf_get, self.__cb_gconf_set, "changed")

	def get_filename(self):
		return gnome.ui.FileEntry.get_full_path(self, gtk.FALSE)

	def set_filename(self, filename):
		self.gtk_entry().set_text(filename)



class HRef(gnome.ui.HRef):

	def __init__(self, url, text):
		gnome.ui.HRef.__init__(self, url, text)
		self.get_children()[0].set_alignment(0, 0.5)



class ImageMenuItem(gtk.ImageMenuItem):

	def __init__(self, stock, text = None):
		gtk.ImageMenuItem.__init__(self, stock)

		self.label = self.get_children()[0]
		self.image = self.get_children()[1]

		if text is not None:
			self.set_text(text)

	def set_stock(self, stock):
		self.image.set_from_stock(stock, gtk.ICON_SIZE_MENU)

	def set_text(self, text):
		self.label.set_text(text)



class Label(gtk.Label):

	def __init__(self, text = None, justify = gtk.JUSTIFY_LEFT):
		gtk.Label.__init__(self)

		self.set_use_markup(gtk.TRUE)
		self.set_line_wrap(gtk.TRUE)
		self.set_text(text)

		self.set_justify(justify)

		if justify == gtk.JUSTIFY_LEFT:
			self.set_alignment(0, 0.5)

		elif justify == gtk.JUSTIFY_CENTER:
			self.set_alignment(0.5, 0.5)

		elif justify == gtk.JUSTIFY_RIGHT:
			self.set_alignment(1, 0.5)

	def set_text(self, text):
		if text is not None:
			gtk.Label.set_markup(self, text)



class OptionMenu(gtk.OptionMenu):

	def __init__(self, menu = None):
		gtk.OptionMenu.__init__(self)

		if menu == None:
			menu = gtk.Menu()

		self.set_menu(menu)

	def append_item(self, item):
		self.menu.append(item)
		if len(self.menu.get_children()) == 1:
			self.set_history(0)

	def get_active_item(self):
		return self.menu.get_children()[self.get_history()]

	def get_item(self, index):
		items = self.menu.get_children()
		return index < len(items) and items[index] or None

	def set_active_item(self, activeitem):
		items = self.get_menu().get_children()

		for i, item in zip(range(len(items)), items):
			if activeitem == item:
				self.set_history(i)

	def set_menu(self, menu):
		self.menu = menu
		gtk.OptionMenu.set_menu(self, menu)



class SpinButton(gtk.SpinButton, GConfHandler):

	def __init__(self, adjustment = None, climb_rate = 0.0, digits = 0):
		gtk.SpinButton.__init__(self, adjustment, climb_rate, digits)
		self.set_increments(1, 1)
		self.set_numeric(gtk.TRUE)

	def __cb_gconf_get(self, client, key):
		self.set_value(client.get_int(key))

	def __cb_gconf_set(self, client, key):
		client.set_int(key, self.get_value_as_int())

	def gconf_bind(self, key):
		GConfHandler.gconf_bind(self, key, self.__cb_gconf_get, self.__cb_gconf_set, "value-changed")



# more extensive custom widgets
class EntryDropdown(OptionMenu):

	def __init__(self):
		revelation.widget.OptionMenu.__init__(self)

		typelist = revelation.entry.get_entry_list()
		typelist.remove(revelation.entry.ENTRY_FOLDER)
		typelist.insert(0, revelation.entry.ENTRY_FOLDER)

		for type in typelist:
			item = revelation.widget.ImageMenuItem(revelation.entry.get_entry_data(type, "icon"), revelation.entry.get_entry_data(type, "name"))
			item.type = type
			self.append_item(item)

			if type == revelation.entry.ENTRY_FOLDER:
				self.append_item(gtk.SeparatorMenuItem())


	def get_type(self):
		item = self.get_active_item()
		return hasattr(item, "type") and item.type or None


	def set_type(self, type):
		for item in self.get_menu().get_children():
			if hasattr(item, "type") and item.type == type:
				self.set_active_item(item)



class ImageLabel(gtk.Alignment):

	def __init__(self, stock, size, text):
		gtk.Alignment.__init__(self, 0.5, 0.5, 0, 0)

		self.hbox = gtk.HBox()
		self.hbox.set_spacing(5)
		self.add(self.hbox)

		self.image = gtk.Image()
		self.hbox.pack_start(self.image, gtk.FALSE, gtk.FALSE)
		self.set_stock(stock, size)

		self.label = Label(text, gtk.JUSTIFY_CENTER)
		self.hbox.pack_start(self.label)

	def set_stock(self, stock, size):
		self.image.set_from_stock(stock, size)

	def set_text(self, text):
		self.label.set_text(text)



class InputSection(gtk.VBox):

	def __init__(self, title = None, sizegroup = None, description = None):
		gtk.VBox.__init__(self)
		self.set_border_width(0)
		self.set_spacing(6)

		self.title = None
		self.description = None
		self.sizegroup = sizegroup is not None and sizegroup or gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

		if title is not None:
			self.title = Label("<span weight=\"bold\">" + revelation.misc.escape_markup(title) + "</span>")
			self.pack_start(self.title, gtk.FALSE)

		if description is not None:
			self.description = Label(revelation.misc.escape_markup(description))
			self.pack_start(self.description, gtk.FALSE)


	def add_inputrow(self, title, widget):
		row = gtk.HBox()
		row.set_spacing(6)
		self.pack_start(row)

		if self.title is not None:
			row.pack_start(Label("   "), gtk.FALSE, gtk.FALSE)

		if title is not None:
			label = Label(revelation.misc.escape_markup(title) + ":")
			self.sizegroup.add_widget(label)
			row.pack_start(label, gtk.FALSE, gtk.FALSE)

		row.pack_start(widget)

		return row


	def clear(self):
		for child in self.get_children():
			if child not in [ self.label, self.description ]:
				child.destroy()



class PasswordEntry(gtk.HBox, GConfHandler):

	def __init__(self, value = None, generator = gtk.TRUE, ignorehide = gtk.FALSE):
		gtk.HBox.__init__(self)

		self.entry = revelation.widget.Entry(value)
		self.entry.connect("changed", self.__cb_changed)
		self.pack_start(self.entry)

		if ignorehide == gtk.FALSE:
			self.gconf_bind("/apps/revelation/view/passwords", self.__cb_gconf_password, None, None)

		if generator == gtk.TRUE:
			self.pwgen = gtk.Button("Generate")
			self.pwgen.connect("clicked", self.__cb_generate)
			self.pack_start(self.pwgen, gtk.FALSE, gtk.FALSE)


	def __cb_changed(self, widget, data = None):
		self.emit("changed")

	def __cb_gconf_password(self, client, key):
		self.set_visibility(client.get_bool(key))

	def __cb_generate(self, object, data = None):
		self.entry.set_text(revelation.misc.generate_password())


	def get_text(self):
		return self.entry.get_text()

	def set_activates_default(self, activates):
		self.entry.set_activates_default(activates)

	def set_text(self, text):
		self.entry.set_text(text)

	def set_visibility(self, visibility):
		self.entry.set_visibility(visibility)

gobject.signal_new("changed", PasswordEntry, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())



class PasswordLabel(Label, GConfHandler):

	def __init__(self, password, justify = gtk.JUSTIFY_LEFT):
		Label.__init__(self, password, justify)
		self.password = password

		self.gconf_bind("/apps/revelation/view/passwords", self.__cb_gconf_password, None, None)

	def __cb_gconf_password(self, client, key):
		if client.get_bool(key) == gtk.TRUE:
			Label.set_markup(self, self.password)
			self.set_selectable(gtk.TRUE)
		else:
			Label.set_text(self, "******")
			self.set_selectable(gtk.FALSE)

