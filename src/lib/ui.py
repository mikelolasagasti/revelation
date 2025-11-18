#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for UI functionality
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

from . import config, data, dialog, entry, io, util

import gettext
import time
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gtk, Gdk, Gio, GLib, Pango  # noqa: E402

_ = gettext.gettext


STOCK_CONTINUE          = _("_Continue")               # "revelation-continue"
STOCK_DISCARD           = "revelation-discard"
STOCK_EDIT              = "revelation-edit"
STOCK_EXPORT            = _("_Export")                 # "revelation-export"
STOCK_FOLDER            = "revelation-folder"
STOCK_GENERATE          = _("_Generate")               # "revelation-generate"
STOCK_IMPORT            = _("_Import")                 # "revelation-import"
STOCK_GOTO              = "revelation-goto"
STOCK_LOCK              = "revelation-lock"
STOCK_NEW_ENTRY         = _("_Add Entry")              # "revelation-new-entry"
STOCK_NEW_FOLDER        = _("_Add Folder")             # "revelation-new-folder"
STOCK_NEXT              = "go-down"                    # "revelation-next"
STOCK_PASSWORD_CHANGE   = _("_Change")                 # "revelation-password-change"
STOCK_PASSWORD_CHECK    = "revelation-password-check"  # nosec
STOCK_PASSWORD_STRONG   = "security-high"              # nosec "revelation-password-strong"
STOCK_PASSWORD_WEAK     = "security-low"               # nosec "revelation-password-weak"
STOCK_PREVIOUS          = "go-up"                      # "revelation-previous"
STOCK_RELOAD            = _("_Reload")                 # "revelation-reload"
STOCK_REMOVE            = "revelation-remove"
STOCK_REPLACE           = _("_Replace")                # "revelation-replace"
STOCK_UNKNOWN           = "dialog-question"            # "revelation-unknown"
STOCK_UNLOCK            = _("_Unlock")                 # "revelation-unlock"
STOCK_UPDATE            = _("_Update")                 # "revelation-update"


STOCK_ENTRY_FOLDER      = "folder"              # "revelation-account-folder"
STOCK_ENTRY_FOLDER_OPEN = "folder-open"         # "revelation-account-folder-open"
STOCK_ENTRY_CREDITCARD  = "application-x-executable"  # "revelation-account-creditcard"
STOCK_ENTRY_CRYPTOKEY   = "dialog-password"     # "revelation-account-cryptokey"
STOCK_ENTRY_DATABASE    = "drive-harddisk"      # "revelation-account-database"
STOCK_ENTRY_DOOR        = "changes-allow"       # "revelation-account-door"
STOCK_ENTRY_EMAIL       = "emblem-mail"         # "revelation-account-email"
STOCK_ENTRY_FTP         = "system-file-manager"  # "revelation-account-ftp"
STOCK_ENTRY_GENERIC     = "document-new"        # "revelation-account-generic"
STOCK_ENTRY_PHONE       = "phone"               # "revelation-account-phone"
STOCK_ENTRY_SHELL       = "utilities-terminal"  # "revelation-account-shell"
STOCK_ENTRY_REMOTEDESKTOP = "preferences-desktop-remote-desktop"  # "revelation-account-remotedesktop"
STOCK_ENTRY_WEBSITE     = "web-browser"         # "revelation-account-website"


# IconSize enum removed in GTK4 - icons auto-size based on context
# These constants are deprecated and no longer used
# Kept for backward compatibility only
ICON_SIZE_APPLET        = None
ICON_SIZE_DATAVIEW      = None
ICON_SIZE_DROPDOWN      = None
ICON_SIZE_ENTRY         = None
ICON_SIZE_FALLBACK      = None
ICON_SIZE_HEADLINE      = None
ICON_SIZE_LABEL         = None
ICON_SIZE_LOGO          = None
ICON_SIZE_TREEVIEW      = None


# EXCEPTIONS #

class DataError(Exception):
    "Exception for invalid data"
    pass


# FUNCTIONS #

