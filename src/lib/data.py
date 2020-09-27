#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing data-related functionality
#
#
# Copyright (c) 2003-2006 Erik Grinaker
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from . import datahandler, entry

from gi.repository import GObject, Gtk, Gdk, GLib
import time


COLUMN_NAME  = 0
COLUMN_ICON  = 1
COLUMN_ENTRY = 2

SEARCH_NEXT     = "next"
SEARCH_PREVIOUS = "prev"



class Clipboard(GObject.GObject):
    "A normal text-clipboard"

    def __init__(self):
        GObject.GObject.__init__(self)

        self.clip_clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.clip_primary   = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)

        self.cleartimer     = Timer(10)
        self.cleartimeout   = 60
        self.cleartimer.connect("ring", self.__cb_clear_ring)

        self.content        = None
        self.contentpointer = 0


    def __cb_clear(self, clipboard, data = None):
        "Clears the clipboard data"

        self.clip_clipboard.clear()
        self.clip_primary.clear()


    def __cb_clear_ring(self, widget):
        "Handles cleartimer rings"

        self.content        = None
        self.contentpointer = 0
        self.set("", False)


    def __cb_get(self, clipboard, selectiondata, info, data):
        "Returns text for clipboard requests"

        if self.content is None:
            text = ""

        elif type(self.content) == list:

            if len(self.content) == 0:
                text = ""

            else:
                text = self.content[self.contentpointer]

            if self.contentpointer < len(self.content) - 1:
                self.contentpointer += 1

        else:
            text = str(self.content)

        selectiondata.set_text(text, len(text))


    def clear(self):
        "Clears the clipboard"

        self.clip_clipboard.clear()
        self.clip_primary.clear()


    def get(self):
        "Fetches text from the clipboard"

        text = self.clip_clipboard.wait_for_text()

        if text is None:
            text = ""

        return text


    def has_contents(self):
        "Checks if the clipboard has any contents"

        return self.clip_clipboard.wait_is_text_available()


    def set(self, content, secret = False):
        "Copies text to the clipboard"

        self.content        = content
        self.contentpointer = 0

        targets = [
            Gtk.TargetEntry.new( "text/plain",    0, 0 ),
            Gtk.TargetEntry.new( "STRING",        0, 0 ),
            Gtk.TargetEntry.new( "TEXT",          0, 0 ),
            Gtk.TargetEntry.new( "COMPOUND_TEXT", 0, 0 ),
            Gtk.TargetEntry.new( "UTF8_STRING",   0, 0 )
        ]

        self.clip_clipboard.set_text(' '.join(self.content), -1)
        self.clip_primary.set_text(' '.join(self.content), -1)


        if secret == True:
            self.cleartimer.start(self.cleartimeout)

        else:
            self.cleartimer.stop()



class EntryClipboard(GObject.GObject):
    "A clipboard for entries"

    def __init__(self):
        GObject.GObject.__init__(self)

        self.clipboard = Gtk.Clipboard.get_for_display(display=Gdk.Display.get_default(), selection=Gdk.Atom.intern("_REVELATION_ENTRY",False))
        self.__has_contents = False

        GObject.timeout_add(500, lambda: self.__check_contents())


    def __check_contents(self):
        "Callback which check the clipboard"

        state = self.has_contents()

        if state != self.__has_contents:
            self.emit("content-toggled", state)
            self.__has_contents = state

        return True


    def clear(self):
        "Clears the clipboard"

        self.clipboard.clear()
        self.__check_contents()


    def get(self):
        "Fetches entries from the clipboard"

        try:
            xml = self.clipboard.wait_for_text()

            if xml in ( None, "" ):
                return None

            handler = datahandler.RevelationXML()
            entrystore = handler.import_data(xml)

            return entrystore

        except datahandler.HandlerError:
            return None


    def has_contents(self):
        "Checks if the clipboard has any contents"

        return self.clipboard.wait_for_text() is not None


    def set(self, entrystore, iters):
        "Copies entries from an entrystore to the clipboard"

        copystore = EntryStore()

        for iter in entrystore.filter_parents(iters):
            copystore.import_entry(entrystore, iter)

        xml = datahandler.RevelationXML().export_data(copystore)
        self.clipboard.set_text(xml,-1)

        self.__check_contents()


GObject.signal_new("content-toggled", EntryClipboard,
                   GObject.SignalFlags.ACTION, GObject.TYPE_BOOLEAN,
                   ( GObject.TYPE_BOOLEAN, ))



class EntrySearch(GObject.GObject):
    "Handles searching in an EntryStore"

    def __init__(self, entrystore):
        GObject.GObject.__init__(self)
        self.entrystore = entrystore

        self.folders        = True
        self.namedesconly   = False
        self.casesensitive  = False


    def find(self, string, entrytype = None, offset = None, direction = SEARCH_NEXT):
        "Searches for an entry, starting at the given offset"

        iter = offset

        while True:

            if direction == SEARCH_NEXT:
                iter = self.entrystore.iter_traverse_next(iter)

            else:
                iter = self.entrystore.iter_traverse_prev(iter)

            # if we've wrapped around, return None
            if self.entrystore.get_path(iter) == self.entrystore.get_path(offset):
                return None

            if self.match(iter, string, entrytype) == True:
                return iter


    def find_all(self, string, entrytype = None):
        "Searches for all entries matching a term"

        matches = []
        iter = self.entrystore.iter_children(None)

        while iter != None:

            if self.match(iter, string, entrytype) == True:
                matches.append(iter)

            iter = self.entrystore.iter_traverse_next(iter)

        return matches


    def match(self, iter, string, entrytype = None):
        "Check if an entry matches the search criteria"

        if iter is None or not string:
            return False

        e = self.entrystore.get_entry(iter)


        # check entry type
        if type(e) == entry.FolderEntry and self.folders == False:
            return False

        if entrytype is not None and type(e) not in ( entrytype, entry.FolderEntry ):
            return False


        # check entry fields
        items = [ e.name, e.description, e.notes ]

        if self.namedesconly == False:
            items.extend([ field.value for field in e.fields if field.value != "" ])


        # run the search
        for item in items:
            if self.casesensitive == True and string in item:
                return True

            elif self.casesensitive == False and string.lower() in item.lower():
                return True

        return False



