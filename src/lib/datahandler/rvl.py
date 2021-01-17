#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling Revelation data
#
#
# Copyright (c) 2003-2006 Erik Grinaker
# Copyright (c) 2012 Mikel Olasagasti
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
from revelation import config, data, entry, util
from revelation.bundle import luks

from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA1
from Cryptodome.Random import get_random_bytes

import defusedxml.minidom
import os
import re
import struct
import zlib

from io import BytesIO

from xml.parsers.expat import ExpatError
from Cryptodome.Cipher import AES

import hashlib


class RevelationXML(base.DataHandler):
    "Handler for Revelation XML data"

    name        = "XML"
    importer    = True
    exporter    = True
    encryption  = False

    def __init__(self):
        base.DataHandler.__init__(self)

    def __lookup_entry(self, typename):
        "Looks up an entry type based on an identifier"

        for entrytype in entry.ENTRYLIST:
            if entrytype().id == typename:
                return entrytype

        else:
            raise entry.EntryTypeError

    def __lookup_field(self, fieldname):
        "Looks up an entry field based on an identifier"

        for fieldtype in entry.FIELDLIST:
            if fieldtype.id == fieldname:
                return fieldtype

        else:
            raise entry.EntryFieldError

    def __xml_import_node(self, entrystore, node, parent = None):
        "Imports a node into an entrystore"

        try:

            # check the node
            if node.nodeType == node.TEXT_NODE:
                return

            if node.nodeType != node.ELEMENT_NODE or node.nodeName != "entry":
                raise base.FormatError

            # create an entry, iter needed for children
            e = self.__lookup_entry(node.attributes["type"].value)()
            iter = entrystore.add_entry(e, parent)

            # handle child nodes
            for child in node.childNodes:

                if child.nodeType != child.ELEMENT_NODE:
                    continue

                elif child.nodeName == "name":
                    e.name = util.dom_text(child)

                elif child.nodeName == "notes":
                    e.notes = util.dom_text(child)

                elif child.nodeName == "description":
                    e.description = util.dom_text(child)

                elif child.nodeName == "updated":
                    e.updated = int(util.dom_text(child))

                elif child.nodeName == "field":
                    e[self.__lookup_field(child.attributes["id"].nodeValue)] = util.dom_text(child)

                elif child.nodeName == "entry":
                    if type(e) != entry.FolderEntry:
                        raise base.DataError

                    self.__xml_import_node(entrystore, child, iter)

                else:
                    raise base.FormatError

            # update entry with actual data
            entrystore.update_entry(iter, e)

        except (entry.EntryTypeError, entry.EntryFieldError):
            raise base.DataError

        except KeyError:
            raise base.FormatError

        except ValueError:
            raise base.DataError

    def check(self, input):
        "Checks if the data is valid"

        if input is None:
            raise base.FormatError

        if isinstance(input, str):
            input = input.encode()

        match = re.match(b"""
            \s*                 # whitespace at beginning
            <\?xml(?:.*)\?>     # xml header
            \s*                 # whitespace after xml header
            <revelationdata     # open revelationdata tag
            [^>]+               # any non-closing character
            dataversion="(\d+)" # dataversion
            [^>]*               # any non-closing character
            >                   # close revelationdata tag
        """, input, re.VERBOSE)

        if match is None:
            raise base.FormatError

        if int(match.group(1)) != 1:
            raise base.VersionError

    def detect(self, input):
        "Checks if this handler can guarantee to handle some data"

        try:
            self.check(input)
            return True

        except (base.FormatError, base.VersionError):
            return False

    def export_data(self, entrystore, password = None, parent = None, level = 0):
        "Serializes data into an XML stream"

        xml = ""
        tabs = "\t" * (level + 1)

        for i in range(entrystore.iter_n_children(parent)):
            iter = entrystore.iter_nth_child(parent, i)
            e = entrystore.get_entry(iter)

            xml += "\n"
            xml += tabs + "<entry type=\"%s\">\n" % e.id
            xml += tabs + " <name>%s</name>\n" % util.escape_markup(e.name)
            xml += tabs + " <description>%s</description>\n" % util.escape_markup(e.description)
            xml += tabs + " <updated>%d</updated>\n" % e.updated
            xml += tabs + " <notes>%s</notes>\n" % util.escape_markup(e.notes)

            for field in e.fields:
                xml += tabs + " <field id=\"%s\">%s</field>\n" % (field.id, util.escape_markup(field.value))

            xml += RevelationXML.export_data(self, entrystore, password, iter, level + 1)
            xml += tabs + "</entry>\n"

        if level == 0:
            header = "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
            header += "<revelationdata version=\"%s\" dataversion=\"1\">\n" % config.VERSION
            footer = "</revelationdata>\n"

            xml = header + xml + footer

        return xml

    def import_data(self, input, password = None):
        "Imports data from a data stream to an entrystore"

        RevelationXML.check(self, input)

        try:
            dom = defusedxml.minidom.parseString(input.strip())

        except ExpatError:
            raise base.FormatError

        if dom.documentElement.nodeName != "revelationdata":
            raise base.FormatError

        if "dataversion" not in dom.documentElement.attributes:
            raise base.FormatError

        entrystore = data.EntryStore()

        for node in dom.documentElement.childNodes:
            self.__xml_import_node(entrystore, node)

        return entrystore


