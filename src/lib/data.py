#
# Revelation 0.3.1 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing data-related functionality
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

import revelation, gobject, gtk, gconf


ENTRYSTORE_COL_NAME	= 0
ENTRYSTORE_COL_ICON	= 1
ENTRYSTORE_COL_TYPE	= 2
ENTRYSTORE_COL_DESC	= 3
ENTRYSTORE_COL_UPDATED	= 4
ENTRYSTORE_COL_FIELDS	= 5

UNDO_ACTION_ADD		= "add"
UNDO_ACTION_CUT		= "cut"
UNDO_ACTION_EDIT	= "edit"
UNDO_ACTION_IMPORT	= "import"
UNDO_ACTION_PASTE	= "paste"
UNDO_ACTION_REMOVE	= "remove"

UNDO_ACTIONTYPE_ADD	= "add"
UNDO_ACTIONTYPE_EDIT	= "edit"
UNDO_ACTIONTYPE_REMOVE	= "remove"

UNDO			= "undo"
REDO			= "redo"

SEARCH_NEXT		= "next"
SEARCH_PREV		= "prev"



class ConfigError(Exception):
	"Config error exception"
	pass



class Config(gobject.GObject):
	"Configuration interface"

	def __init__(self, basedir = "/apps/revelation"):
		gobject.GObject.__init__(self)

		self.basedir = basedir
		self.callbacks = {}

		self.client = gconf.client_get_default()

		# check if config is nice, otherwise install the schema
		if self.check() == gtk.FALSE and self.install_schema() == gtk.FALSE:
			raise ConfigError

		self.client.add_dir(self.basedir, gconf.CLIENT_PRELOAD_NONE)


	def __cb_bind_entry_get(self, config, value, widget):
		"Callback which handles update notifications for entry widgets"

		widget.set_text(str(value))


	def __cb_bind_entry_set(self, widget, key):
		"Callback which updates config entries fro bound entry widgets"

		self.set(key, widget.get_text())


	def __cb_bind_spin_get(self, config, value, widget):
		"Callback which handles update notifications for spin buttons"

		widget.set_value(value)


	def __cb_bind_spin_set(self, widget, key):
		"Callback which updates config entries from bound spin buttons"

		self.set(key, widget.get_value_as_int())


	def __cb_bind_toggle_get(self, config, value, widget):
		"Callback which handles update notifications for toggle widgets"

		widget.set_active(value)


	def __cb_bind_toggle_set(self, widget, key):
		"Callback which updates config entries for bound toggle widgets"

		self.set(key, widget.get_active())


	def __cb_bind_unrealize(self, widget, id):
		"Disconnects a bound widget callback when the widget is unrealized"

		self.client.notify_remove(id)
		del self.callbacks[id]


	def __cb_notify(self, client, id, entry, data):
		"Callback for handling notifications"

		# get the value contents
		value = entry.get_value()

		if value.type == gconf.VALUE_STRING:
			v = value.get_string()

		elif value.type == gconf.VALUE_BOOL:
			v = value.get_bool()

		elif value.type == gconf.VALUE_INT:
			v = value.get_int()

		# look up and call the callback
		callback = self.callbacks[id]["callback"]
		data = self.callbacks[id]["data"]

		callback(self, v, data)


	def bind_widget(self, key, widget):
		"Binds a gtk widget to a gconf key"

		if isinstance(widget, gtk.CheckMenuItem) or isinstance(widget, gtk.ToggleButton):
			signal, cb_get, cb_set = "toggled", self.__cb_bind_toggle_get, self.__cb_bind_toggle_set

		elif isinstance(widget, gtk.SpinButton):
			signal, cb_get, cb_set = "changed", self.__cb_bind_spin_get, self.__cb_bind_spin_set

		elif isinstance(widget, revelation.widget.FileEntry):
			signal, cb_get, cb_set = "changed", self.__cb_bind_entry_get, self.__cb_bind_entry_set
			widget = widget.entry

		elif isinstance(widget, gtk.Entry):
			signal, cb_get, cb_set = "changed", self.__cb_bind_entry_get, self.__cb_bind_entry_set

		else:
			raise ConfigError

		id = self.notify_add(key, cb_get, widget)
		widget.connect(signal, cb_set, key)
		widget.connect("unrealize", self.__cb_bind_unrealize, id)


	def check(self):
		"Checks if the configuration is available"

		try:
			self.get("view/window-width")
			self.get("file/autoload_file")
			self.get("file/autosave")

		except ConfigError:
			return gtk.FALSE

		else:
			return gtk.TRUE
			

	def get(self, key):
		"Looks up a config value"

		value = self.client.get(self.keypath(key))

		if value is None:
			raise ConfigError

		elif value.type == gconf.VALUE_STRING:
			return value.get_string()

		elif value.type == gconf.VALUE_INT:
			return value.get_int()

		elif value.type == gconf.VALUE_BOOL:
			return value.get_bool()


	def install_schema(self):
		"Attempts to install the Revelation configuration schema"

		if not revelation.io.file_exists("/etc/gconf/schemas/revelation.schemas"):
			return gtk.FALSE

		revelation.io.execute("gconftool-2 --install-schema-file=/etc/gconf/schemas/revelation.schemas")

		return self.check()


	def notify_add(self, key, callback, data = None):
		"Adds a callback for a key change"

		id = self.client.notify_add(self.keypath(key), self.__cb_notify)

		self.callbacks[id] = {
			"callback"	: callback,
			"data"		: data
		}

		# call the callback to set an initial state
		callback(self, self.get(key), data)

		return id


	def keypath(self, key):
		"Generates an absolute key path"

		return self.basedir + "/" + key


	def set(self, key, value):
		"Sets a configuration value"

		v = self.client.get(self.keypath(key))

		if v is None:
			raise ConfigError

		if v.type == gconf.VALUE_STRING:
			v.set_string(value)

		elif v.type == gconf.VALUE_BOOL:
			v.set_bool(value)

		elif v.type == gconf.VALUE_INT:
			v.set_int(value)

		self.client.set(self.keypath(key), v)



