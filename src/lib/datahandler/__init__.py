#
# Revelation 0.4.5 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for data handlers
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

from base import HandlerError, DataError, FormatError, PasswordError, VersionError

from fpm import FPM
from gpass import GPass04, GPass05
from netrc import NetRC
from pwsafe import PasswordSafe1, PasswordSafe2, MyPasswordSafe, PasswordGorilla
from rvl import RevelationXML, Revelation
from text import PlainText
from xhtml import XHTML

HANDLERS = [
	FPM,
	GPass04,
	GPass05,
	MyPasswordSafe,
	NetRC,
	PasswordGorilla,
	PasswordSafe1,
	PasswordSafe2,
	PlainText,
	Revelation,
	XHTML,
	RevelationXML
]


class DetectError(Exception):
	"Exception for autodetection error"
	pass


def detect_handler(input):
	"Detects which handler may process a data stream"

	for handler in get_import_handlers():
		if handler().detect(input) == True:
			return handler

	else:
		raise DetectError


def get_export_handlers():
	"Returns a list of handlers which can export"

	handlers = []

	for handler in HANDLERS:
		if handler.exporter:
			handlers.append(handler)

	return handlers


def get_import_handlers():
	"Returns a list of handlers which can import"	

	handlers = []

	for handler in HANDLERS:
		if handler.importer:
			handlers.append(handler)

	return handlers

