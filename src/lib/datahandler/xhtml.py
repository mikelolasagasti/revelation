#
# Revelation 0.4.2 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for exporting to XHTML files
#
#
# Copyright (c) 2003-2005 Erik Grinaker
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
from revelation import config, data, entry

import time


IMAGEPATH	= "http://oss.codepoet.no/revelation/img/fileicons"


class XHTML(base.DataHandler):
	"Data handler for XHTML export"

	name		= "XHTML / CSS"
	importer	= False
	exporter	= True
	encryption	= False


	def __init__(self):
		base.DataHandler.__init__(self)


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
			margin: 0px;
			padding: 0px;
		}

		p {
			margin: 0px 0px 5px 0px;
			padding: 0px;
		}

		table {
			font-family: sans-serif;
			font-size: 10pt;
			line-height: 1.3;

			margin: 0px;
			border-collapse: collapse;

			color: #333333;
			background-color: transparent;
		}

		td {
			text-align: left;
			vertical-align: top;
		}

		th {
			text-align: left;
			vertical-align: top;

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
			margin-bottom: 20px;
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

		img {
			margin: 0px;
			padding: 0px;
			border: none;
		}

		strong {
			color: #000000;
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
			margin: 20px 0px 10px 0px;
			padding: 0px 0px 5px 0px;
			border-bottom: 1px dashed #3366cc;
			text-transform: lowercase;
		}

		#sidebar h2 img.icon {
			width: 24px;
			height: 24px;
			margin-right: 5px;
			vertical-align: middle;
		}

		#sidebar h3 {
			margin-bottom: 2px;
			text-transform: lowercase;
		}

		#sidebar p {
			margin: 0px 5px 10px 15px;
		}

		#sidebar ul {
			list-style: none;
			padding: 0px;
			margin: 0px 0px 10px 0px;
		}

		#sidebar ul ul {
			margin: 0px 0px 0px 15px;
		}

		#sidebar ul.accountlist {
			margin-left: 15px;
		}



		/* the entrylist */
		#entrylist {
			width: 99%;
			padding: 0px;
			margin: 0px;
		}



		/* the footer */
		#footer {
			margin: 50px 220px 10px 0px;
			font-size: 8pt;
			text-align: center;
			color: #aaaaaa;
		}

		#footer a {
			color: #8888ee;
		}



		/* folders */
		li.folder {
			width: 100%;
			list-style-type: none;
		}

		li.folder .folder-data {
			margin: 0px 0px 10px 0px;
			padding: 2px 5px 3px 5px;

			border: 1px solid #3366cc;
			background-color: #e5ecf9;
		}

		li.folder .folder-data h2 {
			margin: 0px;
		}

		li.folder .folder-data p {
			margin: 0px;
		}



		/* accounts  */
		li.account {
			list-style-type: none;
			width: 350px;
			margin: 0px 0px 10px 0px;
			border: 1px solid #3366cc;
		}

		li.account .heading {
			padding: 2px 5px;
			background-color: #e5ecf9;
			border-bottom: 1px solid #3366cc;
		}

		li.account .heading h2 {
			margin: 0px 0px 1px 0px;
		}

		li.account .heading img {
			float: right;
			width: 24px;
			height: 24px;
		}

		li.account .heading .description {
			margin: 0px;
		}

		li.account .heading .type {
			color: #000000;
			font-weight: bold;
		}

		li.account .data {
			padding: 5px;
		}

		li.account .data .fields {
			margin: 0px 0px 3px 0px;
		}

		li.account .data .fields td {
			padding: 1px 0px;
		}

		li.account .data .fields th {
			padding: 1px 5px 1px 0px;
		}

		li.account .updated {
			font-size: 8pt;
			text-align: right;
			margin: 0px;
		}
