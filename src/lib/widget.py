#
# Revelation 0.3.3 - a password manager for GNOME 2
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

import gobject, gtk, gtk.gdk, gnome.ui, revelation, os.path, gconf, bonobo.ui


# simple subclasses for gtk widgets

class Button(gtk.Button):
	"A normal button"

	def __init__(self, label, callback = None):
		gtk.Button.__init__(self, label)

		self.set_use_stock(gtk.TRUE)

		if callback is not None:
			self.connect("clicked", callback)



class CheckButton(gtk.CheckButton):
	"A checkbutton"

	def __init__(self, label = None):
		gtk.CheckButton.__init__(self, label)



class ComboBox(gtk.ComboBox):
	"A combo box"

	def __init__(self, icons = gtk.FALSE):
		gtk.ComboBox.__init__(self)

		self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
		self.set_model(self.model)

		if icons == gtk.TRUE:
			cr = gtk.CellRendererPixbuf()
			cr.set_fixed_size(gtk.icon_size_lookup(revelation.stock.ICON_SIZE_DROPDOWN)[0] + 5, -1)
			self.pack_start(cr, gtk.FALSE)
			self.add_attribute(cr, "stock-id", 1)

		cr = gtk.CellRendererText()
		self.pack_start(cr, gtk.TRUE)
		self.add_attribute(cr, "text", 0)

		self.connect("realize", self.__cb_show)


	def __cb_show(self, widget, data = None):
		"Callback for when the widget is shown"

		if self.get_active() == -1:
			self.set_active(0)


	def append_item(self, text, stock = None, data = None):
		"Appends an item to the liststore"

		self.model.append( [ text, stock, data ] )


	def get_active_item(self):
		"Returns a tuple with data for the currently active item"

		index = self.get_active()
		iter = self.model.iter_nth_child(None, index)

		return self.model.get(iter, 0, 1, 2)


	def replace_item(self, index, text, stock = None, data = None):
		"Replaces an item in the liststore"

		iter = self.model.iter_nth_child(None, index)

		if iter is None:
			self.append_item(text, stock, data)

		else:
			self.model.set(
				iter,
				0, text,
				1, stock,
				2, data
			)



class ComboBoxEntry(gtk.ComboBoxEntry):
	"An entry with a combo box list"

	def __init__(self, list = []):
		gtk.ComboBoxEntry.__init__(self)

		self.model = gtk.ListStore(gobject.TYPE_STRING)
		self.set_model(self.model)
		self.set_text_column(0)

		completion = gtk.EntryCompletion()
		completion.set_model(self.model)
		completion.set_text_column(0)
		completion.set_minimum_key_length(1)
		self.child.set_completion(completion)

		if list is not None:
			for item in list:
				self.model.append([ item ])


	def get_text(self):
		"Returns the text of the entry"

		return self.child.get_text()


	def set_text(self, text):
		"Sets the text of the entry"

		self.child.set_text(text)



class Entry(gtk.Entry):
	"An input entry"

	def __init__(self, text = None):
		gtk.Entry.__init__(self)

		self.set_activates_default(gtk.TRUE)
		self.set_text(text)


	def set_text(self, text):
		"Sets the entry contents"

		if text == None:
			text = ""

		gtk.Entry.set_text(self, text)



class HPaned(gtk.HPaned):
	"Horizontal pane"

	def __init__(self, content_left = None, content_right = None, position = None):
		gtk.HPaned.__init__(self)
		self.set_border_width(6)

		if content_left is not None:
			self.pack1(content_left, gtk.TRUE, gtk.TRUE)

		if content_right is not None:
			self.pack2(content_right, gtk.TRUE, gtk.TRUE)

		if position is not None:
			self.set_position(position)



class HBox(gtk.HBox):
	"A horizontal container"

	def __init__(self, *args):
		gtk.HBox.__init__(self)
		self.set_spacing(6)
		self.set_border_width(0)

		for widget in args:
			self.pack_start(widget)



