#
# Revelation 0.4.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for UI functionality
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

import config, data, dialog, entry, io, util

import bonobo.ui, gobject, gtk, gnome.ui, os, pango, pwd, time, xml.dom.minidom
from xml.parsers.expat import ExpatError
from gnome.ui import HRef as LinkButton


STOCK_ADD			= "revelation-add"
STOCK_DISCARD			= "revelation-discard"
STOCK_EDIT			= "revelation-edit"
STOCK_EXPORT			= "revelation-export"
STOCK_GENERATE			= "revelation-generate"
STOCK_IMPORT			= "revelation-import"
STOCK_GOTO			= "revelation-goto"
STOCK_LOCK			= "revelation-lock"
STOCK_NEXT			= "revelation-next"
STOCK_OVERWRITE			= "revelation-overwrite"
STOCK_PASSWORD_CHANGE		= "revelation-password-change"
STOCK_PREVIOUS			= "revelation-previous"
STOCK_RELOAD			= "revelation-reload"
STOCK_REMOVE			= "revelation-remove"


STOCK_ENTRY_FOLDER		= "revelation-folder"
STOCK_ENTRY_FOLDER_OPEN		= "revelation-folder-open"
STOCK_ENTRY_CREDITCARD		= "revelation-account-creditcard"
STOCK_ENTRY_CRYPTOKEY		= "revelation-account-cryptokey"
STOCK_ENTRY_DATABASE		= "revelation-account-database"
STOCK_ENTRY_DOOR		= "revelation-account-door"
STOCK_ENTRY_EMAIL		= "revelation-account-email"
STOCK_ENTRY_FTP			= "revelation-account-ftp"
STOCK_ENTRY_GENERIC		= "revelation-account-generic"
STOCK_ENTRY_PHONE		= "revelation-account-phone"
STOCK_ENTRY_SHELL		= "revelation-account-shell"
STOCK_ENTRY_WEBSITE		= "revelation-account-website"

STOCK_REVELATION		= "revelation-revelation"


ICON_SIZE_DATAVIEW		= gtk.icon_size_from_name("revelation-dataview")
ICON_SIZE_DROPDOWN		= gtk.icon_size_from_name("revelation-dropdown")
ICON_SIZE_LOGO			= gtk.icon_size_from_name("revelation-logo")
ICON_SIZE_TREEVIEW		= gtk.icon_size_from_name("revelation-treeview")

if ICON_SIZE_DATAVIEW == gtk.ICON_SIZE_INVALID:
	ICON_SIZE_DATAVIEW	= gtk.icon_size_register("revelation-dataview", 24, 24)

if ICON_SIZE_DROPDOWN == gtk.ICON_SIZE_INVALID:
	ICON_SIZE_DROPDOWN	= gtk.icon_size_register("revelation-dropdown", 18, 18)

if ICON_SIZE_LOGO == gtk.ICON_SIZE_INVALID:
	ICON_SIZE_LOGO		= gtk.icon_size_register("revelation-logo", 32, 32)

if ICON_SIZE_TREEVIEW == gtk.ICON_SIZE_INVALID:
	ICON_SIZE_TREEVIEW	= gtk.icon_size_register("revelation-treeview", 18, 18)



##### EXCEPTIONS #####

class DataError(Exception):
	"Exception for invalid data"
	pass



##### FUNCTIONS #####

def config_bind(cfg, key, widget):
	"Binds a config key to a UI widget"

	if isinstance(widget, gtk.CheckMenuItem) or isinstance(widget, gtk.ToggleButton):
		signal	= "toggled"
		cb_get	= lambda c,v,w:	w.set_active(v)
		cb_set	= lambda w,k:	cfg.set(k, w.get_active())

	elif isinstance(widget, gtk.SpinButton):
		signal	= "changed"
		cb_get	= lambda c,v,w:	w.set_value(v)
		cb_set	= lambda w,k:	cfg.set(k, w.get_value())

	elif isinstance(widget, gtk.Entry) or isinstance(widget, FileEntry):
		signal	= "changed"
		cb_get	= lambda c,v,w:	w.set_text(v)
		cb_set	= lambda w,k:	cfg.set(k, w.get_text())

	else:
		raise config.ConfigError

	id = cfg.monitor(key, cb_get, widget)
	widget.connect(signal, cb_set, key)
	widget.connect("destroy", lambda w,i: cfg.forget(i), id)

	return id


def generate_field_display_widget(field, cfg = None):
	"Generates a widget for displaying a field value"

	if field.datatype == entry.DATATYPE_EMAIL:
		widget = LinkButton("mailto:%s" % field.value, util.escape_markup(field.value))

	elif field.datatype == entry.DATATYPE_PASSWORD:
		widget = PasswordLabel(util.escape_markup(field.value), cfg)

	elif field.datatype == entry.DATATYPE_URL:
		widget = LinkButton(field.value, util.escape_markup(field.value))

	else:
		widget = Label(util.escape_markup(field.value))
		widget.set_selectable(True)

	return widget


