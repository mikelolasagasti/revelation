#!/usr/bin/env python

#
# Revelation 0.4.1 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for ui module
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

import gnome, gobject, gtk, unittest

from revelation import config, data, entry, ui



class attrs(unittest.TestCase):
	"ui attributes"

	def test_entry_icons(self):
		"ui module has required entry stock icons"

		self.assertEquals(hasattr(ui, "STOCK_ENTRY_FOLDER"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_FOLDER_OPEN"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_CREDITCARD"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_CRYPTOKEY"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_DATABASE"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_DOOR"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_EMAIL"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_FTP"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_GENERIC"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_PHONE"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_SHELL"), True)
		self.assertEquals(hasattr(ui, "STOCK_ENTRY_WEBSITE"), True)


	def test_icon_sizes(self):
		"ui module has required icon sizes"

		self.assertEquals(hasattr(ui, "ICON_SIZE_DATAVIEW"), True)
		self.assertEquals(hasattr(ui, "ICON_SIZE_DROPDOWN"), True)
		self.assertEquals(hasattr(ui, "ICON_SIZE_LOGO"), True)
		self.assertEquals(hasattr(ui, "ICON_SIZE_TREEVIEW"), True)

		self.assertEquals(gtk.icon_size_lookup(ui.ICON_SIZE_DATAVIEW), (24, 24))
		self.assertEquals(gtk.icon_size_lookup(ui.ICON_SIZE_DROPDOWN), (18, 18))
		self.assertEquals(gtk.icon_size_lookup(ui.ICON_SIZE_LOGO), (32, 32))
		self.assertEquals(gtk.icon_size_lookup(ui.ICON_SIZE_TREEVIEW), (18, 18))



	def test_stock_items(self):
		"ui module has required stock items"

		self.assertEquals(hasattr(ui, "STOCK_ADD"), True)
		self.assertEquals(hasattr(ui, "STOCK_DISCARD"), True)
		self.assertEquals(hasattr(ui, "STOCK_EDIT"), True)
		self.assertEquals(hasattr(ui, "STOCK_EXPORT"), True)
		self.assertEquals(hasattr(ui, "STOCK_GENERATE"), True)
		self.assertEquals(hasattr(ui, "STOCK_GOTO"), True)
		self.assertEquals(hasattr(ui, "STOCK_IMPORT"), True)
		self.assertEquals(hasattr(ui, "STOCK_LOCK"), True)
		self.assertEquals(hasattr(ui, "STOCK_NEXT"), True)
		self.assertEquals(hasattr(ui, "STOCK_OVERWRITE"), True)
		self.assertEquals(hasattr(ui, "STOCK_PASSWORD_CHANGE"), True)
		self.assertEquals(hasattr(ui, "STOCK_PREVIOUS"), True)
		self.assertEquals(hasattr(ui, "STOCK_REMOVE"), True)
		self.assertEquals(hasattr(ui, "STOCK_RELOAD"), True)
		self.assertEquals(hasattr(ui, "STOCK_REVELATION"), True)



class config_bind(unittest.TestCase):
	"config_bind()"

	def setUp(self):
		"sets up common facilities for the test"

		self.config = config.Config()


	def test_check(self):
		"config_bind() handles check items correctly"

		self.config.set("view/searchbar", True)

		# test initial state
		check = ui.CheckButton("Test")
		ui.config_bind(self.config, "view/searchbar", check)
		gtk_run()
		self.assertEquals(check.get_active(), True)

		# test config value change
		self.config.set("view/searchbar", False)
		gtk_run()
		self.assertEquals(check.get_active(), False)

		# test widget change
		check.set_active(True)
		gtk_run()
		self.assertEquals(self.config.get("view/searchbar"), True)


	def test_entry(self):
		"config_bind() handles entries correctly"

		self.config.set("file/autoload_file", "test123")

		# test initial state
		entry = ui.Entry()
		ui.config_bind(self.config, "file/autoload_file", entry)
		gtk_run()
		self.assertEquals(entry.get_text(), "test123")

		# test config value change
		self.config.set("file/autoload_file", "test again")
		gtk_run()
		self.assertEquals(entry.get_text(), "test again")

		# test widget change
		entry.set_text("")
		gtk_run()
		self.assertEquals(self.config.get("file/autoload_file"), "")


	def test_return(self):
		"config_bind() returns the id of the callback"

		check = ui.CheckButton("test")
		id = ui.config_bind(self.config, "view/searchbar", check)
		self.assertEquals(self.config.callbacks.has_key(id), True)


	def test_spin(self):
		"config_bind() handles spin entries correctly"

		self.config.set("view/pane-position", 500)

		# test initial state
		spin = ui.SpinEntry()
		ui.config_bind(self.config, "view/pane-position", spin)
		gtk_run()
		self.assertEquals(spin.get_value(), 500)

		# test config value change
		self.config.set("view/pane-position", 200)
		gtk_run()
		self.assertEquals(spin.get_value(), 200)

		# test widget change
		spin.set_value(300)
		gtk_run()
		self.assertEquals(self.config.get("view/pane-position"), 300)


	def test_unrealize(self):
		"config_bind() removes the callback when the widget is destroyed"

		check = ui.CheckButton()
		id = ui.config_bind(self.config, "view/searchbar", check)
		self.assertEquals(self.config.callbacks.has_key(id), True)

		hbox = ui.HBox()
		hbox.pack_start(check)
		hbox.destroy()
		gtk_run()

		self.assertEquals(self.config.callbacks.has_key(id), False)



class generate_field_display_widget(unittest.TestCase):
	"generate_field_display_widget()"

	def test_value(self):
		"generate_field_display_widget() sets field value on widget"

		for field in entry.FIELDLIST:
			field = field()
			field.value = "test123"

			widget = ui.generate_field_display_widget(field)
			self.assertEquals(widget.get_text(), "test123")


	def test_widgets(self):
		"generate_field_display_widget() generates correct widgets"

		for field in entry.FIELDLIST:
			field = field()
			widget = ui.generate_field_display_widget(field)

			if field.datatype in ( entry.DATATYPE_EMAIL, entry.DATATYPE_URL ):
				self.assertEquals(type(widget), ui.LinkButton)

			elif field.datatype == entry.DATATYPE_PASSWORD:
				self.assertEquals(type(widget), ui.PasswordLabel)

			else:
				self.assertEquals(type(widget), ui.Label)



class generate_field_edit_widget(unittest.TestCase):
	"generate_field_display_widget()"

	def test_value(self):
		"generate_field_edit_widget() sets the field value in the widget"

		for field in entry.FIELDLIST:
			field = field()
			field.value = "test123"

			widget = ui.generate_field_edit_widget(field)

			if type(widget) != ui.FileEntry:
				self.assertEquals(widget.get_text(), "test123")


	def test_widgets(self):
		"generate_field_edit_widget() generates correct widgets"

		for field in entry.FIELDLIST:
			field = field()
			widget = ui.generate_field_edit_widget(field)

			if type(field) == entry.PasswordField:
				self.assertEquals(type(widget), ui.PasswordEntryGenerate)

			elif type(field) == entry.UsernameField:
				self.assertEquals(type(widget), ui.ComboBoxEntry)

			elif field.datatype == entry.DATATYPE_FILE:
				self.assertEquals(type(widget), ui.FileEntry)

			elif field.datatype == entry.DATATYPE_PASSWORD:
				self.assertEquals(type(widget), ui.PasswordEntry)

			else:
				self.assertEquals(type(widget), ui.Entry)



class App(unittest.TestCase):
	"App"

	def test_subclass(self):
		"App is subclass of gnome.ui.App"

		self.assertEquals(isinstance(ui.App("test"), gnome.ui.App), True)



class App_add_toolbar(unittest.TestCase):
	"App.add_toolbar()"

	def test_toolbar(self):
		"App.add_toolbar() doesn't crash :)"

		a = ui.App("test")
		t = ui.Toolbar()
		a.add_toolbar(t, "toolbar", 0, False)



class App_get_title(unittest.TestCase):
	"App.get_title()"

	def test_stripname(self):
		"App.get_title() returns title without appname"

		a = ui.App("test")
		a.set_title("testtitle")
		self.assertEquals(a.get_title(), "testtitle")



