#!/usr/bin/env python

#
# Revelation 0.3.3 - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Unit tests for util module
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

import os, sys, time, unittest

from revelation import util



class escape_markup(unittest.TestCase):
	"escape_markup()"

	def test_amp(self):
		"escape_markup() replaces & with &amp;"

		self.assertEqual(
			util.escape_markup("test&123"),
			"test&123".replace("&", "&amp;")
		)


	def test_gt(self):
		"escape_markup() replaces > with &gt;"

		self.assertEqual(
			util.escape_markup("test>123"),
			"test>123".replace(">", "&gt;")
		)


	def test_lt(self):
		"escape_markup() replaces < with &lt;"

		self.assertEqual(
			util.escape_markup("test<123"),
			"test<123".replace("<", "&lt;")
		)



class execute(unittest.TestCase):
	"execute()"

	def test_output(self):
		"execute() returns output"

		self.assertEqual(util.execute("echo -n test123")[0], "test123")


	def test_run(self):
		"execute() runs command"

		if os.access("/tmp/exectest", os.F_OK):
			os.unlink("/tmp/exectest")

		util.execute("touch /tmp/exectest")

		self.assertEqual(os.access("/tmp/exectest", os.F_OK), True)


	def test_status(self):
		"execute() returns status code"

		self.assertEqual(util.execute("exit 0")[1], 0)
		self.assertEqual(util.execute("exit 1")[1], 1)
		self.assertEqual(util.execute("exit 52")[1], 52)



class execute_child(unittest.TestCase):
	"execute_child()"

	def test_nowait(self):
		"execute_child() doesn't wait"

		start = time.time()
		util.execute_child("sleep 2")
		self.assertEqual(start > time.time() - 1, True)


	def test_pid(self):
		"execute_child() returns process id"

		pid = util.execute_child("sleep 1")
		waitdata = os.waitpid(pid, 0)

		self.assertEqual(pid, waitdata[0])


	def test_run(self):
		"execute_child() runs command"

		if os.access("/tmp/exectest", os.F_OK):
			os.unlink("/tmp/exectest")

		util.execute_child("touch /tmp/exectest")
		time.sleep(1)
		self.assertEqual(os.access("/tmp/exectest", os.F_OK), True)



class generate_password(unittest.TestCase):
	"generate_password()"

	def test_ambiguous(self):
		"generate_password() avoids ambiguous chars when told"

		for i in range(100):
			password = util.generate_password(256, True)

			for char in "0OIl1S5qg":
				self.assertEqual(
					char in password,
					False
				)


	def test_digits(self):
		"generate_password() always includes a digit"

		for i in range(100):
			for char in util.generate_password(8):
				if char.isdigit():
					digit = True
					break

			else:
				digit = False

			self.assertEqual(digit, True)


	def test_length(self):
		"generate_password() returns string of correct length"

		for length in 1, 5, 17, 54, 270:
			self.assertEqual(
				len(util.generate_password(length)),
				length
			)


	def test_lowercase(self):
		"generate_password() always includes a lowercase char"

		for i in range(100):
			for char in util.generate_password(8):
				if char.islower():
					lower = True
					break

			else:
				lower = False

			self.assertEqual(lower, True)


	def test_random(self):
		"generate_password() returns random string"

		for i in range(3):
			self.assertNotEqual(
				util.generate_password(8),
				util.generate_password(8)
			)


	def test_uppercase(self):
		"generate_password() always includes an uppercase char"

		for i in range(100):
			for char in util.generate_password(8):
				if char.isupper():
					upper = True
					break

			else:
				upper = False

			self.assertEqual(upper, True)



class random_string(unittest.TestCase):
	"random_string()"

	def test_length(self):
		"random_string() returns string of correct length"

		for length in 1, 5, 17, 54, 270:
			self.assertEqual(
				len(util.random_string(length)),
				length
			)


	def test_random(self):
		"random_string() returns a random string"

		for i in range(3):
			self.assertNotEqual(
				util.random_string(8),
				util.random_string(8)
			)



