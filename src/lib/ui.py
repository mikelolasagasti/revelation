#
# Revelation 0.3.0 - a password manager for GNOME 2
# $Id$
# http://oss.codepoet.no/revelation/
#
# Module containing specialized, high-level ui components
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

import gobject, gtk, gtk.gdk, gnome.ui, revelation, time, os, gconf


# this class handles the core application ui and mechanism,
# while functionality is handled by the main app
class App(gnome.ui.App):

	def __init__(self):
		gnome.ui.App.__init__(self, revelation.APPNAME, revelation.APPNAME)
		self.connect("file-changed", self.__cb_state_file)
		os.umask(0077)
		self.__init_facilities()

		# set up ui
		self.set_default_size(600, 400)
		self.set_icon_list(
			gtk.gdk.pixbuf_new_from_file(revelation.DATADIR + "/pixmaps/revelation.png"),
			gtk.gdk.pixbuf_new_from_file(revelation.DATADIR + "/pixmaps/revelation-16x16.png")
		)

		self.statusbar = gnome.ui.AppBar(gtk.FALSE, gtk.TRUE, gnome.ui.PREFERENCES_USER)
		self.set_statusbar(self.statusbar)

		self.accelgroup = gtk.AccelGroup()
		self.add_accel_group(self.accelgroup)

		self.__init_toolbar()
		self.__init_menu()
		self.__init_mainarea()

		# set up initial states
		self.tree.select(None)

		self.if_menu.get_widget("<main>/Edit/Find Next").set_sensitive(gtk.FALSE)
		self.if_menu.get_widget("<main>/Edit/Find Previous").set_sensitive(gtk.FALSE)
		self.if_menu.get_widget("<main>/Edit/Undo").set_sensitive(gtk.FALSE)
		self.if_menu.get_widget("<main>/Edit/Redo").set_sensitive(gtk.FALSE)
		self.if_menu.get_widget("<main>/View/Show Passwords").set_active(self.gconf.get_bool("/apps/revelation/view/passwords"))

		self.show_all()

		if self.gconf.get_bool("/apps/revelation/view/toolbar") == gtk.FALSE:
			self.get_dock_item_by_name("Toolbar").hide()
		else:
			self.if_menu.get_widget("<main>/View/Toolbar").set_active(gtk.TRUE)

		if self.gconf.get_bool("/apps/revelation/view/statusbar") == gtk.FALSE:
			self.statusbar.hide()
		else:
			self.if_menu.get_widget("<main>/View/Statusbar").set_active(gtk.TRUE)

		self.file = None
		self.password = None
		self.filepassword = None


	def __init_facilities(self):
		self.icons = revelation.stock.IconFactory(self)
		self.data = revelation.data.DataStore()

		self.gconf = gconf.client_get_default()
		self.gconf.add_dir("/apps/revelation", gconf.CLIENT_PRELOAD_NONE)
		self.gconf.notify_add("/apps/revelation/view/statusbar", self.__cb_gconf_statusbar)
		self.gconf.notify_add("/apps/revelation/view/toolbar", self.__cb_gconf_toolbar)
		self.gconf.notify_add("/apps/revelation/view/passwords", self.__cb_gconf_view_passwords)

		self.clipboard = revelation.data.EntryClipboard()
		self.clipboard.connect("copy", self.__cb_state_clipboard)
		self.clipboard.connect("cut", self.__cb_state_clipboard)

		self.undoqueue = revelation.data.UndoQueue()
		self.undoqueue.connect("can-undo", self.__cb_state_undo, revelation.data.UNDO)
		self.undoqueue.connect("can-redo", self.__cb_state_undo, revelation.data.REDO)

		self.finder = revelation.data.EntrySearch(self.data)
		self.finder.connect("string_changed", self.__cb_state_find)


	def __init_mainarea(self):
		hpaned = gtk.HPaned()
		hpaned.set_border_width(5)
		hpaned.set_position(300)
		self.set_contents(hpaned)

		self.tree = Tree(self.data)
		self.tree.connect("button_press_event", self.__cb_popup_tree)
		self.tree.selection.connect("changed", self.__cb_entry_display)
		self.tree.selection.connect("changed", self.__cb_state_entry)
		scrolledwindow = gtk.ScrolledWindow()
		scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrolledwindow.add(self.tree)
		hpaned.pack1(scrolledwindow, gtk.TRUE)

		self.dataview = DataView()
		self.dataview.display_info()
		alignment = gtk.Alignment(0.5, 0.4, 0, 0)
		alignment.add(self.dataview)
		hpaned.pack2(alignment)


	def __init_menu(self):
		menuitems = (
			("/_File",		None,			None,					None,	0,	"<Branch>"),
			("/File/_New",		"<Control>N",		"Create a new file",			None,	0,	"<StockItem>",	gtk.STOCK_NEW),
			("/File/_Open...",	"<Control>O",		"Open a file",				None,	0,	"<StockItem>",	gtk.STOCK_OPEN),
			("/File/sep1",		None,			None,					None,	0,	"<Separator>"),
			("/File/_Save",		"<Control>S",		"Save data to file",			None,	0,	"<StockItem>",	gtk.STOCK_SAVE),
			("/File/Save _As...",	"<Shift><Control>S",	"Save data to different file",		None,	0,	"<StockItem>",	gtk.STOCK_SAVE_AS),
			("/File/_Revert",	None,			"Revert to the saved copy of the file",	None,	0,	"<StockItem>",	gtk.STOCK_REVERT_TO_SAVED),
			("/File/sep2",		None,			None,					None,	0,	"<Separator>"),
			("/File/Change _Password...",	None,		"Change password of current file",	None,	0,	"<StockItem>",	revelation.stock.STOCK_PASSWORD),
			("/File/_Lock...",	"<Control>L",		"Lock the current data file",		None,	0,	"<StockItem>",	revelation.stock.STOCK_LOCK),
			("/File/sep3",		None,			None,					None,	0,	"<Separator>"),
			("/File/_Import...",	None,			"Import data from a foreign file",	None,	0,	"<StockItem>",	revelation.stock.STOCK_IMPORT),
			("/File/_Export...",	None,			"Export data to a different format",	None,	0,	"<StockItem>",	revelation.stock.STOCK_EXPORT),
			("/File/sep4",		None,			None,					None,	0,	"<Separator>"),
			("/File/_Close",	"<Control>W",		"Close the application",		None,	0, 	"<StockItem>",	gtk.STOCK_CLOSE),
			("/File/_Quit",		"<Control>Q",		"Quit the application",			None,	0, 	"<StockItem>",	gtk.STOCK_QUIT),

			("/_Edit",		None,			None,					None,	0,	"<Branch>"),
			("/Edit/_Add Entry...",	"Insert",		"Create a new entry",			None,	0,	"<StockItem>",	revelation.stock.STOCK_ADD),
			("/Edit/_Edit",		"Return",		"Edit the selected entry",		None,	0,	"<StockItem>",	revelation.stock.STOCK_EDIT),
			("/Edit/Re_move",	"Delete",		"Remove the selected entry",		None,	0,	"<StockItem>",	revelation.stock.STOCK_REMOVE),
			("/Edit/sep1",		None,			None,					None,	0,	"<Separator>"),
			("/Edit/_Undo",		"<Control>Z",		"Undo the last action",			None,	0,	"<StockItem>",	gtk.STOCK_UNDO),
			("/Edit/_Redo",		"<Shift><Control>Z",	"Redo the previously undone action",	None,	0,	"<StockItem>",	gtk.STOCK_REDO),
			("/Edit/sep2",		None,			None,					None,	0,	"<Separator>"),
			("/Edit/Cu_t",		"<Control>X",		"Cut the entry to the clipboard",	None,	0,	"<StockItem>",	gtk.STOCK_CUT),
			("/Edit/_Copy",		"<Control>C",		"Copy the entry to the clipboard",	None,	0,	"<StockItem>",	gtk.STOCK_COPY),
			("/Edit/_Paste",	"<Control>V",		"Paste entry from clipboard",		None,	0,	"<StockItem>",	gtk.STOCK_PASTE),
			("/Edit/sep3",		None,			None,					None,	0,	"<Separator>"),
			("/Edit/_Find...",	"<Control>F",		"Search for an entry",			None,	0,	"<StockItem>",	gtk.STOCK_FIND),
			("/Edit/Find Ne_xt",	"<Control>G",		"Find the next search match",		None,	0,	"<Item>"),
			("/Edit/Find Pre_vious",	"<Shift><Control>G",		"Find the previous search match",	None,	0,	"<Item>"),
			("/Edit/sep4",		None,			None,					None,	0,	"<Separator>"),
			("/Edit/_Select All",	"<Control>A",		"Select all entries",			lambda w,d: self.tree.select_all(),	0,	"<Item>"),
			("/Edit/_Deselect All",	"<Shift><Control>A",	"Deselect all entries",			lambda w,d: self.tree.unselect_all(),	0,	"<Item>"),
			("/Edit/sep5",		None,			None,					None,	0,	"<Separator>"),
			("/Edit/Prefere_nces",	None,			"Edit preferences",			None,	0,	"<StockItem>",	gtk.STOCK_PREFERENCES),

			("/_View",		None,			None,					None,	0,	"<Branch>"),
			("/View/_Toolbar",	None,			"Toggle display of the toolbar",	self.__cb_state_toolbar,	0,	"<CheckItem>"),
			("/View/_Statusbar",	None,			"Toggle display of the statusbar",	self.__cb_state_statusbar,	0,	"<CheckItem>"),
			("/View/sep1",		None,			None,					None,	0,	"<Separator>"),
			("/View/Show _Passwords",	"<Control>P",	"Show passwords",			self.__cb_state_showpasswords,	0,	"<CheckItem>"),

			("/_Help",		None,			None,					None,	0,	"<Branch>"),
			("/Help/_Homepage",	None,			"Visit the Revelation homepage",	lambda w,d: gnome.url_show(revelation.URL),	0,	"<StockItem>", gtk.STOCK_HOME),
			("/Help/_About",	None,			"Show info about this application",	lambda w,d: revelation.dialog.About().run(),	0,	"<StockItem>", "gnome-stock-about")
		)

		self.if_menu = self.create_itemfactory(gtk.MenuBar, self.accelgroup, menuitems)
		self.set_menus(self.if_menu.get_widget("<main>"))


	def __init_toolbar(self):
		self.toolbar = gtk.Toolbar()
		self.toolbar.button_new = self.toolbar.insert_stock(gtk.STOCK_NEW, "New file", None, None, "", -1)
		self.toolbar.button_open = self.toolbar.insert_stock(gtk.STOCK_OPEN, "Open file", None, None, "", -1)
		self.toolbar.button_save = self.toolbar.insert_stock(gtk.STOCK_SAVE, "Save file", None, None, "", -1)
		self.toolbar.append_space()
		self.toolbar.button_entry_add = self.toolbar.insert_stock(revelation.stock.STOCK_ADD, "Add a new entry", None, None, "", -1)
		self.toolbar.button_entry_edit = self.toolbar.insert_stock(revelation.stock.STOCK_EDIT, "Edit the selected entry", None, None, "", -1)
		self.toolbar.button_entry_remove = self.toolbar.insert_stock(revelation.stock.STOCK_REMOVE, "Remove the selected entry", None, None, "", -1)
		self.set_toolbar(self.toolbar)


	def __setattr__(self, name, value):
		if name == "file":
			self.emit("file-changed", value)

		gnome.ui.App.__setattr__(self, name, value)


	# gconf callbacks
	def __cb_gconf_view_passwords(self, client, id, entry, data):
		self.if_menu.get_widget("<main>/View/Show Passwords").set_active(entry.get_value().get_bool())


	def __cb_gconf_statusbar(self, client, id, entry, data):
		if entry.get_value().get_bool() == gtk.TRUE:
			self.statusbar.show()
			self.if_menu.get_widget("<main>/View/Statusbar").set_active(gtk.TRUE)
		else:
			self.statusbar.hide()
			self.if_menu.get_widget("<main>/View/Statusbar").set_active(gtk.FALSE)


	def __cb_gconf_toolbar(self, client, id, entry, data):
		if entry.get_value().get_bool() == gtk.TRUE:
			self.get_dock_item_by_name("Toolbar").show()
			self.if_menu.get_widget("<main>/View/Toolbar").set_active(gtk.TRUE)
		else:
			self.get_dock_item_by_name("Toolbar").hide()
			self.if_menu.get_widget("<main>/View/Toolbar").set_active(gtk.FALSE)


	# state callbacks
	def __cb_state_clipboard(self, widget, data = None):
		self.if_menu.get_widget("<main>/Edit/Paste").set_sensitive(self.clipboard.has_contents())


	def __cb_state_entry(self, widget, data = None):
		selcount = len(self.tree.get_selected())

		self.toolbar.button_entry_add.set_sensitive(selcount < 2)
		self.if_menu.get_widget("<main>/Edit/Add Entry...").set_sensitive(selcount < 2)
		self.if_menu.get_widget("<main>/Edit/Paste").set_sensitive(selcount < 2 and self.clipboard.has_contents())

		self.toolbar.button_entry_edit.set_sensitive(selcount == 1)
		self.if_menu.get_widget("<main>/Edit/Edit").set_sensitive(selcount == 1)

		self.toolbar.button_entry_remove.set_sensitive(selcount > 0)
		self.if_menu.get_widget("<main>/Edit/Remove").set_sensitive(selcount > 0)
		self.if_menu.get_widget("<main>/Edit/Cut").set_sensitive(selcount > 0)
		self.if_menu.get_widget("<main>/Edit/Copy").set_sensitive(selcount > 0)


	def __cb_state_file(self, object, data):
		self.data.changed = gtk.FALSE

		self.if_menu.get_widget("<main>/File/Revert").set_sensitive(data != None)
		self.if_menu.get_widget("<main>/File/Lock...").set_sensitive(data != None)

		if data == None:
			self.set_title("[New file] - " + revelation.APPNAME)
			self.password = None
			self.filepassword = None
		else:
			self.set_title(os.path.basename(data) + " - " + revelation.APPNAME)
			os.chdir(os.path.dirname(data))


	def __cb_state_find(self, widget, data = None):
		self.if_menu.get_widget("<main>/Edit/Find Next").set_sensitive(data != "")
		self.if_menu.get_widget("<main>/Edit/Find Previous").set_sensitive(data != "")


	def __cb_state_showpasswords(self, object, data = None):
		self.gconf.set_bool("/apps/revelation/view/passwords", self.if_menu.get_widget("<main>/View/Show Passwords").get_active())


	def __cb_state_statusbar(self, object, data):
		active = self.if_menu.get_widget("<main>/View/Statusbar").get_active()
		self.gconf.set_bool("/apps/revelation/view/statusbar", active)


	def __cb_state_toolbar(self, object, data = None):
		active = self.if_menu.get_widget("<main>/View/Toolbar").get_active()
		self.gconf.set_bool("/apps/revelation/view/toolbar", active)


	def __cb_state_undo(self, object, state, method):
		if method == revelation.data.UNDO:
			widget = self.if_menu.get_widget("<main>/Edit/Undo")
			action = "_Undo"
		elif method == revelation.data.REDO:
			widget = self.if_menu.get_widget("<main>/Edit/Redo")
			action = "_Redo"

		widget.set_sensitive(state)
		item = widget.get_children()[0]

		if state == gtk.TRUE:
			item.set_label(action + " " + self.undoqueue.get_data(method)["name"])
		else:
			item.set_label(action)


	# misc other callbacks
	def __cb_entry_display(self, object, data = None):
		self.dataview.display_entry(self.data.get_entry(self.tree.get_active()))


	def __cb_menudesc(self, object, item, show):
		if show:
			self.statusbar.set_status(item.get_data("description"))
		else:
			self.statusbar.set_status("")


	def __cb_popup_tree(self, widget, data = None):
		if data.button != 3:
			return

		path = self.tree.get_path_at_pos(int(data.x), int(data.y))

		if path == None:
			self.tree.unselect_all()
		elif self.tree.selection.iter_is_selected(self.data.get_iter(path[0])) == gtk.FALSE:
			self.tree.set_cursor(path[0], path[1], gtk.FALSE)

		iters = self.tree.get_selected()

		menuitems = []
		self.emit("tree-popup", menuitems, iters)

		itemfactory = self.create_itemfactory(gtk.Menu, gtk.AccelGroup(), menuitems)
		itemfactory.popup(int(data.x_root), int(data.y_root), data.button, data.get_time())

		return gtk.TRUE


	# main methods
	def create_itemfactory(self, widget, accelgroup, items):
		itemfactory = MenuFactory(widget, accelgroup)
		itemfactory.create_items(items)
		itemfactory.connect("item-selected", self.__cb_menudesc, gtk.TRUE)
		itemfactory.connect("item-deselected", self.__cb_menudesc, gtk.FALSE)
		return itemfactory


	def run(self):
		self.show_all()
		gtk.main()