class EntryStore(Gtk.TreeStore):
    "A data structure for storing entries"

    def __init__(self):
        Gtk.TreeStore.__init__(
            self,
            GObject.TYPE_STRING,    # name
            GObject.TYPE_STRING,    # icon
            GObject.TYPE_PYOBJECT   # entry
        )

        self.changed = False
        self.connect("row-has-child-toggled", self.__cb_iter_has_child)

        self.set_sort_func(COLUMN_NAME, self.__cmp)
        self.set_sort_column_id(COLUMN_NAME, Gtk.SortType.ASCENDING)


    def __cmp(self, treemodel, iter1, iter2, user_data=None):
        name1 = treemodel.get_value(iter1, COLUMN_NAME).strip().lower()
        name2 = treemodel.get_value(iter2, COLUMN_NAME).strip().lower()

        return (name1 > name2) - (name1 < name2)


    def __cb_iter_has_child(self, widget, path, iter):
        "Callback for iters having children"

        if self.iter_n_children(iter) == 0:
            self.folder_expanded(iter, False)


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

        Gtk.TreeStore.clear(self)
        self.changed = False


    def copy_entry(self, iter, parent = None, sibling = None):
        "Copies an entry recursively"

        newiter = self.add_entry(self.get_entry(iter), parent, sibling)

        for i in range(self.iter_n_children(iter)):
            child = self.iter_nth_child(iter, i)
            self.copy_entry(child, newiter)

        return newiter


    def filter_parents(self, iters):
        "Removes all descendants from the list of iters"

        parents = []

        for child in iters:
            for parent in iters:
                if self.is_ancestor(parent, child):
                    break

            else:
                parents.append(child)

        return parents


    def folder_expanded(self, iter, expanded):
        "Sets the expanded state of an entry"

        e = self.get_entry(iter)

        if e is None or type(e) != entry.FolderEntry:
            return

        elif expanded == True:
            self.set_value(iter, COLUMN_ICON, e.openicon)

        else:
            self.set_value(iter, COLUMN_ICON, e.icon)


    def get_entry(self, iter):
        "Fetches data for an entry"

        if iter is None:
            return None

        e = self.get_value(iter, COLUMN_ENTRY)

        if e is None:
            return None

        else:
            return e.copy()


    def get_iter(self, path):
        "Gets an iter from a path"

        try:
            if not path:
                return None

            if isinstance(path, list):
                path = tuple(path)

            return Gtk.TreeStore.get_iter(self, path)

        except ValueError:
            return None


    def get_path(self, iter):
        "Gets a path from an iter"

        return iter is not None and Gtk.TreeStore.get_path(self, iter) or None


    def get_popular_values(self, fieldtype, threshold = 3):
        "Gets popular values for a field type"

        valuecount = {}
        iter = self.iter_nth_child(None, 0)

        while iter is not None:
            e = self.get_entry(iter)

            if e.has_field(fieldtype) == False:
                iter = self.iter_traverse_next(iter)
                continue

            value = e[fieldtype].strip()

            if value != "":
                if value not in valuecount:
                    valuecount[value] = 0

                valuecount[value] += 1

            iter = self.iter_traverse_next(iter)

        popular = [ value for value, count in valuecount.items() if count >= threshold ]
        popular.sort()

        return popular


    def import_entry(self, source, iter, parent = None, sibling = None):
        "Recursively copies an entry from a different entrystore"

        if iter is not None:
            copy = self.add_entry(source.get_entry(iter), parent, sibling)
            parent, sibling = copy, None

        else:
            copy = None

        newiters = []
        for i in range(source.iter_n_children(iter)):
            child = source.iter_nth_child(iter, i)
            newiter = self.import_entry(source, child, parent, sibling)
            newiters.append(newiter)

        return copy is not None and copy or newiters


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


    def move_entry(self, iter, parent = None, sibling = None):
        "Moves an entry"

        newiter = self.copy_entry(iter, parent, sibling)
        self.remove_entry(iter)

        return newiter


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



class Timer(GObject.GObject):
    "Handles timeouts etc"

    def __init__(self, resolution = 1):
        GObject.GObject.__init__(self)

        self.offset  = None
        self.timeout = None

        GLib.timeout_add(resolution * 1000, self.__cb_check)


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


GObject.signal_new("ring", Timer, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, ())



class UndoQueue(GObject.GObject):
    "Handles undo/redo tracking"

    def __init__(self):
        GObject.GObject.__init__(self)

        self.queue  = []
        self.pointer    = 0


    def add_action(self, name, cb_undo, cb_redo, actiondata):
        "Adds an action to the undo queue"

        del self.queue[self.pointer:]

        self.queue.append(( name, cb_undo, cb_redo, actiondata ))
        self.pointer = len(self.queue)

        self.emit("changed")


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

        self.emit("changed")


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
        self.emit("changed")


    def undo(self):
        "Executes an undo operation"

        if self.can_undo() == False:
            return None

        cb_undo, name, actiondata = self.get_undo_action()
        self.pointer -= 1

        cb_undo(name, actiondata)
        self.emit("changed")


GObject.type_register(UndoQueue)
GObject.signal_new("changed", UndoQueue, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, ())

