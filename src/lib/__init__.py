#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Library initialization script
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


import datahandler, misc, stock, entry, widget, ui, data, io, dialog, druid, sys

APPNAME = "Revelation"
VERSION = "0.3.0"
DATAVERSION = 1
RELNAME = "When the mind rests on nothing, true mind appears"
URL = "http://oss.codepoet.no/revelation/"
AUTHOR = "Erik Grinaker <erikg@codepoet.no>"
COPYRIGHT = "Copyright \302\251 2003-2004 Erik Grinaker"

PREFIX = sys.prefix
DATADIR = PREFIX + "/share/revelation"

# set up some exceptions
class Error(Exception):
	"""Base class for errors"""
	pass

class CancelError(Error):
	"""Exception for user cancellation"""
	pass

class FileError(Error):
	"""Exception for file errors"""
	pass

