#!/usr/bin/env python

#
# Revelation 0.4.0 - a password manager for GNOME 2
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



class PasswordLabel(unittest.TestCase):
	"PasswordLabel"

	def test_config(self):
		"PasswordLabel follows the view/passwords setting"

		global keep_timeout
		keep_timeout = True

		def cb():
			global keep_timeout

			if gtk.main_level() > 0:
				gtk.main_quit()

			return keep_timeout

		gobject.timeout_add(200, cb)

		c = config.Config()
		c.set("view/passwords", True)
		gtk.main()

		label = ui.PasswordLabel("Test123", c)
		self.assertEquals(label.get_text(), "Test123")

		c.set("view/passwords", False)
		gtk.main()
		self.assertEquals(label.get_text(), "******")

		keep_timeout = False
		gtk.main()


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

