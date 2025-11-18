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
from . import CancelError  # noqa: F401

import gettext
import urllib.parse
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gtk, Gio, Gdk, GLib  # noqa: E402

_ = gettext.gettext


EVENT_FILTER        = None
# Track visible dialogs to prevent duplicates (GTK4-compatible)
_visible_dialogs = {}


# EXCEPTIONS #
# CancelError is defined in __init__.py and imported above


# BASE DIALOGS #

class Dialog(Gtk.Dialog):
    "Base class for dialogs"

    def __init__(self, parent, title):
        Gtk.Dialog.__init__(self, title=title)

        # Store response callback for GTK4 compatibility
        self._response_callback = None

        content_area = self.get_content_area()
        ui.apply_css_padding(content_area, 12)
        content_area.set_spacing(12)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_transient_for(parent)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.__cb_keypress)
        self.add_controller(key_controller)

    def __cb_keypress(self, controller, keyval, keycode, state):
        "Callback for handling key presses"

        # close the dialog on escape
        if keyval == Gdk.KEY_Escape:
            self._handle_response(Gtk.ResponseType.CLOSE)
            return True
        return False

    def _ensure_button_box_at_end(self):
        "Ensures the button box is at the end of the content area"
        if hasattr(self, '_button_box') and self._button_box:
            content_area = self.get_content_area()
            if self._button_box.get_parent():
                self._button_box.unparent()
            content_area.append(self._button_box)

    def load_ui_section(self, resource_path, object_name, pack=True):
        "Load a UI section from a resource file and optionally pack it into content area"
        builder = Gtk.Builder()
        builder.add_from_resource(resource_path)
        section = builder.get_object(object_name)

        if pack:
            content_area = self.get_content_area()
            section.set_hexpand(True)
            section.set_vexpand(True)
            content_area.append(section)
            # Ensure button box stays at the end
            self._ensure_button_box_at_end()

        return builder, section

    def add_button(self, label, response_id):
        "Adds a button to the dialog (GTK4 compatible)"
        if not hasattr(self, '_buttons'):
            self._buttons = {}
        if not hasattr(self, '_button_box'):
            # Create button box with linked styling
            self._button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            self._button_box.add_css_class("linked")
            self._button_box.set_halign(Gtk.Align.END)
            self._button_box.set_margin_top(12)

        # Ensure button box is at the end of content area
        self._ensure_button_box_at_end()

        # Create button
        button = Gtk.Button.new_with_mnemonic(label)
        # GTK4: Dialog doesn't have response signal, call response method directly
        button.connect("clicked", lambda w: self._handle_response(response_id))
        self._button_box.append(button)
        self._buttons[response_id] = button
        return button

    def set_default_response(self, response_id):
        "Sets the default response (GTK4 compatible)"
        if hasattr(self, '_buttons') and response_id in self._buttons:
            self._buttons[response_id].grab_focus()
            # Mark as default button with suggested-action style
            self._buttons[response_id].add_css_class("suggested-action")

    def get_widget_for_response(self, response_id):
        "Gets the widget for a response ID (GTK4 compatible)"
        if hasattr(self, '_buttons') and response_id in self._buttons:
            return self._buttons[response_id]
        return None

    def _handle_response(self, response_id):
        "Handles a response from a button click (GTK4 compatible)"
        # Call the response callback if set
        if hasattr(self, '_response_callback') and self._response_callback:
            try:
                # Callback can return False to prevent destruction (for PasswordGenerator OK)
                result = self._response_callback(self, response_id)
                if result is False:
                    return  # Don't destroy if callback returns False
            except BaseException:
                # Callbacks may raise CancelError or other exceptions - catch them
                # The callback itself should handle the exception, but just in case
                # Use BaseException to catch all exceptions including SystemExit, KeyboardInterrupt
                pass
        # Always destroy the dialog after response (GTK4 pattern)
        self.destroy()

    def connect_response(self, callback):
        "Connect a callback for dialog response (GTK4 compatible)"
        self._response_callback = callback

    def connect(self, signal, callback):
        "Override connect to handle 'response' signal for GTK4 compatibility"
        if signal == "response":
            # Store callback for GTK4 compatibility (no response signal exists)
            self._response_callback = callback
            return 0  # Return a handler ID (not used in GTK4)
        else:
            # For other signals, use parent class connect
            return super().connect(signal, callback)

    def disconnect_by_func(self, callback):
        "Override disconnect_by_func to handle 'response' signal for GTK4 compatibility"
        if self._response_callback == callback:
            self._response_callback = None
        else:
            # For other callbacks, use parent class disconnect
            return super().disconnect_by_func(callback)

    def run(self):
        """
        DEPRECATED: This method uses a nested GLib.MainLoop() which is not recommended in GTK4.

        This method is kept only for password_open_sync() which requires a synchronous
        callback for datafile.load(). All other dialogs should use async helper functions:
        - show_error_async(), show_info_async()
        - confirm_async(), file_changes_async()
        - entry_edit_async(), folder_edit_async()
        - password_change_async(), password_save_async()
        - file_selector_async(), export_file_selector_async(), etc.
        - show_unique_dialog() for unique dialogs
        """
        loop = GLib.MainLoop()
        response = [None]

        def on_response(dialog, response_id):
            response[0] = response_id
            if loop.is_running():
                loop.quit()

        self.connect_response(on_response)
        self.present()
        loop.run()

        # Dialog is destroyed by _handle_response, no need to clean up
        return response[0] if response[0] is not None else Gtk.ResponseType.CANCEL


def load_ui_builder(resource_path):
    "Helper function to load a UI builder from a resource file (for non-Dialog classes)"
    builder = Gtk.Builder()
    builder.add_from_resource(resource_path)
    return builder


def replace_widget(builder, object_id, new_widget):
    "Replace a widget from UI file with a custom widget"
    ui_widget = builder.get_object(object_id)
    widget_parent = ui_widget.get_parent()
    ui_widget.unparent()
    new_widget.set_hexpand(True)
    new_widget.set_vexpand(True)
    widget_parent.append(new_widget)
    return new_widget


def set_section_title(builder, object_id, text):
    "Set a section title with bold markup"
    title = builder.get_object(object_id)
    title.set_markup(f"<span weight='bold'>{util.escape_markup(text)}</span>")


def get_entry(builder, object_id):
    "Get an entry widget from builder and set activates_default"
    entry = builder.get_object(object_id)
    entry.set_activates_default(True)
    return entry


class Utility(Dialog):
    "A utility dialog"

    def __init__(self, parent, title):
        Dialog.__init__(self, parent, title)

        self.get_content_area().set_spacing(18)

        self.sizegroup = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

    def add_section(self, title, description = None):
        "Adds an input section to the dialog"

        section = ui.InputSection(title, description, self.sizegroup)
        section.set_hexpand(True)
        section.set_vexpand(True)
        self.get_content_area().append(section)
        # Ensure button box stays at the end
        self._ensure_button_box_at_end()

        return section


