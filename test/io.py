#!/usr/bin/env python

#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for IO module
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

import unittest, os, time

from revelation import data, datahandler, io



class DataFile__init(unittest.TestCase):
	"DataFile()"

	def test_default_file(self):
		"DataFile() file defaults to None"

		f = io.DataFile()
		self.assertEqual(f.get_file(), None)


	def test_default_handler(self):
		"DataFile() handler defaults to datahandler.Revelation"

		f = io.DataFile()
		self.assertEqual(type(f.get_handler()), datahandler.Revelation)


	def test_default_password(self):
		"DataFile() password defaults to None"

		f = io.DataFile()
		self.assertEqual(f.get_password(), None)


	def test_handler(self):
		"DataFile() handles handler arg correctly"

		f = io.DataFile(datahandler.Revelation)
		self.assertEqual(type(f.get_handler()), datahandler.Revelation)


	def test_noargs(self):
		"DataFile() with no args"

		io.DataFile()



class DataFile__str(unittest.TestCase):
	"DataFile.__str__()"


	def test_get_file(self):
		"DataFile.__str__() gives same results as DataFile.get_file()"

		files = [
			"/bin/ls",
			"file:///bin/ls",
			"file:///home/../bin/ls",
			"http://www.google.com/index.html",
			"ftp://test:test123@ftp.testftp.com/test/123"
		]

		for file in files:
			f = io.DataFile()
			f.set_file(file)
			self.assertEqual(str(f), f.get_file())


	def test_none(self):
		"DataFile.__str__() with no file returns ''"

		f = io.DataFile()
		self.assertEqual(str(f), "")



class DataFile_close(unittest.TestCase):
	"DataFile.close()"

	def test_file(self):
		"DataFile.close() resets file uri"

		f = io.DataFile()
		f.set_file("/bin/ls")
		f.close()
		self.assertEqual(f.get_file(), None)


	def test_handler(self):
		"DataFile.close() doesn't reset handler"

		f = io.DataFile()
		f.set_handler(datahandler.Revelation)
		f.close()
		self.assertEqual(type(f.get_handler()), datahandler.Revelation)


	def test_password(self):
		"DataFile.close() resets password"

		f = io.DataFile()
		f.set_password("test123")
		f.close()
		self.assertEqual(f.get_password(), None)



class DataFile_get_file(unittest.TestCase):
	"DataFile.get_file()"

	def test_normpath(self):
		"DataFile.get_file() uses file_normpath()"

		tests = (
			( None					, None ),
			( "/bin/ls"				, "/bin/ls" ),
			( "/home/../bin/ls"			, "/bin/ls" ),
			( "http://www.google.com/index.html"	, "http://www.google.com/index.html" ),
			( "../../../../../../../../../../home/../bin/ls", "/bin/ls"),
			( "file:///bin/ls"			, "/bin/ls" ),
			( "file:../../../../../../../../../../home/../bin/ls", "/bin/ls")
		)

		for input, output in tests:
			self.assertEqual(output, io.file_normpath(input))



class DataFile_get_password(unittest.TestCase):
	"Datafile.get_password()"

	def test_none(self):
		"DataFile.get_password() returns None on no password"

		f = io.DataFile()
		f.set_password(None)
		self.assertEqual(f.get_password(), None)


	def test_password(self):
		"DataFile.get_password() gets password"

		f = io.DataFile()
		f.set_password("test123")
		self.assertEqual(f.get_password(), "test123")



class DataFile_get_handler(unittest.TestCase):
	"DataFile.get_handler()"

	def test_none(self):
		"DataFile.get_handler() returns None when no handler is set"

		f = io.DataFile(None)
		self.assertEqual(f.get_handler(), None)


	def test_normal(self):
		"DataFile.get_handler() returns the handler"

		f = io.DataFile(datahandler.Revelation)
		self.assertEqual(type(f.get_handler()), datahandler.Revelation)