class App_run(unittest.TestCase):
	"App.run()"

	def test_mainloop(self):
		"App.run() starts a gtk mainloop"

		global foo
		foo = False

		def cb():
			global foo
			foo = True
			gtk.main_quit()

		a = ui.App("test")

		gobject.timeout_add(100, cb)
		a.run()

		self.assertEquals(foo, True)
		a.destroy()



class App_set_title(unittest.TestCase):
	"App.set_title()"

	def test_appname(self):
		"App.set_title() appends revelation appname to title"

		a = ui.App("test")
		a.set_title("title")

		self.assertEquals(gtk.Window.get_title(a), "title - " + config.APPNAME)



class Button(unittest.TestCase):
	"Button"

	def test_callback(self):
		"Button attaches callback from arg"

		global foo
		foo = False

		def cb(widget, data = None):
			global foo
			foo = True

		b = ui.Button("test", cb)
		b.clicked()
		gtk_run()

		self.assertEquals(foo, True)


	def test_label(self):
		"Button sets label text from arg"

		self.assertEquals(ui.Button("test123").get_label(), "test123")


	def test_stock(self):
		"Button uses stock items if given"

		self.assertEquals(ui.Button("test").get_use_stock(), True)


	def test_subclass(self):
		"Button is subclass of gtk.Button"

		self.assertEquals(isinstance(ui.Button("test"), gtk.Button), True)



class CheckButton(unittest.TestCase):
	"CheckButton"

	def test_subclass(self):
		"CheckButton is subclass of gtk.CheckButton"

		self.assertEquals(isinstance(ui.CheckButton(), gtk.CheckButton), True)



class ComboBoxEntry(unittest.TestCase):
	"ComboBoxEntry"

	def test_activates_default(self):
		"ComboBoxEntry activates default dialog response by default"

		self.assertEquals(ui.ComboBoxEntry().child.get_activates_default(), True)


	def test_completion(self):
		"ComboBoxEntry sets up an EntryCompletion"

		e = ui.ComboBoxEntry()
		self.assertEquals(e.completion.get_model() is e.model, True)
		self.assertEquals(e.child.get_completion() is e.completion, True)


	def test_model(self):
		"ComboBoxEntry sets up text liststore"

		e = ui.ComboBoxEntry()

		self.assertEquals(hasattr(e, "model"), True)
		self.assertEquals(e.model.get_n_columns(), 1)
		self.assertEquals(e.model.get_column_type(0), gobject.TYPE_STRING)
		self.assertEquals(e.get_text_column(), 0)


	def test_subclass(self):
		"ComboBoxEntry is subclass of gtk.ComboBoxEntry"

		self.assertEquals(isinstance(ui.ComboBoxEntry(), gtk.ComboBoxEntry), True)


	def test_values(self):
		"ComboBoxEntry takes values as arg"

		e = ui.ComboBoxEntry([ "a", "b", "c" ])

		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 0), 0), "a")
		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 1), 0), "b")
		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 2), 0), "c")



class ComboBoxEntry_get_text(unittest.TestCase):
	"ComboBoxEntry.get_text()"

	def test_text(self):
		"ComboBoxEntry.get_text() returns contents of child entry"

		e = ui.ComboBoxEntry("test123")
		self.assertEquals(e.get_text(), e.child.get_text())



class ComboBoxEntry_set_values(unittest.TestCase):
	"ComboBoxEntry.set_values()"

	def test_clear(self):
		"ComboBoxEntry.set_values() replaces existing values"

		e = ui.ComboBoxEntry()
		e.set_values([ "test1", "test2" ])
		e.set_values([ "a", "b", "c" ])

		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 0), 0), "a")
		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 1), 0), "b")
		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 2), 0), "c")


	def test_values(self):
		"ComboBoxEntry.set_values() sets dropdown values"

		e = ui.ComboBoxEntry()
		e.set_values([ "a", "b", "c" ])

		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 0), 0), "a")
		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 1), 0), "b")
		self.assertEquals(e.model.get_value(e.model.iter_nth_child(None, 2), 0), "c")



class ComboBoxEntry_set_text(unittest.TestCase):
	"ComboBoxEntry.set_text()"

	def test_none(self):
		"ComboBoxEntry.set_text() clears entry on None"

		e = ui.ComboBoxEntry()
		e.set_text("test123")
		e.set_text(None)
		self.assertEquals(e.get_text(), "")


	def test_text(self):
		"ComboBoxEntry.set_text() sets entry text"

		e = ui.ComboBoxEntry()
		e.set_text("test123")
		self.assertEquals(e.get_text(), "test123")



class DropDown(unittest.TestCase):
	"DropDown"

	def test_model(self):
		"DropDown model can store text, stock-icon and data"

		d = ui.DropDown()
		self.assertEquals(d.model.get_n_columns(), 3)
		self.assertEquals(d.model.get_column_type(0), gobject.TYPE_STRING)
		self.assertEquals(d.model.get_column_type(1), gobject.TYPE_STRING)
		self.assertEquals(d.model.get_column_type(2), gobject.TYPE_PYOBJECT)


	def test_subclass(self):
		"DropDown is subclass of gtk.ComboBox"

		self.assertEquals(isinstance(ui.DropDown(), gtk.ComboBox), True)



class DropDown_append_item(unittest.TestCase):
	"DropDown.append_item"

	def test_append(self):
		"DropDown.append_item() appends item to model"

		d = ui.DropDown()

		d.append_item("test")
		self.assertEquals(d.model.iter_n_children(None), 1)
		self.assertEquals(d.get_item(0), ( "test", None, None))

		d.append_item("test123")
		self.assertEquals(d.model.iter_n_children(None), 2)
		self.assertEquals(d.get_item(1), ( "test123", None, None))


	def test_data(self):
		"DropDown.append_item() stores all data"

		d = ui.DropDown()
		d.append_item("test", ui.STOCK_REVELATION, {} )
		self.assertEquals(d.get_item(0), ( "test", ui.STOCK_REVELATION, {} ))



class DropDown_delete_item(unittest.TestCase):
	"DropDown.delete_item()"

	def test_delete(self):
		"DropDown.delete_item() deletes item"

		d = ui.DropDown()
		d.append_item("test1")
		d.append_item("test2")
		d.append_item("test3")

		d.delete_item(1)
		self.assertEquals(d.get_item(0), ( "test1", None, None ))
		self.assertEquals(d.get_item(1), ( "test3", None, None ))
		self.assertEquals(d.model.iter_n_children(None), 2)



class DropDown_get_active_item(unittest.TestCase):
	"DropDown.get_active_item()"

	def test_active(self):
		"DropDown.get_active_item() returns data for the active item"

		d = ui.DropDown()
		d.append_item("test1")
		d.append_item("test2")
		d.append_item("test3")

		d.set_active(0)
		self.assertEquals(d.get_active_item(), ( "test1", None, None ))

		d.set_active(2)
		self.assertEquals(d.get_active_item(), ( "test3", None, None ))


	def test_data(self):
		"DropDown.get_active_item() returns all data"

		d = ui.DropDown()
		d.append_item("test", ui.STOCK_REVELATION, {})
		d.set_active(0)
		self.assertEquals(d.get_active_item(), ( "test", ui.STOCK_REVELATION, {} ))



class DropDown_get_item(unittest.TestCase):
	"DropDown.get_item()"

	def test_data(self):
		"DropDown.get_item() returns all data"

		d = ui.DropDown()
		d.append_item("test", ui.STOCK_REVELATION, {})
		self.assertEquals(d.get_item(0), ( "test", ui.STOCK_REVELATION, {} ))



class DropDown_insert_item(unittest.TestCase):
	"DropDown.insert_item()"

	def test_data(self):
		"DropDown.insert_item() stores all data"

		d = ui.DropDown()
		d.append_item("test1")
		d.insert_item(0, "test2", ui.STOCK_REVELATION, {})

		self.assertEquals(d.get_item(0), ( "test2", ui.STOCK_REVELATION, {} ))


	def test_position(self):
		"DropDown.insert_item() stores item at correct position"

		d = ui.DropDown()
		d.append_item("test1")
		d.append_item("test2")
		d.insert_item(1, "test3")

		self.assertEquals(d.get_item(0), ( "test1", None, None ))
		self.assertEquals(d.get_item(1), ( "test3", None, None ))
		self.assertEquals(d.get_item(2), ( "test2", None, None ))



