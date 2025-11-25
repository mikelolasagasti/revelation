#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module with dialogs
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

from . import config, datahandler, entry, io, ui, util

import gettext
import logging
from weakref import WeakValueDictionary
from gi.repository import GObject, Gtk, Gio, Gdk, GLib

from revelation import config, datahandler, entry, io, ui, util

_ = gettext.gettext
logger = logging.getLogger(__name__)

# Track visible dialogs to prevent duplicates (using WeakValueDictionary for automatic cleanup)
_visible_dialogs: WeakValueDictionary[type, Gtk.Dialog] = WeakValueDictionary()


# EXCEPTIONS #

class CancelError(Exception):
    """Exception for dialog cancellations"""
    pass


# BASE DIALOGS #

class Dialog(Gtk.Dialog):
    """
    Base class for dialogs in GTK4.
    Refactored to support async callbacks and validation loops.
    """

    def __init__(self, parent, title):
        super().__init__(title=title)

        self._response_callback = None

        self.set_modal(True)
        if isinstance(parent, Gtk.Window):
            self.set_transient_for(parent)
        self.set_resizable(False)

        # Default size to prevent tiny dialogs
        self.set_default_size(450, -1)

        content_area = self.get_content_area()
        ui.apply_css_padding(content_area, 12)
        content_area.set_spacing(12)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.__cb_keypress)
        self.add_controller(key_controller)

        self.connect("close-request", self._on_close_request)

    def __cb_keypress(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self._handle_response(Gtk.ResponseType.CANCEL)
            return True
        return False

    def _on_close_request(self, dialog):
        self._handle_response(Gtk.ResponseType.CANCEL)
        return True

    def _ensure_button_box_at_end(self):
        """Ensures the button box is visually at the bottom of the content area."""
        if hasattr(self, '_button_box') and self._button_box:
            content_area = self.get_content_area()
            parent = self._button_box.get_parent()

            if parent == content_area:
                parent.reorder_child_after(self._button_box, parent.get_last_child())
            else:
                if parent:
                    parent.remove(self._button_box)
                content_area.append(self._button_box)

    def load_ui_section(self, resource_path, object_name, pack=True):
        """Load a UI section from a resource file"""
        builder = Gtk.Builder()
        builder.set_translation_domain("revelation")
        try:
            builder.add_from_resource(resource_path)
        except GLib.Error as e:
            print(f"ERROR loading resource {resource_path}: {e}")
            return builder, None

        section = builder.get_object(object_name)

        if pack and section:
            content_area = self.get_content_area()
            section.set_hexpand(True)
            content_area.append(section)
            self._ensure_button_box_at_end()
        elif pack and section is None:
            print(f"WARNING: UI Object '{object_name}' not found in '{resource_path}'")

        return builder, section

    def add_button(self, label, response_id):
        if not hasattr(self, '_buttons'):
            self._buttons = {}

        if not hasattr(self, '_button_box'):
            self._button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            self._button_box.add_css_class("dialog-action-box")
            self._button_box.set_halign(Gtk.Align.END)
            self._button_box.set_margin_top(12)
            self.get_content_area().append(self._button_box)

        button = Gtk.Button.new_with_mnemonic(label)
        button.connect("clicked", lambda w: self._handle_response(response_id))

        self._button_box.append(button)
        self._buttons[response_id] = button

        self._ensure_button_box_at_end()
        return button

    def set_default_response(self, response_id):
        if hasattr(self, '_buttons') and response_id in self._buttons:
            btn = self._buttons[response_id]
            btn.grab_focus()
            btn.add_css_class("suggested-action")
            self.set_default_widget(btn)

    def get_widget_for_response(self, response_id):
        if hasattr(self, '_buttons') and response_id in self._buttons:
            return self._buttons[response_id]
        return None

    def connect_response(self, callback):
        self._response_callback = callback

    def _handle_response(self, response_id):
        keep_open = False
        if self._response_callback:
            try:
                keep_open = bool(self._response_callback(self, response_id))
            except CancelError:
                keep_open = False
            except Exception as e:
                logger.exception(f"Error in dialog callback: {e}")
                keep_open = False

        if not keep_open:
            self.destroy()


def load_ui_builder(resource_path):
    builder = Gtk.Builder()
    builder.set_translation_domain("revelation")
    builder.add_from_resource(resource_path)
    return builder


def replace_widget(builder, object_id, new_widget):
    ui_widget = builder.get_object(object_id)
    if ui_widget:
        widget_parent = ui_widget.get_parent()
        if widget_parent:
            widget_parent.remove(ui_widget)
            new_widget.set_hexpand(True)
            new_widget.set_vexpand(True)
            widget_parent.append(new_widget)
    return new_widget


def set_section_title(builder, object_id, text):
    title = builder.get_object(object_id)
    if title:
        title.set_markup(f"<span weight='bold'>{util.escape_markup(text)}</span>")


def get_entry(builder, object_id):
    entry = builder.get_object(object_id)
    if entry:
        entry.set_activates_default(True)
    return entry


class Utility(Dialog):
    """A utility dialog"""

    def __init__(self, parent, title):
        super().__init__(parent, title)
        self.set_resizable(False)
        self.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

    def add_section(self, title, description=None):
        section = ui.InputSection(title, description, self.sizegroup)
        self.get_content_area().append(section)
        self._ensure_button_box_at_end()
        return section


class Message(Dialog):
    """A message dialog"""

    def __init__(self, parent, title, text, stockimage):
        super().__init__(parent, title)
        self.set_resizable(False)

        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/message.ui', 'message_hbox')

        image = builder.get_object('message_image')
        if image:
            if stockimage:
                image.set_from_icon_name(stockimage)
            else:
                image.set_visible(False)

        label = builder.get_object('message_label')
        if label:
            markup = f"<span size='larger' weight='bold'>{util.escape_markup(title)}</span>\n\n{text}"
            label.set_markup(markup)

        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)


