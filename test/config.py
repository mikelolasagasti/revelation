#!/usr/bin/env python

#
# Revelation 0.4.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for config module
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

from revelation import config

import gconf, gobject, gtk, unittest



class attrs(unittest.TestCase):
	"config attributes"

	def test_attrs(self):
		"config module has required attributes"

		attrs = [
			"APPNAME", "VERSION", "DATAVERSION", "RELNAME",
			"URL", "AUTHOR", "COPYRIGHT",
			"DIR_GCONFSCHEMAS", "DIR_ICONS", "DIR_UI",
			"FILE_GCONFTOOL"
		]

		for attr in attrs:
			self.assertEquals(hasattr(config, attr), True)



class Config__init(unittest.TestCase):
	"Config.__init__()"

	def test_basedir(self):
		"Config.__init__() sets correct default basedir"

		cfg = config.Config()
		self.assertEquals(cfg.basedir, "/apps/revelation")


	def test_inv_basedir(self):
		"Config.__init__() raises ConfigError on invalid basedir"

		self.assertRaises(config.ConfigError, config.Config, "/test/123")



class Config_check(unittest.TestCase):
	"Config.check()"

	pass



class Config_forget(unittest.TestCase):
	"Config.forget()"

	def test_forget(self):
		"Config.forget() removes the callback"

		global foo
		foo = 0

		def cb(key, value, userdata):
			global foo
			foo += 1

			if gtk.main_level() > 0:
				gtk.main_quit()

		cfg = config.Config()
		id = cfg.monitor("file/autoload_file", cb)

		cfg.set("file/autoload_file", "test123")
		gtk.main()
		self.assertEquals(foo, 2)

		cfg.forget(id)

		cfg.set("file/autoload_file", "test")
		gobject.timeout_add(500, lambda: gtk.main_quit())
		gtk.main()
		self.assertEquals(foo, 2)


	def test_inv_id(self):
		"Config.forget() raises ConfigError on invalid id"

		cfg = config.Config()
		self.assertRaises(config.ConfigError, cfg.forget, 1)



class Config_get(unittest.TestCase):
	"Config.get()"


	def test_absolute(self):
		"Config.get() handles absolute paths"

		cfg = config.Config()
		cfg.get("/desktop/gnome/interface/gtk_theme")


	def test_nonexist(self):
		"Config.get() raises ConfigError on non-existant node"

		cfg = config.Config()
		self.assertRaises(config.ConfigError, cfg.get, "test/123")


	def test_relative(self):
		"Config.get() handles relative paths"

		cfg = config.Config()
		cfg.get("file/autoload_file")



class Config_monitor(unittest.TestCase):
	"Config.monitor()"

	def test_change(self):
		"Config.monitor() calls callback on change"

		global foo
		foo = 0

		def cb(key, value, userdata):
			global foo
			foo += 1

			if gtk.main_level() > 0:
				gtk.main_quit()

		cfg = config.Config()
		cfg.monitor("file/autoload_file", cb)

		cfg.set("file/autoload_file", "test123")
		gtk.main()
		self.assertEquals(foo, 2)


	def test_id(self):
		"Config.monitor() returns a valid callback id"

		cfg = config.Config()
		id = cfg.monitor("file/autoload_file", lambda k,v,d: None)

		self.assertNotEqual(id, None)
		cfg.forget(id)


	def test_init(self):
		"Config.monitor() calls callback on setup"

		def cb(key, value, userdata):
			global foo
			foo = "test"

		cfg = config.Config()
		cfg.monitor("file/autoload_file", cb)

		self.assertEquals(foo, "test")



class Config_set(unittest.TestCase):
	"Config.set()"

	def test_absolute(self):
		"Config.set() handler absolute paths"

		cfg = config.Config()

		cfg.set("/apps/revelation/file/autoload_file", "123test")
		self.assertEquals(cfg.get("/apps/revelation/file/autoload_file"), "123test")


	def test_relative(self):
		"Config.set() handles relative paths"

		cfg = config.Config()

		cfg.set("file/autoload_file", "test123")
		self.assertEquals(cfg.get("file/autoload_file"), "test123")



if __name__ == "__main__":
	unittest.main()

