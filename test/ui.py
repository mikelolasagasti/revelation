#!/usr/bin/env python

#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for ui module
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

import gobject, gtk, unittest

from revelation import config, entry, ui



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
		self.assertEquals(hasattr(ui, "STOCK_IMPORT"), True)
		self.assertEquals(hasattr(ui, "STOCK_LAUNCH"), True)
		self.assertEquals(hasattr(ui, "STOCK_LOCK"), True)
		self.assertEquals(hasattr(ui, "STOCK_NEXT"), True)
		self.assertEquals(hasattr(ui, "STOCK_OVERWRITE"), True)
		self.assertEquals(hasattr(ui, "STOCK_PASSWORD_CHANGE"), True)
		self.assertEquals(hasattr(ui, "STOCK_PREVIOUS"), True)
		self.assertEquals(hasattr(ui, "STOCK_REMOVE"), True)
		self.assertEquals(hasattr(ui, "STOCK_REVELATION"), True)



class config_bind(unittest.TestCase):
	"config_bind()"

	def __cb_timeout(self):
		"callback for timing out gtk mainloop"

		if gtk.main_level() > 0:
			gtk.main_quit()

		return self.__timeout_keep


	def setUp(self):
		"sets up common facilities for the test"

		self.__timeout_keep = True
		gobject.timeout_add(200, self.__cb_timeout)

		self.config = config.Config()


	def tearDown(self):
		"removes common facilities"

		self.__timeout_keep = False
		gtk.main()


	def test_check(self):
		"config_bind() handles check items correctly"

		self.config.set("view/searchbar", True)

		# test initial state
		check = ui.CheckButton("Test")
		ui.config_bind(self.config, "view/searchbar", check)
		gtk.main()
		self.assertEquals(check.get_active(), True)

		# test config value change
		self.config.set("view/searchbar", False)
		gtk.main()
		self.assertEquals(check.get_active(), False)

		# test widget change
		check.set_active(True)
		gtk.main()
		self.assertEquals(self.config.get("view/searchbar"), True)


	def test_entry(self):
		"config_bind() handles entries correctly"

		self.config.set("file/autoload_file", "test123")

		# test initial state
		entry = ui.Entry()
		ui.config_bind(self.config, "file/autoload_file", entry)
		gtk.main()
		self.assertEquals(entry.get_text(), "test123")

		# test config value change
		self.config.set("file/autoload_file", "test again")
		gtk.main()
		self.assertEquals(entry.get_text(), "test again")

		# test widget change
		entry.set_text("")
		gtk.main()
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
		gtk.main()
		self.assertEquals(spin.get_value(), 500)

		# test config value change
		self.config.set("view/pane-position", 200)
		gtk.main()
		self.assertEquals(spin.get_value(), 200)

		# test widget change
		spin.set_value(300)
		gtk.main()
		self.assertEquals(self.config.get("view/pane-position"), 300)


	def test_unrealize(self):
		"config_bind() removes the callback when the widget is destroyed"

		check = ui.CheckButton()
		id = ui.config_bind(self.config, "view/searchbar", check)
		self.assertEquals(self.config.callbacks.has_key(id), True)

		hbox = ui.HBox()
		hbox.pack_start(check)
		hbox.destroy()
		gtk.main()

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



if __name__ == "__main__":
	unittest.main()