class Entry(unittest.TestCase):
	"Entry"

	def test_activates_default(self):
		"Entry activates default dialog response by default"

		self.assertEquals(ui.Entry().get_activates_default(), True)


	def test_subclass(self):
		"Entry is subclass of gtk.Entry"

		self.assertEquals(isinstance(ui.Entry(), gtk.Entry), True)


	def test_text(self):
		"Entry takes text as arg"

		self.assertEquals(ui.Entry("test123").get_text(), "test123")



class Entry_set_text(unittest.TestCase):
	"Entry.set_text()"

	def test_none(self):
		"Entry.set_text() blanks entry on None"

		e = ui.Entry("test")
		e.set_text(None)
		self.assertEquals(e.get_text(), "")


	def test_text(self):
		"Entry.set_text() sets text correctly"

		e = ui.Entry()
		e.set_text("test")
		self.assertEquals(e.get_text(), "test")



class EventBox(unittest.TestCase):
	"EventBox"

	def test_child(self):
		"EventBox takes child as argument"

		label = ui.Label("test")
		eventbox = ui.EventBox(label)
		self.assertEquals(eventbox.get_child() is label, True)


	def test_subclass(self):
		"EventBox is subclass of gtk.EventBox"

		self.assertEquals(isinstance(ui.EventBox(), gtk.EventBox), True)



class EntryDropDown(unittest.TestCase):
	"EntryDropDown"

	def test_data(self):
		"EntryDropDown stores correct data"

		d = ui.EntryDropDown()
		name, stock, e = d.get_item(0)
		self.assertEquals(e.typename, name)
		self.assertEquals(e.icon, stock)


	def test_entries(self):
		"EntryDropDown stores all entries"

		entries = entry.ENTRYLIST[:]
		d = ui.EntryDropDown()

		for index in range(d.model.iter_n_children(None)):
			name, stock, e = d.get_item(index)
			self.assertEquals(e in entries, True)
			entries.remove(e)

		self.assertEquals(entries, [])


	def test_subclass(self):
		"EntryDropDown is subclass of DropDown"

		self.assertEquals(isinstance(ui.EntryDropDown(), ui.DropDown), True)



class EntryDropDown_get_active_type(unittest.TestCase):
	"EntryDropDown.get_active_type()"

	def test_active(self):
		"EntryDropDown.get_active_type() returns active type"

		d = ui.EntryDropDown()
		d.set_active(3)

		self.assertEquals(d.get_item(3)[2], d.get_active_type())



class EntryDropDown_set_active_type(unittest.TestCase):
	"EntryDropDown.set_active_type()"

	def test_active(self):
		"EntryDropDown.set_active_type() sets active type"

		d = ui.EntryDropDown()
		d.set_active_type(entry.GenericEntry)
		self.assertEquals(d.get_active_type(), entry.GenericEntry)



class EntryTree(unittest.TestCase):
	"EntryTree"

	def test_crs(self):
		"EntryTree sets up proper cell renderers"

		t = ui.EntryTree(data.EntryStore())
		crs = t.get_column(0).get_cell_renderers()

		if type(crs[0]) == gtk.CellRendererPixbuf:
			cr_pixbuf = crs[0]
			cr_text = crs[1]

		elif type(crs[0]) == gtk.CellRendererText:
			cr_text = crs[0]
			cr_pixbuf = crs[1]

		self.assertEquals(cr_pixbuf.get_property("stock-size"), ui.ICON_SIZE_TREEVIEW)



class EntryView(unittest.TestCase):
	"EntryView"

	def test_subclass(self):
		"EntryView is subclass of gtk.VBox"

		self.assertEquals(isinstance(ui.EntryView(), gtk.VBox), True)



class EntryView_clear(unittest.TestCase):
	"EntryView.clear()"

	def test_children(self):
		"EntryView.clear() empties widget contents"

		v = ui.EntryView()

		e = entry.GenericEntry()
		e.name = "test"
		e[entry.UsernameField] = "username"

		v.display_entry(e)
		v.clear()
		self.assertEquals(len(v.get_children()), 0)


	def test_entry(self):
		"EntryView.clear() clears the entry attribute"

		v = ui.EntryView()
		v.display_entry(entry.GenericEntry())
		v.clear()

		self.assertEquals(v.entry, None)



class EntryView_display_entry(unittest.TestCase):
	"EntryView"

	def test_display(self):
		"EntryView.display_entry() displays entry"

		v = ui.EntryView()

		e = entry.GenericEntry()
		e.name = "test"
		e.description = "desc"
		e[entry.UsernameField] = "username"

		v.display_entry(e)
		self.assertNotEqual(len(v.get_children()), 0)


	def test_entry(self):
		"EntryView.display_entry() sets entry attribute"

		v = ui.EntryView()
		e = entry.GenericEntry()
		v.display_entry(e)

		self.assertEquals(v.entry is e, True)



class EntryView_display_info(unittest.TestCase):
	"EntryView.display_info()"

	def test_clear(self):	
		"EntryView.display_info() removes the entry"

		v = ui.EntryView()
		v.display_entry(entry.GenericEntry())
		v.display_info()

		self.assertEquals(v.entry, None)


	def test_display(self):
		"EntryView.display_info() displays info"

		v = ui.EntryView()
		v.display_info()

		self.assertNotEqual(len(v.get_children()), 0)



class FileEntry(unittest.TestCase):
	"FileEntry"

	def test_button(self):
		"FileEntry has Button as button attribute"

		self.assertEquals(isinstance(ui.FileEntry().button, ui.Button), True)


	def test_entry(self):
		"FileEntry has Entry as entry attribute"

		self.assertEquals(isinstance(ui.FileEntry().entry, ui.Entry), True)


	def test_file(self):
		"FileEntry takes file as argument"

		e = ui.FileEntry(None, "/bin/ls")
		self.assertEquals(e.get_filename(), "/bin/ls")


	def test_layout(self):
		"FileEntry is HBox with Entry and Button"

		e = ui.FileEntry()
		self.assertEquals(isinstance(e, ui.HBox), True)
		self.assertEquals(len(e.get_children()), 2)
		self.assertEquals(e.get_children()[0] is e.entry, True)
		self.assertEquals(e.get_children()[1] is e.button, True)


	def test_title(self):
		"FileEntry takes file selector title as argument"

		self.assertEquals(ui.FileEntry("test").title, "test")



class FileEntry_get_filename(unittest.TestCase):
	"FileEntry.get_filename()"

	def test_filename(self):
		"FileEntry.get_filename() returns entry contents"

		e = ui.FileEntry(None, "/bin/ls")
		self.assertEquals(e.get_filename(), "/bin/ls")



class FileEntry_get_text(unittest.TestCase):
	"FileEntry.get_text()"

	def test_filename(self):
		"FileEntry.get_text() returns entry contents"

		e = ui.FileEntry(None, "/bin/ls")
		self.assertEquals(e.get_text(), "/bin/ls")



class FileEntry_set_filename(unittest.TestCase):
	"FileEntry.set_filename()"

	def test_filename(self):
		"FileEntry.set_filename() sets filename in entry"

		e = ui.FileEntry()
		e.set_filename("/bin/ls")
		self.assertEquals(e.get_filename(), "/bin/ls")


	def test_normpath(self):
		"FileEntry.set_filename() applies io.file_normpath()"

		e = ui.FileEntry()
		e.set_filename("/home/../bin/./ls")
		self.assertEquals(e.get_filename(), "/bin/ls")



class FileEntry_set_text(unittest.TestCase):
	"FileEntry.set_text()"

	def test_text(self):
		"FileEntry.set_text() sets text in entry"

		e = ui.FileEntry()
		e.set_text("test")
		self.assertEquals(e.get_text(), "test")