def apply_css_padding(widget, padding):
    "Apply CSS padding to a widget (replaces set_border_width)"
    # Add CSS class with padding value to avoid conflicts between different padding values
    css_class = f"revelation-padding-{padding}"
    widget.add_css_class(css_class)

    # Create CSS provider with the class selector
    css_provider = Gtk.CssProvider()
    css = f".{css_class} {{ padding: {padding}px; }}"
    css_provider.load_from_data(css.encode())
    display = widget.get_display()
    Gtk.StyleContext.add_provider_for_display(display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def generate_field_display_widget(field, cfg = None, userdata = None):
    "Generates a widget for displaying a field value"

    if field.datatype == entry.DATATYPE_EMAIL:
        widget = LinkButton("mailto:%s" % field.value, util.escape_markup(field.value))

    elif field.datatype == entry.DATATYPE_PASSWORD:
        widget = PasswordLabel(util.escape_markup(field.value), cfg, userdata)

    elif field.datatype == entry.DATATYPE_URL:
        widget = LinkButton(field.value, util.escape_markup(field.value))

    else:
        widget = Label(util.escape_markup(field.value))
        widget.set_selectable(True)

    return widget


def generate_field_edit_widget(field, cfg = None, userdata = None):
    "Generates a widget for editing a field"

    if type(field) == entry.PasswordField:
        widget = PasswordEntryGenerate(None, cfg, userdata)

    elif type(field) == entry.UsernameField:
        widget = Gtk.ComboBoxText.new_with_entry()
        setup_comboboxentry(widget, userdata)

    elif field.datatype == entry.DATATYPE_FILE:
        widget = FileEntry()

    elif field.datatype == entry.DATATYPE_PASSWORD:
        widget = PasswordEntry(None, cfg, userdata)

    else:
        widget = Entry()

    widget.set_text(field.value or "")

    return widget


def setup_comboboxentry(widget, userdata=None):
    widget.entry = widget.get_child()
    widget.entry.set_activates_default(True)

    widget.set_text = widget.entry.set_text
    widget.get_text = widget.entry.get_text

    widget.completion = Gtk.EntryCompletion()
    # Create a simple model for completion
    widget.completion_model = Gtk.ListStore(GObject.TYPE_STRING)
    widget.completion.set_model(widget.completion_model)
    widget.completion.set_text_column(0)
    widget.completion.set_minimum_key_length(1)
    widget.entry.set_completion(widget.completion)

    def set_values(vlist):
        "Sets the values for the dropdown"

        widget.remove_all()
        widget.completion_model.clear()

        for item in vlist:
            widget.append_text(item)
            widget.completion_model.append((item,))

    widget.set_values = set_values

    if userdata is not None:
        widget.set_values(userdata)


# CONTAINERS #


class InputSection(Gtk.Box):
    "A section of input fields"

    def __init__(self, title = None, description = None, sizegroup = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_spacing(6)

        self.title  = None
        self.desc   = None
        self.sizegroup  = sizegroup

        if title is not None:
            self.title = Label("<span weight=\"bold\">%s</span>" % util.escape_markup(title))
            self.title.set_vexpand(True)
            self.append(self.title)

        if description is not None:
            self.desc = Label(util.escape_markup(description))
            self.desc.set_vexpand(True)
            self.append(self.desc)

        if sizegroup is None:
            self.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

    def append_widget(self, title, widget, indent = True):
        "Adds a widget to the section"

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.set_spacing(12)
        self.append(row)

        if self.title is not None and indent:
            row.append(Label(""))

        if title is not None:
            label = Label("%s:" % util.escape_markup(title))
            self.sizegroup.add_widget(label)
            row.append(label)

        widget.set_hexpand(True)
        widget.set_vexpand(True)
        row.append(widget)

    def clear(self):
        "Removes all widgets"

        child = self.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            if child not in (self.title, self.desc):
                child.unparent()
            child = next_child


# DISPLAY WIDGETS #

class ImageLabel(Gtk.Box):
    "A label with an image"

    def __init__(self, text = None, stock = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)

        self.image = Gtk.Image()
        self.image.set_vexpand(True)
        self.append(self.image)

        self.label = Label(text)
        self.label.set_hexpand(True)
        self.label.set_vexpand(True)
        self.append(self.label)

        if stock is not None:
            self.image.set_from_icon_name(stock)

    def set_stock(self, stock):
        "Sets the image"

        self.image.set_from_icon_name(stock)

    def set_text(self, text):
        "Sets the label text"

        self.label.set_text(text)


class Label(Gtk.Label):
    "A text label"

    # Map justification to horizontal alignment
    _JUSTIFY_TO_ALIGN = {
        Gtk.Justification.LEFT: Gtk.Align.START,
        Gtk.Justification.CENTER: Gtk.Align.CENTER,
        Gtk.Justification.RIGHT: Gtk.Align.END,
    }

    def __init__(self, text = None, justify = Gtk.Justification.LEFT):
        Gtk.Label.__init__(self)

        self.set_text(text)
        self.set_justify(justify)
        self.set_use_markup(True)
        self.set_wrap(True)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(self._JUSTIFY_TO_ALIGN.get(justify, Gtk.Align.START))

    def set_text(self, text):
        "Sets the text of the label"

        if text is None:
            Gtk.Label.set_text(self, "")
        else:
            Gtk.Label.set_markup(self, text)


class PasswordLabel(Gtk.Box):
    "A label for displaying passwords"

    def __init__(self, password = "", cfg = None, clipboard = None, justify = Gtk.Justification.LEFT):  # nosec
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.password   = util.unescape_markup(password)
        self.config = cfg
        self.clipboard  = clipboard

        self.label = Label(util.escape_markup(self.password), justify)
        self.label.set_selectable(True)
        self.append(self.label)

        self.show_password(cfg.get_boolean("view-passwords"))
        self.config.connect('changed::view-passwords', lambda w, k: self.show_password(w.get_boolean(k)))

        click_gesture = Gtk.GestureClick.new()
        click_gesture.set_button(0)  # All buttons
        click_gesture.connect("pressed", self.__cb_button_press)
        self.label.add_controller(click_gesture)

    def __cb_drag_data_get(self, widget, context, selection, info, timestamp, data = None):
        "Provides data for a drag operation"
        pass

    def __cb_button_press(self, gesture, n_press, x, y):
        "Populates the popup menu"

        if self.label.get_selectable():
            return False

        button = gesture.get_current_button()
        if button == 3:
            menu = Menu()

            menuitem = ImageMenuItem("edit-copy", _('Copy password'))
            menuitem.connect("activate", lambda w: self.clipboard.set([self.password], True))
            menu.append(menuitem)

            menu.popup_at_widget(self.label, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)

            return True
        return False

    def set_ellipsize(self, ellipsize):
        "Sets ellipsize for the label"

        self.label.set_ellipsize(ellipsize)

    def show_password(self, show = True):
        "Sets whether to display the password"

        if show:
            self.label.set_text(util.escape_markup(self.password))
            self.label.set_selectable(True)

        else:
            self.label.set_text(Gtk.Entry().get_invisible_char()*6)
            self.label.set_selectable(False)


class EditableTextView(Gtk.ScrolledWindow):
    "An editable text view"

    def __init__(self, buffer = None, text = None):

        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.textview = Gtk.TextView(buffer=buffer)
        self.textbuffer = self.textview.get_buffer()
        self.set_child(self.textview)

        if text is not None:
            self.textview.get_buffer().set_text(text)

    def set_text(self, text):
        "Sets the entry contents"

        if text is None:
            self.textbuffer.set_text("")

        self.textbuffer.set_text(text)

    def get_text(self):
        "Returns the text of the entry"

        return self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), False)