class Warning(Message):
    def __init__(self, parent, title, text):
        super().__init__(parent, title, text, "dialog-warning")


# QUESTION DIALOGS #

class FileChanged(Warning):
    def __init__(self, parent, filename):
        display_name = io.file_get_display_name(filename) if filename else _("Untitled file")
        super().__init__(parent, _("File changed"),
                         _("The file '%s' has changed on disk.") % display_name)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_RELOAD, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)


class FileChanges(Warning):
    def __init__(self, parent, title, text):
        super().__init__(parent, title, text)
        self.add_button(_("_Discard"), Gtk.ResponseType.ACCEPT)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Save"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)


class FileChangesNew(FileChanges):
    def __init__(self, parent):
        super().__init__(
            parent,
            _("Save changes to current file?"),
            _("You have made changes which have not been saved. If you create a new file without saving then these changes will be lost.")
        )


class FileChangesOpen(FileChanges):
    def __init__(self, parent):
        super().__init__(
            parent,
            _('Save changes before opening?'),
            _('You have made changes which have not been saved. If you open a different file without saving then these changes will be lost.')
        )


class FileChangesQuit(FileChanges):
    def __init__(self, parent):
        super().__init__(
            parent,
            _('Save changes before quitting?'),
            _('You have made changes which have not been saved. If you quit without saving, then these changes will be lost.')
        )


class FileChangesClose(FileChanges):
    def __init__(self, parent):
        super().__init__(
            parent,
            _('Save changes before closing?'),
            _('You have made changes which have not been saved. If you close without saving, then these changes will be lost.')
        )


class FileReplace(Warning):
    def __init__(self, parent, file):
        display_name = io.file_get_display_name(file) if file else _("Untitled file")
        super().__init__(parent, _("Replace file?"),
                         _("File '%s' already exists. Do you want to overwrite it?") % display_name)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Replace"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.CANCEL)


class FileSaveInsecure(Warning):
    def __init__(self, parent):
        super().__init__(parent, _("Save insecure password?"),
                         _("You are about to save a password to an unencrypted file. Are you sure you want to continue?"))
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Save"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.CANCEL)


# FILE SELECTION DIALOGS #

class FileSelector:
    """
    DEPRECATED: Use open_file_selector_async() or save_file_selector_async() instead.
    This class is kept for backward compatibility.
    """
    def __init__(self, parent, title, action=Gtk.FileChooserAction.OPEN):
        self.parent = parent
        self.title = title
        self.action = action

    def get_filename(self):
        return None

    def run(self):
        """DEPRECATED: This method blocks. Use async functions instead."""
        raise NotImplementedError("FileSelector.run() is deprecated. Use open_file_selector_async() or save_file_selector_async() instead.")


# FileChooserDialog classes removed - replaced with Gtk.FileDialog in async functions below
# These classes are kept for backward compatibility but deprecated
class ExportFileSelector:
    """DEPRECATED: Use export_file_selector_async() instead"""
    pass


class ImportFileSelector:
    """DEPRECATED: Use import_file_selector_async() instead"""
    pass


class OpenFileSelector:
    """DEPRECATED: Use open_file_selector_async() instead"""
    pass


class SaveFileSelector:
    """DEPRECATED: Use save_file_selector_async() instead"""
    pass


