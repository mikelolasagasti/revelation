#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module containing stock items and related functionality
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

import gtk, gtk.gdk, gobject, revelation


STOCK_ADD			= "revelation-add"
STOCK_DISCARD			= "revelation-discard"
STOCK_EDIT			= "revelation-edit"
STOCK_EXPORT			= "revelation-export"
STOCK_GENERATE			= "revelation-generate"
STOCK_IMPORT			= "revelation-import"
STOCK_LAUNCH			= "revelation-launch"
STOCK_LOCK			= "revelation-lock"
STOCK_NEXT			= "revelation-next"
STOCK_OVERWRITE			= "revelation-overwrite"
STOCK_PASSWORD_CHANGE		= "revelation-password"
STOCK_PREVIOUS			= "revelation-previous"
STOCK_REMOVE			= "revelation-remove"


STOCK_ENTRY_FOLDER		= "revelation-folder"
STOCK_ENTRY_FOLDER_OPEN		= "revelation-folder-open"

STOCK_ENTRY_CREDITCARD		= "revelation-account-creditcard"
STOCK_ENTRY_CRYPTOKEY		= "revelation-account-cryptokey"
STOCK_ENTRY_DATABASE		= "revelation-account-database"
STOCK_ENTRY_DOOR		= "revelation-account-door"
STOCK_ENTRY_EMAIL		= "revelation-account-email"
STOCK_ENTRY_FTP			= "revelation-account-ftp"
STOCK_ENTRY_GENERIC		= "revelation-account-generic"
STOCK_ENTRY_PHONE		= "revelation-account-phone"
STOCK_ENTRY_SHELL		= "revelation-account-shell"
STOCK_ENTRY_WEBSITE		= "revelation-account-website"

STOCK_REVELATION		= "revelation-revelation"


ICON_SIZE_DROPDOWN		= gtk.icon_size_register("revelation-dropdown",	16, 16)
ICON_SIZE_TREEVIEW		= gtk.icon_size_register("revelation-treeview",	20, 20)
ICON_SIZE_DATAVIEW		= gtk.icon_size_register("revelation-dataview",	24, 24)
ICON_SIZE_LOGO			= gtk.icon_size_register("revelation-logo",	32, 32)



class ItemFactory(gtk.IconFactory):
	"A stock icon factory"

	def __init__(self, parent):
		gtk.IconFactory.__init__(self)
		self.add_default()

		self.parent	= parent
		self.theme	= gtk.icon_theme_get_default()

		if revelation.DIR_ICONS not in self.theme.get_search_path():
			self.theme.append_search_path(revelation.DIR_ICONS)

		self.__init_entryicons()
		self.__init_items()
		self.__init_logo()


	def __init_entryicons(self):
		"Loads entry icons"

		icons = {
			STOCK_ENTRY_CREDITCARD		: "stock_creditcard",
			STOCK_ENTRY_CRYPTOKEY		: "stock_keyring",
			STOCK_ENTRY_DATABASE		: "stock_data-sources",
			STOCK_ENTRY_DOOR		: "stock_exit",
			STOCK_ENTRY_EMAIL		: "stock_mail",
			STOCK_ENTRY_FTP			: "gnome-ftp",
			STOCK_ENTRY_GENERIC		: "stock_lock",
			STOCK_ENTRY_PHONE		: "stock_cell-phone",
			STOCK_ENTRY_SHELL		: "gnome-terminal",
			STOCK_ENTRY_WEBSITE		: "stock_hyperlink-toolbar",
			STOCK_ENTRY_FOLDER		: "gnome-fs-directory",
			STOCK_ENTRY_FOLDER_OPEN		: "gnome-fs-directory-accept"
		}

		for id, name in icons.items():
			self.load_stock_icon(id, name, ( gtk.ICON_SIZE_MENU, ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_TREEVIEW ))


	def __init_items(self):
		"Loads item icons"

		items = (
			(STOCK_ADD,		"_Add Entry",	gtk.STOCK_ADD),
			(STOCK_DISCARD,		"_Discard",	gtk.STOCK_DELETE),
			(STOCK_EDIT,		"_Edit",	gtk.STOCK_PROPERTIES),
			(STOCK_EXPORT,		"_Export",	gtk.STOCK_EXECUTE),
			(STOCK_GENERATE,	"_Generate",	gtk.STOCK_EXECUTE),
			(STOCK_IMPORT,		"_Import",	gtk.STOCK_CONVERT),
			(STOCK_LAUNCH,		"_Launch",	gtk.STOCK_JUMP_TO),
			(STOCK_LOCK,		"_Lock",	gtk.STOCK_DIALOG_AUTHENTICATION),
			(STOCK_NEXT,		"Ne_xt",	gtk.STOCK_GO_FORWARD),
			(STOCK_OVERWRITE,	"_Overwrite",	gtk.STOCK_SAVE_AS),
			(STOCK_PASSWORD_CHANGE,	"_Change",	"stock_lock-ok"),
			(STOCK_PREVIOUS,	"Pre_vious",	gtk.STOCK_GO_BACK),
			(STOCK_REMOVE,		"Re_move",	gtk.STOCK_DELETE)
		)

		for id, name, icon in items:
			self.create_stock_item(id, name, icon)


	def __init_logo(self):
		"Loads the application logo"

		self.load_stock_icon(STOCK_REVELATION, "revelation", [ ICON_SIZE_LOGO, gtk.ICON_SIZE_DIALOG ])


	def create_stock_item(self, id, name, stockicon = None):
		"Creates a stock item"

		gtk.stock_add(((id, name, 0, 0, None),))

		if stockicon is None:
			pass

		elif gtk.stock_lookup(stockicon) is not None:
			iconset = self.parent.get_style().lookup_icon_set(stockicon)
			self.add(id, iconset)

		else:
			self.load_stock_icon(id, stockicon, [ gtk.ICON_SIZE_SMALL_TOOLBAR, gtk.ICON_SIZE_LARGE_TOOLBAR, gtk.ICON_SIZE_MENU, gtk.ICON_SIZE_BUTTON ])


	def load_icon(self, name, size):
		"Loads an icon"

		try:
			return self.theme.load_icon(name, size, 0)

		except gobject.GError:
			return None


	def load_stock_icon(self, id, name, sizes):
		"Registers a stock icon"

		iconset = gtk.IconSet()

		for size in sizes:
			pixelsize = gtk.icon_size_lookup(size)[0]

			source = gtk.IconSource()
			source.set_size(size)
			source.set_size_wildcarded(gtk.FALSE)
			source.set_pixbuf(self.theme.load_icon(name, pixelsize, 0))
			iconset.add_source(source)

		self.add(id, iconset)