class Message(Dialog):
    "A message dialog"

    def __init__(self, parent, title, text, stockimage):
        Dialog.__init__(self, parent, "")

        # Load UI from file
        builder, message_hbox = self.load_ui_section('/info/olasagasti/revelation/ui/message.ui', 'message_hbox')
        content_area = self.get_content_area()
        content_area.set_spacing(24)

        # Set up image (optional) - image is defined in XML
        self.message_image = builder.get_object('message_image')
        if stockimage is not None:
            self.message_image.set_from_icon_name(stockimage)
        else:
            # Hide the image if no icon provided
            self.message_image.set_visible(False)

        # Get contents VBox from UI file
        self.contents = builder.get_object('contents')

        # Get message label and set markup
        label = builder.get_object('message_label')
        label.set_markup("<span size=\"larger\" weight=\"bold\">%s</span>\n\n%s" % (util.escape_markup(title), text))

    def run(self):
        "Displays the dialog"

        response = Dialog.run(self)
        self.destroy()

        return response


class Error(Message):
    "Displays an error message"

    def __init__(self, parent, title, text):
        Message.__init__(self, parent, title, text, "dialog-error")
        self.add_button(_("_OK"), Gtk.ResponseType.OK)


class Info(Message):
    "Displays an info message"

    def __init__(self, parent, title, text):
        Message.__init__(self, parent, title, text, "dialog-information")
        self.add_button(_("_OK"), Gtk.ResponseType.OK)


class Question(Message):
    "Displays a question"

    def __init__(self, parent, title, text):
        Message.__init__(self, parent, title, text, "dialog-question")
        self.add_button(_("_OK"), Gtk.ResponseType.OK)


class Warning(Message):
    "Displays a warning message"

    def __init__(self, parent, title, text):
        Message.__init__(self, parent, title, text, "dialog-warning")


# QUESTION DIALOGS #

class FileChanged(Warning):
    "Notifies about changed file"

    def __init__(self, parent, filename):
        # Ensure filename is a display name, not a raw URI or portal path
        display_name = io.file_get_display_name(filename) if filename else _("Untitled file")
        Warning.__init__(
            self, parent, _('File has changed'), _('The current file \'%s\' has changed. Do you want to reload it?') % display_name
        )

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_RELOAD, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

    def run(self):
        "Displays the dialog"

        if Warning.run(self) == Gtk.ResponseType.OK:
            return True

        else:
            raise CancelError


class FileChanges(Warning):
    "Asks to save changes before proceeding"

    def __init__(self, parent, title, text):
        Warning.__init__(self, parent, title, text)

        self.add_button(_("_Discard"), Gtk.ResponseType.ACCEPT)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Save"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

    def run(self):
        "Displays the dialog"

        response = Warning.run(self)

        if response == Gtk.ResponseType.OK:
            return True

        elif response == Gtk.ResponseType.ACCEPT:
            return False

        elif response in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.CLOSE):
            raise CancelError


class FileChangesNew(FileChanges):
    "Asks the user to save changes when creating a new file"

    def __init__(self, parent):
        FileChanges.__init__(
            self, parent, _('Save changes to current file?'),
            _('You have made changes which have not been saved. If you create a new file without saving then these changes will be lost.')
        )


class FileChangesOpen(FileChanges):
    "Asks the user to save changes when opening a different file"

    def __init__(self, parent):
        FileChanges.__init__(
            self, parent, _('Save changes before opening?'),
            _('You have made changes which have not been saved. If you open a different file without saving then these changes will be lost.')
        )


class FileChangesQuit(FileChanges):
    "Asks the user to save changes when quitting"

    def __init__(self, parent):
        FileChanges.__init__(
            self, parent, _('Save changes before quitting?'),
            _('You have made changes which have not been saved. If you quit without saving, then these changes will be lost.')
        )


class FileChangesClose(FileChanges):
    "Asks the user to save changes when closing"

    def __init__(self, parent):
        FileChanges.__init__(
            self, parent, _('Save changes before closing?'),
            _('You have made changes which have not been saved. If you close without saving, then these changes will be lost.')
        )


class FileReplace(Warning):
    "Asks for confirmation when replacing a file"

    def __init__(self, parent, file):
        # Ensure filename is a display name, not a raw URI or portal path
        display_name = io.file_get_display_name(file) if file else _("Untitled file")
        Warning.__init__(
            self, parent, _('Replace existing file?'),
            _('The file \'%s\' already exists - do you wish to replace this file?') % display_name
        )

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_REPLACE, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.CANCEL)

    def run(self):
        "Displays the dialog"

        if Warning.run(self) == Gtk.ResponseType.OK:
            return True

        else:
            raise CancelError


class FileSaveInsecure(Warning):
    "Asks for confirmation when exporting to insecure file"

    def __init__(self, parent):
        Warning.__init__(
            self, parent, _('Save to insecure file?'),
            _('You have chosen to save your passwords to an insecure (unencrypted) file format - if anyone has access to this file, they will be able to see your passwords.'),
        )

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Save"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.CANCEL)

    def run(self):
        "Runs the dialog"

        if Warning.run(self) == Gtk.ResponseType.OK:
            return True

        else:
            raise CancelError


# FILE SELECTION DIALOGS #

class FileSelector(Gtk.FileChooserNative):
    "A normal file selector"

    def __init__(self, parent, title=None,
                 action=Gtk.FileChooserAction.OPEN):

        Gtk.FileChooserNative.__init__(self, title=title, action=action)
        self.set_transient_for(parent)
        self.inputsection = None

    def add_widget(self, title, widget):
        "Adds a widget to the file selection"

        if self.inputsection is None:
            self.inputsection = ui.InputSection()
            self.set_extra_widget(self.inputsection)

        self.inputsection.append_widget(title, widget)

    def get_filename(self):
        "Returns the file URI (for portal compatibility)"

        file = self.get_file()
        if file is None:
            return None
        return file.get_uri()

    def get_file_path(self):
        "Returns the file path (for backward compatibility)"

        file = self.get_file()
        if file is None:
            return None
        uri = file.get_uri()
        if uri.startswith('file://'):
            return io.file_normpath(urllib.parse.unquote(uri))
        # For portal URIs, we can't convert to path
        return None

    def run(self):
        "Displays and runs the file selector, returns the filename"

        loop = GLib.MainLoop()
        response = [None]

        def on_response(dialog, response_id):
            response[0] = response_id
            loop.quit()

        self.connect_response(on_response)
        self.present()
        loop.run()

        self._response_callback = None
        filename = self.get_filename()
        self.destroy()

        if response[0] == Gtk.ResponseType.ACCEPT:
            return filename
        else:
            raise CancelError