class HRef(gnome.ui.HRef):
	"A button containing a link"

	def __init__(self, url, text):
		gnome.ui.HRef.__init__(self, url, text)
		self.get_children()[0].set_alignment(0, 0.5)



class Image(gtk.Image):
	"A widget for displaying an image"

	def __init__(self, stock = None, size = None):
		gtk.Image.__init__(self)

		if stock is not None:
			self.set_from_stock(stock, size)



class ImageMenuItem(gtk.ImageMenuItem):
	"A menuitem with a stock icon"

	def __init__(self, stock, text = None):
		gtk.ImageMenuItem.__init__(self, stock)

		self.label = self.get_children()[0]
		self.image = self.get_children()[1]

		if text is not None:
			self.set_text(text)


	def set_stock(self, stock):
		"Set the stock item to use as icon"

		self.image.set_from_stock(stock, gtk.ICON_SIZE_MENU)


	def set_text(self, text):
		"Set the item text"

		self.label.set_text(text)



class Label(gtk.Label):
	"A text label"

	def __init__(self, text = None, justify = gtk.JUSTIFY_LEFT):
		gtk.Label.__init__(self)

		self.set_text(text)
		self.set_justify(justify)
		self.set_use_markup(gtk.TRUE)
		self.set_line_wrap(gtk.TRUE)

		if justify == gtk.JUSTIFY_LEFT:
			self.set_alignment(0, 0.5)

		elif justify == gtk.JUSTIFY_CENTER:
			self.set_alignment(0.5, 0.5)

		elif justify == gtk.JUSTIFY_RIGHT:
			self.set_alignment(1, 0.5)


	def set_text(self, text):
		"Sets the text of the label"

		if text is not None:
			gtk.Label.set_markup(self, text)



class Notebook(gtk.Notebook):
	"A notebook (tabbed view)"

	def __init__(self):
		gtk.Notebook.__init__(self)


	def create_page(self, title):
		"Creates a notebook page"

		page = NotebookPage()
		self.append_page(page, Label(title))

		return page



class ScrolledWindow(gtk.ScrolledWindow):
	"A scrolled window which partially displays a different widget"

	def __init__(self, contents = None):
		gtk.ScrolledWindow.__init__(self)

		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		if contents is not None:
			self.add(contents)



class SpinButton(gtk.SpinButton):
	"An entry for numbers"

	def __init__(self, adjustment = None, climb_rate = 0.0, digits = 0):
		gtk.SpinButton.__init__(self, adjustment, climb_rate, digits)

		self.set_increments(1, 5)
		self.set_range(0, 100000)
		self.set_numeric(gtk.TRUE)



class Statusbar(gtk.Statusbar):
	"A window statusbar"

	def __init__(self):
		gtk.Statusbar.__init__(self)

		self.contextid = self.get_context_id("statusbar")


	def clear(self):
		"Clears the statusbar"

		self.pop(self.contextid)


	def set_status(self, text):
		"Displays a text in the statusbar"

		self.clear()
		self.push(self.contextid, text)