def generate_field_edit_widget(field, cfg = None, userdata = None):
	"Generates a widget for editing a field"

	if type(field) == entry.PasswordField:
		widget = PasswordEntryGenerate(cfg)

	elif type(field) == entry.UsernameField:
		widget = ComboBoxEntry(userdata)

	elif field.datatype == entry.DATATYPE_FILE:
		widget = FileEntry()

	elif field.datatype == entry.DATATYPE_PASSWORD:
		widget = PasswordEntry(cfg)

	else:
		widget = Entry()

	widget.set_text(field.value)

	return widget



##### CONTAINERS #####

class HBox(gtk.HBox):
	"A horizontal container"

	def __init__(self, *args):
		gtk.HBox.__init__(self)

		self.set_spacing(6)
		self.set_border_width(0)

		for widget in args:
			self.pack_start(widget)



class VBox(gtk.VBox):
	"A vertical container"

	def __init__(self, *args):
		gtk.VBox.__init__(self)

		self.set_spacing(6)
		self.set_border_width(0)

		for widget in args:
			self.pack_start(widget)



class HPaned(gtk.HPaned):
	"A horizontal pane"

	def __init__(self, left = None, right = None):
		gtk.HPaned.__init__(self)
		self.set_border_width(6)

		if left is not None:
			self.pack1(left, True, True)

		if right is not None:
			self.pack2(right, True, True)



class Notebook(gtk.Notebook):
	"A notebook (tabbed view)"

	def __init__(self):
		gtk.Notebook.__init__(self)


	def create_page(self, title):
		"Creates a notebook page"

		page = NotebookPage()
		self.append_page(page, Label(title))

		return page



class NotebookPage(VBox):
	"A notebook page"

	def __init__(self):
		VBox.__init__(self)

		self.sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.set_border_width(12)
		self.set_spacing(18)


	def add_section(self, title, description = None):
		"Adds an input section to the notebook"

		section = InputSection(title, description, self.sizegroup)
		self.pack_start(section, False, False)

		return section



class ScrolledWindow(gtk.ScrolledWindow):
	"A scrolled window for partially displaying a child widget"

	def __init__(self, contents = None):
		gtk.ScrolledWindow.__init__(self)

		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		if contents is not None:
			self.add(contents)



class Toolbar(gtk.Toolbar):
	"A Toolbar subclass"

	def __init__(self):
		gtk.Toolbar.__init__(self)


	def append_widget(self, widget):
		"Appends a widget to the toolbar"

		toolitem = gtk.ToolItem()
		toolitem.add(widget)

		self.insert(toolitem, -1)



class InputSection(VBox):
	"A section of input fields"

	def __init__(self, title = None, description = None, sizegroup = None):
		VBox.__init__(self)

		self.title	= None
		self.desc	= None
		self.sizegroup	= sizegroup

		if title is not None:
			self.title = Label("<span weight=\"bold\">%s</span>" % util.escape_markup(title))
			self.pack_start(self.title, False)

		if description is not None:
			self.desc = Label(util.escape_markup(description))
			self.pack_start(self.desc, False)

		if sizegroup is None:
			self.sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)


	def append_widget(self, title, widget):
		"Adds a widget to the section"

		row = HBox()
		row.set_spacing(12)
		self.pack_start(row, False, False)

		if self.title is not None:
			row.pack_start(Label("   "), False, False)

		if title is not None:
			label = Label("%s:" % util.escape_markup(title))
			self.sizegroup.add_widget(label)
			row.pack_start(label, False, False)

		row.pack_start(widget)


	def clear(self):
		"Removes all widgets"

		for child in self.get_children():
			if child not in ( self.title, self.desc ):
				child.destroy()



##### DISPLAY WIDGETS #####

class EventBox(gtk.EventBox):
	"A container which handles events for a widget (for tooltips etc)"

	def __init__(self, widget = None):
		gtk.EventBox.__init__(self)

		self.widget = widget

		if widget is not None:
			self.add(self.widget)



class Image(gtk.Image):
	"A widget for displaying an image"

	def __init__(self, stock = None, size = None):
		gtk.Image.__init__(self)

		if stock is not None:
			self.set_from_stock(stock, size)



class ImageLabel(gtk.Alignment):
	"A label with an image"

	def __init__(self, text, stock, size):
		gtk.Alignment.__init__(self, 0.5, 0.5, 0, 0)

		self.hbox = HBox()
		self.add(self.hbox)

		self.image = Image()
		self.hbox.pack_start(self.image, False, False)
		self.set_stock(stock, size)

		self.label = Label(text, gtk.JUSTIFY_CENTER)
		self.hbox.pack_start(self.label)


	def set_stock(self, stock, size):
		"Sets the image"

		self.image.set_from_stock(stock, size)


	def set_text(self, text):
		"Sets the label text"

		self.label.set_text(text)



