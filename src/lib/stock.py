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

import gtk, gtk.gdk, revelation


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
STOCK_PREVIOUS			= "revelation-previous"
STOCK_REMOVE			= "revelation-remove"

STOCK_ACCOUNT_CREDITCARD	= "revelation-account-creditcard"
STOCK_ACCOUNT_CRYPTOKEY		= "revelation-account-cryptokey"
STOCK_ACCOUNT_DATABASE		= "revelation-account-database"
STOCK_ACCOUNT_DOOR		= "revelation-account-door"
STOCK_ACCOUNT_EMAIL		= "revelation-account-email"
STOCK_ACCOUNT_FTP		= "revelation-account-ftp"
STOCK_ACCOUNT_GENERIC		= "revelation-account-generic"
STOCK_ACCOUNT_PHONE		= "revelation-account-phone"
STOCK_ACCOUNT_SHELL		= "revelation-account-shell"
STOCK_ACCOUNT_WEBSITE		= "revelation-account-website"

STOCK_ACCOUNT			= STOCK_ACCOUNT_GENERIC
STOCK_APPLICATION		= "revelation-application"
STOCK_FOLDER			= "revelation-folder"
STOCK_FOLDER_OPEN		= "revelation-folder-open"
STOCK_PASSWORD			= "revelation-password"


ICON_SIZE_DATAVIEW		= gtk.icon_size_register("revelation-dataview", 24, 24)
ICON_SIZE_DROPDOWN		= gtk.icon_size_register("revelation-dropdown", 16, 16)
ICON_SIZE_DRUID			= gtk.icon_size_register("revelation-druid", 48, 48)

# this one needs to be a normal gtk icon size, as the tree cellrenderer
# seems to have problems with custom ones.
ICON_SIZE_TREEVIEW		= gtk.ICON_SIZE_SMALL_TOOLBAR


gtk.stock_add((
	(STOCK_ADD,		"_Add Entry",	0, 0, None),
	(STOCK_DISCARD,		"_Discard",	0, 0, None),
	(STOCK_EDIT,		"_Edit",	0, 0, None),
	(STOCK_EXPORT,		"_Export",	0, 0, None),
	(STOCK_GENERATE,	"_Generate",	0, 0, None),
	(STOCK_IMPORT,		"_Import",	0, 0, None),
	(STOCK_LAUNCH,		"_Launch",	0, 0, None),
	(STOCK_LOCK,		"_Lock",	0, 0, None),
	(STOCK_NEXT,		"Ne_xt",	0, 0, None),
	(STOCK_OVERWRITE,	"_Overwrite",	0, 0, None),
	(STOCK_PREVIOUS,	"Pre_vious",	0, 0, None),
	(STOCK_REMOVE,		"Re_move",	0, 0, None)
))



class IconFactory(gtk.IconFactory):
	"A stock icon factory"

	def __init__(self, widget):
		gtk.IconFactory.__init__(self)
		self.add_default()

		icons = {
			STOCK_APPLICATION		: "revelation.png",
			STOCK_ACCOUNT_CREDITCARD	: "account-creditcard.png",
			STOCK_ACCOUNT_CRYPTOKEY		: "account-cryptokey.png",
			STOCK_ACCOUNT_DATABASE		: "account-database.png",
			STOCK_ACCOUNT_DOOR		: "account-door.png",
			STOCK_ACCOUNT_EMAIL		: "account-email.png",
			STOCK_ACCOUNT_FTP		: "account-ftp.png",
			STOCK_ACCOUNT_GENERIC		: "account-generic.png",
			STOCK_ACCOUNT_PHONE		: "account-phone.png",
			STOCK_ACCOUNT_SHELL		: "account-shell.png",
			STOCK_ACCOUNT_WEBSITE		: "account-website.png",
			STOCK_FOLDER			: "folder.png",
			STOCK_FOLDER_OPEN		: "folder-open.png",
			STOCK_LOCK			: "account-generic.png",
			STOCK_PASSWORD			: "password.png"
		}

		for id, filename in icons.items():
			iconset = gtk.IconSet(gtk.gdk.pixbuf_new_from_file(revelation.DIR_IMAGES + "/" + filename))
			self.add(id, iconset)

		itemicons = {
			STOCK_ADD			: STOCK_ACCOUNT,
			STOCK_DISCARD			: gtk.STOCK_DELETE,
			STOCK_EDIT			: gtk.STOCK_PROPERTIES,
			STOCK_EXPORT			: gtk.STOCK_EXECUTE,
			STOCK_GENERATE			: gtk.STOCK_EXECUTE,
			STOCK_IMPORT			: gtk.STOCK_CONVERT,
			STOCK_LAUNCH			: gtk.STOCK_JUMP_TO,
			STOCK_LOCK			: STOCK_LOCK,
			STOCK_NEXT			: gtk.STOCK_GO_FORWARD,
			STOCK_OVERWRITE			: gtk.STOCK_SAVE_AS,
			STOCK_PREVIOUS			: gtk.STOCK_GO_BACK,
			STOCK_REMOVE			: gtk.STOCK_DELETE
		}

		for id, stock in itemicons.items():
			iconset = widget.get_style().lookup_icon_set(stock)
			self.add(id, iconset)

