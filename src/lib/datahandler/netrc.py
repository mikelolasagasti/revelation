#
# Revelation 0.3.0 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling .netrc files
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


import revelation, base, StringIO, shlex, time


class NetRC(base.Handler):

	def __init__(self):
		base.Handler.__init__(self)


	def export_data(self, entrystore):

		iter = None
		data = ""

		while 1:
			iter = entrystore.iter_traverse_next(iter)

			if iter is None:
				break

			entry = entrystore.get_entry(iter)

			if not entry.has_field(revelation.entry.FIELD_GENERIC_HOSTNAME) or not entry.has_field(revelation.entry.FIELD_GENERIC_USERNAME) or not entry.has_field(revelation.entry.FIELD_GENERIC_PASSWORD):
				continue

			hostname = entry.get_field(revelation.entry.FIELD_GENERIC_HOSTNAME).value
			username = entry.get_field(revelation.entry.FIELD_GENERIC_USERNAME).value
			password = entry.get_field(revelation.entry.FIELD_GENERIC_PASSWORD).value

			if hostname == "" or username == "" or password == "":
				continue

			if entry.name != "":
				data += "# " + entry.name + "\n"

			if entry.description != "":
				data += "# " + entry.description + "\n"

			data += "machine " + hostname + "\n"
			data += "	login " + username + "\n"
			data += "	password " + password + "\n"
			data += "\n"

		return data


	def import_data(self, entrystore, data):
		datafp = StringIO.StringIO(data)
		lexer = shlex.shlex(datafp)
		lexer.wordchars += r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

		while 1:
			# look for a machine, default or macdef top-level keyword
			tt = lexer.get_token()

			if not tt:
				break

			elif tt == "machine":
				name = lexer.get_token()
	
			elif tt == "default":
				name = "default"

			elif tt == "macdef":
				lexer.whitespace = ' \t'

				while 1:
					line = lexer.instream.readline()
					if not line or line == '\012':
						lexer.whitespace = ' \t\r\n'
						break
				continue

			else:
				print "invtoken1", tt
				raise base.FormatError


			# we're looking at an entry, so fetch data
			entry = revelation.entry.Entry(revelation.entry.ENTRY_ACCOUNT_GENERIC)
			entry.name = name
			entry.updated = time.time()

			if name != "default":
				entry.set_field(revelation.entry.FIELD_GENERIC_HOSTNAME, name)

			while 1:
				tt = lexer.get_token()
				if tt == "" or tt == "machine" or tt == "default" or tt == "macdef":
					entrystore.add_entry(None, entry)
					lexer.push_token(tt)
					break

				elif tt == "login" or tt == "user":
					entry.set_field(revelation.entry.FIELD_GENERIC_USERNAME, lexer.get_token())

				elif tt == "account":
					lexer.get_token()

				elif tt == "password":
					entry.set_field(revelation.entry.FIELD_GENERIC_PASSWORD, lexer.get_token())

				else:
					print "invtoken2", tt
					raise FormatError

		datafp.close()