class TextView(Gtk.TextView):
    "A text view"

    def __init__(self, buffer = None, text = None):
        Gtk.TextView.__init__(self)
        self.set_buffer(buffer)

        self.set_editable(False)
        self.set_wrap_mode(Gtk.WrapMode.NONE)
        self.set_cursor_visible(False)
        self.add_css_class("monospace")
        css_provider = Gtk.CssProvider()
        css = ".monospace { font-family: monospace; }"
        css_provider.load_from_data(css.encode())
        display = self.get_display()
        Gtk.StyleContext.add_provider_for_display(display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        if text is not None:
            self.get_buffer().set_text(text)


# TEXT ENTRIES #

class Entry(Gtk.Entry):
    "A normal text entry"

    def __init__(self, text = None):
        Gtk.Entry.__init__(self)

        self.set_activates_default(True)
        if text is not None:
            Gtk.Entry.set_text(self, text)


class FileEntry(Gtk.Box):
    "A file entry"

    def __init__(self, title = None, file = None, type = Gtk.FileChooserAction.OPEN):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)

        self.title = title is not None and title or _('Select File')
        self.type = type

        self.entry = Entry()
        self.entry.connect("changed", lambda w: self.emit("changed"))
        self.entry.set_hexpand(True)
        self.entry.set_vexpand(True)
        self.append(self.entry)

        self.button = Gtk.Button(label=_('Browse...'))
        self.button.connect("clicked", self.__cb_filesel)
        self.append(self.button)

        if file is not None:
            self.set_filename(file)

    def __cb_filesel(self, widget, data = None):
        "Displays a file selector when Browse is pressed"

        try:
            # Get parent window for the file selector
            toplevel = self.get_toplevel()
            parent = toplevel if isinstance(toplevel, Gtk.Window) else None

            fsel = dialog.FileSelector(parent, self.title, self.type)
            file = self.get_filename()

            # Only set filename if it's not empty and is a valid path
            if file and file != "" and file != "/":
                try:
                    fsel.set_filename(file)
                except (ValueError, TypeError):
                    # If setting filename fails, just continue without it
                    pass

            filename = fsel.run()
            if filename:
                self.set_filename(filename)

        except dialog.CancelError:
            pass

    def get_filename(self):
        "Gets the current filename"

        return io.file_normpath(self.entry.get_text())

    def get_text(self):
        "Wrapper to emulate Entry"

        return self.entry.get_text()

    def set_filename(self, filename):
        "Sets the current filename"

        self.entry.set_text(io.file_normpath(filename))
        self.entry.set_position(-1)

    def set_text(self, text):
        "Wrapper to emulate Entry"

        self.entry.set_text(text)


GObject.type_register(FileEntry)
GObject.signal_new("changed", FileEntry, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, ())


class PasswordEntry(Gtk.Entry):
    "An entry for editing a password (follows the 'show passwords' preference)"

    def __init__(self, password = None, cfg = None, clipboard = None):
        Gtk.Entry.__init__(self)
        self.set_visibility(False)
        self.set_activates_default(True)
        if password:
            self.set_text(password)

        self.autocheck  = True
        self.config = cfg
        self.clipboard  = clipboard

        self.connect("changed", self.__cb_check_password)
        click_gesture = Gtk.GestureClick.new()
        click_gesture.set_button(3)
        click_gesture.connect("pressed", self.__cb_button_press)
        self.add_controller(click_gesture)

        if cfg is not None:
            self.config.bind('view-passwords', self, "visibility", Gio.SettingsBindFlags.DEFAULT)

    def __cb_check_password(self, widget, data = None):
        "Callback for changed, checks the password"

        if not self.autocheck:
            return

        password = self.get_text()

        if len(password) == 0:
            self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)

        else:
            try:
                util.check_password(password)

            except ValueError as reason:
                self.set_password_strong(False, _('The password %s') % str(reason))

            else:
                self.set_password_strong(True, _('The password seems good'))

    def __cb_button_press(self, gesture, n_press, x, y):
        "Handles right-click to show context menu"

        if n_press == 1 and self.clipboard is not None:
            menu = Menu()
            menuitem = ImageMenuItem("edit-copy", _('Copy password'))
            menuitem.connect("activate", lambda w: self.clipboard.set([self.get_text()], True))
            menu.append(menuitem)
            menu.popup_at_widget(self, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)
            return True
        return False


    def set_password_strong(self, strong, reason = ""):
        "Sets whether the password is strong or not"

        self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, strong and STOCK_PASSWORD_STRONG or STOCK_PASSWORD_WEAK)
        self.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, reason)