class HBox(unittest.TestCase):
	"HBox"

	def test_children(self):
		"HBox accepts children as arguments"

		hbox = ui.HBox(ui.Label("a"), ui.Label("b"), ui.Label("c"))

		self.assertEquals(len(hbox.get_children()), 3)
		self.assertEquals(hbox.get_children()[0].get_text(), "a")
		self.assertEquals(hbox.get_children()[1].get_text(), "b")
		self.assertEquals(hbox.get_children()[2].get_text(), "c")


	def test_hig(self):
		"HBox conforms to the HIG"

		hbox = ui.HBox()
		self.assertEquals(hbox.get_spacing(), 6)
		self.assertEquals(hbox.get_border_width(), 0)


	def test_parent(self):
		"HBox is subclass of gtk.HBox"

		self.assertEquals(isinstance(ui.HBox(), gtk.HBox), True)



class HPaned(unittest.TestCase):
	"HPaned"

	def test_children(self):
		"HPaned accepts children as arguments"

		hpaned = ui.HPaned(ui.Label("a"), ui.Label("b"))

		self.assertEquals(hpaned.get_child1().get_text(), "a")
		self.assertEquals(hpaned.get_child2().get_text(), "b")


	def test_subclass(self):
		"HPaned is subclass of gtk.HPaned"

		self.assertEquals(isinstance(ui.HPaned(), gtk.HPaned), True)



class ItemFactory(unittest.TestCase):
	"ItemFactory"

	def test_icondir(self):
		"ItemFactory puts icondir in search path"

		self.assertEquals(config.DIR_ICONS in ui.ItemFactory(gtk.Window()).theme.get_search_path(), True)


	def test_icons(self):
		"ItemFactory registers icons on init"

		f = ui.ItemFactory(gtk.Window())
		gtk_run()

		for stock in (
			ui.STOCK_ENTRY_FOLDER,
			ui.STOCK_ENTRY_FOLDER_OPEN,
			ui.STOCK_ENTRY_CREDITCARD,
			ui.STOCK_ENTRY_CRYPTOKEY,
			ui.STOCK_ENTRY_DATABASE,
			ui.STOCK_ENTRY_DOOR,
			ui.STOCK_ENTRY_EMAIL,
			ui.STOCK_ENTRY_FTP,
			ui.STOCK_ENTRY_GENERIC,
			ui.STOCK_ENTRY_PHONE,
			ui.STOCK_ENTRY_SHELL,
			ui.STOCK_ENTRY_WEBSITE,
			ui.STOCK_REVELATION
		):
			self.assertEquals(stock in gtk.stock_list_ids(), True)



	def test_subclass(self):
		"ItemFactory is subclass of gtk.IconFactory"

		self.assertEquals(isinstance(ui.ItemFactory(gtk.Window()), gtk.IconFactory), True)



class ItemFactory_create_stock_item(unittest.TestCase):
	"ItemFactory.create_stock_item()"

	def test_create(self):
		"ItemFactory.create_stock_item() creates stock item"

		f = ui.ItemFactory(gtk.Window())
		f.create_stock_item("test123", "Just a test", gtk.STOCK_ADD)

		self.assertEquals("test123" in gtk.stock_list_ids(), True)


	def test_data(self):
		"ItemFactory.create_stock_item() stores all data for item"

		f = ui.ItemFactory(gtk.Window())
		f.create_stock_item("test", "Just a test", gtk.STOCK_ADD)

		stock = gtk.stock_lookup("test")

		self.assertNotEqual(stock, None)
		self.assertEquals(stock[0], "test")
		self.assertEquals(stock[1], "Just a test")



class ItemFactory_load_icon(unittest.TestCase):
	"ItemFactory.load_icon()"

	def test_load(self):
		"ItemFactory.load_icon() loads stock icon"

		f = ui.ItemFactory(gtk.Window())
		icon = f.load_icon("stock_people", gtk.ICON_SIZE_MENU)

		self.assertEquals(type(icon), gtk.gdk.Pixbuf)



class ItemFactory_load_stock_icon(unittest.TestCase):
	"ItemFactory.load_stock_icon()"

	def test_load(self):
		"ItemFactory.load_stock_icon() loads and registers icon"

		f = ui.ItemFactory(gtk.Window())
		f.load_stock_icon("nicestock", "stock_example", ( gtk.ICON_SIZE_MENU, gtk.ICON_SIZE_LARGE_TOOLBAR ))

		self.assertEquals("nicestock" in gtk.stock_list_ids(), True)



class Image(unittest.TestCase):
	"Image"

	def test_stock(self):
		"Image takes stock and size as arguments"

		image = ui.Image(ui.STOCK_REVELATION, ui.ICON_SIZE_LOGO)
		self.assertEquals(image.get_stock(), ( ui.STOCK_REVELATION, ui.ICON_SIZE_LOGO ))


	def test_subclass(self):
		"Image is subclass of gtk.Image"

		self.assertEquals(isinstance(ui.Image(), gtk.Image), True)



class ImageLabel(unittest.TestCase):
	"ImageLabel"

	def setUp(self):
		"sets up common facilities"

		self.imagelabel = ui.ImageLabel("Test", ui.STOCK_REVELATION, ui.ICON_SIZE_LOGO)


	def test_hig(self):
		"ImageLabel conforms to the HIG"

		self.assertEquals(self.imagelabel.hbox.get_spacing(), 6)


	def test_image(self):
		"ImageLabel sets image correctly"

		self.assertEquals(self.imagelabel.image.get_stock(), ( ui.STOCK_REVELATION, ui.ICON_SIZE_LOGO ))


	def test_label(self):
		"ImageLabel sets label correctly"

		self.assertEquals(self.imagelabel.label.get_text(), "Test")



class ImageLabel_set_stock(unittest.TestCase):
	"ImageLabel.set_stock()"

	def test_stock(self):
		"ImageLabel.set_stock() sets image correctly"

		imagelabel = ui.ImageLabel("Test", ui.STOCK_REVELATION, ui.ICON_SIZE_LOGO)

		imagelabel.set_stock(ui.STOCK_ENTRY_FOLDER, ui.ICON_SIZE_DATAVIEW)
		self.assertEquals(imagelabel.image.get_stock(), ( ui.STOCK_ENTRY_FOLDER, ui.ICON_SIZE_DATAVIEW ))



class ImageLabel_set_text(unittest.TestCase):
	"ImageLabel.set_text()"

	def test_text(self):
		"ImageLabel.set_text() sets text correctly"

		imagelabel = ui.ImageLabel("Test", ui.STOCK_REVELATION, ui.ICON_SIZE_LOGO)

		imagelabel.set_text("test123")
		self.assertEquals(imagelabel.label.get_text(), "test123")



class ImageMenuItem(unittest.TestCase):
	"ImageMenuItem"

	def test_image(self):
		"ImageMenuItem makes image available as image attribute"

		i = ui.ImageMenuItem(gtk.STOCK_ADD, "test")
		self.assertEquals(isinstance(i.image, gtk.Image), True)
		self.assertEquals(i.image is i.get_children()[1], True)


	def test_label(self):
		"ImageMenuItem makes label available as label attribute"

		i = ui.ImageMenuItem(gtk.STOCK_ADD, "test")
		self.assertEquals(isinstance(i.label, gtk.Label), True)
		self.assertEquals(i.label is i.get_children()[0], True)


	def test_stock(self):
		"ImageMenuItem sets image stock from arg"

		i = ui.ImageMenuItem(gtk.STOCK_ADD)
		self.assertEquals(i.image.get_stock(), ( gtk.STOCK_ADD, gtk.ICON_SIZE_MENU ))


	def test_subclass(self):
		"ImageMenuItem is subclass of gtk.ImageMenuItem"

		self.assertEquals(isinstance(ui.ImageMenuItem(gtk.STOCK_ADD), gtk.ImageMenuItem), True)


	def test_text(self):
		"ImageMenuItem sets label text from arg"

		i = ui.ImageMenuItem(gtk.STOCK_ADD, "test")
		self.assertEquals(i.label.get_text(), "test")



class ImageMenuItem_set_stock(unittest.TestCase):
	"ImageMenuItem.set_stock()"

	def test_stock(self):
		"ImageMenuItem.set_stock() sets the stock image"

		i = ui.ImageMenuItem(gtk.STOCK_ADD)
		i.set_stock(gtk.STOCK_REMOVE)
		self.assertEquals(i.image.get_stock(), ( gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU ))



