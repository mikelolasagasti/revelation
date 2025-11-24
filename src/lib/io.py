#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for IO-related functionality
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

from . import datahandler

import gettext
from gi.repository import Gio, GObject, GLib

_ = gettext.gettext


class DataFile(GObject.GObject):
    "Handles data files"

    def __init__(self, handler):
        GObject.GObject.__init__(self)

        self.__gfile    = None  # Store Gio.File object directly (GTK4 best practice)
        self.__handler      = None
        self.__password     = None
        self.__monitorhandle    = None

        self.set_handler(handler)

    def __str__(self):
        # Return display name for string representation (user-friendly)
        return self.get_file_display_name() or ""

    def __cb_monitor(self, monitor, gfile, other_file, event):
        "Callback for file monitoring"
        if event == Gio.FileMonitorEvent.CHANGED:
            # Emit display name for UI, not raw URI
            self.emit("content-changed", self.get_file_display_name())

    def __monitor(self, gfile):
        "Starts monitoring a file"

        self.__monitor_stop()

        if gfile is not None:
            try:
                self.__monitorhandle = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
                self.__monitorhandle.connect('changed', self.__cb_monitor)
            except GLib.GError:
                # Monitoring may not be supported for portal documents or other reasons
                # This is expected and fine - autosave will still work
                self.__monitorhandle = None

    def __monitor_stop(self):
        "Stops monitoring the current file"

        if self.__monitorhandle is not None:
            self.__monitorhandle.cancel()
            self.__monitorhandle = None

    def close(self):
        "Closes the current file"

        self.set_password(None)
        self.set_file(None)

    def get_file(self):
        "Gets the current file as a Gio.File object"

        return self.__gfile

    def get_file_display_name(self):
        "Gets a user-friendly display name for the current file. Never returns portal paths or raw URIs."

        return file_get_display_name(self.__gfile)

    def get_file_display_path(self):
        "Gets a user-friendly full path for statusbar messages. Shows full path when available, filename for portal documents."

        return file_get_display_path(self.__gfile)

    def get_file_path(self):
        "Gets the current file path (for backward compatibility)"

        if self.__gfile is None:
            return None
        path = self.__gfile.get_path()
        return path

    def get_handler(self):
        "Gets the current handler"

        return self.__handler

    def get_password(self):
        "Gets the current password"

        return self.__password

    def load(self, file_or_uri, password = None, pwgetter = None):
        """
        Loads a file synchronously.

        DEPRECATED: Use load_async() instead. This method will be removed in a future version.
        The pwgetter parameter is deprecated - callers should prompt for password before calling load_async().
        """
        # Convert to GFile once, use throughout
        gfile = as_gfile(file_or_uri)
        if gfile is None:
            raise IOError("Invalid file or URI")

        # Read file directly using GFile API
        try:
            ok, data, etag = gfile.load_contents()
            if not ok:
                raise IOError("Failed to read file")
        except GLib.GError as e:
            raise IOError(f"Error reading file: {e}")

        if self.__handler is None:
            self.__handler = datahandler.detect_handler(data)()

        self.__handler.check(data)

        if self.__handler.encryption and password is None and pwgetter is not None:
            password = pwgetter()

        entrystore = self.__handler.import_data(data, password)

        self.set_password(password)
        self.set_file(gfile)

        return entrystore

    def load_async(self, file_or_uri, password, callback, cancellable=None):
        """
        Loads a file asynchronously.

        Args:
            file_or_uri: File path, URI, or Gio.File object
            password: Password for encrypted files (None if not encrypted or not yet provided)
            callback: Function called with (entrystore, error) where error is None on success
            cancellable: Optional Gio.Cancellable
        """
        # Convert to GFile once, use throughout
        gfile = as_gfile(file_or_uri)
        if gfile is None:
            callback(None, IOError("Invalid file or URI"))
            return

        # Read file asynchronously using GFile API
        def on_contents_loaded(source, result):
            try:
                ok, data, etag = source.load_contents_finish(result)
                if not ok:
                    callback(None, IOError("Failed to read file"))
                    return
            except GLib.GError as e:
                callback(None, IOError(f"Error reading file: {e}"))
                return

            try:
                if self.__handler is None:
                    self.__handler = datahandler.detect_handler(data)()

                self.__handler.check(data)

                # Note: password must be provided by caller before calling load_async
                # If encryption is required and password is None, caller should prompt first
                entrystore = self.__handler.import_data(data, password)

                self.set_password(password)
                self.set_file(gfile)

                callback(entrystore, None)
            except Exception as e:
                callback(None, e)

        gfile.load_contents_async(cancellable, on_contents_loaded)

    def save_async(self, entrystore, file, password, callback, cancellable=None):
        """
        Saves an entrystore to a file asynchronously.

        Args:
            entrystore: The entry store to save
            file: File path, URI, or Gio.File object
            password: Password for encryption (None if not encrypted)
            callback: Function called with (success, error) where error is None on success
            cancellable: Optional Gio.Cancellable
        """
        # Convert to GFile if needed
        gfile = as_gfile(file)
        if gfile is None:
            callback(False, IOError("Invalid file or URI"))
            return

        self.__monitor_stop()

        # Prepare data for writing
        data = self.__handler.export_data(entrystore, password)
        if data is None:
            data = ""
        if isinstance(data, str):
            data = data.encode()

        def on_contents_replaced(source, result):
            try:
                ok, etag = source.replace_contents_finish(result)
                if not ok:
                    callback(False, IOError("Failed to write file"))
                    return
            except GLib.GError as e:
                callback(False, IOError(f"Error writing file: {e}"))
                return

            # need to use idle_add() to avoid notifying about current save
            GLib.idle_add(lambda: self.__monitor(gfile))

            self.set_password(password)
            self.set_file(gfile)

            callback(True, None)

        gfile.replace_contents_async(
            data, None, True, Gio.FileCreateFlags.REPLACE_DESTINATION,
            cancellable, on_contents_replaced
        )

    def save(self, entrystore, file, password = None):
        """
        Saves an entrystore to a file synchronously.

        DEPRECATED: Use save_async() instead. This method will be removed in a future version.
        """
        # Convert to GFile if needed
        gfile = as_gfile(file)
        if gfile is None:
            raise IOError("Invalid file or URI")

        self.__monitor_stop()

        # Write file directly using GFile API
        data = self.__handler.export_data(entrystore, password)
        if data is None:
            data = ""
        if isinstance(data, str):
            data = data.encode()

        try:
            ok, etag = gfile.replace_contents(data, None, True, Gio.FileCreateFlags.REPLACE_DESTINATION, None)
            if not ok:
                raise IOError("Failed to write file")
        except GLib.GError as e:
            raise IOError(f"Error writing file: {e}")

        # need to use idle_add() to avoid notifying about current save
        GLib.idle_add(lambda: self.__monitor(gfile))

        self.set_password(password)
        self.set_file(gfile)

    def set_file(self, file_or_uri):
        "Sets the current file"

        # Convert to GFile immediately - handles paths, URIs, and GFile objects
        if file_or_uri is None:
            gfile = None
        elif isinstance(file_or_uri, Gio.File):
            gfile = file_or_uri
        else:
            gfile = as_gfile(file_or_uri)

        # Check if changed using GFile.equal() method
        if self.__gfile is None and gfile is None:
            return  # No change

        if self.__gfile is None or gfile is None or not self.__gfile.equal(gfile):
            # Changed - update file
            self.__gfile = gfile

            # Emit the canonical URI for backward compatibility
            uri = gfile.get_uri() if gfile else None
            self.emit("changed", uri)

            # Monitor the GFile directly
            self.__monitor(gfile)

    def set_handler(self, handler):
        "Sets and initializes the current data handler"

        self.__handler = handler is not None and handler() or None

    def set_password(self, password):
        "Sets the password for the current file"

        self.__password = password