class PasswordEntryGenerate(Gtk.Box):
    "A password entry with a generator button"

    def __init__(self, password = None, cfg = None, clipboard = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)
        self.config = cfg

        self.pwentry = PasswordEntry(password, cfg, clipboard)
        self.pwentry.set_hexpand(True)
        self.pwentry.set_vexpand(True)
        self.append(self.pwentry)

        self.button = Gtk.Button(label=_('Generate'))
        self.button.connect("clicked", lambda w: self.generate())
        self.append(self.button)

        self.entry = self.pwentry

    def generate(self):
        "Generates a password for the entry"

        password = util.generate_password(self.config.get_int("passwordgen-length"), self.config.get_boolean("passwordgen-punctuation"))
        self.pwentry.set_text(password)

    def get_text(self):
        "Wrapper for the entry"

        return self.pwentry.get_text()

    def set_text(self, text):
        "Wrapper for the entry"

        self.pwentry.set_text(text)


# BUTTONS #

class DropDown(Gtk.ComboBox):
    "A dropdown button"

    def __init__(self, icons = False):
        Gtk.ComboBox.__init__(self)

        self.model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)
        self.set_model(self.model)

        if icons:
            cr = Gtk.CellRendererPixbuf()
            cr.set_fixed_size(21, -1)
            self.pack_start(cr, False)
            self.add_attribute(cr, "icon-name", 1)

        cr = Gtk.CellRendererText()
        self.pack_start(cr, True)
        self.add_attribute(cr, "text", 0)

        self.connect("realize", self.__cb_show)

    def __cb_show(self, widget, data = None):
        "Callback for when widget is shown"

        if self.get_active() == -1:
            self.set_active(0)

    def append_item(self, text, stock = None, data = None):
        "Appends an item to the dropdown"

        self.model.append((text, stock, data))

    def get_active_item(self):
        "Returns a tuple with data for the current item"

        iter = self.model.iter_nth_child(None, self.get_active())
        return self.model.get(iter, 0, 1, 2)

    def get_item(self, index):
        "Returns data for an item"

        return self.model.get(self.model.iter_nth_child(None, index), 0, 1, 2)

    def get_num_items(self):
        "Returns the number of items in the dropdown"

        return self.model.iter_n_children(None)

    def insert_item(self, index, text, stock = None, data = None):
        "Inserts an item in the dropdown"

        self.model.insert(index, (text, stock, data))


class EntryDropDown(DropDown):
    "An entry type dropdown"

    def __init__(self):
        DropDown.__init__(self, True)

        for e in entry.ENTRYLIST:
            if e != entry.FolderEntry:
                self.append_item(e().typename, e().icon, e)

    def get_active_type(self):
        "Get the currently active type"

        item = self.get_active_item()

        if item is not None:
            return item[2]

    def set_active_type(self, entrytype):
        "Set the active type"

        for i in range(self.get_num_items()):
            if self.get_item(i)[2] == entrytype:
                self.set_active(i)
                break


class LinkButton(Gtk.LinkButton):
    "A link button"

    def __init__(self, url, label):
        Gtk.LinkButton.__init__(self, uri=url, label=label)
        self.set_halign(Gtk.Align.START)

        self.label = self.get_first_child()

        "If URI is too long reduce it for the label"
        if len(label) > 60:
            self.label.set_text(label[0:59] + " (...)")

    def set_ellipsize(self, ellipsize):
        "Sets ellipsize for label"

        self.label.set_ellipsize(ellipsize)

    def set_justify(self, justify):
        "Sets justify for label"

        self.label.set_justify(justify)


# FILE CHOOSER BUTTON #