class ImageMenuItem_set_text(unittest.TestCase):
	"ImageMenuItem.set_text()"

	def test_text(self):
		"ImageMenuItem.set_text() sets label text"

		i = ui.ImageMenuItem(gtk.STOCK_ADD)
		i.set_text("test123")
		self.assertEquals(i.label.get_text(), "test123")



class InputSection(unittest.TestCase):
	"InputSection"

	def test_description(self):
		"InputSection creates description label correctly"

		sect = ui.InputSection("Title", "Description")
		self.assertEquals(len(sect.get_children()), 2)
		self.assertEquals(type(sect.get_children()[1]), ui.Label)
		self.assertEquals(sect.get_children()[1].get_text(), "Description")


	def test_hig(self):
		"InputSection conforms to the HIG"

		sect = ui.InputSection()
		self.assertEquals(sect.get_spacing(), 6)


	def test_sizegroup(self):
		"InputSection uses sizegroup correctly"

		sizegroup = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		sect = ui.InputSection("Title", "Description", sizegroup)
		self.assertEquals(sect.sizegroup is sizegroup, True)


	def test_sizegroup_default(self):
		"InputSection sets up horizontal sizegroup by default"

		sect = ui.InputSection()
		self.assertEquals(type(sect.sizegroup), gtk.SizeGroup)
		self.assertEquals(sect.sizegroup.get_mode(), gtk.SIZE_GROUP_HORIZONTAL)


	def test_subclass(self):
		"InputSection is subclass of gtk.VBox"

		self.assertEquals(isinstance(ui.InputSection(), gtk.VBox), True)


	def test_title(self):
		"InputSection creates title label correctly"

		sect = ui.InputSection("Title")
		self.assertEquals(len(sect.get_children()), 1)
		self.assertEquals(type(sect.get_children()[0]), ui.Label)
		self.assertEquals(sect.get_children()[0].get_text(), "Title")



class InputSection_append_widget(unittest.TestCase):
	"InputSection.append_widget()"

	def test_hig(self):
		"InputSection.append_widget() conforms to the HIG"

		sect = ui.InputSection()
		sect.append_widget("Test", ui.Entry())

		row = sect.get_children()[0]
		self.assertEquals(row.get_spacing(), 12)
		self.assertEquals(row.get_children()[0].get_text(), "Test:")


	def test_label_none(self):
		"InputSection.append_widget() expands widget to max width on None label"

		sect = ui.InputSection()
		entry = ui.Entry()
		sect.append_widget(None, entry)

		row = sect.get_children()[0]
		self.assertEquals(len(row.get_children()), 1)
		self.assertEquals(row.get_children()[0] is entry, True)


	def test_pair(self):
		"InputSection.append_widget() generates a label/widget pair"

		sect = ui.InputSection()
		entry = ui.Entry()
		sect.append_widget("Test", entry)

		row = sect.get_children()[0]
		self.assertEquals(type(row.get_children()[0]), ui.Label)
		self.assertEquals(row.get_children()[0].get_text(), "Test:")

		self.assertEquals(row.get_children()[1] is entry, True)



class InputSection_clear(unittest.TestCase):
	"InputSection.clear()"

	def test_clear(self):
		"InputSection.clear() clears the section"

		sect = ui.InputSection()
		sect.append_widget("Test", ui.Entry())
		sect.append_widget("Test2", ui.Entry())
		self.assertEquals(len(sect.get_children()), 2)

		sect.clear()
		self.assertEquals(len(sect.get_children()), 0)


	def test_title_description(self):
		"InputSection.clear() preserves title and description labels"

		sect = ui.InputSection("Title", "Description")
		sect.append_widget("Test", ui.Entry())
		sect.append_widget("Test2", ui.Entry())
		self.assertEquals(len(sect.get_children()), 4)

		sect.clear()
		self.assertEquals(len(sect.get_children()), 2)
		self.assertEquals(sect.get_children()[0].get_text(), "Title")
		self.assertEquals(sect.get_children()[1].get_text(), "Description")



class Label(unittest.TestCase):
	"Label"

	def test_subclass(self):
		"Label is subclass of gtk.Label"

		self.assertEquals(isinstance(ui.Label(), gtk.Label), True)


	def test_justify(self):
		"Label sets justify from args"

		self.assertEquals(ui.Label("Test", gtk.JUSTIFY_LEFT).get_justify(), gtk.JUSTIFY_LEFT)
		self.assertEquals(ui.Label("Test", gtk.JUSTIFY_CENTER).get_justify(), gtk.JUSTIFY_CENTER)
		self.assertEquals(ui.Label("Test", gtk.JUSTIFY_RIGHT).get_justify(), gtk.JUSTIFY_RIGHT)


	def test_justify_alignment(self):
		"Label justify argument affects label alignment as well"

		self.assertEquals(ui.Label("Test", gtk.JUSTIFY_LEFT).get_alignment()[0], 0)
		self.assertEquals(ui.Label("Test", gtk.JUSTIFY_CENTER).get_alignment()[0], 0.5)
		self.assertEquals(ui.Label("Test", gtk.JUSTIFY_RIGHT).get_alignment()[0], 1)


	def test_line_wrap(self):
		"Label enables line-wrapping by default"

		self.assertEquals(ui.Label().get_line_wrap(), True)


	def test_markup(self):
		"Label enables markup by default"

		self.assertEquals(ui.Label().get_use_markup(), True)
		self.assertEquals(ui.Label("<span weight=\"bold\">Test</span>").get_text(), "Test")


	def test_text(self):
		"Label sets text correctly from args"

		self.assertEquals(ui.Label("Test").get_text(), "Test")


	def test_text_none(self):
		"Label has no text when given None as text"

		self.assertEquals(ui.Label(None).get_text(), "")



class Label_set_text(unittest.TestCase):
	"Label.set_text()"

	def test_markup(self):
		"Label.set_text() handles markup"

		label = ui.Label()
		label.set_text("<span weight=\"bold\">test</span>")
		self.assertEquals(label.get_text(), "test")


	def test_none(self):
		"Label.set_text() clears label contents when given None"

		label = ui.Label("Test")
		label.set_text(None)
		self.assertEquals(label.get_text(), "")


	def test_text(self):
		"Label.set_text() sets text correctly"

		label = ui.Label("Test")
		label.set_text("test123")
		self.assertEquals(label.get_text(), "test123")



class Notebook(unittest.TestCase):
	"Notebook"

	def test_subclass(self):
		"Notebook is subclass of gtk.Notebook"

		self.assertEquals(isinstance(ui.Notebook(), gtk.Notebook), True)



class Notebook_create_page(unittest.TestCase):
	"Notebook.create_page()"

	def test_create(self):
		"Notebook.create_page() creates a notebook page"

		notebook = ui.Notebook()
		notebook.create_page("test1")
		notebook.create_page("test2")

		self.assertEquals(notebook.get_n_pages(), 2)


	def test_label(self):
		"Notebook.create_page() creates a tab label for the page"

		notebook = ui.Notebook()
		page = notebook.create_page("test")
		self.assertEquals(notebook.get_tab_label(page).get_text(), "test")


	def test_return(self):
		"Notebook.create_page() returns the created page"

		notebook = ui.Notebook()
		page = notebook.create_page("test")

		self.assertEquals(type(page), ui.NotebookPage)



class NotebookPage(unittest.TestCase):
	"NotebookPage"

	def test_hig(self):
		"NotebookPage conforms to the HIG"

		page = ui.NotebookPage()
		self.assertEquals(page.get_spacing(), 18)
		self.assertEquals(page.get_border_width(), 12)


	def test_subclass(self):
		"NotebookPage is subclass of ui.VBox"

		self.assertEquals(isinstance(ui.NotebookPage(), ui.VBox), True)