gobject.signal_new("file-changed", App, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new("tree-popup", App, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))



class DataView(gtk.VBox):

	def __init__(self):
		gtk.VBox.__init__(self)
		self.set_spacing(15)
		self.set_border_width(10)

		self.size_name = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.size_value = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

		self.data = None


	def clear(self, force = gtk.FALSE):
		if force == gtk.TRUE or self.data is not None:
			self.data = None
			for child in self.get_children():
				child.destroy()


	def display_entry(self, data):
		if data is None:
			self.clear()
			return

		self.clear(gtk.TRUE)
		self.data = data

		# set up metadata display
		metabox = gtk.VBox()
		metabox.set_spacing(4)
		self.pack_start(metabox)

		metabox.pack_start(revelation.widget.ImageLabel(
			data["icon"], revelation.stock.ICON_SIZE_DATAVIEW,
			"<span size=\"large\" weight=\"bold\">" + revelation.misc.escape_markup(data["name"]) + "</span>"
		))

		metabox.pack_start(revelation.widget.Label("<span weight=\"bold\">" + revelation.entry.get_entry_data(data["type"], "name") + (data["description"] != "" and "; " or "") + "</span>" + revelation.misc.escape_markup(data["description"]), gtk.JUSTIFY_CENTER))

		# set up field list
		rows = []

		for field in revelation.entry.get_entry_fields(data["type"]):
			if not data["fields"].has_key(field) or data["fields"][field] == "":
				continue

			row = gtk.HBox()
			row.set_spacing(5)
			rows.append(row)

			label = revelation.widget.Label("<span weight=\"bold\">" + revelation.misc.escape_markup(revelation.entry.get_field_data(field, "name")) + ":</span>", gtk.JUSTIFY_RIGHT)
			self.size_name.add_widget(label)
			row.pack_start(label, gtk.FALSE, gtk.FALSE)


			type = revelation.entry.get_field_data(field, "type")

			if type == revelation.entry.FIELD_TYPE_EMAIL:
				widget = revelation.widget.HRef("mailto:" + data["fields"][field], revelation.misc.escape_markup(data["fields"][field]))

			elif type == revelation.entry.FIELD_TYPE_URL:
				widget = revelation.widget.HRef(data["fields"][field], revelation.misc.escape_markup(data["fields"][field]))

			elif type == revelation.entry.FIELD_TYPE_PASSWORD:
				widget = revelation.widget.PasswordLabel(revelation.misc.escape_markup(data["fields"][field]))

			else:
				widget = revelation.widget.Label(revelation.misc.escape_markup(data["fields"][field]))
				widget.set_selectable(gtk.TRUE)

			self.size_value.add_widget(widget)
			row.pack_start(widget, gtk.FALSE, gtk.FALSE)


		if len(rows) > 0:
			fieldlist = gtk.VBox()
			fieldlist.set_spacing(2)
			self.pack_start(fieldlist)

			for row in rows:
				fieldlist.pack_start(row, gtk.FALSE, gtk.FALSE)

		# display updatetime
		if data["type"] != revelation.entry.ENTRY_FOLDER:
			self.pack_start(revelation.widget.Label("Updated " + revelation.misc.timediff_simple(data["updated"]) + " ago; \n" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data["updated"])), gtk.JUSTIFY_CENTER))

		self.show_all()


	def display_info(self):
		self.clear(gtk.TRUE)

		self.pack_start(revelation.widget.ImageLabel(
			revelation.stock.STOCK_APPLICATION, gtk.ICON_SIZE_DND,
			"<span size=\"x-large\" weight=\"bold\">" + revelation.APPNAME + " " + revelation.VERSION + "</span>"
		))

		self.pack_start(revelation.widget.Label("A password manager for GNOME 2"))

		gpl = "\nThis program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details."
		label = revelation.widget.Label("<span size=\"x-small\">" + gpl + "</span>", gtk.JUSTIFY_LEFT)
		label.set_size_request(250, -1)
		self.pack_start(label)

		self.show_all()


	def pack_start(self, widget):
		alignment = gtk.Alignment(0.5, 0.5, 0, 0)
		alignment.add(widget)
		gtk.VBox.pack_start(self, alignment)



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