class TextView(gtk.TextView):
	"A text view"

	def __init__(self, buffer = None, text = None):
		gtk.TextView.__init__(self, buffer)

		if text is not None:
			self.get_buffer().set_text(text)

		self.set_editable(gtk.FALSE)
		self.set_wrap_mode(gtk.WRAP_NONE)
		self.set_cursor_visible(gtk.FALSE)



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
	"A widget for displaying a tree"

	def __init__(self, model = None):
		gtk.TreeView.__init__(self, model)
		self.set_headers_visible(gtk.FALSE)
		self.model = model

		self.selection = self.get_selection()
		self.selection.set_mode(gtk.SELECTION_MULTIPLE)

		self.connect("button_press_event", self.__cb_buttonpress)
		self.connect("key_press_event", self.__cb_keypress)


	def __cb_buttonpress(self, object, data):
		"Callback for handling mouse clicks"

		# handle doubleclick
		if data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS:
			path = self.get_path_at_pos(int(data.x), int(data.y))

			if path is not None:
				iter = self.model.get_iter(path[0])
				self.toggle_expanded(iter)
				self.emit("doubleclick", iter)

		# display popup on right-click
		if data.button == 3:
			path = self.get_path_at_pos(int(data.x), int(data.y))

			if path is None:
				self.unselect_all()

			elif self.selection.iter_is_selected(self.model.get_iter(path[0])) == gtk.FALSE:
				self.set_cursor(path[0], path[1], gtk.FALSE)

			# create the menu
			self.emit("popup", data)

			return gtk.TRUE


	def __cb_keypress(self, object, data):
		"Callback for handling key presses"

		# expand/collapse an item when space is pressed
		if data.keyval == 32:
			self.toggle_expanded(self.get_active())


	def collapse_row(self, iter):
		"Collapse a tree row"

		gtk.TreeView.collapse_row(self, self.model.get_path(iter))


	def expand_row(self, iter):
		"Expand a tree row"

		if iter is not None and self.model.iter_n_children(iter) > 0:
			gtk.TreeView.expand_row(self, self.model.get_path(iter), gtk.FALSE)


	def expand_to_iter(self, iter):
		"Expand all items up to and including a given iter"

		path = self.model.get_path(iter)

		for i in range(len(path)):
			iter = self.model.get_iter(path[0:i])
			self.expand_row(iter)


	def get_active(self):
		"Get the currently active row"

		iter = self.model.get_iter(self.get_cursor()[0])

		if iter is None or self.selection.iter_is_selected(iter) == gtk.FALSE:
			return None

		return iter


	def get_selected(self):
		"Get a list of currently selected rows"

		list = []
		self.selection.selected_foreach(lambda model, path, iter: list.append(iter))

		return list


	def select(self, iter):
		"Select a particular row"

		if iter == None:
			self.unselect_all()

		else:
			self.expand_to_iter(iter)
			self.set_cursor(self.model.get_path(iter))


	def select_all(self):
		"Select all rows in the tree"

		self.selection.select_all()
		self.selection.emit("changed")
		self.emit("cursor_changed")


	def set_model(self, model):
		"Change the tree model which is being displayed"

		gtk.TreeView.set_model(self, model)
		self.model = model


	def toggle_expanded(self, iter):
		"Toggle the expanded state of a row"

		if iter is None:
			return

		elif self.row_expanded(self.model.get_path(iter)):
			self.collapse_row(iter)

		else:
			self.expand_row(iter)


	def unselect_all(self):
		"Unselect all rows in the tree"

		self.selection.unselect_all()
		self.selection.emit("changed")
		self.emit("cursor_changed")
		self.emit("unselect_all")


gobject.signal_new("doubleclick", TreeView, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new("popup", TreeView, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))



class Toolbar(gtk.Toolbar):
	"A Toolbar subclass"

	def __init__(self):
		gtk.Toolbar.__init__(self)


	def append_stock(self, stock, tooltip, callback = None):
		"Appends a stock item to the toolbar"

		return self.insert_stock(stock, tooltip, None, callback, "", -1)


	def append_widget(self, widget, tooltip = None):
		"Appends a widget to the toolbar"

		return gtk.Toolbar.append_widget(self, widget, tooltip, tooltip)



class UIManager(gtk.UIManager):
	"UI item manager"

	def __init__(self):
		gtk.UIManager.__init__(self)

		self.connect("connect-proxy", self.__cb_connect_proxy)


	def __cb_connect_proxy(self, uimanager, action, widget):
		"Callback for connecting proxies to an action"

		if type(widget) in [ gtk.MenuItem, gtk.ImageMenuItem, gtk.CheckMenuItem ]:
			widget.tooltip = action.get_property("tooltip")


	def append_action_group(self, actiongroup):
		"Appends an action group"

		gtk.UIManager.insert_action_group(self, actiongroup, len(self.get_action_groups()))


	def get_action(self, name):
		"Looks up an action in the managers action groups"

		for actiongroup in self.get_action_groups():
			action = actiongroup.get_action(name)

			if action is not None:
				return action

		else:
			return None


	def get_action_group(self, name):
		"Returns the named action group"

		for actiongroup in self.get_action_groups():
			if actiongroup.get_name() == name:
				return actiongroup

		else:
			return None