class NotebookPage_add_section(unittest.TestCase):
	"NotebookPage.add_section()"

	def test_create(self):
		"NotebookPage.add_section() adds an InputSection"

		page = ui.NotebookPage()
		page.add_section("Test")

		self.assertEquals(len(page.get_children()), 1)
		self.assertEquals(type(page.get_children()[0]), ui.InputSection)


	def test_return(self):
		"NotebookPage.add_section() returns InputSection"

		page = ui.NotebookPage()
		section = page.add_section("Test")

		self.assertEquals(type(section), ui.InputSection)
		self.assertEquals(section is page.get_children()[0], True)


	def test_sizegroup(self):
		"NotebookPage.add_section() uses common sizegroup for all sections"

		page = ui.NotebookPage()
		sect1 = page.add_section("Test1")
		sect2 = page.add_section("Test2")

		self.assertEquals(sect1.sizegroup is page.sizegroup, True)
		self.assertEquals(sect2.sizegroup is page.sizegroup, True)



class PasswordEntry(unittest.TestCase):
	"PasswordEntry"

	def test_config(self):
		"PasswordEntry sets visibility based on config value"

		c = config.Config()
		c.set("view/passwords", False)

		e = ui.PasswordEntry(c)
		gtk_run()
		self.assertEquals(e.get_visibility(), False)

		c.set("view/passwords", True)
		gtk_run()
		self.assertEquals(e.get_visibility(), True)


	def test_config_none(self):
		"PasswordEntry accepts None as config"

		ui.PasswordEntry(None)


	def test_password(self):
		"PasswordEntry takes password as arg"

		self.assertEquals(ui.PasswordEntry(None, "test123").get_text(), "test123")


	def test_subclass(self):
		"PasswordEntry is subclass of Entry"

		self.assertEquals(isinstance(ui.PasswordEntry(), ui.Entry), True)



class PasswordEntryGenerate(unittest.TestCase):
	"PasswordEntryGenerate"

	def test_button(self):
		"PasswordEntryGenerate has button attribute"

		self.assertEquals(isinstance(ui.PasswordEntryGenerate(config.Config()).button, ui.Button), True)


	def test_entry(self):
		"PasswordEntryGenerate has child PasswordEntry as entry attribute"

		self.assertEquals(isinstance(ui.PasswordEntryGenerate(config.Config()).entry, ui.PasswordEntry), True)


	def test_generate(self):
		"PasswordEntryGenerate generates password on button click"

		e = ui.PasswordEntryGenerate(config.Config())
		e.button.clicked()
		gtk_run()
		self.assertNotEqual(e.entry.get_text(), "")


	def test_layout(self):
		"PasswordEntryGenerate has entry and button as children"

		e = ui.PasswordEntryGenerate(config.Config())
		self.assertEquals(len(e.get_children()), 2)
		self.assertEquals(e.get_children()[0] is e.entry, True)
		self.assertEquals(e.get_children()[1] is e.button, True)


	def test_password(self):
		"PasswordEntryGenerate takes password as arg"

		self.assertEquals(ui.PasswordEntryGenerate(config.Config(), "test123").entry.get_text(), "test123")



class PasswordEntryGenerate_generate(unittest.TestCase):
	"PasswordEntryGenerate.generate()"

	def test_generate(self):
		"PasswordEntryGenerate.generates() generates password in entry"

		e = ui.PasswordEntryGenerate(config.Config())
		e.generate()
		self.assertNotEqual(e.entry.get_text(), "")



class PasswordEntryGenerate_get_text(unittest.TestCase):
	"PasswordEntryGenerate.get_text()"

	def test_text(self):
		"PasswordEntryGenerate.get_text() returns entry contents"

		self.assertEquals(ui.PasswordEntryGenerate(config.Config(), "test123").get_text(), "test123")



class PasswordEntryGenerate_set_text(unittest.TestCase):
	"PasswordEntryGenerate.set_text()"

	def test_text(self):
		"PasswordEntryGenerate.set_text() sets entry contents"

		e = ui.PasswordEntryGenerate(config.Config())
		e.set_text("test123")
		self.assertEquals(e.get_text(), "test123")



class PasswordLabel(unittest.TestCase):
	"PasswordLabel"

	def test_config(self):
		"PasswordLabel follows the view/passwords setting"

		c = config.Config()
		c.set("view/passwords", True)
		gtk_run()

		label = ui.PasswordLabel("Test123", c)
		self.assertEquals(label.get_text(), "Test123")

		c.set("view/passwords", False)
		gtk_run()
		self.assertEquals(label.get_text(), "******")

		keep_timeout = False
		gtk_run()


	def test_password(self):
		"PasswordLabel sets password from password arg"

		label = ui.PasswordLabel("test123")
		self.assertEquals(label.get_text(), "test123")
		self.assertEquals(label.password, "test123")


	def test_selectable(self):
		"PasswordLabel has selectable text"

		self.assertEquals(ui.PasswordLabel("test").get_selectable(), True)


	def test_subclass(self):
		"PasswordLabel is subclass of Label"

		self.assertEquals(isinstance(ui.PasswordLabel(), ui.Label), True)



class PasswordLabel_show_password(unittest.TestCase):
	"PasswordLabel.show_password()"

	def test_show(self):
		"PasswordLabel.show_password() works as expected"

		label = ui.PasswordLabel("test123")

		label.show_password(True)
		self.assertEquals(label.get_text(), "test123")

		label.show_password(False)
		self.assertEquals(label.get_text(), "******")



class ScrolledWindow(unittest.TestCase):
	"ScrolledWindow"

	def test_content(self):
		"ScrolledWindow sets contents from argument"

		tree = ui.TreeView(gtk.TreeStore(str))
		s = ui.ScrolledWindow(tree)

		self.assertEquals(s.get_child() is tree, True)


	def test_policy(self):
		"ScrolledWindow uses automatic scrollbar display by default"

		s = ui.ScrolledWindow()
		self.assertEquals(s.get_policy(), ( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC ))


	def test_subclass(self):
		"ScrolledWindow is subclass of gtk.ScrolledWindow"

		self.assertEquals(isinstance(ui.ScrolledWindow(), gtk.ScrolledWindow), True)



class Searchbar(unittest.TestCase):
	"Searchbar"

	def test_subclass(self):
		"Searchbar is subclass of gtk.Toolbar"

		self.assertEquals(isinstance(ui.Searchbar(), gtk.Toolbar), True)



class SpinEntry(unittest.TestCase):
	"SpinEntry"

	def test_increments(self):
		"SpinEntry uses 1 and 5 as increments"

		self.assertEquals(ui.SpinEntry().get_increments(), (1, 5))


	def test_numeric(self):
		"SpinEntry is numeric only"

		self.assertEquals(ui.SpinEntry().get_numeric(), True)


	def test_subclass(self):
		"SpinEntry is subclass of gtk.SpinButton"

		self.assertEquals(isinstance(ui.SpinEntry(), gtk.SpinButton), True)



class Statusbar(unittest.TestCase):
	"Statusbar"

	def test_subclass(self):
		"Statusbar is subclasss of gtk.Statusbar"

		self.assertEquals(isinstance(ui.Statusbar(), gtk.Statusbar), True)



class Statusbar_clear(unittest.TestCase):
	"Statusbar.clear()"

	def test_clear(self):
		"Statusbar.clear() clears the statusbar"

		s = ui.Statusbar()
		s.set_status("test123")
		s.set_status("test")
		s.clear()
		self.assertEquals(s.get_children()[0].get_children()[0].get_text(), "")



class Statusbar_set_text(unittest.TestCase):
	"Statusbar.set_text()"

	def test_text(self):
		"Statusbar.set_text() sets the statusbar text"

		s = ui.Statusbar()
		s.set_status("test123")
		self.assertEquals(s.get_children()[0].get_children()[0].get_text(), "test123")



class TextView(unittest.TestCase):
	"TextView"

	def test_buffer(self):
		"TextView takes buffer as argument"

		buffer = gtk.TextBuffer()
		buffer.set_text("test123")
		self.assertEquals(ui.TextView(buffer).get_buffer() is buffer, True)


	def test_cursor(self):
		"TextView has hidden cursor by default"

		self.assertEquals(ui.TextView().get_cursor_visible(), False)


	def test_editable(self):
		"TextView is not editable by default"

		self.assertEquals(ui.TextView().get_editable(), False)


	def test_font(self):
		"TextView uses Monospace font by default"

		# TODO fix this
		#self.assertEquals(ui.TextView().get_pango_context().get_font_description().get_family(), "Monospace")
		pass


	def test_subclass(self):
		"TextView is subclass of gtk.TextView"

		self.assertEquals(isinstance(ui.TextView(), gtk.TextView), True)


	def test_text(self):
		"TextView takes text contents as argument"

		t = ui.TextView(None, "test123")
		b = t.get_buffer()
		self.assertEquals(b.get_text(b.get_start_iter(), b.get_end_iter()), "test123")


	def test_wrap(self):
		"TextView doesn't wrap by default"

		self.assertEquals(ui.TextView().get_wrap_mode(), gtk.WRAP_NONE)



