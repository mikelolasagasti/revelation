#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing custom widgets, mostly extensions of gtk ones
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
class App(gnome.ui.App):

	def __init__(self, appname):
		gnome.ui.App.__init__(self, appname, appname)
		self.appname = appname

		self.toolbar = Toolbar()
		self.toolbar.connect("hide", self.__cb_toolbar_hide)
		self.toolbar.connect("show", self.__cb_toolbar_show)
		self.set_toolbar(self.toolbar)

		self.statusbar = gnome.ui.AppBar(gtk.FALSE, gtk.TRUE, gnome.ui.PREFERENCES_USER)
		self.set_statusbar(self.statusbar)

		self.accelgroup = gtk.AccelGroup()
		self.add_accel_group(self.accelgroup)


	def __cb_toolbar_hide(self, object, data = None):
		self.get_dock_item_by_name("Toolbar").hide()


	def __cb_toolbar_show(self, object, data = None):
		self.get_dock_item_by_name("Toolbar").show()


	def __cb_menudesc(self, object, item, show):
		if show:
			self.statusbar.set_status(item.get_data("description"))
		else:
			self.statusbar.set_status("")


	def __create_itemfactory(self, widget, accelgroup, items):
		itemfactory = MenuFactory(widget, accelgroup)
		itemfactory.create_items(items)
		itemfactory.connect("item-selected", self.__cb_menudesc, gtk.TRUE)
		itemfactory.connect("item-deselected", self.__cb_menudesc, gtk.FALSE)
		return itemfactory


	def create_menu(self, menuitems):
		self.if_menu = self.__create_itemfactory(gtk.MenuBar, self.accelgroup, menuitems)
		self.set_menus(self.if_menu.get_widget("<main>"))


	def popup(self, menuitems, x, y, button, time):
		itemfactory = self.__create_itemfactory(gtk.Menu, self.accelgroup, menuitems)
		itemfactory.popup(x, y, button, time)


	def run(self):
		self.show_all()
		gtk.main()


	def set_title(self, title):
		gnome.ui.App.set_title(self, title + " - " + self.appname)



class CheckButton(gtk.CheckButton, GConfHandler):

	def __init__(self, label = None):
		gtk.CheckButton.__init__(self, label)

	def __cb_gconf_get(self, client, key):
		self.set_active(client.get_bool(key))

	def __cb_gconf_set(self, client, key):
		client.set_bool(key, self.get_active())

	def gconf_bind(self, key):
		GConfHandler.gconf_bind(self, key, self.__cb_gconf_get, self.__cb_gconf_set, "toggled")



class Entry(gtk.Entry, GConfHandler):

	def __init__(self, text = None):
		gtk.Entry.__init__(self)
		self.set_activates_default(gtk.TRUE)
		self.set_text(text)


	def __cb_gconf_get(self, client, key):
		self.set_text(client.get_string(key))


	def __cb_gconf_set(self, client, key):
		client.set_string(key, self.get_text())


	def gconf_bind(self, key):
		GConfHandler.gconf_bind(self, key, self.__cb_gconf_get, self.__cb_gconf_set, "changed")


	def set_text(self, text):
		if text == None:
			text = ""

		gtk.Entry.set_text(self, text)



class FileEntry(gtk.HBox):

	def __init__(self, title, filename = None):
		gtk.HBox.__init__(self)
		self.set_spacing(5)
		self.title = title

		self.entry = Entry()
		self.pack_start(self.entry)

		self.button = gtk.Button("Browse...")
		self.button.connect("clicked", self.__cb_filesel)
		self.pack_start(self.button, gtk.FALSE, gtk.FALSE)

		if filename is not None:
			self.set_filename(filename)


	def __cb_filesel(self, object, data = None):
		fsel = gtk.FileSelection(self.title)
		fsel.set_modal(gtk.TRUE)
		fsel.set_filename(self.get_filename())

		fsel.show_all()
		response = fsel.run()

		if response == gtk.RESPONSE_OK:
			self.set_filename(fsel.get_filename())

		fsel.destroy()


	def gconf_bind(self, key):
		self.entry.gconf_bind(key)


	def get_filename(self):
		return self.entry.get_text()

	def set_filename(self, filename):
		self.entry.set_text(os.path.normpath(filename))
		self.entry.set_position(-1)