class Label(gtk.Label):
	"A text label"

	def __init__(self, text = None, justify = gtk.JUSTIFY_LEFT):
		gtk.Label.__init__(self)

		self.set_text(text)
		self.set_justify(justify)
		self.set_use_markup(True)
		self.set_line_wrap(True)

		if justify == gtk.JUSTIFY_LEFT:
			self.set_alignment(0, 0.5)

		elif justify == gtk.JUSTIFY_CENTER:
			self.set_alignment(0.5, 0.5)

		elif justify == gtk.JUSTIFY_RIGHT:
			self.set_alignment(1, 0.5)


	def set_text(self, text):
		"Sets the text of the label"

		if text is None:
			gtk.Label.set_text(self, "")

		else:
			gtk.Label.set_markup(self, text)



class PasswordLabel(Label):
	"A label for displaying passwords"

	def __init__(self, password = "", cfg = None, justify = gtk.JUSTIFY_LEFT):
		Label.__init__(self, password, justify)

		self.password	= password
		self.config	= cfg
		self.clipboard	= data.Clipboard()
		self.set_selectable(True)

		if self.config is not None:
			self.config.monitor("view/passwords", lambda k,v,d: self.show_password(v))

		self.connect("populate-popup", self.__cb_popup)


	def __cb_popup(self, widget, menu):
		"Populates the popup menu"

		menuitem = ImageMenuItem(gtk.STOCK_COPY, "Copy password")
		menuitem.connect("activate", lambda w: self.clipboard.set(self.password))

		menu.insert(menuitem, 2)
		menu.show_all()


	def show_password(self, show = True):
		"Sets whether to display the password"

		if show == True:
			self.set_text(self.password)

		else:
			self.set_text("******")



class TextView(gtk.TextView):
	"A text view"

	def __init__(self, buffer = None, text = None):
		gtk.TextView.__init__(self, buffer)

		self.set_editable(False)
		self.set_wrap_mode(gtk.WRAP_NONE)
		self.set_cursor_visible(False)
		self.modify_font(pango.FontDescription("Monospace"))

		if text is not None:
			self.get_buffer().set_text(text)



##### TEXT ENTRIES #####

class Entry(gtk.Entry):
	"A normal text entry"

	def __init__(self, text = None):
		gtk.Entry.__init__(self)

		self.set_activates_default(True)
		self.set_text(text)


	def set_text(self, text):
		"Sets the entry contents"

		if text is None:
			text = ""

		gtk.Entry.set_text(self, text)



class ComboBoxEntry(gtk.ComboBoxEntry):
	"An entry with a combo box list"

	def __init__(self, list = []):
		gtk.ComboBoxEntry.__init__(self)

		self.child.set_activates_default(True)

		self.model = gtk.ListStore(gobject.TYPE_STRING)
		self.set_model(self.model)
		self.set_text_column(0)

		self.completion = gtk.EntryCompletion()
		self.completion.set_model(self.model)
		self.completion.set_text_column(0)
		self.completion.set_minimum_key_length(1)
		self.child.set_completion(self.completion)

		if list is not None:
			self.set_values(list)


	def get_text(self):
		"Returns the text of the entry"

		return self.child.get_text()


	def set_text(self, text):
		"Sets the text of the entry"

		if text is None:
			self.child.set_text("")

		else:
			self.child.set_text(text)


	def set_values(self, list):
		"Sets the values for the dropdown"

		self.model.clear()

		for item in list:
			self.model.append((item,))



class FileEntry(HBox):
	"A file entry"

	def __init__(self, title = None, file = None, type = gtk.FILE_CHOOSER_ACTION_OPEN):
		HBox.__init__(self)

		self.title = title is not None and title or "Select File"
		self.type = type

		self.entry = Entry()
		self.entry.connect("changed", lambda w: self.emit("changed"))
		self.pack_start(self.entry)

		self.button = Button("Browse...", self.__cb_filesel)
		self.pack_start(self.button, False, False)

		if file is not None:
			self.set_filename(file)


	def __cb_filesel(self, widget, data = None):
		"Displays a file selector when Browse is pressed"

		try:
			fsel = dialog.FileSelector(None, self.title, self.type)

			fsel.set_filename(self.get_filename())
			self.set_filename(fsel.run())

		except dialog.CancelError:
			pass


	def get_filename(self):
		"Gets the current filename"

		return self.entry.get_text()


	def get_text(self):
		"Wrapper to emulate Entry"

		return self.entry.get_text()


	def set_filename(self, filename):
		"Sets the current filename"

		self.entry.set_text(io.file_normpath(filename))
		self.entry.set_position(-1)


	def set_text(self, text):
		"Wrapper to emulate Entry"

		self.entry.set_text(text)


gobject.type_register(FileEntry)
gobject.signal_new("changed", FileEntry, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())



