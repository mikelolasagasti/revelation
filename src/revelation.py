#!/usr/bin/python

#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
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

import gettext, gobject, gtk, gtk.gdk, os, pwd, sys, dbus, urllib
from dbus.mainloop.glib import DBusGMainLoop

from revelation import config, data, datahandler, dialog, entry, io, ui, util

_ = gettext.gettext

class Revelation(ui.App):
	"The Revelation application"

	def __init__(self):
		sys.excepthook = self.__cb_exception
		os.umask(0077)

		gettext.bindtextdomain(config.PACKAGE, config.DIR_LOCALE)
		gettext.bind_textdomain_codeset(config.PACKAGE, "UTF-8")
		gettext.textdomain(config.PACKAGE)

		ui.App.__init__(self, config.APPNAME)

		self.connect("delete-event", self.__cb_quit)

		try:
			self.__init_actions()
			self.__init_facilities()
			self.__init_ui()
			self.__init_states()
			self.__init_dbus()

		except IOError:
			dialog.Error(self, _('Missing data files'), _('Some of Revelations system files could not be found, please reinstall Revelation.')).run()
			sys.exit(1)

		except config.ConfigError:
			dialog.Error(self, _('Missing configuration data'), _('Revelation could not find its configuration data, please reinstall Revelation.')).run()
			sys.exit(1)

		except ui.DataError:
			dialog.Error(self, _('Invalid data files'), _('Some of Revelations system files contain invalid data, please reinstall Revelation.')).run()
			sys.exit(1)


	def __init_actions(self):
		"Sets up actions"

		# set up placeholders
		group	= ui.ActionGroup("placeholder")
		self.uimanager.append_action_group(group)

		group.add_action(ui.Action("menu-edit",		_('_Edit')))
		group.add_action(ui.Action("menu-entry",	_('E_ntry')))
		group.add_action(ui.Action("menu-file",		_('_File')))
		group.add_action(ui.Action("menu-help",		_('_Help')))
		group.add_action(ui.Action("menu-view",		_('_View')))
		group.add_action(ui.Action("popup-tree"))

		# set up dynamic actions
		group	= ui.ActionGroup("dynamic")
		self.uimanager.append_action_group(group)

		action	= ui.Action("clip-paste",	_('_Paste'),		_('Paste entry from clipboard'),		"gtk-paste")
		action.connect("activate",		self.__cb_clip_paste)
		group.add_action(action, "<Control>V")

		action	= ui.Action("entry-goto",	_('_Go to'),		_('Go to the selected entries'),		"revelation-goto",	True)
		action.connect("activate",		lambda w: self.entry_goto(self.tree.get_selected()))
		group.add_action(action, "<Shift><Control>Return")

		action	= ui.Action("redo",		_('_Redo'),		_('Redo the previously undone action'),		"gtk-redo")
		action.connect("activate",		lambda w: self.redo())
		group.add_action(action, "<Shift><Control>Z")

		action	= ui.Action("undo",		_('_Undo'),		_('Undo the last action'),			"gtk-undo")
		action.connect("activate",		lambda w: self.undo())
		group.add_action(action, "<Control>Z")

		# set up group for multiple entries
		group	= ui.ActionGroup("entry-multiple")
		self.uimanager.append_action_group(group)

		action	= ui.Action("clip-copy",	_('_Copy'),		_('Copy selected entries to the clipboard'),	"gtk-copy")
		action.connect("activate",		self.__cb_clip_copy)
		group.add_action(action, "<Control>C")

		action	= ui.Action("clip-chain",	_('Copy Pass_word'),	_('Copy password to the clipboard'))
		action.connect("activate",		lambda w: self.clip_chain(self.entrystore.get_entry(self.tree.get_active())))
		group.add_action(action, "<Shift><Control>C")

		action	= ui.Action("clip-cut",		_('Cu_t'),		_('Cut selected entries to the clipboard'),	"gtk-cut")
		action.connect("activate",		self.__cb_clip_cut)
		group.add_action(action, "<Control>X")

		action	= ui.Action("entry-remove",	_('Re_move'),		_('Remove the selected entries'),		"revelation-remove")
		action.connect("activate",		lambda w: self.entry_remove(self.tree.get_selected()))
		group.add_action(action, "<Control>Delete")

		# action group for "optional" entries
		group	= ui.ActionGroup("entry-optional")
		self.uimanager.append_action_group(group)

		action	= ui.Action("entry-add",	_('_Add Entry...'),	_('Create a new entry'),			"revelation-new-entry",		True)
		action.connect("activate",		lambda w: self.entry_add(None, self.tree.get_active()))
		group.add_action(action, "<Control>Insert")

		action	= ui.Action("entry-folder",	_('Add _Folder...'),	_('Create a new folder'),			"revelation-new-folder")
		action.connect("activate",		lambda w: self.entry_folder(None, self.tree.get_active()))
		group.add_action(action, "<Shift><Control>Insert")

		# action group for single entries
		group	= ui.ActionGroup("entry-single")
		self.uimanager.append_action_group(group)

		action	= ui.Action("entry-edit",	_('_Edit...'),		_('Edit the selected entry'),			"revelation-edit")
		action.connect("activate",		lambda w: self.entry_edit(self.tree.get_active()))
		group.add_action(action, "<Control>Return")

		# action group for existing file
		group	= ui.ActionGroup("file-exists")
		self.uimanager.append_action_group(group)

		action	= ui.Action("file-lock",	_('_Lock'),		_('Lock the current data file'),		"revelation-lock")
		action.connect("activate",		lambda w: self.file_lock())
		group.add_action(action, "<Control>L")

		# action group for searching
		group	= ui.ActionGroup("find")
		self.uimanager.append_action_group(group)

		action	= ui.Action("find-next",	_('Find Ne_xt'),	_('Find the next search match'),		"find-next")
		action.connect("activate",		lambda w: self.__entry_find(self, self.searchbar.entry.get_text(), self.searchbar.dropdown.get_active_type(), data.SEARCH_NEXT))
		group.add_action(action, "<Control>G")

		action	= ui.Action("find-previous",	_('Find Pre_vious'),	_('Find the previous search match'),		"find-previous")
		action.connect("activate",		lambda w: self.__entry_find(self, self.searchbar.entry.get_text(), self.searchbar.dropdown.get_active_type(), data.SEARCH_PREVIOUS))
		group.add_action(action, "<Shift><Control>G")

		# global action group
		group	= ui.ActionGroup("file")
		self.uimanager.append_action_group(group)

		action	= ui.Action("file-change-password",	_('Change _Password...'),	_('Change password of current file'),		"revelation-password-change")
		action.connect("activate",		lambda w: self.file_change_password())
		group.add_action(action)

		action	= ui.Action("file-close",	_('_Close'),		_('Close the application'),			"gtk-close")
		action.connect("activate",		self.__cb_quit)
		group.add_action(action, "<Control>W")

		action	= ui.Action("file-export",	_('_Export...'),	_('Export data to a different file format'),	"revelation-export")
		action.connect("activate",		lambda w: self.file_export())
		group.add_action(action)

		action	= ui.Action("file-import",	_('_Import...'),	_('Import data from a foreign file'),		"revelation-import")
		action.connect("activate",		lambda w: self.file_import())
		group.add_action(action)

		action	= ui.Action("file-new",		_('_New'),		_('Create a new file'),				"gtk-new")
		action.connect("activate",		lambda w: self.file_new())
		group.add_action(action, "<Control>N")

		action	= ui.Action("file-open",	_('_Open'),		_('Open a file'),				"gtk-open")
		action.connect("activate",		lambda w: self.file_open())
		group.add_action(action, "<Control>O")

		action	= ui.Action("file-save",	_('_Save'),		_('Save data to a file'),			"gtk-save",		True)
		action.connect("activate",		lambda w: self.file_save(self.datafile.get_file(), self.datafile.get_password()))
		group.add_action(action, "<Control>S")

		action	= ui.Action("file-save-as",	_('Save _as...'),	_('Save data to a different file'),		"gtk-save-as")
		action.connect("activate",		lambda w: self.file_save(None, None))
		group.add_action(action, "<Shift><Control>S")

		action	= ui.Action("find",		_('_Find...'),		_('Search for an entry'),			"gtk-find")
		action.connect("activate",		lambda w: self.entry_find())
		group.add_action(action, "<Control>F")

		action	= ui.Action("help-about",	_('_About'),		_('About this application'),			"gnome-stock-about")
		action.connect("activate",		lambda w: self.about())
		group.add_action(action)

		action	= ui.Action("prefs",		_('Prefere_nces'),	_('Edit preferences'),				"gtk-preferences")
		action.connect("activate",		lambda w: self.prefs())
		group.add_action(action)

		action	= ui.Action("pwchecker",	_('Password _Checker'),	_('Opens a password checker'),			"revelation-password-check")
		action.connect("activate",		lambda w: self.pwcheck())
		group.add_action(action)

		action	= ui.Action("pwgenerator",	_('Password _Generator'),	_('Opens a password generator'),	"revelation-generate")
		action.connect("activate",		lambda w: self.pwgen())
		group.add_action(action)

		action	= ui.Action("quit",		_('_Quit'),		_('Quit the application'),			"gtk-quit")
		action.connect("activate",		self.__cb_quit)
		group.add_action(action, "<Control>Q")

		action	= ui.Action("select-all",	_('_Select All'),	_('Selects all entries'))
		action.connect("activate",		lambda w: self.tree.select_all())
		group.add_action(action, "<Control>A")

		action	= ui.Action("select-none",	_('_Deselect All'),	_('Deselects all entries'))
		action.connect("activate",		lambda w: self.tree.unselect_all())
		group.add_action(action, "<Shift><Control>A")

		action	= ui.ToggleAction("view-passwords",	_('Show _Passwords'),	_('Toggle display of passwords'))
		group.add_action(action, "<Control>P")

		action	= ui.ToggleAction("view-searchbar",	_('S_earch Toolbar'),	_('Toggle the search toolbar'))
		group.add_action(action)

		action	= ui.ToggleAction("view-statusbar",	_('_Statusbar'),	_('Toggle the statusbar'))
		group.add_action(action)

		action	= ui.ToggleAction("view-toolbar",	_('_Main Toolbar'),	_('Toggle the main toolbar'))
		group.add_action(action)


	def __init_facilities(self):
		"Sets up various facilities"

		self.clipboard		= data.Clipboard()
		self.config		= config.Config()
		self.datafile		= io.DataFile(datahandler.Revelation2)
		self.entryclipboard	= data.EntryClipboard()
		self.entrystore		= data.EntryStore()
		self.entrysearch	= data.EntrySearch(self.entrystore)
		self.items		= ui.ItemFactory(self)
		self.locktimer		= data.Timer()
		self.undoqueue		= data.UndoQueue()

		self.datafile.connect("changed", lambda w,f: self.__state_file(f))
		self.datafile.connect("content-changed", self.__cb_file_content_changed)
		self.entryclipboard.connect("content-toggled", lambda w,d: self.__state_clipboard(d))
		self.locktimer.connect("ring", self.__cb_file_autolock)
		self.undoqueue.connect("changed", lambda w: self.__state_undo(self.undoqueue.get_undo_action(), self.undoqueue.get_redo_action()))

		# check if configuration is updated, install schema if not
		if self.__check_config() == False:

			if config.install_schema("%s/revelation.schemas" % config.DIR_GCONFSCHEMAS) == False:
				raise config.ConfigError

			self.config.client.clear_cache()

			if self.__check_config() == False:
				raise config.ConfigError

		self.config.monitor("file/autolock_timeout",	lambda k,v,d: self.locktimer.start(v * 60))

		dialog.EVENT_FILTER = self.__cb_event_filter


	def __init_states(self):
		"Sets the initial application state"

		# set window states
		self.set_default_size(
			self.config.get("view/window-width"),
			self.config.get("view/window-height")
		)

		self.move(
			self.config.get("view/window-position-x"),
			self.config.get("view/window-position-y")
		)

		self.hpaned.set_position(
			self.config.get("view/pane-position")
		)

		# bind ui widgets to config keys
		bind = {
			"view/passwords"	: "/menubar/menu-view/view-passwords",
			"view/searchbar"	: "/menubar/menu-view/view-searchbar",
			"view/statusbar"	: "/menubar/menu-view/view-statusbar",
			"view/toolbar"		: "/menubar/menu-view/view-toolbar"
		}

		for key, path in bind.items():
			ui.config_bind(self.config, key, self.uimanager.get_widget(path))

		self.show_all()

		self.window.add_filter(self.__cb_event_filter)


		# set some variables
		self.entrysearch.string	= ''
		self.entrysearch.type	= None

		# set ui widget states
		self.__state_clipboard(self.entryclipboard.has_contents())
		self.__state_entry([])
		self.__state_file(None)
		self.__state_find(self.searchbar.entry.get_text())
		self.__state_undo(None, None)

		# set states from config
		self.config.monitor("view/searchbar", self.__cb_config_toolbar, self.searchbar)
		self.config.monitor("view/statusbar", self.__cb_config_toolbar, self.statusbar)
		self.config.monitor("view/toolbar", self.__cb_config_toolbar, self.toolbar)
		self.config.monitor("view/toolbar_style", self.__cb_config_toolbar_style)

		# give focus to searchbar entry if shown
		if self.searchbar.get_property("visible") == True:
			self.searchbar.entry.grab_focus()


	def __init_ui(self):
		"Sets up the UI"

		gtk.about_dialog_set_url_hook(lambda d,l: gtk.show_uri(None, l, gtk.get_current_event_time()))
		gtk.about_dialog_set_email_hook(lambda d,l: gtk.show_uri(None, "mailto:" + l, gtk.get_current_event_time()))

		# set window icons
		pixbufs = [ self.items.get_pixbuf("revelation", size) for size in ( 48, 32, 24, 16) ]
		pixbufs = [ pixbuf for pixbuf in pixbufs if pixbuf != None ]

		if len(pixbufs) > 0:
			gtk.window_set_default_icon_list(*pixbufs)

		# load UI definitions
		self.uimanager.add_ui_from_file(config.DIR_UI + "/menubar.xml")
		self.uimanager.add_ui_from_file(config.DIR_UI + "/popup-tree.xml")
		self.uimanager.add_ui_from_file(config.DIR_UI + "/toolbar.xml")

		# set up toolbar and menus
		self.set_menus(self.uimanager.get_widget("/menubar"))

		self.toolbar = self.uimanager.get_widget("/toolbar")
		self.toolbar.connect("popup-context-menu", lambda w,x,y,b: True)
		self.set_toolbar(self.toolbar)

		try:
			detachable = self.config.get("/desktop/gnome/interface/toolbar_detachable")

		except config.ConfigError:
			detachable = False

		self.searchbar = ui.Searchbar()
		self.add_toolbar(self.searchbar, "searchbar", 2, detachable)

		# set up main application widgets
		self.tree = ui.EntryTree(self.entrystore)
		self.scrolledwindow = ui.ScrolledWindow(self.tree)

		self.entryview = ui.EntryView(self.config, self.clipboard)
		alignment = ui.Alignment(self.entryview, 0.5, 0.5, 1, 0)

		self.hpaned = ui.HPaned(self.scrolledwindow, alignment)
		self.set_contents(self.hpaned)

		# set up drag-and-drop
		self.drag_dest_set(gtk.DEST_DEFAULT_ALL, ( ( "text/uri-list", 0, 0 ), ), gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_LINK )
		self.connect("drag_data_received", self.__cb_drag_dest)

		self.tree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, ( ( "revelation/treerow", gtk.TARGET_SAME_APP | gtk.TARGET_SAME_WIDGET, 0), ), gtk.gdk.ACTION_MOVE)
		self.tree.enable_model_drag_dest(( ( "revelation/treerow", gtk.TARGET_SAME_APP | gtk.TARGET_SAME_WIDGET, 0), ), gtk.gdk.ACTION_MOVE)
		self.tree.connect("drag_data_received", self.__cb_tree_drag_received)

		# set up callbacks
		self.searchbar.connect("key-press-event", self.__cb_searchbar_key_press)
		self.searchbar.button_next.connect("clicked", self.__cb_searchbar_button_clicked, data.SEARCH_NEXT)
		self.searchbar.button_prev.connect("clicked", self.__cb_searchbar_button_clicked, data.SEARCH_PREVIOUS)
		self.searchbar.entry.connect("changed", lambda w: self.__state_find(self.searchbar.entry.get_text()))

		self.tree.connect("popup", lambda w,d: self.popup(self.uimanager.get_widget("/popup-tree"), d.button, d.time))
		self.tree.connect("doubleclick", self.__cb_tree_doubleclick)
		self.tree.connect("key-press-event", self.__cb_tree_keypress)
		self.tree.selection.connect("changed", lambda w: self.entryview.display_entry(self.entrystore.get_entry(self.tree.get_active())))
		self.tree.selection.connect("changed", lambda w: self.__state_entry(self.tree.get_selected()))

	def __init_dbus(self):
		loop = DBusGMainLoop()
		self.bus = dbus.SessionBus(mainloop=loop)
		self.bus.add_signal_receiver(self.__cb_screensaver_lock, signal_name='ActiveChanged', dbus_interface='org.gnome.ScreenSaver')
		self.bus.add_signal_receiver(self.__cb_screensaver_lock, signal_name='ActiveChanged', dbus_interface='org.freedesktop.ScreenSaver')

	##### STATE HANDLERS #####

	def __save_state(self):
		"Saves the current application state"

		width, height = self.get_size()
		self.config.set("view/window-width", width)
		self.config.set("view/window-height", height)

		x, y = self.get_position()
		self.config.set("view/window-position-x", x)
		self.config.set("view/window-position-y", y)

		self.config.set("view/pane-position", self.hpaned.get_position())


	def __state_clipboard(self, has_contents):
		"Sets states based on the clipboard contents"

		self.uimanager.get_action("clip-paste").set_property("sensitive", has_contents)


	def __state_entry(self, iters):
		"Sets states for entry-dependant ui items"

		# widget sensitivity based on number of entries
		self.uimanager.get_action_group("entry-multiple").set_sensitive(len(iters) > 0)
		self.uimanager.get_action_group("entry-single").set_sensitive(len(iters) == 1)
		self.uimanager.get_action_group("entry-optional").set_sensitive(len(iters) < 2)


		# copy password sensitivity
		s = False

		for iter in iters:
			e = self.entrystore.get_entry(iter)

			for f in e.fields:
				if f.datatype == entry.DATATYPE_PASSWORD and f.value != "":
					s = True

		self.uimanager.get_action("clip-chain").set_property("sensitive", s)


		# goto sensitivity
		try:
			for iter in iters:
				e = self.entrystore.get_entry(iter)

				if self.config.get("launcher/%s" % e.id) not in ( "", None ):
					s = True
					break

			else:
				s = False

		except config.ConfigError:
			s = False

		self.uimanager.get_action("entry-goto").set_sensitive(s)


	def __state_file(self, file):
		"Sets states based on file"

		self.uimanager.get_action_group("file-exists").set_sensitive(file is not None)

		if file is not None:
			self.set_title(os.path.basename(file))

			if io.file_is_local(file):
				os.chdir(os.path.dirname(file))

		else:
			self.set_title('[' + _('New file') + ']')


	def __state_find(self, string):
		"Sets states based on the current search string"

		self.uimanager.get_action_group("find").set_sensitive(string != "")


	def __state_undo(self, undoaction, redoaction):
		"Sets states based on undoqueue actions"

		if undoaction is None:
			s, l = False, _('_Undo')

		else:
			s, l = True, _('_Undo %s') % undoaction[1].lower()

		action = self.uimanager.get_action("undo")
		action.set_property("sensitive", s)
		action.set_property("label", l)


		if redoaction is None:
			s, l = False, _('_Redo')

		else:
			s, l = True, _('_Redo %s') % redoaction[1].lower()

		action = self.uimanager.get_action("redo")
		action.set_property("sensitive", s)
		action.set_property("label", l)




	##### MISC CALLBACKS #####

	def __cb_clip_copy(self, widget, data = None):
		"Handles copying to the clipboard"

		focuswidget = self.get_focus()

		if focuswidget is self.tree:
			self.clip_copy(self.tree.get_selected())

		elif isinstance(focuswidget, gtk.Label) or isinstance(focuswidget, gtk.Entry):
			focuswidget.emit("copy-clipboard")


	def __cb_clip_cut(self, widget, data = None):
		"Handles cutting to clipboard"

		focuswidget = self.get_focus()

		if focuswidget is self.tree:
			self.clip_cut(self.tree.get_selected())

		elif isinstance(focuswidget, gtk.Entry):
			focuswidget.emit("cut-clipboard")


	def __cb_clip_paste(self, widget, data = None):
		"Handles pasting from clipboard"

		focuswidget = self.get_focus()

		if focuswidget is self.tree:
			self.clip_paste(self.entryclipboard.get(), self.tree.get_active())

		elif isinstance(focuswidget, gtk.Entry):
			focuswidget.emit("paste-clipboard")


	def __cb_drag_dest(self, widget, context, x, y, seldata, info, time, userdata = None):
		"Handles file drops"

		if seldata.data is None:
			return

		files = [ file.strip() for file in seldata.data.split("\n") if file.strip() != "" ]

		if len(files) > 0:
			self.file_open(files[0])


	def __cb_event_filter(self, event):
		"Event filter for gdk window"

		self.locktimer.reset()
		return gtk.gdk.FILTER_CONTINUE


	def __cb_exception(self, type, value, trace):
		"Callback for unhandled exceptions"

		if type == KeyboardInterrupt:
			sys.exit(1)

		traceback = util.trace_exception(type, value, trace)
		sys.stderr.write(traceback)

		if dialog.Exception(self, traceback).run() == True:
			gtk.main()

		else:
			sys.exit(1)


	def __cb_file_content_changed(self, widget, file):
		"Callback for changed file"

		try:
			if dialog.FileChanged(self, file).run() == True:
				self.file_open(self.datafile.get_file(), self.datafile.get_password())

		except dialog.CancelError:
			self.statusbar.set_status(_('Open cancelled'))


	def __cb_file_autolock(self, widget, data = None):
		"Callback for locking the file"

		if self.config.get("file/autolock") == True:
			self.file_lock()


	def __cb_screensaver_lock(self, screensaver_active):
		if screensaver_active and self.config.get("file/autolock") == True:
			self.file_lock()

	def __cb_quit(self, widget, data = None):
		"Callback for quit"

		if self.quit() == False:
			return True

		else:
			return False


	def __cb_searchbar_button_clicked(self, widget, direction = data.SEARCH_NEXT):
		"Callback for searchbar button clicks"

		self.__entry_find(self, self.searchbar.entry.get_text(), self.searchbar.dropdown.get_active_type(), direction)
		self.searchbar.entry.select_region(0, -1)


	def __cb_searchbar_key_press(self, widget, data):
		"Callback for searchbar key presses"

		# escape
		if data.keyval == 65307:
			self.config.set("view/searchbar", False)


	def __cb_tree_doubleclick(self, widget, iter):
		"Handles doubleclicks on the tree"

		if self.config.get("behavior/doubleclick") == "edit":
			self.entry_edit(iter)

		elif self.config.get("behavior/doubleclick") == "copy":
			self.clip_chain(self.entrystore.get_entry(iter))

		else:
			self.entry_goto((iter,))


	def __cb_tree_drag_received(self, tree, context, x, y, seldata, info, time):
		"Callback for drag drops on the treeview"

		# get source and destination data
		sourceiters = self.entrystore.filter_parents(self.tree.get_selected())
		destrow = self.tree.get_dest_row_at_pos(x, y)

		if destrow is None:
			destpath = ( self.entrystore.iter_n_children(None) - 1, )
			pos = gtk.TREE_VIEW_DROP_AFTER

		else:
			destpath, pos = destrow

		destiter = self.entrystore.get_iter(destpath)
		destpath = self.entrystore.get_path(destiter)

		# avoid drops to current iter or descentants
		for sourceiter in sourceiters:
			sourcepath = self.entrystore.get_path(sourceiter)

			if self.entrystore.is_ancestor(sourceiter, destiter) == True or sourcepath == destpath:
				context.finish(False, False, long(time))
				return

			elif pos == gtk.TREE_VIEW_DROP_BEFORE and sourcepath[:-1] == destpath[:-1] and sourcepath[-1] == destpath[-1] - 1:
				context.finish(False, False, long(time))
				return

			elif pos == gtk.TREE_VIEW_DROP_AFTER and sourcepath[:-1] == destpath[:-1] and sourcepath[-1] == destpath[-1] + 1:
				context.finish(False, False, long(time))
				return


		# move the entries
		if pos in ( gtk.TREE_VIEW_DROP_INTO_OR_BEFORE, gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
			parent = destiter
			sibling = None

		elif pos == gtk.TREE_VIEW_DROP_BEFORE:
			parent = self.entrystore.iter_parent(destiter)
			sibling = destiter

		elif pos == gtk.TREE_VIEW_DROP_AFTER:
			parent = self.entrystore.iter_parent(destiter)

			sibpath = list(destpath)
			sibpath[-1] += 1
			sibling = self.entrystore.get_iter(sibpath)

		self.entry_move(sourceiters, parent, sibling)

		context.finish(False, False, long(time))


	def __cb_tree_keypress(self, widget, data = None):
		"Handles key presses for the tree"

		# return
		if data.keyval == 65293:
			self.entry_edit(self.tree.get_active())

		# insert
		elif data.keyval == 65379:
			self.entry_add(None, self.tree.get_active())

		# delete
		elif data.keyval == 65535:
			self.entry_remove(self.tree.get_selected())



	##### CONFIG CALLBACKS #####

	def __cb_config_toolbar(self, config, value, toolbar):
		"Config callback for showing toolbars"

		if value == True:
			toolbar.show()

		else:
			toolbar.hide()


	def __cb_config_toolbar_style(self, config, value, data = None):
		"Config callback for setting toolbar style"

		if value == "both":
			self.toolbar.set_style(gtk.TOOLBAR_BOTH)

		elif value == "both-horiz":
			self.toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)

		elif value == "icons":
			self.toolbar.set_style(gtk.TOOLBAR_ICONS)

		elif value == "text":
			self.toolbar.set_style(gtk.TOOLBAR_TEXT)

		else:
			self.toolbar.unset_style()


	#### UNDO / REDO CALLBACKS #####

	def __cb_redo_add(self, name, actiondata):
		"Redoes an add action"

		path, e = actiondata
		parent = self.entrystore.get_iter(path[:-1])
		sibling = self.entrystore.get_iter(path)

		iter = self.entrystore.add_entry(e, parent, sibling)
		self.tree.select(iter)


	def __cb_redo_edit(self, name, actiondata):
		"Redoes an edit action"

		path, preentry, postentry = actiondata
		iter = self.entrystore.get_iter(path)

		self.entrystore.update_entry(iter, postentry)
		self.tree.select(iter)


	def __cb_redo_import(self, name, actiondata):
		"Redoes an import action"

		paths, entrystore = actiondata
		self.entrystore.import_entry(entrystore, None)


	def __cb_redo_move(self, name, actiondata):
		"Redoes a move action"

		newiters = []

		for prepath, postpath in actiondata:
			prepath, postpath = list(prepath), list(postpath)

			# adjust path if necessary
			if len(prepath) <= len(postpath):
				if prepath[:-1] == postpath[:len(prepath) - 1]:
					if prepath[-1] <= postpath[len(prepath) - 1]:
						postpath[len(prepath) - 1] += 1

			newiter = self.entrystore.move_entry(
				self.entrystore.get_iter(prepath),
				self.entrystore.get_iter(postpath[:-1]),
				self.entrystore.get_iter(postpath)
			)

			newiters.append(newiter)

		if len(newiters) > 0:
			self.tree.select(newiters[0])


	def __cb_redo_paste(self, name, actiondata):
		"Redoes a paste action"

		entrystore, parentpath, paths = actiondata
		iters = self.entrystore.import_entry(entrystore, None, self.entrystore.get_iter(parentpath))

		if len(iters) > 0:
			self.tree.select(iters[0])


	def __cb_redo_remove(self, name, actiondata):
		"Redoes a remove action"

		iters = []
		for path, entrystore in actiondata:
			iters.append(self.entrystore.get_iter(path))

		for iter in iters:
			self.entrystore.remove_entry(iter)

		self.tree.unselect_all()


	def __cb_undo_add(self, name, actiondata):
		"Undoes an add action"

		path, e = actiondata

		self.entrystore.remove_entry(self.entrystore.get_iter(path))
		self.tree.unselect_all()


	def __cb_undo_edit(self, name, actiondata):
		"Undoes an edit action"

		path, preentry, postentry = actiondata
		iter = self.entrystore.get_iter(path)

		self.entrystore.update_entry(iter, preentry)
		self.tree.select(iter)


	def __cb_undo_import(self, name, actiondata):
		"Undoes an import action"

		paths, entrystore = actiondata
		iters = [ self.entrystore.get_iter(path) for path in paths ]

		for iter in iters:
			self.entrystore.remove_entry(iter)

		self.tree.unselect_all()


	def __cb_undo_move(self, name, actiondata):
		"Undoes a move action"

		actiondata = actiondata[:]
		actiondata.reverse()

		newiters = []

		for prepath, postpath in actiondata:
			prepath, postpath = list(prepath), list(postpath)

			# adjust path if necessary
			if len(postpath) <= len(prepath):
				if postpath[:-1] == prepath[:len(postpath) - 1]:
					if postpath[-1] <= prepath[len(postpath) - 1]:
						prepath[len(postpath) - 1] += 1

			newiter = self.entrystore.move_entry(
				self.entrystore.get_iter(postpath),
				self.entrystore.get_iter(prepath[:-1]),
				self.entrystore.get_iter(prepath)
			)

			newiters.append(newiter)

		if len(newiters) > 0:
			self.tree.select(newiters[-1])


	def __cb_undo_paste(self, name, actiondata):
		"Undoes a paste action"

		entrystore, parentpath, paths = actiondata
		iters = [ self.entrystore.get_iter(path) for path in paths ]

		for iter in iters:
			self.entrystore.remove_entry(iter)

		self.tree.unselect_all()


	def __cb_undo_remove(self, name, actiondata):
		"Undoes a remove action"

		iters = []
		for path, entrystore in actiondata:
			parent = self.entrystore.get_iter(path[:-1])
			sibling = self.entrystore.get_iter(path)

			iter = self.entrystore.import_entry(entrystore, entrystore.iter_nth_child(None, 0), parent, sibling)
			iters.append(iter)

		self.tree.select(iters[0])



	##### PRIVATE METHODS #####

	def __check_config(self):
		"Checks if the configuration is correct"

		try:
			self.config.get("launcher/website")
			self.config.get("view/searchbar")
			self.config.get("clipboard/chain_username")
			self.config.get("behavior/doubleclick")
			self.config.get("view/toolbar_style")

			return True

		except config.ConfigError:
			return False


	def __entry_find(self, parent, string, entrytype, direction = data.SEARCH_NEXT):
		"Searches for an entry"

		match = self.entrysearch.find(string, entrytype, self.tree.get_active(), direction)

		if match != None:
			self.tree.select(match)
			self.statusbar.set_status(_('Match found for \'%s\'') % string)

		else:
			self.statusbar.set_status(_('No match found for \'%s\'') % string)
			dialog.Error(parent, _('No match found'), _('The string \'%s\' does not match any entries. Try searching for a different phrase.') % string).run()


	def __file_autosave(self):
		"Autosaves the current file if needed"

		try:
			if self.datafile.get_file() is None or self.datafile.get_password() is None:
				return

			if self.config.get("file/autosave") == False:
				return

			self.datafile.save(self.entrystore, self.datafile.get_file(), self.datafile.get_password())
			self.entrystore.changed = False

		except IOError:
			pass


	def __file_load(self, file, password, datafile = None):
		"Loads data from a data file into an entrystore"

		# We may need to change the datahandler
		old_handler = None

		try:
			if datafile is None:
				datafile = self.datafile

				# Because there are two fileversion we need to check if we are really dealing
				# with version two. If we aren't chances are high, that we are
				# dealing with version one. In this case we use the version one
				# handler and save the file as version two if it is changed, to
				# allow seemless upgrades.
				if datafile.get_handler().detect(io.file_read(file)) != True:
					# Store the datahandler to be reset later on
					old_handler = datafile.get_handler()
					# Load the revelation fileversion one handler
					datafile.set_handler(datahandler.Revelation)
					dialog.Info(self,_('Old file format'), _('Revelation detected that \'%s\' file has the old and actually non-secure file format. It is strongly recommended to save this file with the new format. Revelation will do it automatically if you press save after opening the file.') % file).run()

			while 1:
				try:
					result = datafile.load(file, password, lambda: dialog.PasswordOpen(self, os.path.basename(file)).run())
					break

				except datahandler.PasswordError:
					dialog.Error(self, _('Incorrect password'), _('The password you entered for the file \'%s\' was not correct.') % file).run()

		except datahandler.FormatError:
			self.statusbar.set_status(_('Open failed'))
			dialog.Error(self, _('Invalid file format'), _('The file \'%s\' contains invalid data.') % file).run()

		except ( datahandler.DataError, entry.EntryTypeError, entry.EntryFieldError ):
			self.statusbar.set_status(_('Open failed'))
			dialog.Error(self, _('Unknown data'), _('The file \'%s\' contains unknown data. It may have been created by a newer version of Revelation.') % file).run()

		except datahandler.VersionError:
			self.statusbar.set_status(_('Open failed'))
			dialog.Error(self, _('Unknown data version'), _('The file \'%s\' has a future version number, please upgrade Revelation to open it.') % file).run()

		except datahandler.DetectError:
			self.statusbar.set_status(_('Open failed'))
			dialog.Error(self, _('Unable to detect filetype'), _('The file type of the file \'%s\' could not be automatically detected. Try specifying the file type manually.')% file).run()

		except IOError:
			self.statusbar.set_status(_('Open failed'))
			dialog.Error(self, _('Unable to open file'), _('The file \'%s\' could not be opened. Make sure that the file exists, and that you have permissions to open it.') % file).run()

		# If we switched the datahandlers before we need to switch back to the
		# version2 handler here, to ensure a seemless version upgrade on save
		if old_handler != None:
			datafile.set_handler(old_handler.__class__)

		return result


	def __get_common_usernames(self, e = None):
		"Returns a list of possibly relevant usernames"

		list = []

		if e is not None and e.has_field(entry.UsernameField):
			list.append(e[entry.UsernameField])

		list.append(pwd.getpwuid(os.getuid())[0])
		list.extend(self.entrystore.get_popular_values(entry.UsernameField, 3))

		list = {}.fromkeys(list).keys()
		list.sort()

		return list



	##### PUBLIC METHODS #####

	def about(self):
		"Displays the about dialog"

		dialog.run_unique(dialog.About, self)


	def clip_chain(self, e):
		"Copies all passwords from an entry as a chain"

		if e == None:
			return

		secrets = [ field.value for field in e.fields if field.datatype == entry.DATATYPE_PASSWORD and field.value != "" ]

		if self.config.get("clipboard/chain_username") == True and len(secrets) > 0 and e.has_field(entry.UsernameField) and e[entry.UsernameField] != "":
			secrets.insert(0, e[entry.UsernameField])

		if len(secrets) == 0:
			self.statusbar.set_status(_('Entry has no password to copy'))

		else:
			self.clipboard.set(secrets, True)
			self.statusbar.set_status(_('Password copied to clipboard'))


	def clip_copy(self, iters):
		"Copies entries to the clipboard"

		self.entryclipboard.set(self.entrystore, iters)
		self.statusbar.set_status(_('Entries copied'))


	def clip_cut(self, iters):
		"Cuts entries to the clipboard"

		iters = self.entrystore.filter_parents(iters)
		self.entryclipboard.set(self.entrystore, iters)

		# store undo data (need paths)
		undoactions = []
		for iter in iters:
			undostore = data.EntryStore()
			undostore.import_entry(self.entrystore, iter)
			path = self.entrystore.get_path(iter)
			undoactions.append( ( path, undostore ) )

		# remove data
		for iter in iters:
			self.entrystore.remove_entry(iter)

		self.undoqueue.add_action(
			_('Cut entries'), self.__cb_undo_remove, self.__cb_redo_remove,
			undoactions
		)

		self.__file_autosave()

		self.tree.unselect_all()
		self.statusbar.set_status(_('Entries cut'))


	def clip_paste(self, entrystore, parent):
		"Pastes entries from the clipboard"

		if entrystore == None:
			return

		parent = self.tree.get_active()
		iters = self.entrystore.import_entry(entrystore, None, parent)

		paths = [ self.entrystore.get_path(iter) for iter in iters ]

		self.undoqueue.add_action(
			_('Paste entries'), self.__cb_undo_paste, self.__cb_redo_paste,
			( entrystore, self.entrystore.get_path(parent), paths )
		)

		if len(iters) > 0:
			self.tree.select(iters[0])

		self.statusbar.set_status(_('Entries pasted'))


	def entry_add(self, e = None, parent = None, sibling = None):
		"Adds an entry"

		try:
			if e == None:
				d = dialog.EntryEdit(self, _('Add Entry'), None, self.config, self.clipboard)
				d.set_fieldwidget_data(entry.UsernameField, self.__get_common_usernames())
				e = d.run()

			iter = self.entrystore.add_entry(e, parent, sibling)

			self.undoqueue.add_action(
				_('Add entry'), self.__cb_undo_add, self.__cb_redo_add,
				( self.entrystore.get_path(iter), e.copy() )
			)

			self.__file_autosave()
			self.tree.select(iter)
			self.statusbar.set_status(_('Entry added'))

		except dialog.CancelError:
			self.statusbar.set_status(_('Add entry cancelled'))


	def entry_edit(self, iter):
		"Edits an entry"

		try:
			if iter == None:
				return

			e = self.entrystore.get_entry(iter)

			if type(e) == entry.FolderEntry:
				d = dialog.FolderEdit(self, _('Edit Folder'), e)

			else:
				d = dialog.EntryEdit(self, _('Edit Entry'), e, self.config, self.clipboard)
				d.set_fieldwidget_data(entry.UsernameField, self.__get_common_usernames(e))


			n = d.run()
			self.entrystore.update_entry(iter, n)
			self.tree.select(iter)

			self.undoqueue.add_action(
				_('Update entry'), self.__cb_undo_edit, self.__cb_redo_edit,
				( self.entrystore.get_path(iter), e.copy(), n.copy() )
			)

			self.__file_autosave()
			self.statusbar.set_status(_('Entry updated'))

		except dialog.CancelError:
			self.statusbar.set_status(_('Edit entry cancelled'))


	def entry_find(self):
		"Searches for an entry"

		self.config.set("view/searchbar", True)
		self.searchbar.entry.select_region(0, -1)
		self.searchbar.entry.grab_focus()


	def entry_folder(self, e = None, parent = None, sibling = None):
		"Adds a folder"

		try:
			if e == None:
				e = dialog.FolderEdit(self, _('Add folder')).run()

			iter = self.entrystore.add_entry(e, parent, sibling)

			self.undoqueue.add_action(
				_('Add folder'), self.__cb_undo_add, self.__cb_redo_add,
				( self.entrystore.get_path(iter), e.copy() )
			)

			self.__file_autosave()
			self.tree.select(iter)
			self.statusbar.set_status(_('Folder added'))

		except dialog.CancelError:
			self.statusbar.set_status(_('Add folder cancelled'))


	def entry_goto(self, iters):
		"Goes to an entry"

		for iter in iters:
			try:

				# get goto data for entry
				e = self.entrystore.get_entry(iter)
				command = self.config.get("launcher/%s" % e.id)

				if command in ( "", None ):
					self.statusbar.set_status(_('No goto command found for %s entries') % e.typename)
					return

				subst = {}
				for field in e.fields:
					subst[field.symbol] = field.value

				# copy passwords to clipboard
				chain = []

				for field in e.fields:
					if field.datatype == entry.DATATYPE_PASSWORD and field.value != "":
						chain.append(field.value)

				if self.config.get("clipboard/chain_username") == True and len(chain) > 0 and e.has_field(entry.UsernameField) == True and e[entry.UsernameField] != "" and "%" + entry.UsernameField.symbol not in command:
					chain.insert(0, e[entry.UsernameField])

				self.clipboard.set(chain, True)

				# generate and run goto command
				command = util.parse_subst(command, subst)
				util.execute_child(command)

				self.statusbar.set_status(_('Entry opened'))

			except ( util.SubstFormatError, config.ConfigError ):
				dialog.Error(self, _('Invalid goto command format'), _('The goto command for \'%s\' entries is invalid, please correct it in the preferences.') % e.typename).run()

			except util.SubstValueError:
				dialog.Error(self, _('Missing entry data'), _('The entry \'%s\' does not have all the data required to open it.') % e.name).run()


	def entry_move(self, sourceiters, parent = None, sibling = None):
		"Moves a set of entries"

		if type(sourceiters) != list:
			sourceiters = [ sourceiters ]

		newiters = []
		undoactions = []

		for sourceiter in sourceiters:
			sourcepath = self.entrystore.get_path(sourceiter)
			newiter = self.entrystore.move_entry(sourceiter, parent, sibling)
			newpath = self.entrystore.get_path(newiter)

			undoactions.append( ( sourcepath, newpath ) )
			newiters.append(newiter)

		self.undoqueue.add_action(
			_('Move entry'), self.__cb_undo_move, self.__cb_redo_move,
			undoactions
		)

		if len(newiters) > 0:
			self.tree.select(newiters[0])

		self.__file_autosave()
		self.statusbar.set_status(_('Entries moved'))


	def entry_remove(self, iters):
		"Removes the selected entries"

		try:
			if len(iters) == 0:
				return

			entries = [ self.entrystore.get_entry(iter) for iter in iters ]
			dialog.EntryRemove(self, entries).run()
			iters = self.entrystore.filter_parents(iters)

			# store undo data (need paths)
			undoactions = []
			for iter in iters:
				undostore = data.EntryStore()
				undostore.import_entry(self.entrystore, iter)
				path = self.entrystore.get_path(iter)
				undoactions.append( ( path, undostore ) )

			# remove data
			for iter in iters:
				self.entrystore.remove_entry(iter)

			self.undoqueue.add_action(
				_('Remove entry'), self.__cb_undo_remove, self.__cb_redo_remove,
				undoactions
			)

			self.tree.unselect_all()
			self.__file_autosave()
			self.statusbar.set_status(_('Entries removed'))

		except dialog.CancelError:
			self.statusbar.set_status(_('Entry removal cancelled'))


	def file_change_password(self, password = None):
		"Changes the password of the current data file"

		try:
			if password == None:
				password = dialog.PasswordChange(self, self.datafile.get_password()).run()

			self.datafile.set_password(password)
			self.entrystore.changed = True

			self.__file_autosave()
			self.statusbar.set_status(_('Password changed'))

		except dialog.CancelError:
			self.statusbar.set_status(_('Password change cancelled'))


	def file_export(self):
		"Exports data to a foreign file format"

		try:
			file, handler = dialog.ExportFileSelector(self).run()
			datafile = io.DataFile(handler)

			if datafile.get_handler().encryption == True:
				password = dialog.PasswordSave(self, file).run()

			else:
				dialog.FileSaveInsecure(self).run()
				password = None

			datafile.save(self.entrystore, file, password)
			self.statusbar.set_status(_('Data exported to %s') % datafile.get_file())

		except dialog.CancelError:
			self.statusbar.set_status(_('Export cancelled'))

		except IOError:
			dialog.Error(self, _('Unable to write to file'), _('The file \'%s\' could not be opened for writing. Make sure that you have the proper permissions to write to it.') % file).run()
			self.statusbar.set_status(_('Export failed'))


	def file_import(self):
		"Imports data from a foreign file"

		try:
			file, handler = dialog.ImportFileSelector(self).run()
			datafile = io.DataFile(handler)
			entrystore = self.__file_load(file, None, datafile)

			if entrystore is not None:
				newiters = self.entrystore.import_entry(entrystore, None)
				paths = [ self.entrystore.get_path(iter) for iter in newiters ]

				self.undoqueue.add_action(
					_('Import data'), self.__cb_undo_import, self.__cb_redo_import,
					( paths, entrystore )
				)

				self.statusbar.set_status(_('Data imported from %s') % datafile.get_file())

			self.__file_autosave()

		except dialog.CancelError:
			self.statusbar.set_status(_('Import cancelled'))


	def file_lock(self):
		"Locks the current file"

		if self.datafile.get_file() is None:
			return

		if self.file_locked is True:
			return

		password = self.datafile.get_password()

		if password is None:
			return

		self.locktimer.stop()
		self.bus.remove_signal_receiver(self.__cb_screensaver_lock, signal_name='ActiveChanged', dbus_interface='org.gnome.ScreenSaver')
		self.bus.remove_signal_receiver(self.__cb_screensaver_lock, signal_name='ActiveChanged', dbus_interface='org.freedesktop.ScreenSaver')


		# TODO can this be done more elegantly?
		transients = [ window for window in gtk.window_list_toplevels() if window.get_transient_for() == self ]

		# store current state
		activeiter = self.tree.get_active()
		oldtitle = self.get_title()

		# clear application contents
		self.tree.set_model(None)
		self.entryview.clear()
		self.set_title('[' + _('Locked') + ']')
		self.statusbar.set_status(_('File locked'))
		self.file_locked = True;

		# hide any dialogs
		for window in transients:
			window.hide()

		# lock file
		try:
			d = dialog.PasswordLock(self, password)

			if self.entrystore.changed == True:
				l = ui.ImageLabel(_('Quit disabled due to unsaved changes'), ui.STOCK_WARNING)
				d.contents.pack_start(l)
				d.get_button(1).set_sensitive(False)

			d.run()

		except dialog.CancelError:
			self.quit()

		# unlock the file and restore state
		self.tree.set_model(self.entrystore)
		self.tree.select(activeiter)
		self.set_title(oldtitle)
		self.statusbar.set_status(_('File unlocked'))
		self.file_locked = False;

		for window in transients:
			window.show()

		self.locktimer.start(self.config.get("file/autolock_timeout") * 60)
		self.bus.add_signal_receiver(self.__cb_screensaver_lock, signal_name='ActiveChanged', dbus_interface='org.gnome.ScreenSaver')
		self.bus.add_signal_receiver(self.__cb_screensaver_lock, signal_name='ActiveChanged', dbus_interface='org.freedesktop.ScreenSaver')


	def file_new(self):
		"Opens a new file"

		try:
			if self.entrystore.changed == True and dialog.FileChangesNew(self).run() == True:
				if self.file_save(self.datafile.get_file(), self.datafile.get_password()) == False:
					raise dialog.CancelError

			self.entrystore.clear()
			self.datafile.close()
			self.undoqueue.clear()
			self.statusbar.set_status(_('New file created'))

		except dialog.CancelError:
			self.statusbar.set_status(_('New file cancelled'))


	def file_open(self, file = None, password = None):
		"Opens a data file"

		try:
			if self.entrystore.changed == True and dialog.FileChangesOpen(self).run() == True:
				if self.file_save(self.datafile.get_file(), self.datafile.get_password()) == False:
					raise dialog.CancelError

			if file is None:
				file = dialog.OpenFileSelector(self).run()

			entrystore = self.__file_load(file, password)

			if entrystore is None:
				return

			self.entrystore.clear()
			self.entrystore.import_entry(entrystore, None)
			self.entrystore.changed = False
			self.undoqueue.clear()

			self.file_locked = False;
			self.statusbar.set_status(_('Opened file %s') % self.datafile.get_file())

		except dialog.CancelError:
			self.statusbar.set_status(_('Open cancelled'))


	def file_save(self, file = None, password = None):
		"Saves data to a file"

		try:
			if file is None:
				file = dialog.SaveFileSelector(self).run()

			if password == None:
				password = dialog.PasswordSave(self, file).run()

			self.datafile.save(self.entrystore, file, password)
			self.entrystore.changed = False
			self.statusbar.set_status(_('Data saved to file %s') % file)

			return True

		except dialog.CancelError:
			self.statusbar.set_status(_('Save cancelled'))
			return False

		except IOError:
			dialog.Error(self, _('Unable to save file'), _('The file \'%s\' could not be opened for writing. Make sure that you have the proper permissions to write to it.') % file).run()
			self.statusbar.set_status(_('Save failed'))
			return False


	def prefs(self):
		"Displays the application preferences"

		dialog.run_unique(Preferences, self, self.config)


	def pwcheck(self):
		"Displays the password checking dialog"

		dialog.run_unique(dialog.PasswordChecker, self, self.config, self.clipboard)


	def pwgen(self):
		"Displays the password generator dialog"

		dialog.run_unique(dialog.PasswordGenerator, self, self.config, self.clipboard)


	def quit(self):
		"Quits the application"

		try:
			if self.entrystore.changed == True and dialog.FileChangesQuit(self).run() == True:
				if self.file_save(self.datafile.get_file(), self.datafile.get_password()) == False:
					raise dialog.CancelError

			self.clipboard.clear()
			self.entryclipboard.clear()

			self.__save_state()

			gtk.main_quit()
			sys.exit(0)
			return True

		except dialog.CancelError:
			self.statusbar.set_status(_('Quit cancelled'))
			return False


	def redo(self):
		"Redoes the previous action"

		action = self.undoqueue.get_redo_action()

		if action is None:
			return

		self.undoqueue.redo()
		self.statusbar.set_status(_('%s redone') % action[1])
		self.__file_autosave()


	def run(self):
		"Runs the application"

		if len(sys.argv) > 1:
			file = sys.argv[1]

		elif self.config.get("file/autoload") == True:
			file = self.config.get("file/autoload_file")

		else:
			file = ""


		if file != "":
			self.file_open(io.file_normpath(urllib.unquote(file)))

		gtk.main()


	def undo(self):
		"Undoes the previous action"

		action = self.undoqueue.get_undo_action()

		if action is None:
			return

		self.undoqueue.undo()
		self.statusbar.set_status(_('%s undone') % action[1])
		self.__file_autosave()



