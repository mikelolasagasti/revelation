#
# Revelation 0.4.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module with various utility functions
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

import datetime, os, random, shlex, string, StringIO, traceback


class SubstFormatError(Exception):
	"Exception for parse_subst format errors"
	pass


class SubstValueError(Exception):
	"Exception for missing values in parse_subst"
	pass



def dom_text(node):
	"Returns text content of a DOM node"

	text = ""

	for child in node.childNodes:
		if child.nodeType == node.TEXT_NODE:
			text += child.nodeValue

	return text


def escape_markup(string):
	"Escapes a string so it can be placed in a markup string"

	string = string.replace("&", "&amp;")
	string = string.replace("<", "&lt;")
	string = string.replace(">", "&gt;")

	return string


def execute(command):
	"Runs a command, returns its status code and output"

	p = os.popen(command, "r")
	output = p.read()
	status = p.close()

	if status is None:
		status = 0

	status = status >> 8

	return output, status


def execute_child(command):
	"Runs a command as a child, returns its process ID"

	items = shlex.split(command.encode("iso-8859-1"), 0)
	return os.spawnvp(os.P_NOWAIT, items[0], items)


def generate_password(length, avoidambiguous = False):
	"Generates a password"

	password = []

	while len(password) < length:

		if len(password) < int(round(length * 0.15)):
			set = string.digits

		elif len(password) < int(round(length * (0.15 + 0.24))):
			set = string.ascii_lowercase

		elif len(password) < int(round(length * (0.15 + 0.24 + 0.24))):
			set = string.ascii_uppercase

		else:
			set = string.ascii_letters + string.digits


		char = set[int(random.random() * len(set))]

		if avoidambiguous == True and char in "0OIl1S5qg":
			continue

		password.append(char)


	random.shuffle(password)

	return "".join(password)


def pad_right(string, length, padchar = " "):
	"Right-pads a string to a given length"

	if string is None:
		return None

	if len(string) >= length:
		return string

	return string + ((length - len(string)) * padchar)


def parse_subst(string, map):
	"Parses a string for substitution variables"

	result = ""

	pos = 0
	while pos < len(string):

		char = string[pos]
		next = pos + 1 < len(string) and string[pos + 1] or ""


		# handle normal characters
		if char != "%":
			result += char
			pos += 1


		# handle % escapes (%%)
		elif next == "%":
			result += "%"
			pos += 2


		# handle optional substitution variables
		elif next == "?":
			if map.has_key(string[pos + 2]):
				result += map[string[pos + 2]]
				pos += 3

			else:
				raise SubstFormatError


		# handle optional substring expansions
		elif next == "(":

			try:
				result += parse_subst(string[pos + 2:string.index("%)", pos + 1)], map)

			except ValueError:
				raise SubstFormatError

			except SubstValueError:
				pass

			pos = string.index("%)", pos + 1) + 2


		# handle required ("normal") substitution variables
		elif map.has_key(next):

			if map[next] in [ "", None ]:
				raise SubstValueError

			result += map[next]
			pos += 2


		# otherwise, it's a format error
		else:
			raise SubstFormatError


	return result


def random_string(length):
	"Generates a random string"

	s = ""
	for i in range(length):
		s += chr(int(random.random() * 255))

	return s


def time_period_rough(start, end):
	"Returns the rough period from start to end in human-readable format"

	if end < start:
		return "0 seconds"

	start	= datetime.datetime.utcfromtimestamp(float(start))
	end	= datetime.datetime.utcfromtimestamp(float(end))
	delta	= end - start


	if delta.days >= 365:
		period, unit = delta.days / 365, "year"

	elif delta.days >= 31 or (end.month != start.month and (end.day > start.day or (end.day == start.day and end.time() >= start.time()))):
		period = ((end.year - start.year) * 12) + end.month - start.month

		if end.day < start.day or (end.day == start.day and end.time() < start.time()):
			period -= 1

		unit = "month"

	elif delta.days >= 7:
		period, unit = delta.days / 7, "week"

	elif delta.days >= 1:
		period, unit = delta.days, "day"

	elif delta.seconds >= 3600:
		period, unit = delta.seconds / 3600, "hour"

	elif delta.seconds >= 60:
		period, unit = delta.seconds / 60, "minute"

	else:
		period, unit = delta.seconds, "second"


	return "%d %s" % ( period, unit + (period != 1 and "s" or "") )


def trace_exception(type, value, tb):
	"Returns an exception traceback as a string"

	trace = StringIO.StringIO()
	traceback.print_exception(type, value, tb, None, trace)

	return trace.getvalue()

