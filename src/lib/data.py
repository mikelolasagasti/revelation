#
# Revelation 0.3.0 - a password manager for GNOME 2
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

import gtk, revelation, gobject


ENTRYSTORE_COL_NAME		= 0
ENTRYSTORE_COL_ICON		= 1
ENTRYSTORE_COL_TYPE		= 2
ENTRYSTORE_COL_DESC		= 3
ENTRYSTORE_COL_UPDATED		= 4
ENTRYSTORE_COL_FIELDS		= 5

UNDO				= "undo"
REDO				= "redo"

SEARCH_NEXT			= "next"
SEARCH_PREV			= "prev"


class EntrySearch(gobject.GObject):

	def __init__(self, entrystore):
		gobject.GObject.__init__(self)
		self.entrystore = entrystore

		self.string = ""
		self.type = None
		self.folders = gtk.TRUE
		self.namedesc = gtk.FALSE
		self.casesens = gtk.FALSE


	def __setattr__(self, name, value):
		if name == "string":
			self.emit("string_changed", value)

		gobject.GObject.__setattr__(self, name, value)


	def find(self, offset, direction = SEARCH_NEXT):
		if direction == SEARCH_NEXT:
			traverse = self.entrystore.iter_traverse_next
		else:
			traverse = self.entrystore.iter_traverse_prev

		iter = traverse(offset)

		while not self.entrystore.iter_compare(iter, offset):
			if self.match(iter) == gtk.TRUE:
				return iter

			iter = traverse(iter)

		return None


	def match(self, iter):
		if iter == None:
			return gtk.FALSE

		data = self.entrystore.get_entry(iter)

		# check type
		if data["type"] == revelation.entry.ENTRY_FOLDER and self.folders == gtk.FALSE:
			return gtk.FALSE

		if self.type is not None and data["type"] not in [ self.type, revelation.entry.ENTRY_FOLDER ]:
			return gtk.FALSE

		# check the items
		items = [ data["name"], data["description"] ]
		if self.namedesc == gtk.FALSE:
			items.extend(data["fields"].values())

		# run the search
		for item in items:
			if self.casesens == gtk.TRUE and item.find(self.string) >= 0:
				return gtk.TRUE
			elif self.casesens == gtk.FALSE and item.lower().find(self.string.lower()) >= 0:
				return gtk.TRUE

		return gtk.FALSE


gobject.signal_new("string_changed", EntrySearch, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_STRING, ))



class TreeStore(gtk.TreeStore):

	def filter_parents(self, iters):
		parents = []
		for child in iters:
			for parent in iters:
				if self.is_ancestor(parent, child):
					break
			else:
				parents.append(child)

		return parents


	def get_iter(self, path):
		if path in [ None, "", () ]:
			return None

		try: iter = gtk.TreeStore.get_iter(self, path)
		except ValueError: iter = None

		return iter


	def get_path(self, iter):
		if iter is None:
			return None
		else:
			return gtk.TreeStore.get_path(self, iter)


	def has_contents(self):
		return self.iter_n_children(None) > 0


	def is_empty(self):
		return self.iter_n_children(None) == 0


	def iter_compare(self, iter1, iter2):
		return self.get_path(iter1) == self.get_path(iter2)


	def iter_traverse_next(self, iter):
		
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