# TODO fix tests for internal callbacks (keyboard handling, drag/drop etc)
class TreeView(unittest.TestCase):
	"TreeView"

	def test_headers_visible(self):
		"TreeView disables tree headers by default"

		self.assertEquals(ui.TreeView(data.EntryStore()).get_headers_visible(), False)


	def test_selection(self):
		"TreeView makes selection available through selection attribute"

		t = ui.TreeView(data.EntryStore())
		self.assertEquals(t.selection is t.get_selection(), True)


	def test_subclass(self):
		"TreeView is subclass of gtk.TreeView"

		self.assertEquals(isinstance(ui.TreeView(data.EntryStore()), gtk.TreeView), True)



class TreeView_collapse_row(unittest.TestCase):
	"TreeView.collapse_row()"

	def test_collapse(self):
		"TreeView.collapse_row() collapses row"

		e = data.EntryStore()
		fiter = e.add_entry(entry.FolderEntry())
		iter = e.add_entry(entry.GenericEntry(), fiter)

		t = ui.TreeView(e)
		t.expand_row(fiter)
		t.collapse_row(fiter)

		self.assertEquals(t.row_expanded(( 0, )), False)


	def test_iter(self):
		"TreeView.collapse_row() takes iter instead of path"

		e = data.EntryStore()
		iter = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.collapse_row(iter)
		self.assertRaises(TypeError, t.collapse_row, ( 0, ))



class TreeView_expand_row(unittest.TestCase):
	"TreeView.expand_row()"

	def test_expand(self):
		"TreeView.expand_row() expands row"

		e = data.EntryStore()
		fiter = e.add_entry(entry.FolderEntry())
		iter = e.add_entry(entry.GenericEntry(), fiter)

		t = ui.TreeView(e)
		t.expand_row(fiter)

		self.assertEquals(t.row_expanded(( 0, )), True)


	def test_iter(self):
		"TreeView.expand_row() takes iter instead of path"

		e = data.EntryStore()
		iter = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.expand_row(iter)
		self.assertRaises(TypeError, t.collapse_row, ( 0, ))



class TreeView_expand_to_iter(unittest.TestCase):
	"TreeView.expand_to_iter()"

	def test_ancestors(self):
		"TreeView.expand_to_iter() expands all ancestor"

		e = data.EntryStore()
		piter1 = e.add_entry(entry.FolderEntry())
		piter2 = e.add_entry(entry.FolderEntry(), piter1)
		piter3 = e.add_entry(entry.FolderEntry(), piter2)
		piter4 = e.add_entry(entry.FolderEntry(), piter3)
		iter = e.add_entry(entry.GenericEntry(), piter4)

		t = ui.TreeView(e)
		t.expand_to_iter(iter)

		for i in ( piter1, piter2, piter3, piter4 ):
			self.assertEquals(t.row_expanded(e.get_path(i)), True)

	def test_no_expand(self):
		"TreeView.expand_to_iter() doesn't expand the given iter"

		e = data.EntryStore()
		piter1 = e.add_entry(entry.FolderEntry())
		piter2 = e.add_entry(entry.FolderEntry(), piter1)
		iter = e.add_entry(entry.GenericEntry(), piter2)

		t = ui.TreeView(e)
		t.expand_to_iter(piter2)

		self.assertEquals(t.row_expanded(e.get_path(piter2)), False)



class TreeView_get_active(unittest.TestCase):
	"TreeView.get_active()"

	def test_cursor(self):
		"TreeView.get_active() returns the current cursor"

		e = data.EntryStore()
		iter1 = e.add_entry(entry.GenericEntry())
		iter2 = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.set_cursor(e.get_path(iter2))

		self.assertEquals(e.get_path(t.get_active()), t.get_cursor()[0])

	def test_selected(self):
		"TreeView.get_active() only returns cursor if selected"

		e = data.EntryStore()
		iter1 = e.add_entry(entry.GenericEntry())
		iter2 = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.set_cursor(e.get_path(iter2))
		t.selection.unselect_iter(iter2)

		self.assertEquals(t.get_active(), None)


class TreeView_get_selected(unittest.TestCase):
	"TreeView.get_selected()"

	def test_selected(self):
		"TreeView.get_selected() returns list of selected iters"

		e = data.EntryStore()
		iters = []

		iters.append(e.add_entry(entry.GenericEntry()))
		iters.append(e.add_entry(entry.GenericEntry()))
		iters.append(e.add_entry(entry.GenericEntry()))
		iters.append(e.add_entry(entry.GenericEntry()))

		t = ui.TreeView(e)
		t.selection.select_iter(iters[0])
		t.selection.select_iter(iters[2])
		t.selection.select_iter(iters[3])

		selected = t.get_selected()

		self.assertEquals(e.get_path(iters[0]), e.get_path(selected[0]))
		self.assertEquals(e.get_path(iters[2]), e.get_path(selected[1]))
		self.assertEquals(e.get_path(iters[3]), e.get_path(selected[2]))



class TreeView_select(unittest.TestCase):
	"TreeView.select()"

	def test_cursor(self):
		"TreeView.select() sets the cursor to the row"

		e = data.EntryStore()
		iter1 = e.add_entry(entry.GenericEntry())
		iter2 = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.select(iter2)

		self.assertEquals(t.get_cursor()[0], e.get_path(iter2))


	def test_expand(self):
		"TreeView.select() expands all ancestors"

		e = data.EntryStore()
		fiter1 = e.add_entry(entry.FolderEntry())
		fiter2 = e.add_entry(entry.FolderEntry(), fiter1)
		iter = e.add_entry(entry.GenericEntry(), fiter2)

		t = ui.TreeView(e)
		t.select(iter)

		self.assertEquals(t.row_expanded(e.get_path(fiter1)), True)
		self.assertEquals(t.row_expanded(e.get_path(fiter2)), True)


	def test_select(self):
		"TreeView.select() unselects all on None"

		e = data.EntryStore()
		iter1 = e.add_entry(entry.GenericEntry())
		iter2 = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.select(iter2)

		self.assertEquals(t.selection.iter_is_selected(iter1), False)
		self.assertEquals(t.selection.iter_is_selected(iter2), True)

		t.select(None)
		self.assertEquals(t.get_selected(), [])
		self.assertEquals(t.get_active(), None)


	def test_select(self):
		"TreeView.select() selects the row"

		e = data.EntryStore()
		iter1 = e.add_entry(entry.GenericEntry())
		iter2 = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)
		t.select(iter2)

		self.assertEquals(t.selection.iter_is_selected(iter1), False)
		self.assertEquals(t.selection.iter_is_selected(iter2), True)



class TreeView_set_model(unittest.TestCase):
	"TreeView.set_model()"

	def test_attr(self):
		"TreeView.set_model() sets the .model attribute"

		e = data.EntryStore()
		t = ui.TreeView(e)

		e2 = data.EntryStore()
		t.set_model(e2)

		self.assertEquals(t.model is e, False)
		self.assertEquals(t.model is e2, True)



class TreeView_toggle_expanded(unittest.TestCase):
	"TreeView.toggle_expanded()"

	def test_collapse(self):
		"TreeView.toggle_expanded() collapses expanded rows"

		e = data.EntryStore()
		fiter = e.add_entry(entry.FolderEntry())
		iter = e.add_entry(entry.GenericEntry(), fiter)

		t = ui.TreeView(e)
		t.expand_row(fiter)

		self.assertEquals(t.row_expanded(e.get_path(fiter)), True)
		t.toggle_expanded(fiter)
		self.assertEquals(t.row_expanded(e.get_path(fiter)), False)


	def test_expand(self):
		"TreeView.toggle_expanded() expands collapsed rows"

		e = data.EntryStore()
		fiter = e.add_entry(entry.FolderEntry())
		iter = e.add_entry(entry.GenericEntry(), fiter)

		t = ui.TreeView(e)

		self.assertEquals(t.row_expanded(e.get_path(fiter)), False)
		t.toggle_expanded(fiter)
		self.assertEquals(t.row_expanded(e.get_path(fiter)), True)


