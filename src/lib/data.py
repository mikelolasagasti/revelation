#
# Revelation 0.3.3 - a password manager for GNOME 2
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

from revelation import entry

import gobject, gtk


COLUMN_NAME	= 0
COLUMN_ICON	= 1
COLUMN_ENTRY	= 2

SEARCH_NEXT	= "next"
SEARCH_PREV	= "prev"



class EntrySearch(object):
	"Handles searching in an EntryStore"

	def __init__(self, entrystore):
		self.entrystore	= entrystore

		self.folders		= True
		self.namedesconly	= False
		self.casesensitive	= False


	def find(self, string, entrytype = None, offset = None, direction = SEARCH_NEXT):
		"Searches for an entry, starting at the given offset"

		iter = offset

		while 1:

			if direction == SEARCH_NEXT:
				iter = self.entrystore.iter_traverse_next(iter)

			else:
				iter = self.entrystore.iter_traverse_prev(iter)

			# if we've wrapped around, return None
			if self.entrystore.get_path(iter) == self.entrystore.get_path(offset):
				return None

			if self.match(iter, string, entrytype) == True:
				return iter


	def match(self, iter, string, entrytype = None):
		"Check if an entry matches the search criteria"

		if iter is None:
			return False

		e = self.entrystore.get_entry(iter)


		# check entry type
		if type(e) == entry.FolderEntry and self.folders == False:
			return False

		if entrytype is not None and type(e) not in ( entrytype, entry.FolderEntry ):
			return False


		# check entry fields
		items = [ e.name, e.description ]

		if self.namedesconly == False:
			items.extend([ field.value for field in e.fields if field.value != "" ])


		# run the search
		for item in items:
			if self.casesensitive == True and item.find(string) >= 0:
				return True

			elif self.casesensitive == False and item.lower().find(string.lower()) >= 0:
				return True

		return False



class EntryStore(gtk.TreeStore):
	"A data structure for storing entries"

	def __init__(self):
		gtk.TreeStore.__init__(
			self,
			gobject.TYPE_STRING,	# name
			gobject.TYPE_STRING,	# icon
			gobject.TYPE_PYOBJECT	# entry
		)

		self.changed = False


	def add_entry(self, e, parent = None, sibling = None):
		"Adds an entry"

		# place after parent if it's not a folder
		if parent is not None and type(self.get_entry(parent)) != entry.FolderEntry:
			iter = self.insert_after(self.iter_parent(parent), parent)

		# place before sibling, if given
		elif sibling is not None:
			iter = self.insert_before(parent, sibling)

		# otherwise, append to parent
		else:
			iter = self.append(parent)

		self.update_entry(iter, e)
		self.changed = True

		return iter


	def clear(self):
		"Removes all entries"

		gtk.TreeStore.clear(self)
		self.changed = False


	def get_entry(self, iter):
		"Fetches data for an entry"

		if iter is None:
			return None

		return self.get_value(iter, COLUMN_ENTRY).copy()


	def get_iter(self, path):
		"Gets an iter from a path"

		try:
			if path in ( None, "", (), [] ):
				return None

			return gtk.TreeStore.get_iter(self, path)

		except ValueError:
			return None


	def get_path(self, iter):
		"Gets a path from an iter"

		return iter is not None and gtk.TreeStore.get_path(self, iter) or None


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


	def remove_entry(self, iter):
		"Removes an entry, and its children if any"

		if iter is None:
			return None

		self.remove(iter)
		self.changed = True


	def update_entry(self, iter, e):
		"Updates an entry"

		if None in ( iter, e):
			return None

		self.set_value(iter, COLUMN_NAME, e.name)
		self.set_value(iter, COLUMN_ICON, e.icon)
		self.set_value(iter, COLUMN_ENTRY, e.copy())

		self.changed = True



class UndoQueue(object):
	"Handles undo/redo tracking"

	def __init__(self):
		self.queue	= []
		self.pointer	= 0


	def add_action(self, name, cb_undo, cb_redo, actiondata):
		"Adds an action to the undo queue"

		del self.queue[self.pointer:]

		self.queue.append(( name, cb_undo, cb_redo, actiondata ))
		self.pointer = len(self.queue)


	def can_redo(self):
		"Checks if a redo action is possible"

		return self.pointer < len(self.queue)


	def can_undo(self):
		"Checks if an undo action is possible"

		return self.pointer > 0


	def clear(self):
		"Clears the queue"

		self.queue = []
		self.pointer = 0


	def get_redo_action(self):
		"Returns data for the next redo operation"

		if self.can_redo() == False:
			return None

		name, cb_undo, cb_redo, actiondata = self.queue[self.pointer]

		return cb_redo, name, actiondata


	def get_undo_action(self):
		"Returns data for the next undo operation"

		if self.can_undo() == False:
			return None

		name, cb_undo, cb_redo, actiondata = self.queue[self.pointer - 1]

		return cb_undo, name, actiondata


	def redo(self):
		"Executes a redo operation"

		if self.can_redo() == False:
			return None

		cb_redo, name, actiondata = self.get_redo_action()
		self.pointer += 1

		cb_redo(name, actiondata)


	def undo(self):
		"Executes an undo operation"

		if self.can_undo() == False:
			return None

		cb_undo, name, actiondata = self.get_undo_action()
		self.pointer -= 1

		cb_undo(name, actiondata)

