#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
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


class DataView(revelation.widget.VBox):
	"An UI component for displaying an entry"

	def __init__(self):
		revelation.widget.VBox.__init__(self)
		self.set_spacing(15)
		self.set_border_width(10)

		self.size_name = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
		self.size_value = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

		self.entry = None


	def clear(self, force = gtk.FALSE):
		"Clears the data view"

		# only clear if containing an entry, or if forced
		if force == gtk.TRUE or self.entry is not None:

			self.entry = None

			for child in self.get_children():
				child.destroy()


	def display_entry(self, entry):
		"Displays an entry"

		if entry is None:
			self.clear()
			return

		self.clear(gtk.TRUE)
		self.entry = entry

		# set up metadata display
		metabox = revelation.widget.VBox()
		self.pack_start(metabox)

		metabox.pack_start(revelation.widget.ImageLabel(
			entry.icon, revelation.stock.ICON_SIZE_DATAVIEW,
			"<span size=\"large\" weight=\"bold\">" + revelation.misc.escape_markup(entry.name) + "</span>"
		))

		metabox.pack_start(revelation.widget.Label("<span weight=\"bold\">" + entry.typename + (entry.description != "" and "; " or "") + "</span>" + revelation.misc.escape_markup(entry.description), gtk.JUSTIFY_CENTER))

		# set up field list
		rows = []

		for field in entry.get_fields():
			if field.value == "":
				continue

			row = revelation.widget.HBox()
			rows.append(row)

			label = revelation.widget.Label("<span weight=\"bold\">" + revelation.misc.escape_markup(field.name) + ":</span>", gtk.JUSTIFY_RIGHT)
			self.size_name.add_widget(label)
			row.pack_start(label, gtk.FALSE, gtk.FALSE)


			if field.type == revelation.entry.FIELD_TYPE_EMAIL:
				widget = revelation.widget.HRef("mailto:" + field.value, revelation.misc.escape_markup(field.value))

			elif field.type == revelation.entry.FIELD_TYPE_URL:
				widget = revelation.widget.HRef(field.value, revelation.misc.escape_markup(field.value))

			elif field.type == revelation.entry.FIELD_TYPE_PASSWORD:
				widget = revelation.widget.PasswordLabel(revelation.misc.escape_markup(field.value))

			else:
				widget = revelation.widget.Label(revelation.misc.escape_markup(field.value))
				widget.set_selectable(gtk.TRUE)

			self.size_value.add_widget(widget)
			row.pack_start(widget, gtk.FALSE, gtk.FALSE)


		if len(rows) > 0:
			fieldlist = revelation.widget.VBox()
			fieldlist.set_spacing(2)
			self.pack_start(fieldlist)

			for row in rows:
				fieldlist.pack_start(row, gtk.FALSE, gtk.FALSE)

		# display updatetime
		if entry.type != revelation.entry.ENTRY_FOLDER:
			self.pack_start(revelation.widget.Label("Updated " + entry.get_updated_age() + " ago; \n" + entry.get_updated_iso(), gtk.JUSTIFY_CENTER))

		self.show_all()


	def display_info(self):
		"Displays info about the application"

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
		"Adds a widget to the data view"

		alignment = gtk.Alignment(0.5, 0.5, 0, 0)
		alignment.add(widget)
		revelation.widget.VBox.pack_start(self, alignment)



class Tree(revelation.widget.TreeView):
	"The entry tree"

	def __init__(self, datastore = None):
		revelation.widget.TreeView.__init__(self, datastore)

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


	def __cb_row_collapsed(self, object, iter, extra):
		"Updates folder icons when collapsed"

		self.model.set_folder_state(iter, gtk.FALSE)


	def __cb_row_expanded(self, object, iter, extra):
		"Updates folder icons when expanded"

		# make sure all children are collapsed (some may have lingering expand icons)
		for i in range(self.model.iter_n_children(iter)):
			child = self.model.iter_nth_child(iter, i)

			if self.row_expanded(self.model.get_path(child)) == gtk.FALSE:
				self.model.set_folder_state(child, gtk.FALSE)

		self.model.set_folder_state(iter, gtk.TRUE)


	def set_model(self, model):
		"Sets the model displayed by the tree view"

		revelation.widget.TreeView.set_model(self, model)

		if model is not None:
			for i in range(model.iter_n_children(None)):
				model.set_folder_state(model.iter_nth_child(None, i), gtk.FALSE)