class DataFile_load(unittest.TestCase):
	"DataFile.load()"

	def test_file(self):
		"DataFile.load() updates file property"

		xml = 	"<?xml version=\"1.0\" ?>" 		\
			"<revelationdata dataversion=\"1\">"	\
			"</revelationdata>"

		io.file_write("/tmp/iotest-xmldata", xml)

		f = io.DataFile(datahandler.RevelationXML)
		entrystore = f.load("/tmp/iotest-xmldata")
		self.assertEqual(f.get_file(), "/tmp/iotest-xmldata")


	def test_load(self):
		"DataFile.load() returns an EntryStore on success"

		xml = 	"<?xml version=\"1.0\" ?>" 		\
			"<revelationdata dataversion=\"1\">"	\
			"</revelationdata>"

		io.file_write("/tmp/iotest-xmldata", xml)

		f = io.DataFile(datahandler.RevelationXML)
		entrystore = f.load("/tmp/iotest-xmldata")
		self.assertEqual(type(entrystore), data.EntryStore)


	def test_none(self):
		"DataFile.load() raises IOError when passed None"

		self.assertRaises(IOError, io.DataFile().load, None)


	def test_pwgetter(self):
		"DataFile.load() calls pwgetter() when password isn't passed"

		global pwflag
		pwflag = False

		def pwgetter():
			global pwflag
			pwflag = True
			return "dummy"

		handler = datahandler.Revelation()
		encdata = handler.export_data(data.EntryStore(), "jeje")

		io.file_write("/tmp/iotest-testfile", encdata)

		try:
			f = io.DataFile(datahandler.Revelation)
			f.load("/tmp/iotest-testfile", None, pwgetter)

		except datahandler.PasswordError:
			pass

		self.assertEqual(pwflag, True)



class DataFile_set_file(unittest.TestCase):
	"DataFile.set_file()"

	def test_file(self):
		"DataFile.set_file() sets the file"

		f = io.DataFile()
		f.set_file("/bin/ls")
		self.assertEqual(f.get_file(), "/bin/ls")


	def test_none(self):
		"DataFile.set_file() handles None correctly"

		f = io.DataFile()
		f.set_file("/bin/ls")
		f.set_file(None)
		self.assertEqual(f.get_file(), None)



class DataFile_set_handler(unittest.TestCase):
	"DataFile.set_handler()"

	def test_handler(self):
		"DataFile.set_handler() sets handler correctly"

		f = io.DataFile(None)
		f.set_handler(datahandler.Revelation)
		self.assertEqual(type(f.get_handler()), datahandler.Revelation)

	def test_init(self):
		"DataFile.set_handler() works like init"

		for handler in ( datahandler.Revelation, None ):
			a = io.DataFile(handler)
			b = io.DataFile(None)
			b.set_handler(handler)

			self.assertEqual(type(a.get_handler()), type(b.get_handler()))


	def test_none(self):
		"DataFile.set_handler() handles None correctly"

		f = io.DataFile(datahandler.Revelation)
		f.set_handler(None)
		self.assertEqual(f.get_handler(), None)



class DataFile_set_password(unittest.TestCase):
	"Datafile.set_password()"

	def test_none(self):
		"DataFile.set_password() handles None correctly"

		f = io.DataFile()
		f.set_password(None)
		self.assertEqual(f.get_password(), None)


	def test_password(self):
		"DataFile.set_password() sets password"

		f = io.DataFile()
		f.set_password("test123")
		self.assertEqual(f.get_password(), "test123")



class file_exists(unittest.TestCase):
	"file_exists()"

	def test_local(self):
		"file_exists() with local file"

		self.assertEqual(io.file_exists("/bin/ls"), True)


	def test_none(self):
		"file_exists() passed None"

		self.assertEqual(io.file_exists(None), False)


	def test_nonexist(self):
		"file_exists() with non-existant file"

		self.assertEqual(io.file_exists("/fjkdlsafjø8942389"), False)


	def test_remote(self):
		"file_exists() with remote file"

		self.assertEqual(io.file_exists("http://www.google.com/index.html"), True)



