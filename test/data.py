#!/usr/bin/env python

#
# Revelation 0.4.2 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for data module
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

import gobject, gtk, unittest

from revelation import data, entry, ui



class Clipboard_clear(unittest.TestCase):
	"Clipboard.clear()"

	def test_clear(self):
		"Clipboard.clear() clears the clipboard"

		c = data.Clipboard()
		c.set("just a test")
		self.assertEquals(c.get(), "just a test")

		c.clear()
		self.assertEquals(c.get(), "")


	def test_clipboard_primary(self):
		"Clipboard.clear() clears both CLIPBOARD and PRIMARY"

		c = data.Clipboard()
		c.set("test123")
		c.clear()

		self.assertEquals(gtk.clipboard_get("CLIPBOARD").wait_for_text() in ( "", None ), True)
		self.assertEquals(gtk.clipboard_get("PRIMARY").wait_for_text() in ( "", None ), True)



class Clipboard_get(unittest.TestCase):
	"Clipboard.get()"

	def test_chain(self):
		"Clipboard.get() returns next chain item"

		c = data.Clipboard()
		c.set( [ "a", "b", "c" ] )

		self.assertEquals(c.get(), "a")
		self.assertEquals(c.get(), "b")
		self.assertEquals(c.get(), "c")


	def test_chain_clipboard_primary(self):
		"Clipboard.get() chain is split over CLIPBOARD and PRIMARY"

		c = data.Clipboard()
		c.set( [ "a", "b", "c", "d" ] )

		self.assertEquals(gtk.clipboard_get("CLIPBOARD").wait_for_text(), "a")
		self.assertEquals(gtk.clipboard_get("PRIMARY").wait_for_text(), "b")
		self.assertEquals(gtk.clipboard_get("CLIPBOARD").wait_for_text(), "c")
		self.assertEquals(gtk.clipboard_get("PRIMARY").wait_for_text(), "d")


	def test_chain_last(self):
		"Clipboard.get() returns last chain item on chain end"

		c = data.Clipboard()
		c.set( [ "a", "b", "c" ] )

		self.assertEquals(c.get(), "a")
		self.assertEquals(c.get(), "b")
		self.assertEquals(c.get(), "c")
		self.assertEquals(c.get(), "c")


	def test_clipboard(self):
		"Clipboard.get() returns CLIPBOARD contents, not PRIMARY"

		clip = gtk.clipboard_get("CLIPBOARD")
		clip.set_text("clipboardtest")

		pri = gtk.clipboard_get("PRIMARY")
		pri.set_text("primarytest")

		c = data.Clipboard()
		self.assertEquals(c.get(), "clipboardtest")


	def test_get(self):
		"Clipboard.get() returns the clipboard contents"

		c = data.Clipboard()
		c.set("test123")
		self.assertEquals(c.get(), "test123")


	def test_none(self):
		"Clipboard.get() returns empty string if no contents"

		c = data.Clipboard()
		c.clear()
		self.assertEquals(c.get(), "")



class Clipboard_has_contents(unittest.TestCase):
	"Clipboard.has_contents()"

	def test_chain(self):
		"Clipboard.has_contents() doesn't affect chain pointer"

		c = data.Clipboard()
		c.set( [ "a", "b", "c" ])

		c.get()
		c.has_contents()
		self.assertEquals(c.get(), "b")


	def test_contents(self):
		"Clipboard.has_contents() returns True when contents"

		c = data.Clipboard()
		c.set("test123")
		self.assertEquals(c.has_contents(), True)


	def test_empty(self):
		"Clipboard.has_contents() returns False when empty"

		c = data.Clipboard()
		c.clear()
		self.assertEquals(c.has_contents(), False)



class Clipboard_set(unittest.TestCase):
	"Clipboard.set()"

	def test_chain(self):
		"Clipboard.set() handles a list as a chain"

		c = data.Clipboard()
		c.set( [ "a", "b", "c" ])

		self.assertEquals(c.get(), "a")
		self.assertEquals(c.get(), "b")
		self.assertEquals(c.get(), "c")


	def test_clipboard_primary(self):
		"Clipboard.set() updates both CLIPBOARD and PRIMARY"

		clip = gtk.clipboard_get("CLIPBOARD")
		clip.clear()

		pri = gtk.clipboard_get("PRIMARY")
		pri.clear()

		c = data.Clipboard()
		c.set("test123")

		self.assertEquals(clip.wait_for_text(), "test123")
		self.assertEquals(pri.wait_for_text(), "test123")


	def test_set(self):
		"Clipboard.set() sets the clipboard contents"

		c = data.Clipboard()

		c.clear()
		self.assertEquals(c.get(), "")

		c.set("test123")
		self.assertEquals(c.get(), "test123")



class EntryClipboard_clear(unittest.TestCase):
	"EntryClipboard.clear()"

	def setUp(self):
		"Sets up common facilities"

		self.entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "Testentry"
		self.entrystore.add_entry(e)


	def test_clipboard_primary(self):
		"EntryClipboard.clear() doesn't touch the CLIPBOARD or PRIMARY selections"

		clip = gtk.clipboard_get("CLIPBOARD")
		clip.set_text("testclip")

		pri = gtk.clipboard_get("PRIMARY")
		pri.set_text("testpri")

		c = data.EntryClipboard()
		c.clear()

		self.assertEquals(clip.wait_for_text(), "testclip")
		self.assertEquals(pri.wait_for_text(), "testpri")


	def test_clear(self):
		"EntryClipboard.clear() clears the clipboard"

		c = data.EntryClipboard()
		c.set(self.entrystore, [ self.entrystore.iter_nth_child(None, 0) ])
		c.clear()

		self.assertEquals(c.get(), None)


	def test_toggle(self):
		"EntryClipboard.clear() emits the content-toggled signal"

		def cb(widget, data):
			global foo
			foo = "success"

		c = data.EntryClipboard()
		c.set(self.entrystore, [ self.entrystore.iter_nth_child(None, 0) ])

		c.connect("content-toggled", cb)
		c.clear()

		self.assertEquals(foo, "success")