class HPaned(gtk.HPaned):

	def __init__(self, content_left = None, content_right = None, position = None):
		gtk.HPaned.__init__(self)
		self.set_border_width(6)

		if content_left is not None:
			self.pack1(content_left, gtk.TRUE, gtk.TRUE)

		if content_right is not None:
			self.pack2(content_right, gtk.TRUE, gtk.TRUE)

		if position is not None:
			self.set_position(position)



class HRef(gnome.ui.HRef):

	def __init__(self, url, text):
		gnome.ui.HRef.__init__(self, url, text)
		self.get_children()[0].set_alignment(0, 0.5)



class Image(gtk.Image):

	def __init__(self, stock = None, size = None):
		gtk.Image.__init__(self)

		if stock is not None:
			self.set_from_stock(stock, size)



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



class MenuFactory(gtk.ItemFactory):

	def __init__(self, widget, accelgroup):
		gtk.ItemFactory.__init__(self, widget, "<main>", accelgroup)

	def __cb_select(self, object):
		self.emit("item-selected", object)

	def __cb_deselect(self, object):
		self.emit("item-deselected", object)


	def create_items(self, items):

		# strip description from items, and create the items
		ifitems = []
		for item in items:
			ifitems.append(item[0:2] + item[3:])

		gtk.ItemFactory.create_items(self, ifitems)

		# set up description for items
		for item in items:
			if item[5] in ["<Item>", "<StockItem>", "<CheckItem>"]:
				widget = self.get_widget("<main>" + item[0].replace("_", ""))
				widget.set_data("description", item[2])
				widget.connect("select", self.__cb_select)
				widget.connect("deselect", self.__cb_deselect)


gobject.signal_new("item-selected", MenuFactory, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gtk.MenuItem,))
gobject.signal_new("item-deselected", MenuFactory, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gtk.MenuItem,))



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



class ScrolledWindow(gtk.ScrolledWindow):

	def __init__(self, contents = None):
		gtk.ScrolledWindow.__init__(self)
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		if contents is not None:
			self.add(contents)



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



class TreeStore(gtk.TreeStore):
	"An enhanced gtk.TreeStore"

	def __init__(self, *args):
		gtk.TreeStore.__init__(self, *args)


	def filter_parents(self, iters):
		"Get only the topmost nodes of a group of iters (no descendants)"

		parents = []
		for child in iters:
			for parent in iters:
				if self.is_ancestor(parent, child):
					break

			else:
				parents.append(child)

		return parents


	def get_iter(self, path):
		"Gets an iter from a path"

		if path in [ None, "", () ]:
			return None

		try:
			iter = gtk.TreeStore.get_iter(self, path)

		except ValueError:
			iter = None

		return iter


	def get_path(self, iter):
		"Gets a path from an iter"

		if iter is None:
			return None

		else:
			return gtk.TreeStore.get_path(self, iter)


	def has_contents(self):
		"Checks if the TreeStore contains any nodes"

		return self.iter_n_children(None) > 0


	def iter_compare(self, iter1, iter2):
		"Checks if two iters point to the same node"

		return self.get_path(iter1) == self.get_path(iter2)


	def iter_traverse_next(self, iter):
		"Gets the 'logically next' iter"
		
		# get the first child, if any
		child = self.iter_nth_child(iter, 0)
		if child is not None:
			return child

		# check for a sibling or, if not found, a sibling of any ancestors
		parent = iter
		while parent is not None:
			sibling = parent.copy()
			sibling = self.iter_next(sibling)

			if sibling is not None:
				return sibling

			parent = self.iter_parent(parent)

		return None


	def iter_traverse_prev(self, iter):
		"Gets the 'logically previous' iter"

		# get the previous sibling, or parent, of the iter - if any
		if iter is not None:
			parent = self.iter_parent(iter)
			index = self.get_path(iter)[-1]

			# if no sibling is found, return the parent
			if index == 0:
				return parent

			# otherwise, get the sibling
			iter = self.iter_nth_child(parent, index - 1)

		# get the last, deepest child of the sibling or root, if any
		while self.iter_n_children(iter) > 0:
			iter = self.iter_nth_child(iter, self.iter_n_children(iter) - 1)

		return iter