class PasswordEntry(Entry):
	"An entry for editing a password (follows the 'show passwords' preference"

	def __init__(self, cfg = None, password = None):
		Entry.__init__(self, password)
		self.set_visibility(False)

		self.config	= cfg
		self.clipboard	= data.Clipboard()

		if cfg != None:
			self.config.monitor("view/passwords", lambda k,v,d: self.set_visibility(v))

		self.connect("changed", self.__cb_check_password)
		self.connect("focus-in-event", self.__cb_check_password)
		self.connect("focus-out-event", self.__cb_check_password)
		self.connect("populate-popup", self.__cb_popup)


	def __cb_check_password(self, widget, data = None):
		"Callback for changed, checks the password"

		password = self.get_text()

		if len(password) == 0 or self.is_focus() == False:
			color = Entry().rc_get_style().base[gtk.STATE_NORMAL]

		else:
			try:
				util.check_password(password)

			except ValueError:
				color = gtk.gdk.color_parse("#ffbaba")

			else:
				color = gtk.gdk.color_parse("#baffba")

		self.modify_base(gtk.STATE_NORMAL, color)


	def __cb_popup(self, widget, menu):
		"Populates the popup menu"

		menuitem = ImageMenuItem(gtk.STOCK_COPY, "Copy password")
		menuitem.connect("activate", lambda w: self.clipboard.set(self.get_text()))

		menu.insert(menuitem, 2)
		menu.show_all()



class PasswordEntryGenerate(HBox):
	"A password entry with a generator button"

	def __init__(self, cfg, password = None):
		HBox.__init__(self)
		self.config = cfg

		self.entry = PasswordEntry(cfg, password)
		self.pack_start(self.entry)

		self.button = Button("Generate", lambda w: self.generate())
		self.pack_start(self.button, False, False)


	def generate(self):
		"Generates a password for the entry"

		length = self.config.get("passwordgen/length")
		avoid_ambiguous = self.config.get("passwordgen/avoid_ambiguous")
		password = util.generate_password(length, avoid_ambiguous)

		self.entry.set_text(password)


	def get_text(self):
		"Wrapper for the entry"

		return self.entry.get_text()


	def set_text(self, text):
		"Wrapper for the entry"

		self.entry.set_text(text)



class SpinEntry(gtk.SpinButton):
	"An entry for numbers"

	def __init__(self, adjustment = None, climb_rate = 0.0, digits = 0):
		gtk.SpinButton.__init__(self, adjustment, climb_rate, digits)

		self.set_increments(1, 5)
		self.set_range(0, 100000)
		self.set_numeric(True)



##### BUTTONS #####

class Button(gtk.Button):
	"A normal button"

	def __init__(self, label, callback = None):
		gtk.Button.__init__(self, label)

		self.set_use_stock(True)

		if callback is not None:
			self.connect("clicked", callback)



class CheckButton(gtk.CheckButton):
	"A checkbutton"

	def __init__(self, label = None):
		gtk.CheckButton.__init__(self, label)



class DropDown(gtk.ComboBox):
	"A dropdown button"

	def __init__(self, icons = False):
		gtk.ComboBox.__init__(self)

		self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
		self.set_model(self.model)

		if icons == True:
			cr = gtk.CellRendererPixbuf()
			cr.set_fixed_size(gtk.icon_size_lookup(ICON_SIZE_DROPDOWN)[0] + 5, -1)
			self.pack_start(cr, False)
			self.add_attribute(cr, "stock-id", 1)

		cr = gtk.CellRendererText()
		self.pack_start(cr, True)
		self.add_attribute(cr, "text", 0)

		self.connect("realize", self.__cb_show)


	def __cb_show(self, widget, data = None):
		"Callback for when widget is shown"

		if self.get_active() == -1:
			self.set_active(0)


	def append_item(self, text, stock = None, data = None):
		"Appends an item to the dropdown"

		self.model.append( ( text, stock, data ) )


	def delete_item(self, index):
		"Removes an item from the dropdown"

		if self.model.iter_n_children(None) > index:
			iter = self.model.iter_nth_child(None, index)
			self.model.remove(iter)


	def get_active_item(self):
		"Returns a tuple with data for the current item"

		iter = self.model.iter_nth_child(None, self.get_active())
		return self.model.get(iter, 0, 1, 2)


	def get_item(self, index):
		"Returns data for an item"

		return self.model.get(self.model.iter_nth_child(None, index), 0, 1, 2)


	def insert_item(self, index, text, stock = None, data = None):
		"Inserts an item in the dropdown"

		self.model.insert(index, ( text, stock, data ) )



class EntryDropDown(DropDown):
	"An entry type dropdown"

	def __init__(self):
		DropDown.__init__(self, True)

		for e in entry.ENTRYLIST:
			self.append_item(e.typename, e.icon, e)


	def get_active_type(self):
		"Get the currently active type"

		item = self.get_active_item()

		if item is not None:
			return item[2]


	def set_active_type(self, entrytype):
		"Set the active type"

		for i in range(self.model.iter_n_children(None)):
			iter = self.model.iter_nth_child(None, i)

			if self.model.get_value(iter, 2) == entrytype:
				self.set_active(i)



##### MENU ITEMS #####

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



##### MISCELLANEOUS WIDGETS #####