class EntryClipboard_get(unittest.TestCase):
	"EntryClipboard.get()"

	def test_corrupt(self):
		"EntryClipboard.get() returns None on corrupt clipboard data"

		c = gtk.clipboard_get("_REVELATION_ENTRY")
		c.set_text("dummydata")
		self.assertEquals(c.wait_for_text(), "dummydata")

		e = data.EntryClipboard()
		self.assertEquals(e.get(), None)


	def test_empty(self):
		"EntryClipboard.get() returns None on empty clipboard"

		c = data.EntryClipboard()
		c.clear()
		self.assertEquals(c.get(), None)


	def test_get(self):
		"EntryClipboard.get() returns a complete entry store"

		# set up entrystore
		entrystore = data.EntryStore()

		f = entry.FolderEntry()
		f.name = "folder"
		folderiter = entrystore.add_entry(f)

		e = entry.GenericEntry()
		e.name = "testentry"
		e.description = "desc"
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		iter = entrystore.add_entry(e, folderiter)

		# do clipboard transfer
		c = data.EntryClipboard()
		c.set(entrystore, [ folderiter ])
		copystore = c.get()

		f2 = copystore.get_entry(copystore.get_iter( (0,) ))
		self.assertEquals(f.name, f2.name)

		e2 = copystore.get_entry(copystore.get_iter( (0,0) ))
		self.assertEquals(e.name, e2.name)
		self.assertEquals(e.description, e2.description)
		self.assertEquals(e[entry.HostnameField], e2[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], e2[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], e2[entry.PasswordField])



class EntryClipboard_has_contents(unittest.TestCase):
	"EntryClipboard.has_contents()"

	def test_contents(self):
		"EntryClipboard.has_contents() returns True on contents"

		entrystore = data.EntryStore()
		e = entry.GenericEntry()
		iter = entrystore.add_entry(e)

		c = data.EntryClipboard()
		c.set(entrystore, [ iter ])

		self.assertEquals(c.has_contents(), True)


	def test_empty(self):
		"EntryClipboard.has_contents() returns False on no contents"

		c = data.EntryClipboard()
		c.clear()

		self.assertEquals(c.has_contents(), False)



class EntryClipboard_set(unittest.TestCase):
	"EntryClipboars.set()"

	def test_set(self):
		"EntryClipboard.set() sets all entry data"

		# set up entrystore
		entrystore = data.EntryStore()

		f = entry.FolderEntry()
		f.name = "folder"
		folderiter = entrystore.add_entry(f)

		e = entry.GenericEntry()
		e.name = "testentry"
		e.description = "desc"
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		iter = entrystore.add_entry(e, folderiter)

		g = entry.GenericEntry()
		g.name = "generic"
		giter = entrystore.add_entry(g)

		# do clipboard transfer
		c = data.EntryClipboard()
		c.set(entrystore, [ folderiter, giter ])
		copystore = c.get()

		f2 = copystore.get_entry(copystore.get_iter( (0,) ))
		self.assertEquals(type(f), type(f2))
		self.assertEquals(f.name, f2.name)

		e2 = copystore.get_entry(copystore.get_iter( (0,0) ))
		self.assertEquals(type(e), type(e2))
		self.assertEquals(e.name, e2.name)
		self.assertEquals(e.description, e2.description)
		self.assertEquals(e[entry.HostnameField], e2[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], e2[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], e2[entry.PasswordField])

		g2 = copystore.get_entry(copystore.get_iter( (1,) ))
		self.assertEquals(type(g), type(g2))
		self.assertEquals(g.name, g2.name)


	def test_toggle(self):
		"EntryClipboard.set() emits the content-toggled signal"

		def cb(widget, data):
			global foo
			foo = "success"

		entrystore = data.EntryStore()
		e = entry.GenericEntry()
		iter = entrystore.add_entry(e)

		c = data.EntryClipboard()
		c.clear()

		c.connect("content-toggled", cb)
		c.set(entrystore, [ iter ])

		self.assertEquals(foo, "success")



class EntrySearch__init(unittest.TestCase):
	"EntrySearch.__init__()"

	def test_attrs(self):
		"EntrySearch.__init__() sets required attributes"

		entrysearch = data.EntrySearch(data.EntryStore())
		self.assertEquals(hasattr(entrysearch, "folders"), True)


	def test_defaults(self):
		"EntrySearch.__init__() sets proper defaults"

		entrysearch = data.EntrySearch(data.EntryStore())
		self.assertEquals(entrysearch.folders, True)
		self.assertEquals(entrysearch.namedesconly, False)
		self.assertEquals(entrysearch.casesensitive, False)



class EntrySearch_find(unittest.TestCase):
	"EntrySearch.find()"


	def setUp(self):
		"Sets up an entrystore for testing"

		self.entrystore = data.EntryStore()
		self.entrysearch = data.EntrySearch(self.entrystore)

		e = entry.GenericEntry()
		e.name = "entry0"
		self.entrystore.add_entry(e)

		e = entry.FolderEntry()
		e.name = "folder0"
		parent = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "entry1"
		self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry2"
		self.entrystore.add_entry(e)


	def test_direction(self):
		"EntrySearch.find() uses direction correctly"

		iter = self.entrysearch.find("entry")
		self.assertEquals(self.entrystore.get_path(iter), (0, ))

		iter = self.entrysearch.find("entry", None, None, data.SEARCH_PREVIOUS)
		self.assertEquals(self.entrystore.get_path(iter), (2, ))


	def test_find(self):
		"EntrySearch.find() returns correct entry"

		iter = self.entrysearch.find("entry1")
		self.assertEquals(self.entrystore.get_path(iter), (1, 0))


	def test_nomatch(self):
		"EntrySearch.find() returns None on no match"

		iter = self.entrysearch.find("test123")
		self.assertEquals(iter, None)


	def test_offset(self):
		"EntrySearch.find() finds next match after offset"

		offset = self.entrystore.get_iter((1, 0))
		iter = self.entrysearch.find("entry", None, offset)

		self.assertEquals(self.entrystore.get_path(iter), (2, ))


	def test_offset_wrap(self):
		"EntrySearch.find() wraps around"

		offset = self.entrystore.get_iter((2, ))
		iter = self.entrysearch.find("entry", None, offset)

		self.assertEquals(self.entrystore.get_path(iter), (0, ))

	def test_offset_nomatch(self):
		"EntrySearch.find() returns None if no match other than offset"

		offset = self.entrystore.get_iter((1, ))
		iter = self.entrysearch.find("folder", None, offset)

		self.assertEquals(iter, None)



