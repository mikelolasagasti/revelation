#
# Revelation 0.4.4 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Library initialization script
#
#
# Copyright (c) 2003-2005 Erik Grinaker
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

import crack
import util
import config
import gnomemisc
import datahandler
import io
import entry
import data
import ui
import dialog


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