class EntryStore(TreeStore):

	def __init__(self):
		TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_PYOBJECT)


	def add_entry(self, parent, data = None):
		iter = self.append(parent)
		self.update_entry(iter, data)
		return iter


	def export_entrystore(self, iters = [], entrystore = None, parent = None):
		if entrystore == None:
			entrystore = EntryStore()

		for iter in iters:
			child = entrystore.add_entry(parent, self.get_entry(iter))

			for i in range(self.iter_n_children(iter)):
				self.export_entrystore([self.iter_nth_child(iter, i)], entrystore, child)

		return entrystore


	def get_entry(self, iter):
		if iter == None:
			return None

		data = {
			"name"		: self.get_value(iter, ENTRYSTORE_COL_NAME),
			"type"		: self.get_value(iter, ENTRYSTORE_COL_TYPE),
			"icon"		: self.get_value(iter, ENTRYSTORE_COL_ICON),
			"description"	: self.get_value(iter, ENTRYSTORE_COL_DESC),
			"updated"	: self.get_value(iter, ENTRYSTORE_COL_UPDATED),
			"fields"	: self.get_value(iter, ENTRYSTORE_COL_FIELDS)
		}

		for field in revelation.entry.get_entry_fields(data["type"]):
			if not data["fields"].has_key(field):
				data["fields"][field] = ""

		return data


	def get_entry_type(self, iter):
		if iter is None:
			return None
		else:
			return self.get_value(iter, ENTRYSTORE_COL_TYPE)


	def import_entrystore(self, entrystore, parent = None, sibling = None, importiter = None):
		baseiters = []

		for i in range(entrystore.iter_n_children(importiter)):
			importchild = entrystore.iter_nth_child(importiter, i)

			if sibling == None:
				childiter = self.add_entry(parent, entrystore.get_entry(importchild))
			else:
				childiter = self.insert_entry_before(parent, sibling, entrystore.get_entry(importchild))

			baseiters.append(childiter)

			if entrystore.iter_has_child(importchild):
				self.import_entrystore(entrystore, childiter, None, importchild)

		return baseiters


	def import_entrystore_after(self, entrystore, parent, sibling):
		return self.import_entrystore(entrystore, parent, self.iter_next(sibling))


	def import_entrystore_before(self, entrystore, parent, sibling):
		return self.import_entrystore(entrystore, parent, sibling)


	def insert_entry_after(self, parent, sibling, data = None):
		iter = self.insert_after(parent, sibling)
		self.update_entry(iter, data)
		return iter


	def insert_entry_before(self, parent, sibling, data = None):
		iter = self.insert_before(parent, sibling)
		self.update_entry(iter, data)
		return iter


	def remove_entry(self, iter):
		while self.iter_has_child(iter):
			self.remove_entry(self.iter_nth_child(iter, 0))
		self.remove(iter)


	def update_entry(self, iter, data):
		if data is not None:
			self.set_value(iter, ENTRYSTORE_COL_NAME, data.get("name", ""))
			self.set_value(iter, ENTRYSTORE_COL_TYPE, data.get("type", revelation.entry.ENTRY_FOLDER))
			self.set_value(iter, ENTRYSTORE_COL_DESC, data.get("description", ""))
			self.set_value(iter, ENTRYSTORE_COL_UPDATED, data.get("updated", 0))
			self.set_value(iter, ENTRYSTORE_COL_FIELDS, data.get("fields", {}))
			self.set_value(iter, ENTRYSTORE_COL_ICON, revelation.entry.get_entry_data(data.get("type", revelation.entry.ENTRY_FOLDER), "icon"))