class TreeView(gtk.TreeView):
	"A tree display"

	def __init__(self, model):
		gtk.TreeView.__init__(self, model)
		self.set_headers_visible(False)
		self.model = model

		self.__cbid_drag_motion	= None
		self.__cbid_drag_end	= None

		self.selection = self.get_selection()
		self.selection.set_mode(gtk.SELECTION_MULTIPLE)

		self.connect("button_press_event", self.__cb_buttonpress)
		self.connect("key_press_event", self.__cb_keypress)


	def __cb_buttonpress(self, widget, data):
		"Callback for handling mouse clicks"

		path = self.get_path_at_pos(int(data.x), int(data.y))

		# handle click outside entry
		if path is None:
			self.unselect_all()

		# handle doubleclick
		if data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS and path != None:
			iter = self.model.get_iter(path[0])
			self.toggle_expanded(iter)
			self.emit("doubleclick", iter)

		# display popup on right-click
		elif data.button == 3:
			if path != None and self.selection.iter_is_selected(self.model.get_iter(path[0])) == False:
				self.set_cursor(path[0], path[1], False)

			self.emit("popup", data)

			return True

		# handle drag-and-drop of multiple rows
		elif self.__cbid_drag_motion == None and data.button in ( 1, 2 ) and data.type == gtk.gdk.BUTTON_PRESS and path != None and self.selection.iter_is_selected(self.model.get_iter(path[0])) == True and len(self.get_selected()) > 1:
			self.__cbid_drag_motion = self.connect("motion_notify_event", self.__cb_drag_motion, data.copy() )
			self.__cbid_drag_end = self.connect("button_release_event", self.__cb_button_release, data.copy() )

			return True


	def __cb_button_release(self, widget, data, userdata = None):
		"Ends a drag"

		self.emit("button_press_event", userdata)
		self.__drag_check_end()


	def __cb_drag_motion(self, widget, data, userdata = None):
		"Monitors drag motion"

		if self.drag_check_threshold(int(userdata.x), int(userdata.y), int(data.x), int(data.y)) == True:
			self.__drag_check_end()
			self.drag_begin( (( "revelation/treerow", gtk.TARGET_SAME_APP | gtk.TARGET_SAME_WIDGET, 0), ), gtk.gdk.ACTION_MOVE, userdata.button, userdata)


	def __cb_keypress(self, widget, data = None):
		"Callback for handling key presses"

		# expand/collapse node on space
		if data.keyval == 32:
			self.toggle_expanded(self.get_active())


	def __drag_check_end(self):
		"Ends a drag check"

		self.disconnect(self.__cbid_drag_motion)
		self.disconnect(self.__cbid_drag_end)

		self.__cbid_drag_motion = None
		self.__cbid_drag_end = None


	def collapse_row(self, iter):
		"Collapse a tree row"

		gtk.TreeView.collapse_row(self, self.model.get_path(iter))


	def expand_row(self, iter):
		"Expand a tree row"

		if iter is not None and self.model.iter_n_children(iter) > 0:
			gtk.TreeView.expand_row(self, self.model.get_path(iter), False)


	def expand_to_iter(self, iter):
		"Expand all items up to and including a given iter"

		path = self.model.get_path(iter)

		for i in range(len(path)):
			iter = self.model.get_iter(path[0:i])
			self.expand_row(iter)


	def get_active(self):
		"Get the currently active row"

		iter = self.model.get_iter(self.get_cursor()[0])

		if iter is None or self.selection.iter_is_selected(iter) == False:
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



class EntryTree(TreeView):
	"An entry tree"

	def __init__(self, entrystore):
		TreeView.__init__(self, entrystore)

		column = gtk.TreeViewColumn()
		self.append_column(column)

		cr = gtk.CellRendererPixbuf()
		column.pack_start(cr, False) 
		column.add_attribute(cr, "stock-id", data.COLUMN_ICON)
		cr.set_property("stock-size", ICON_SIZE_TREEVIEW)

		cr = gtk.CellRendererText()
		column.pack_start(cr, True)
		column.add_attribute(cr, "text", data.COLUMN_NAME)

		self.connect("doubleclick", self.__cb_doubleclick)
		self.connect("row-expanded", self.__cb_row_expanded)
		self.connect("row-collapsed", self.__cb_row_collapsed)


	def __cb_doubleclick(self, widget, iter):
		"Stop doubleclick emission on folder"

		if type(self.model.get_entry(iter)) == entry.FolderEntry:
			self.stop_emission("doubleclick")


	def __cb_row_collapsed(self, object, iter, extra):
		"Updates folder icons when collapsed"

		self.model.folder_expanded(iter, False)


	def __cb_row_expanded(self, object, iter, extra):
		"Updates folder icons when expanded"

		# make sure all children are collapsed (some may have lingering expand icons)
		for i in range(self.model.iter_n_children(iter)):
			child = self.model.iter_nth_child(iter, i)

			if self.row_expanded(self.model.get_path(child)) == False:
				self.model.folder_expanded(child, False)

		self.model.folder_expanded(iter, True)


	def set_model(self, model):
		"Sets the model displayed by the tree view"

		TreeView.set_model(self, model)

		if model is None:
			return

		for i in range(model.iter_n_children(None)):
			model.folder_expanded(model.iter_nth_child(None, i), False)