# PASSWORD DIALOGS #

class Password(Message):
    def __init__(self, parent, title, text, stock=_("_OK")):
        super().__init__(parent, title, text, "dialog-password")
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.entries = {}

    def add_entry(self, name, entry_widget=None):
        if entry_widget is None:
            entry_widget = ui.Entry()
            entry_widget.set_visibility(False)
            entry_widget.set_activates_default(True)

        self.entries[name] = entry_widget

        content = self.get_content_area()
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.append(Gtk.Label(label=f"{name}:"))
        row.append(entry_widget)
        content.append(row)
        self._ensure_button_box_at_end()
        return entry_widget


class PasswordChange(Password):
    def __init__(self, parent, password=None):
        Dialog.__init__(self, parent, _("Change password"))
        self.set_resizable(False)

        # CORRECT ID: password_section (matches XML)
        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/password-change.ui', 'password_section', pack=True)

        self.entry_current = builder.get_object('current_password_entry')
        self.entry_old_row = builder.get_object('current_password_row')
        self.entry_new = builder.get_object('new_password_entry')
        self.entry_confirm = builder.get_object('confirm_password_entry')

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_PASSWORD_CHANGE, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        if password is None and self.entry_old_row:
            self.entry_old_row.set_visible(False)
            self.entry_current = None


class PasswordLock(Password):
    def __init__(self, parent, password):
        Dialog.__init__(self, parent, _("Locked"))
        self.set_resizable(False)

        # CORRECT ID: password_section (matches XML)
        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/password-lock.ui', 'password_section')

        self.entry_password = builder.get_object('password_entry')
        self.entry_password.set_activates_default(True)

        self.add_button(_("_Quit"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_UNLOCK, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)


class PasswordOpen(Password):
    def __init__(self, parent, filename):
        Dialog.__init__(self, parent, _("Password required"))
        self.set_resizable(False)

        # Use XML layout to ensure correct structure and IDs
        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/password-open.ui', 'password_section')

        self.entry_password = builder.get_object('password_entry')
        if self.entry_password:
            self.entry_password.set_activates_default(True)

        text = _("Enter the password for '%s'") % io.file_get_display_name(filename)
        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_margin_bottom(10)

        if _section:
            _section.prepend(label)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)


class PasswordSave(Password):
    def __init__(self, parent, filename):
        Dialog.__init__(self, parent, _("Password required"))
        self.set_resizable(False)

        # CORRECT ID: password_section (matches XML)
        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/password-save.ui', 'password_section')

        self.entry_new = builder.get_object('new_password_entry')
        self.entry_confirm = builder.get_object('confirm_password_entry')

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)


# ENTRY DIALOGS #

