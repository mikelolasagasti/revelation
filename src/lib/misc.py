#
# Revelation 0.3.2 - a password manager for GNOME 2
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

import time, random, gtk


def escape_markup(string):
	"Escapes a string so it can be placed in a markup string"

	string = string.replace("&", "&amp;")
	string = string.replace("<", "&lt;")
	string = string.replace(">", "&gt;")

	return string



def generate_password():
	"Generates a random password"

	def get_random_item(list):
		return list[int(random.random() * len(list))]


	pwlen = revelation.data.config_get("passwordgen/length")

	# set up list of chars to exclude
	exclude = []
	if revelation.data.config_get("passwordgen/avoid_ambiguous") == gtk.TRUE:
		exclude = [ "0", "O", "I", "l", "1", "S", "5", "q", "g" ]


	# calculate the minimum share of the password for each character class
	sharedigits = int(round(pwlen * 0.15))
	sharechars = int(round(pwlen * 0.24))
	sharecaps = int(round(pwlen * 0.24))

	# set up a set of all usable ascii characters
	digits = range(48, 58)
	chars = range(65, 91)
	caps = range(97, 123)

	full = []
	full.extend(digits)
	full.extend(chars)
	full.extend(caps)


	# generate characters for the password
	pwchars = []
	while len(pwchars) < pwlen:

		# get digits
		if len(pwchars) < sharedigits:
			char = chr(get_random_item(digits))

		# get chars
		elif len(pwchars) < sharechars + sharedigits:
			char = chr(get_random_item(chars))

		# get caps
		elif len(pwchars) < sharecaps + sharechars + sharedigits:
			char = chr(get_random_item(caps))

		# get random characters
		else:
			char = chr(get_random_item(full))


		if char not in exclude:
			pwchars.append(char)


	# shuffle the password
	password = ""
	for i in range(len(pwchars)):
		password += pwchars.pop(int(random.random() * len(pwchars)))

	return password



def timediff_simple(start, end = None):
	"Returns an approximate time difference in human-readable format"

	if end is None:
		end = time.time()

	if end < start:
		return None

	diff = int(end - start)

	gmstart = time.gmtime(start)
	gmend = time.gmtime(end)

	# get a human-readable time period
	if diff >= int(365.25 * 24 * 60 * 60):
		period = int(diff / 365.25 / 24 / 60 / 60)
		unit = "year"

	elif gmend.tm_mon - gmstart.tm_mon >= 2 or (gmend.tm_mon - gmstart.tm_mon == 1 and gmend.tm_mday >= gmstart.tm_mday):
		period = gmend.tm_mon - gmstart.tm_mon
		unit = "month"

	elif diff >= 7 * 24 * 60 * 60:
		period = diff / 7 / 24 / 60 / 60
		unit = "week"

	elif diff >= 24 * 60 * 60:
		period = diff / 24 / 60 / 60
		unit = "day"

	elif diff >= 60 * 60:
		period = diff / 60 / 60
		unit = "hour"

	elif diff >= 60:
		period = diff / 60
		unit = "minute"

	else:
		period = diff
		unit = "second"


	if period == 1:
		return str(period) + " " + unit

	else:
		return str(period) + " " + unit + "s"