GObject.type_register(DataFile)
GObject.signal_new("changed", DataFile, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, (str,))
GObject.signal_new("content-changed", DataFile, GObject.SignalFlags.ACTION,
                   GObject.TYPE_BOOLEAN, (str,))


def as_gfile(file_or_uri):
    "Converts a file path, URI, or Gio.File to a Gio.File object"

    # If already a GFile, return it directly
    if isinstance(file_or_uri, Gio.File):
        return file_or_uri

    if not file_or_uri:
        return None

    # Handle URIs (file://, portal://, etc.)
    if isinstance(file_or_uri, str) and "://" in file_or_uri:
        return Gio.File.new_for_uri(file_or_uri)

    # Handle paths
    return Gio.File.new_for_path(file_or_uri)


def file_exists(file_or_uri):
    "Checks if a file exists"

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        return False
    return gfile.query_exists()


def file_is_local(file_or_uri):
    "Checks if a file is on a local filesystem"

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        return False
    return gfile.is_native()


def file_get_display_name(file_or_gfile):
    "Gets a human-readable filename from GFile. Never returns portal paths or raw URIs."

    gfile = as_gfile(file_or_gfile)
    if gfile is None:
        return _("Untitled file")

    parse_name = gfile.get_parse_name()
    basename = gfile.get_basename()

    # If parse_name looks like a portal document path, use basename instead
    if parse_name and not _is_portal_path(parse_name):
        return parse_name

    return basename or _("Untitled file")


def _is_portal_path(path):
    "Checks if a path looks like a portal document path (internal implementation detail, not for users)"

    if not path or not isinstance(path, str):
        return False

    # Portal documents can be in /run/user/*/doc/ or /run/flatpak/doc/
    return (path.startswith("/run/user/") and "/doc/" in path) or \
           (path.startswith("/run/flatpak/doc/"))


def file_get_display_path(file_or_gfile):
    "Gets a user-friendly full path for display in statusbar messages. Shows full path when available, filename for portal documents."

    gfile = as_gfile(file_or_gfile)
    if gfile is None:
        return _("Untitled file")

    parse_name = gfile.get_parse_name()
    basename = gfile.get_basename()

    # If it's a portal path, show only the filename (we don't have the real path)
    if parse_name and _is_portal_path(parse_name):
        return basename or _("Untitled file")

    # For regular files, show the full parse_name (user-friendly path)
    if parse_name:
        return parse_name

    # Fallback to basename if parse_name is not available
    return basename or _("Untitled file")