class FileChooserButton(Gtk.Box):
    "A replacement for Gtk.FileChooserButton (removed in GTK4)"

    __gsignals__ = {
        'file-set': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, title=None, action=Gtk.FileChooserAction.OPEN):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)

        self.title = title
        self.action = action
        self.filters = []
        self._filename = None

        # Create button with label
        self.button = Gtk.Button()
        self.button.set_hexpand(True)
        self.button.connect("clicked", self.__cb_button_clicked)
        self.append(self.button)

        # Update button label
        self.__update_button_label()

    def __update_button_label(self):
        "Updates the button label to show current filename"
        if self._filename:
            display_name = io.file_get_display_name(self._filename)
            self.button.set_label(display_name)
        else:
            self.button.set_label(_("Select File..."))

    def __get_parent_window(self):
        "Gets the parent window for the file chooser"
        widget = self
        while widget:
            if isinstance(widget, Gtk.Window):
                return widget
            widget = widget.get_parent()
        return None

    def __cb_button_clicked(self, button):
        "Opens file chooser dialog when button is clicked"
        from . import dialog

        parent = self.__get_parent_window()
        if parent is None:
            parent = Gtk.Application.get_default().get_active_window()

        chooser = dialog.OpenFileSelector(parent)
        if self.action != Gtk.FileChooserAction.OPEN:
            # For non-OPEN actions, use FileSelector directly
            chooser = dialog.FileSelector(parent, self.title or _("Select File"), self.action)

        # Apply filters
        for filter_obj in self.filters:
            chooser.add_filter(filter_obj)

        # Set current file if any
        if self._filename:
            try:
                # Try set_file() first (for URIs), then set_filename() (for paths)
                if self._filename.startswith('file://'):
                    file = Gio.File.new_for_uri(self._filename)
                    chooser.set_file(file)
                else:
                    chooser.set_filename(self._filename)
            except Exception:
                pass  # File might not exist

        try:
            filename = chooser.run()
            if filename:
                self.set_filename(filename)
        except dialog.CancelError:
            pass

    def set_filename(self, filename):
        "Sets the selected filename"
        self._filename = filename
        self.__update_button_label()
        self.emit("file-set")

    def get_filename(self):
        "Gets the selected filename"
        return self._filename

    def add_filter(self, filter_obj):
        "Adds a file filter"
        self.filters.append(filter_obj)

    def set_sensitive(self, sensitive):
        "Sets button sensitivity"
        self.button.set_sensitive(sensitive)

    def get_sensitive(self):
        "Gets button sensitivity"
        return self.button.get_sensitive()


# MENUS AND MENU ITEMS #

class ImageMenuItem:
    "A menuitem with an icon"

    def __init__(self, stock, text = None):
        self.stock = stock
        self.text = text or ""
        self.activate_callback = None
        self.menu_item = None

    def connect(self, signal, callback):
        "Connect activate signal"
        if signal == "activate":
            self.activate_callback = callback

    def set_stock(self, stock):
        "Set the stock item to use as icon"
        self.stock = stock

    def set_text(self, text):
        "Set the item text"
        self.text = text

    def _create_gio_menuitem(self):
        "Create Gio.MenuItem from this"
        if self.menu_item is None:
            # Create menu item with icon and label
            label = self.text
            icon_str = f"{self.stock} " if self.stock else ""
            detailed_action = None

            # Store callback for later execution
            if self.activate_callback:
                # Use a unique action name
                action_name = f"menu-action-{id(self)}"
                detailed_action = f"app.{action_name}"
                # Store callback to be connected via action
                self._action_name = action_name
                self._action_callback = self.activate_callback

            self.menu_item = Gio.MenuItem.new(label, detailed_action)
            if self.stock:
                self.menu_item.set_attribute_value("icon", GLib.Variant.new_string(self.stock))

        return self.menu_item


class Menu:
    "A menu"

    def __init__(self):
        self.menu_model = Gio.Menu.new()
        self.items = []
        self.popover = None
        self._actions = {}  # Store actions for callbacks

    def append(self, item):
        "Append a menu item"
        if isinstance(item, ImageMenuItem):
            gio_item = item._create_gio_menuitem()
            self.menu_model.append_item(gio_item)
            self.items.append(item)
            # Store action if needed
            if hasattr(item, '_action_name') and item._action_callback:
                self._actions[item._action_name] = item._action_callback

    def insert(self, item, position):
        "Insert a menu item at position"
        if isinstance(item, ImageMenuItem):
            gio_item = item._create_gio_menuitem()
            self.menu_model.insert_item(position, gio_item)
            self.items.insert(position, item)
            # Store action if needed
            if hasattr(item, '_action_name') and item._action_callback:
                self._actions[item._action_name] = item._action_callback

    def show_all(self):
        "Show the menu"
        self.popover = Gtk.PopoverMenu.new_from_model(self.menu_model)

        app = Gtk.Application.get_default()
        if app and self._actions:
            for action_name, callback in self._actions.items():
                action = Gio.SimpleAction.new(action_name, None)
                def make_activate_handler(cb):
                    return lambda a, p: cb(None)
                action.connect("activate", make_activate_handler(callback))
                app.add_action(action)

    def popup_at_widget(self, widget, widget_anchor, menu_anchor, trigger_event):
        "Popup menu at widget"
        if self.popover is None:
            self.popover = Gtk.PopoverMenu.new_from_model(self.menu_model)
            app = Gtk.Application.get_default()
            if app and self._actions:
                for action_name, callback in self._actions.items():
                    action = Gio.SimpleAction.new(action_name, None)
                    def make_activate_handler(cb):
                        return lambda a, p: cb(None)
                    action.connect("activate", make_activate_handler(callback))
                    app.add_action(action)

        if self.popover:
            self.popover.set_parent(widget)
            # Get widget allocation for positioning
            allocation = widget.get_allocation()
            rect = Gdk.Rectangle()
            rect.x = allocation.x
            rect.y = allocation.y
            rect.width = allocation.width
            rect.height = allocation.height
            self.popover.set_pointing_to(rect)
            self.popover.popup()

    def popup_at_pointer(self, event=None):
        "Popup menu at pointer"
        if self.popover is None:
            self.popover = Gtk.PopoverMenu.new_from_model(self.menu_model)
            app = Gtk.Application.get_default()
            if app and self._actions:
                for action_name, callback in self._actions.items():
                    action = Gio.SimpleAction.new(action_name, None)
                    def make_activate_handler(cb):
                        return lambda a, p: cb(None)
                    action.connect("activate", make_activate_handler(callback))
                    app.add_action(action)

        if self.popover:
            # Get the widget that should parent the popover
            # For now, use the default widget or window
            self.popover.popup()