class Preferences(dialog.Utility):
	"A preference dialog"

	def __init__(self, parent, cfg):
		dialog.Utility.__init__(self, parent, _('Preferences'))
		self.config = cfg
		self.set_modal(False)

		self.notebook = ui.Notebook()
		self.vbox.pack_start(self.notebook)

		self.page_general = self.notebook.create_page(_('General'))
		self.__init_section_files(self.page_general)
		self.__init_section_password(self.page_general)

		self.page_interface = self.notebook.create_page(_('Interface'))
		self.__init_section_doubleclick(self.page_interface)
		self.__init_section_toolbar(self.page_interface)

		self.page_gotocmd = self.notebook.create_page(_('Goto Commands'))
		self.__init_section_gotocmd(self.page_gotocmd)

		self.connect("response", lambda w,d: self.destroy())


	def __init_section_doubleclick(self, page):
		"Sets up the doubleclick section"

		self.section_doubleclick = page.add_section(_('Doubleclick Action'))

		# radio-button for go to
		self.radio_doubleclick_goto = ui.RadioButton(None, _('Go to account, if possible'))
		ui.config_bind(self.config, "behavior/doubleclick", self.radio_doubleclick_goto, "goto")

		self.radio_doubleclick_goto.set_tooltip_text(_('Go to the account (open in external application) on doubleclick, if required data is filled in'))
		self.section_doubleclick.append_widget(None, self.radio_doubleclick_goto)

		# radio-button for edit
		self.radio_doubleclick_edit = ui.RadioButton(self.radio_doubleclick_goto, _('Edit account'))
		ui.config_bind(self.config, "behavior/doubleclick", self.radio_doubleclick_edit, "edit")

		self.radio_doubleclick_edit.set_tooltip_text(_('Edit the account on doubleclick'))
		self.section_doubleclick.append_widget(None, self.radio_doubleclick_edit)

		# radio-button for copy
		self.radio_doubleclick_copy = ui.RadioButton(self.radio_doubleclick_goto, _('Copy password to clipboard'))
		ui.config_bind(self.config, "behavior/doubleclick", self.radio_doubleclick_copy, "copy")

		self.radio_doubleclick_copy.set_tooltip_text(_('Copy the account password to clipboard on doubleclick'))
		self.section_doubleclick.append_widget(None, self.radio_doubleclick_copy)


	def __init_section_files(self, page):
		"Sets up the files section"

		self.section_files = page.add_section(_('Files'))

		# checkbutton and file button for autoloading a file
		self.check_autoload = ui.CheckButton(_('Open file on startup:'))
		ui.config_bind(self.config, "file/autoload", self.check_autoload)

		self.check_autoload.connect("toggled", lambda w: self.button_autoload_file.set_sensitive(w.get_active()))
		self.check_autoload.set_tooltip_text(_('When enabled, this file will be opened when the program is started'))

		self.button_autoload_file = ui.FileButton(_('Select File to Automatically Open'))
		ui.config_bind(self.config, "file/autoload_file", self.button_autoload_file)
		self.button_autoload_file.set_sensitive(self.check_autoload.get_active())

		eventbox = ui.EventBox(self.button_autoload_file)
		eventbox.set_tooltip_text(_('File to open when Revelation is started'))

		hbox = ui.HBox()
		hbox.pack_start(self.check_autoload, False, False)
		hbox.pack_start(eventbox)
		self.section_files.append_widget(None, hbox)

		# check-button for autosave
		self.check_autosave = ui.CheckButton(_('Automatically save data when changed'))
		ui.config_bind(self.config, "file/autosave", self.check_autosave)

		self.check_autosave.set_tooltip_text(_('Automatically save the data file when an entry is added, modified or removed'))
		self.section_files.append_widget(None, self.check_autosave)

		# autolock file
		self.check_autolock = ui.CheckButton(_('Lock file when inactive for'))
		ui.config_bind(self.config, "file/autolock", self.check_autolock)
		self.check_autolock.connect("toggled", lambda w: self.spin_autolock_timeout.set_sensitive(w.get_active()))
		self.check_autolock.set_tooltip_text(_('Automatically lock the data file after a period of inactivity'))

		self.spin_autolock_timeout = ui.SpinEntry()
		self.spin_autolock_timeout.set_range(1, 120)
		self.spin_autolock_timeout.set_sensitive(self.check_autolock.get_active())
		ui.config_bind(self.config, "file/autolock_timeout", self.spin_autolock_timeout)
		self.spin_autolock_timeout.set_tooltip_text(_('The period of inactivity before locking the file, in minutes'))

		hbox = ui.HBox()
		hbox.set_spacing(3)
		hbox.pack_start(self.check_autolock, False, False)
		hbox.pack_start(self.spin_autolock_timeout, False, False)
		hbox.pack_start(ui.Label(_('minutes')))
		self.section_files.append_widget(None, hbox)


	def __init_section_gotocmd(self, page):
		"Sets up the goto command section"

		self.section_gotocmd = page.add_section(_('Goto Commands'))

		for entrytype in entry.ENTRYLIST:
			if entrytype == entry.FolderEntry:
				continue

			e = entrytype()

			widget = ui.Entry()
			ui.config_bind(self.config, "launcher/%s" % e.id, widget)

			tooltip = _('Goto command for %s accounts. The following expansion variables can be used:') % e.typename + "\n\n"

			for field in e.fields:
				tooltip += "%%%s: %s\n" % ( field.symbol, field.name )

			tooltip += "\n"
			tooltip += _('%%: a "%" sign') + "\n"
			tooltip += _('%?x: optional expansion variable') + "\n"
			tooltip += _('%(...%): optional substring expansion')

			widget.set_tooltip_text(tooltip)
			self.section_gotocmd.append_widget(e.typename, widget)


	def __init_section_password(self, page):
		"Sets up the password section"

		self.section_password = page.add_section(_('Passwords'))

		# show passwords checkbutton
		self.check_show_passwords = ui.CheckButton(_('Display passwords and other secrets'))
		ui.config_bind(self.config, "view/passwords", self.check_show_passwords)

		self.check_show_passwords.set_tooltip_text(_('Display passwords and other secrets, such as PIN codes (otherwise, hide with ******)'))
		self.section_password.append_widget(None, self.check_show_passwords)

		# chain username checkbutton
		self.check_chain_username = ui.CheckButton(_('Also copy username when copying password'))
		ui.config_bind(self.config, "clipboard/chain_username", self.check_chain_username)

		self.check_chain_username.set_tooltip_text(_('When the password is copied to clipboard, put the username before the password as a clipboard "chain"'))
		self.section_password.append_widget(None, self.check_chain_username)

		# use punctuation chars checkbutton
		self.check_punctuation_chars = ui.CheckButton(_('Use punctuation characters for passwords'))
		ui.config_bind(self.config, "passwordgen/punctuation", self.check_punctuation_chars)

		self.check_punctuation_chars.set_tooltip_text(_('When passwords are generated, use punctuation characters like %, =, { or .'))
		self.section_password.append_widget(None, self.check_punctuation_chars)

		# password length spinbutton
		self.spin_pwlen = ui.SpinEntry()
		self.spin_pwlen.set_range(4, 32)
		ui.config_bind(self.config, "passwordgen/length", self.spin_pwlen)

		self.spin_pwlen.set_tooltip_text(_('The number of characters in generated passwords - 8 or more are recommended'))
		self.section_password.append_widget(_('Length of generated passwords'), self.spin_pwlen)


	def __init_section_toolbar(self, page):
		"Sets up the toolbar section"

		self.section_toolbar = page.add_section(_('Toolbar Style'))

		# radio-button for desktop default
		self.radio_toolbar_desktop = ui.RadioButton(None, _('Use desktop default'))
		ui.config_bind(self.config, "view/toolbar_style", self.radio_toolbar_desktop, "desktop")

		self.radio_toolbar_desktop.set_tooltip_text(_('Show toolbar items with default style'))
		self.section_toolbar.append_widget(None, self.radio_toolbar_desktop)

		# radio-button for icons and text
		self.radio_toolbar_both = ui.RadioButton(self.radio_toolbar_desktop, _('Show icons and text'))
		ui.config_bind(self.config, "view/toolbar_style", self.radio_toolbar_both, "both")

		self.radio_toolbar_both.set_tooltip_text(_('Show toolbar items with both icons and text'))
		self.section_toolbar.append_widget(None, self.radio_toolbar_both)

		# radio-button for icons and important text
		self.radio_toolbar_bothhoriz = ui.RadioButton(self.radio_toolbar_desktop, _('Show icons and important text'))
		ui.config_bind(self.config, "view/toolbar_style", self.radio_toolbar_bothhoriz, "both-horiz")

		self.radio_toolbar_bothhoriz.set_tooltip_text(_('Show toolbar items with text beside important icons'))
		self.section_toolbar.append_widget(None, self.radio_toolbar_bothhoriz)

		# radio-button for icons only
		self.radio_toolbar_icons = ui.RadioButton(self.radio_toolbar_desktop, _('Show icons only'))
		ui.config_bind(self.config, "view/toolbar_style", self.radio_toolbar_icons, "icons")

		self.radio_toolbar_icons.set_tooltip_text(_('Show toolbar items with icons only'))
		self.section_toolbar.append_widget(None, self.radio_toolbar_icons)

		# radio-button for text only
		self.radio_toolbar_text = ui.RadioButton(self.radio_toolbar_desktop, _('Show text only'))
		ui.config_bind(self.config, "view/toolbar_style", self.radio_toolbar_text, "text")

		self.radio_toolbar_text.set_tooltip_text(_('Show toolbar items with text only'))
		self.section_toolbar.append_widget(None, self.radio_toolbar_text)


	def run(self):
		"Runs the preference dialog"

		self.show_all()

		if dialog.EVENT_FILTER != None:
			self.window.add_filter(dialog.EVENT_FILTER)

		# for some reason, gtk crashes on close-by-escape unless we do this
		self.get_button(0).grab_focus()
		self.notebook.grab_focus()



if __name__ == "__main__":
	app = Revelation()
	app.run()