class VBox(gtk.VBox):
	"A vertical container"

	def __init__(self, *args):
		gtk.VBox.__init__(self)
		self.set_spacing(6)
		self.set_border_width(0)

		for widget in args:
			self.pack_start(widget)



# more extensive custom widgets

class EntryDropdown(ComboBox):
	"A dropdown menu with all available entry types"

	def __init__(self):
		ComboBox.__init__(self, gtk.TRUE)

		for entry in revelation.entry.get_entry_list():
			self.append_item(entry.typename, entry.icon, entry)


	def get_type(self):
		"Get the currently active type"

		try:
			return self.get_active_item()[2]

		except AttributeError:
			return None


	def set_type(self, entrytype):
		"Set the active type"

		for i in range(self.model.iter_n_children(None)):
			iter = self.model.iter_nth_child(None, i)

			if self.model.get_value(iter, 2) is entrytype:
				self.set_active(i)



class FileEntry(HBox):
	"An entry for file names with a Browse button"

	def __init__(self, title = None, filename = None):
		HBox.__init__(self)

		if title is None:
			self.title = "Select File"

		else:
			self.title = title

		self.entry = Entry()
		self.pack_start(self.entry)

		self.button = Button("Browse...", self.__cb_filesel)
		self.pack_start(self.button, gtk.FALSE, gtk.FALSE)

		if filename is not None:
			self.set_filename(filename)


	def __cb_filesel(self, object, data = None):
		"Displays a file selector when Browse is pressed"

		fsel = revelation.dialog.FileSelector(None, self.title)
		fsel.set_modal(gtk.TRUE)

		if self.get_filename() != "":
			fsel.set_filename(self.get_filename())

		try:
			self.set_filename(fsel.run())

		except revelation.CancelError:
			pass


	def get_filename(self):
		"Gets the current filename"

		return self.entry.get_text()


	def get_text(self):
		"Returns the current entry text"

		return self.entry.get_text()


	def set_filename(self, filename):
		"Sets the filename of the entry"

		self.entry.set_text(os.path.normpath(filename))
		self.entry.set_position(-1)


	def set_text(self, text):
		"Wrapper to emulate Entry"

		self.entry.set_text(text)



class ImageLabel(gtk.Alignment):
	"A label with an image"

	def __init__(self, stock, size, text):
		gtk.Alignment.__init__(self, 0.5, 0.5, 0, 0)

		self.hbox = HBox()
		self.add(self.hbox)

		self.image = Image()
		self.hbox.pack_start(self.image, gtk.FALSE, gtk.FALSE)
		self.set_stock(stock, size)

		self.label = Label(text, gtk.JUSTIFY_CENTER)
		self.hbox.pack_start(self.label)


	def set_stock(self, stock, size):
		"Sets the label icon"

		self.image.set_from_stock(stock, size)


	def set_text(self, text):
		"Sets the label text"

		self.label.set_text(text)



