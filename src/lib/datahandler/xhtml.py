#
# Revelation 0.3.2 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for exporting to XHTML files
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
import gtk, time


class XHTML(base.DataHandler):
	"Data handler for XHTML export"

	name		= "XHTML / CSS"
	importer	= gtk.FALSE
	exporter	= gtk.TRUE
	encryption	= gtk.FALSE


	def __init__(self):
		base.DataHandler.__init__(self)

		self.imagepath = "http://oss.codepoet.no/revelation/img/fileicons/"


	def __generate_css(self):
		"Generates a CSS for the XHTML document"

		css = """
		/* containers */
		body {
			margin: 20px 10px;
			padding: 0px;

			font-family: sans-serif;
			font-size: 10pt;
			line-height: 1.3;

			color: #333333;
			background-color: #ffffff;
		}

		div {
			display: block;
			clear: none;
			margin: 0px;
			padding: 0px;
		}

		p {
			display: block;
			width: auto;
			margin: 0px 0px 5px 0px;
			padding: 0px;
		}

		table, tr, td, th {
			width: auto;
			font-family: sans-serif;
			font-size: 10pt;
			line-height: 1.4;

			color: #333333;
			background-color: transparent;
		}

		table {
			margin: 0px 0px;
			border-collapse: collapse;
		}

		td, th {
			text-align: left;
			vertical-align: middle;
		}

		th {
			font-weight: bold;
			color: #000000;
		}



		/* headings */
		h1, h2, h3 {
			margin: 0px;
			padding: 0px;
			line-height: 1;
			font-weight: bold;
			color: #000000;
		}

		h1 {
			margin-bottom: 10px;
			font-size: 16pt;
		}

		h2 {
			margin-bottom: 5px;
			font-size: 14pt;
		}

		h3 {
			font-size: 10pt;
		}



		/* content */
		a {
			color: #3333cc;
			text-decoration: none;
		}

		a:hover {
			text-decoration: underline;
		}

		strong {
			color: #000000;
			font-weight: bold;
		}



		/* classes */
		li.account {
			display: block;
			width: 350px;
			border: 1px solid #3366cc;
			margin: 0px 0px 10px 0px;
		}

		li.account .data {
			padding: 5px;
		}

		li.account .description {
			margin: 0px;
		}

		li.account .fields {
			margin: 0px 0px 3px 0px;
		}

		li.account .fields td {
			padding: 1px 2px 1px 0px;
		}

		li.account .fields th {
			padding: 1px 5px 1px 0px;
		}

		li.account .heading {
			padding: 2px 5px;
			background-color: #e5ecf9;
			border-bottom: 1px solid #3366cc;
		}

		li.account .heading h2 {
			margin: 0px 0px 1px 0px;
			padding: 0px;
		}

		li.account .heading img {
			float: right;
			width: 24px;
			height: 24px;
		}

		li.account .heading .type {
			color: #000000;
			font-weight: bold;
		}

		li.account .updated {
			font-size: 8pt;
			text-align: right;
			margin: 0px;
		}



		li.folder {
			display: block;
			width: 100%;
		}

		li.folder .folder-data {
			background-color: #e5ecf9;
			border-top: 1px solid #3366cc;
			border-bottom: 1px solid #3366cc;
			margin: 0px 0px 10px 0px;
			padding: 2px 5px;
		}

		li.folder .folder-data h2 {
			margin: 0px;
			padding: 0px;
		}

		li.folder .folder-data p {
			margin: 0px;
			padding: 0px;
		}



		/* the content area */
		#content {
			margin-right: 220px;
		}



		/* the sidebar */
		#sidebar {
			width: 200px;
			float: right;
		}

		#sidebar h2 {
			margin: 10px 0px 10px 0px;
			padding: 0px 5px 5px 5px;
			border-bottom: 1px dashed #3366cc;
		}

		#sidebar ul {
			list-style: none;
			padding: 0px;
			margin: 5px 5px 10px 10px;
		}


		/* the entrylist */
		#entrylist {
			list-style: none;
			padding: 0px;
			margin: 0px;
		}

		#entrylist li {
			list-style: none;
		}
"""

		return css


	def __generate_entry(self, entrystore, iter, depth = 0):
		"Generates xhtml for an entry"

		tabs = "\t" * (depth + 2)
		entry = entrystore.get_entry(iter)

		xhtml = ""

		if type(entry) == revelation.entry.FolderEntry:
			xhtml += tabs + "<li class=\"folder\">\n"
			xhtml += tabs + "	<div class=\"folder-data\">\n"
			xhtml += tabs + "		<h2>" + entry.name + "</h2>\n"

			if entry.description != "":
				xhtml += tabs + "		<p class=\"description\">" + entry.description + "</p>\n"

			xhtml += tabs + "	</div>\n"
			xhtml += tabs + "\n"
			xhtml += tabs + "	<ul>\n"

			for i in range(entrystore.iter_n_children(iter)):
				child = entrystore.iter_nth_child(iter, i)
				xhtml += self.__generate_entry(entrystore, child, depth + 1)

			xhtml += tabs + "	</ul>\n"
			xhtml += tabs + "</li>\n"
			xhtml += tabs + "\n"


		else:
			xhtml += tabs + "<li class=\"account\">\n"
			xhtml += tabs + "	<div class=\"heading\">\n"
			xhtml += tabs + "		<img src=\"" + self.imagepath + "/account-" + entry.id + ".png\" alt=\"" + entry.typename + "\" />\n"
			xhtml += tabs + "		<h2>" + entry.name + "</h2>\n"
			xhtml += tabs + "		<p class=\"description\">\n"
			xhtml += tabs + "			<span class=\"type\">" + entry.typename

			if entry.description != "":
				xhtml += ";</span> " + entry.description + "\n"

			else:
				xhtml += "</span>\n"

			xhtml += tabs + "		</p>\n"
			xhtml += tabs + "	</div>\n"
			xhtml += tabs + "\n"

			xhtml += tabs + "	<div class=\"data\">\n"
			xhtml += tabs + "		<table class=\"fields\">\n"

			for field in entry.fields:
				if field.value == "":
					continue

				xhtml += tabs + "			<tr>\n"
				xhtml += tabs + "				<th>" + field.name + ":</th>\n"
				xhtml += tabs + "				<td>" + field.value + "</td>\n"
				xhtml += tabs + "			</tr>\n"

			xhtml += tabs + "		</table>\n"
			xhtml += tabs + "		<p class=\"updated\">Updated " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.updated)) + "</p>\n"
			xhtml += tabs + "	</div>\n"
			xhtml += tabs + "</li>\n"

		return xhtml


	def __generate_entrylist(self, entrystore):
		"Generates xhtml for an entrystore"

		xhtml = ""
		xhtml += "<div id=\"content\">\n"
		xhtml += "	<ul id=\"entrylist\">\n"

		for i in range(entrystore.iter_n_children(None)):
			iter = entrystore.iter_nth_child(None, i)
			xhtml += self.__generate_entry(entrystore, iter)

		xhtml += "	</ul>\n"
		xhtml += "</div>\n"

		return xhtml


	def __generate_footer(self):
		"Generates an xhtml footer"

		xhtml = ""
		xhtml += "</body>\n"
		xhtml += "</html>\n"

		return xhtml


	def __generate_header(self):
		"Generates an xhtml header"

		xhtml = ""
		xhtml += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">\n"
		xhtml += "<html xmlns=\"http://www.w3.org/1999/xhtml\">\n"
		xhtml += "<head>\n"
		xhtml += "	<title>Revelation account list</title>\n"
		xhtml += "	<meta http-equiv=\"Content-Type\" content=\"text/html; charset=ISO-8859-1\" />\n"
		xhtml += "\n"
		xhtml += "	<style type=\"text/css\">\n"
		xhtml += self.__generate_css()
		xhtml += "	</style>\n"
		xhtml += "</head>\n"
		xhtml += "\n"
		xhtml += "<body>\n"
		xhtml += "<h1>Revelation account list</h1>\n"
		xhtml += "\n"

		return xhtml


	def __generate_sidebar(self, entrystore):
		"Generates a sidebar"

		# find the entries
		index = 0
		iter = None
		entries = {}

		while 1:
			iter = entrystore.iter_traverse_next(iter)

			if iter is None:
				break

			entry = entrystore.get_entry(iter)

			if type(entry) == revelation.entry.FolderEntry:
				pass

			else:
				entry = entry.copy()
				entry.index = index

				if not entries.has_key(type(entry)):
					entries[type(entry)] = []

				entries[type(entry)].append(entry)

			index += 1


		# generate the xhtml
		xhtml = ""
		xhtml += "<div id=\"sidebar\">\n"
		xhtml += "	<h2 style=\"margin-top: 0px;\">File info</h2>\n"
		xhtml += "\n"
		xhtml += "	<p>\n"
		xhtml += "		<strong>Created:</strong><br />\n"
		xhtml += "		" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n"
		xhtml +="	</p>\n"
		xhtml += "\n"
		xhtml += "	<h2>Account list</h2>\n"
		xhtml += "\n"

		for entrytype in revelation.entry.get_entry_list():
			if not entries.has_key(entrytype):
				continue

			xhtml += "	<h3>" + entrytype.typename + ":</h3>\n"
			xhtml += "\n"
			xhtml += "	<ul class=\"accountlist\">\n"

			entrylist = entries[entrytype]
			entrylist.sort(lambda x,y: cmp(x.name.lower(), y.name.lower()))

			for entry in entrylist:
				xhtml += "		<li><a href=\"#" + str(entry.index) + "\">" + entry.name + "</a></li>\n"

			xhtml += "	</ul>\n"
			xhtml += "\n"

		xhtml += "</div>\n"
		xhtml += "\n"

		return xhtml


	def export_data(self, entrystore, password = None):
		"Exports data from an entrystore into a XHTML document"

		xhtml = ""
		xhtml += self.__generate_header()
		xhtml += self.__generate_sidebar(entrystore)
		xhtml += self.__generate_entrylist(entrystore)
		xhtml += self.__generate_footer()

		return xhtml