class ExportFileSelector(FileSelector):
    "A file selector for exporting files"

    def __init__(self, parent):
        FileSelector.__init__(
            self, parent, _('Select File to Export to'),
            Gtk.FileChooserAction.SAVE
        )

        # set up filetype dropdown
        self.dropdown = ui.DropDown()
        self.add_widget(_('Filetype'), self.dropdown)

        for handler in datahandler.get_export_handlers():
            self.dropdown.append_item(handler.name, None, handler)

        for index in range(self.dropdown.get_num_items()):
            if self.dropdown.get_item(index)[2] == datahandler.RevelationXML:
                self.dropdown.set_active(index)

    def run(self):
        "Displays the dialog"

        loop = GLib.MainLoop()
        response = [None]

        def on_response(dialog, response_id):
            response[0] = response_id
            loop.quit()

        self.connect_response(on_response)
        self.present()
        loop.run()

        self._response_callback = None

        if response[0] == Gtk.ResponseType.ACCEPT:
            filename = self.get_filename()
            handler = self.dropdown.get_active_item()[2]
            self.destroy()

            return filename, handler
        else:
            self.destroy()
            raise CancelError


class ImportFileSelector(FileSelector):
    "A file selector for importing files"

    def __init__(self, parent):
        FileSelector.__init__(
            self, parent, _('Select File to Import'),
            Gtk.FileChooserAction.OPEN
        )

        # set up filetype dropdown
        self.dropdown = ui.DropDown()
        self.add_widget(_('Filetype'), self.dropdown)

        self.dropdown.append_item(_('Automatically detect'))

        for handler in datahandler.get_import_handlers():
            self.dropdown.append_item(handler.name, None, handler)

    def run(self):
        "Displays the dialog"

        loop = GLib.MainLoop()
        response = [None]

        def on_response(dialog, response_id):
            response[0] = response_id
            loop.quit()

        self.connect_response(on_response)
        self.present()
        loop.run()

        self._response_callback = None

        if response[0] == Gtk.ResponseType.ACCEPT:
            filename = self.get_filename()
            handler = self.dropdown.get_active_item()[2]
            self.destroy()

            return filename, handler
        else:
            self.destroy()
            raise CancelError


class OpenFileSelector(FileSelector):
    "A file selector for opening files"

    def __init__(self, parent):
        FileSelector.__init__(
            self, parent, _('Select File to Open'),
            Gtk.FileChooserAction.OPEN
        )

        filter = Gtk.FileFilter()
        filter.set_name(_('Revelation files'))
        filter.add_mime_type("application/x-revelation")
        self.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern("*")
        self.add_filter(filter)


class SaveFileSelector(FileSelector):
    "A file selector for saving files"

    def __init__(self, parent):
        FileSelector.__init__(
            self, parent, _('Select File to Save to'),
            Gtk.FileChooserAction.SAVE
        )

        filter = Gtk.FileFilter()
        filter.set_name(_('Revelation files'))
        filter.add_mime_type("application/x-revelation")
        self.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern("*")
        self.add_filter(filter)


# PASSWORD DIALOGS #