class EntrySearch(gobject.GObject):
	"Does entry searching in entrystores"

	def __init__(self, entrystore):
		gobject.GObject.__init__(self)

		self.entrystore	= entrystore

		self.string	= ""
		self.type	= None

		self.folders	= gtk.TRUE
		self.namedesc	= gtk.FALSE
		self.casesens	= gtk.FALSE


	def __setattr__(self, name, value):
		"Customized attribute access"

		if name == "string":
			self.emit("changed")

		gobject.GObject.__setattr__(self, name, value)


	def find(self, offset, direction = SEARCH_NEXT):
		"Search for an entry, starting at the given offset"

		if offset is None:
			iter = None

		else:
			iter = offset.copy()

		while 1:

			# get the "logically next" iter
			if direction == SEARCH_NEXT:
				iter = self.entrystore.iter_traverse_next(iter)

			else:
				iter = self.entrystore.iter_traverse_prev(iter)

			# if we've wrapped around without a match, return None
			if self.entrystore.iter_compare(iter, offset):
				return None

			# return the match if found
			if self.match(iter):
				return iter


	def match(self, iter):
		"Check if an entry matches the search criteria"

		if iter is None:
			return gtk.FALSE

		entry = self.entrystore.get_entry(iter)


		# check the entry type
		if entry.type == revelation.entry.ENTRY_FOLDER and self.folders == gtk.FALSE:
			return gtk.FALSE

		if self.type is not None and entry.type not in [ self.type, revelation.entry.ENTRY_FOLDER ]:
			return gtk.FALSE


		# check the entry fields
		items = [ entry.name, entry.description ]

		if self.namedesc:
			for field in entry.get_fields():
				if field.value != "":
					items.append(field.value)


		# run the search
		for item in items:
			if self.casesens == gtk.TRUE and item.find(self.string) >= 0:
				return gtk.TRUE

			elif self.casesens == gtk.FALSE and item.lower().find(self.string.lower()) >= 0:
				return gtk.TRUE

		return gtk.FALSE


