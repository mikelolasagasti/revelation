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
					'pixmaps/revelation.png'
				] ),

				( 'share/revelation/pixmaps', [
					'pixmaps/account-creditcard.png',
					'pixmaps/account-cryptokey.png',
					'pixmaps/account-database.png',
					'pixmaps/account-door.png',
					'pixmaps/account-email.png',
					'pixmaps/account-ftp.png',
					'pixmaps/account-generic.png',
					'pixmaps/account-phone.png',
					'pixmaps/account-shell.png',
					'pixmaps/account-website.png',
					'pixmaps/folder.png',
					'pixmaps/folder-open.png',
					'pixmaps/password.png',
					'pixmaps/revelation.png',
					'pixmaps/revelation-16x16.png'
				] ),

				( 'share/applications', [
					'gnome/revelation.desktop'
				] ),

				( '/etc/gconf/schemas', [
					'gnome/revelation.schemas'
				] )
			]
)

