#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module with miscellaneous functionality
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

import time, random, gtk, revelation


class SubstFormatError(Exception):
	"Exception for parse_subst format errors"
	pass


class SubstValueError(Exception):
	"Exception for missing values in parse_subst"
	pass



def parse_subst(string, subst):
	"Parses a string for substitution variables"

	result = ""

	i = 0
	while i < len(string):

		# handle normal characters
		if string[i] != "%":
			result += string[i]
			i += 1


		# handle % escapes (%%)
		elif string[i + 1] == "%":
			result += "%"
			i += 2


		# handle optional substitution variables
		elif string[i + 1] == "?":
			if subst.has_key(string[i + 2]):
				result += subst[string[i + 2]]
				i += 3

			else:
				raise SubstFormatError


		# handle optional substring expansions
		elif string[i + 1] == "(":

			try:
				result += parse_subst(string[i + 2:string.index("%)", i + 1)], subst)

			except ValueError:
				raise SubstFormatError

			except SubstValueError:
				pass

			i = string.index("%)", i + 1) + 2


		# handle required ("normal") substitution variables
		elif subst.has_key(string[i + 1]):

			if subst[string[i + 1]] in [ "", None ]:
				raise SubstValueError

			result += subst[string[i + 1]]
			i += 2


		# otherwise, it's a format error
		else:
			raise SubstFormatError


	return result