class EntrySearch_match(unittest.TestCase):
	"EntrySearch.match()"

	def setUp(self):
		"Sets up an entrystore and entrysearch for testing"

		self.entrystore = data.EntryStore()
		self.entrysearch = data.EntrySearch(self.entrystore)

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"

		self.iter = self.entrystore.add_entry(e)

		e = entry.FolderEntry()
		e.name = "folder"
		self.folderiter = self.entrystore.add_entry(e)


	def test_blank(self):
		"EntrySearch.match() matches on blank string"

		self.assertEquals(self.entrysearch.match(self.iter, ""), True)


	def test_casesensitive(self):
		"EntrySearch.match() uses casesensitive attribute correctly"

		self.entrysearch.casesensitive = True
		self.assertEquals(self.entrysearch.match(self.iter, "NamE"), False)

		self.entrysearch.casesensitive = False
		self.assertEquals(self.entrysearch.match(self.iter, "NamE"), True)


	def test_folder(self):
		"EntrySearch.match() uses folders attribute correctly"

		self.entrysearch.folders = False
		self.assertEquals(self.entrysearch.match(self.folderiter, "folder"), False)

		self.entrysearch.folders = True
		self.assertEquals(self.entrysearch.match(self.folderiter, "folder"), True)


	def test_namedesconly(self):
		"EntrySearch.match() uses namedesconly attribute correctly"

		self.entrysearch.namedesconly = True
		self.assertEquals(self.entrysearch.match(self.iter, "username"), False)

		self.entrysearch.namedesconly = False
		self.assertEquals(self.entrysearch.match(self.iter, "username"), True)


	def test_none(self):
		"EntrySearch.match() returns False on None"

		self.assertEquals(self.entrysearch.match(None, "test"), False)


	def test_string(self):
		"EntrySearch.match() matches on string"

		self.assertEquals(self.entrysearch.match(self.iter, "test"), False)
		self.assertEquals(self.entrysearch.match(self.iter, "name"), True)
		self.assertEquals(self.entrysearch.match(self.iter, "ript"), True)


	def test_type(self):
		"EntrySearch.match() matches on entry type"

		self.assertEquals(self.entrysearch.match(self.iter, "name", entry.GenericEntry), True)
		self.assertEquals(self.entrysearch.match(self.iter, "name", entry.WebEntry), False)



class EntryStore__init(unittest.TestCase):
	"EntryStore.__init__()"

	def test_changed(self):
		"EntryStore.__init__() sets .changed to False"

		e = data.EntryStore()
		self.assertEquals(e.changed, False)


	def test_columns(self):
		"EntryStore.__init__() sets up correct columns"

		e = data.EntryStore()

		self.assertEquals(e.get_n_columns(), 3)
		self.assertEquals(e.get_column_type(0), gobject.TYPE_STRING)
		self.assertEquals(e.get_column_type(1), gobject.TYPE_STRING)
		self.assertEquals(e.get_column_type(2), gobject.TYPE_PYOBJECT)



class EntryStore_add_entry(unittest.TestCase):
	"EntryStore.add_entry()"

	def test_add(self):
		"EntryStore.add_entry() adds an iter"

		entrystore = data.EntryStore()
		e = entry.GenericEntry()

		entrystore.add_entry(e)

		self.assertEquals(entrystore.iter_n_children(None), 1)


	def test_changed(self):
		"EntryStore.add_entry() sets .changed to True"

		entrystore = data.EntryStore()
		e = entry.GenericEntry()

		self.assertEquals(entrystore.changed, False)
		entrystore.add_entry(e)
		self.assertEquals(entrystore.changed, True)


	def test_copy(self):
		"EntryStore.add_entry() stores a copy of the entry"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "test123"

		iter = entrystore.add_entry(e)

		e.name = "changed"

		self.assertEquals(entrystore.get_value(iter, 2).name, "test123")


	def test_data(self):
		"EntryStore.add_entry() stores all data"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1
		e.get_field(entry.HostnameField).value = "hostname"
		e.get_field(entry.UsernameField).value = "username"
		e.get_field(entry.PasswordField).value = "password"

		iter = entrystore.add_entry(e)

		self.assertEquals(entrystore.get_value(iter, 0), "name")
		self.assertEquals(entrystore.get_value(iter, 1), e.icon)

		ce = entrystore.get_value(iter, 2)
		self.assertEquals(e.name, ce.name)
		self.assertEquals(e.description, ce.description)
		self.assertEquals(e.updated, ce.updated)
		self.assertEquals(e[entry.HostnameField], ce[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], ce[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], ce[entry.PasswordField])


	def test_parent(self):
		"EntryStore.add_entry() adds below parent folder"

		entrystore = data.EntryStore()
		parent = entrystore.add_entry(entry.FolderEntry())
		iter = entrystore.add_entry(entry.GenericEntry(), parent)

		self.assertNotEquals(parent, None)
		self.assertEquals(entrystore.iter_n_children(None), 1)
		self.assertEquals(entrystore.iter_n_children(parent), 1)


	def test_parent_notfolder(self):
		"EntryStore.add_entry() appends to root if parent is not folder"

		entrystore = data.EntryStore()
		parent = entrystore.add_entry(entry.GenericEntry())
		iter = entrystore.add_entry(entry.GenericEntry(), parent)

		self.assertNotEquals(parent, None)
		self.assertEquals(entrystore.iter_n_children(None), 2)
		self.assertEquals(entrystore.iter_n_children(parent), 0)


	def test_sibling(self):
		"EntryStore.add_entry() adds before sibling"

		entrystore = data.EntryStore()

		p = entry.FolderEntry()
		p.name = "folder"
		parent = entrystore.add_entry(p)

		s = entry.GenericEntry()
		s.name = "sibling"
		sibling = entrystore.add_entry(s, parent)

		e = entry.GenericEntry()
		e.name = "test123"
		entrystore.add_entry(e, parent, sibling)

		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(parent, 0)).name, "test123")
		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(parent, 1)).name, "sibling")



