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
		iter = offset

		while 1:
			if direction == SEARCH_NEXT:
				iter = self.entrystore.iter_traverse_next(iter)
			else:
				iter = self.entrystore.iter_traverse_prev(iter)

			if self.entrystore.iter_compare(iter, offset):
				return None

			if self.match(iter):
				return iter


	def match(self, iter):
		if iter == None:
			return gtk.FALSE

		entry = self.entrystore.get_entry(iter)

		# check type
		if entry.type == revelation.entry.ENTRY_FOLDER and self.folders == gtk.FALSE:
			return gtk.FALSE

		if self.type is not None and entry.type not in [ self.type, revelation.entry.ENTRY_FOLDER ]:
			return gtk.FALSE

		# check the items
		items = [ entry.name, entry.description ]
		if self.namedesc == gtk.FALSE:
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


gobject.signal_new("string_changed", EntrySearch, gobject.SIGNAL_ACTION, gobject.TYPE_BOOLEAN, (gobject.TYPE_STRING, ))



class EntryStore(revelation.widget.TreeStore):
	"A basic class structure for handling a tree of entries"

	def __init__(self):
		revelation.widget.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_PYOBJECT)
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
		self.changed = gtk.FALSE


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

		entry = revelation.entry.Entry()

		entry.name		= self.get_value(iter, ENTRYSTORE_COL_NAME)
		entry.description	= self.get_value(iter, ENTRYSTORE_COL_DESC)
		entry.updated		= self.get_value(iter, ENTRYSTORE_COL_UPDATED)

		entry.set_type(self.get_value(iter, ENTRYSTORE_COL_TYPE))
		entry.fields		= self.get_value(iter, ENTRYSTORE_COL_FIELDS)

		return entry


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


	def set_folder_state(self, iter, open):
		"Sets the state of a folder (collapsed or expanded)"

		if iter is None or self.get_entry(iter).type != revelation.entry.ENTRY_FOLDER:
			return

		if open:
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



class EntryClipboard(EntryStore):
	"Copies/cuts/pastes entries to/from another entrystore"

	def __init__(self):
		EntryStore.__init__(self)


	def copy(self, entrystore, iters):
		"Copies a group of nodes from an entrystore"

		if len(iters) > 0 and None not in iters:
			self.clear()

			for iter in iters:
				entrystore.export_entry(iter, self)

			self.emit("copy")


	def cut(self, entrystore, iters):
		"Cuts a group of nodes from an entrystore"

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

