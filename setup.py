#!/usr/bin/env python
# $Id$

from distutils.core import setup
import sys, os

setup(
	name		= 'Revelation',
	version		= '0.3.0',
	description	= 'Password manager for GNOME 2',
	author		= 'Erik Grinaker',
	author_email	= 'erikg@wired-networks.net',
	url		= 'http://oss.wired-networks.net/revelation/',

	packages	= [ 'revelation' ],
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

if "install" in sys.argv:
	p = os.popen("GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source` gconftool-2 --makefile-install-rule /etc/gconf/schemas/revelation.schemas")
	p.close()