class EntryStore_clear(unittest.TestCase):
	"EntryStore.clear()"

	def test_changed(self):
		"EntryStore.clear() sets .changed to False"

		entrystore = data.EntryStore()
		entrystore.add_entry(entry.GenericEntry())
		entrystore.add_entry(entry.GenericEntry())

		self.assertEquals(entrystore.changed, True)
		entrystore.clear()
		self.assertEquals(entrystore.changed, False)


	def test_clear(self):
		"EntryStore.clear() removes all entries"

		entrystore = data.EntryStore()
		entrystore.add_entry(entry.GenericEntry())
		entrystore.add_entry(entry.GenericEntry())

		self.assertEquals(entrystore.iter_n_children(None), 2)
		entrystore.clear()
		self.assertEquals(entrystore.iter_n_children(None), 0)



class EntryStore_copy_entry(unittest.TestCase):
	"EntryStore.copy_entry()"

	def test_copy(self):
		"EntryStore.copy_entry() copies entry"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1
		e.get_field(entry.HostnameField).value = "hostname"
		e.get_field(entry.UsernameField).value = "username"
		e.get_field(entry.PasswordField).value = "password"
		iter = entrystore.add_entry(e)

		f = entry.FolderEntry()
		f.name = "folder"
		folderiter = entrystore.add_entry(f)

		newiter = entrystore.copy_entry(iter, folderiter)
		self.assertNotEquals(entrystore.get_path(iter), entrystore.get_path(newiter))

		ce = entrystore.get_entry(newiter)
		self.assertEquals(e.name, ce.name)
		self.assertEquals(e.description, ce.description)
		self.assertEquals(e.updated, ce.updated)
		self.assertEquals(e[entry.HostnameField], ce[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], ce[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], ce[entry.PasswordField])


	def test_recursive(self):
		"EntryStore.copy_entry() copies entries recursively"

		entrystore = data.EntryStore()

		f = entry.FolderEntry()
		f.name = "folder"
		folderiter = entrystore.add_entry(f)

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1
		e.get_field(entry.HostnameField).value = "hostname"
		e.get_field(entry.UsernameField).value = "username"
		e.get_field(entry.PasswordField).value = "password"
		iter = entrystore.add_entry(e, folderiter)

		newiter = entrystore.copy_entry(folderiter, None)
		self.assertNotEquals(entrystore.get_path(folderiter), entrystore.get_path(newiter))

		cf = entrystore.get_entry(newiter)
		self.assertEquals(f.name, cf.name)

		ce = entrystore.get_entry(entrystore.iter_nth_child(newiter, 0))
		self.assertEquals(e.name, ce.name)
		self.assertEquals(e.description, ce.description)
		self.assertEquals(e.updated, ce.updated)
		self.assertEquals(e[entry.HostnameField], ce[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], ce[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], ce[entry.PasswordField])



class EntryStore_filter_parents(unittest.TestCase):
	"EntryStore.filter_parents()"

	def test_filter(self):
		"EntryStore.filter_parents() removes all siblings"

		entrystore = data.EntryStore()

		p1 = entrystore.add_entry(entry.FolderEntry())
		p2 = entrystore.add_entry(entry.FolderEntry())
		p3 = entrystore.add_entry(entry.FolderEntry())

		cp1 = entrystore.add_entry(entry.FolderEntry(), p2)
		cp2 = entrystore.add_entry(entry.FolderEntry(), p3)

		c1 = entrystore.add_entry(entry.GenericEntry(), p1)
		c2 = entrystore.add_entry(entry.GenericEntry(), cp1)
		c3 = entrystore.add_entry(entry.GenericEntry(), cp2)

		self.assertEquals(
			entrystore.filter_parents([ p1, p2, cp1, cp2, c1, c2, c3 ]),
			[ p1, p2, cp2 ]
		)



class EntryStore_folder_expanded(unittest.TestCase):
	"EntryStore.folder_expanded()"

	def test_collapse(self):
		"EntryStore.folder_expanded() sets open folder icon on expand"

		entrystore = data.EntryStore()

		f = entry.FolderEntry()
		folderiter = entrystore.add_entry(f)

		entrystore.folder_expanded(folderiter, True)
		entrystore.folder_expanded(folderiter, False)
		self.assertEquals(entrystore.get_value(folderiter, data.COLUMN_ICON), ui.STOCK_ENTRY_FOLDER)


	def test_expand(self):
		"EntryStore.folder_expanded() sets open folder icon on expand"

		entrystore = data.EntryStore()

		f = entry.FolderEntry()
		folderiter = entrystore.add_entry(f)

		entrystore.folder_expanded(folderiter, True)
		self.assertEquals(entrystore.get_value(folderiter, data.COLUMN_ICON), ui.STOCK_ENTRY_FOLDER_OPEN)



class EntryStore_get_entry(unittest.TestCase):
	"EntryStore.get_entry()"

	def test_copy(self):
		"EntryStore.get_entry() returns a copy of the entry"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "test123"
		iter = entrystore.add_entry(e)

		e = entrystore.get_entry(iter)
		e.name = "changed"

		self.assertEquals(entrystore.get_entry(iter).name, "test123")


	def test_data(self):
		"EntryStore.get_entry() returns all entry data"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1
		e.get_field(entry.HostnameField).value = "hostname"
		e.get_field(entry.UsernameField).value = "username"
		e.get_field(entry.PasswordField).value = "password"

		iter = entrystore.add_entry(e)

		ce = entrystore.get_entry(iter)
		self.assertEquals(e.name, ce.name)
		self.assertEquals(e.description, ce.description)
		self.assertEquals(e.updated, ce.updated)
		self.assertEquals(e[entry.HostnameField], ce[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], ce[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], ce[entry.PasswordField])


	def test_none(self):
		"EntryStore.get_entry() returns None on no iter"

		entrystore = data.EntryStore()
		self.assertEquals(entrystore.get_entry(None), None)