gobject.type_register(EntrySearch)
gobject.signal_new("changed", EntrySearch, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())



class EntryStore(revelation.widget.TreeStore):
	"A basic class for handling a tree of entries"

	def __init__(self):
		revelation.widget.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_PYOBJECT)

		self.file		= None
		self.password		= None
		self.filepassword	= None
		self.changed		= gtk.FALSE

		self.connect("file-changed", self.__cb_file_changed)


	def __setattr__(self, name, value):
		"Custom attribute access"

		revelation.widget.TreeStore.__setattr__(self, name, value)

		if name == "file":
			self.emit("file-changed", value)

		elif name == "password":
			self.changed = gtk.TRUE


	def __cb_file_changed(self, widget, file = None):
		"Callback for when the file changes"

		if file is None:
			self.password = None
			self.filepassword = None

		self.changed = gtk.FALSE


	def add_entry(self, parent, entry = None, sibling = None):
		"Adds an entry"

		# place after "parent" if it's not a folder
		if parent is not None and self.get_entry(parent).type != revelation.entry.ENTRY_FOLDER:
			iter = self.insert_after(self.iter_parent(parent), parent)

		# place before sibling, if given
		elif sibling is not None:
			iter = self.insert_before(parent, sibling)

		# otherwise, append to parent
		else:
			iter = self.append(parent)

		self.update_entry(iter, entry)
		self.changed = gtk.TRUE

		return iter


	def clear(self):
		"Removes all entries in the EntryStore"

		revelation.widget.TreeStore.clear(self)

		self.set_file(None, None, None)
		self.changed = gtk.FALSE

		self.emit("cleared")


	def export_entry(self, iter, dest, destparent = None, destsibling = None):
		"Exports an entry, and all its children, into a different EntryStore"

		destchild = dest.add_entry(destparent, self.get_entry(iter), destsibling)

		for i in range(self.iter_n_children(iter)):
			self.export_entry(self.iter_nth_child(iter, i), dest, destchild)

		return destchild


	def get_entry(self, iter):
		"Fetches data for an entry"

		if iter is None:
			return None

		entry = revelation.entry.Entry(self.get_value(iter, ENTRYSTORE_COL_TYPE))

		entry.name		= self.get_value(iter, ENTRYSTORE_COL_NAME)
		entry.description	= self.get_value(iter, ENTRYSTORE_COL_DESC)
		entry.updated		= self.get_value(iter, ENTRYSTORE_COL_UPDATED)
		entry.fields		= self.get_value(iter, ENTRYSTORE_COL_FIELDS)

		return entry


	def get_entries(self, iters):
		"Fetches a list of entries"

		entries = []

		for iter in iters:
			entries.append(self.get_entry(iter))

		return entries


	def import_entrystore(self, source, parent = None, sibling = None):
		"Imports entries from a different entrystore"

		newiters = []

		# go through each base entry in the source, and export it
		# from the source to self
		for i in range(source.iter_n_children(None)):
			sourceiter = source.iter_nth_child(None, i)
			newiter = source.export_entry(sourceiter, self, parent, sibling)
			newiters.append(newiter)

		return newiters


	def remove_entry(self, iter):
		"Removes an entry, and its children if any"

		parent = self.iter_parent(iter)
		self.remove(iter)
		self.changed = gtk.TRUE

		# collapse parent if empty
		if self.iter_n_children(parent) == 0:
			self.set_folder_state(parent, gtk.FALSE)


	def replace_entrystore(self, source):
		"Replaces the current entrystore data with those of a different entrystore"

		self.clear()
		self.import_entrystore(source)
		self.set_file(source.file, source.password, source.filepassword)


	def set_file(self, file, password = None, filepassword = None):
		"Sets the current file for the data"

		self.password = password

		if filepassword is not None:
			self.filepassword = filepassword

		else:
			self.filepassword = password

		self.file = file


	def set_folder_state(self, iter, open):
		"Sets the state of a folder (collapsed or expanded)"

		if iter is None or self.get_entry(iter).type != revelation.entry.ENTRY_FOLDER:
			return

		elif open:
			self.set_value(iter, ENTRYSTORE_COL_ICON, revelation.stock.STOCK_FOLDER_OPEN)

		else:
			self.set_value(iter, ENTRYSTORE_COL_ICON, revelation.stock.STOCK_FOLDER)


	def update_entry(self, iter, entry):
		"Updates data for an entry"

		if iter is None or entry is None:
			return

		self.set_value(iter, ENTRYSTORE_COL_NAME, entry.name)
		self.set_value(iter, ENTRYSTORE_COL_TYPE, entry.type)
		self.set_value(iter, ENTRYSTORE_COL_DESC, entry.description)
		self.set_value(iter, ENTRYSTORE_COL_UPDATED, entry.updated)
		self.set_value(iter, ENTRYSTORE_COL_FIELDS, entry.fields)

		# keep icon if current is folder-open and the type still is folder
		if entry.type != revelation.entry.ENTRY_FOLDER or self.get_value(iter, ENTRYSTORE_COL_ICON) != revelation.stock.STOCK_FOLDER_OPEN:
			self.set_value(iter, ENTRYSTORE_COL_ICON, entry.icon)

		self.changed = gtk.TRUE