class DataStore(EntryStore):

	def __init__(self):
		EntryStore.__init__(self)
		self.changed = gtk.FALSE


	def add_entry(self, parent, data = None):

		# place inside parent if folder
		if self.get_entry_type(parent) in (revelation.entry.ENTRY_FOLDER, None):
			iter = EntryStore.add_entry(self, parent, data)

		# place after "parent" if not folder
		else:
			iter = EntryStore.insert_entry_after(self, self.iter_parent(parent), parent, data)

		self.changed = gtk.TRUE

		return iter


	def clear(self):
		EntryStore.clear(self)
		self.changed = gtk.FALSE


	def get_entry(self, iter):
		data = EntryStore.get_entry(self, iter)

		# always return the normal, closed folder icon for folders.
		# the open folder icon is only for tree-internal use.
		if data is not None and data["icon"] == revelation.stock.STOCK_FOLDER_OPEN:
			data["icon"] = revelation.stock.STOCK_FOLDER

		return data


	def remove_entry(self, iter):
		parent = self.iter_parent(iter)
		EntryStore.remove_entry(self, iter)

		# collapse parent if empty
		if self.iter_n_children(parent) == 0:
			self.set_folder_state(parent, gtk.FALSE)

		self.changed = gtk.TRUE


	def set_folder_state(self, iter, open):
		if iter == None or self.get_entry_type(iter) != revelation.entry.ENTRY_FOLDER:
			return

		if open == gtk.TRUE:
			icon = revelation.stock.STOCK_FOLDER_OPEN
		else:
			icon = revelation.stock.STOCK_FOLDER

		self.set_value(iter, ENTRYSTORE_COL_ICON, icon)


	def update_entry(self, iter, data):
		if data is None:
			return

		EntryStore.update_entry(self, iter, data)

		# keep icon if current is folder-open and the type still is folder
		if data["type"] == revelation.entry.ENTRY_FOLDER and self.get_value(iter, ENTRYSTORE_COL_ICON) == revelation.stock.STOCK_FOLDER_OPEN:
			self.set_value(iter, ENTRYSTORE_COL_ICON, revelation.stock.STOCK_FOLDER_OPEN)

		self.changed = gtk.TRUE



class EntryClipboard(EntryStore):

	def __init__(self):
		EntryStore.__init__(self)


	def copy(self, datastore, iters):
		if len(iters) > 0 and None not in iters:
			self.clear()
			datastore.export_entrystore(iters, self)
			self.emit("copy")


	def cut(self, datastore, iters):
		self.copy(datastore, iters)

		for iter in iters:
			datastore.remove_entry(iter)

		self.emit("cut")


	def paste(self, datastore, parent, sibling = None):
		if sibling == None:
			iters = datastore.import_entrystore(self, parent)
		else:
			iters = datastore.import_entrystore_after(self, parent, sibling)

		self.emit("paste")
		return iters


gobject.signal_new("copy", EntryClipboard, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new("cut", EntryClipboard, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())
gobject.signal_new("paste", EntryClipboard, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, ())



class UndoQueue(gobject.GObject):

	def __init__(self):
		gobject.GObject.__init__(self)
		self.queue = []
		self.actionptr = 0


	def add_action(self, name, action, data):

		# remove any items later in the queue
		del self.queue[self.actionptr:]

		self.queue.append({ "name" : name, "action" : action, "data" : data })
		self.actionptr = len(self.queue)

		self.emit("can-undo", self.can_undo())
		self.emit("can-redo", self.can_undo(REDO))


	def can_undo(self, method = UNDO):
		if method == UNDO:
			return self.actionptr > 0
		else:
			return self.actionptr < len(self.queue)


	def clear(self):
		self.queue = []
		self.actionptr = 0

		self.emit("can-undo", gtk.FALSE)
		self.emit("can-redo", gtk.FALSE)


	def get_data(self, method = UNDO):
		if method == UNDO:
			ptr = self.actionptr - 1
		else:
			ptr = self.actionptr

		if self.can_undo(method):
			return self.queue[ptr]
		else:
			return None


	def redo(self):
		if self.can_undo(REDO):
			self.emit("redo", self.get_data(REDO))
			self.actionptr = self.actionptr + 1

		self.emit("can-undo", self.can_undo())
		self.emit("can-redo", self.can_undo(REDO))


	def undo(self):
		if self.can_undo():
			self.emit("undo", self.get_data())
			self.actionptr = self.actionptr - 1

		self.emit("can-undo", self.can_undo())
		self.emit("can-redo", self.can_undo(REDO))


gobject.signal_new("undo", UndoQueue, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new("redo", UndoQueue, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new("can-undo", UndoQueue, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_BOOLEAN, ))
gobject.signal_new("can-redo", UndoQueue, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_BOOLEAN, ))

