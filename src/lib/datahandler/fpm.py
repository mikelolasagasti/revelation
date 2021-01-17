#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling Figaro's Password Manager data
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from . import base
from revelation import data, entry, util

import math
import secrets
import string

import defusedxml.minidom

from xml.parsers.expat import ExpatError
from Cryptodome.Cipher import Blowfish
from Cryptodome.Hash import MD5
import Cryptodome.Random as Random


class FPM(base.DataHandler):
    "Data handler for Figaro's Password Manager data"

    name        = "Figaro's Password Manager"
    importer    = True
    exporter    = True
    encryption  = True

    def __init__(self):
        base.DataHandler.__init__(self)

    def __decrypt(self, cipher, data):
        "Decrypts data"

        if isinstance(data, str):
            data = data.encode()

        # decode ascii armoring
        decoded = b""

        for i in range(len(data) // 2):
            high = data[2 * i] - ord("a")
            low =  data[2 * i + 1] - ord("a")
            decoded += bytes((high * 16 + low,))
        data = decoded

        # decrypt data
        data = cipher.decrypt(data)

        # unrotate field
        blocks = int(math.ceil(len(data) / float(8)))
        plain = b""

        for offset in range(8):
            for block in range(blocks):
                plain += bytes((data[block * 8 + offset],))

        return plain.split(b"\x00")[0]

    def __encrypt(self, cipher, data):
        "Encrypts data"

        # get data sizes
        blocks = (len(data) // 7) + 1
        size = 8 * blocks

        # add noise
        rand = Random.new()
        data += b'\x00' + rand.read(size - len(data) - 1)

        # rotate data
        rotated = b""
        for block in range(blocks):
            for offset in range(8):
                rotated += bytes((data[offset * blocks + block],))

        data = rotated

        # encrypt data
        data = cipher.encrypt(data)

        # ascii-armor data
        res = b""

        for i in range(len(data)):
            high = data[i] // 16
            low = data[i] - high * 16
            res += bytes((ord("a") + high, ord("a") + low))

        data = res

        return data

    def check(self, input):
        "Checks if the data is valid"

        try:
            if input is None:
                raise base.FormatError

            dom = defusedxml.minidom.parseString(input.strip())

            if dom.documentElement.nodeName != "FPM":
                raise base.FormatError

            minversion = dom.documentElement.attributes["min_version"].nodeValue

            if int(minversion.split(".")[1]) > 58:
                raise base.VersionError

        except ExpatError:
            raise base.FormatError

        except (KeyError, IndexError):
            raise base.FormatError

    def detect(self, input):
        "Checks if this handler can handle the given data"

        try:
            self.check(input)
            return True

        except (base.FormatError, base.VersionError, base.DataError):
            return False

    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        # set up encryption engine
        alphabet = string.ascii_letters + string.digits
        salt = bytes([''.join(secrets.choice(alphabet) for i in range(8))])
        password = MD5.new(salt + password.encode()).digest()  # nosec

        cipher = Blowfish.new(password, Blowfish.MODE_ECB)  # nosec

        # generate data
        xml = "<?xml version=\"1.0\" ?>\n"
        xml += "<FPM full_version=\"00.58.00\" min_version=\"00.58.00\" display_version=\"00.58.00\">\n"
        xml += "    <KeyInfo salt=\"%s\" vstring=\"%s\" />\n" % (salt.decode(), self.__encrypt(cipher, b"FIGARO").decode())
        xml += "    <LauncherList></LauncherList>\n"
        xml += "    <PasswordList>\n"

        iter = entrystore.iter_children(None)

        while iter is not None:
            e = entrystore.get_entry(iter)

            if type(e) != entry.FolderEntry:
                e = e.convert_generic()

                xml += "        <PasswordItem>\n"
                xml += "            <title>%s</title>\n" % self.__encrypt(cipher, e.name.encode()).decode()
                xml += "            <url>%s</url>\n" % self.__encrypt(cipher, e.get_field(entry.HostnameField).value.encode()).decode()
                xml += "            <user>%s</user>\n" % self.__encrypt(cipher, e.get_field(entry.UsernameField).value.encode()).decode()
                xml += "            <password>%s</password>\n" % self.__encrypt(cipher, e.get_field(entry.PasswordField).value.encode()).decode()
                xml += "            <notes>%s</notes>\n" % self.__encrypt(cipher, e.description.encode()).decode()

                path = entrystore.get_path(iter).to_string()

                if len(path) > 1:
                    foldername = entrystore.get_entry(entrystore.get_iter(path[0])).name
                    xml += "            <category>%s</category>\n" % self.__encrypt(cipher, foldername.encode()).decode()

                else:
                    xml += "            <category></category>\n"

                xml += "            <launcher></launcher>\n"
                xml += "        </PasswordItem>\n"

            iter = entrystore.iter_traverse_next(iter)

        xml += "    </PasswordList>\n"
        xml += "</FPM>\n"

        return xml

    def import_data(self, input, password):
        "Imports data into an entrystore"

        try:

            # check and load data
            self.check(input)
            dom = defusedxml.minidom.parseString(input.strip())

            if dom.documentElement.nodeName != "FPM":
                raise base.FormatError

            # set up decryption engine, and check if password is correct
            keynode = dom.documentElement.getElementsByTagName("KeyInfo")[0]
            salt = keynode.attributes["salt"].nodeValue.encode()
            vstring = keynode.attributes["vstring"].nodeValue.encode()

            password = MD5.new(salt + password.encode()).digest()  # nosec
            cipher = Blowfish.new(password, Blowfish.MODE_ECB)  # nosec

            if self.__decrypt(cipher, vstring) != b"FIGARO":
                raise base.PasswordError

        except ExpatError:
            raise base.FormatError

        except (IndexError, KeyError):
            raise base.FormatError

        # import entries into entrystore
        entrystore = data.EntryStore()
        folders = {}

        for node in dom.getElementsByTagName("PasswordItem"):

            parent = None
            e = entry.GenericEntry()

            for fieldnode in [node for node in node.childNodes if node.nodeType == node.ELEMENT_NODE]:

                content = self.__decrypt(cipher, util.dom_text(fieldnode)).decode()

                if content == "":
                    continue

                elif fieldnode.nodeName == "title":
                    e.name = content

                elif fieldnode.nodeName == "user":
                    e.get_field(entry.UsernameField).value = content

                elif fieldnode.nodeName == "url":
                    e.get_field(entry.HostnameField).value = content

                elif fieldnode.nodeName == "password":
                    e.get_field(entry.PasswordField).value = content

                elif fieldnode.nodeName == "notes":
                    e.description = content

                elif fieldnode.nodeName == "category":

                    if content in folders:
                        parent = folders[content]

                    else:
                        folderentry = entry.FolderEntry()
                        folderentry.name = content

                        parent = entrystore.add_entry(folderentry)
                        folders[content] = parent

            entrystore.add_entry(e, parent)

        return entrystore
