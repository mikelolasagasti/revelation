#
# Revelation 0.4.6 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module with various utility functions
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import crack

import datetime, math, os, random, shlex, string, StringIO, traceback


class SubstFormatError(Exception):
	"Exception for parse_subst format errors"
	pass


class SubstValueError(Exception):
	"Exception for missing values in parse_subst"
	pass



def check_password(password):
	"Checks if a password is valid"

	# check for length
	if len(password) < 6:
		raise ValueError, "is too short"


	# check for entropy
	pwlen	= len(password)
	ent	= entropy(password)
	idealent = entropy_ideal(pwlen)

	if (pwlen < 100 and ent / idealent < 0.8) or (pwlen >= 100 and ent < 5.3):
		raise ValueError, "isn't varied enough"


	# check the password strength
	lc, uc, d, o = 0, 0, 0, 0

	for c in password:
		if c in string.ascii_lowercase:
			lc += 1

		elif c in string.ascii_uppercase:
			uc += 1

		elif c in string.digits:
			d += 1

		else:
			o += 1

	classcount = [ lc, uc, d, o ]
	classcount.sort()
	classcount.reverse()

	cred = sum([ count * (1 + (weight ** 2.161 / 10)) for weight, count in zip(range(1, len(classcount) + 1), classcount) ])

	if cred < 10:
		raise ValueError, "is too weak"


	# check if the password is a palindrome
	for i in range(len(password)):
		if password[i] != password[-i - 1]:
			break

	else:
		raise ValueError, "is a palindrome"


	# check password with cracklib
	try:
		if len(password) < 100:
			crack.FascistCheck(password)

	except ValueError, reason:

		# modify reason
		reason = str(reason).strip()
		reason = reason.replace("simplistic/systematic", "systematic")
		reason = reason.replace(" dictionary", "")

		if reason[:3] == "it ":
			reason = reason[3:]

		if reason[:5] == "it's ":
			reason = "is " + reason[5:]

		raise ValueError, reason

	except IOError:
		pass


def dom_text(node):
	"Returns text content of a DOM node"

	text = ""

	for child in node.childNodes:
		if child.nodeType == node.TEXT_NODE:
			text += child.nodeValue.encode("utf-8")

	return text


def entropy(string):
	"Calculates the Shannon entropy of a string"

	# get probability of chars in string
	prob = [ float(string.count(c)) / len(string) for c in dict.fromkeys(list(string)) ]

	# calculate the entropy
	entropy = - sum([ p * math.log(p) / math.log(2.0) for p in prob ])

	return entropy


def entropy_ideal(length):
	"Calculates the ideal Shannon entropy of a string with given length"

	prob = 1.0 / length

	return -1.0 * length * prob * math.log(prob) / math.log(2.0)


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

	# set up character sets
	d	= string.digits
	lc	= string.ascii_lowercase
	uc	= string.ascii_uppercase

	if avoidambiguous == True:
		d	= d.translate(string.maketrans("", ""), "015")
		lc	= lc.translate(string.maketrans("", ""), "lqg")
		uc	= uc.translate(string.maketrans("", ""), "IOS")

	fullset = d + uc + lc

	charsets = (
		( d,	0.15 ),
		( uc,	0.24 ),
		( lc,	0.24 ),
	)

	
	# function for generating password
	def genpw(length):
		password = []

		for set, share in charsets:
			password.extend([ random.choice(set) for i in range(int(round(length * share))) ])

		while len(password) < length:
			password.append(random.choice(fullset))

		random.shuffle(password)

		return "".join(password)


	# check password, and regenerate if needed
	while 1:
		try:
			password = genpw(length)

			if length <= 6:
				return password

			check_password(password)

			return password

		except ValueError:
			continue


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


def unescape_markup(string):
	"Unescapes a string to get literal values"

	string = string.replace("&amp;", "&")
	string = string.replace("&lt;", "<")
	string = string.replace("&gt;", ">")

	return string