class EntryEdit(Utility):
    def __init__(self, parent, title, e=None, cfg=None, clipboard=None):
        super().__init__(parent, title)
        self.set_default_size(500, 600)

        self.entry = e
        self.config = cfg
        self.clipboard = clipboard
        self.widgetdata = {}
        self.entry_field = {}
        self.fielddata = {}

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/entry-edit.ui', 'meta_section')

        # Reduce spacing in meta_section to minimize gap before Account Data
        if _section:
            _section.set_spacing(6)  # Ensure spacing is minimal

        set_section_title(builder, 'meta_title', title)
        set_section_title(builder, 'notes_title', _('Notes'))

        self.name_entry = builder.get_object('name_entry')
        self.desc_entry = builder.get_object('description_entry')

        self.dropdown = ui.EntryDropDown()
        self.dropdown.connect("changed", lambda w: self.__setup_fieldsect(self.dropdown.get_active_type()().fields))

        dropdown_container = builder.get_object('type_dropdown_container')
        if dropdown_container:
            dropdown_container.set_vexpand(False)
            dropdown_container.append(self.dropdown)

        notes_placeholder = builder.get_object('notes_placeholder')
        if notes_placeholder:
            parent_box = notes_placeholder.get_parent()
            self.notes_view = ui.EditableTextView(text=e.notes if e else "")
            sw = Gtk.ScrolledWindow()
            sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            sw.set_vexpand(True)
            sw.set_hexpand(True)
            sw.set_child(self.notes_view)
            parent_box.append(sw)
            parent_box.remove(notes_placeholder)

        self.sect_fields = self.add_section(_('Account Data'))
        self.sect_fields.set_hexpand(True)
        # Add a small top margin for visual separation between Type dropdown and Account Data section
        self.sect_fields.set_margin_top(24)

        self.sizegroup.add_widget(builder.get_object('name_label'))
        self.sizegroup.add_widget(builder.get_object('description_label'))
        self.sizegroup.add_widget(builder.get_object('type_label'))

        self.set_entry(e)

    def __setup_fieldsect(self, fields):
        """Generates a field section based on a field list"""
        for fieldtype, fieldentry in self.entry_field.items():
            if hasattr(fieldentry, 'get_text'):
                self.fielddata[fieldtype] = fieldentry.get_text()

        self.entry_field = {}
        self.sect_fields.clear()

        for field in fields:
            userdata = self.widgetdata.get(type(field))
            if userdata is None and field.datatype == entry.DATATYPE_PASSWORD:
                userdata = self.clipboard

            fieldentry = ui.generate_field_edit_widget(field, self.config, userdata)
            self.entry_field[type(field)] = fieldentry

            val = self.fielddata.get(type(field), field.value)
            if hasattr(fieldentry, 'set_text'):
                fieldentry.set_text(val or "")

            if hasattr(fieldentry, "set_tooltip_text"):
                fieldentry.set_tooltip_text(field.description)
            elif hasattr(fieldentry, "entry"):
                fieldentry.entry.set_tooltip_text(field.description)

            self.sect_fields.append_widget(field.name, fieldentry)

        self._ensure_button_box_at_end()

    def set_fieldwidget_data(self, fieldtype, userdata):
        """Sets user data for fieldwidget"""
        self.widgetdata[fieldtype] = userdata
        if fieldtype == entry.UsernameField and entry.UsernameField in self.entry_field:
            self.entry_field[entry.UsernameField].set_values(userdata)

    def get_entry(self):
        e = self.dropdown.get_active_type()()
        e.name = self.name_entry.get_text()
        e.description = self.desc_entry.get_text()
        e.notes = self.notes_view.get_text()

        for field in e.fields:
            if type(field) in self.entry_field:
                field.value = self.entry_field[type(field)].get_text()
        return e

    def set_entry(self, e):
        e = e is not None and e.copy() or entry.GenericEntry()
        self.name_entry.set_text(e.name)
        self.desc_entry.set_text(e.description)
        self.notes_view.set_text(e.notes)
        self.dropdown.set_active_type(type(e))

        for field in e.fields:
            self.fielddata[type(field)] = field.value or ""

        self.__setup_fieldsect(e.fields)


class EntryRemove(Warning):
    def __init__(self, parent, entries):
        if len(entries) > 1:
            title = _('Really remove the %i selected entries?') % len(entries)
            text = _('By removing these entries you will also remove any entries they may contain.')
        elif isinstance(entries[0], entry.FolderEntry):
            title = _('Really remove folder \'%s\'?') % entries[0].name
            text = _('By removing this folder you will also remove all accounts and folders it contains.')
        else:
            title = _('Really remove account \'%s\'?') % entries[0].name
            text = _('Please confirm that you wish to remove this account.')

        super().__init__(parent, title, text)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_REMOVE, Gtk.ResponseType.YES)
        self.set_default_response(Gtk.ResponseType.YES)


class FolderEdit(Utility):
    def __init__(self, parent, title, e=None):
        super().__init__(parent, title)
        self.entry = e
        self.set_default_size(350, 200)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        # CORRECT ID: folder_section (matches XML)
        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/folder-edit.ui', 'folder_section')

        set_section_title(builder, 'section_title', title)

        self.name_entry = builder.get_object('name_entry')
        self.desc_entry = builder.get_object('description_entry')

        self.sizegroup.add_widget(builder.get_object('name_label'))
        self.sizegroup.add_widget(builder.get_object('description_label'))

        if e:
            self.name_entry.set_text(e.name)
            self.desc_entry.set_text(e.description)

    def get_entry(self):
        e = self.entry if self.entry else entry.FolderEntry()
        e.name = self.name_entry.get_text()
        e.description = self.desc_entry.get_text()
        return e


class About(Gtk.AboutDialog):
    def __init__(self, parent):
        super().__init__(modal=True)
        if isinstance(parent, Gtk.Window):
            self.set_transient_for(parent)

        self.set_program_name(config.APPNAME)
        self.set_version(config.VERSION)
        self.set_copyright(config.COPYRIGHT)
        self.set_comments(('"%s"\n\n' + _('A password manager for the GNOME desktop')) % config.RELNAME)
        self.set_license(config.LICENSE)
        self.set_website(config.URL)
        self.set_authors(config.AUTHORS)
        self.set_artists(config.ARTISTS)
        self.set_logo_icon_name(config.APPID)