class TreeView_unselect_all(unittest.TestCase):
	"TreeView.unselect_all()"

	def test_unselect(self):
		"TreeView.unselect_all() unselects all rows"

		e = data.EntryStore()
		iter1 = e.add_entry(entry.GenericEntry())
		iter2 = e.add_entry(entry.GenericEntry())

		t = ui.TreeView(e)

		t.select(iter2)
		self.assertEquals(len(t.get_selected()), 1)

		t.unselect_all()
		self.assertEquals(t.get_selected(), [])



class Toolbar(unittest.TestCase):
	"Toolbar"

	def test_subclass(self):
		"Toolbar is subclass of gtk.Toolbar"

		self.assertEquals(isinstance(ui.Toolbar(), gtk.Toolbar), True)



class Toolbar_append_widget(unittest.TestCase):
	"Toolbar.append_widget()"

	def test_append(self):
		"Toolbar.append_widget() appends a widget"

		label = ui.Label("test")
		toolbar = ui.Toolbar()
		toolbar.append_widget(label)

		self.assertEquals(len(toolbar.get_children()), 1)
		self.assertEquals(toolbar.get_children()[0].get_child() is label, True)



class UIManager(unittest.TestCase):
	"UIManager"

	def test_subclass(self):
		"UIManager is subclass of gtk.UIManager"

		self.assertEquals(isinstance(ui.UIManager(), gtk.UIManager), True)



class UIManager_add_actions_from_file(unittest.TestCase):
	"UIManager.add_actions_from_file()"

	def test_ioerror(self):
		"UIManager.add_actions_from_file() raises IOError on file error"

		self.assertRaises(IOError, ui.UIManager().add_actions_from_file, "/dummyfile123")



class UIManager_add_actions_from_string(unittest.TestCase):
	"UIManager.add_actions_from_string()"

	def test_action(self):
		"UIManager.add_actions_from_string() creates action correctly"

		mgr = ui.UIManager()

		mgr.add_actions_from_string("""
<?xml version=\"1.0\" ?>
<actions>
	<actiongroup name=\"testgroup\">
		<action>
			<name>test</name>
			<label>Just a test</label>
			<stock>gtk-ok</stock>
			<accel>&lt;Control&gt;O</accel>
			<description>Test-description</description>
		</action>
	</actiongroup>
</actions>
""")

		action = mgr.get_action("test")

		self.assertEquals(action.get_property("name"), "test")
		self.assertEquals(action.get_property("label"), "Just a test")
		self.assertEquals(action.get_property("stock-id"), "gtk-ok")
		self.assertEquals(action.get_property("tooltip"), "Test-description")
		self.assertEquals(action.get_property("action-group").get_name(), "testgroup")


	def test_actiongroup(self):
		"UIManager.add_actions_from_string() creates action groups"

		mgr = ui.UIManager()

		mgr.add_actions_from_string("""
<?xml version=\"1.0\" ?>
<actions>
	<actiongroup name=\"testgroup\">
		<action>
			<name>test</name>
			<label>Just a test</label>
			<stock>gtk-ok</stock>
			<accel>&lt;Control&gt;O</accel>
			<description>Test-description</description>
		</action>
	</actiongroup>
</actions>
""")

		actiongroup = mgr.get_action_group("testgroup")
		self.assertEquals(isinstance(actiongroup, gtk.ActionGroup), True)


	def test_invalid(self):
		"UIManager.add_actions_from_string() raises DataError on invalid data"

		xml = """
<?xml version="1.0" ?>
<actions>
	<dummy></dummy>
</action>
"""

		self.assertRaises(ui.DataError, ui.UIManager().add_actions_from_string, xml)


	def test_optional(self):
		"UIManager.add_actions_from_string() uses optional action elements"

		mgr = ui.UIManager()

		mgr.add_actions_from_string("""
<?xml version=\"1.0\" ?>
<actions>
	<actiongroup name=\"testgroup\">
		<action>
			<name>test</name>
		</action>
	</actiongroup>
</actions>
""")

		action = mgr.get_action("test")

		self.assertEquals(action.get_property("name"), "test")
		self.assertEquals(action.get_property("label"), "")
		self.assertEquals(action.get_property("stock-id"), "")
		self.assertEquals(action.get_property("tooltip"), "")
		self.assertEquals(action.get_property("action-group").get_name(), "testgroup")



class UIManager_add_ui_from_file(unittest.TestCase):
	"UIManager.add_ui_from_file()"

	def test_ioerror(self):
		"UIManager.add_ui_from_file() raises IOError on file error"

		self.assertRaises(IOError, ui.UIManager().add_ui_from_file, "/dummyfile123")



class UIManager_append_action_group(unittest.TestCase):
	"UIManager.append_action_group()"

	def test_append(self):
		"UIManager.append_action_group() appends action group"

		mgr = ui.UIManager()
		mgr.add_actions_from_string("""
<?xml version="1.0" ?>
<actions>
	<actiongroup name="testa" />
	<actiongroup name="testb" />
</actions>
		""")

		group = gtk.ActionGroup("testc")
		mgr.append_action_group(group)

		self.assertEquals(mgr.get_action_group("testc") is group, True)
		self.assertEquals(mgr.get_action_groups()[2], group)



class UIManager_get_action(unittest.TestCase):
	"UIManager.get_action()"

	def test_action(self):
		"UIManager.get_action() looks up action"

		mgr = ui.UIManager()
		mgr.add_actions_from_string("""
<?xml version="1.0" ?>
<actions>
	<actiongroup name="testgroup">
		<action>
			<name>testaction</name>
		</action>
	</actiongroup>
</actions>
		""")

		action = mgr.get_action("testaction")
		self.assertEquals(isinstance(action, gtk.Action), True)
		self.assertEquals(action.get_property("name"), "testaction")


	def test_none(self):
		"UIManager.get_action() returns None if not found"

		self.assertEquals(ui.UIManager().get_action("test"), None)



class UIManager_get_action_group(unittest.TestCase):
	"UIManager.get_action_group()"

	def test_action(self):
		"UIManager.get_action_group() looks up group"

		mgr = ui.UIManager()
		mgr.add_actions_from_string("""
<?xml version="1.0" ?>
<actions>
	<actiongroup name="testgroup">
		<action>
			<name>testaction</name>
		</action>
	</actiongroup>
</actions>
		""")

		group = mgr.get_action_group("testgroup")
		self.assertEquals(isinstance(group, gtk.ActionGroup), True)
		self.assertEquals(group.get_name(), "testgroup")


	def test_none(self):
		"UIManager.get_action_group() returns None if not found"

		self.assertEquals(ui.UIManager().get_action_group("test"), None)



class VBox(unittest.TestCase):
	"VBox"

	def test_children(self):
		"VBox accepts children as arguments"

		vbox = ui.VBox(ui.Label("a"), ui.Label("b"), ui.Label("c"))

		self.assertEquals(len(vbox.get_children()), 3)
		self.assertEquals(vbox.get_children()[0].get_text(), "a")
		self.assertEquals(vbox.get_children()[1].get_text(), "b")
		self.assertEquals(vbox.get_children()[2].get_text(), "c")


	def test_hig(self):
		"VBox conforms to the HIG"

		vbox = ui.VBox()
		self.assertEquals(vbox.get_spacing(), 6)
		self.assertEquals(vbox.get_border_width(), 0)


	def test_subclass(self):
		"VBox is subclass of gtk.VBox"

		self.assertEquals(isinstance(ui.VBox(), gtk.VBox), True)



def gtk_run():
	while gtk.events_pending():
		gtk.main_iteration()



if __name__ == "__main__":
	gnome.init("revelation-test", "revelation-test")
	unittest.main()

