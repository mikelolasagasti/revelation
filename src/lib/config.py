#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# module for configuration handling
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

from . import util
import gettext, os, sys

_ = gettext.gettext

DIR_PREFIX      = sys.path[0]
DIR_ICONS       = DIR_PREFIX+"/data/icons"
DIR_LOCALE      = DIR_PREFIX+"/data/locale"
DIR_UI          = DIR_PREFIX+"/data/ui"
DIR_GSCHEMAS    = DIR_PREFIX+"/data/schemas"

APPNAME     = "Revelation"
PACKAGE     = "revelation"
VERSION     = "0.5.0"
DATAVERSION = 2
RELNAME     = "One Toke Over the Line"
URL         = "http://revelation.olasagasti.info/"
AUTHORS     = [ "Erik Grinaker <erikg@codepoet.no>","Mikel Olasagasti Uranga <mikel@olasagasti.info>" ]
ARTISTS     = [ "Erik Grinaker <erikg@codepoet.no>" ]
COPYRIGHT   = _('Copyright') + " \302\251 2003-2007 Erik Grinaker\n2010-2012 Mikel Olasagasti Uranga"
LICENSE     = _("""Revelation is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Revelation is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Revelation; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA""")



class ConfigError(Exception):
    "Configuration error exception"
    pass