class Password(Message):
    "A base dialog for asking for passwords"

    def __init__(self, parent, title, text, stock = _("_OK")):
        Message.__init__(self, parent, title, text, "dialog-password")

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(stock, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        self.entries = []

        self.sect_passwords = ui.InputSection()
        self.sect_passwords.set_hexpand(True)
        self.sect_passwords.set_vexpand(True)
        self.contents.append(self.sect_passwords)

    def add_entry(self, name, entry = None):
        "Adds a password entry to the dialog"

        if entry is None:
            entry = ui.Entry()
            entry.set_visibility(False)

        self.sect_passwords.append_widget(name, entry)
        self.entries.append(entry)

        return entry

    def run(self):
        "Displays the dialog"

        if len(self.entries) > 0:
            self.entries[0].grab_focus()

        return Dialog.run(self)


class PasswordChange(Password):
    "A dialog for changing the password"

    def __init__(self, parent, password = None):
        Password.__init__(
            self, parent, _('Enter new password'),
            _('Enter a new password for the current data file. The file must be saved before the new password is applied.'),
            ui.STOCK_PASSWORD_CHANGE
        )

        self.password = password

        # Load password section from UI file
        builder, password_section = self.load_ui_section('/info/olasagasti/revelation/ui/password-change.ui', 'password_section', pack=False)

        # Replace the InputSection with UI file content
        # GTK4: remove() removed, use unparent()
        self.sect_passwords.unparent()
        # Add the UI file section
        password_section.set_hexpand(True)
        password_section.set_vexpand(True)
        self.contents.append(password_section)

        # Get the current password entry from UI file (optional)
        current_entry_row = builder.get_object('current_password_entry').get_parent()
        if password is not None:
            self.entry_current = get_entry(builder, 'current_password_entry')
        else:
            # Hide the current password row if password is None
            current_entry_row.set_visible(False)
            self.entry_current = None

        # Get the new password entry from UI file and replace with PasswordEntry
        self.entry_new = replace_widget(builder, 'new_password_entry', ui.PasswordEntry())

        # Get the confirm password entry from UI file
        self.entry_confirm = get_entry(builder, 'confirm_password_entry')
        self.entry_confirm.autocheck = False

        # Build entries list
        self.entries = []
        if self.entry_current is not None:
            self.entries.append(self.entry_current)
        self.entries.extend([self.entry_new, self.entry_confirm])

    def run(self):
        "Displays the dialog"

        while True:
            if Password.run(self) != Gtk.ResponseType.OK:
                self.destroy()
                raise CancelError

            elif self.password is not None and self.entry_current.get_text() != self.password:
                Error(self, _('Incorrect password'), _('The password you entered as the current file password is incorrect.')).run()

            elif self.entry_new.get_text() != self.entry_confirm.get_text():
                Error(self, _('Passwords don\'t match'), _('The password and password confirmation you entered does not match.')).run()

            else:
                password = self.entry_new.get_text()

                try:
                    util.check_password(password)

                except ValueError as res:
                    WarnInsecure = Warning(
                        self, _('Use insecure password?'),
                        _('The password you entered is not secure; %s. Are you sure you want to use it?') % str(res).lower()
                    )

                    WarnInsecure.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
                    WarnInsecure.add_button(_("_OK"), Gtk.ResponseType.OK)
                    WarnInsecure.set_default_response(Gtk.ResponseType.CANCEL)

                    response = WarnInsecure.run()
                    if response != Gtk.ResponseType.OK:
                        continue

                self.destroy()
                return password


class PasswordLock(Password):
    "Asks for a password when the file is locked"

    def __init__(self, parent, password):
        Password.__init__(
            self, parent, _('Enter password to unlock file'),
            _('The current file has been locked, please enter the file password to unlock it.'),
            ui.STOCK_UNLOCK
        )

        cancel_button = self.get_widget_for_response(Gtk.ResponseType.CANCEL)
        if cancel_button:
            cancel_button.set_label(_("_Quit"))
        self.set_default_response(Gtk.ResponseType.OK)

        self.password = password

        # Load password section from UI file
        builder, password_section = self.load_ui_section('/info/olasagasti/revelation/ui/password-lock.ui', 'password_section', pack=False)

        # Replace the InputSection with UI file content
        # GTK4: remove() removed, use unparent()
        self.sect_passwords.unparent()
        # Add the UI file section
        password_section.set_hexpand(True)
        password_section.set_vexpand(True)
        self.contents.append(password_section)

        # Get the password entry from UI file
        self.entry_password = get_entry(builder, 'password_entry')
        self.entries = [self.entry_password]

    def run(self):
        "Displays the dialog"

        while True:
            try:
                response = Password.run(self)

                if response == Gtk.ResponseType.CANCEL:
                    raise CancelError

                elif response != Gtk.ResponseType.OK:
                    continue

                elif self.entry_password.get_text() == self.password:
                    break

                else:
                    Error(self, _('Incorrect password'), _('The password you entered was not correct, please try again.')).run()

            except CancelError:
                cancel_button = self.get_widget_for_response(Gtk.ResponseType.CANCEL)
                if cancel_button and cancel_button.get_property("sensitive"):
                    self.destroy()
                    raise

                else:
                    continue

        self.destroy()


class PasswordOpen(Password):
    "Password dialog for opening files"

    def __init__(self, parent, filename):
        # Ensure filename is a display name, not a raw URI or portal path
        display_name = io.file_get_display_name(filename) if filename else _("Untitled file")
        Password.__init__(
            self, parent, _('Enter file password'),
            _('The file "%s" is encrypted. Please enter the file password to open it.') % display_name,
            _("_Open")
        )

        self.set_default_response(Gtk.ResponseType.OK)

        # Load password section from UI file
        builder, password_section = self.load_ui_section('/info/olasagasti/revelation/ui/password-open.ui', 'password_section', pack=False)

        # Replace the InputSection with UI file content
        self.sect_passwords.unparent()
        # Add the UI file section
        password_section.set_hexpand(True)
        password_section.set_vexpand(True)
        self.contents.append(password_section)

        # Get the password entry from UI file
        self.entry_password = get_entry(builder, 'password_entry')
        self.entries = [self.entry_password]

    def run(self):
        "Displays the dialog"

        response = Password.run(self)
        password = self.entry_password.get_text()
        self.destroy()

        if response == Gtk.ResponseType.OK:
            return password

        else:
            raise CancelError


class PasswordSave(Password):
    "Password dialog for saving data"

    def __init__(self, parent, filename):
        # Ensure filename is a display name, not a raw URI or portal path
        display_name = io.file_get_display_name(filename) if filename else _("Untitled file")
        Password.__init__(
            self, parent, _('Enter password for file'),
            _('Please enter a password for the file \'%s\'. You will need this password to open the file at a later time.') % display_name,
            _("_Save")
        )

        # Load password section from UI file
        builder, password_section = self.load_ui_section('/info/olasagasti/revelation/ui/password-save.ui', 'password_section', pack=False)

        # Replace the InputSection with UI file content
        # GTK4: remove() removed, use unparent()
        self.sect_passwords.unparent()
        # Add the UI file section
        password_section.set_hexpand(True)
        password_section.set_vexpand(True)
        self.contents.append(password_section)

        # Get the new password entry from UI file and replace with PasswordEntry
        self.entry_new = replace_widget(builder, 'new_password_entry', ui.PasswordEntry())

        # Get the confirm password entry from UI file
        self.entry_confirm = get_entry(builder, 'confirm_password_entry')
        self.entry_confirm.autocheck = False

        self.entries = [self.entry_new, self.entry_confirm]

    def run(self):
        "Displays the dialog"

        while True:
            if Password.run(self) != Gtk.ResponseType.OK:
                self.destroy()
                raise CancelError

            elif self.entry_new.get_text() != self.entry_confirm.get_text():
                Error(self, _('Passwords don\'t match'), _('The passwords you entered does not match.')).run()

            elif len(self.entry_new.get_text()) == 0:
                Error(self, _('No password entered'), _('You must enter a password for the new data file.')).run()

            else:
                password = self.entry_new.get_text()

                try:
                    util.check_password(password)

                except ValueError as res:
                    res = str(res).lower()

                    WarnInsecure = Warning(
                        self, _('Use insecure password?'),
                        _('The password you entered is not secure; %s. Are you sure you want to use it?') % res
                    )

                    WarnInsecure.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
                    WarnInsecure.add_button(_("_OK"), Gtk.ResponseType.OK)
                    WarnInsecure.set_default_response(Gtk.ResponseType.CANCEL)

                    response = WarnInsecure.run()
                    if response != Gtk.ResponseType.OK:
                        continue

                self.destroy()
                return password


# ENTRY DIALOGS #

class EntryEdit(Utility):
    "A dialog for editing entries"

    def __init__(self, parent, title, e = None, cfg = None, clipboard = None):
        Utility.__init__(self, parent, title)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        if not e:
            self.add_button(ui.STOCK_NEW_ENTRY, Gtk.ResponseType.OK)
        else:
            self.add_button(ui.STOCK_UPDATE, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        self.config      = cfg
        self.clipboard   = clipboard
        self.entry_field = {}
        self.fielddata   = {}
        self.widgetdata  = {}

        # Load UI from file
        builder, unused_section = self.load_ui_section('/info/olasagasti/revelation/ui/entry-edit.ui', 'meta_section', pack=False)

        # Get sections from UI file
        meta_section = builder.get_object('meta_section')
        notes_section = builder.get_object('notes_section')

        # Set section titles with markup
        set_section_title(builder, 'meta_title', title)
        set_section_title(builder, 'notes_title', _('Notes'))

        # Add sections to dialog
        content_area = self.get_content_area()
        meta_section.set_hexpand(True)
        meta_section.set_vexpand(True)
        content_area.append(meta_section)
        self.sect_fields = self.add_section(_('Account Data'))
        notes_section.set_hexpand(True)
        notes_section.set_vexpand(True)
        content_area.append(notes_section)
        # Ensure button box stays at the end
        self._ensure_button_box_at_end()

        # Get entry widgets from UI file
        self.entry_name = get_entry(builder, 'name_entry')
        self.entry_desc = get_entry(builder, 'description_entry')

        # Add EntryDropDown to Box container (defined in XML)
        dropdown_container = builder.get_object('type_dropdown_container')
        self.dropdown = ui.EntryDropDown()
        self.dropdown.connect("changed", lambda w: self.__setup_fieldsect(self.dropdown.get_active_type()().fields))
        dropdown_container.append(self.dropdown)

        # Replace notes placeholder with EditableTextView
        notes_placeholder = builder.get_object('notes_placeholder')
        notes_placeholder_parent = notes_placeholder.get_parent()
        # GTK4: remove() removed, use unparent()
        notes_placeholder.unparent()
        self.entry_notes = ui.EditableTextView()
        self.entry_notes.set_tooltip_text(_('Notes for the entry'))
        self.entry_notes.set_hexpand(True)
        self.entry_notes.set_vexpand(True)
        notes_placeholder_parent.append(self.entry_notes)

        # Add labels to sizegroup for alignment
        name_label = builder.get_object('name_label')
        description_label = builder.get_object('description_label')
        type_label = builder.get_object('type_label')
        self.sizegroup.add_widget(name_label)
        self.sizegroup.add_widget(description_label)
        self.sizegroup.add_widget(type_label)

        # populate the dialog with data
        self.set_entry(e)

    def __setup_fieldsect(self, fields):
        "Generates a field section based on a field list"

        # store current field values
        for fieldtype, fieldentry in self.entry_field.items():
            self.fielddata[fieldtype] = fieldentry.get_text()

        self.entry_field = {}
        self.sect_fields.clear()

        # generate field entries
        for field in fields:

            if type(field) in self.widgetdata:
                userdata = self.widgetdata[type(field)]

            elif field.datatype == entry.DATATYPE_PASSWORD:
                userdata = self.clipboard

            else:
                userdata = None

            fieldentry = ui.generate_field_edit_widget(field, self.config, userdata)
            self.entry_field[type(field)] = fieldentry

            if type(field) in self.fielddata:
                fieldentry.set_text(self.fielddata[type(field)])

            if hasattr(fieldentry, "set_tooltip_text"):
                fieldentry.set_tooltip_text(field.description)

            elif hasattr(fieldentry, "entry"):
                fieldentry.entry.set_tooltip_text(field.description)

            self.sect_fields.append_widget(field.name, fieldentry)


    def get_entry(self):
        "Generates an entry from the dialog contents"

        e = self.dropdown.get_active_type()()

        e.name = self.entry_name.get_text()
        e.description = self.entry_desc.get_text()
        e.notes = self.entry_notes.get_text()

        for field in e.fields:
            field.value = self.entry_field[type(field)].get_text()

        return e

    def run(self):
        "Displays the dialog"

        while True:

            if Utility.run(self) == Gtk.ResponseType.OK:
                e = self.get_entry()

                if e.name == "":
                    Error(self, _('Name not entered'), _('You must enter a name for the account')).run()
                    continue

                self.destroy()
                return e

            else:
                self.destroy()
                raise CancelError

    def set_entry(self, e):
        "Sets an entry for the dialog"

        e = e is not None and e.copy() or entry.GenericEntry()

        self.entry_name.set_text(e.name)
        self.entry_desc.set_text(e.description)
        self.entry_notes.set_text(e.notes)
        self.dropdown.set_active_type(type(e))

        for field in e.fields:
            if type(field) in self.entry_field:
                self.entry_field[type(field)].set_text(field.value or "")

    def set_fieldwidget_data(self, fieldtype, userdata):
        "Sets user data for fieldwidget"

        self.widgetdata[fieldtype] = userdata

        if fieldtype == entry.UsernameField and entry.UsernameField in self.entry_field:
            self.entry_field[entry.UsernameField].set_values(userdata)


class EntryRemove(Warning):
    "Asks for confirmation when removing entries"

    def __init__(self, parent, entries):

        if len(entries) > 1:
            title   = _('Really remove the %i selected entries?') % len(entries)
            text    = _('By removing these entries you will also remove any entries they may contain.')

        elif type(entries[0]) == entry.FolderEntry:
            title   = _('Really remove folder \'%s\'?') % entries[0].name
            text    = _('By removing this folder you will also remove all accounts and folders it contains.')

        else:
            title   = _('Really remove account \'%s\'?') % entries[0].name
            text    = _('Please confirm that you wish to remove this account.')

        Warning.__init__(self, parent, title, text)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_Remove"), Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.CANCEL)

    def run(self):
        "Displays the dialog"

        if Warning.run(self) == Gtk.ResponseType.OK:
            return True

        else:
            raise CancelError


class FolderEdit(Utility):
    "Dialog for editing a folder"

    def __init__(self, parent, title, e = None):
        Utility.__init__(self, parent, title)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        if not e:
            self.add_button(ui.STOCK_NEW_FOLDER, Gtk.ResponseType.OK)
        else:
            self.add_button(ui.STOCK_UPDATE, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        # Load UI from file
        builder, section = self.load_ui_section('/info/olasagasti/revelation/ui/folder-edit.ui', 'folder_section')

        # Set section title with markup
        set_section_title(builder, 'section_title', title)

        # Get entry widgets from UI file
        self.entry_name = get_entry(builder, 'name_entry')
        self.entry_desc = get_entry(builder, 'description_entry')

        # Add labels to sizegroup for alignment
        name_label = builder.get_object('name_label')
        description_label = builder.get_object('description_label')
        self.sizegroup.add_widget(name_label)
        self.sizegroup.add_widget(description_label)

        # populate the dialog with data
        self.set_entry(e)

    def get_entry(self):
        "Generates an entry from the dialog contents"

        e = entry.FolderEntry()
        e.name = self.entry_name.get_text()
        e.description = self.entry_desc.get_text()

        return e

    def run(self):
        "Displays the dialog"

        while True:

            if Utility.run(self) == Gtk.ResponseType.OK:
                e = self.get_entry()

                if e.name == "":
                    Error(self, _('Name not entered'), _('You must enter a name for the folder')).run()
                    continue

                self.destroy()
                return e

            else:
                self.destroy()
                raise CancelError

    def set_entry(self, e):
        "Sets an entry for the dialog"

        if e is None:
            return

        self.entry_name.set_text(e.name)
        self.entry_desc.set_text(e.description)


# MISCELLANEOUS DIALOGS #

class About(Gtk.AboutDialog):
    "About dialog"

    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)

        # Store response callback for GTK4 compatibility
        self._response_callback = None

        if isinstance(parent, Gtk.Window):
            self.set_transient_for(parent)

        # Load static properties from UI file
        builder = load_ui_builder('/info/olasagasti/revelation/ui/about.ui')
        ui_dialog = builder.get_object('about_dialog')

        # Copy static properties from UI file
        self.set_property("program-name", ui_dialog.get_property("program-name"))
        self.set_property("website-label", ui_dialog.get_property("website-label"))
        self.set_property("license-type", ui_dialog.get_property("license-type"))

        # Set properties from config (source of truth)
        self.set_name(config.APPNAME)
        self.set_version(config.VERSION)
        self.set_copyright(config.COPYRIGHT)
        self.set_comments(('"%s"\n\n' + _('A password manager for the GNOME desktop')) % config.RELNAME)
        self.set_license(config.LICENSE)
        self.set_website(config.URL)
        self.set_authors(config.AUTHORS)
        self.set_artists(config.ARTISTS)

    def _handle_response(self, response_id):
        "Handles a response from a button click (GTK4 compatible)"
        # Call the response callback if set
        if hasattr(self, '_response_callback') and self._response_callback:
            self._response_callback(self, response_id)
        else:
            # Fallback: if no callback is set, just destroy the dialog
            # This shouldn't happen in normal operation, but it's a safety net
            self.destroy()

    def connect(self, signal, callback):
        "Override connect to handle 'response' signal for GTK4 compatibility"
        if signal == "response":
            # Store callback for GTK4 compatibility (no response signal exists)
            self._response_callback = callback
            return 0  # Return a handler ID (not used in GTK4)
        else:
            # For other signals, use parent class connect
            return super().connect(signal, callback)

    def disconnect_by_func(self, callback):
        "Override disconnect_by_func to handle 'response' signal for GTK4 compatibility"
        if self._response_callback == callback:
            self._response_callback = None
        else:
            # For other callbacks, use parent class disconnect
            return super().disconnect_by_func(callback)

    def run(self):
        "Displays the dialog"

        # GTK4: AboutDialog doesn't have response signal, use close-request instead
        loop = GLib.MainLoop()
        response = [Gtk.ResponseType.CLOSE]  # Default to CLOSE for AboutDialog

        def on_close_request(dialog):
            response[0] = Gtk.ResponseType.CLOSE
            if loop.is_running():
                loop.quit()
            # Dialog will be destroyed by close-request handler
            return False  # Allow close

        self.connect("close-request", on_close_request)
        self.present()

        # Run the loop until dialog is closed
        loop.run()

        # Clean up
        self.disconnect_by_func(on_close_request)

        # Destroy dialog if it's still visible
        if self.get_visible():
            self.destroy()


class Exception(Error):
    "Displays a traceback for an unhandled exception"

    def __init__(self, parent, traceback):
        Error.__init__(
            self, parent, _('Unknown error'),
            _('An unknown error occurred. Please report the text below to the Revelation developers, along with what you were doing that may have caused the error. You may attempt to continue running Revelation, but it may behave unexpectedly.')
        )

        self.add_button(_("_Quit"), Gtk.ResponseType.CANCEL)
        self.add_button(ui.STOCK_CONTINUE, Gtk.ResponseType.OK)

        # Load traceback section from UI file
        builder, unused_section = self.load_ui_section('/info/olasagasti/revelation/ui/exception.ui', 'exception_section', pack=False)

        # Get the scrolled window from UI file
        ui_scrolled = builder.get_object('traceback_scrolled')
        # Replace the textview with custom ui.TextView
        ui_textview = builder.get_object('traceback_textview')
        textview = ui.TextView(None, traceback)
        ui_scrolled.set_child(None)
        ui_scrolled.set_child(textview)

        ui_scrolled.set_hexpand(True)
        ui_scrolled.set_vexpand(True)
        self.contents.append(ui_scrolled)

    def run(self):
        "Runs the dialog"

        response = Dialog.run(self)
        self.destroy()
        return response == Gtk.ResponseType.OK


class PasswordChecker(Utility):
    "A password checker dialog"

    def __init__(self, parent, cfg = None, clipboard = None):
        Utility.__init__(self, parent, _('Password Checker'))

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        self.cfg = cfg
        self.set_modal(False)
        self.set_size_request(300, -1)

        # Load UI from file
        builder, section = self.load_ui_section('/info/olasagasti/revelation/ui/password-checker.ui', 'password_checker_section')

        # Set section title with markup
        set_section_title(builder, 'section_title', _('Password Checker'))

        # Get password entry from UI file and replace with PasswordEntry
        self.entry = replace_widget(builder, 'password_entry', ui.PasswordEntry(None, cfg, clipboard))
        self.entry.autocheck = False
        self.entry.set_width_chars(40)
        self.entry.connect("changed", self.__cb_changed)
        self.entry.set_tooltip_text(_('Enter a password to check'))

        # Get result display widgets from UI file (Box with Image and Label)
        self.result_container = builder.get_object('result_container')
        self.result_image = builder.get_object('result_image')
        self.result_label = builder.get_object('result_label')
        # Set initial icon
        self.result_image.set_from_icon_name(ui.STOCK_UNKNOWN)

        # Add label to sizegroup for alignment
        password_label = builder.get_object('password_label')
        self.sizegroup.add_widget(password_label)

    def __cb_changed(self, widget, data = None):
        "Callback for entry changes"

        password = self.entry.get_text()

        try:
            if len(password) == 0:
                icon    = ui.STOCK_UNKNOWN
                result  = _('Enter a password to check')

            else:
                util.check_password(password)
                icon    = ui.STOCK_PASSWORD_STRONG
                result  = _('The password seems good')

        except ValueError as reason:
            icon    = ui.STOCK_PASSWORD_WEAK
            result = _('The password %s') % str(reason)

        self.result_label.set_markup(util.escape_markup(result))
        self.result_image.set_from_icon_name(icon)



class PasswordGenerator(Utility):
    "A password generator dialog"

    def __init__(self, parent, cfg, clipboard = None):
        Utility.__init__(self, parent, _('Password Generator'))

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.add_button(ui.STOCK_GENERATE, Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        self.config = cfg
        self.set_modal(False)

        # Load UI from file
        builder, section = self.load_ui_section('/info/olasagasti/revelation/ui/password-generator.ui', 'password_generator_section')

        # Set section title with markup
        set_section_title(builder, 'section_title', _('Password Generator'))

        # Get widgets from UI file
        self.entry = replace_widget(builder, 'password_entry', ui.PasswordEntry(None, cfg, clipboard))
        self.entry.autocheck = False
        self.entry.set_editable(False)
        self.entry.set_tooltip_text(_('The generated password'))

        # Get spin button from UI file (range and adjustment already set in XML)
        self.spin_pwlen = builder.get_object('length_spin')
        self.config.bind("passwordgen-length", self.spin_pwlen, "value", Gio.SettingsBindFlags.DEFAULT)

        self.check_punctuation_chars = builder.get_object('punctuation_check')
        if self.config.get_int("passwordgen-length"):
            self.check_punctuation_chars.set_sensitive(True)
        self.config.bind("passwordgen-punctuation", self.check_punctuation_chars, "active", Gio.SettingsBindFlags.DEFAULT)
        self.check_punctuation_chars.set_tooltip_text(_('When passwords are generated, use punctuation characters like %, =, { or .'))

        # Set up response callback for Generate button (OK response)
        # OK generates password without closing, CLOSE closes the dialog
        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.OK:
                # Generate password
                self.__cb_response(dialog, response_id)
                # Return False to prevent dialog destruction (allow multiple generations)
                return False
            # For CLOSE or other responses, allow normal destruction
            return True

        self.connect_response(on_response)

    def __cb_response(self, widget, response):
        "Callback for dialog responses"

        if response == Gtk.ResponseType.OK:
            # Generate password
            password = util.generate_password(self.spin_pwlen.get_value(), self.check_punctuation_chars.get_active())
            self.entry.set_text(password)


# FUNCTIONS #

# Async dialog helper functions (GTK4-compliant, no nested loops)

def show_error_async(parent, title, message):
    """
    Shows an error dialog asynchronously (GTK4-compliant).
    Just presents the dialog - no callback needed for simple errors.
    """
    d = Error(parent, title, message)
    # Error dialogs should not have response callbacks - they just show and close
    # This prevents any exceptions from propagating and causing loops
    d._response_callback = None
    d.present()

def show_info_async(parent, title, message):
    """
    Shows an info dialog asynchronously (GTK4-compliant).
    Just presents the dialog - no callback needed for simple info.
    """
    d = Info(parent, title, message)
    # Info dialogs should not have response callbacks - they just show and close
    d._response_callback = None
    d.present()

def confirm_async(parent, title, message, callback):
    """
    Shows a confirmation dialog asynchronously (GTK4-compliant).
    Calls callback(True) if user confirms, callback(False) if cancelled.
    """
    d = Question(parent, title, message)
    d.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
    d.add_button(_("_Yes"), Gtk.ResponseType.OK)
    d.set_default_response(Gtk.ResponseType.OK)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.OK:
                callback(True)
            else:
                callback(False)
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def file_changes_async(dialog_class, parent, callback):
    """
    Shows a FileChanges dialog asynchronously (GTK4-compliant).
    Calls callback(True) if user wants to save, callback(False) if discard,
    or callback(None) if cancelled (caller should raise CancelError).
    """
    d = dialog_class(parent)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.OK:
                callback(True)
            elif response_id == Gtk.ResponseType.ACCEPT:
                callback(False)
            else:
                # CANCEL or CLOSE - callback receives None, caller should raise CancelError
                callback(None)
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def entry_remove_async(parent, entries, callback):
    """
    Shows an EntryRemove dialog asynchronously (GTK4-compliant).
    Calls callback(True) if user confirms, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    d = EntryRemove(parent, entries)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.OK:
                callback(True)
            else:
                # CANCEL or CLOSE - callback receives None, caller should raise CancelError
                callback(None)
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def file_save_insecure_async(parent, callback):
    """
    Shows a FileSaveInsecure dialog asynchronously (GTK4-compliant).
    Calls callback(True) if user confirms, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    d = FileSaveInsecure(parent)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.OK:
                callback(True)
            else:
                # CANCEL or CLOSE - callback receives None, caller should raise CancelError
                callback(None)
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def exception_async(parent, traceback, callback):
    """
    Shows an Exception dialog asynchronously (GTK4-compliant).
    Calls callback(True) if user wants to continue, callback(False) if quit.
    """
    d = Exception(parent, traceback)

    def on_response(dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            callback(True)
        else:
            callback(False)
        dialog.destroy()

    d.connect_response(on_response)
    d.present()

def file_selector_async(selector_class, parent, callback, *args):
    """
    Shows a file selector dialog asynchronously (GTK4-compliant).
    Calls callback(filename) if user accepts, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    d = selector_class(parent, *args)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.ACCEPT:
                filename = dialog.get_filename()
                callback(filename)
            else:
                callback(None)  # Caller should raise CancelError
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def export_file_selector_async(parent, callback):
    """
    Shows an ExportFileSelector dialog asynchronously (GTK4-compliant).
    Calls callback(filename, handler) if user accepts, or callback(None, None) if cancelled
    (caller should raise CancelError).
    """
    d = ExportFileSelector(parent)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.ACCEPT:
                filename = dialog.get_filename()
                handler = dialog.dropdown.get_active_item()[2]
                callback(filename, handler)
            else:
                callback(None, None)  # Caller should raise CancelError
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def import_file_selector_async(parent, callback):
    """
    Shows an ImportFileSelector dialog asynchronously (GTK4-compliant).
    Calls callback(filename, handler) if user accepts, or callback(None, None) if cancelled
    (caller should raise CancelError).
    """
    d = ImportFileSelector(parent)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.ACCEPT:
                filename = dialog.get_filename()
                handler = dialog.dropdown.get_active_item()[2]
                callback(filename, handler)
            else:
                callback(None, None)  # Caller should raise CancelError
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def password_open_async(parent, filename, callback):
    """
    Shows a PasswordOpen dialog asynchronously (GTK4-compliant).
    Calls callback(password) if user enters password, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    d = PasswordOpen(parent, filename)

    def on_response(dialog, response_id):
        try:
            if response_id == Gtk.ResponseType.OK:
                password = dialog.entry_password.get_text()
                callback(password)
            else:
                callback(None)  # Caller should raise CancelError
        except Exception as e:
            print("Unhandled callback exception:", e)
        finally:
            dialog.destroy()

    d.connect_response(on_response)
    d.present()

def password_open_sync(parent, filename):
    """
    Shows a PasswordOpen dialog synchronously.
    This is a wrapper around password_open_async() that uses a nested loop.
    Only used by datafile.load() which expects a synchronous callback.

    Returns password string or raises CancelError.
    """
    loop = GLib.MainLoop()
    result = [None]
    error = [None]

    def on_response(password):
        result[0] = password
        if loop.is_running():
            loop.quit()

    password_open_async(parent, filename, on_response)
    loop.run()

    if result[0] is None:
        raise CancelError
    return result[0]

def password_change_async(parent, current_password, callback):
    """
    Shows a PasswordChange dialog asynchronously (GTK4-compliant).
    Handles validation loop internally - re-prompts on validation errors.
    Calls callback(password) if user enters valid password, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    def show_dialog():
        d = PasswordChange(parent, current_password)

        def on_response(dialog, response_id):
            try:
                if response_id != Gtk.ResponseType.OK:
                    dialog.destroy()
                    callback(None)  # Caller should raise CancelError
                    return

                # Validate password
                if current_password is not None and dialog.entry_current.get_text() != current_password:
                    dialog.destroy()
                    show_error_async(parent, _('Incorrect password'), _('The password you entered as the current file password is incorrect.'))
                    # Re-prompt
                    show_dialog()
                    return

                if dialog.entry_new.get_text() != dialog.entry_confirm.get_text():
                    dialog.destroy()
                    show_error_async(parent, _('Passwords don\'t match'), _('The password and password confirmation you entered does not match.'))
                    # Re-prompt
                    show_dialog()
                    return

                password = dialog.entry_new.get_text()

                # Check password strength
                try:
                    util.check_password(password)
                    # Password is valid
                    dialog.destroy()
                    callback(password)
                except ValueError as res:
                    dialog.destroy()
                    # Ask user if they want to use insecure password
                    def on_insecure_response(result):
                        try:
                            if result is None or not result:
                                # User cancelled or said no - re-prompt
                                show_dialog()
                            else:
                                # User confirmed insecure password
                                callback(password)
                        except Exception as e:
                            print("Unhandled callback exception:", e)

                    confirm_async(parent, _('Use insecure password?'), 
                                _('The password you entered is not secure; %s. Are you sure you want to use it?') % str(res).lower(),
                                on_insecure_response)
            except Exception as e:
                print("Unhandled callback exception:", e)
                dialog.destroy()

        d.connect_response(on_response)
        d.present()

    show_dialog()

def password_save_async(parent, filename, callback):
    """
    Shows a PasswordSave dialog asynchronously (GTK4-compliant).
    Handles validation loop internally - re-prompts on validation errors.
    Calls callback(password) if user enters valid password, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    def show_dialog():
        d = PasswordSave(parent, filename)

        def on_response(dialog, response_id):
            try:
                if response_id != Gtk.ResponseType.OK:
                    dialog.destroy()
                    callback(None)  # Caller should raise CancelError
                    return

                # Validate password
                if dialog.entry_new.get_text() != dialog.entry_confirm.get_text():
                    dialog.destroy()
                    show_error_async(parent, _('Passwords don\'t match'), _('The passwords you entered does not match.'))
                    # Re-prompt
                    show_dialog()
                    return

                if len(dialog.entry_new.get_text()) == 0:
                    dialog.destroy()
                    show_error_async(parent, _('No password entered'), _('You must enter a password for the new data file.'))
                    # Re-prompt
                    show_dialog()
                    return

                password = dialog.entry_new.get_text()

                # Check password strength
                try:
                    util.check_password(password)
                    # Password is valid
                    dialog.destroy()
                    callback(password)
                except ValueError as res:
                    dialog.destroy()
                    # Ask user if they want to use insecure password
                    def on_insecure_response(result):
                        try:
                            if result is None or not result:
                                # User cancelled or said no - re-prompt
                                show_dialog()
                            else:
                                # User confirmed insecure password
                                callback(password)
                        except Exception as e:
                            print("Unhandled callback exception:", e)

                    confirm_async(parent, _('Use insecure password?'), 
                                _('The password you entered is not secure; %s. Are you sure you want to use it?') % str(res).lower(),
                                on_insecure_response)
            except Exception as e:
                print("Unhandled callback exception:", e)
                dialog.destroy()

        d.connect_response(on_response)
        d.present()

    show_dialog()

def entry_edit_async(parent, title, e, cfg, clipboard, callback):
    """
    Shows an EntryEdit dialog asynchronously (GTK4-compliant).
    Handles validation loop internally - re-prompts on validation errors.
    Calls callback(entry) if user enters valid entry, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    def show_dialog():
        d = EntryEdit(parent, title, e, cfg, clipboard)

        def on_response(dialog, response_id):
            try:
                if response_id != Gtk.ResponseType.OK:
                    dialog.destroy()
                    callback(None)  # Caller should raise CancelError
                    return

                entry_obj = dialog.get_entry()

                if entry_obj.name == "":
                    dialog.destroy()
                    show_error_async(parent, _('Name not entered'), _('You must enter a name for the account'))
                    # Re-prompt
                    show_dialog()
                    return

                # Entry is valid
                dialog.destroy()
                callback(entry_obj)
            except Exception as e:
                print("Unhandled callback exception:", e)
                dialog.destroy()

        d.connect_response(on_response)
        d.present()

    show_dialog()

def folder_edit_async(parent, title, e, callback):
    """
    Shows a FolderEdit dialog asynchronously (GTK4-compliant).
    Handles validation loop internally - re-prompts on validation errors.
    Calls callback(folder) if user enters valid folder, or callback(None) if cancelled
    (caller should raise CancelError).
    """
    def show_dialog():
        d = FolderEdit(parent, title, e)

        def on_response(dialog, response_id):
            try:
                if response_id != Gtk.ResponseType.OK:
                    dialog.destroy()
                    callback(None)  # Caller should raise CancelError
                    return

                folder_obj = dialog.get_entry()

                if folder_obj.name == "":
                    dialog.destroy()
                    show_error_async(parent, _('Name not entered'), _('You must enter a name for the folder'))
                    # Re-prompt
                    show_dialog()
                    return

                # Folder is valid
                dialog.destroy()
                callback(folder_obj)
            except Exception as e:
                print("Unhandled callback exception:", e)
                dialog.destroy()

        d.connect_response(on_response)
        d.present()

    show_dialog()

def password_lock_async(parent, password, callback, dialog_instance=None):
    """
    Shows a PasswordLock dialog asynchronously (GTK4-compliant).
    Handles validation loop internally - re-prompts on validation errors.
    Calls callback(password) if user enters correct password, or callback(None) if cancelled
    (caller should quit).
    """
    def show_dialog(d=None):
        if d is None:
            d = PasswordLock(parent, password)

        def on_response(dialog, response_id):
            try:
                if response_id != Gtk.ResponseType.OK:
                    dialog.destroy()
                    callback(None)  # Caller should quit
                    return

                entered_password = dialog.entry_password.get_text()

                if entered_password != password:
                    dialog.destroy()
                    show_error_async(parent, _('Incorrect password'), _('The password you entered was not correct, please try again.'))
                    # Re-prompt
                    show_dialog()
                    return

                # Password is correct
                dialog.destroy()
                callback(entered_password)
            except Exception as e:
                print("Unhandled callback exception:", e)
                dialog.destroy()

        d.connect_response(on_response)
        d.present()

    show_dialog(dialog_instance)

def show_unique_dialog(dialog_class, *args):
    """
    Shows a unique dialog (GTK4-compatible).
    If a dialog of this class is already visible, presents it.
    Otherwise, creates a new dialog and shows it.
    """
    # Check if dialog of this class is already visible
    if dialog_class in _visible_dialogs:
        d = _visible_dialogs[dialog_class]
        try:
            # Check if dialog is still valid
            if d.get_visible():
                d.present()
                return d
            else:
                # Dialog is not visible, remove it
                del _visible_dialogs[dialog_class]
        except (AttributeError, RuntimeError, GLib.GError, TypeError):
            # Dialog was destroyed, remove it
            if dialog_class in _visible_dialogs:
                del _visible_dialogs[dialog_class]

    # Create new dialog
    d = dialog_class(*args)

    # Track it as visible
    _visible_dialogs[dialog_class] = d

    # Connect to close-request to remove from tracking when closed
    def on_close(dialog):
        if dialog_class in _visible_dialogs:
            del _visible_dialogs[dialog_class]
        return False  # Allow close

    d.connect("close-request", on_close)

    # Also connect to destroy signal to handle programmatic destruction or ESC
    def on_destroy(dialog):
        _visible_dialogs.pop(dialog_class, None)

    d.connect("destroy", on_destroy)

    # Present the dialog
    d.present()

    return d