class Statusbar(gtk.Statusbar):
	"An application statusbar"

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



##### FACTORIES AND MANAGERS #####

class ItemFactory(gtk.IconFactory):
	"A stock item factory"

	def __init__(self, parent):
		gtk.IconFactory.__init__(self)
		self.add_default()

		self.parent	= parent
		self.theme	= gtk.icon_theme_get_default()

		if config.DIR_ICONS not in self.theme.get_search_path():
			self.theme.append_search_path(config.DIR_ICONS)

		self.load_stock_icon(STOCK_REVELATION, "revelation", ( ICON_SIZE_LOGO, gtk.ICON_SIZE_DIALOG ))

		self.__init_entryicons()
		self.__init_items()


	def __init_entryicons(self):
		"Loads entry icons"

		icons = {
			STOCK_ENTRY_CREDITCARD		: "stock_creditcard",
			STOCK_ENTRY_CRYPTOKEY		: "stock_keyring",
			STOCK_ENTRY_DATABASE		: "stock_data-sources",
			STOCK_ENTRY_DOOR		: "stock_exit",
			STOCK_ENTRY_EMAIL		: "stock_mail",
			STOCK_ENTRY_FTP			: "gnome-ftp",
			STOCK_ENTRY_GENERIC		: "stock_lock",
			STOCK_ENTRY_PHONE		: "stock_cell-phone",
			STOCK_ENTRY_SHELL		: "gnome-terminal",
			STOCK_ENTRY_WEBSITE		: "stock_hyperlink-toolbar",
			STOCK_ENTRY_FOLDER		: "gnome-fs-directory",
			STOCK_ENTRY_FOLDER_OPEN		: "gnome-fs-directory-accept"
		}

		for id, name in icons.items():
			self.load_stock_icon(id, name, ( gtk.ICON_SIZE_MENU, ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_TREEVIEW ))


	def __init_items(self):
		"Creates stock items"

		items = (
			( STOCK_ADD,		"_Add Entry",	gtk.STOCK_ADD ),
			( STOCK_DISCARD,	"_Discard",	gtk.STOCK_DELETE ),
			( STOCK_EDIT,		"_Edit",	"stock_edit" ),
			( STOCK_EXPORT,		"_Export",	gtk.STOCK_EXECUTE ),
			( STOCK_GENERATE,	"_Generate",	gtk.STOCK_EXECUTE ),
			( STOCK_GOTO,		"_Go to",	gtk.STOCK_JUMP_TO ),
			( STOCK_IMPORT,		"_Import",	gtk.STOCK_CONVERT ),
			( STOCK_LOCK,		"_Lock",	gtk.STOCK_DIALOG_AUTHENTICATION ),
			( STOCK_NEXT,		"Ne_xt",	gtk.STOCK_GO_FORWARD ),
			( STOCK_OVERWRITE,	"_Overwrite",	gtk.STOCK_SAVE_AS ),
			( STOCK_PASSWORD_CHANGE,"_Change",	"stock_lock-ok" ),
			( STOCK_PREVIOUS,	"Pre_vious",	gtk.STOCK_GO_BACK ),
			( STOCK_RELOAD,		"_Reload",	gtk.STOCK_REFRESH ),
			( STOCK_REMOVE,		"Re_move",	gtk.STOCK_DELETE )
		)

		for id, name, icon in items:
			self.create_stock_item(id, name, icon)


	def create_stock_item(self, id, name, icon = None):
		"Creates a stock item"

		gtk.stock_add(((id, name, 0, 0, None), ))

		if icon is None:
			pass

		elif gtk.stock_lookup(icon) is not None:
			iconset = self.parent.get_style().lookup_icon_set(icon)
			self.add(id, iconset)

		else:
			self.load_stock_icon(id, icon, ( gtk.ICON_SIZE_SMALL_TOOLBAR, gtk.ICON_SIZE_LARGE_TOOLBAR, gtk.ICON_SIZE_MENU, gtk.ICON_SIZE_BUTTON ))


	def load_icon(self, id, size):
		"Loads an icon"

		return self.theme.load_icon(id, size, 0)


	def load_stock_icon(self, id, icon, sizes):
		"Registers a stock icon"

		iconset = gtk.IconSet()

		for size in sizes:
			pixelsize = gtk.icon_size_lookup(size)[0]

			source = gtk.IconSource()
			source.set_size(size)
			source.set_size_wildcarded(False)

			pixbuf = self.theme.load_icon(icon, pixelsize, 0)
			source.set_pixbuf(pixbuf)
			iconset.add_source(source)

		self.add(id, iconset)



