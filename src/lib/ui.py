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
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, Gdk, Gio, Pango  # noqa: E402

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
STOCK_ENTRY_CREDITCARD  = "x-office-contact"    # "revelation-account-creditcard"
STOCK_ENTRY_CRYPTOKEY   = "dialog-password"     # "revelation-account-cryptokey"
STOCK_ENTRY_DATABASE    = "server-database"     # "revelation-account-database"
STOCK_ENTRY_DOOR        = "changes-allow"       # "revelation-account-door"
STOCK_ENTRY_EMAIL       = "emblem-mail"         # "revelation-account-email"
STOCK_ENTRY_FTP         = "system-file-manager"  # "revelation-account-ftp"
STOCK_ENTRY_GENERIC     = "document-new"        # "revelation-account-generic"
STOCK_ENTRY_PHONE       = "phone"               # "revelation-account-phone"
STOCK_ENTRY_SHELL       = "utilities-terminal"  # "revelation-account-shell"
STOCK_ENTRY_REMOTEDESKTOP = "preferences-desktop-remote-desktop"  # "revelation-account-remotedesktop"
STOCK_ENTRY_WEBSITE     = "web-browser"         # "revelation-account-website"


ICON_SIZE_APPLET        = Gtk.IconSize.LARGE_TOOLBAR
ICON_SIZE_DATAVIEW      = Gtk.IconSize.LARGE_TOOLBAR
ICON_SIZE_DROPDOWN      = Gtk.IconSize.SMALL_TOOLBAR
ICON_SIZE_ENTRY         = Gtk.IconSize.MENU
ICON_SIZE_FALLBACK      = Gtk.IconSize.LARGE_TOOLBAR
ICON_SIZE_HEADLINE      = Gtk.IconSize.LARGE_TOOLBAR
ICON_SIZE_LABEL         = Gtk.IconSize.MENU
ICON_SIZE_LOGO          = Gtk.IconSize.DND
ICON_SIZE_TREEVIEW      = Gtk.IconSize.MENU

