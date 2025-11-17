#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for IO-related functionality
#
# TODO GTK4 Migration Notes:
# ===========================
# This module currently uses URI strings (self.__uri) for file handling.
# For GTK4 migration, consider storing Gio.File objects directly:
#
# Benefits:
# - Eliminates file_normpath() and as_gfile() conversion overhead
# - GFile handles paths/URIs transparently - no ad-hoc detection needed
# - Aligns with GTK4 best practices (GFile is the standard abstraction)
# - Simplifies all file operations (read, write, monitor, etc.)
# - Better type safety and clearer code
#
# Migration path:
# 1. Change DataFile.__uri to DataFile.__gfile (Gio.File)
# 2. Convert paths/URIs to GFile immediately in public API methods
# 3. Remove file_normpath() - GFile handles normalization
# 4. Remove as_gfile() - convert directly with Gio.File.new_for_path/uri()
# 5. Update all file operations to work with GFile objects directly
# 6. Keep public API accepting paths/URIs for backward compatibility
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
import os.path
import re
from gi.repository import Gio, GObject, GLib

_ = gettext.gettext


class DataFile(GObject.GObject):
    "Handles data files"

    # TODO GTK4: Migrate to store Gio.File objects directly instead of URI strings
    # - Change self.__uri to self.__gfile (Gio.File)
    # - Convert paths/URIs to GFile immediately in set_file()
    # - get_file() returns self.__gfile.get_uri() if needed, or the GFile object
    # - This eliminates need for file_normpath() and as_gfile() conversions
    # - Simplifies all file operations and aligns with GTK4 best practices

    def __init__(self, handler):
        GObject.GObject.__init__(self)

        self.__uri      = None
        self.__handler      = None
        self.__password     = None
        self.__monitorhandle    = None

        self.set_handler(handler)

    def __str__(self):
        # Return display name for string representation (user-friendly)
        return self.get_file_display_name() or ""

    def __cb_monitor(self, monitor_uri, info_uri, event, data = None):
        "Callback for file monitoring"
        if event == Gio.FileMonitorEvent.CHANGED:
            # Emit display name for UI, not raw URI
            self.emit("content-changed", self.get_file_display_name())

    def __monitor(self, file):
        "Starts monitoring a file"

        # TODO GTK4: If using GFile, this becomes:
        #   def __monitor(self, gfile):
        #       self.__monitor_stop()
        #       if gfile is not None:
        #           self.__monitorhandle = gfile.monitor_file(...)
        #   No need for file_monitor() helper

        self.__monitor_stop()

        if file is not None:
            self.__monitorhandle = file_monitor(file, self.__cb_monitor)

    def __monitor_stop(self):
        "Stops monitoring the current file"

        if self.__monitorhandle is not None:
            file_monitor_cancel(self.__monitorhandle)
            self.__monitorhandle = None

    def close(self):
        "Closes the current file"

        self.set_password(None)
        self.set_file(None)

    def get_file(self):
        "Gets the current file URI"

        return self.__uri

    def get_file_display_name(self):
        "Gets a user-friendly display name for the current file. Never returns portal paths or raw URIs."

        return file_get_display_name(self.__uri)

    def get_file_display_path(self):
        "Gets a user-friendly full path for statusbar messages. Shows full path when available, filename for portal documents."

        return file_get_display_path(self.__uri)

    def get_file_path(self):
        "Gets the current file path (for backward compatibility)"

        if self.__uri and self.__uri.startswith('file://'):
            return re.sub("^file://", "", str(self.__uri))
        return None

    def get_handler(self):
        "Gets the current handler"

        return self.__handler

    def get_password(self):
        "Gets the current password"

        return self.__password

    def load(self, file_or_uri, password = None, pwgetter = None):
        "Loads a file"

        # TODO GTK4: Simplify - convert to GFile once, use throughout:
        #   gfile = as_gfile(file_or_uri) if not isinstance(file_or_uri, Gio.File) else file_or_uri
        #   data = gfile.load_contents()[1]  # Direct GFile operation
        #   self.__gfile = gfile
        #   No need for file_normpath() or intermediate URI conversions

        # file_normpath now preserves URIs, so we can pass it directly
        file_or_uri = file_normpath(file_or_uri)
        data = file_read(file_or_uri)

        if self.__handler is None:
            self.__handler = datahandler.detect_handler(data)()

        self.__handler.check(data)

        if self.__handler.encryption and password is None and pwgetter is not None:
            password = pwgetter()

        entrystore = self.__handler.import_data(data, password)

        self.set_password(password)
        self.set_file(file_or_uri)

        return entrystore

    def save(self, entrystore, file, password = None):
        "Saves an entrystore to a file"

        # TODO GTK4: If using GFile, this becomes:
        #   gfile = as_gfile(file) if not isinstance(file, Gio.File) else file
        #   gfile.replace_contents(...)  # Direct operation
        #   self.__gfile = gfile
        #   self.__monitor(gfile)  # Pass GFile directly

        self.__monitor_stop()
        file_write(file, self.__handler.export_data(entrystore, password))

        # need to use idle_add() to avoid notifying about current save
        GLib.idle_add(lambda: self.__monitor(file))

        self.set_password(password)
        self.set_file(file)

    def set_file(self, file_or_uri):
        "Sets the current file"

        # TODO GTK4: Simplify this - convert to GFile immediately:
        #   if file_or_uri is None:
        #       self.__gfile = None
        #   else:
        #       self.__gfile = as_gfile(file_or_uri)  # or Gio.File.new_for_path/uri directly
        #   self.emit("changed", self.__gfile.get_uri() if self.__gfile else None)

        # If it's already a file:// URI, use it; otherwise convert path to file:// URI
        if file_or_uri is None:
            uri = None
        elif file_or_uri.startswith("file://"):
            uri = file_or_uri
        else:
            # Convert path to file:// URI
            path = file_normpath(file_or_uri)
            if path:
                gfile = as_gfile(path)
                if gfile:
                    uri = gfile.get_uri()
                else:
                    uri = None
            else:
                uri = None

        if self.__uri != uri:
            self.__uri = uri
            # Emit the canonical URI, not the original input
            self.emit("changed", uri)

            # Monitor the canonical URI, not the original input
            # This ensures we're monitoring the actual file that's stored
            self.__monitor(uri)

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
    "Converts a file path or URI to a Gio.File object"

    # TODO GTK4: This helper can be removed if DataFile stores GFile directly
    # Public API can accept paths/URIs and convert immediately to GFile
    # All internal operations work with GFile objects

    if not file_or_uri:
        return None

    if file_or_uri.startswith("file://"):
        return Gio.File.new_for_uri(file_or_uri)
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
    return gfile.get_uri_scheme() == 'file'