class Timer(gobject.GObject):
	"Handles timeouts etc"

	def __init__(self, resolution = 5):
		gobject.GObject.__init__(self)

		self.offset		= None
		self.timeout		= None

		gobject.timeout_add(resolution * 1000, self.__cb_check)


	def __cb_check(self):
		"Checks if the timeout has been reached"

		if None not in (self.offset, self.timeout) and int(time.time()) >= (self.offset + self.timeout):
			self.stop()
			self.emit("ring")

		return True


	def reset(self):
		"Resets the timer"

		if self.offset != None:
			self.offset = int(time.time())


	def start(self, timeout):
		"Starts the timer"

		if timeout == 0:
			self.stop()

		else:
			self.offset = int(time.time())
			self.timeout = timeout


	def stop(self):
		"Stops the timer"

		self.offset = None
		self.timeout = None


gobject.signal_new("ring", Timer, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())



class UIManager(gtk.UIManager):
	"UI item manager"

	def __init__(self):
		gtk.UIManager.__init__(self)

		self.connect("connect-proxy", self.__cb_connect_proxy)


	def __cb_connect_proxy(self, uimanager, action, widget):
		"Callback for connecting proxies to an action"

		if type(widget) in ( gtk.MenuItem, gtk.ImageMenuItem, gtk.CheckMenuItem ):
			widget.tooltip = action.get_property("tooltip")

		else:
			widget.set_property("label", widget.get_property("label").replace("...", ""))


	def add_actions_from_file(self, file):
		"Sets up actions from an XML file"

		data = io.file_read(file)
		self.add_actions_from_string(data)


	def add_actions_from_string(self, string):
		"Sets up actions from an XML string"

		try:
			dom = xml.dom.minidom.parseString(string.strip())

		except ExpatError:
			raise DataError

		if dom.documentElement.nodeName != "actions":
			raise DataError


		# load action groups
		for groupnode in dom.documentElement.childNodes:

			if groupnode.nodeType != groupnode.ELEMENT_NODE:
				continue

			if groupnode.nodeName != "actiongroup":
				raise DataError

			if not groupnode.attributes.has_key("name"):
				raise DataError

			actiongroup = gtk.ActionGroup(groupnode.attributes["name"].nodeValue)


			# load actions
			for actionnode in groupnode.childNodes:

				if actionnode.nodeType != actionnode.ELEMENT_NODE:
					continue

				actiondata = {
					"name"		: "",
					"type"		: "normal",
					"label"		: "",
					"stock"		: "",
					"accel"		: None,
					"description"	: ""
				}

				if actionnode.attributes.has_key("type"):
					actiondata["type"] = actionnode.attributes["type"].nodeValue

				for node in actionnode.childNodes:

					if node.nodeType != node.ELEMENT_NODE:
						continue

					elif actiondata.has_key(node.nodeName):
						actiondata[node.nodeName] = util.dom_text(node)

					else:
						raise DataError

				if actiondata["name"] == "":
					raise DataError

				if actiondata["type"] == "normal":
					action = gtk.Action(
						actiondata["name"], actiondata["label"],
						actiondata["description"], actiondata["stock"]
					)

				elif actiondata["type"] == "toggle":
					action = gtk.ToggleAction(
						actiondata["name"], actiondata["label"],
						actiondata["description"], actiondata["stock"]
					)

				else:
					raise DataError

				actiongroup.add_action_with_accel(action, actiondata["accel"])


			self.append_action_group(actiongroup)


	def add_ui_from_file(self, file):
		"Loads ui from a file"

		try:
			gtk.UIManager.add_ui_from_file(self, file)

		except gobject.GError:
			raise IOError


	def append_action_group(self, actiongroup):
		"Appends an action group"

		gtk.UIManager.insert_action_group(self, actiongroup, len(self.get_action_groups()))


	def get_action(self, name):
		"Looks up an action in the managers actiongroups"

		for actiongroup in self.get_action_groups():
			action = actiongroup.get_action(name)

			if action is not None:
				return action


	def get_action_group(self, name):
		"Returns the named action group"

		for actiongroup in self.get_action_groups():
			if actiongroup.get_name() == name:
				return actiongroup



##### APPLICATION COMPONENTS #####