STOCK_ICONS = (
    (STOCK_ENTRY_CREDITCARD,   "contact-new",          (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_CRYPTOKEY,    "dialog-password",      (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_DATABASE,     "package_system",       (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_DOOR,         "changes-allow",        (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_EMAIL,        "emblem-mail",          (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_FTP,          "system-file-manager",  (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_GENERIC,      "document-new",         (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_PHONE,        "phone",                (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_SHELL,        "utilities-terminal",   (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_REMOTEDESKTOP, "preferences-desktop-remote-desktop", (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_WEBSITE,      "web-browser",          (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_FOLDER,       "folder",               (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
    (STOCK_ENTRY_FOLDER_OPEN,  "folder-open",          (ICON_SIZE_DATAVIEW, ICON_SIZE_DROPDOWN, ICON_SIZE_ENTRY, ICON_SIZE_TREEVIEW)),
)

STOCK_ITEMS = (
    (STOCK_CONTINUE,       _('_Continue'),     "stock_test-mode"),
    (STOCK_DISCARD,        _('_Discard'),      Gtk.STOCK_DELETE),
    (STOCK_EDIT,           _('_Edit'),         Gtk.STOCK_EDIT),
    (STOCK_EXPORT,         _('_Export'),       Gtk.STOCK_EXECUTE),
    (STOCK_FOLDER,         '',                 "stock_folder"),
    (STOCK_GENERATE,       _('_Generate'),     Gtk.STOCK_EXECUTE),
    (STOCK_GOTO,           _('_Go to'),        Gtk.STOCK_JUMP_TO),
    (STOCK_IMPORT,         _('_Import'),       Gtk.STOCK_CONVERT),
    (STOCK_LOCK,           _('_Lock'),         "stock_lock"),
    (STOCK_NEW_ENTRY,      _('_Add Entry'),    Gtk.STOCK_ADD),
    (STOCK_NEW_FOLDER,     _('_Add Folder'),   "stock_folder"),
    (STOCK_NEXT,           _('Next'),          Gtk.STOCK_GO_DOWN),
    (STOCK_PASSWORD_CHANGE, _('_Change'),       "stock_lock-ok"),
    (STOCK_PASSWORD_CHECK, _('_Check'),        "stock_lock-ok"),
    (STOCK_PASSWORD_STRONG, '',                 "stock_lock-ok"),
    (STOCK_PASSWORD_WEAK,  '',                 "stock_lock-broken"),
    (STOCK_PREVIOUS,       _('Previous'),      Gtk.STOCK_GO_UP),
    (STOCK_RELOAD,         _('_Reload'),       Gtk.STOCK_REFRESH),
    (STOCK_REMOVE,         _('Re_move'),       Gtk.STOCK_DELETE),
    (STOCK_REPLACE,        _('_Replace'),      Gtk.STOCK_SAVE_AS),
    (STOCK_UNKNOWN,        _('Unknown'),       "dialog-question"),
    (STOCK_UNLOCK,         _('_Unlock'),       "stock_lock-open"),
    (STOCK_UPDATE,         _('_Update'),       "stock_edit"),
)


# EXCEPTIONS #

class DataError(Exception):
    "Exception for invalid data"
    pass


# FUNCTIONS #

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
        widget = Gtk.ComboBox.new_with_entry()
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

    widget.model = Gtk.ListStore(GObject.TYPE_STRING)
    widget.set_model(widget.model)
    widget.set_entry_text_column(0)

    widget.completion = Gtk.EntryCompletion()
    widget.completion.set_model(widget.model)
    widget.completion.set_text_column(0)
    widget.completion.set_minimum_key_length(1)
    widget.entry.set_completion(widget.completion)

    def set_values(vlist):
        "Sets the values for the dropdown"

        widget.model.clear()

        for item in vlist:
            widget.model.append((item,))

    widget.set_values = set_values

    if userdata is not None:
        widget.set_values(userdata)


# CONTAINERS #



class Toolbar(Gtk.Toolbar):
    "A Toolbar subclass"

    def append_space(self):
        "Appends a space to the toolbar"

        space = Gtk.SeparatorToolItem()
        space.set_draw(False)

        self.insert(space, -1)

    def append_widget(self, widget, tooltip = None):
        "Appends a widget to the toolbar"

        toolitem = Gtk.ToolItem()
        toolitem.add(widget)

        if tooltip != None:
            toolitem.set_tooltip_text(tooltip)

        self.insert(toolitem, -1)


class InputSection(Gtk.Box):
    "A section of input fields"

    def __init__(self, title = None, description = None, sizegroup = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.set_border_width(0)

        self.title  = None
        self.desc   = None
        self.sizegroup  = sizegroup

        if title is not None:
            self.title = Label("<span weight=\"bold\">%s</span>" % util.escape_markup(title))
            self.pack_start(self.title, False, True, 0)

        if description is not None:
            self.desc = Label(util.escape_markup(description))
            self.pack_start(self.desc, False, True, 0)

        if sizegroup is None:
            self.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

    def append_widget(self, title, widget, indent = True):
        "Adds a widget to the section"

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.set_spacing(12)
        row.set_border_width(0)
        self.pack_start(row, False, False, 0)

        if self.title is not None and indent == True:
            row.pack_start(Label(""), False, False, 0)

        if title is not None:
            label = Label("%s:" % util.escape_markup(title))
            self.sizegroup.add_widget(label)
            row.pack_start(label, False, False, 0)

        row.pack_start(widget, True, True, 0)

    def clear(self):
        "Removes all widgets"

        for child in self.get_children():
            if child not in (self.title, self.desc):
                child.destroy()


# DISPLAY WIDGETS #

class ImageLabel(Gtk.Box):
    "A label with an image"

    def __init__(self, text = None, stock = None, size = ICON_SIZE_LABEL):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)
        self.set_border_width(0)

        self.image = Gtk.Image()
        self.pack_start(self.image, False, True, 0)

        self.label = Label(text)
        self.pack_start(self.label, True, True, 0)

        if text != None:
            self.set_text(text)

        if stock != None:
            self.set_stock(stock, size)

    def set_ellipsize(self, ellipsize):
        "Sets label ellisization"

        self.label.set_ellipsize(ellipsize)

    def set_stock(self, stock, size):
        "Sets the image"

        self.image.set_from_icon_name(stock, size)

    def set_text(self, text):
        "Sets the label text"

        self.label.set_text(text)


class Label(Gtk.Label):
    "A text label"

    def __init__(self, text = None, justify = Gtk.Justification.LEFT):
        Gtk.Label.__init__(self)

        self.set_text(text)
        self.set_justify(justify)
        self.set_use_markup(True)
        self.set_line_wrap(True)

        self.set_valign(Gtk.Align.CENTER)
        if justify == Gtk.Justification.LEFT:
            self.set_halign(Gtk.Align.START)

        elif justify == Gtk.Justification.CENTER:
            self.set_halign(Gtk.Align.CENTER)

        elif justify == Gtk.Justification.RIGHT:
            self.set_halign(Gtk.Align.END)

    def set_text(self, text):
        "Sets the text of the label"

        if text is None:
            Gtk.Label.set_text(self, "")

        else:
            Gtk.Label.set_markup(self, text)


class PasswordLabel(Gtk.EventBox):
    "A label for displaying passwords"

    def __init__(self, password = "", cfg = None, clipboard = None, justify = Gtk.Justification.LEFT):  # nosec
        Gtk.EventBox.__init__(self)

        self.password   = util.unescape_markup(password)
        self.config = cfg
        self.clipboard  = clipboard

        self.label = Label(util.escape_markup(self.password), justify)
        self.label.set_selectable(True)
        self.add(self.label)

        self.show_password(cfg.get_boolean("view-passwords"))
        self.config.connect('changed::view-passwords', lambda w, k: self.show_password(w.get_boolean(k)))

        self.connect("button-press-event", self.__cb_button_press)
        self.connect("drag-data-get", self.__cb_drag_data_get)

    def __cb_drag_data_get(self, widget, context, selection, info, timestamp, data = None):
        "Provides data for a drag operation"

        selection.set_text(self.password, -1)

    def __cb_button_press(self, widget, data = None):
        "Populates the popup menu"

        if self.label.get_selectable() == True:
            return False

        elif data.button == 3:
            menu = Menu()

            menuitem = ImageMenuItem(Gtk.STOCK_COPY, _('Copy password'))
            menuitem.connect("activate", lambda w: self.clipboard.set([self.password], True))
            menu.append(menuitem)

            menu.show_all()
            menu.popup_at_pointer(data)

            return True

    def set_ellipsize(self, ellipsize):
        "Sets ellipsize for the label"

        self.label.set_ellipsize(ellipsize)

    def show_password(self, show = True):
        "Sets whether to display the password"

        if show == True:
            self.label.set_text(util.escape_markup(self.password))
            self.label.set_selectable(True)
            self.drag_source_unset()

        else:
            self.label.set_text(Gtk.Entry().get_invisible_char()*6)
            self.label.set_selectable(False)

            self.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK,
                [
                    Gtk.TargetEntry.new("text/plain",    0, 0),
                    Gtk.TargetEntry.new("TEXT",          0, 1),
                    Gtk.TargetEntry.new("STRING",        0, 2),
                    Gtk.TargetEntry.new("COMPOUND TEXT", 0, 3),
                    Gtk.TargetEntry.new("UTF8_STRING",   0, 4)
                ],
                Gdk.DragAction.COPY
            )


class EditableTextView(Gtk.ScrolledWindow):
    "An editable text view"

    def __init__(self, buffer = None, text = None):

        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        self.textview = Gtk.TextView(buffer=buffer)
        self.textbuffer = self.textview.get_buffer()
        self.add(self.textview)

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
        self.modify_font(Pango.FontDescription("Monospace"))

        if text is not None:
            self.get_buffer().set_text(text)


# TEXT ENTRIES #

class Entry(Gtk.Entry):
    "A normal text entry"

    def __init__(self, text = None):
        Gtk.Entry.__init__(self)

        self.set_activates_default(True)
        self.set_text(text)

    def set_text(self, text):
        "Sets the entry contents"

        if text is None:
            text = ""

        Gtk.Entry.set_text(self, text)


class FileEntry(Gtk.Box):
    "A file entry"

    def __init__(self, title = None, file = None, type = Gtk.FileChooserAction.OPEN):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)
        self.set_border_width(0)

        self.title = title is not None and title or _('Select File')
        self.type = type

        self.entry = Entry()
        self.entry.connect("changed", lambda w: self.emit("changed"))
        self.pack_start(self.entry, True, True, 0)

        self.button = Gtk.Button(label=_('Browse...'))
        self.button.connect("clicked", self.__cb_filesel)
        self.pack_start(self.button, False, False, 0)

        if file is not None:
            self.set_filename(file)

    def __cb_filesel(self, widget, data = None):
        "Displays a file selector when Browse is pressed"

        try:
            fsel = dialog.FileSelector(None, self.title, self.type)
            file = self.get_filename()

            if file != None:
                fsel.set_filename(file)

            self.set_filename(fsel.run())

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
        if password:
            self.set_text(password)

        self.autocheck  = True
        self.config = cfg
        self.clipboard  = clipboard

        self.connect("changed", self.__cb_check_password)
        self.connect("populate-popup", self.__cb_popup)

        if cfg != None:
            self.config.bind('view-passwords', self, "visibility", Gio.SettingsBindFlags.DEFAULT)

    def __cb_check_password(self, widget, data = None):
        "Callback for changed, checks the password"

        if self.autocheck == False:
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

    def __cb_popup(self, widget, menu):
        "Populates the popup menu"

        if self.clipboard != None:
            menuitem = ImageMenuItem(Gtk.STOCK_COPY, _('Copy password'))
            menuitem.connect("activate", lambda w: self.clipboard.set([self.get_text()], True))

            menu.insert(menuitem, 2)

        menu.show_all()

    def set_password_strong(self, strong, reason = ""):
        "Sets whether the password is strong or not"

        self.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, strong and STOCK_PASSWORD_STRONG or STOCK_PASSWORD_WEAK)
        self.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, reason)


class PasswordEntryGenerate(Gtk.Box):
    "A password entry with a generator button"

    def __init__(self, password = None, cfg = None, clipboard = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_spacing(6)
        self.set_border_width(0)
        self.config = cfg

        self.pwentry = PasswordEntry(password, cfg, clipboard)
        self.pack_start(self.pwentry, True, True, 0)

        self.button = Gtk.Button(label=_('Generate'))
        self.button.connect("clicked", lambda w: self.generate())
        self.pack_start(self.button, False, False, 0)

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


class SpinEntry(Gtk.SpinButton):
    "An entry for numbers"

    def __init__(self, adjustment = None, climb_rate = 0.0, digits = 0):
        Gtk.SpinButton.__init__(self)
        self.configure(adjustment, climb_rate, digits)

        self.set_increments(1, 5)
        self.set_range(0, 100000)
        self.set_numeric(True)


# BUTTONS #

class DropDown(Gtk.ComboBox):
    "A dropdown button"

    def __init__(self, icons = False):
        Gtk.ComboBox.__init__(self)

        self.model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)
        self.set_model(self.model)

        if icons == True:
            cr = Gtk.CellRendererPixbuf()
            cr.set_fixed_size(Gtk.icon_size_lookup(ICON_SIZE_DROPDOWN)[1] + 5, -1)
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

    def delete_item(self, index):
        "Removes an item from the dropdown"

        if self.model.iter_n_children(None) > index:
            iter = self.model.iter_nth_child(None, index)
            self.model.remove(iter)

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

        for i in range(self.model.iter_n_children(None)):
            iter = self.model.iter_nth_child(None, i)

            if self.model.get_value(iter, 2) == entrytype:
                self.set_active(i)


class FileButton(Gtk.FileChooserButton):
    "A file chooser button"

    def __init__(self, title = None, file = None, type = Gtk.FileChooserAction.OPEN):
        Gtk.FileChooserButton.__init__(self, title)
        self.set_action(type)
        self.set_local_only(False)

        if file != None:
            self.set_filename(file)

    def get_filename(self):
        "Gets the filename"

        return io.file_normpath(self.get_uri())

    def set_filename(self, filename):
        "Sets the filename"

        filename = io.file_normpath(filename)

        if filename != io.file_normpath(self.get_filename()):
            Gtk.FileChooserButton.set_filename(self, filename)


class LinkButton(Gtk.LinkButton):
    "A link button"

    def __init__(self, url, label):
        Gtk.LinkButton.__init__(self, uri=url, label=label)
        self.set_halign(Gtk.Align.START)

        self.label = self.get_children()[0]

        "If URI is too long reduce it for the label"
        if len(label) > 60:
            self.label.set_text(label[0:59] + " (...)")

    def set_ellipsize(self, ellipsize):
        "Sets ellipsize for label"

        self.label.set_ellipsize(ellipsize)

    def set_justify(self, justify):
        "Sets justify for label"

        self.label.set_justify(justify)


# MENUS AND MENU ITEMS #

class ImageMenuItem(Gtk.MenuItem):
    "A menuitem with an icon"

    def __init__(self, stock, text = None):
        Gtk.MenuItem.__init__(self)

        # Create a horizontal box for image and label
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_spacing(6)

        # Create and add image
        self.image = Gtk.Image()
        self.image.set_from_icon_name(stock, Gtk.IconSize.MENU)
        box.pack_start(self.image, False, False, 0)

        # Create and add label
        self.label = Gtk.Label()
        if text is not None:
            self.label.set_text(text)
        else:
            # Try to get text from stock icon name
            self.label.set_text("")
        box.pack_start(self.label, True, True, 0)

        # Add box to menuitem
        self.add(box)

    def set_stock(self, stock):
        "Set the stock item to use as icon"

        self.image.set_from_icon_name(stock, Gtk.IconSize.MENU)

    def set_text(self, text):
        "Set the item text"

        self.label.set_text(text)


class Menu(Gtk.Menu):
    "A menu"

    def __init__(self):
        Gtk.Menu.__init__(self)


# MISCELLANEOUS WIDGETS #

class TreeView(Gtk.TreeView):
    "A tree display"

    def __init__(self, model):
        Gtk.TreeView.__init__(self, model=model)
        self.set_headers_visible(False)
        self.model = model

        self.__cbid_drag_motion = None
        self.__cbid_drag_end    = None

        self.selection = self.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.connect("button-press-event", self.__cb_buttonpress)
        self.connect("key-press-event", self.__cb_keypress)

    def __cb_buttonpress(self, widget, data):
        "Callback for handling mouse clicks"

        path = self.get_path_at_pos(int(data.x), int(data.y))

        # handle click outside entry
        if path is None:
            self.unselect_all()

        # handle doubleclick
        if data.button == 1 and data.type == Gdk.EventType._2BUTTON_PRESS and path != None:
            iter = self.model.get_iter(path[0])
            self.toggle_expanded(iter)

            if iter != None:
                self.emit("doubleclick", iter)

        # display popup on right-click
        elif data.button == 3:
            if path != None and self.selection.iter_is_selected(self.model.get_iter(path[0])) == False:
                self.set_cursor(path[0], path[1], False)

            self.emit("popup", data)

            return True

        # handle drag-and-drop of multiple rows
        elif self.__cbid_drag_motion is None and data.button in (1, 2) and data.type == Gdk.EventType.BUTTON_PRESS and path != None and self.selection.iter_is_selected(self.model.get_iter(path[0])) == True and len(self.get_selected()) > 1:
            self.__cbid_drag_motion = self.connect("motion-notify-event", self.__cb_drag_motion, data.copy())
            self.__cbid_drag_end = self.connect("button-release-event", self.__cb_button_release, data.copy())

            return True

    def __cb_button_release(self, widget, data, userdata = None):
        "Ends a drag"

        self.emit("button-press-event", userdata)
        self.__drag_check_end()

    def __cb_drag_motion(self, widget, data, userdata = None):
        "Monitors drag motion"

        if self.drag_check_threshold(int(userdata.x), int(userdata.y), int(data.x), int(data.y)) == True:
            self.__drag_check_end()
            uritarget = Gtk.TargetEntry.new("revelation/treerow", Gtk.TargetFlags.SAME_APP | Gtk.TargetFlags.SAME_WIDGET, 0)
            self.drag_begin_with_coordinates(Gtk.TargetList([uritarget]), Gdk.DragAction.MOVE, userdata.button.button, userdata, userdata.x, userdata.y)

    def __cb_keypress(self, widget, data = None):
        "Callback for handling key presses"

        # expand/collapse node on space
        if data.keyval == Gdk.KEY_space:
            self.toggle_expanded(self.get_active())

    def __drag_check_end(self):
        "Ends a drag check"

        self.disconnect(self.__cbid_drag_motion)
        self.disconnect(self.__cbid_drag_end)

        self.__cbid_drag_motion = None
        self.__cbid_drag_end = None

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

        if iter is None or self.selection.iter_is_selected(iter) == False:
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
        cr.set_property("stock-size", ICON_SIZE_TREEVIEW)

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

            if self.row_expanded(self.model.get_path(child)) == False:
                self.model.folder_expanded(child, False)

        self.model.folder_expanded(iter, True)

    def set_model(self, model):
        "Sets the model displayed by the tree view"

        TreeView.set_model(self, model)

        if model is None:
            return

        for i in range(model.iter_n_children(None)):
            model.folder_expanded(model.iter_nth_child(None, i), False)


class Statusbar(Gtk.Statusbar):
    "An application statusbar"

    def __init__(self):
        Gtk.Statusbar.__init__(self)
        self.contextid = self.get_context_id("statusbar")

    def clear(self):
        "Clears the statusbar"

        self.pop(self.contextid)

    def set_status(self, text):
        "Displays a text in the statusbar"

        self.clear()
        self.push(self.contextid, text or "")


# APPLICATION COMPONENTS #

class AppWindow(Gtk.ApplicationWindow):
    "An application window"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class App(Gtk.Application):
    "An application"

    def __init__(self, appname):
        Gtk.Application.__init__(self,
                                 application_id='info.olasagasti.revelation')

        self.toolbars = {}

    def __connect_menu_statusbar(self, menu):
        "Connects a menus items to the statusbar"

        for item in menu.get_children():
            if isinstance(item, Gtk.MenuItem) == True:
                item.connect("select", self.cb_menudesc, True)
                item.connect("deselect", self.cb_menudesc, False)

    def cb_menudesc(self, item, show):
        "Displays menu descriptions in the statusbar"

        if show == True:
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
        self.main_vbox.pack_start(toolbar, False, True, 0)

        toolbar.connect("show", self.__cb_toolbar_show, name)
        toolbar.connect("hide", self.__cb_toolbar_hide, name)

        toolbar.show_all()

    def get_title(self):
        "Returns the app title"

        title = Gtk.Window.get_title(self.window)

        return title.replace(" - " + config.APPNAME, "")

    def popup(self, menu, button, time):
        "Displays a popup menu"

        # get Gtk.Menu
        gmenu = Gtk.Menu.new_from_model(menu)
        gmenu.attach_to_widget(self.window, None)

        # transfer the tooltips from Gio.Menu to Gtk.Menu
        menu_item_index = 0
        menu_items = gmenu.get_children()
        for sect in range(menu.get_n_items()):
            for item in range(menu.get_item_link(sect, 'section').get_n_items()):
                tooltip_text = menu.get_item_link(sect, 'section').get_item_attribute_value(item, 'tooltip', None)
                if tooltip_text:
                    tooltip_text = tooltip_text.unpack()
                menu_items[menu_item_index].set_tooltip_text(tooltip_text)
                menu_item_index += 1
            # skip section separator
            menu_item_index += 1

        self.__connect_menu_statusbar(gmenu)
        gmenu.popup_at_pointer()

    def set_menus(self, menubar):
        "Sets the menubar for the application"

        for item in menubar.get_children():
            self.__connect_menu_statusbar(item.get_submenu())

        self.main_vbox.pack_start(menubar, False, True, 0)

    def set_title(self, title):
        "Sets the window title"

        Gtk.Window.set_title(self.window, title + " - " + config.APPNAME)

    def set_toolbar(self, toolbar):
        "Sets the application toolbar"

        self.main_vbox.pack_start(toolbar, False, True, 0)
        toolbar.connect("show", self.__cb_toolbar_show, "Toolbar")
        toolbar.connect("hide", self.__cb_toolbar_hide, "Toolbar")

    def set_contents(self, widget):
        self.main_vbox.pack_start(widget, True, True, 0)


class EntryView(Gtk.Box):
    "A component for displaying an entry"

    def __init__(self, cfg = None, clipboard = None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.set_spacing(12)
        self.set_border_width(12)

        self.config     = cfg
        self.clipboard  = clipboard
        self.entry      = None

    def clear(self, force = False):
        "Clears the data view"

        self.entry = None

        for child in self.get_children():
            child.destroy()

    def display_entry(self, e):
        "Displays info about an entry"

        self.clear()
        self.entry = e

        if self.entry is None:
            return

        # set up metadata display
        metabox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        metabox.set_spacing(6)
        metabox.set_border_width(0)
        self.pack_start(metabox)

        label = ImageLabel(
            "<span size=\"large\" weight=\"bold\">%s</span>" % util.escape_markup(e.name),
            e.icon, ICON_SIZE_DATAVIEW
        )
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        metabox.pack_start(label, True, True, 0)

        label = Label("<span weight=\"bold\">%s</span>%s" % (e.typename + (e.description != "" and ": " or ""), util.escape_markup(e.description)), Gtk.Justification.CENTER)
        metabox.pack_start(label, True, True, 0)

        # set up field list
        fields = [field for field in e.fields if field.value != ""]

        if len(fields) > 0:
            table = Gtk.Grid()
            self.pack_start(table)
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
        self.pack_start(label)

        # display updatetime
        if type(e) != entry.FolderEntry:
            label = Label((_('Updated %s ago') + "\n%s") % (util.time_period_rough(e.updated, time.time()), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.updated))), Gtk.Justification.CENTER)
            self.pack_start(label)

        self.show_all()

    def pack_start(self, widget):
        "Adds a widget to the data view"

        widget.set_halign(Gtk.Align.CENTER)
        widget.set_valign(Gtk.Align.CENTER)
        Gtk.Box.pack_start(self, widget, False, False, 0)


class Searchbar(Toolbar):
    "A toolbar for easy searching"

    def __init__(self):
        Toolbar.__init__(self)

        # Load UI from file
        builder = Gtk.Builder()
        builder.add_from_resource('/info/olasagasti/revelation/ui/searchbar.ui')

        # Get the box from UI file
        box = builder.get_object('searchbar_box')
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

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
        dropdown_parent.remove(dropdown_placeholder)
        dropdown_parent.pack_start(self.dropdown, False, False, 0)
        dropdown_parent.show_all()

        self.append_widget(box)

        self.connect("show", self.__cb_show)

        self.entry.connect("changed", self.__cb_entry_changed)
        self.entry.connect("key-press-event", self.__cb_key_press)

        self.button_next.set_sensitive(False)
        self.button_prev.set_sensitive(False)

    def __cb_entry_changed(self, widget, data = None):
        "Callback for entry changes"

        s = self.entry.get_text() != ""

        self.button_next.set_sensitive(s)
        self.button_prev.set_sensitive(s)

    def __cb_key_press(self, widget, data = None):
        "Callback for key presses"

        # return
        if data.keyval == Gdk.KEY_Return and widget.get_text() != "":
            if (data.state & Gdk.ModifierType.SHIFT_MASK) == Gdk.ModifierType.SHIFT_MASK:
                self.button_prev.activate()

            else:
                self.button_next.activate()

            return True

    def __cb_show(self, widget, data = None):
        "Callback for widget display"

        self.entry.select_region(0, -1)
        self.entry.grab_focus()