class file_normpath(unittest.TestCase):
	"file_normpath()"

	def test_empty(self):
		"file_normpath handles ''"

		self.assertEqual(io.file_normpath(""), None)

	def test_local(self):
		"file_normpath handles local files"

		self.assertEqual(io.file_normpath("/bin/ls"), "/bin/ls")


	def test_none(self):
		"file_normpath returns None when no file"

		self.assertEqual(io.file_normpath(None), None)


	def test_normalize(self):
		"file_normpath normalizes paths"

		self.assertEqual(io.file_normpath("/home/../bin/ls"), "/bin/ls")


	def test_remote(self):	
		"file_normpath works for remote files"

		self.assertEqual(io.file_normpath("http://www.google.com/index.html"), "http://www.google.com/index.html")


	def test_resolve(self):
		"file_normpath resolves relative paths"

		self.assertEqual(io.file_normpath("../../../../../../../../../../home/../bin/ls"), "/bin/ls")


	def test_striplocal(self):
		"file_normpath strips file:// for local files"

		self.assertEqual(io.file_normpath("file:///bin/ls"), "/bin/ls")


	def test_striplocal_relative(self):
		"file_normpath strips file: for local, relative paths"

		self.assertEqual(io.file_normpath("file:../../../../../../../../home/../bin/ls"), "/bin/ls")



class file_read(unittest.TestCase):
	"file_read()"

	def test_invperm(self):
		"file_read() without perms"

		io.file_write("/tmp/iotest-perms", "")
		os.chmod("/tmp/iotest-perms", 0000)
		self.assertRaises(IOError, io.file_read, "/tmp/iotest-perms")


	def test_local(self):
		"file_read() on local file"

		self.assertNotEqual(io.file_read("/bin/ls"), "")
		self.assertNotEqual(io.file_read("/bin/ls"), None)


	def test_none(self):
		"file_read() passed None"

		self.assertRaises(IOError, io.file_read, None)


	def test_nonexist(self):
		"file_read() on non-existant file"

		self.assertRaises(IOError, io.file_read, "/jfejiof0312e390rjw")


	def test_remote(self):
		"file_read() on remote file"

		self.assertNotEqual(io.file_read("http://www.google.com/index.html"), "")
		self.assertNotEqual(io.file_read("http://www.google.com/index.html"), None)




class file_is_local(unittest.TestCase):
	"file_is_local()"

	def test_local(self):
		"file_is_local() for local file"

		self.assertEqual(io.file_is_local("/bin/ls"), True)


	def test_none(self):
		"file_is_local() for None"

		self.assertEqual(io.file_is_local(None), False)


	def test_remote(self):
		"file_is_local() for remote file"

		self.assertEqual(io.file_is_local("http://www.google.com/index.html"), False)



class file_write(unittest.TestCase):
	"file_write()"

	def test_create(self):
		"file_write() creates file"

		file = "/tmp/iotest-tempfile"
		data = "test123"

		if os.access(file, os.F_OK):
			os.unlink(file)

		io.file_write(file, "test123")
		self.assertEqual(os.access(file, os.F_OK), True)


	def test_invperm(self):
		"file_write() without perms"

		io.file_write("/tmp/iotest-perms", "")
		os.chmod("/tmp/iotest-perms", 0000)
		self.assertRaises(IOError, io.file_write, "/tmp/iotest-perms", "test123")


	def test_nofile(self):
		"file_write() passed None as file"

		self.assertRaises(IOError, io.file_write, None, "test123")


	def test_nodata(self):
		"file_write() handles None as data"

		io.file_write("/tmp/iotest-testfile", None)

		f = open("/tmp/iotest-testfile")
		self.assertEquals(f.read(), "")
		f.close()


	def test_overwrite(self):
		"file_write() overwrites file"

		file = "/tmp/iotest-tempfile"
		data = "testjejejeje"

		f = open(file, "w")
		f.write("dummydata")
		f.close()

		io.file_write(file, data)

		f = open(file)
		self.assertEqual(f.read(), data)
		f.close()



if __name__ == "__main__":
	unittest.main()