class Revelation(RevelationXML):
    "Handler for Revelation data"

    name        = "Revelation"
    importer    = True
    exporter    = True
    encryption  = True

    def __init__(self):
        RevelationXML.__init__(self)

    def __generate_header(self):
        "Generates a header"

        header = "rvl\x00"         # magic string
        header += "\x01"           # data version
        header += "\x00"           # separator
        header += "\x00\x04\x06"   # application version TODO
        header += "\x00\x00\x00"   # separator

        return header

    def __parse_header(self, header):
        "Parses a data header, returns the data version"

        if header is None:
            raise base.FormatError

        match = re.match(b"""
            ^               # start of header
            rvl\x00         # magic string
            (.)             # data version
            \x00            # separator
            (.{3})          # app version
            \x00\x00\x00    # separator
        """, header, re.VERBOSE)

        if match is None:
            raise base.FormatError

        return ord(match.group(1))

    def check(self, input):
        "Checks if the data is valid"

        if input is None:
            raise base.FormatError

        if len(input) < (12 + 16):
            raise base.FormatError

        dataversion = self.__parse_header(input[:12])

        if dataversion != 1:
            raise base.VersionError

    def detect(self, input):
        "Checks if the handler can guarantee to use the data"

        try:
            self.check(input)
            return True

        except (base.FormatError, base.VersionError):
            return False

    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        # check and pad password
        if password is None:
            raise base.PasswordError

        password = util.pad_right(password[:32], 32, "\0")

        # generate XML
        data = RevelationXML.export_data(self, entrystore)

        # compress data, and right-pad with the repeated ascii
        # value of the pad length
        data = zlib.compress(data.encode())

        padlen = 16 - (len(data) % 16)
        if padlen == 0:
            padlen = 16

        data += bytearray((padlen,)) * padlen

        # generate an initial vector for the CBC encryption
        iv = os.urandom(16)

        data = AES.new(password.encode("utf8"), AES.MODE_CBC, iv).encrypt(data)

        # encrypt the iv, and prepend it to the data with a header
        data = self.__generate_header().encode("utf8") + AES.new(password.encode("utf8"), AES.MODE_ECB).encrypt(iv) + data

        return data

    def import_data(self, input, password):
        "Imports data into an entrystore"

        # check and pad password
        if password is None:
            raise base.PasswordError

        password = util.pad_right(password[:32], 32, "\0")

        # check the data
        self.check(input)
        dataversion = self.__parse_header(input[:12])

        # handle only version 1 data files
        if dataversion != 1:
            raise base.VersionError

        cipher = AES.new(password.encode("utf8"), AES.MODE_ECB)
        iv = cipher.decrypt(input[12:28])

        # decrypt the data
        input = input[28:]

        if len(input) % 16 != 0:
            raise base.FormatError

        cipher = AES.new(password.encode("utf8"), AES.MODE_CBC, iv)
        input = cipher.decrypt(input)

        # decompress data
        padlen = input[-1]
        for i in input[-padlen:]:
            if i != padlen:
                raise base.PasswordError

        input = zlib.decompress(input[0:-padlen]).decode()

        # check and import data
        if input.strip()[:5] != "<?xml":
            raise base.PasswordError

        entrystore = RevelationXML.import_data(self, input)

        return entrystore