class InputSection(VBox):
	"A section of input fields"

	def __init__(self, title = None, sizegroup = None, description = None):
		VBox.__init__(self)

		self.title = None
		self.description = None

		if sizegroup is None:
			self.sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

		else:
			self.sizegroup = sizegroup

		if title is not None:
			self.title = Label("<span weight=\"bold\">" + revelation.misc.escape_markup(title) + "</span>")
			self.pack_start(self.title, gtk.FALSE)

		if description is not None:
			self.description = Label(revelation.misc.escape_markup(description))
			self.pack_start(self.description, gtk.FALSE)


	def add_inputrow(self, title, widget):
		"Adds an input row to the section"

		row = HBox()
		self.pack_start(row, gtk.FALSE, gtk.FALSE)

		if self.title is not None:
			row.pack_start(Label("   "), gtk.FALSE, gtk.FALSE)

		if title is not None:
			label = Label(revelation.misc.escape_markup(title) + ":")
			self.sizegroup.add_widget(label)
			row.pack_start(label, gtk.FALSE, gtk.FALSE)

		row.pack_start(widget)

		return row


	def clear(self):
		"Clears the input section"

		for child in self.get_children():
			if child not in [ self.label, self.description ]:
				child.destroy()



class NotebookPage(VBox):
	"A notebook page"

	def __init__(self):
		VBox.__init__(self)

		self.sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.set_border_width(12)
		self.set_spacing(18)


	def add_section(self, title, description = None):
		"Adds an input section to the dialog"

		section = InputSection(title, self.sizegroup, description)
		self.pack_start(section, gtk.FALSE, gtk.FALSE)

		return section



class PasswordEntry(Entry):
	"An entry which edits a password (follows the 'show passwords' preference"

	def __init__(self, password = None):
		Entry.__init__(self, password)

		revelation.data.config_connect("view/passwords", self.__cb_gconf_password)
		self.set_visibility(revelation.data.config_get("view/passwords"))


	def __cb_gconf_password(self, client, id, entry, data):
		"Callback which shows or hides the password"

		self.set_visibility(entry.get_value().get_bool())



class PasswordEntryGenerate(HBox):
	"A password entry with a generator button"

	def __init__(self, password = None):
		HBox.__init__(self)

		self.entry = PasswordEntry(password)
		self.pack_start(self.entry)

		self.button = Button("Generate", lambda w: self.entry.set_text(revelation.misc.generate_password()))
		self.pack_start(self.button, gtk.FALSE, gtk.FALSE)


	def __getattr__(self, name):
		"Proxy lookups for missing attributes to the entry"

		return getattr(self.entry, name)



class PasswordLabel(Label):
	"A label which displays a passwords (follows the 'show passwords' preference)"

	def __init__(self, password, justify = gtk.JUSTIFY_LEFT):
		Label.__init__(self, password, justify)
		self.password = password

		revelation.data.config_connect("view/passwords", self.__cb_gconf_password)

		if revelation.data.config_get("view/passwords") == gtk.TRUE:
			self.show_password()

		else:
			self.hide_password()


	def __cb_gconf_password(self, client, id, entry, data):
		"Callback which displays or hides the password"

		if entry.get_value().get_bool() == gtk.TRUE:
			self.show_password()

		else:
			self.hide_password()


	def hide_password(self):
		"Hides the password"

		self.set_text("******")
		self.set_selectable(gtk.FALSE)


	def show_password(self):
		"Shows the password"

		self.set_text(self.password)
		self.set_selectable(gtk.TRUE)