class ExceptionDialog(Message):
    def __init__(self, parent, traceback):
        title = gettext.gettext("An error has occurred")
        msg = gettext.gettext("An unhandled exception occurred.")

        super().__init__(parent, title, msg, "dialog-error")

        self.add_button(gettext.gettext("_Quit"), Gtk.ResponseType.REJECT)
        self.add_button(ui.STOCK_CONTINUE, Gtk.ResponseType.ACCEPT)

        sw = Gtk.ScrolledWindow()
        sw.set_min_content_height(300)
        sw.set_min_content_width(500)
        sw.set_child(ui.TextView(text=traceback))
        sw.set_vexpand(True)
        sw.set_hexpand(True)

        self.get_content_area().append(sw)
        self.set_default_size(600, 400)
        self._ensure_button_box_at_end()


class PasswordChecker(Utility):
    def __init__(self, parent, cfg=None, clipboard=None):
        super().__init__(parent, _('Password Checker'))

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.cfg = cfg
        self.set_modal(False)
        self.set_size_request(300, -1)

        # For unique dialogs, hide instead of destroy when closed
        def on_response(dlg, response):
            # Handle both CLOSE (button) and CANCEL (Escape/close-request)
            if response in (Gtk.ResponseType.CLOSE, Gtk.ResponseType.CANCEL):
                self.set_visible(False)
                return True  # Keep dialog alive (don't destroy)
            return False

        self.connect_response(on_response)

        # Explicitly connect close-request handler (GTK4 doesn't auto-connect _on_close_request)
        self.connect("close-request", self._on_close_request)

        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/password-checker.ui', 'password_checker_section')
        set_section_title(builder, 'section_title', _('Password Checker'))

        self.entry = replace_widget(builder, 'password_entry', ui.PasswordEntry(None, cfg, clipboard))
        self.entry.autocheck = False
        # PasswordEntry is a Gtk.Box wrapper, access the inner Gtk.PasswordEntry
        self.entry.entry.set_width_chars(40)
        self.entry.entry.connect("changed", self.__cb_changed)

        self.result_label = builder.get_object('result_label')
        self.result_image = builder.get_object('result_image')
        self.result_image.set_from_icon_name(ui.STOCK_UNKNOWN)

        self.sizegroup.add_widget(builder.get_object('password_label'))

    def _on_close_request(self, dialog):
        # Override to hide instead of destroy for unique dialogs
        # Centralized in show_unique_dialog, but we need this for close-request signal
        self.set_visible(False)
        return True  # Prevent default close behavior

    def __cb_changed(self, widget, data=None):
        password = self.entry.get_text()
        try:
            if not password:
                icon = ui.STOCK_UNKNOWN
                result = _('Enter a password to check')
            else:
                util.check_password(password)
                icon = ui.STOCK_PASSWORD_STRONG
                result = _('The password seems good')
        except ValueError as reason:
            icon = ui.STOCK_PASSWORD_WEAK
            result = _('The password %s') % str(reason)

        self.result_label.set_markup(util.escape_markup(result))
        self.result_image.set_from_icon_name(icon)