class EntryStore_get_iter(unittest.TestCase):
	"EntryStore.get_iter()"

	def test_inv(self):
		"EntryStore.get_iter() returns None on invalid path"

		self.assertEquals(data.EntryStore().get_iter((0,)), None)


	def test_iter(self):
		"EntryStore.get_iter() returns iter"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "test123"

		entrystore.add_entry(e)
		iter = entrystore.get_iter((0,))

		self.assertEquals(e.name, entrystore.get_entry(iter).name)


	def test_none(self):
		"EntryStore.get_iter() handles None and variations"

		entrystore = data.EntryStore()
		self.assertEquals(entrystore.get_iter(None), None)
		self.assertEquals(entrystore.get_iter(""), None)
		self.assertEquals(entrystore.get_iter(()), None)
		self.assertEquals(entrystore.get_iter([]), None)



class EntryStore_get_path(unittest.TestCase):
	"EntryStore.get_path()"

	def test_none(self):
		"EntryStore.get_path() handles None"

		self.assertEquals(data.EntryStore().get_path(None), None)


	def test_path(self):
		"EntryStore.get_path() returns a path"

		entrystore = data.EntryStore()
		parent = entrystore.add_entry(entry.FolderEntry())
		entrystore.add_entry(entry.GenericEntry(), parent)
		iter = entrystore.add_entry(entry.GenericEntry(), parent)

		self.assertEquals(entrystore.get_path(iter), (0, 1))



class EntryStore_get_popular_values(unittest.TestCase):
	"EntryStore.get_popular_values()"

	def setUp(self):
		"Sets up an entrystore"

		self.entrystore = data.EntryStore()

		for username in [
			"test1",
			"test2", "test2",
			"test3", "test3", "test3",
			"test4", "test4", "test4", "test4",
			"test5", "test5", "test5", "test5", "test5"
		]:
			e = entry.GenericEntry()
			e[entry.UsernameField] = username
			self.entrystore.add_entry(e)

		for password in [
			"pwtest1",
			"pwtest2", "pwtest2",
			"pwtest3", "pwtest3", "pwtest3"
		]:
			e = entry.GenericEntry()
			e[entry.PasswordField] = password
			self.entrystore.add_entry(e)


	def test_alphabetic(self):
		"EntryStore.get_popular_values() returns values alphabetically"

		self.assertEquals(self.entrystore.get_popular_values(entry.UsernameField, 3), [ "test3", "test4", "test5" ])


	def test_field(self):
		"EntryStore.get_popular_values() checks given field only"

		for username in "test3", "test4", "test5":
			self.assertEquals(username in self.entrystore.get_popular_values(entry.UsernameField, 3), True)

		self.assertEquals("pwtest3" in self.entrystore.get_popular_values(entry.PasswordField, 3), True)


	def test_threshold(self):
		"EntryStore.get_popular_values() uses threshold correctly"

		for username in "test3", "test4", "test5":
			self.assertEquals(username in self.entrystore.get_popular_values(entry.UsernameField, 3), True)

		for username in [ "test5" ]:
			self.assertEquals(username in self.entrystore.get_popular_values(entry.UsernameField, 5), True)


	def test_threshold_default(self):
		"EntryStore.get_popular_values() has default threshold of 3"

		for username in "test3", "test4", "test5":
			self.assertEquals(username in self.entrystore.get_popular_values(entry.UsernameField, 3), True)



class EntryStore_import_entry(unittest.TestCase):
	"EntryStore.import_entry()"

	def setUp(self):
		"Set up entrystores"

		self.importstore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1000
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"

		self.importstore.add_entry(e)

		fiter = self.importstore.add_entry(entry.FolderEntry())
		self.importstore.add_entry(entry.GenericEntry(), fiter)
		self.importstore.add_entry(entry.GenericEntry(), fiter)
		self.importstore.add_entry(entry.GenericEntry())


	def test_entrydata(self):
		"EntryStore.import_entry() imports all entry data"

		entrystore = data.EntryStore()
		entrystore.import_entry(self.importstore, self.importstore.iter_nth_child(None, 0))

		e = entrystore.get_entry(entrystore.iter_nth_child(None, 0))
		o = self.importstore.get_entry(self.importstore.iter_nth_child(None, 0))

		self.assertEquals(e.name, o.name)
		self.assertEquals(e.description, o.description)
		self.assertEquals(e.updated, o.updated)
		self.assertEquals(e[entry.HostnameField], o[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], o[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], o[entry.PasswordField])


	def test_parent(self):
		"EntryStore.import_entry() imports to parent correctly"

		entrystore = data.EntryStore()
		fiter = entrystore.add_entry(entry.FolderEntry())
		entrystore.import_entry(self.importstore, self.importstore.iter_nth_child(None, 0), fiter)

		self.assertEquals(entrystore.iter_n_children(fiter), 1)


	def test_recursive(self):
		"EntryStore.import_entry() imports entries recursively"

		entrystore = data.EntryStore()
		entrystore.import_entry(self.importstore, self.importstore.iter_nth_child(None, 1))

		self.assertEquals(entrystore.iter_n_children(entrystore.iter_nth_child(None, 0)), 2)


	def test_return_single(self):
		"EntryStore.import_entry() returns new iter when specified"

		entrystore = data.EntryStore()
		iter = entrystore.import_entry(self.importstore, self.importstore.iter_nth_child(None, 1))

		self.assertEquals(entrystore.get_path(iter), (0, ))


	def test_return_multiple(self):
		"EntryStore.import_entry() returns all new iters when not specified"

		entrystore = data.EntryStore()
		iters = entrystore.import_entry(self.importstore, None)

		self.assertEquals(len(iters), 3)

		for iter, index in zip(iters, range(len(iters))):
			self.assertEquals(entrystore.get_path(iter), (index, ))


	def test_sibling(self):
		"EntryStore.import_entry() places entry before sibling"

		entrystore = data.EntryStore()
		fiter = entrystore.add_entry(entry.FolderEntry())

		e = entry.GenericEntry()
		e.name = "test1"
		entrystore.add_entry(e, fiter)

		e = entry.GenericEntry()
		e.name = "test2"
		sibling = entrystore.add_entry(e, fiter)

		entrystore.import_entry(self.importstore, self.importstore.iter_nth_child(None, 0), fiter, sibling)

		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(fiter, 0)).name, "test1")
		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(fiter, 1)).name, "name")
		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(fiter, 2)).name, "test2")



