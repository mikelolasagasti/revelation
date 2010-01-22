#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for data handlers
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

from base import Error, DataError, FormatError, PasswordError, VersionError

from csvfile import CSV
from fpm import FPM
from gpass import GPass04, GPass05
from netrc import NetRC
from pwsafe import PasswordSafe1, PasswordSafe2, MyPasswordSafe, MyPasswordSafeOld, PasswordGorilla
from rvl import RevelationXML, Revelation, Revelation2, RevelationLUKS
from splashid import SplashIDCSV
from text import PlainText
from xhtml import XHTML

HANDLERS = [
	CSV,
	FPM,
	GPass04,
	GPass05,
	MyPasswordSafe,
	MyPasswordSafeOld,
	NetRC,
	PasswordGorilla,
	PasswordSafe1,
	PasswordSafe2,
	PlainText,
	Revelation,
	Revelation2,
	RevelationLUKS,
	SplashIDCSV,
	XHTML,
	RevelationXML
]


class DetectError(Error):
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