"""

		return css


	def __generate_entry(self, entrystore, iter, depth = 0):
		"Generates xhtml for an entry"

		tabs = "\t" * (depth + 2)
		e = entrystore.get_entry(iter)

		if e is not None:
			e.path = self.__get_entryid(entrystore, iter)


		xhtml = ""

		if e is None:

			xhtml += "<div id=\"content\">\n"
			xhtml += "	<ul id=\"entrylist\">\n"

			for i in range(entrystore.iter_n_children(iter)):
				child = entrystore.iter_nth_child(iter, i)
				xhtml += self.__generate_entry(entrystore, child, depth)

			xhtml += "	</ul>\n"
			xhtml += "</div>\n"


		elif type(e) == entry.FolderEntry:
			xhtml += tabs + "<li class=\"folder\" id=\"%s\">\n" % e.path
			xhtml += tabs + "	<div class=\"folder-data\">\n"
			xhtml += tabs + "		<h2>%s</h2>\n" % e.name

			if e.description != "":
				xhtml += tabs + "		<p class=\"description\">%s</p>\n" % e.description

			xhtml += tabs + "	</div>\n"
			xhtml += tabs + "\n"
			xhtml += tabs + "	<ul>\n"

			for i in range(entrystore.iter_n_children(iter)):
				child = entrystore.iter_nth_child(iter, i)
				xhtml += self.__generate_entry(entrystore, child, depth + 2)

			xhtml += tabs + "	</ul>\n"
			xhtml += tabs + "</li>\n"
			xhtml += tabs + "\n"


		else:

			xhtml += tabs + "<li class=\"account\" id=\"%s\">\n" % e.path
			xhtml += tabs + "	<div class=\"heading\">\n"
			xhtml += tabs + "		<img src=\"%s/entry/%s.png\" alt=\"%s\" />\n" % ( IMAGEPATH, e.id, e.typename )
			xhtml += tabs + "		<h2>%s</h2>\n" % e.name
			xhtml += tabs + "		<p class=\"description\"><span class=\"type\">%s</span>%s</p>\n" % ( e.typename + (e.description != "" and "; " or ""), e.description )
			xhtml += tabs + "	</div>\n"
			xhtml += tabs + "\n"

			xhtml += tabs + "	<div class=\"data\">\n"

			fields = []
			for field in e.fields:
				if field.value != "":
					fields.append(field)

			if len(fields) > 0:
				xhtml += tabs + "		<table class=\"fields\">\n"

				for field in fields:
					xhtml += tabs + "			<tr>\n"
					xhtml += tabs + "				<th>" + field.name + ":</th>\n"
					xhtml += tabs + "				<td>" + field.value + "</td>\n"
					xhtml += tabs + "			</tr>\n"

				xhtml += tabs + "		</table>\n"

			xhtml += tabs + "		<p class=\"updated\">Updated " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.updated)) + "</p>\n"
			xhtml += tabs + "	</div>\n"
			xhtml += tabs + "</li>\n"
			xhtml += tabs + "\n"

		return xhtml


	def __generate_footer(self):
		"Generates an xhtml footer"

		xhtml = ""
		xhtml += "<div id=\"footer\">\n"
		xhtml += "	Generated by <a href=\"%s\">%s %s</a>" % ( config.URL, config.APPNAME, config.VERSION )
		xhtml += "</div>\n"
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

		xhtml = ""
		xhtml += "<div id=\"sidebar\">\n"
		xhtml += self.__generate_sidebar_fileinfo()
		xhtml += self.__generate_sidebar_foldertree(entrystore)
		xhtml += self.__generate_sidebar_accountlist(entrystore)
		xhtml += "</div>\n"

		return xhtml


	def __generate_sidebar_accountlist(self, entrystore):
		"Generates an account list"

		# find the entries
		entries = {}
		iter = entrystore.iter_nth_child(None, 0)

		while iter is not None:
			e = entrystore.get_entry(iter)
			e.path = self.__get_entryid(entrystore, iter)

			if type(e) != entry.FolderEntry:
				if not entries.has_key(type(e)):
					entries[type(e)] = []

				entries[type(e)].append(e)

			iter = entrystore.iter_traverse_next(iter)


		# generate the xhtml
		xhtml = ""
		xhtml += "	<h2><img src=\"%s/sidebar/accountlist.png\" class=\"icon\" alt=\"Account list\" />Account list</h2>\n" % IMAGEPATH
		xhtml += "\n"

		for entrytype in entry.ENTRYLIST:
			if not entries.has_key(entrytype):
				continue

			xhtml += "	<h3>%s:</h3>\n" % entrytype.typename
			xhtml += "\n"
			xhtml += "	<ul class=\"accountlist\">\n"

			entrylist = entries[entrytype]
			entrylist.sort(lambda x,y: cmp(x.name.lower(), y.name.lower()))

			for e in entrylist:
				xhtml += "		<li><a href=\"#%s\">%s</a></li>\n" % ( str(e.path), e.name )

			xhtml += "	</ul>\n"
			xhtml += "\n"

		return xhtml


	def __generate_sidebar_fileinfo(self):
		"Generates file info for the sidebar"

		xhtml = ""
		xhtml += "	<h2 style=\"margin-top: 0px;\"><img src=\"%s/sidebar/file.png\" class=\"icon\" alt=\"File info\" />File info</h2>\n" % IMAGEPATH
		xhtml += "\n"
		xhtml += "	<h3>Created:</h3>\n"
		xhtml += "	<p>%s</p>\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		xhtml += "\n"
		xhtml += "	<h3>Revelation version:</h3>\n"
		xhtml += "	<p>%s</p>\n" % config.VERSION
		xhtml += "\n"

		return xhtml


	def __generate_sidebar_foldertree(self, entrystore, parent = None, depth = 0):
		"Generates a folder tree for the sidebar"

		tabs = "\t" * ((depth * 2) - 2)
		xhtml = ""

		if parent is None:
			xhtml += "	<h2><img src=\"%s/sidebar/foldertree.png\" class=\"icon\" alt=\"Folder tree\" />Folder tree</h2>\n" % IMAGEPATH
			xhtml += "\n"

		# fetch folder list
		folders = []
		for i in range(entrystore.iter_n_children(parent)):
			iter = entrystore.iter_nth_child(parent, i)
			e = entrystore.get_entry(iter)
			e.path = self.__get_entryid(entrystore, iter)
			e.iter = iter

			if type(e) == entry.FolderEntry:
				folders.append(e)


		# generate xhtml
		if len(folders) > 0:
			xhtml += tabs + "<ul>\n"

			for e in folders:
				childxhtml = self.__generate_sidebar_foldertree(entrystore, e.iter, depth + 1)

				if childxhtml != "":
					xhtml += tabs + "	<li>\n"
					xhtml += tabs + "		<a href=\"#%s\">%s</a>\n" % ( str(e.path), e.name )
					xhtml += childxhtml
					xhtml += tabs + "	</li>\n"

				else:
					xhtml += tabs + "	<li><a href=\"#%s\">%s</a></li>\n" % ( str(e.path), e.name )

			xhtml += tabs + "</ul>\n"


		return xhtml


	def __get_entryid(self, entrystore, iter):
		"Returns an entry id for an iter"

		path = "entry-"

		for i in entrystore.get_path(iter):
			path += str(i) + "-"

		path = path[:-1]

		return path


	def export_data(self, entrystore, password = None):
		"Exports data from an entrystore into a XHTML document"

		xhtml = ""
		xhtml += self.__generate_header()
		xhtml += self.__generate_sidebar(entrystore)
		xhtml += self.__generate_entry(entrystore, None)
		xhtml += self.__generate_footer()

		return xhtml