# MISCELLANEOUS WIDGETS #

class TreeView(Gtk.TreeView):
    "A tree display"

    def __init__(self, model):
        Gtk.TreeView.__init__(self, model=model)
        self.set_headers_visible(False)
        self.model = model

        self.selection = self.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.set_button(0)  # All buttons
        click_gesture.connect("pressed", self.__cb_buttonpress)
        click_gesture.connect("released", self.__cb_button_release)
        self.add_controller(click_gesture)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.__cb_keypress)
        self.add_controller(key_controller)

        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("motion", self.__cb_motion)
        self.add_controller(motion_controller)
        self.__drag_start_x = None
        self.__drag_start_y = None
        self.__drag_button = None

    def __cb_buttonpress(self, gesture, n_press, x, y):
        "Callback for handling mouse clicks"

        button = gesture.get_current_button()
        path = self.get_path_at_pos(int(x), int(y))

        # handle click outside entry
        if path is None:
            self.unselect_all()
            return

        # handle doubleclick
        if button == 1 and n_press == 2 and path is not None:
            iter = self.model.get_iter(path[0])
            self.toggle_expanded(iter)

            if iter is not None:
                self.emit("doubleclick", iter)

        # display popup on right-click
        elif button == 3:
            if path is not None and not self.selection.iter_is_selected(self.model.get_iter(path[0])):
                self.set_cursor(path[0], path[1], False)

            # Create a simple event-like object for popup signal
            class PopupEvent:
                def __init__(self, button, x, y):
                    self.button = button
                    self.x = x
                    self.y = y
            self.emit("popup", PopupEvent(button, x, y))

        # handle drag-and-drop of multiple rows (start tracking)
        elif button in (1, 2) and n_press == 1 and path is not None and self.selection.iter_is_selected(self.model.get_iter(path[0])) and len(self.get_selected()) > 1:
            self.__drag_start_x = x
            self.__drag_start_y = y
            self.__drag_button = button

    def __cb_button_release(self, gesture, n_press, x, y):
        "Ends a drag"

        if self.__drag_start_x is not None:
            self.__drag_check_end()

    def __cb_motion(self, controller, x, y):
        "Monitors drag motion"

        if self.__drag_start_x is not None and self.__drag_button is not None:
            # Check drag threshold (default is 8 pixels)
            threshold = 8
            dx = abs(x - self.__drag_start_x)
            dy = abs(y - self.__drag_start_y)

            if dx > threshold or dy > threshold:
                self.__drag_check_end()
                # Trigger drag using DragSource (will be handled by the drag source in revelation.py)
                # For now, we'll rely on the DragSource that's already set up
                # The custom multi-row drag will need to be integrated with the DragSource
                self.__drag_start_x = None
                self.__drag_start_y = None
                self.__drag_button = None

    def __cb_keypress(self, controller, keyval, keycode, state):
        "Callback for handling key presses"

        # expand/collapse node on space
        if keyval == Gdk.KEY_space:
            self.toggle_expanded(self.get_active())
            return True
        return False

    def __drag_check_end(self):
        "Ends a drag check"

        self.__drag_start_x = None
        self.__drag_start_y = None
        self.__drag_button = None

    def collapse_row(self, iter):
        "Collapse a tree row"

        Gtk.TreeView.collapse_row(self, self.model.get_path(iter))

    def expand_row(self, iter):
        "Expand a tree row"

        if iter is not None and self.model.iter_n_children(iter) > 0:
            Gtk.TreeView.expand_row(self, self.model.get_path(iter), False)

    def expand_to_iter(self, iter):
        "Expand all items up to and including a given iter"

        path = self.model.get_path(iter)

        for i in range(len(path)):
            iter = self.model.get_iter(path[0:i])
            self.expand_row(iter)

    def get_active(self):
        "Get the currently active row"

        if self.model is None:
            return None

        iter = self.model.get_iter(self.get_cursor()[0])

        if iter is None or not self.selection.iter_is_selected(iter):
            return None

        return iter

    def get_selected(self):
        "Get a list of currently selected rows"

        list = []
        self.selection.selected_foreach(lambda model, path, iter: list.append(iter))

        return list

    def select(self, iter):
        "Select a particular row"

        if iter is None:
            self.unselect_all()

        else:
            self.expand_to_iter(iter)
            self.set_cursor(self.model.get_path(iter))

    def select_all(self):
        "Select all rows in the tree"

        self.selection.select_all()
        self.selection.emit("changed")
        self.emit("cursor_changed")

    def set_model(self, model):
        "Change the tree model which is being displayed"

        Gtk.TreeView.set_model(self, model)
        self.model = model

    def toggle_expanded(self, iter):
        "Toggle the expanded state of a row"

        if iter is None:
            return

        elif self.row_expanded(self.model.get_path(iter)):
            self.collapse_row(iter)

        else:
            self.expand_row(iter)

    def unselect_all(self):
        "Unselect all rows in the tree"

        self.selection.unselect_all()
        self.selection.emit("changed")
        self.emit("cursor_changed")
        self.emit("unselect_all")


