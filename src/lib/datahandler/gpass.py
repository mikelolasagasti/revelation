#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id: gpass.py 602 2007-01-03 08:06:28Z erikg $
#
# Module for handling GPass data
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
from revelation import data, entry

import locale, re
from Cryptodome.Cipher import Blowfish
from Cryptodome.Hash import SHA


IV  = b"\x05\x17\x01\x7b\x0c\x03\x36\x5e"


def decrypt(ciphertext, password, magic = None):
    "Decrypts a data stream"

    # decrypt data
    if len(ciphertext) % 8 != 0:
        raise base.FormatError

    key     = SHA.new(password.encode()).digest()
    cipher      = Blowfish.new(key, Blowfish.MODE_CBC, IV)

    plaintext   = cipher.decrypt(ciphertext)

    # check magic string
    if magic != None:
        if plaintext[:len(magic)] != magic:
            raise base.PasswordError

        else:
            plaintext = plaintext[len(magic):]

    # remove padding
    padchar = plaintext[-1]
    npadchar = padchar

    if (npadchar > 0):
        if plaintext[-npadchar:] != bytes([padchar] * npadchar):
            raise base.FormatError

        plaintext = plaintext[:-npadchar]
    return plaintext


def encrypt(plaintext, password):
    "Encrypts a data stream"

    # right-pad data
    padlen = 8 - len(plaintext) % 8

    if padlen == 0:
        padlen = 8

    plaintext += bytes([padlen] * padlen)

    # encrypt data
    key = SHA.new(password.encode()).digest()
    cipher  = Blowfish.new(key, Blowfish.MODE_CBC, IV)

    return cipher.encrypt(plaintext)



class GPass04(base.DataHandler):
    "Data handler for GPass 0.4.x data"

    name        = "GPass 0.4.x"
    importer    = True
    exporter    = True
    encryption  = True


    def __init__(self):
        base.DataHandler.__init__(self)


    def export_data(self, entrystore, password):
        "Exports data to a data stream"

        data = "GNOME Password Manager\n"

        iter = entrystore.iter_nth_child(None, 0)

        while iter is not None:
            e = entrystore.get_entry(iter)

            if type(e) != entry.FolderEntry:
                e = e.convert_generic()

                data += e.name + "\n"
                data += (e[entry.UsernameField] or "") + "\n"
                data += (e[entry.PasswordField] or "") + "\n"
                data += (e[entry.HostnameField] or "") + "\n"
                data += str(e.updated) + "\n"
                data += str(e.updated) + "\n"
                data += "0\n"
                data += str(len(e.description) + 1) + "\n"
                data += e.description + "\n"

            iter = entrystore.iter_traverse_next(iter)

        return encrypt(data.encode(), password)


    def import_data(self, input, password):
        "Imports data from a data stream to an entrystore"

        plaintext = decrypt(input, password, b"GNOME Password Manager\n").decode()

        entrystore = data.EntryStore()
        lines = plaintext.splitlines()

        while len(lines) > 0:

            e = entry.GenericEntry()

            e.name          = lines[0]
            e[entry.UsernameField]  = lines[1]
            e[entry.PasswordField]  = lines[2]
            e[entry.HostnameField]  = lines[3]
            e.updated       = int(lines[5])
            desclen         = int(lines[7])

            if e[entry.HostnameField] == "http://":
                e[entry.HostnameField] = ""

            del lines[:8]

            d = ""
            while len(d) < desclen and len(lines) > 0:
                d += lines[0] + "\n"
                del lines[0]

            e.description = re.sub("[\r\n]+", " ", d).strip()

            entrystore.add_entry(e)

        return entrystore