class App(gnome.ui.App):
	"An application window"

	def __init__(self, appname):
		gnome.ui.App.__init__(self, appname, appname)

		self.statusbar = Statusbar()
		self.set_statusbar(self.statusbar)

		self.uimanager = UIManager()
		self.add_accel_group(self.uimanager.get_accel_group())


	def __connect_menu_statusbar(self, menu):
		"Connects a menus items to the statusbar"

		for item in menu.get_children():
			if isinstance(item, gtk.MenuItem) == True:
				item.connect("select", self.cb_menudesc, True)
				item.connect("deselect", self.cb_menudesc, False)


	def cb_menudesc(self, item, show):
		"Displays menu descriptions in the statusbar"

		if show == True:
			self.statusbar.set_status(item.tooltip)

		else:
			self.statusbar.clear()


	def __cb_toolbar_hide(self, widget, name):
		"Hides the toolbar dock when the toolbar is hidden"

		self.get_dock_item_by_name(name).hide()


	def __cb_toolbar_show(self, widget, name):
		"Shows the toolbar dock when the toolbar is shown"

		self.get_dock_item_by_name(name).show()


	def add_toolbar(self, toolbar, name, band, detachable):
		"Adds a toolbar"

		behavior = bonobo.ui.DOCK_ITEM_BEH_EXCLUSIVE

		if detachable == False:
			behavior |= bonobo.ui.DOCK_ITEM_BEH_LOCKED

		gnome.ui.App.add_toolbar(self, toolbar, name, behavior, 0, band, 0, 0)

		toolbar.connect("show", self.__cb_toolbar_show, name)
		toolbar.connect("hide", self.__cb_toolbar_hide, name)

		toolbar.show_all()


	def get_title(self):
		"Returns the app title"

		title = gnome.ui.App.get_title(self)

		return title.replace(" - " + config.APPNAME, "")


	def popup(self, menu, button, time):
		"Displays a popup menu"

		self.__connect_menu_statusbar(menu)
		menu.popup(None, None, None, button, time)


	def run(self):
		"Runs the application"

		self.show_all()
		gtk.main()


	def set_menus(self, menubar):
		"Sets the menubar for the application"

		for item in menubar.get_children():
			self.__connect_menu_statusbar(item.get_submenu())

		gnome.ui.App.set_menus(self, menubar)


	def set_title(self, title):
		"Sets the window title"

		gnome.ui.App.set_title(self, title + " - " + config.APPNAME)


	def set_toolbar(self, toolbar):
		"Sets the application toolbar"

		gnome.ui.App.set_toolbar(self, toolbar)
		toolbar.connect("show", self.__cb_toolbar_show, "Toolbar")
		toolbar.connect("hide", self.__cb_toolbar_hide, "Toolbar")



class EntryView(VBox):
	"A component for displaying an entry"

	def __init__(self, cfg = None):
		VBox.__init__(self)
		self.config = cfg
		self.set_spacing(15)
		self.set_border_width(10)

		self.size_name	= gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.size_value	= gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

		self.entry = None


	def clear(self, force = False):
		"Clears the data view"

		self.entry = None

		for child in self.get_children():
			child.destroy()


	def display_entry(self, e):
		"Displays info about an entry"

		if e is None:
			if self.entry is not None:
				self.clear()

			return

		self.clear()
		self.entry = e

		# set up metadata display
		metabox = VBox()
		self.pack_start(metabox)

		metabox.pack_start(ImageLabel(
			"<span size=\"large\" weight=\"bold\">%s</span>" % util.escape_markup(e.name),
			e.icon, ICON_SIZE_DATAVIEW
		))

		metabox.pack_start(Label("<span weight=\"bold\">%s</span>%s" % ( e.typename + (e.description != "" and "; " or ""), util.escape_markup(e.description) ), gtk.JUSTIFY_CENTER))

		# set up field list
		fields = [ field for field in e.fields if field.value != "" ]

		if len(fields) > 0:
			fieldlist = VBox()
			fieldlist.set_spacing(2)
			self.pack_start(fieldlist)

			for field in fields:
				row = HBox()
				fieldlist.pack_start(row, False, False)

				label = Label("<span weight=\"bold\">%s:</span>" % util.escape_markup(field.name), gtk.JUSTIFY_RIGHT)
				self.size_name.add_widget(label)
				row.pack_start(label, False, False)

				widget = generate_field_display_widget(field, self.config)
				self.size_value.add_widget(widget)
				row.pack_start(widget, False, False)

		# display updatetime
		if type(e) != entry.FolderEntry:
			self.pack_start(Label("Updated %s ago;\n%s" % ( util.time_period_rough(e.updated, time.time()), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.updated)) ), gtk.JUSTIFY_CENTER))

		self.show_all()


	def display_info(self):
		"Displays info about the application"

		self.clear()

		self.pack_start(ImageLabel(
			"""<span size="x-large" weight="bold">%s %s</span>""" % ( config.APPNAME, config.VERSION ),
			STOCK_REVELATION, ICON_SIZE_LOGO
		))

		self.pack_start(Label("A password manager for GNOME 2"))
	
		gpl = "\nThis program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details."
		label = Label("<span size=\"x-small\">" + gpl + "</span>", gtk.JUSTIFY_LEFT)
		label.set_size_request(250, -1)
		self.pack_start(label)


	def pack_start(self, widget):
		"Adds a widget to the data view"

		alignment = gtk.Alignment(0.5, 0.5, 0, 0)
		alignment.add(widget)
		VBox.pack_start(self, alignment)



class Searchbar(Toolbar):
	"A toolbar for easy searching"

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

		self.button.set_sensitive(False)


	def __cb_key_press(self, widget, data = None):
		"Callback for key presses"

		# return
		if data.keyval == 65293 and widget.get_text() != "":
			self.button.activate()
			return True