class time_period_rough(unittest.TestCase):
	"time_period_rough()"

	def test_endfirst(self):
		"time_period_rough() returns '0 seconds' when end-time is earliest"

		self.assertEqual(
			util.time_period_rough(1098565803, 1098565800),
			"0 seconds"
		)


	def test_results(self):
		"time_period_rough() returns correct results"

		data = (

			# year intervals
			( "2004-10-23 10:00:00", "2005-10-23 10:00:00", "1 year" ),
			( "2004-10-23 10:00:00", "2006-10-23 09:59:59", "1 year" ),
			( "2004-10-23 10:00:00", "2007-02-11 15:14:31", "2 years" ),
			( "2004-10-23 10:00:00", "2015-12-11 15:14:31", "11 years" ),

			# month intervals
			( "2004-10-23 10:00:00", "2004-11-23 10:00:00", "1 month" ),
			#( "2004-10-23 10:00:00", "2004-12-23 09:59:59", "1 month" ),
			#( "2004-02-01 10:00:00", "2004-03-01 10:00:00", "1 month" ),
			( "2004-10-23 10:00:00", "2004-12-23 10:00:00", "2 months" ),
			( "2004-10-23 10:00:00", "2005-03-07 23:11:42", "4 months" ),
			( "2004-10-23 10:00:00", "2005-10-23 09:59:59", "11 months" ),

			# week intervals
			( "2004-10-23 10:00:00", "2004-10-30 10:00:00", "1 week" ),
			( "2004-10-23 10:00:00", "2004-10-31 15:41:11", "1 week" ),
			( "2004-10-23 10:00:00", "2004-11-23 09:59:59", "4 weeks" ),
			( "2004-10-23 10:00:00", "2004-11-06 18:11:21", "2 weeks" ),

			# day intervals
			( "2004-10-23 10:00:00", "2004-10-24 10:00:00", "1 day" ),
			( "2004-10-23 10:00:00", "2004-10-25 09:59:59", "1 day" ),
			( "2004-10-23 10:00:00", "2004-10-25 10:00:00", "2 days" ),
			( "2004-10-23 10:00:00", "2004-10-29 19:21:47", "6 days" ),
			( "2004-10-30 10:00:00", "2004-11-03 04:13:17", "3 days" ),
			( "2004-12-29 08:11:45", "2005-01-03 10:48:53", "5 days" ),


			# hour intervals
			( "2004-10-23 10:00:00", "2004-10-23 11:00:00", "1 hour" ),
			( "2004-10-23 10:00:00", "2004-10-23 11:53:24", "1 hour" ),
			( "2004-10-23 10:00:00", "2004-10-23 12:00:00", "2 hours" ),
			( "2004-10-23 10:00:00", "2004-10-23 19:59:59", "9 hours" ),
			( "2004-10-23 05:32:11", "2004-10-23 14:18:32", "8 hours" ),
			( "2004-10-23 10:00:00", "2004-10-24 09:59:59", "23 hours" ),
			( "2004-10-31 10:00:00", "2004-11-01 04:42:11", "18 hours" ),
			( "2004-12-31 17:43:11", "2005-01-01 11:18:55", "17 hours" ),

			# minute intervals
			( "2004-10-23 10:00:00", "2004-10-23 10:01:00", "1 minute" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:01:13", "1 minute" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:02:00", "2 minutes" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:24:41", "24 minutes" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:59:59", "59 minutes" ),
			( "2004-10-23 10:42:28", "2004-10-23 11:18:04", "35 minutes" ),
			( "2004-10-23 23:57:21", "2004-10-24 00:13:22", "16 minutes" ),
			( "2004-10-31 23:57:21", "2004-11-01 00:13:22", "16 minutes" ),
			( "2004-12-31 23:57:21", "2005-01-01 00:13:22", "16 minutes" ),

			# second intervals
			( "2004-10-23 10:00:00", "2004-10-23 10:00:00", "0 seconds" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:00:01", "1 second" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:00:23", "23 seconds" ),
			( "2004-10-23 10:00:00", "2004-10-23 10:00:59", "59 seconds" ),
			( "2004-10-23 12:59:48", "2004-10-23 13:00:12", "24 seconds" ),
			( "2004-10-23 23:59:43", "2004-10-24 00:00:22", "39 seconds" ),
			( "2004-10-31 23:59:43", "2004-11-01 00:00:22", "39 seconds" ),
			( "2004-12-31 23:59:43", "2005-01-01 00:00:22", "39 seconds" )
		)

		for start, end, range in data:
			start = time.mktime((int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13]), int(start[14:16]), int(start[17:19]), 0, 1, 0))
			end = time.mktime((int(end[0:4]), int(end[5:7]), int(end[8:10]), int(end[11:13]), int(end[14:16]), int(end[17:19]), 0, 1, 0))

			self.assertEqual(
				util.time_period_rough(start, end),
				range
			)



if __name__ == "__main__":
	unittest.main()