GObject.signal_new("doubleclick", TreeView, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, (GObject.TYPE_PYOBJECT, ))
GObject.signal_new("popup", TreeView, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, (GObject.TYPE_PYOBJECT, ))


class EntryTree(TreeView):
    "An entry tree"

    def __init__(self, entrystore):
        TreeView.__init__(self, entrystore)

        column = Gtk.TreeViewColumn()
        self.append_column(column)

        cr = Gtk.CellRendererPixbuf()
        column.pack_start(cr, False)
        column.add_attribute(cr, "icon-name", data.COLUMN_ICON)

        cr = Gtk.CellRendererText()
        column.pack_start(cr, True)
        column.add_attribute(cr, "text", data.COLUMN_NAME)

        self.connect("doubleclick", self.__cb_doubleclick)
        self.connect("row-expanded", self.__cb_row_expanded)
        self.connect("row-collapsed", self.__cb_row_collapsed)

    def __cb_doubleclick(self, widget, iter):
        "Stop doubleclick emission on folder"

        if type(self.model.get_entry(iter)) == entry.FolderEntry:
            self.stop_emission("doubleclick")

    def __cb_row_collapsed(self, object, iter, extra):
        "Updates folder icons when collapsed"

        self.model.folder_expanded(iter, False)

    def __cb_row_expanded(self, object, iter, extra):
        "Updates folder icons when expanded"

        # make sure all children are collapsed (some may have lingering expand icons)
        for i in range(self.model.iter_n_children(iter)):
            child = self.model.iter_nth_child(iter, i)

            if not self.row_expanded(self.model.get_path(child)):
                self.model.folder_expanded(child, False)

        self.model.folder_expanded(iter, True)

    def set_model(self, model):
        "Sets the model displayed by the tree view"

        TreeView.set_model(self, model)

        if model is None:
            return

        for i in range(model.iter_n_children(None)):
            model.folder_expanded(model.iter_nth_child(None, i), False)


class Statusbar(Gtk.Box):
    "An application statusbar"

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.add_css_class("statusbar")

        # Create label for status text
        self.label = Gtk.Label()
        self.label.set_halign(Gtk.Align.START)
        self.label.set_hexpand(True)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)
        self.append(self.label)

    def clear(self):
        "Clears the statusbar"

        self.label.set_text("")

    def set_status(self, text):
        "Displays a text in the statusbar"

        self.label.set_text(text or "")


# APPLICATION COMPONENTS #

class AppWindow(Gtk.ApplicationWindow):
    "An application window"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # GTK4: Show menubar by default
        self.set_show_menubar(True)


class App(Gtk.Application):
    "An application"

    def __init__(self, appname):
        Gtk.Application.__init__(self,
                                 application_id='info.olasagasti.revelation')

        self.toolbars = {}

    def __connect_menu_statusbar(self, menu):
        "Connects a menus items to the statusbar"

        if isinstance(menu, Gtk.PopoverMenu):
            pass
        else:
            pass

    def cb_menudesc(self, item, show):
        "Displays menu descriptions in the statusbar"

        if show:
            self.statusbar.set_status(item.get_label())

        else:
            self.statusbar.clear()

    def __cb_toolbar_hide(self, widget, name):
        "Hides the toolbar dock when the toolbar is hidden"

        if name in self.toolbars:
            self.toolbars[name].hide()

    def __cb_toolbar_show(self, widget, name):
        "Shows the toolbar dock when the toolbar is shown"

        if name in self.toolbars:
            self.toolbars[name].show()

    def add_toolbar(self, toolbar, name, band):
        "Adds a toolbar"

        self.toolbars[name] = toolbar
        toolbar.set_vexpand(True)
        self.main_vbox.append(toolbar)

        toolbar.connect("show", self.__cb_toolbar_show, name)
        toolbar.connect("hide", self.__cb_toolbar_hide, name)

    def get_title(self):
        "Returns the app title"

        title = Gtk.Window.get_title(self.window)

        return title.replace(" - " + config.APPNAME, "")

    def popup(self, menu, button, time):
        "Displays a popup menu"

        popover = Gtk.PopoverMenu.new_from_model(menu)
        popover.set_parent(self.window)

        self.__connect_menu_statusbar(popover)
        popover.popup()

    def set_menubar(self, menubar):
        "Sets the menubar for the application"

        # GTK4: Set menubar on the application, not the window
        Gtk.Application.set_menubar(self, menubar)

    def set_title(self, title):
        "Sets the window title"

        Gtk.Window.set_title(self.window, title + " - " + config.APPNAME)

    def set_toolbar(self, toolbar):
        "Sets the application toolbar"

        toolbar.set_vexpand(True)
        self.main_vbox.append(toolbar)
        toolbar.connect("show", self.__cb_toolbar_show, "Toolbar")
        toolbar.connect("hide", self.__cb_toolbar_hide, "Toolbar")

    def set_contents(self, widget):
        widget.set_hexpand(True)
        widget.set_vexpand(True)
        self.main_vbox.append(widget)