class EntryStore_iter_traverse_prev(unittest.TestCase):
	"EntryStore.iter_traverse_prev()"

	def setUp(self):
		"Set up the entrystore"

		self.entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "entry0"
		self.entrystore.add_entry(e)

		e = entry.FolderEntry()
		e.name = "folder0"
		parent = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "entry1"
		self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry2"
		self.entrystore.add_entry(e, parent)

		e = entry.FolderEntry()
		e.name = "folder1"
		parent2 = self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry3"
		self.entrystore.add_entry(e, parent2)

		e = entry.GenericEntry()
		e.name = "entry4"
		self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry5"
		self.entrystore.add_entry(e)
	
		e = entry.FolderEntry()
		e.name = "folder2"
		parent = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "entry6"
		self.entrystore.add_entry(e, parent)


	def test_none(self):
		"EntryStore.iter_traverse_prev() returns last node on None"

		iter = self.entrystore.iter_traverse_prev(None)
		self.assertEquals(self.entrystore.get_entry(iter).name, "entry6")


	def test_traverse(self):
		"EntryStore.iter_traverse_prev() uses correct traversal"

		order = (
			"entry6",
			"folder2",
			"entry5",
			"entry4",
			"entry3",
			"folder1",
			"entry2",
			"entry1",
			"folder0",
			"entry0"
		)

		iter = None

		for name in order:
			iter = self.entrystore.iter_traverse_prev(iter)
			self.assertEquals(self.entrystore.get_entry(iter).name, name)



class EntryStore_iter_traverse_next(unittest.TestCase):
	"EntryStore.iter_traverse_next()"

	def setUp(self):
		"Set up the entrystore"

		self.entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "entry0"
		self.entrystore.add_entry(e)

		e = entry.FolderEntry()
		e.name = "folder0"
		parent = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "entry1"
		self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry2"
		self.entrystore.add_entry(e, parent)

		e = entry.FolderEntry()
		e.name = "folder1"
		parent2 = self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry3"
		self.entrystore.add_entry(e, parent2)

		e = entry.GenericEntry()
		e.name = "entry4"
		self.entrystore.add_entry(e, parent)

		e = entry.GenericEntry()
		e.name = "entry5"
		self.entrystore.add_entry(e)
	
		e = entry.FolderEntry()
		e.name = "folder2"
		parent = self.entrystore.add_entry(e)

		e = entry.GenericEntry()
		e.name = "entry6"
		self.entrystore.add_entry(e, parent)


	def test_none(self):
		"EntryStore.iter_traverse_next() returns first node on None"

		iter = self.entrystore.iter_traverse_next(None)
		self.assertEquals(self.entrystore.get_entry(iter).name, "entry0")


	def test_traverse(self):
		"EntryStore.iter_traverse_next() uses correct traversal"

		order = (
			"entry0",
			"folder0",
			"entry1",
			"entry2",
			"folder1",
			"entry3",
			"entry4",
			"entry5",
			"folder2",
			"entry6"
		)

		iter = None

		for name in order:
			iter = self.entrystore.iter_traverse_next(iter)
			self.assertEquals(self.entrystore.get_entry(iter).name, name)



class EntryStore_move_entry(unittest.TestCase):
	"EntryStore.move_entry()"

	def test_entrydata(self):
		"EntryStore.move_entry() preserves all entry data"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "name"
		e.description = "description"
		e.updated = 1000
		e[entry.HostnameField] = "hostname"
		e[entry.UsernameField] = "username"
		e[entry.PasswordField] = "password"
		iter = entrystore.add_entry(e)

		fiter = entrystore.add_entry(entry.FolderEntry())

		entrystore.move_entry(iter, fiter)

		m = entrystore.get_entry(entrystore.iter_nth_child(fiter, 0))

		self.assertEquals(e.name, m.name)
		self.assertEquals(e.description, m.description)
		self.assertEquals(e.updated, m.updated)
		self.assertEquals(e[entry.HostnameField], m[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], m[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], m[entry.PasswordField])


	def test_move(self):
		"EntryStore.move_entry() moves the entry"

		entrystore = data.EntryStore()

		entrystore.add_entry(entry.GenericEntry())
		fiter = entrystore.add_entry(entry.FolderEntry())
		entrystore.add_entry(entry.GenericEntry())

		entrystore.move_entry(entrystore.iter_nth_child(None, 2), fiter)

		self.assertEquals(entrystore.iter_n_children(None), 2)
		self.assertEquals(entrystore.iter_n_children(fiter), 1)


	def test_parent(self):
		"EntryStore.move_entry() moves to parent correctly"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "test1"
		iter = entrystore.add_entry(e)

		fiter = entrystore.add_entry(entry.FolderEntry())

		e = entry.GenericEntry()
		e.name = "test2"
		entrystore.add_entry(e, fiter)

		entrystore.move_entry(iter, fiter)

		e = entrystore.get_entry(entrystore.iter_nth_child(fiter, 1))
		self.assertEquals(e.name, "test1")


	def test_recursive(self):
		"EntryStore.move_entry() moves entries recursively"

		entrystore = data.EntryStore()
		iter = entrystore.add_entry(entry.FolderEntry())
		entrystore.add_entry(entry.GenericEntry(), iter)
		entrystore.add_entry(entry.GenericEntry(), iter)

		fiter = entrystore.add_entry(entry.FolderEntry())

		entrystore.move_entry(iter, fiter)
		self.assertEquals(entrystore.iter_n_children(entrystore.iter_nth_child(fiter, 0)), 2)


	def test_return(self):
		"EntryStore.move_entry() returns new iter"

		entrystore = data.EntryStore()
		iter = entrystore.add_entry(entry.GenericEntry())
		fiter = entrystore.add_entry(entry.FolderEntry())

		newiter = entrystore.move_entry(iter, fiter)
		self.assertEquals(entrystore.get_path(newiter), (0,0))


	def test_sibling(self):
		"EntryStore.move_entry() moves to before sibling"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		e.name = "test1"
		iter = entrystore.add_entry(e)

		fiter = entrystore.add_entry(entry.FolderEntry())

		e = entry.GenericEntry()
		e.name = "test2"
		entrystore.add_entry(e, fiter)

		e = entry.GenericEntry()
		e.name = "test3"
		sibling = entrystore.add_entry(e, fiter)

		entrystore.move_entry(iter, fiter, sibling)

		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(fiter, 0)).name, "test2")
		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(fiter, 1)).name, "test1")
		self.assertEquals(entrystore.get_entry(entrystore.iter_nth_child(fiter, 2)).name, "test3")