class Tree(gtk.TreeView):

	def __init__(self, datastore = None):
		gtk.TreeView.__init__(self, datastore)
		self.set_headers_visible(gtk.FALSE)
		self.model = datastore
		self.selection = self.get_selection()
		self.selection.set_mode(gtk.SELECTION_MULTIPLE)

		self.connect("button_press_event", self.__cb_buttonpress)
		self.connect("key_press_event", self.__cb_keypress)
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


	def __cb_buttonpress(self, object, data):
		if data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS:
			path = self.get_path_at_pos(int(data.x), int(data.y))

			if path != None:
				iter = self.model.get_iter(path[0])
				self.toggle_expanded(iter)
				self.emit("doubleclick", iter)

	def __cb_keypress(self, object, data):
		if data.keyval == 32:
			self.toggle_expanded(self.get_active())

	def __cb_row_collapsed(self, object, iter, extra):
		self.model.set_folder_state(iter, gtk.FALSE)

	def __cb_row_expanded(self, object, iter, extra):
		for i in range(self.model.iter_n_children(iter)):
			child = self.model.iter_nth_child(iter, i)
			if self.row_expanded(self.model.get_path(child)) == gtk.FALSE:
				self.model.set_folder_state(child, gtk.FALSE)

		self.model.set_folder_state(iter, gtk.TRUE)


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

		if model is not None:
			for i in range(model.iter_n_children(None)):
				model.set_folder_state(model.iter_nth_child(None, i), gtk.FALSE)


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

gobject.signal_new("doubleclick", Tree, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))

