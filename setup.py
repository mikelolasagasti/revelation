#!/usr/bin/env python
# $Id$

from distutils.core import setup
import sys, os

setup(
	name		= 'Revelation',
	version		= '0.3.3',
	description	= 'Password manager for GNOME 2',
	author		= 'Erik Grinaker',
	author_email	= 'erikg@codepoet.no',
	url		= 'http://oss.codepoet.no/revelation/',

	packages	= [ 'revelation', 'revelation.datahandler' ],
	package_dir	= { 'revelation' : 'src/lib' },

	scripts		= [ 'src/revelation' ],

	data_files	= [
				( 'share/pixmaps', [
					'data/images/revelation.png'
				] ),

				( 'share/revelation/pixmaps', [
					'data/images/account-creditcard.png',
					'data/images/account-cryptokey.png',
					'data/images/account-database.png',
					'data/images/account-door.png',
					'data/images/account-email.png',
					'data/images/account-ftp.png',
					'data/images/account-generic.png',
					'data/images/account-phone.png',
					'data/images/account-shell.png',
					'data/images/account-website.png',
					'data/images/folder.png',
					'data/images/folder-open.png',
					'data/images/password.png',
					'data/images/revelation.png',
					'data/images/revelation-16x16.png'
				] ),

				( 'share/applications', [
					'data/revelation.desktop'
				] ),

				( '/etc/gconf/schemas', [
					'data/revelation.schemas'
				] )
			]
)