class EntryStore_remove_entry(unittest.TestCase):
	"EntryStore.remove_entry()"

	def test_none(self):
		"EntryStore.remove_entry() handles None"

		data.EntryStore().remove_entry(None)


	def test_remove(self):
		"EntryStore.remove_entry() removes entry"

		entrystore = data.EntryStore()
		iter = entrystore.add_entry(entry.GenericEntry())

		self.assertEquals(entrystore.iter_n_children(None), 1)
		entrystore.remove_entry(iter)
		self.assertEquals(entrystore.iter_n_children(None), 0)

	

class EntryStore_update_entry(unittest.TestCase):
	"EntryStore.update_entry()"

	def test_changed(self):
		"EntryStore.update_entry() sets .changed to True"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		iter = entrystore.add_entry(e)
		entrystore.changed = False

		e.name = "test"
		entrystore.update_entry(iter, e)
		self.assertEquals(entrystore.changed, True)


	def test_data(self):
		"EntryStore.update_entry() updates all data"

		entrystore = data.EntryStore()

		e = entry.GenericEntry()
		iter = entrystore.add_entry(e)

		e.name = "name"
		e.description = "description"
		e.updated = 1
		e.get_field(entry.HostnameField).value = "hostname"
		e.get_field(entry.UsernameField).value = "username"
		e.get_field(entry.PasswordField).value = "password"

		entrystore.update_entry(iter, e)

		ce = entrystore.get_entry(iter)
		self.assertEquals(entrystore.get_value(iter, 0), e.name)
		self.assertEquals(entrystore.get_value(iter, 1), e.icon)
		self.assertEquals(e.name, ce.name)
		self.assertEquals(e.description, ce.description)
		self.assertEquals(e.updated, ce.updated)
		self.assertEquals(e[entry.HostnameField], ce[entry.HostnameField])
		self.assertEquals(e[entry.UsernameField], ce[entry.UsernameField])
		self.assertEquals(e[entry.PasswordField], ce[entry.PasswordField])


	def test_none(self):
		"EntryStore.update_entry() accepts None iter"

		entrystore = data.EntryStore()
		entrystore.update_entry(None, None)



class UndoQueue_add_action(unittest.TestCase):
	"UndoQueue.add_action()"

	def test_add(self):
		"UndoQueue.add_action() adds an action"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("test", None, None, {})

		self.assertEquals(undoqueue.can_undo(), True)
		self.assertEquals(undoqueue.can_redo(), False)

		self.assertEquals(undoqueue.get_undo_action(), ( None, "test", {} ))


	def test_inject(self):
		"UndoQueue.add_action() removes actions later in the queue"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("test0", lambda n,d: 1, lambda n,d: 1, {})
		undoqueue.add_action("test1", lambda n,d: 1, lambda n,d: 1, {})
		undoqueue.add_action("test2", lambda n,d: 1, lambda n,d: 1, {})
		undoqueue.add_action("test3", lambda n,d: 1, lambda n,d: 1, {})

		undoqueue.undo()
		undoqueue.undo()

		undoqueue.add_action("test4", lambda n,d: 1, lambda n,d: 1, {})

		self.assertEquals(undoqueue.can_redo(), False)
		self.assertEquals(undoqueue.get_undo_action()[1], "test4")
		undoqueue.undo()
		self.assertEquals(undoqueue.get_undo_action()[1], "test1")



class UndoQueue_can_redo(unittest.TestCase):
	"UndoQueue.can_redo()"

	def test_can_redo(self):
		"UndoQueue.can_redo() returns correct values"

		undoqueue = data.UndoQueue()
		self.assertEquals(undoqueue.can_redo(), False)

		undoqueue.add_action("test", lambda n,d: 1, lambda n,d: 1, None)
		self.assertEquals(undoqueue.can_redo(), False)

		undoqueue.add_action("test", lambda n,d: 1, lambda n,d: 1, None)
		self.assertEquals(undoqueue.can_redo(), False)

		undoqueue.undo()
		self.assertEquals(undoqueue.can_redo(), True)

		undoqueue.undo()
		self.assertEquals(undoqueue.can_redo(), True)

		undoqueue.redo()
		self.assertEquals(undoqueue.can_redo(), True)

		undoqueue.redo()
		self.assertEquals(undoqueue.can_redo(), False)



