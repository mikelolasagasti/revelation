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
import urllib.parse
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gtk, Gio, Gdk, GLib  # noqa: E402

_ = gettext.gettext


EVENT_FILTER        = None
UNIQUE_DIALOGS      = {}


# EXCEPTIONS #

class CancelError(Exception):
    "Exception for dialog cancellations"
    pass


# BASE DIALOGS #

class Dialog(Gtk.Dialog):
    "Base class for dialogs"

    def __init__(self, parent, title):
        Gtk.Dialog.__init__(self, title=title)

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
            self.response(Gtk.ResponseType.CLOSE)
            return True
        return False

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

        return builder, section

    def run(self):
        "Runs the dialog"

        self.show_all()

        loop = GLib.MainLoop()
        response = [None]  # Use list to allow modification in closure

        def on_response(dialog, response_id):
            response[0] = response_id
            loop.quit()

        self.connect("response", on_response)
        self.present()

        # Run the loop until response is received
        loop.run()

        # Clean up
        self.disconnect_by_func(on_response)

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
    widget_parent.show_all()
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

        self.show_all()
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
        self.set_local_only(False)
        self.inputsection = None

    def add_widget(self, title, widget):
        "Adds a widget to the file selection"

        if self.inputsection is None:
            self.inputsection = ui.InputSection()
            self.set_extra_widget(self.inputsection)

        self.inputsection.append_widget(title, widget)

    def get_filename(self):
        "Returns the file URI (for portal compatibility)"

        return self.get_uri()

    def get_file_path(self):
        "Returns the file path (for backward compatibility)"

        uri = self.get_uri()
        if uri is None:
            return None
        if uri.startswith('file://'):
            return io.file_normpath(urllib.parse.unquote(uri))
        # For portal URIs, we can't convert to path
        return None

    def run(self):
        "Displays and runs the file selector, returns the filename"

        response = Gtk.FileChooserNative.run(self)
        filename = self.get_filename()
        self.destroy()

        if response == Gtk.ResponseType.ACCEPT:
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

        self.inputsection.show_all()

        if Gtk.FileChooserNative.run(self) == Gtk.ResponseType.ACCEPT:
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

        self.inputsection.show_all()

        if Gtk.FileChooserNative.run(self) == Gtk.ResponseType.ACCEPT:
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

        self.set_do_overwrite_confirmation(True)
        self.connect("confirm-overwrite", self.__cb_confirm_overwrite)

    def __cb_confirm_overwrite(self, widget, data = None):
        "Handles confirm-overwrite signals"

        try:
            # Always use display name for UI - never show raw URIs or portal paths to users
            display_name = io.file_get_display_name(self.get_uri())
            FileReplace(self, display_name).run()

        except CancelError:
            return Gtk.FileChooserConfirmation.SELECT_AGAIN

        else:
            return Gtk.FileChooserConfirmation.ACCEPT_FILENAME


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

        self.show_all()

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

        self.get_widget_for_response(Gtk.ResponseType.CANCEL).set_label(_("_Quit"))
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
                if self.get_widget_for_response(Gtk.ResponseType.CANCEL).get_property("sensitive"):
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

        # Get entry widgets from UI file
        self.entry_name = get_entry(builder, 'name_entry')
        self.entry_desc = get_entry(builder, 'description_entry')

        # Add EntryDropDown to Box container (defined in XML)
        dropdown_container = builder.get_object('type_dropdown_container')
        self.dropdown = ui.EntryDropDown()
        self.dropdown.connect("changed", lambda w: self.__setup_fieldsect(self.dropdown.get_active_type()().fields))
        dropdown_container.append(self.dropdown)
        dropdown_container.show_all()

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
        notes_placeholder_parent.show_all()

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

        # show widgets
        self.sect_fields.show_all()

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
            self.show_all()

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
            self.show_all()

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

    def run(self):
        "Displays the dialog"

        self.show_all()
        Dialog.run(self)

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

        self.show_all()
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

        self.connect("response", self.__cb_response)

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

    def __cb_response(self, widget, response):
        "Callback for response"

        self.destroy()

    def run(self):
        "Displays the dialog"

        self.show_all()

        # for some reason, Gtk crashes on close-by-escape
        # if we don't do this
        self.get_widget_for_response(Gtk.ResponseType.CLOSE).grab_focus()
        self.entry.grab_focus()


class PasswordGenerator(Utility):
    "A password generator dialog"

    def __init__(self, parent, cfg, clipboard = None):
        Utility.__init__(self, parent, _('Password Generator'))

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.add_button(ui.STOCK_GENERATE, Gtk.ResponseType.OK)

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

        self.connect("response", self.__cb_response)

    def __cb_response(self, widget, response):
        "Callback for dialog responses"

        if response == Gtk.ResponseType.OK:
            self.entry.set_text(util.generate_password(self.spin_pwlen.get_value(), self.check_punctuation_chars.get_active()))

        else:
            self.destroy()

    def run(self):
        "Displays the dialog"

        self.show_all()
        self.get_widget_for_response(Gtk.ResponseType.OK).grab_focus()


# FUNCTIONS #

def create_unique_dialog(dialog, *args):
    "Creates a unique dialog or returns existing one"

    if unique_exists(dialog):
        return get_unique(dialog)

    UNIQUE_DIALOGS[dialog] = dialog(*args)
    UNIQUE_DIALOGS[dialog].connect("destroy", lambda w: remove_unique(dialog))
    return UNIQUE_DIALOGS[dialog]


def get_unique(dialog):
    "Returns a unique dialog if it exists, None otherwise"

    if unique_exists(dialog):
        return UNIQUE_DIALOGS[dialog]
    return None


def present_unique(dialog):
    "Presents a unique dialog if it exists, returns True if presented"

    if unique_exists(dialog):
        get_unique(dialog).present()
        return True
    return False


def remove_unique(dialog):
    "Removes a unique dialog"

    if unique_exists(dialog):
        UNIQUE_DIALOGS[dialog] = None


def run_unique_dialog(dialog, *args):
    "Runs a unique dialog, returns None if already presented"

    if present_unique(dialog):
        return None

    d = create_unique_dialog(dialog, *args)
    return d.run()


def unique_exists(dialog):
    "Checks if a unique dialog exists"

    return dialog in UNIQUE_DIALOGS and UNIQUE_DIALOGS[dialog] is not None
