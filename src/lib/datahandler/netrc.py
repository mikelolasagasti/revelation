#
# Revelation 0.3.2 - a password manager for GNOME 2
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

import revelation, base
import StringIO, shlex, time, gtk


class NetRC(base.DataHandler):
	"Data handler for .netrc data"

	name		= ".netrc"
	importer	= gtk.TRUE
	exporter	= gtk.TRUE
	encryption	= gtk.FALSE


	def export_data(self, entrystore):
		"Converts data from an entrystore into a data stream"

		data = ""
		iter = entrystore.iter_nth_child(None, 0)

		while iter is not None:

			entry = entrystore.get_entry(iter)

			# only export entries which have a hostname, username and password
			if not entry.has_field(revelation.entry.HostnameField) or not entry.has_field(revelation.entry.UsernameField) or not entry.has_field(revelation.entry.PasswordField):
				iter = entrystore.iter_traverse_next(iter)
				continue

			hostname = entry.get_field(revelation.entry.HostnameField).value
			username = entry.get_field(revelation.entry.UsernameField).value
			password = entry.get_field(revelation.entry.PasswordField).value

			if hostname == "" or username == "" or password == "":
				iter = entrystore.iter_traverse_next(iter)
				continue


			# add name and description as comments, if any
			if entry.name != "":
				data += "# " + entry.name + "\n"

			if entry.description != "":
				data += "# " + entry.description + "\n"


			# export the entry itself
			data += "machine " + hostname + "\n"
			data += "	login " + username + "\n"
			data += "	password " + password + "\n"
			data += "\n"

			iter = entrystore.iter_traverse_next(iter)

		return data


	def import_data(self, data):
		"Imports data from a data stream into an entrystore"

		entrystore = revelation.data.EntryStore()

		# set up a lexical parser
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

			# skip macdef entries
			elif tt == "macdef":
				lexer.whitespace = ' \t'

				while 1:
					line = lexer.instream.readline()

					if not line or line == '\012':
						lexer.whitespace = ' \t\r\n'
						break
				continue

			else:
				raise base.FormatError


			# we're looking at an entry, so fetch data
			entry = revelation.entry.GenericEntry()
			entry.name = name
			entry.updated = time.time()

			if name != "default":
				entry.get_field(revelation.entry.HostnameField).value = name

			while 1:
				tt = lexer.get_token()

				# if we find a new entry, break out of current field-collecting loop
				if tt == "" or tt == "machine" or tt == "default" or tt == "macdef":
					entrystore.add_entry(None, entry)
					lexer.push_token(tt)
					break

				elif tt == "login" or tt == "user":
					entry.get_field(revelation.entry.UsernameField).value = lexer.get_token()

				elif tt == "account":
					lexer.get_token()

				elif tt == "password":
					entry.get_field(revelation.entry.PasswordField).value = lexer.get_token()

				else:
					raise base.FormatError

		datafp.close()

		return entrystore