class UndoQueue_can_undo(unittest.TestCase):
	"UndoQueue.can_undo()"

	def test_can_undo(self):
		"UndoQueue.can_undo() returns correct values"

		undoqueue = data.UndoQueue()
		self.assertEquals(undoqueue.can_undo(), False)

		undoqueue.add_action("test", lambda n,d: 1, lambda n,d: 1, None)
		self.assertEquals(undoqueue.can_undo(), True)

		undoqueue.add_action("test", lambda n,d: 1, lambda n,d: 1, None)
		self.assertEquals(undoqueue.can_undo(), True)

		undoqueue.undo()
		self.assertEquals(undoqueue.can_undo(), True)

		undoqueue.undo()
		self.assertEquals(undoqueue.can_undo(), False)



class UndoQueue_clear(unittest.TestCase):
	"UndoQueue.clear()"

	def test_clear(self):
		"UndoQueue.clear() clears the queue"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("test", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("test", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.undo()

		self.assertEquals(undoqueue.can_redo(), True)
		self.assertEquals(undoqueue.can_undo(), True)

		undoqueue.clear()
		self.assertEquals(undoqueue.can_redo(), False)
		self.assertEquals(undoqueue.can_undo(), False)



class UndoQueue_get_redo_action(unittest.TestCase):
	"UndoQueue.get_redo_action()"

	def test_data(self):
		"UndoQueue.get_redo_action() returns correct data"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("name", lambda n,d: 1, None, [])
		undoqueue.undo()

		self.assertEquals(undoqueue.get_redo_action(), ( None, "name", [] ))


	def test_order(self):
		"UndoQueue.get_redo_action() returns the correct action"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("name0", lambda n,d: 1, None, [])
		undoqueue.add_action("name1", lambda n,d: 1, None, [])
		undoqueue.add_action("name2", lambda n,d: 1, None, [])
		undoqueue.undo()
		undoqueue.undo()

		self.assertEquals(undoqueue.get_redo_action(), ( None, "name1", [] ))



class UndoQueue_get_undo_action(unittest.TestCase):
	"UndoQueue.get_undo_action()"

	def test_data(self):
		"UndoQueue.get_undo_action() returns correct data"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("name", None, lambda n,d: 1, [])
		self.assertEquals(undoqueue.get_undo_action(), ( None, "name", [] ))


	def test_order(self):
		"UndoQueue.get_undo_action() returns the correct action"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("name0", lambda n,d: 1, None, [])
		undoqueue.add_action("name1", lambda n,d: 1, None, [])
		undoqueue.add_action("name2", lambda n,d: 1, None, [])
		undoqueue.undo()
		undoqueue.undo()

		self.assertEquals(undoqueue.get_undo_action()[1], "name0" )




class UndoQueue_redo(unittest.TestCase):
	"UndoQueue.redo()"

	def test_callback(self):
		"UndoQueue.redo() correctly calls the callback"

		global called
		called = False

		def cb(name, actiondata):
			global called
			called = True

			self.assertEquals(name, "name")
			self.assertEquals(actiondata, "data")

		undoqueue = data.UndoQueue()
		undoqueue.add_action("name", lambda n,d: 1, cb, "data")
		undoqueue.undo()
		undoqueue.redo()

		self.assertEquals(called, True)


	def test_increment(self):
		"UndoQueue.redo() increments the action pointer"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("action0", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action1", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action2", lambda n,d: 1, lambda n,d: 1, None)

		undoqueue.undo()
		undoqueue.undo()
		undoqueue.undo()

		self.assertEquals(undoqueue.get_redo_action()[1], "action0")
		undoqueue.redo()
		self.assertEquals(undoqueue.get_redo_action()[1], "action1")
		undoqueue.redo()
		self.assertEquals(undoqueue.get_redo_action()[1], "action2")
		undoqueue.redo()
		self.assertEquals(undoqueue.get_redo_action(), None)


	def test_overflow(self):
		"UndoQueue.redo() doesn't overflow the pointer"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("action0", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action1", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action2", lambda n,d: 1, lambda n,d: 1, None)

		undoqueue.undo()
		undoqueue.undo()
		undoqueue.undo()
		undoqueue.redo()
		undoqueue.redo()
		undoqueue.redo()

		self.assertEquals(undoqueue.get_undo_action()[1], "action2")
		undoqueue.redo()
		self.assertEquals(undoqueue.get_undo_action()[1], "action2")



class UndoQueue_undo(unittest.TestCase):
	"UndoQueue.undo()"

	def test_callback(self):
		"UndoQueue.undo() correctly calls the callback"

		global called
		called = False

		def cb(name, actiondata):
			global called
			called = True

			self.assertEquals(name, "name")
			self.assertEquals(actiondata, "data")

		undoqueue = data.UndoQueue()
		undoqueue.add_action("name", cb, lambda n,d: 1, "data")
		undoqueue.undo()

		self.assertEquals(called, True)


	def test_increment(self):
		"UndoQueue.undo() decrements the action pointer"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("action0", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action1", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action2", lambda n,d: 1, lambda n,d: 1, None)

		self.assertEquals(undoqueue.get_undo_action()[1], "action2")
		undoqueue.undo()

		self.assertEquals(undoqueue.get_undo_action()[1], "action1")
		undoqueue.undo()

		self.assertEquals(undoqueue.get_undo_action()[1], "action0")
		undoqueue.undo()

		self.assertEquals(undoqueue.get_undo_action(), None)


	def test_overflow(self):
		"UndoQueue.undo() doesn't make the pointer negative"

		undoqueue = data.UndoQueue()
		undoqueue.add_action("action0", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action1", lambda n,d: 1, lambda n,d: 1, None)
		undoqueue.add_action("action2", lambda n,d: 1, lambda n,d: 1, None)

		undoqueue.undo()
		undoqueue.undo()

		self.assertEquals(undoqueue.get_undo_action()[1], "action0")

		undoqueue.undo()
		self.assertEquals(undoqueue.get_undo_action(), None)
		self.assertEquals(undoqueue.get_redo_action()[1], "action0")

		undoqueue.undo()
		self.assertEquals(undoqueue.get_undo_action(), None)
		self.assertEquals(undoqueue.get_redo_action()[1], "action0")



if __name__ == "__main__":
	unittest.main()