class Revelation2(RevelationXML):
    "Handler for Revelation data version 2"

    name        = "Revelation2"
    importer    = True
    exporter    = True
    encryption  = True

    def __init__(self):
        RevelationXML.__init__(self)

    def __generate_header(self):
        "Generates a header"

        header = b"rvl\x00"        # magic string
        header += b"\x02"           # data version
        header += b"\x00"           # separator
        header += b"\x00\x04\x07"   # application version
        header += b"\x00\x00\x00"   # separator

        return header

    def __parse_header(self, header):
        "Parses a data header, returns the data version"

        if header is None:
            raise base.FormatError

        match = re.match(b"""
            ^               # start of header
            rvl\x00         # magic string
            (.)             # data version
            \x00            # separator
            (.{3})          # app version
            \x00\x00\x00    # separator
        """, header, re.VERBOSE)

        if match is None:
            raise base.FormatError

        return ord(match.group(1))

    def check(self, input):
        "Checks if the data is valid"

        if input is None:
            raise base.FormatError

        if len(input) < (12 + 16):
            raise base.FormatError

        dataversion = self.__parse_header(input[:12])

        if dataversion != 2:
            raise base.VersionError

    def detect(self, input):
        "Checks if the handler can guarantee to use the data"

        try:
            self.check(input)
            return True

        except (base.FormatError, base.VersionError):
            return False

    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        # check and hash password with a salt
        if password is None:
            raise base.PasswordError

        # 64-bit salt
        salt = get_random_bytes(8)

        # 256-bit key
        key = PBKDF2(password, salt, 32, count=12000, hmac_hash_module=SHA1)

        # generate XML
        data = RevelationXML.export_data(self, entrystore)

        # compress data, and right-pad with the repeated ascii
        # value of the pad length
        data = zlib.compress(data.encode())

        padlen = 16 - (len(data) % 16)
        if padlen == 0:
            padlen = 16

        data += bytearray((padlen,)) * padlen

        # 128-bit IV
        iv = get_random_bytes(16)

        data = AES.new(key, AES.MODE_CBC, iv).encrypt(hashlib.sha256(data).digest() + data)

        # encrypt the iv, and prepend it to the data with a header and the used salt
        data = self.__generate_header() + salt + iv + data

        return data

    def import_data(self, input, password):
        "Imports data into an entrystore"

        # check and pad password
        if password is None:
            raise base.PasswordError

        # check the data
        self.check(input)
        dataversion = self.__parse_header(input[:12])

        # handle only version 2 data files
        if dataversion != 2:
            raise base.VersionError

        # Fetch the used 64 bit salt
        salt = input[12:20]
        iv = input[20:36]
        key = PBKDF2(password, salt, 32, count=12000, hmac_hash_module=SHA1)
        # decrypt the data
        input = input[36:]

        if len(input) % 16 != 0:
            raise base.FormatError

        cipher = AES.new(key, AES.MODE_CBC, iv)
        input = cipher.decrypt(input)
        hash256 = input[0:32]
        data = input[32:]

        if hash256 != hashlib.sha256(data).digest():
            raise base.PasswordError

        # decompress data
        padlen = data[-1]
        for i in data[-padlen:]:
            if i != padlen:
                raise base.FormatError

        data = zlib.decompress(data[0:-padlen]).decode()

        # check and import data
        if data.strip()[:5] != "<?xml":
            raise base.FormatError

        entrystore = RevelationXML.import_data(self, data)

        return entrystore


class RevelationLUKS(RevelationXML):
    "Handler for Revelation XML using the LUKS on disk format"

    name        = "Revelation LUKS"
    importer    = True
    exporter    = True
    encryption  = True

    def __init__(self):
        RevelationXML.__init__(self)
        self.luks_header = None
        self.luks_buff = None
        self.current_slot = False

    def check(self, input):
        "Checks if the data is valid"

        if input is None:
            raise base.FormatError

        sbuf = BytesIO(input)

        l = luks.LuksFile()

        try:
            l.load_from_file(sbuf)

        except:
            l.close()
            raise base.FormatError

        l.close()

    def detect(self, input):
        "Checks if the handler can guarantee to use the data"

        try:
            self.check(input)
            return True

        except (base.FormatError, base.VersionError):
            return False

    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        # check and pad password
        if password is None:
            raise base.PasswordError

        # generate and compress XML
        data = RevelationXML.export_data(self, entrystore)
        data = zlib.compress(data.encode())

        # data needs to be padded to 512 bytes
        # We use Merkle-Damgard length padding (1 bit followed by 0 bits + size)
        # http://en.wikipedia.org/wiki/Merkle-Damg%C3%A5rd_hash_function
        padlen = 512 - (len(data) % 512)

        if padlen < 4:
            padlen = 512 + padlen

        if padlen > 4:
            data += bytes([128] + [0] * (padlen - 5))

        data += struct.pack("<I", padlen)

        # create a new luks file in memory
        buffer      = BytesIO()
        luksfile    = luks.LuksFile()
        luksfile.create(buffer, "aes", "cbc-essiv:sha256", "sha1", 16, 400)

        luksfile.set_key(0, password, 5000, 400)

        # encrypt the data
        luksfile.encrypt_data(0, data)
        buffer.seek(0)

        return buffer.read()

    def import_data(self, input, password):
        "Imports data into an entrystore"

        # check password
        if password is None:
            raise base.PasswordError

        # create a LuksFile
        buffer      = BytesIO(input)
        luksfile    = luks.LuksFile()

        try:
            luksfile.load_from_file(buffer)

        except:
            luksfile.close()
            buffer.close()
            raise base.FormatError

        slot = luksfile.open_any_key(password)

        if slot is None:
            luksfile.close()
            buffer.close()
            raise base.PasswordError

        data = luksfile.decrypt_data(0, luksfile.data_length())

        # remove the pad, and decompress
        padlen = struct.unpack("<I", data[-4:])[0]
        data = zlib.decompress(data[0:-padlen]).decode()

        if data.strip()[:5] != "<?xml":
            raise base.FormatError

        entrystore = RevelationXML.import_data(self, data)

        return entrystore