class EntryView(Gtk.Box):
    "A component for displaying an entry"

    def __init__(self, cfg = None, clipboard = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_spacing(12)
        apply_css_padding(self, 12)

        self.config     = cfg
        self.clipboard  = clipboard
        self.entry      = None

    def clear(self, force = False):
        "Clears the data view"

        self.entry = None

        child = self.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            child.unparent()
            child = next_child

    def display_entry(self, e):
        "Displays info about an entry"

        self.clear()
        self.entry = e

        if self.entry is None:
            return

        # set up metadata display
        metabox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        metabox.set_spacing(6)
        self.append(metabox)

        label = ImageLabel(
            "<span size=\"large\" weight=\"bold\">%s</span>" % util.escape_markup(e.name),
            e.icon
        )
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        label.set_hexpand(True)
        label.set_vexpand(True)
        metabox.append(label)

        label = Label("<span weight=\"bold\">%s</span>%s" % (e.typename + (e.description != "" and ": " or ""), util.escape_markup(e.description)), Gtk.Justification.CENTER)
        label.set_hexpand(True)
        label.set_vexpand(True)
        metabox.append(label)

        # set up field list
        fields = [field for field in e.fields if field.value != ""]

        if len(fields) > 0:
            table = Gtk.Grid()
            self.append(table)
            table.set_column_spacing(10)
            table.set_row_spacing(5)

            for rowindex, field in zip(range(len(fields)), fields):
                label = Label("<span weight=\"bold\">%s: </span>" % util.escape_markup(field.name))
                label.set_hexpand(True)
                table.attach(label, 0, rowindex, 1, 1)

                widget = generate_field_display_widget(field, self.config, self.clipboard)
                widget.set_hexpand(True)
                table.attach(widget, 1, rowindex, 1, 1)

        # notes
        label = Label("<span weight=\"bold\">%s</span>%s" % ((e.notes != "" and _("Notes: ") or ""),
                                                             util.escape_markup(e.notes)), Gtk.Justification.LEFT)
        self.append(label)

        # display updatetime
        if type(e) != entry.FolderEntry:
            label = Label((_('Updated %s ago') + "\n%s") % (util.time_period_rough(e.updated, time.time()), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.updated))), Gtk.Justification.CENTER)
            self.append(label)


    def pack_start(self, widget):
        "Adds a widget to the data view"

        widget.set_halign(Gtk.Align.CENTER)
        widget.set_valign(Gtk.Align.CENTER)
        self.append(widget)


class Searchbar(Gtk.Box):
    "A toolbar for easy searching"

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.add_css_class("toolbar")

        # Load UI from file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/searchbar.ui')

        # Get the box from UI file
        box = builder.get_object('searchbar_box')
        box.add_css_class("linked")

        # Get widgets from UI file
        self.entry = builder.get_object('search_entry')
        self.button_prev = builder.get_object('button_prev')
        self.button_next = builder.get_object('button_next')

        # Replace dropdown placeholder with EntryDropDown
        dropdown_placeholder = builder.get_object('dropdown_placeholder')
        self.dropdown = EntryDropDown()
        self.dropdown.insert_item(0, _('Any type'), "help-about")
        # Replace the placeholder in the UI
        dropdown_parent = dropdown_placeholder.get_parent()
        dropdown_placeholder.unparent()
        dropdown_parent.append(self.dropdown)

        # Add the search box to the toolbar
        self.append(box)

        self.connect("show", self.__cb_show)

        self.entry.connect("changed", self.__cb_entry_changed)
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.__cb_key_press)
        self.entry.add_controller(key_controller)

        self.button_next.set_sensitive(False)
        self.button_prev.set_sensitive(False)

    def __cb_entry_changed(self, widget, data = None):
        "Callback for entry changes"

        s = self.entry.get_text() != ""

        self.button_next.set_sensitive(s)
        self.button_prev.set_sensitive(s)

    def __cb_key_press(self, controller, keyval, keycode, state):
        "Callback for key presses"

        # return
        if keyval == Gdk.KEY_Return and self.entry.get_text() != "":
            if (state & Gdk.ModifierType.SHIFT_MASK) == Gdk.ModifierType.SHIFT_MASK:
                self.button_prev.activate()

            else:
                self.button_next.activate()

            return True
        return False

    def __cb_show(self, widget, data = None):
        "Callback for widget display"

        self.entry.select_region(0, -1)
        self.entry.grab_focus()