# application components
class App(gnome.ui.App):
	"An application window"

	def __init__(self, appname):
		gnome.ui.App.__init__(self, appname, appname)
		self.appname = appname

		self.statusbar = Statusbar()
		self.set_statusbar(self.statusbar)

		self.uimanager = UIManager()
		self.add_accel_group(self.uimanager.get_accel_group())


	def __cb_toolbar_hide(self, object, name):
		"Hides the toolbar dock when the toolbar is hidden"

		self.get_dock_item_by_name(name).hide()


	def __cb_toolbar_show(self, object, name):
		"Shows the toolbar dock when the toolbar is hidden"

		self.get_dock_item_by_name(name).show()


	def __cb_menudesc(self, item, show):
		"Displays menu descriptions in the statusbar"

		if show:
			self.statusbar.set_status(item.tooltip)

		else:
			self.statusbar.clear()


	def __connect_menu_statusbar(self, menu):
		"Connects a menu to the statusbar, for tooltip displays"

		for item in menu.get_children():
			if type(item) in [ gtk.MenuItem, gtk.ImageMenuItem, gtk.CheckMenuItem ]:
				item.connect("select", self.__cb_menudesc, gtk.TRUE)
				item.connect("deselect", self.__cb_menudesc, gtk.FALSE)


	def add_toolbar(self, toolbar, name, band):
		"Adds a toolbar"

		behavior = bonobo.ui.DOCK_ITEM_BEH_EXCLUSIVE

		if revelation.data.config_get("/desktop/gnome/interface/toolbar_detachable") == gtk.FALSE:
			behavior |= bonobo.ui.DOCK_ITEM_BEH_LOCKED

		gnome.ui.App.add_toolbar(self, toolbar, name, behavior, 0, band, 0, 0)

		toolbar.connect("show", self.__cb_toolbar_show, name)
		toolbar.connect("hide", self.__cb_toolbar_hide, name)

		toolbar.show_all()


	def popup(self, menu, button, time):
		"Displays a popup menu"

		self.__connect_menu_statusbar(menu)
		menu.popup(None, None, None, button, time)


	def run(self):
		"Runs the application"

		self.show_all()
		gtk.main()


	def set_menus(self, menubar):
		"Sets the menus"

		for menubaritem in menubar.get_children():
			self.__connect_menu_statusbar(menubaritem.get_submenu())

		gnome.ui.App.set_menus(self, menubar)


	def set_title(self, title):
		"Sets the window title"

		gnome.ui.App.set_title(self, title + " - " + self.appname)


	def set_toolbar(self, toolbar):
		"Sets the application toolbar"

		gnome.ui.App.set_toolbar(self, toolbar)
		toolbar.connect("hide", self.__cb_toolbar_hide, "Toolbar")
		toolbar.connect("show", self.__cb_toolbar_show, "Toolbar")



class DataView(VBox):
	"An UI component for displaying an entry"

	def __init__(self):
		VBox.__init__(self)
		self.set_spacing(15)
		self.set_border_width(10)

		self.size_name = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.size_value = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

		self.entry = None


	def clear(self, force = gtk.FALSE):
		"Clears the data view"

		# only clear if containing an entry, or if forced
		if force == gtk.FALSE and self.entry is None:
			return

		self.entry = None

		for child in self.get_children():
			child.destroy()


	def display_entry(self, entry):
		"Displays an entry"

		if entry is None:
			self.clear()
			return

		self.clear(gtk.TRUE)
		self.entry = entry

		# set up metadata display
		metabox = VBox()
		self.pack_start(metabox)

		metabox.pack_start(ImageLabel(
			entry.icon, revelation.stock.ICON_SIZE_DATAVIEW,
			"<span size=\"large\" weight=\"bold\">" + revelation.misc.escape_markup(entry.name) + "</span>"
		))

		metabox.pack_start(Label("<span weight=\"bold\">" + entry.typename + (entry.description != "" and "; " or "") + "</span>" + revelation.misc.escape_markup(entry.description), gtk.JUSTIFY_CENTER))

		# set up field list
		rows = []

		for field in entry.fields:

			if field.value == "":
				continue

			row = HBox()
			rows.append(row)

			label = Label("<span weight=\"bold\">" + revelation.misc.escape_markup(field.name) + ":</span>", gtk.JUSTIFY_RIGHT)
			self.size_name.add_widget(label)
			row.pack_start(label, gtk.FALSE, gtk.FALSE)

			widget = field.generate_display_widget()
			self.size_value.add_widget(widget)
			row.pack_start(widget, gtk.FALSE, gtk.FALSE)


		if len(rows) > 0:
			fieldlist = VBox()
			fieldlist.set_spacing(2)
			self.pack_start(fieldlist)

			for row in rows:
				fieldlist.pack_start(row, gtk.FALSE, gtk.FALSE)

		# display updatetime
		if type(entry) != revelation.entry.FolderEntry:
			self.pack_start(Label("Updated " + entry.get_updated_age() + " ago; \n" + entry.get_updated_iso(), gtk.JUSTIFY_CENTER))

		self.show_all()


	def display_info(self):
		"Displays info about the application"

		self.clear(gtk.TRUE)

		self.pack_start(ImageLabel(
			revelation.stock.STOCK_REVELATION, revelation.stock.ICON_SIZE_LOGO,
			"<span size=\"x-large\" weight=\"bold\">" + revelation.APPNAME + " " + revelation.VERSION + "</span>"
		))

		self.pack_start(Label("A password manager for GNOME 2"))

		gpl = "\nThis program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details."
		label = Label("<span size=\"x-small\">" + gpl + "</span>", gtk.JUSTIFY_LEFT)
		label.set_size_request(250, -1)
		self.pack_start(label)

		self.show_all()


	def pack_start(self, widget):
		"Adds a widget to the data view"

		alignment = gtk.Alignment(0.5, 0.5, 0, 0)
		alignment.add(widget)
		VBox.pack_start(self, alignment)