class TreeView(gtk.TreeView):

	def __init__(self, model = None):
		gtk.TreeView.__init__(self, model)
		self.set_headers_visible(gtk.FALSE)
		self.model = model

		self.selection = self.get_selection()
		self.selection.set_mode(gtk.SELECTION_MULTIPLE)

		self.connect("button_press_event", self.__cb_buttonpress)
		self.connect("key_press_event", self.__cb_keypress)


	def __cb_buttonpress(self, object, data):
		if data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS:
			path = self.get_path_at_pos(int(data.x), int(data.y))

			if path is not None:
				iter = self.model.get_iter(path[0])
				self.toggle_expanded(iter)
				self.emit("doubleclick", iter)


	def __cb_keypress(self, object, data):
		if data.keyval == 32:
			self.toggle_expanded(self.get_active())


	def collapse_row(self, iter):
		gtk.TreeView.collapse_row(self, self.model.get_path(iter))


	def expand_row(self, iter):
		if iter is not None and self.model.iter_n_children(iter) > 0:
			gtk.TreeView.expand_row(self, self.model.get_path(iter), gtk.FALSE)


	def expand_to_iter(self, iter):
		path = self.model.get_path(iter)
		for i in range(len(path)):
			iter = self.model.get_iter(path[0:i])
			self.expand_row(iter)


	def get_active(self):
		iter = self.model.get_iter(self.get_cursor()[0])

		if iter == None or self.selection.iter_is_selected(iter) == gtk.FALSE:
			return None

		return iter


	def get_selected(self):
		list = []
		self.selection.selected_foreach(lambda model, path, iter: list.append(iter))
		return list


	def select(self, iter):
		if iter == None:
			self.unselect_all()
		else:
			self.expand_to_iter(iter)
			self.set_cursor(self.model.get_path(iter))


	def select_all(self):
		self.selection.select_all()
		self.selection.emit("changed")
		self.emit("cursor_changed")


	def set_model(self, model):
		gtk.TreeView.set_model(self, model)
		self.model = model


	def toggle_expanded(self, iter):
		if iter == None:
			return
		elif self.row_expanded(self.model.get_path(iter)):
			self.collapse_row(iter)
		else:
			self.expand_row(iter)


	def unselect_all(self):
		self.selection.unselect_all()
		self.selection.emit("changed")
		self.emit("cursor_changed")
		self.emit("unselect_all")


gobject.signal_new("doubleclick", TreeView, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))



class Toolbar(gtk.Toolbar):
	"A Toolbar subclass"

	def __init__(self):
		gtk.Toolbar.__init__(self)

	def append_stock(self, stock, tooltip, callback = None):
		"Appends a stock item to the toolbar"

		return self.insert_stock(stock, tooltip, None, callback, "", -1)


# more extensive custom widgets
class EntryDropdown(OptionMenu):

	def __init__(self):
		revelation.widget.OptionMenu.__init__(self)

		typelist = revelation.entry.ENTRYDATA.keys()
		typelist.sort()
		typelist.remove(revelation.entry.ENTRY_FOLDER)
		typelist.insert(0, revelation.entry.ENTRY_FOLDER)

		for type in typelist:
			item = revelation.widget.ImageMenuItem(revelation.entry.ENTRYDATA[type]["icon"], revelation.entry.ENTRYDATA[type]["name"])
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

		self.image = Image()
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