class GPass05(base.DataHandler):
    "Data handler for GPass 0.5.x data"

    name        = "GPass 0.5.x (or newer)"
    importer    = True
    exporter    = True
    encryption  = True


    def __init__(self):
        base.DataHandler.__init__(self)


    def __getint(self, input):
        "Fetches an integer from the input"

        if len(input) < 4:
            raise base.FormatError

        return input[0] << 0 | input[1] << 8 | input[2] << 16 | input[3] << 24


    def __getstr(self, input):
        "Fetches a string from the input"

        length = self.__getint(input[:4])

        if len(input) < (4 + length):
            raise base.FormatError

        string = input[4:4 + length]

        if len(string) != length:
            raise base.FormatError

        return string


    def __mkint(self, input):
        "Creates a string-representation of an integer"

        string = b""

        for i in range(4):
            string += bytes([input >> i * 8 & 0xff])

        return string


    def __mkstr(self, input):
        "Makes a string suitable for inclusion in the data stream"

        return self.__mkint(len(input)) + input


    def __normstr(self, string):
        "Normalizes a string"

        string = re.sub(b"[\r\n]+", b" ", string)

        return string.decode()


    def __packint(self, input):
        "Packs an integer"

        if input == 0:
            return b"\x00"

        string = b""

        while input > 0:
            c   = input % 0x80
            input   = input // 0x80

            if input > 0:
                c |= 0x80

            string += bytes([c])

        return string


    def __packstr(self, input):
        "Packs a string"
        return self.__packint(len(input.encode())) + input.encode()


    def __unpackint(self, input):
        "Fetches a packed number from the input"

        value   = 0
        b   = 1

        for i in range(min(len(input), 6)):
            c = input[i]

            if c & 0x80:
                value   += b * (c & 0x7f)
                b   *= 0x80;

            else:
                value   += b * c

                return i + 1, value

        # if we didn't return in the for-loop, the input is invalid
        else:
            raise base.FormatError


    def __unpackstr(self, input):
        "Unpacks a string from the input"

        cut, length = self.__unpackint(input[:6])

        if len(input) < cut + length:
            raise base.FormatError

        return cut + length, input[cut:cut + length]


    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        plaintext   = b"GPassFile version 1.1.0"
        iter        = entrystore.iter_children(None)
        id      = 0
        foldermap   = {}

        while iter != None:
            id += 1

            path        = entrystore.get_path(iter).to_string()
            parentpath  = ':'.join(path.split(':')[:-1])

            if len(parentpath) > 0 and parentpath in foldermap:
                parentid = foldermap[parentpath]

            else:
                parentid = 0


            e = entrystore.get_entry(iter)

            if type(e) == entry.FolderEntry:
                foldermap[path] = id

            elif type(e) != entry.GenericEntry:
                e = e.convert_generic()


            entrydata   = b""
            entrydata   += self.__mkint(id)
            entrydata   += self.__mkint(parentid)
            entrydata   += self.__mkstr(type(e) == entry.FolderEntry and b"folder" or b"general")

            attrdata    = b""
            attrdata    += self.__packstr(e.name)
            attrdata    += self.__packstr(e.description)
            attrdata    += self.__packint(e.updated)
            attrdata    += self.__packint(e.updated)
            attrdata    += self.__packint(0)
            attrdata    += self.__packint(0)

            if type(e) == entry.GenericEntry:
                attrdata    += self.__packstr(e[entry.UsernameField] or "")
                attrdata    += self.__packstr(e[entry.PasswordField] or "")
                attrdata    += self.__packstr(e[entry.HostnameField] or "")

            entrydata   += self.__mkstr(attrdata)
            plaintext   += entrydata

            iter = entrystore.iter_traverse_next(iter)

        return encrypt(plaintext, password)


    def import_data(self, input, password):
        "Imports data from a data stream to an entrystore"

        plaintext = decrypt(input, password, b"GPassFile version 1.1.0")

        entrystore = data.EntryStore()
        foldermap = {}

        while len(plaintext) > 0:

            # parse data
            id      = self.__getint(plaintext[:4])
            plaintext   = plaintext[4:]

            parentid    = self.__getint(plaintext[:4])
            plaintext   = plaintext[4:]

            entrytype   = self.__getstr(plaintext)
            plaintext   = plaintext[4 + len(entrytype):]

            attrdata    = self.__getstr(plaintext)
            plaintext   = plaintext[4 + len(attrdata):]


            l, name     = self.__unpackstr(attrdata)
            attrdata    = attrdata[l:]

            l, desc     = self.__unpackstr(attrdata)
            attrdata    = attrdata[l:]

            l, ctime    = self.__unpackint(attrdata)
            attrdata    = attrdata[l:]

            l, mtime    = self.__unpackint(attrdata)
            attrdata    = attrdata[l:]

            l, expire   = self.__unpackint(attrdata)
            attrdata    = attrdata[l:]

            l, etime    = self.__unpackint(attrdata)
            attrdata    = attrdata[l:]

            if entrytype == b"general":
                l, username = self.__unpackstr(attrdata)
                attrdata    = attrdata[l:]

                l, password = self.__unpackstr(attrdata)
                attrdata    = attrdata[l:]

                l, hostname = self.__unpackstr(attrdata)
                attrdata    = attrdata[l:]

            else:
                username = password = hostname = b""


            # create entry
            if entrytype == b"general":
                e = entry.GenericEntry()

                e.name          = self.__normstr(name)
                e.description       = self.__normstr(desc)
                e.updated       = mtime

                e[entry.HostnameField]  = self.__normstr(hostname)
                e[entry.UsernameField]  = self.__normstr(username)
                e[entry.PasswordField]  = self.__normstr(password)

            elif entrytype == b"folder":
                e = entry.FolderEntry()

                e.name          = self.__normstr(name)
                e.description       = self.__normstr(desc)
                e.updated       = mtime

            else:
                continue


            # add entry to entrystore
            if parentid in foldermap:
                parent = foldermap[parentid]

            else:
                parent = None

            iter = entrystore.add_entry(e, parent)

            if type(e) == entry.FolderEntry:
                foldermap[id] = iter


        return entrystore