def file_monitor(file_or_uri, callback):
    "Starts monitoring a file. Returns None if monitoring is not supported (e.g., portal documents)"

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        return None

    try:
        handle = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
        handle.connect('changed', callback)
        return handle
    except GLib.GError:
        # Monitoring may not be supported for portal documents or other reasons
        # This is expected and fine - autosave will still work
        # Return None to indicate monitoring is not available
        return None


def file_monitor_cancel(handle):
    "Cancels file monitoring"

    handle.cancel()


def file_normpath(file_or_uri):
    "Normalizes a file path or preserves file:// URIs"

    # TODO GTK4: This function can be removed entirely
    # - GFile handles paths and URIs transparently
    # - No need to normalize before creating GFile objects
    # - GFile.new_for_path() and GFile.new_for_uri() handle all cases
    # - Only kept for backward compatibility with existing code that expects normalized paths

    if not file_or_uri:
        return ""

    # Preserve file:// URIs as-is
    if file_or_uri.startswith("file://"):
        return file_or_uri

    # Otherwise, normalize path (backward compatibility)
    return os.path.abspath(os.path.expanduser(file_or_uri))


def file_read(file_or_uri):
    "Reads data from a file"

    # TODO GTK4: If DataFile stores GFile, this can accept GFile directly:
    #   def file_read(gfile):
    #       if gfile is None: raise IOError
    #       ok, contents, etag = gfile.load_contents()
    #       return contents

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        raise IOError

    try:
        ok, contents, etag = gfile.load_contents()
        return contents
    except GLib.GError:
        raise IOError


def file_write(file_or_uri, data):
    "Writes data to file"

    # TODO GTK4: If DataFile stores GFile, this can accept GFile directly:
    #   def file_write(gfile, data):
    #       if gfile is None: raise IOError
    #       ... rest of function works with gfile directly

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        raise IOError

    if data is None:
        data = ""

    if isinstance(data, str):
        data = data.encode()

    try:
        ok, etag = gfile.replace_contents(data, None, True, Gio.FileCreateFlags.REPLACE_DESTINATION, None)
        return ok
    except GLib.GError:
        raise IOError


def file_get_display_name(file_or_uri):
    "Gets a human-readable filename from URI or path using GIO's parse_name. Never returns portal paths or raw URIs."

    # TODO GTK4: If DataFile stores GFile, this can accept GFile directly:
    #   def file_get_display_name(gfile):
    #       if gfile is None: return _("Untitled file")
    #       parse_name = gfile.get_parse_name()
    #       # If parse_name looks like a portal path, use basename instead
    #       if parse_name and _is_portal_path(parse_name):
    #           return gfile.get_basename() or _("Untitled file")
    #       return parse_name or gfile.get_basename() or _("Untitled file")

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        return _("Untitled file")

    # Use get_parse_name() for user-friendly display names
    parse_name = gfile.get_parse_name()

    # If parse_name looks like a portal document path (temporary sandbox path),
    # use basename instead to avoid showing /run/user/.../doc/... or /run/flatpak/doc/... to users
    if parse_name and _is_portal_path(parse_name):
        basename = gfile.get_basename()
        if basename:
            return basename
        return _("Untitled file")

    if parse_name:
        return parse_name

    # Fallback to basename if parse_name is not available
    basename = gfile.get_basename()
    if basename:
        return basename

    # Last resort: return a generic name rather than exposing internal paths/URIs
    return _("Untitled file")


def _is_portal_path(path):
    "Checks if a path looks like a portal document path (internal implementation detail, not for users)"

    if not path or not isinstance(path, str):
        return False

    # Portal documents can be in /run/user/*/doc/ or /run/flatpak/doc/
    return (path.startswith("/run/user/") and "/doc/" in path) or \
           (path.startswith("/run/flatpak/doc/"))


def file_get_display_path(file_or_uri):
    "Gets a user-friendly full path for display in statusbar messages. Shows full path when available, filename for portal documents."

    gfile = as_gfile(file_or_uri)
    if gfile is None:
        return _("Untitled file")

    # Use get_parse_name() for user-friendly display names
    parse_name = gfile.get_parse_name()

    # If it's a portal path, show only the filename (we don't have the real path)
    if parse_name and _is_portal_path(parse_name):
        basename = gfile.get_basename()
        if basename:
            return basename
        return _("Untitled file")

    # For regular files, show the full parse_name (user-friendly path)
    if parse_name:
        return parse_name

    # Fallback to basename if parse_name is not available
    basename = gfile.get_basename()
    if basename:
        return basename

    return _("Untitled file")
