#!/usr/bin/python3

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

import gettext
import locale
import os
import pwd
import sys
import urllib.parse
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio, GLib, GObject  # noqa: E402
from revelation import config, data, datahandler, dialog, entry, io, ui, util  # noqa: E402

_ = gettext.gettext


class Revelation(ui.App):
    "The Revelation application"

    def __init__(self):
        sys.excepthook = self.__cb_exception
        os.umask(0o077)

        gettext.bindtextdomain(config.PACKAGE, config.DIR_LOCALE)
        gettext.textdomain(config.PACKAGE)

        # Gtk.Builder uses the C lib's locale API, accessible with the locale module
        locale.bindtextdomain(config.PACKAGE, config.DIR_LOCALE)
        locale.bind_textdomain_codeset(config.PACKAGE, "UTF-8")

        ui.App.__init__(self, config.APPNAME)
        self.window = None

        resource_path = os.path.join(config.DIR_UI, 'revelation.gresource')
        resource = Gio.Resource.load(resource_path)
        resource._register()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # Icon is set via desktop file, but we can also set it programmatically
        try:
            Gtk.Application.set_icon_name(self, "info.olasagasti.revelation")
        except AttributeError:
            # Fallback if method not available
            pass
        if not self.window:
            self.window = ui.AppWindow(application=self, title="Revelation")
            self.main_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
            self.window.set_child(self.main_vbox)
        self.add_window(self.window)

    def do_activate(self):

        # Load menubar as GMenu from resource
        menubar_builder = Gtk.Builder()
        menubar_builder.add_from_resource('/info/olasagasti/revelation/ui/menubar.ui')
        self.menubar = menubar_builder.get_object('menubar')

        self.popupbuilder = Gtk.Builder()
        self.popupbuilder.add_from_resource('/info/olasagasti/revelation/ui/popup-tree.ui')
        self.popupmenu = self.popupbuilder.get_object("popup-tree")

        if self.window:
            self.window.connect("close-request", self.__cb_quit)

        try:
            self.__init_config()
            self.__init_actions()
            self.__init_facilities()
            self.__init_ui()
            self.__init_states()
            self.__init_dbus()

        except IOError:
            dialog.Error(self.window, _('Missing data files'), _('Some of Revelations system files could not be found, please reinstall Revelation.')).run()
            sys.exit(1)

        except config.ConfigError:
            dialog.Error(self.window, _('Missing configuration data'), _('Revelation could not find its configuration data, please reinstall Revelation.')).run()
            sys.exit(1)

        except ui.DataError:
            dialog.Error(self.window, _('Invalid data files'), _('Some of Revelations system files contain invalid data, please reinstall Revelation.')).run()
            sys.exit(1)

        if len(sys.argv) > 1:
            file = sys.argv[1]

        elif self.config.get_boolean("file-autoload"):
            file = self.config.get_string("file-autoload-file")

        else:
            file = ""

        if file != "":
            self.file_open(io.file_normpath(urllib.parse.unquote(file)))

        # Present the window to make it visible
        if self.window:
            self.window.present()

    def __init_config(self):
        "Get configuration schema"

        schema_source = Gio.SettingsSchemaSource.get_default()
        rvl_schema = schema_source.lookup('org.revelation', recursive=True)

        if not rvl_schema:
            schema_source = Gio.SettingsSchemaSource.new_from_directory(config.DIR_GSCHEMAS, schema_source, False)
            rvl_schema = schema_source.lookup('org.revelation', recursive=True)

        if not rvl_schema:
            raise config.ConfigError

        rvl_settings = Gio.Settings.new_full(rvl_schema, None, None)
        self.config = rvl_settings

    def __init_actions(self):
        "Sets up actions"

        # set up placeholders
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("placeholder", group)
        self._action_groups = {"placeholder": group}

        action_menu_edit  = Gio.SimpleAction.new("menu-edit",  None)
        action_menu_entry = Gio.SimpleAction.new("menu-entry", None)
        action_menu_file  = Gio.SimpleAction.new("menu-file",  None)
        action_menu_help  = Gio.SimpleAction.new("menu-help",  None)
        action_menu_view  = Gio.SimpleAction.new("menu-view",  None)
        action_popup_tree = Gio.SimpleAction.new("popup-tree", None)
        group.add_action(action_menu_edit)
        group.add_action(action_menu_entry)
        group.add_action(action_menu_file)
        group.add_action(action_menu_help)
        group.add_action(action_menu_view)
        group.add_action(action_popup_tree)

        # set up dynamic actions
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("dynamic", group)
        self._action_groups["dynamic"] = group

        action = Gio.SimpleAction.new("clip-paste", None)
        action.connect("activate",      self.__cb_clip_paste)
        group.add_action(action)

        action = Gio.SimpleAction.new("entry-goto", None)
        action.connect("activate", lambda w, k: self.entry_goto(self.tree.get_selected()))
        group.add_action(action)

        action = Gio.SimpleAction.new("redo", None)
        action.connect("activate", lambda w, k: self.redo())
        group.add_action(action)

        action = Gio.SimpleAction.new("undo", None)
        action.connect("activate", lambda w, k: self.undo())
        group.add_action(action)

        # set up group for multiple entries
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("entry-multiple", group)
        self._action_groups["entry-multiple"] = group

        action = Gio.SimpleAction.new("clip-copy", None)
        action.connect("activate",      self.__cb_clip_copy)
        group.add_action(action)

        action = Gio.SimpleAction.new("clip-chain", None)
        action.connect("activate", lambda w, k: self.clip_chain(self.entrystore.get_entry(self.tree.get_active())))
        group.add_action(action)

        action = Gio.SimpleAction.new("clip-cut", None)
        action.connect("activate",      self.__cb_clip_cut)
        group.add_action(action)

        action = Gio.SimpleAction.new("entry-remove", None)
        action.connect("activate", lambda w, k: self.entry_remove(self.tree.get_selected()))
        group.add_action(action)

        # action group for "optional" entries
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("entry-optional", group)
        self._action_groups["entry-optional"] = group

        action = Gio.SimpleAction.new("entry-add", None)
        action.connect("activate", lambda w, k: self.entry_add(None, self.tree.get_active()))
        group.add_action(action)

        action = Gio.SimpleAction.new("entry-folder", None)
        action.connect("activate", lambda w, k: self.entry_folder(None, self.tree.get_active()))
        group.add_action(action)

        # action group for single entries
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("entry-single", group)
        self._action_groups["entry-single"] = group

        action = Gio.SimpleAction.new("entry-edit", None)
        action.connect("activate", lambda w, k: self.entry_edit(self.tree.get_active()))
        group.add_action(action)

        # action group for existing file
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("file-exists", group)
        self._action_groups["file-exists"] = group

        action = Gio.SimpleAction.new("file-lock", None)
        action.connect("activate", lambda w, k: self.file_lock())
        group.add_action(action)

        # action group for searching
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("find", group)
        self._action_groups["find"] = group

        action = Gio.SimpleAction.new("find-next", None)
        action.connect("activate", lambda w, k: self.__entry_find(self, self.searchbar.entry.get_text(), self.searchbar.dropdown.get_active_type(), data.SEARCH_NEXT))
        group.add_action(action)

        action = Gio.SimpleAction.new("find-previous", None)
        action.connect("activate", lambda w, k: self.__entry_find(self, self.searchbar.entry.get_text(), self.searchbar.dropdown.get_active_type(), data.SEARCH_PREVIOUS))
        group.add_action(action)

        # global action group
        group = Gio.SimpleActionGroup()
        self.window.insert_action_group("file", group)
        self._action_groups["file"] = group

        action = Gio.SimpleAction.new("file-change-password", None)
        action.connect("activate", lambda w, k: self.file_change_password())
        group.add_action(action)

        action = Gio.SimpleAction.new("file-close", None)
        action.connect("activate",      self.__cb_close)
        group.add_action(action)

        action = Gio.SimpleAction.new("file-export", None)
        action.connect("activate", lambda w, k: self.file_export())
        group.add_action(action)

        action = Gio.SimpleAction.new("file-import", None)
        action.connect("activate", lambda w, k: self.file_import())
        group.add_action(action)

        action = Gio.SimpleAction.new("file-new", None)
        action.connect("activate", lambda w, k: self.file_new())
        group.add_action(action)

        action = Gio.SimpleAction.new("file-open", None)
        action.connect("activate", lambda w, k: self.file_open())
        group.add_action(action)

        action = Gio.SimpleAction.new("file-save", None)
        action.connect("activate", lambda w, k: self.file_save(self.datafile.get_file(), self.datafile.get_password()))
        group.add_action(action)

        action = Gio.SimpleAction.new("file-save-as", None)
        action.connect("activate", lambda w, k: self.file_save(None, None))
        group.add_action(action)

        action = Gio.SimpleAction.new("find", None)
        action.connect("activate", lambda w, k: self.entry_find())
        group.add_action(action)

        action = Gio.SimpleAction.new("help-about", None)
        action.connect("activate", lambda w, k: self.about())
        group.add_action(action)

        action = Gio.SimpleAction.new("prefs", None)
        action.connect("activate", lambda w, k: self.prefs())
        group.add_action(action)

        action = Gio.SimpleAction.new("pwchecker", None)
        action.connect("activate", lambda w, k: self.pwcheck())
        group.add_action(action)

        action = Gio.SimpleAction.new("pwgenerator", None)
        action.connect("activate", lambda w, k: self.pwgen())
        group.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate",      self.__cb_quit)
        group.add_action(action)

        action = Gio.SimpleAction.new("select-all", None)
        action.connect("activate", lambda w, k: self.tree.select_all())
        group.add_action(action)

        action = Gio.SimpleAction.new("select-none", None)
        action.connect("activate", lambda w, k: self.tree.unselect_all())
        group.add_action(action)

        action_vp = Gio.SimpleAction.new_stateful("view-passwords", None, GLib.Variant.new_boolean(self.config.get_boolean("view-passwords")))
        action_vp.connect("activate", lambda w, k: action_vp.set_state(GLib.Variant.new_boolean(not action_vp.get_state())))
        action_vp.connect("activate", lambda w, k: self.config.set_boolean("view-passwords", action_vp.get_state()))
        self.config.connect("changed::view-passwords", lambda w, k: action_vp.set_state(GLib.Variant.new_boolean(w.get_boolean(k))))
        group.add_action(action_vp)

        action_vs = Gio.SimpleAction.new_stateful("view-searchbar", None, GLib.Variant.new_boolean(True))
        action_vs.connect("activate", lambda w, k: action_vs.set_state(GLib.Variant.new_boolean(not action_vs.get_state())))
        action_vs.connect("activate", lambda w, k: self.config.set_boolean("view-searchbar", action_vs.get_state()))
        action_vs.connect("activate", lambda w, k: self.searchbar.set_visible(GLib.Variant.new_boolean(action_vs.get_state())))
        self.config.connect("changed::view-searchbar", lambda w, k: action_vs.set_state(GLib.Variant.new_boolean(w.get_boolean(k))))
        self.config.connect("changed::view-searchbar", lambda w, k: self.searchbar.set_visible(GLib.Variant.new_boolean(w.get_boolean(k))))
        group.add_action(action_vs)

        action_va = Gio.SimpleAction.new_stateful("view-statusbar", None, GLib.Variant.new_boolean(True))
        action_va.connect("activate", lambda w, k: action_va.set_state(GLib.Variant.new_boolean(not action_va.get_state())))
        action_va.connect("activate", lambda w, k: self.config.set_boolean("view-statusbar", action_va.get_state()))
        action_va.connect("activate", lambda w, k: self.statusbar.set_visible(GLib.Variant.new_boolean(action_va.get_state())))
        self.config.connect("changed::view-statusbar", lambda w, k: action_va.set_state(GLib.Variant.new_boolean(w.get_boolean(k))))
        self.config.connect("changed::view-statusbar", lambda w, k: self.statusbar.set_visible(GLib.Variant.new_boolean(w.get_boolean(k))))
        group.add_action(action_va)

        action_vt = Gio.SimpleAction.new_stateful("view-toolbar", None, GLib.Variant.new_boolean(True))
        action_vt.connect("activate", lambda w, k: action_vt.set_state(GLib.Variant.new_boolean(not action_vt.get_state())))
        action_vt.connect("activate", lambda w, k: self.config.set_boolean("view-toolbar", action_vt.get_state()))
        action_vt.connect("activate", lambda w, k: self.toolbar.set_visible(GLib.Variant.new_boolean(action_vt.get_state())))
        self.config.connect("changed::view-toolbar", lambda w, k: action_vt.set_state(GLib.Variant.new_boolean(w.get_boolean(k))))
        self.config.connect("changed::view-toolbar", lambda w, k: self.toolbar.set_visible(GLib.Variant.new_boolean(w.get_boolean(k))))
        self.config.connect("changed::view-toolbar-style", lambda w, k: self.__cb_config_toolbar_style(w, w.get_string(k)))
        group.add_action(action_vt)

    def __init_facilities(self):
        "Sets up various facilities"

        self.clipboard      = data.Clipboard()
        self.datafile       = io.DataFile(datahandler.Revelation2)
        self.entryclipboard = data.EntryClipboard()
        self.entrystore     = data.EntryStore()
        self.entrysearch    = data.EntrySearch(self.entrystore)
        display = Gdk.Display.get_default()
        self.items = Gtk.IconTheme.get_for_display(display)
        self.locktimer      = data.Timer()
        self.undoqueue      = data.UndoQueue()

        self.datafile.connect("changed", lambda w, f: self.__state_file(f))
        self.datafile.connect("content-changed", self.__cb_file_content_changed)
        self.entryclipboard.connect("content-toggled", lambda w, d: self.__state_clipboard(d))
        self.locktimer.connect("ring", self.__cb_file_autolock)
        self.undoqueue.connect("changed", lambda w: self.__state_undo(self.undoqueue.get_undo_action(), self.undoqueue.get_redo_action()))

        self.config.connect("changed::file-autolock-timeout", lambda w, k: self.locktimer.start(60 * w.get_int(k)))
        if self.config.get_boolean("file-autolock"):
            self.locktimer.start(60 * self.config.get_int("file-autolock-timeout"))

    def __init_states(self):
        "Sets the initial application state"

        # set window states
        self.window.set_default_size(
            self.config.get_int("view-window-width"),
            self.config.get_int("view-window-height")
        )

        self.hpaned.set_position(
            self.config.get_int("view-pane-position")
        )

        # bind ui widgets to config keys
        bind = {
            "view-passwords": "/menubar/menu-view/view-passwords",
            "view-searchbar": "/menubar/menu-view/view-searchbar",
            "view-statusbar": "/menubar/menu-view/view-statusbar",
            "view-toolbar": "/menubar/menu-view/view-toolbar"
        }

        for key in bind.keys():
            action = self._action_groups["file"].lookup_action(key)
            if action:
                action.set_state(self.config.get_value(key))


        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.__cb_lock_timer_reset)
        self.window.add_controller(key_controller)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.set_button(0)  # All buttons
        click_gesture.connect("pressed", self.__cb_lock_timer_reset_click)
        self.window.add_controller(click_gesture)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("motion", self.__cb_lock_timer_reset_motion)
        self.window.add_controller(motion_controller)

        self.file_locked = False

        # set some variables
        self.entrysearch.string = ''
        self.entrysearch.type   = None

        # set ui widget states
        self.__state_clipboard(self.entryclipboard.has_contents())
        self.__state_entry([])
        self.__state_file(None)
        self.__state_find(self.searchbar.entry.get_text())
        self.__state_undo(None, None)

        # set states from config
        self.searchbar.set_visible(self.config.get_boolean("view-searchbar"))
        self.statusbar.set_visible(self.config.get_boolean("view-statusbar"))
        self.toolbar.set_visible(self.config.get_boolean("view-toolbar"))
        self.__cb_config_toolbar_style(self.config, self.config.get_string("view-toolbar-style"))

        # give focus to searchbar entry if shown
        if self.searchbar.get_property("visible"):
            self.searchbar.entry.grab_focus()

    def __init_ui(self):
        "Sets up the UI"

        # add custom icons path
        display = Gdk.Display.get_default()
        _icon_theme = Gtk.IconTheme.get_for_display(display)
        if _icon_theme is not None:
            _icon_theme.add_search_path(config.DIR_ICONS)

        # set up toolbar and menus
        self.set_menubar(self.menubar)

        # Load toolbar from UI file
        toolbarbuilder = Gtk.Builder()
        toolbarbuilder.add_from_resource('/info/olasagasti/revelation/ui/toolbar.ui')
        self.toolbar = toolbarbuilder.get_object('toolbar')

        # Connect toolbar button signals
        open_item = toolbarbuilder.get_object('open_item')
        open_item.connect('clicked', lambda k: self._action_groups["file"].lookup_action("file-open").activate())

        save_item = toolbarbuilder.get_object('save_item')
        save_item.connect('clicked', lambda k: self._action_groups["file"].lookup_action("file-save").activate())

        addentry_item = toolbarbuilder.get_object('addentry_item')
        addentry_item.connect('clicked', lambda k: self._action_groups["entry-optional"].lookup_action("entry-add").activate())

        addfolder_item = toolbarbuilder.get_object('addfolder_item')
        addfolder_item.connect('clicked', lambda k: self._action_groups["entry-optional"].lookup_action("entry-folder").activate())

        gotoentry_item = toolbarbuilder.get_object('gotoentry_item')
        gotoentry_item.connect('clicked', lambda k: self._action_groups["dynamic"].lookup_action("entry-goto").activate())

        editentry_item = toolbarbuilder.get_object('editentry_item')
        editentry_item.connect('clicked', lambda k: self._action_groups["entry-single"].lookup_action("entry-edit").activate())

        removeentry_item = toolbarbuilder.get_object('removeentry_item')
        removeentry_item.connect('clicked', lambda k: self._action_groups["entry-multiple"].lookup_action("entry-remove").activate())

        self.add_toolbar(self.toolbar, "toolbar", 1)

        self.searchbar = ui.Searchbar()
        self.add_toolbar(self.searchbar, "searchbar", 2)

        # set up main application widgets
        self.tree = ui.EntryTree(self.entrystore)
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_child(self.tree)

        self.entryview = ui.EntryView(self.config, self.clipboard)
        self.entryview.set_halign(Gtk.Align.CENTER)
        self.entryview.set_valign(Gtk.Align.CENTER)
        self.entryview.set_hexpand(True)

        self.hpaned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.hpaned.set_start_child(self.scrolledwindow)
        self.hpaned.set_resize_start_child(True)
        self.hpaned.set_end_child(self.entryview)
        self.hpaned.set_resize_end_child(True)
        ui.apply_css_padding(self.hpaned, 6)
        self.set_contents(self.hpaned)

        self.statusbar = ui.Statusbar()
        self.statusbar.set_vexpand(True)
        self.main_vbox.append(self.statusbar)

        # set up drag-and-drop
        # Window drop target for file drops (supports both Gio.File and text/uri-list)
        window_drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY | Gdk.DragAction.MOVE | Gdk.DragAction.LINK)
        window_drop_target.set_gtypes([Gio.File, GObject.TYPE_STRING])
        window_drop_target.connect("drop", self.__cb_window_drop)
        self.window.add_controller(window_drop_target)

        # TreeView drop target for tree row drops
        # Store selected iters when drag begins, use in drop handler
        self.__drag_selected_iters = None
        formats = Gdk.ContentFormats.parse("revelation/treerow")
        tree_drop_target = Gtk.DropTargetAsync.new(formats, Gdk.DragAction.MOVE)
        tree_drop_target.connect("drop", self.__cb_tree_drop_async)
        self.tree.add_controller(tree_drop_target)

        # TreeView drag source for tree row drags
        tree_drag_source = Gtk.DragSource.new()
        tree_drag_source.set_actions(Gdk.DragAction.MOVE)
        tree_drag_source.connect("prepare", self.__cb_tree_drag_prepare)
        tree_drag_source.connect("drag-begin", self.__cb_tree_drag_begin)
        self.tree.add_controller(tree_drag_source)

        # set up callbacks
        searchbar_key_controller = Gtk.EventControllerKey.new()
        searchbar_key_controller.connect("key-pressed", self.__cb_searchbar_key_press)
        self.searchbar.entry.add_controller(searchbar_key_controller)

        self.searchbar.button_next.connect("clicked", self.__cb_searchbar_button_clicked, data.SEARCH_NEXT)
        self.searchbar.button_prev.connect("clicked", self.__cb_searchbar_button_clicked, data.SEARCH_PREVIOUS)
        self.searchbar.entry.connect("changed", lambda w: self.__state_find(self.searchbar.entry.get_text()))

        self.tree.connect("popup", lambda w, d: self.popup(self.popupmenu, d.button, 0))
        self.tree.connect("doubleclick", self.__cb_tree_doubleclick)
        self.tree.selection.connect("changed", lambda w: self.entryview.display_entry(self.entrystore.get_entry(self.tree.get_active())))
        self.tree.selection.connect("changed", lambda w: self.__state_entry(self.tree.get_selected()))

    def __init_dbus(self):
        app = Gio.Application.get_default
        self.dbus_subscription_id = app().get_dbus_connection().signal_subscribe(None, "org.gnome.ScreenSaver", "ActiveChanged", "/org/gnome/ScreenSaver", None, Gio.DBusSignalFlags.NONE, self.__cb_screensaver_lock)

    # STATE HANDLERS #

    def __save_state(self):
        "Saves the current application state"

        width = self.window.get_width()
        height = self.window.get_height()
        self.config.set_int("view-window-width", width)
        self.config.set_int("view-window-height", height)

        # GTK4: get_position() removed, use get_surface() to get position if needed
        # For now, skip saving position as it's not critical
        # surface = self.window.get_surface()
        # if surface:
        #     x, y = surface.get_position()
        #     self.config.set_int("view-window-position-x", x)
        #     self.config.set_int("view-window-position-y", y)

        if hasattr(self, 'hpaned') and self.hpaned is not None:
            self.config.set_int("view-pane-position", self.hpaned.get_position())
        self.config.sync()

    def __state_clipboard(self, has_contents):
        "Sets states based on the clipboard contents"

        self._action_groups["dynamic"].lookup_action("clip-paste").set_enabled(has_contents)

    def __state_entry(self, iters):
        "Sets states for entry-dependant ui items"

        # widget sensitivity based on number of entries
        for action in self._action_groups["entry-multiple"].list_actions():
            self._action_groups["entry-multiple"].lookup_action(action).set_enabled(len(iters) > 0)
        for action in self._action_groups["entry-single"].list_actions():
            self._action_groups["entry-single"].lookup_action(action).set_enabled(len(iters) == 1)
        for action in self._action_groups["entry-optional"].list_actions():
            self._action_groups["entry-optional"].lookup_action(action).set_enabled(len(iters) < 2)

        # copy password sensitivity
        s = False

        for iter in iters:
            e = self.entrystore.get_entry(iter)

            for f in e.fields:
                if f.datatype == entry.DATATYPE_PASSWORD and f.value != "":
                    s = True

        self._action_groups["entry-multiple"].lookup_action("clip-chain").set_enabled(s)

        # goto sensitivity
        try:
            for iter in iters:
                e = self.entrystore.get_entry(iter)

                if (e.id == "folder"):
                    continue

                if self.config.get_string("launcher-%s" % e.id) not in ("", None):
                    s = True
                    break

            else:
                s = False

        except config.ConfigError:
            s = False

        self._action_groups["dynamic"].lookup_action("entry-goto").set_enabled(s)

    def __state_file(self, file):
        "Sets states based on file"

        for action in self._action_groups["file-exists"].list_actions():
            self._action_groups["file-exists"].lookup_action(action).set_enabled(file is not None)

        if file is not None:
            self.window.set_title(io.file_get_display_name(file))

            # Note: os.chdir() is deprecated for GTK apps and can break portal sandbox semantics
            # We keep it for backward compatibility with relative paths, but only for local file:// URIs
            if io.file_is_local(file):
                if file and not file.startswith("file://"):
                    # It's a plain path
                    try:
                        os.chdir(os.path.dirname(file))
                    except (OSError, ValueError):
                        pass  # Ignore chdir errors (e.g., file in root, deleted parent dir)
                elif file and file.startswith('file://'):
                    # Extract path from file:// URI
                    try:
                        gfile = Gio.File.new_for_uri(file)
                        parent = gfile.get_parent()
                        if parent:
                            parent_path = parent.get_path()
                            if parent_path:
                                os.chdir(parent_path)
                    except (GLib.GError, OSError, ValueError):
                        pass  # Ignore chdir errors

        else:
            self.window.set_title('[' + _('New file') + ']')

    def __state_find(self, string):
        "Sets states based on the current search string"

        for action in self._action_groups["find"].list_actions():
            self._action_groups["find"].lookup_action(action).set_enabled(string != "")

    def __state_undo(self, undoaction, redoaction):
        "Sets states based on undoqueue actions"

        if undoaction is None:
            s, l = False, _('_Undo')

        else:
            s, l = True, _('_Undo %s') % undoaction[1].lower()

        action = self._action_groups["dynamic"].lookup_action("undo")
        action.set_enabled(s)
        # TODO action.set_property("label", l)

        if redoaction is None:
            s, l = False, _('_Redo')

        else:
            s, l = True, _('_Redo %s') % redoaction[1].lower()

        action = self._action_groups["dynamic"].lookup_action("redo")
        action.set_enabled(s)
        # TODO action.set_property("label", l)

    # MISC CALLBACKS #

    def __cb_clip_copy(self, widget, data = None):
        "Handles copying to the clipboard"

        focuswidget = self.window.get_focus()

        if focuswidget is self.tree:
            self.clip_copy(self.tree.get_selected())

        elif isinstance(focuswidget, Gtk.Label) or isinstance(focuswidget, Gtk.Entry):
            focuswidget.emit("copy-clipboard")

    def __cb_clip_cut(self, widget, data = None):
        "Handles cutting to clipboard"

        focuswidget = self.window.get_focus()

        if focuswidget is self.tree:
            self.clip_cut(self.tree.get_selected())

        elif isinstance(focuswidget, Gtk.Entry):
            focuswidget.emit("cut-clipboard")

    def __cb_clip_paste(self, widget, data = None):
        "Handles pasting from clipboard"

        focuswidget = self.window.get_focus()

        if focuswidget is self.tree:
            self.clip_paste(self.entryclipboard.get(), self.tree.get_active())

        elif isinstance(focuswidget, Gtk.Entry):
            focuswidget.emit("paste-clipboard")

    def __cb_window_drop(self, drop_target, value, x, y, userdata = None):
        "Handles file drops on window"

        if value is None:
            return False

        if isinstance(value, Gio.File):
            self.file_open(value.get_path())
            return True
        elif isinstance(value, str):
            # Handle text/uri-list format
            uris = [uri.strip() for uri in value.split("\n") if uri.strip()]
            if len(uris) > 0:
                # Convert URI to file path
                if uris[0].startswith("file://"):
                    file_path = urllib.parse.unquote(uris[0][7:])
                    self.file_open(file_path)
                    return True

        return False

    def __cb_lock_timer_reset(self, controller, keyval, keycode, state):
        "Reset lock timer on key press"
        self.locktimer.reset()
        return False

    def __cb_lock_timer_reset_click(self, gesture, n_press, x, y):
        "Reset lock timer on button press"
        self.locktimer.reset()

    def __cb_lock_timer_reset_motion(self, controller, x, y):
        "Reset lock timer on motion"
        self.locktimer.reset()

    def __cb_exception(self, type, value, trace):
        "Callback for unhandled exceptions"

        if type == KeyboardInterrupt:
            sys.exit(1)

        traceback = util.trace_exception(type, value, trace)
        sys.stderr.write(traceback)

        if dialog.Exception(self.window, traceback).run():
            pass

        else:
            sys.exit(1)

    def __cb_file_content_changed(self, widget, file):
        "Callback for changed file"

        try:
            # 'file' parameter is already a display name (emitted by DataFile)
            if dialog.FileChanged(self.window, file).run():
                self.file_open(self.datafile.get_file(), self.datafile.get_password())

        except dialog.CancelError:
            self.statusbar.set_status(_('Open cancelled'))

    def __cb_file_autolock(self, widget, data = None):
        "Callback for locking the file"

        if self.config.get_boolean("file-autolock"):
            self.file_lock()

    def __cb_screensaver_lock(self, connection, unique_name, object_path, interface, signal, state):
        if state[0] and self.config.get_boolean("file-autolock"):
            self.file_lock()

    def __cb_quit(self, widget, data = None):
        "Callback for quit"

        if not self.quit():
            return True

        else:
            return False

    def __cb_close(self, widget, data = None):
        "Callback for Close"

        if not self.file_close():
            return True

        else:
            return False

    def __cb_searchbar_button_clicked(self, widget, direction = data.SEARCH_NEXT):
        "Callback for searchbar button clicks"

        self.__entry_find(self, self.searchbar.entry.get_text(), self.searchbar.dropdown.get_active_type(), direction)
        self.searchbar.entry.select_region(0, -1)

    def __cb_searchbar_key_press(self, controller, keyval, keycode, state):
        "Callback for searchbar key presses"

        # escape
        if keyval == Gdk.KEY_Escape:
            self.searchbar.entry.remove_css_class("error")
            self.config.set_boolean("view-searchbar", False)
            return True
        return False

    def __cb_tree_doubleclick(self, widget, iter):
        "Handles doubleclicks on the tree"

        if self.config.get_string("behavior-doubleclick") == "edit":
            self.entry_edit(iter)

        elif self.config.get_string("behavior-doubleclick") == "copy":
            self.clip_chain(self.entrystore.get_entry(iter))

        else:
            self.entry_goto((iter,))

    def __cb_tree_drag_prepare(self, drag_source, x, y):
        "Prepares drag source content"

        # Store selected iters for use in drop handler
        self.__drag_selected_iters = self.entrystore.filter_parents(self.tree.get_selected())

        if len(self.__drag_selected_iters) == 0:
            return None

        # Create content provider with dummy string (data is in __drag_selected_iters)
        content_provider = Gdk.ContentProvider.new_for_value("revelation/treerow")
        return content_provider

    def __cb_tree_drag_begin(self, drag_source, drag):
        "Called when drag begins"
        pass

    def __cb_tree_drop_async(self, drop_target, drop, x, y, userdata = None):
        "Callback for drag drops on the treeview"

        if self.__drag_selected_iters is None or len(self.__drag_selected_iters) == 0:
            return False

        # get source and destination data
        sourceiters = self.__drag_selected_iters
        path = self.tree.get_path_at_pos(int(x), int(y))

        if path is None:
            # Drop at end of root
            destpath = (self.entrystore.iter_n_children(None) - 1, )
            pos = Gtk.TreeViewDropPosition.AFTER
        else:
            destpath = path[0]
            # Determine drop position based on y coordinate within row
            # For simplicity, use INTO_OR_AFTER (can be refined later)
            pos = Gtk.TreeViewDropPosition.INTO_OR_AFTER

        destiter = self.entrystore.get_iter(destpath)
        destpath = self.entrystore.get_path(destiter)

        # avoid drops to current iter or descentants
        for sourceiter in sourceiters:
            sourcepath = self.entrystore.get_path(sourceiter)

            if self.entrystore.is_ancestor(sourceiter, destiter) or sourcepath == destpath:
                self.__drag_selected_iters = None
                return False

            elif pos == Gtk.TreeViewDropPosition.BEFORE and sourcepath[:-1] == destpath[:-1] and sourcepath[-1] == destpath[-1] - 1:
                self.__drag_selected_iters = None
                return False

            elif pos == Gtk.TreeViewDropPosition.AFTER and sourcepath[:-1] == destpath[:-1] and sourcepath[-1] == destpath[-1] + 1:
                self.__drag_selected_iters = None
                return False

        # move the entries
        if pos in (Gtk.TreeViewDropPosition.INTO_OR_BEFORE, Gtk.TreeViewDropPosition.INTO_OR_AFTER):
            parent = destiter
            sibling = None

        elif pos == Gtk.TreeViewDropPosition.BEFORE:
            parent = self.entrystore.iter_parent(destiter)
            sibling = destiter

        elif pos == Gtk.TreeViewDropPosition.AFTER:
            parent = self.entrystore.iter_parent(destiter)

            sibpath = list(destpath)
            sibpath[-1] += 1
            sibling = self.entrystore.get_iter(sibpath)

        self.entry_move(sourceiters, parent, sibling)

        self.__drag_selected_iters = None
        return True

    def __cb_tree_keypress(self, widget, data = None):
        "Handles key presses for the tree (deprecated - handled by TreeView event controller)"

        # Key presses are now handled by TreeView's EventControllerKey
        # This method is kept for compatibility but may be removed
        if data.keyval == Gdk.KEY_Return:
            self.entry_edit(self.tree.get_active())

        # insert
        elif data.keyval == Gdk.KEY_Insert:
            self.entry_add(None, self.tree.get_active())

        # delete
        elif data.keyval == Gdk.KEY_Delete:
            self.entry_remove(self.tree.get_selected())

    # CONFIG CALLBACKS #

    def __cb_config_toolbar_style(self, config, value, data = None):
        "Config callback for setting toolbar style"

        # Remove all style classes first
        self.toolbar.remove_css_class("toolbar-icons")
        self.toolbar.remove_css_class("toolbar-text")
        self.toolbar.remove_css_class("toolbar-both")
        self.toolbar.remove_css_class("toolbar-both-horiz")

        if value == "both":
            self.toolbar.add_css_class("toolbar-both")

        elif value == "both-horiz":
            self.toolbar.add_css_class("toolbar-both-horiz")

        elif value == "icons":
            self.toolbar.add_css_class("toolbar-icons")

        elif value == "text":
            self.toolbar.add_css_class("toolbar-text")

        # "desktop" style is default, no class needed

    # UNDO / REDO CALLBACKS #

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
        iters = [self.entrystore.get_iter(path) for path in paths]

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
        iters = [self.entrystore.get_iter(path) for path in paths]

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

    # PRIVATE METHODS #

    def __entry_find(self, parent, string, entrytype, direction = data.SEARCH_NEXT):
        "Searches for an entry"

        match = self.entrysearch.find(string, entrytype, self.tree.get_active(), direction)

        if match is not None:
            self.tree.select(match)
            self.statusbar.set_status(_('Match found for "%s"') % string)
            self.searchbar.entry.remove_css_class("error")

        else:
            self.statusbar.set_status(_('No match found for "%s"') % string)
            self.searchbar.entry.add_css_class("error")

    def __file_autosave(self):
        "Autosaves the current file if needed"

        try:
            if self.datafile.get_file() is None or self.datafile.get_password() is None:
                return

            if not self.config.get_boolean("file-autosave"):
                return

            self.datafile.save(self.entrystore, self.datafile.get_file(), self.datafile.get_password())
            self.entrystore.changed = False

        except IOError:
            pass

    def __file_load(self, file, password, datafile = None):
        "Loads data from a data file into an entrystore"

        # We may need to change the datahandler
        old_handler = None
        result = None

        try:
            if datafile is None:
                datafile = self.datafile

                # Because there are two fileversion we need to check if we are really dealing
                # with version two. If we aren't chances are high, that we are
                # dealing with version one. In this case we use the version one
                # handler and save the file as version two if it is changed, to
                # allow seamless upgrades.
                if not datafile.get_handler().detect(io.file_read(file)):
                    # Store the datahandler to be reset later on
                    old_handler = datafile.get_handler()
                    # Load the revelation fileversion one handler
                    datafile.set_handler(datahandler.Revelation)
                    dialog.Info(self.window, _('Old file format'), _('Revelation detected that \'%s\' file has the old and actually non-secure file format. It is strongly recommended to save this file with the new format. Revelation will do it automatically if you press save after opening the file.') % io.file_get_display_name(file)).run()

            while True:
                try:
                    result = datafile.load(file, password, lambda: dialog.PasswordOpen(self.window, io.file_get_display_name(file)).run())
                    break

                except datahandler.PasswordError:
                    dialog.Error(self.window, _('Incorrect password'), _('The password you entered for the file \'%s\' was not correct.') % io.file_get_display_name(file)).run()

        except datahandler.FormatError:
            self.statusbar.set_status(_('Open failed'))
            dialog.Error(self.window, _('Invalid file format'), _('The file \'%s\' contains invalid data.') % io.file_get_display_name(file)).run()

        except (datahandler.DataError, entry.EntryTypeError, entry.EntryFieldError):
            self.statusbar.set_status(_('Open failed'))
            dialog.Error(self.window, _('Unknown data'), _('The file \'%s\' contains unknown data. It may have been created by a newer version of Revelation.') % io.file_get_display_name(file)).run()

        except datahandler.VersionError:
            self.statusbar.set_status(_('Open failed'))
            dialog.Error(self.window, _('Unknown data version'), _('The file \'%s\' has a future version number, please upgrade Revelation to open it.') % io.file_get_display_name(file)).run()

        except datahandler.DetectError:
            self.statusbar.set_status(_('Open failed'))
            dialog.Error(self.window, _('Unable to detect filetype'), _('The file type of the file \'%s\' could not be automatically detected. Try specifying the file type manually.') % io.file_get_display_name(file)).run()

        except IOError:
            self.statusbar.set_status(_('Open failed'))
            dialog.Error(self.window, _('Unable to open file'), _('The file \'%s\' could not be opened. Make sure that the file exists, and that you have permissions to open it.') % io.file_get_display_name(file)).run()

        # If we switched the datahandlers before we need to switch back to the
        # version2 handler here, to ensure a seamless version upgrade on save
        if old_handler is not None:
            datafile.set_handler(old_handler.__class__)

        return result

    def __get_common_usernames(self, e = None):
        "Returns a list of possibly relevant usernames"

        ulist = []

        if e is not None and e.has_field(entry.UsernameField):
            ulist.append(e[entry.UsernameField])

        ulist.append(pwd.getpwuid(os.getuid())[0])
        ulist.extend(self.entrystore.get_popular_values(entry.UsernameField, 3))

        ulist = list({}.fromkeys(ulist).keys())
        ulist.sort()

        return ulist

    # PUBLIC METHODS #

    def about(self):
        "Displays the about dialog"

        dialog.run_unique_dialog(dialog.About, self)

    def clip_chain(self, e):
        "Copies all passwords from an entry as a chain"

        if e is None:
            return

        secrets = [field.value for field in e.fields if field.datatype == entry.DATATYPE_PASSWORD and field.value != ""]

        if self.config.get_boolean("clipboard-chain-username") and len(secrets) > 0 and e.has_field(entry.UsernameField) and e[entry.UsernameField] != "":
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
            undoactions.append((path, undostore))

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

        if entrystore is None:
            return

        parent = self.tree.get_active()
        iters = self.entrystore.import_entry(entrystore, None, parent)

        paths = [self.entrystore.get_path(iter) for iter in iters]

        self.undoqueue.add_action(
            _('Paste entries'), self.__cb_undo_paste, self.__cb_redo_paste,
            (entrystore, self.entrystore.get_path(parent), paths)
        )

        if len(iters) > 0:
            self.tree.select(iters[0])

        self.statusbar.set_status(_('Entries pasted'))

    def entry_add(self, e = None, parent = None, sibling = None):
        "Adds an entry"

        try:
            if e is None:
                d = dialog.EntryEdit(self.window, _('Add Entry'), None, self.config, self.clipboard)
                d.set_fieldwidget_data(entry.UsernameField, self.__get_common_usernames())
                e = d.run()

            iter = self.entrystore.add_entry(e, parent, sibling)

            self.undoqueue.add_action(
                _('Add entry'), self.__cb_undo_add, self.__cb_redo_add,
                (self.entrystore.get_path(iter), e.copy())
            )

            self.__file_autosave()
            self.tree.select(iter)
            self.statusbar.set_status(_('Entry added'))

        except dialog.CancelError:
            self.statusbar.set_status(_('Add entry cancelled'))

    def entry_edit(self, iter):
        "Edits an entry"

        try:
            if iter is None:
                return

            e = self.entrystore.get_entry(iter)

            if type(e) == entry.FolderEntry:
                d = dialog.FolderEdit(self.window, _('Edit Folder'), e)

            else:
                d = dialog.EntryEdit(self.window, _('Edit Entry'), e, self.config, self.clipboard)
                d.set_fieldwidget_data(entry.UsernameField, self.__get_common_usernames(e))

            n = d.run()
            self.entrystore.update_entry(iter, n)
            self.tree.select(iter)

            self.undoqueue.add_action(
                _('Update entry'), self.__cb_undo_edit, self.__cb_redo_edit,
                (self.entrystore.get_path(iter), e.copy(), n.copy())
            )

            self.__file_autosave()
            self.statusbar.set_status(_('Entry updated'))

        except dialog.CancelError:
            self.statusbar.set_status(_('Edit entry cancelled'))

    def entry_find(self):
        "Searches for an entry"

        self.config.set_boolean("view-searchbar", True)
        self.searchbar.entry.select_region(0, -1)
        self.searchbar.entry.grab_focus()

    def entry_folder(self, e = None, parent = None, sibling = None):
        "Adds a folder"

        try:
            if e is None:
                e = dialog.FolderEdit(self.window, _('Add folder')).run()

            iter = self.entrystore.add_entry(e, parent, sibling)

            self.undoqueue.add_action(
                _('Add folder'), self.__cb_undo_add, self.__cb_redo_add,
                (self.entrystore.get_path(iter), e.copy())
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
                command = self.config.get_string("launcher-%s" % e.id)

                if command in ("", None):
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

                if self.config.get_boolean("clipboard-chain-username") and len(chain) > 0 and e.has_field(entry.UsernameField) and e[entry.UsernameField] != "" and "%" + entry.UsernameField.symbol not in command:
                    chain.insert(0, e[entry.UsernameField])

                self.clipboard.set(chain, True)

                # generate and run goto command
                command = util.parse_subst(command, subst)
                util.execute_child(command)

                self.statusbar.set_status(_('Entry opened'))

            except (util.SubstFormatError, config.ConfigError):
                dialog.Error(self.window, _('Invalid goto command format'), _('The goto command for \'%s\' entries is invalid, please correct it in the preferences.') % e.typename).run()

            except util.SubstValueError:
                dialog.Error(self.window, _('Missing entry data'), _('The entry \'%s\' does not have all the data required to open it.') % e.name).run()

    def entry_move(self, sourceiters, parent = None, sibling = None):
        "Moves a set of entries"

        if type(sourceiters) != list:
            sourceiters = [sourceiters]

        newiters = []
        undoactions = []

        for sourceiter in sourceiters:
            sourcepath = self.entrystore.get_path(sourceiter)
            newiter = self.entrystore.move_entry(sourceiter, parent, sibling)
            newpath = self.entrystore.get_path(newiter)

            undoactions.append((sourcepath, newpath))
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

            entries = [self.entrystore.get_entry(iter) for iter in iters]
            dialog.EntryRemove(self.window, entries).run()
            iters = self.entrystore.filter_parents(iters)

            # store undo data (need paths)
            undoactions = []
            for iter in iters:
                undostore = data.EntryStore()
                undostore.import_entry(self.entrystore, iter)
                path = self.entrystore.get_path(iter)
                undoactions.append((path, undostore))

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
            if password is None:
                password = dialog.PasswordChange(self.window, self.datafile.get_password()).run()

            self.datafile.set_password(password)
            self.entrystore.changed = True

            self.__file_autosave()
            self.statusbar.set_status(_('Password changed'))

        except dialog.CancelError:
            self.statusbar.set_status(_('Password change cancelled'))

    def file_close(self):
        "Closes the current file"

        try:
            if self.entrystore.changed and dialog.FileChangesClose(self.window).run():
                if not self.file_save(self.datafile.get_file(), self.datafile.get_password()):
                    raise dialog.CancelError

            self.clipboard.clear()
            self.entryclipboard.clear()
            self.entrystore.clear()
            self.undoqueue.clear()
            self.statusbar.set_status(_('Closed file %s') % self.datafile.get_file_display_path())
            self.datafile.close()

            return True

        except dialog.CancelError:
            self.statusbar.set_status(_('Close file cancelled'))
            return False

    def file_export(self):
        "Exports data to a foreign file format"

        try:
            file, handler = dialog.ExportFileSelector(self.window).run()
            datafile = io.DataFile(handler)

            if datafile.get_handler().encryption:
                password = dialog.PasswordSave(self.window, io.file_get_display_name(file)).run()

            else:
                dialog.FileSaveInsecure(self.window).run()
                password = None

            datafile.save(self.entrystore, file, password)
            self.statusbar.set_status(_('Data exported to %s') % datafile.get_file_display_path())

        except dialog.CancelError:
            self.statusbar.set_status(_('Export cancelled'))

        except IOError:
            dialog.Error(self.window, _('Unable to write to file'), _('The file \'%s\' could not be opened for writing. Make sure that you have the proper permissions to write to it.') % io.file_get_display_name(file)).run()
            self.statusbar.set_status(_('Export failed'))

    def file_import(self):
        "Imports data from a foreign file"

        try:
            file, handler = dialog.ImportFileSelector(self.window).run()
            datafile = io.DataFile(handler)
            entrystore = self.__file_load(file, None, datafile)

            if entrystore is not None:
                newiters = self.entrystore.import_entry(entrystore, None)
                paths = [self.entrystore.get_path(iter) for iter in newiters]

                self.undoqueue.add_action(
                    _('Import data'), self.__cb_undo_import, self.__cb_redo_import,
                    (paths, entrystore)
                )

                self.statusbar.set_status(_('Data imported from %s') % datafile.get_file_display_path())

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
        app = Gio.Application.get_default
        app().get_dbus_connection().signal_unsubscribe(self.dbus_subscription_id)

        # TODO can this be done more elegantly?
        transients = [window for window in Gtk.Window.list_toplevels() if window.get_transient_for() == self]

        # store current state
        activeiter = self.tree.get_active()
        oldtitle = self.get_title()

        # clear application contents
        self.tree.set_model(None)
        self.entryview.clear()
        self.window.set_title('[' + _('Locked') + ']')
        self.statusbar.set_status(_('File locked'))
        self.file_locked = True

        # hide any dialogs
        for window in transients:
            window.hide()

        # lock file
        try:
            d = dialog.PasswordLock(self.window, password)

            if self.entrystore.changed:
                l = ui.ImageLabel(_('Quit disabled due to unsaved changes'), "dialog-warning")
                l.set_hexpand(True)
                l.set_vexpand(True)
                d.contents.append(l)
                cancel_button = d.get_widget_for_response(Gtk.ResponseType.CANCEL)
                if cancel_button:
                    cancel_button.set_sensitive(False)

            d.run()

        except dialog.CancelError:
            self.quit()

        # unlock the file and restore state
        self.tree.set_model(self.entrystore)
        self.tree.select(activeiter)
        self.window.set_title(oldtitle)
        self.statusbar.set_status(_('File unlocked'))
        self.file_locked = False

        for window in transients:
            window.show()

        self.locktimer.start(self.config.get_int("file-autolock-timeout") * 60)
        app = Gio.Application.get_default
        self.dbus_subscription_id = app().get_dbus_connection().signal_subscribe(None, "org.gnome.ScreenSaver", "ActiveChanged", "/org/gnome/ScreenSaver", None, Gio.DBusSignalFlags.NONE, self.__cb_screensaver_lock)

    def file_new(self):
        "Opens a new file"

        try:
            if self.entrystore.changed and dialog.FileChangesNew(self.window).run():
                if not self.file_save(self.datafile.get_file(), self.datafile.get_password()):
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
            if self.entrystore.changed and dialog.FileChangesOpen(self.window).run():
                if not self.file_save(self.datafile.get_file(), self.datafile.get_password()):
                    raise dialog.CancelError

            if file is None:
                file = dialog.OpenFileSelector(self.window).run()

            entrystore = self.__file_load(file, password)

            if entrystore is None:
                return

            self.entrystore.clear()
            self.entrystore.import_entry(entrystore, None)
            self.entrystore.changed = False
            self.undoqueue.clear()

            self.file_locked = False
            self.locktimer.start(60 * self.config.get_int("file-autolock-timeout"))
            self.statusbar.set_status(_('Opened file %s') % self.datafile.get_file_display_path())

        except dialog.CancelError:
            self.statusbar.set_status(_('Open cancelled'))

    def file_save(self, file = None, password = None):
        "Saves data to a file"

        try:
            if file is None:
                file = dialog.SaveFileSelector(self.window).run()

            if password is None:
                password = dialog.PasswordSave(self.window, io.file_get_display_name(file)).run()

            self.datafile.save(self.entrystore, file, password)
            self.entrystore.changed = False
            self.statusbar.set_status(_('Data saved to file %s') % io.file_get_display_path(file))

            return True

        except dialog.CancelError:
            self.statusbar.set_status(_('Save cancelled'))
            return False

        except IOError:
            dialog.Error(self.window, _('Unable to save file'), _('The file \'%s\' could not be opened for writing. Make sure that you have the proper permissions to write to it.') % io.file_get_display_name(file)).run()
            self.statusbar.set_status(_('Save failed'))
            return False

    def prefs(self):
        "Displays the application preferences"

        dialog.run_unique_dialog(Preferences, self.window, self.config)

    def pwcheck(self):
        "Displays the password checking dialog"

        dialog.run_unique_dialog(dialog.PasswordChecker, self.window, self.config, self.clipboard)

    def pwgen(self):
        "Displays the password generator dialog"

        dialog.run_unique_dialog(dialog.PasswordGenerator, self.window, self.config, self.clipboard)

    def quit(self):
        "Quits the application"

        try:
            if self.entrystore.changed and dialog.FileChangesQuit(self.window).run():
                if not self.file_save(self.datafile.get_file(), self.datafile.get_password()):
                    raise dialog.CancelError

            self.clipboard.clear()
            self.entryclipboard.clear()

            self.__save_state()

            Gtk.Application.quit(self)
            if sys.exc_info()[1]:
                # avoid raising an additional exception
                os._exit(0)
            else:
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

    def __init__(self, parent, cfg=None):
        dialog.Utility.__init__(self, parent, _('Preferences'))
        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.set_default_response(Gtk.ResponseType.CLOSE)
        self.config = cfg
        self.set_modal(False)

        # Load notebook and pages from UI file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/preferences.ui')
        self.notebook = builder.get_object('preferences_notebook')
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)
        self.get_content_area().append(self.notebook)
        # Ensure button box stays at the end
        self._ensure_button_box_at_end()

        # Get pages and tab labels from UI file
        self.page_general = builder.get_object('page_general')
        tab_general = builder.get_object('tab_general')
        ui.apply_css_padding(self.page_general, 12)
        self.page_general.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.notebook.append_page(self.page_general, tab_general)
        self.__init_section_files(self.page_general)
        self.__init_section_password(self.page_general)

        self.page_interface = builder.get_object('page_interface')
        tab_interface = builder.get_object('tab_interface')
        ui.apply_css_padding(self.page_interface, 12)
        self.page_interface.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.notebook.append_page(self.page_interface, tab_interface)
        self.__init_section_doubleclick(self.page_interface)
        self.__init_section_toolbar(self.page_interface)

        self.page_gotocmd = builder.get_object('page_gotocmd')
        tab_gotocmd = builder.get_object('tab_gotocmd')
        ui.apply_css_padding(self.page_gotocmd, 12)
        self.page_gotocmd.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        self.notebook.append_page(self.page_gotocmd, tab_gotocmd)
        self.__init_section_gotocmd(self.page_gotocmd)

        self.connect("response", lambda w, d: self.destroy())

    def __init_section_doubleclick(self, page):
        "Sets up the doubleclick section"

        # Load UI from file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/preferences-doubleclick.ui')

        # Get the section from UI file
        doubleclick_section = builder.get_object('doubleclick_section')

        # Set section title with markup
        doubleclick_title = builder.get_object('doubleclick_title')
        doubleclick_title.set_markup(f"<span weight='bold'>{util.escape_markup(_('Doubleclick Action'))}</span>")

        # Add section to page
        page.append(doubleclick_section)
        self.section_doubleclick = doubleclick_section

        # Get radio buttons from UI file
        self.radio_doubleclick_goto = builder.get_object('radio_doubleclick_goto')
        self.radio_doubleclick_edit = builder.get_object('radio_doubleclick_edit')
        self.radio_doubleclick_copy = builder.get_object('radio_doubleclick_copy')

        # Set up radio button group (GTK4: use set_group instead of join_group)
        self.radio_doubleclick_edit.set_group(self.radio_doubleclick_goto)
        self.radio_doubleclick_copy.set_group(self.radio_doubleclick_goto)

        # Connect signals
        self.radio_doubleclick_goto.connect("toggled", lambda w: w.get_active() and self.config.set_string("behavior-doubleclick", "goto"))
        self.radio_doubleclick_edit.connect("toggled", lambda w: w.get_active() and self.config.set_string("behavior-doubleclick", "edit"))
        self.radio_doubleclick_copy.connect("toggled", lambda w: w.get_active() and self.config.set_string("behavior-doubleclick", "copy"))

        # Set active radio button based on config
        {"goto": self.radio_doubleclick_goto,
         "edit": self.radio_doubleclick_edit,
         "copy": self.radio_doubleclick_copy}[self.config.get_string("behavior-doubleclick")].set_active(True)

    def __init_section_files(self, page):
        "Sets up the files section"

        # Load UI from file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/preferences-files.ui')

        # Get the section from UI file
        files_section = builder.get_object('files_section')

        # Set section title with markup
        files_title = builder.get_object('files_title')
        files_title.set_markup(f"<span weight='bold'>{util.escape_markup(_('Files'))}</span>")

        # Add section to page
        page.append(files_section)
        self.section_files = files_section

        # Get widgets from UI file
        self.check_autoload = builder.get_object('check_autoload')
        placeholder = builder.get_object('button_autoload_file')
        self.check_autosave = builder.get_object('check_autosave')
        self.check_autolock = builder.get_object('check_autolock')

        # Replace placeholder with FileChooserButton
        parent = placeholder.get_parent()
        placeholder.unparent()
        self.button_autoload_file = ui.FileChooserButton(_("Select File to Automatically Open"))
        self.button_autoload_file.set_hexpand(True)
        self.button_autoload_file.set_tooltip_text(_("File to open when Revelation is started"))
        parent.append(self.button_autoload_file)

        # Set up GSettings bindings
        self.config.bind("file-autoload", self.check_autoload, "active", Gio.SettingsBindFlags.DEFAULT)
        self.config.bind("file-autosave", self.check_autosave, "active", Gio.SettingsBindFlags.DEFAULT)
        self.config.bind("file-autolock", self.check_autolock, "active", Gio.SettingsBindFlags.DEFAULT)

        # Connect signals
        self.check_autoload.connect("toggled", lambda w: self.button_autoload_file.set_sensitive(w.get_active()))
        self.check_autolock.connect("toggled", lambda w: self.spin_autolock_timeout.set_sensitive(w.get_active()))

        # Set up file chooser button
        if self.config.get_boolean("file-autoload"):
            self.button_autoload_file.set_filename(self.config.get_string("file-autoload-file"))
        self.button_autoload_file.connect('file-set', lambda w: self.config.set_string("file-autoload-file", w.get_filename()))
        self.config.connect("changed::autoload-file", lambda w, fname: self.button_autoload_file.set_filename(w.get_string(fname)))
        self.button_autoload_file.set_sensitive(self.check_autoload.get_active())

        # Add file filters
        filter = Gtk.FileFilter()
        filter.set_name(_('Revelation files'))
        filter.add_mime_type("application/x-revelation")
        self.button_autoload_file.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern("*")
        self.button_autoload_file.add_filter(filter)

        # Get spin button from UI file (range and adjustment already set in XML)
        self.spin_autolock_timeout = builder.get_object('spin_autolock_timeout')
        self.spin_autolock_timeout.set_sensitive(self.check_autolock.get_active())
        self.config.bind("file-autolock-timeout", self.spin_autolock_timeout, "value", Gio.SettingsBindFlags.DEFAULT)

    def __init_section_gotocmd(self, page):
        "Sets up the goto command section"

        section = ui.InputSection(_('Goto Commands'), None, page.sizegroup)
        page.append(section)
        self.section_gotocmd = section

        for entrytype in entry.ENTRYLIST:
            if entrytype == entry.FolderEntry:
                continue

            e = entrytype()

            widget = ui.Entry()
            self.config.bind("launcher-"+e.id, widget, "text", Gio.SettingsBindFlags.DEFAULT)

            tooltip = _('Goto command for %s accounts. The following expansion variables can be used:') % e.typename + "\n\n"

            for field in e.fields:
                tooltip += "%%%s: %s\n" % (field.symbol, field.name)

            tooltip += "\n"
            tooltip += _('%%: a "%" sign') + "\n"
            tooltip += _('%?x: optional expansion variable') + "\n"
            tooltip += _('%(...%): optional substring expansion')

            widget.set_tooltip_text(tooltip)
            self.section_gotocmd.append_widget(e.typename, widget)

    def __init_section_password(self, page):
        "Sets up the password section"

        # Load UI from file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/preferences-passwords.ui')

        # Get the section from UI file
        passwords_section = builder.get_object('passwords_section')

        # Set section title with markup
        passwords_title = builder.get_object('passwords_title')
        passwords_title.set_markup(f"<span weight='bold'>{util.escape_markup(_('Passwords'))}</span>")

        # Add section to page
        page.append(passwords_section)
        self.section_password = passwords_section

        # Get widgets from UI file
        self.check_show_passwords = builder.get_object('check_show_passwords')
        self.check_chain_username = builder.get_object('check_chain_username')
        self.check_punctuation_chars = builder.get_object('check_punctuation_chars')

        # Set up GSettings bindings
        self.config.bind("view-passwords", self.check_show_passwords, "active", Gio.SettingsBindFlags.DEFAULT)
        self.config.bind("clipboard-chain-username", self.check_chain_username, "active", Gio.SettingsBindFlags.DEFAULT)
        self.config.bind("passwordgen-punctuation", self.check_punctuation_chars, "active", Gio.SettingsBindFlags.DEFAULT)

        # Get spin button from UI file (range and adjustment already set in XML)
        self.spin_pwlen = builder.get_object('spin_pwlen')
        self.config.bind("passwordgen-length", self.spin_pwlen, "value", Gio.SettingsBindFlags.DEFAULT)

        # Add label to sizegroup for alignment
        password_length_label = builder.get_object('password_length_label')
        page.sizegroup.add_widget(password_length_label)

    def __init_section_toolbar(self, page):
        "Sets up the toolbar section"

        # Load UI from file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/preferences-toolbar.ui')

        # Get the section from UI file
        toolbar_section = builder.get_object('toolbar_section')

        # Set section title with markup
        toolbar_title = builder.get_object('toolbar_title')
        toolbar_title.set_markup(f"<span weight='bold'>{util.escape_markup(_('Toolbar Style'))}</span>")

        # Add section to page
        page.append(toolbar_section)
        self.section_toolbar = toolbar_section

        # Get radio buttons from UI file
        self.radio_toolbar_desktop = builder.get_object('radio_toolbar_desktop')
        self.radio_toolbar_both = builder.get_object('radio_toolbar_both')
        self.radio_toolbar_bothhoriz = builder.get_object('radio_toolbar_bothhoriz')
        self.radio_toolbar_icons = builder.get_object('radio_toolbar_icons')
        self.radio_toolbar_text = builder.get_object('radio_toolbar_text')

        # Set up radio button group
        # GTK4: use set_group instead of join_group
        self.radio_toolbar_both.set_group(self.radio_toolbar_desktop)
        self.radio_toolbar_bothhoriz.set_group(self.radio_toolbar_desktop)
        self.radio_toolbar_icons.set_group(self.radio_toolbar_desktop)
        self.radio_toolbar_text.set_group(self.radio_toolbar_desktop)

        # Connect signals
        self.radio_toolbar_desktop.connect("toggled", lambda w: w.get_active() and self.config.set_string("view-toolbar-style", "desktop"))
        self.radio_toolbar_both.connect("toggled", lambda w: w.get_active() and self.config.set_string("view-toolbar-style", "both"))
        self.radio_toolbar_bothhoriz.connect("toggled", lambda w: w.get_active() and self.config.set_string("view-toolbar-style", "both-horiz"))
        self.radio_toolbar_icons.connect("toggled", lambda w: w.get_active() and self.config.set_string("view-toolbar-style", "icons"))
        self.radio_toolbar_text.connect("toggled", lambda w: w.get_active() and self.config.set_string("view-toolbar-style", "text"))

        # Set active radio button based on config
        {"desktop":    self.radio_toolbar_desktop,
         "both":       self.radio_toolbar_both,
         "both-horiz": self.radio_toolbar_bothhoriz,
         "icons":      self.radio_toolbar_icons,
         "text":       self.radio_toolbar_text
         }[self.config.get_string("view-toolbar-style")].set_active(True)

    def run(self):
        "Runs the preference dialog"

        # for some reason, Gtk crashes on close-by-escape unless we do this
        close_button = self.get_widget_for_response(Gtk.ResponseType.CLOSE)
        if close_button:
            close_button.grab_focus()
        self.notebook.grab_focus()

        # Call parent run() to actually show the dialog
        dialog.Dialog.run(self)


if __name__ == "__main__":
    app = Revelation()
    app.set_flags(Gio.ApplicationFlags.NON_UNIQUE)
    app.run()