gobject.signal_new("cleared", EntryStore, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new("file-changed", EntryStore, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT,))



class EntryClipboard(EntryStore):
	"Copies/cuts/pastes entries to/from another entrystore"

	def __init__(self):
		EntryStore.__init__(self)


	def copy(self, entrystore, iters):
		"Copies a group of entries from an entrystore"

		if len(iters) == 0 or None in iters:
			return

		self.clear()

		for iter in iters:
			entrystore.export_entry(iter, self)

		self.emit("copy")


	def cut(self, entrystore, iters):
		"Cuts a group of entries from an entrystore"

		self.copy(entrystore, iters)

		for iter in iters:
			entrystore.remove_entry(iter)

		self.emit("cut")


	def paste(self, entrystore, parent, sibling = None):
		"Pastes the clipboard contents into an entrystore"

		iters = entrystore.import_entrystore(self, parent, sibling)
		self.emit("paste")

		return iters


gobject.signal_new("copy", EntryClipboard, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new("cut", EntryClipboard, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new("paste", EntryClipboard, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())



class UndoAction(gobject.GObject):
	"A class containing data about an action that can be undone/redone"

	def __init__(self, action):
		gobject.GObject.__init__(self)

		self.set_action(action)
		self.data = []


	def add_data(self, path, parent, data):
		"Adds a piece of data to the action"

		self.data.append({
			"path"		: path,
			"parent"	: parent,
			"data"		: data
		})


	def set_action(self, action):
		"Sets the type of action"

		self.action = action

		if self.action == UNDO_ACTION_ADD:
			self.name	= "Add Entry"
			self.actiontype	= UNDO_ACTIONTYPE_ADD

		elif self.action == UNDO_ACTION_CUT:
			self.name	= "Cut"
			self.actiontype	= UNDO_ACTIONTYPE_REMOVE

		elif self.action == UNDO_ACTION_EDIT:
			self.name	= "Edit Entry"
			self.actiontype	= UNDO_ACTIONTYPE_EDIT

		elif self.action == UNDO_ACTION_IMPORT:
			self.name	= "Import"
			self.actiontype	= UNDO_ACTIONTYPE_ADD

		elif self.action == UNDO_ACTION_PASTE:
			self.name	= "Paste"
			self.actiontype	= UNDO_ACTIONTYPE_ADD

		elif self.action == UNDO_ACTION_REMOVE:
			self.name	= "Remove Entry"
			self.actiontype	= UNDO_ACTIONTYPE_REMOVE



class UndoQueue(gobject.GObject):
	"Handles undo/redo for an entrystore"

	def __init__(self, entrystore):
		gobject.GObject.__init__(self)

		self.entrystore	= entrystore
		self.queue	= []
		self.actionptr	= 0

		self.entrystore.connect("cleared", self.__cb_entrystore_cleared)


	def __cb_entrystore_cleared(self, widget, data = None):
		"Cleares the undo queue when the entry store is cleared"

		self.clear()


	def add_action(self, action, iters, extradata = None):
		"Adds an action to the undo queue"

		if not isinstance(iters, list) and iters != None:
			iters = [iters]

		# get data about the action
		actionitem = UndoAction(action)

		for iter in iters:
			path		= self.entrystore.get_path(iter)
			parent		= self.entrystore.get_path(self.entrystore.iter_parent(iter))

			if action == UNDO_ACTION_EDIT:
				data	= (self.entrystore.get_entry(iter), extradata)

			else:
				data	= EntryStore()
				self.entrystore.export_entry(iter, data)

			actionitem.add_data(path, parent, data)


		# remove any items later in the queue and add the action
		del self.queue[self.actionptr:]

		self.queue.append(actionitem)
		self.actionptr = len(self.queue)

		self.emit("changed")


	def can_redo(self):
		"Checks if a redo action is possible"

		return self.actionptr < len(self.queue)


	def can_undo(self, method = UNDO):
		"Checks if an undo action is possible"

		return self.actionptr > 0


	def clear(self):
		"Clears the undo queue"

		self.queue = []
		self.actionptr = 0
		self.emit("changed")


	def execute(self, action, method = UNDO):
		"Executes and undo or redo action"

		iters = []

		# undo add, or redo remove (same operation)
		if (method == UNDO and action.actiontype == UNDO_ACTIONTYPE_ADD) or (method == REDO and action.actiontype == UNDO_ACTIONTYPE_REMOVE):
			for item in action.data:
				item["iter"] = self.entrystore.get_iter(item["path"])

			for item in action.data:
				self.entrystore.remove_entry(item["iter"])

		# undo remove, or redo add (same operation)
		elif (method == UNDO and action.actiontype == UNDO_ACTIONTYPE_REMOVE) or (method == REDO and action.actiontype == UNDO_ACTIONTYPE_ADD):
			for item in action.data:
				newiters = self.entrystore.import_entrystore(item["data"], self.entrystore.get_iter(item["parent"]), self.entrystore.get_iter(item["path"]))
				iters.extend(newiters)

		# handle edit actions
		elif action.actiontype == UNDO_ACTIONTYPE_EDIT:
			iter = self.entrystore.get_iter(action.data[0]["path"])
			iters.append(iter)

			if method == UNDO:
				self.entrystore.update_entry(iter, action.data[0]["data"][1])

			elif method == REDO:
				self.entrystore.update_entry(iter, action.data[0]["data"][0])

		return iters


	def get_action(self, method = UNDO):
		"Fetches the current UndoAction object for an operation"

		if method == UNDO and self.can_undo():
			return self.queue[self.actionptr - 1]

		elif method == REDO and self.can_redo():
			return self.queue[self.actionptr]


	def redo(self):
		"Executes a redo operation"

		if not self.can_redo():
			return

		iters = self.execute(self.get_action(REDO), REDO)
		self.actionptr += 1
		self.emit("changed")

		return iters


	def undo(self):
		"Executes an undo operation"

		if not self.can_undo():
			return

		iters = self.execute(self.get_action(), UNDO)
		self.actionptr -= 1
		self.emit("changed")

		return iters


gobject.type_register(UndoQueue)
gobject.signal_new("changed", UndoQueue, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())