class Searchbar(Toolbar):
	"Search bar"

	def __init__(self):
		Toolbar.__init__(self)

		self.label	= Label("  Search for: ")
		self.entry	= Entry()
		self.button	= Button(" Find ")

		self.append_widget(self.label)
		self.append_widget(self.entry)
		self.append_widget(self.button)

		self.entry.connect("changed", lambda w: self.button.set_sensitive(self.entry.get_text() != ""))
		self.entry.connect("key-press-event", self.__cb_key_press)
		self.entry.emit("changed")


	def __cb_key_press(self, widget, data = None):
		"Callback for key presses"

		# handle return
		if data.keyval == 65293 and widget.get_text() != "":
			self.button.clicked()
			return gtk.TRUE



class Tree(TreeView):
	"The entry tree"

	def __init__(self, datastore = None):
		TreeView.__init__(self, datastore)

		self.connect("doubleclick", self.__cb_doubleclick)
		self.connect("row-expanded", self.__cb_row_expanded)
		self.connect("row-collapsed", self.__cb_row_collapsed)

		column = gtk.TreeViewColumn()
		self.append_column(column)

		cr = gtk.CellRendererPixbuf()
		column.pack_start(cr, gtk.FALSE)
		column.add_attribute(cr, "stock-id", revelation.data.ENTRYSTORE_COL_ICON)
		cr.set_property("stock-size", revelation.stock.ICON_SIZE_TREEVIEW)

		cr = gtk.CellRendererText()
		column.pack_start(cr, gtk.TRUE)
		column.add_attribute(cr, "text", revelation.data.ENTRYSTORE_COL_NAME)


	def __cb_doubleclick(self, widget, iter):
		"Callback for doubleclick, stops signal propagation when on a folder"

		if type(self.model.get_entry(iter)) == revelation.entry.FolderEntry:
			self.stop_emission("doubleclick")


	def __cb_row_collapsed(self, object, iter, extra):
		"Updates folder icons when collapsed"

		self.model.set_folder_state(iter, gtk.FALSE)


	def __cb_row_expanded(self, object, iter, extra):
		"Updates folder icons when expanded"

		# make sure all children are collapsed (some may have lingering expand icons)
		for i in range(self.model.iter_n_children(iter)):
			child = self.model.iter_nth_child(iter, i)

			if self.row_expanded(self.model.get_path(child)) == gtk.FALSE:
				self.model.set_folder_state(child, gtk.FALSE)

		self.model.set_folder_state(iter, gtk.TRUE)


	def set_model(self, model):
		"Sets the model displayed by the tree view"

		TreeView.set_model(self, model)

		if model is None:
			return

		for i in range(model.iter_n_children(None)):
			model.set_folder_state(model.iter_nth_child(None, i), gtk.FALSE)