class PasswordGenerator(Utility):
    def __init__(self, parent, cfg, clipboard=None):
        super().__init__(parent, _('Password Generator'))

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.add_button(ui.STOCK_GENERATE, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        self.config = cfg
        self.set_modal(False)

        builder, _section = self.load_ui_section('/info/olasagasti/revelation/ui/password-generator.ui', 'password_generator_section')
        set_section_title(builder, 'section_title', _('Password Generator'))

        self.entry = replace_widget(builder, 'password_entry', ui.PasswordEntry(None, cfg, clipboard))
        self.entry.autocheck = False
        # PasswordEntry is a Gtk.Box wrapper, access the inner Gtk.PasswordEntry
        self.entry.entry.set_editable(False)

        self.spin_pwlen = builder.get_object('length_spin')
        self.check_punctuation = builder.get_object('punctuation_check')

        self.config.bind("passwordgen-length", self.spin_pwlen, "value", Gio.SettingsBindFlags.DEFAULT)
        self.config.bind("passwordgen-punctuation", self.check_punctuation, "active", Gio.SettingsBindFlags.DEFAULT)

        def internal_response(dlg, response):
            if response == Gtk.ResponseType.OK:
                length = self.spin_pwlen.get_value()
                use_punct = self.check_punctuation.get_active()
                password = util.generate_password(length, use_punct)
                self.entry.set_text(password)
                return True  # Keep dialog open
            elif response in (Gtk.ResponseType.CLOSE, Gtk.ResponseType.CANCEL):
                # For unique dialogs, hide instead of destroy when closed
                self.set_visible(False)
                return True  # Keep dialog alive (don't destroy)
            return False

        self.connect_response(internal_response)

        # Explicitly connect close-request handler (GTK4 doesn't auto-connect _on_close_request)
        self.connect("close-request", self._on_close_request)

    def _on_close_request(self, dialog):
        # Override to hide instead of destroy for unique dialogs
        self.set_visible(False)
        return True  # Prevent default close behavior


# ASYNC FUNCTIONS (GTK4 Compliance) #

def show_error_async(parent, title, message):
    alert = Gtk.AlertDialog(message=title, detail=message, modal=True)
    # FIX: Use parent explicitly to ensure z-order
    alert.choose(parent, None, lambda *args: None, None)


def show_info_async(parent, title, message):
    alert = Gtk.AlertDialog(message=title, detail=message, modal=True)
    alert.choose(parent, None, lambda *args: None, None)


def confirm_async(parent, title, message, callback):
    alert = Gtk.AlertDialog(message=title, detail=message, modal=True)
    alert.set_buttons([_("_Cancel"), _("_Yes")])
    alert.set_default_button(1)
    alert.set_cancel_button(0)

    def on_finish(source, result, data):
        try:
            btn = source.choose_finish(result)
            callback(btn == 1)
        except GLib.Error:
            callback(False)

    alert.choose(parent, None, on_finish, None)


def file_changes_async(dialog_class, parent, callback):
    d = dialog_class(parent)

    def on_response(dlg, response):
        try:
            if response == Gtk.ResponseType.OK:
                callback(True)
            elif response == Gtk.ResponseType.ACCEPT:
                callback(False)
            else:
                callback(None)
        except CancelError:
            pass
        return False
    d.connect_response(on_response)
    d.present()


def entry_remove_async(parent, entries, callback):
    d = EntryRemove(parent, entries)

    def on_response(dlg, res):
        try:
            callback(True) if res == Gtk.ResponseType.YES else callback(None)
        except CancelError:
            pass
        return False
    d.connect_response(on_response)
    d.present()


def file_save_insecure_async(parent, callback):
    d = FileSaveInsecure(parent)

    def on_response(dlg, res):
        try:
            callback(True) if res == Gtk.ResponseType.OK else callback(None)
        except CancelError:
            pass
        return False
    d.connect_response(on_response)
    d.present()


def exception_async(parent, traceback, callback):
    d = ExceptionDialog(parent, traceback)

    def on_response(dlg, res):
        callback(res == Gtk.ResponseType.ACCEPT)
        return False
    d.connect_response(on_response)
    d.present()


def file_selector_async(selector_class, parent, callback, *args):
    """
    DEPRECATED: This function is kept for backward compatibility.
    Use specific async functions like open_file_selector_async() or save_file_selector_async() instead.
    """
    # For OpenFileSelector, use the new async function
    if selector_class == OpenFileSelector:
        open_file_selector_async(parent, callback)
    elif selector_class == SaveFileSelector:
        save_file_selector_async(parent, callback, *args)
    else:
        callback(None)


def _select_file_type_async(parent, handlers, default_handler, callback, is_import=False):
    """Helper to select file type after file selection"""
    if not handlers or len(handlers) == 0:
        callback(None)
        return

    # If only one handler and it's not auto-detect, use it directly
    if len(handlers) == 1 and not is_import:
        callback(handlers[0])
        return

    # Create a simple dialog for file type selection
    dlg = Gtk.Dialog(title=_("Select file type"), transient_for=parent, modal=True)
    dlg.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
    dlg.add_button(_("_OK"), Gtk.ResponseType.OK)
    dlg.set_default_response(Gtk.ResponseType.OK)

    content = dlg.get_content_area()
    content.set_spacing(12)
    content.set_margin_top(12)
    content.set_margin_bottom(12)
    content.set_margin_start(12)
    content.set_margin_end(12)

    label = Gtk.Label(label=_("Select the file type:"))
    label.set_halign(Gtk.Align.START)
    content.append(label)

    # Use radio buttons for single selection
    selected_handler = [default_handler]
    radio_group = None

    if is_import:
        # Add auto-detect option
        radio_auto = Gtk.CheckButton(label=_("Automatically detect"))
        radio_auto.set_active(default_handler is None)
        radio_auto.connect("toggled", lambda w: selected_handler.__setitem__(0, None) if w.get_active() else None)
        content.append(radio_auto)
        radio_group = radio_auto

    for handler in handlers:
        # Create radio button in the same group
        if radio_group:
            radio = Gtk.CheckButton(label=handler.name, group=radio_group)
        else:
            radio = Gtk.CheckButton(label=handler.name)
            radio_group = radio
        radio.set_active(handler == default_handler)
        radio.connect("toggled", lambda w, h=handler: selected_handler.__setitem__(0, h) if w.get_active() else None)
        content.append(radio)

    def on_response(dialog, response):
        if response == Gtk.ResponseType.OK:
            callback(selected_handler[0])
        else:
            callback(None)
        dialog.destroy()

    dlg.connect("response", on_response)
    dlg.present()


def export_file_selector_async(parent, callback):
    """Opens a file save dialog for exporting, then prompts for file type"""
    dialog = Gtk.FileDialog(title=_("Export file"))
    dialog.set_modal(True)

    def on_file_selected(dlg, result):
        try:
            file = dlg.save_finish(result)
            if file:
                filename = file.get_path() or file.get_uri()
                # Get export handlers and prompt for type
                handlers = datahandler.get_export_handlers()
                default_handler = None
                for handler in handlers:
                    if handler.name == "Revelation":
                        default_handler = handler
                        break
                _select_file_type_async(
                    parent, handlers, default_handler, 
                    lambda handler: callback(filename, handler)
                )
            else:
                callback(None, None)
        except GLib.GError as e:
            # Check if user cancelled explicitly
            # Note: Gio.IOErrorEnum.CANCELLED works for 99% of platforms.
            # Some backends may use Gio.DBusError.CANCELLED or code 2, but GTK examples
            # typically check only Gio.IOErrorEnum.CANCELLED, which is sufficient for most cases.
            if e.code == Gio.IOErrorEnum.CANCELLED:
                callback(None, None)  # User cancelled
            else:
                # Real error - log it and still call callback
                logger.error("File dialog error: %s", e)
                callback(None, None)

    dialog.save(parent, None, on_file_selected)


def import_file_selector_async(parent, callback):
    """Opens a file open dialog for importing, then prompts for file type"""
    dialog = Gtk.FileDialog(title=_("Import file"))
    dialog.set_modal(True)

    def on_file_selected(dlg, result):
        try:
            file = dlg.open_finish(result)
            if file:
                filename = file.get_path() or file.get_uri()
                # Get import handlers and prompt for type (auto-detect is default)
                handlers = datahandler.get_import_handlers()
                _select_file_type_async(
                    parent, handlers, None, 
                    lambda handler: callback(filename, handler), is_import=True
                )
            else:
                callback(None, None)
        except GLib.GError as e:
            # Check if user cancelled explicitly
            # Note: Gio.IOErrorEnum.CANCELLED works for 99% of platforms.
            # Some backends may use Gio.DBusError.CANCELLED or code 2, but GTK examples
            # typically check only Gio.IOErrorEnum.CANCELLED, which is sufficient for most cases.
            if e.code == Gio.IOErrorEnum.CANCELLED:
                callback(None, None)  # User cancelled
            else:
                # Real error - log it and still call callback
                logger.error("File dialog error: %s", e)
                callback(None, None)

    dialog.open(parent, None, on_file_selected)


def open_file_selector_async(parent, callback):
    """Opens a file open dialog"""
    dialog = Gtk.FileDialog(title=_("Select file"))
    dialog.set_modal(True)

    # Add filters
    all_filter = Gtk.FileFilter()
    all_filter.set_name(_("All files"))
    all_filter.add_pattern("*")

    rvl_filter = Gtk.FileFilter()
    rvl_filter.set_name(_("Revelation files"))
    rvl_filter.add_pattern("*.rvl")

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(all_filter)
    filters.append(rvl_filter)
    dialog.set_filters(filters)
    dialog.set_default_filter(rvl_filter)

    def on_file_selected(dlg, result):
        try:
            file = dlg.open_finish(result)
            if file:
                filename = file.get_path() or file.get_uri()
                callback(filename)
            else:
                callback(None)
        except GLib.GError as e:
            # Check if user cancelled explicitly
            if e.code == Gio.IOErrorEnum.CANCELLED:
                callback(None)  # User cancelled
            else:
                # Real error - log it and still call callback
                logger.error("File dialog error: %s", e)
                callback(None)

    dialog.open(parent, None, on_file_selected)


def save_file_selector_async(parent, callback, title=_("Select file")):
    """Opens a file save dialog"""
    dialog = Gtk.FileDialog(title=title)
    dialog.set_modal(True)

    def on_file_selected(dlg, result):
        try:
            file = dlg.save_finish(result)
            if file:
                filename = file.get_path() or file.get_uri()
                callback(filename)
            else:
                callback(None)
        except GLib.GError as e:
            # Check if user cancelled explicitly
            if e.code == Gio.IOErrorEnum.CANCELLED:
                callback(None)  # User cancelled
            else:
                # Real error - log it and still call callback
                logger.error("File dialog error: %s", e)
                callback(None)

    dialog.save(parent, None, on_file_selected)


def password_open_async(parent, filename, callback):
    d = PasswordOpen(parent, filename)

    def on_response(dlg, response):
        print(f"DEBUG: password_open_async response: {response}")
        if response == Gtk.ResponseType.OK:
            pw = dlg.entry_password.get_text()
            print(f"DEBUG: Sending password (len={len(pw)}) to callback")
            callback(pw)
        else:
            print("DEBUG: Dialog cancelled")
            callback(None)
        return False
    d.connect_response(on_response)
    d.present()


def password_open_sync(parent, filename):
    """
    DEPRECATED: Use password_open_async() instead.
    This method is kept for backward compatibility with old sync load() method.
    It will be removed once all callers are migrated to async flow.
    """
    loop = GLib.MainLoop()
    result = [None]

    def cb(password):
        result[0] = password
        loop.quit()

    password_open_async(parent, filename, cb)
    loop.run()

    if result[0] is None:
        raise CancelError
    return result[0]


def password_change_async(parent, current_password, callback):
    d = PasswordChange(parent, current_password)

    def on_response(dlg, response):
        if response != Gtk.ResponseType.OK:
            callback(None)
            return False

        pw_current = dlg.entry_current.get_text() if dlg.entry_current else None
        pw_new = dlg.entry_new.get_text()
        pw_conf = dlg.entry_confirm.get_text()

        if current_password and pw_current != current_password:
            show_error_async(dlg, _('Incorrect password'), _('The current file password is incorrect.'))
            return True  # Keep Open
        if pw_new != pw_conf:
            show_error_async(dlg, _('Passwords do not match'), _('The passwords do not match.'))
            return True  # Keep Open

        callback(pw_new)
        return False
    d.connect_response(on_response)
    d.present()


def password_save_async(parent, filename, callback):
    d = PasswordSave(parent, filename)

    def on_response(dlg, response):
        if response != Gtk.ResponseType.OK:
            callback(None)
            return False
        pw = dlg.entry_new.get_text()
        conf = dlg.entry_confirm.get_text()
        if pw != conf:
            show_error_async(dlg, _('Error'), _('Passwords do not match.'))
            return True
        if len(pw) == 0:
            show_error_async(dlg, _('Error'), _('Password cannot be empty.'))
            return True
        callback(pw)
        return False
    d.connect_response(on_response)
    d.present()


def entry_edit_async(parent, title, e, cfg, clipboard, callback):
    d = EntryEdit(parent, title, e, cfg, clipboard)

    def on_response(dlg, response):
        if response == Gtk.ResponseType.OK:
            obj = dlg.get_entry()
            if not obj.name:
                show_error_async(dlg, _('Error'), _('Name is required'))
                return True
            callback(obj)
            return False
        else:
            callback(None)
            return False
    d.connect_response(on_response)
    d.present()


def folder_edit_async(parent, title, e, callback):
    d = FolderEdit(parent, title, e)

    def on_response(dlg, response):
        if response == Gtk.ResponseType.OK:
            obj = dlg.get_entry()
            if not obj.name:
                show_error_async(dlg, _('Error'), _('Name is required'))
                return True
            callback(obj)
        else:
            callback(None)
        return False
    d.connect_response(on_response)
    d.present()


def password_lock_async(parent, password, callback, dialog_instance=None):
    d = dialog_instance or PasswordLock(parent, password)

    def on_response(dlg, response):
        if response == Gtk.ResponseType.OK:
            if dlg.entry_password.get_text() == password:
                callback(password)
                return False
            else:
                show_error_async(dlg, _('Error'), _('Incorrect password'))
                return True
        else:
            callback(None)
            return False
    d.connect_response(on_response)
    d.present()


def show_unique_dialog(dialog_class, *args):
    # Get existing instance if still alive (WeakValueDictionary auto-removes destroyed dialogs)
    dialog = _visible_dialogs.get(dialog_class)

    if dialog is not None:
        # Dialog is still alive - present it (WeakValueDictionary ensures it's valid)
        dialog.present()
        return dialog

    # Create new unique dialog
    dialog = dialog_class(*args)

    # Store in WeakValueDictionary - automatically removed when dialog is destroyed
    # No need for manual cleanup or validity checks - WeakValueDictionary handles it
    _visible_dialogs[dialog_class] = dialog

    dialog.present()
    return dialog