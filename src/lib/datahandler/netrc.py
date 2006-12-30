#
# Revelation 0.4.8 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling .netrc files
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

import base
from revelation import data, entry

import shlex, StringIO, time


class NetRC(base.DataHandler):
	"Data handler for .netrc data"

	name		= "netrc"
	importer	= True
	exporter	= True
	encryption	= False


	def export_data(self, entrystore, password = None):
		"Converts data from an entrystore to netrc data"

		netrc = ""
		iter = entrystore.iter_nth_child(None, 0)

		while iter is not None:
			e = entrystore.get_entry(iter)

			try:
				if "" in ( e[entry.HostnameField], e[entry.UsernameField], e[entry.PasswordField] ):
					raise ValueError

				if e.name != "":
					netrc += "# %s\n" % e.name

				if e.description != "":
					netrc += "# %s\n" % e.description

				netrc += "machine %s\n" % e[entry.HostnameField]
				netrc += "	login %s\n" % e[entry.UsernameField]
				netrc += "	password %s\n" % e[entry.PasswordField]
				netrc += "\n"

			except ( entry.EntryFieldError, ValueError ):
				pass

			iter = entrystore.iter_traverse_next(iter)

		return netrc


	def import_data(self, netrc, password = None):
		"Imports data from a netrc stream to an entrystore"

		entrystore = data.EntryStore()

		# set up a lexical parser
		datafp = StringIO.StringIO(netrc)
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
			e = entry.GenericEntry()
			e.name = name
			e.updated = time.time()

			if name != "default":
				e[entry.HostnameField] = name

			while 1:
				tt = lexer.get_token()

				# if we find a new entry, break out of current field-collecting loop
				if tt == "" or tt == "machine" or tt == "default" or tt == "macdef":
					entrystore.add_entry(e)
					lexer.push_token(tt)
					break

				elif tt == "login" or tt == "user":
					e[entry.UsernameField] = lexer.get_token()

				elif tt == "account":
					lexer.get_token()

				elif tt == "password":
					e[entry.PasswordField] = lexer.get_token()

				else:
					raise base.FormatError

		datafp.close()

		return entrystore

