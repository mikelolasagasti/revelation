#
# Revelation - a password manager for GNOME 2
# http://oss.codepoet.no/revelation/
# $Id$
#
# Module for handling PasswordSafe data
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

import locale, re, struct
from Cryptodome.Cipher import Blowfish
import Cryptodome.Random as Random


FIELDTYPE_NAME      = 0x00
FIELDTYPE_UUID      = 0x01
FIELDTYPE_GROUP     = 0x02
FIELDTYPE_TITLE     = 0x03
FIELDTYPE_USER      = 0x04
FIELDTYPE_NOTES     = 0x05
FIELDTYPE_PASSWORD  = 0x06
FIELDTYPE_END       = 0xff



# We need our own SHA1-implementation, because Password Safe does
# non-standard things we need to replicate. This implementation is
# written by J. Hallen and L. Creighton for the Pypy project, with
# slight modifications by Erik Grinaker.
class SHA:

    K = [
        0x5A827999,
        0x6ED9EBA1,
        0x8F1BBCDC,
        0xCA62C1D6
    ]


    def __init__(self, input = None):
        self.count = [0, 0]
        self.init()

        if input != None:
            self.update(input)


    def __bytelist2longBigEndian(self, list):
        imax = len(list)//4
        hl = [0] * imax

        j = 0
        i = 0
        while i < imax:
            b0 = list[j] << 24
            b1 = list[j+1] << 16
            b2 = list[j+2] << 8
            b3 = list[j+3]
            hl[i] = b0 | b1 | b2 | b3
            i = i+1
            j = j+4

        return hl


    def __long2bytesBigEndian(self, n, blocksize=0):
        s = b''
        pack = struct.pack
        while n > 0:
            s = pack('>I', n & 0xffffffff) + s
            n = n >> 32

        for i in range(len(s)):
            if s[i] != b'\000':
                break
        else:
            s = b'\000'
            i = 0

        s = s[i:]

        if blocksize > 0 and len(s) % blocksize:
            s = (blocksize - len(s) % blocksize) * b'\000' + s

        return s


    def __rotateLeft(self, x, n):
        return (x << n) | (x >> (32-n))


    def __transform(self, W):
        for t in range(16, 80):
            W.append(self.__rotateLeft(
                W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1) & 0xffffffff)

        A = self.H0
        B = self.H1
        C = self.H2
        D = self.H3
        E = self.H4

        for t in range(0, 20):
            TEMP = self.__rotateLeft(A, 5) + ((B & C) | ((~ B) & D)) + E + W[t] + self.K[0]
            E = D
            D = C
            C = self.__rotateLeft(B, 30) & 0xffffffff
            B = A
            A = TEMP & 0xffffffff

        for t in range(20, 40):
            TEMP = self.__rotateLeft(A, 5) + (B ^ C ^ D) + E + W[t] + self.K[1]
            E = D
            D = C
            C = self.__rotateLeft(B, 30) & 0xffffffff
            B = A
            A = TEMP & 0xffffffff

        for t in range(40, 60):
            TEMP = self.__rotateLeft(A, 5) + ((B & C) | (B & D) | (C & D)) + E + W[t] + self.K[2]
            E = D
            D = C
            C = self.__rotateLeft(B, 30) & 0xffffffff
            B = A
            A = TEMP & 0xffffffff

        for t in range(60, 80):
            TEMP = self.__rotateLeft(A, 5) + (B ^ C ^ D)  + E + W[t] + self.K[3]
            E = D
            D = C
            C = self.__rotateLeft(B, 30) & 0xffffffff
            B = A
            A = TEMP & 0xffffffff


        self.H0 = (self.H0 + A) & 0xffffffff
        self.H1 = (self.H1 + B) & 0xffffffff
        self.H2 = (self.H2 + C) & 0xffffffff
        self.H3 = (self.H3 + D) & 0xffffffff
        self.H4 = (self.H4 + E) & 0xffffffff


    def digest(self):
        H0 = self.H0
        H1 = self.H1
        H2 = self.H2
        H3 = self.H3
        H4 = self.H4
        input = [] + self.input
        count = [] + self.count

        index = (self.count[1] >> 3) & 0x3f

        if index < 56:
            padLen = 56 - index
        else:
            padLen = 120 - index

        padding = [128] + [0] * 63
        self.update(padding[:padLen])
        bits = self.__bytelist2longBigEndian(self.input[:56]) + count

        self.__transform(bits)

        digest = self.__long2bytesBigEndian(self.H0, 4) + \
                self.__long2bytesBigEndian(self.H1, 4) + \
                self.__long2bytesBigEndian(self.H2, 4) + \
                self.__long2bytesBigEndian(self.H3, 4) + \
                self.__long2bytesBigEndian(self.H4, 4)

        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.input = input
        self.count = count

        return digest


    def hexdigest(self):
        return ''.join(['%02x' % ord(c) for c in self.digest()])


    def init(self, H0 = 0x67452301, H1 = 0xEFCDAB89, H2 = 0x98BADCFE, H3 = 0x10325476, H4 = 0xC3D2E1F0):
        self.length = 0
        self.input = []

        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4


    def update(self, inBuf):
        leninBuf = len(inBuf)

        index = (self.count[1] >> 3) & 0x3F

        self.count[1] = self.count[1] + (leninBuf << 3)
        if self.count[1] < (leninBuf << 3):
            self.count[0] = self.count[0] + 1
        self.count[0] = self.count[0] + (leninBuf >> 29)

        partLen = 64 - index

        if leninBuf >= partLen:
            self.input[index:] = list(inBuf[:partLen])
            self.__transform(self.__bytelist2longBigEndian(self.input))
            i = partLen
            while i + 63 < leninBuf:
                self.__transform(self.__bytelist2longBigEndian(list(inBuf[i:i+64])))
                i = i + 64
            else:
                self.input = list(inBuf[i:leninBuf])
        else:
            i = 0
            self.input = self.input + list(inBuf)


# misc functions common to both datahandlers
def decrypt(key, ciphertext, iv = None):
    "Decrypts data"

    if len(ciphertext) % 8 != 0:
        raise base.FormatError

    cipher      = Blowfish.new(key, Blowfish.MODE_ECB)
    cbc     = iv
    plaintext   = b""

    for cipherblock in [ ciphertext[i * 8 : (i + 1) * 8] for i in range(len(ciphertext) // 8) ]:

        plainblock = decrypt_block(cipher, cipherblock)

        if cbc != None:
            plainblock = bytes([ plainblock[i] ^ cbc[i] for i in range(len(plainblock)) ])
            cbc = cipherblock

        plaintext += plainblock

    return plaintext


def decrypt_block(cipher, block):
    "Decrypts a block with the given cipher"

    block = bytes((block[3], block[2], block[1], block[0], block[7], block[6], block[5], block[4]))
    block = cipher.decrypt(block)
    block = bytes((block[3], block[2], block[1], block[0], block[7], block[6], block[5], block[4]))

    return block


def encrypt(key, plaintext, iv = None):
    "Encrypts data"

    if len(plaintext) % 8 != 0:
        raise base.FormatError

    cipher      = Blowfish.new(key, Blowfish.MODE_ECB)
    cbc     = iv
    ciphertext  = b""

    for plainblock in [ plaintext[i * 8 : (i + 1) * 8] for i in range(len(plaintext) // 8) ]:

        if cbc != None:
            plainblock = bytes([ plainblock[i] ^ cbc[i] for i in range(len(plainblock)) ])

        cipherblock = encrypt_block(cipher, plainblock)
        ciphertext += cipherblock

        if cbc != None:
            cbc = cipherblock


    return ciphertext


def encrypt_block(cipher, block):
    "Encrypts a block with the given cipher"

    block = bytes((block[3], block[2], block[1], block[0], block[7], block[6], block[5], block[4]))
    block = cipher.encrypt(block)
    block = bytes((block[3], block[2], block[1], block[0], block[7], block[6], block[5], block[4]))

    return block


def generate_testhash(password, random):
    "Generates a testhash based on a password and a random string"

    key = SHA(random + b"\x00\x00" + password.encode()).digest()
    cipher  = Blowfish.new(key, Blowfish.MODE_ECB)

    for i in range(1000):
        random = encrypt_block(cipher, random)

    h = SHA()
    h.init(0, 0, 0, 0, 0)
    h.update(random)
    h.update(b"\x00\x00")
    testhash = h.digest()

    return testhash



def create_field(value, type = FIELDTYPE_NAME):
    "Creates a field"
    if isinstance(value, str):
        value = value.encode()

    field = struct.pack("ii", len(value), type) + value

    if len(value) == 0 or len(value) % 8 != 0:
        field += b"\x00" * (8 - len(value) % 8)

    return field


def normalize_field(field):
    "Normalizes a field value"

    enc = locale.getpreferredencoding()

    field = field.replace(b"\x00", b"")
    field = re.sub(b"\s+", b" ", field)
    field = field.strip()
    field = field.decode(enc, "replace")

    return field


def parse_field_header(header):
    "Parses field data, returns the length and type"

    if len(header) < 8:
        raise base.FormatError

    length, type = struct.unpack("ii", header[:8])

    if length == 0 or length % 8 != 0:
        length += 8 - length % 8

    return length, type



class PasswordSafe1(base.DataHandler):
    "Data handler for PasswordSafe 1.x data"

    name        = "Password Safe 1.x"
    importer    = True
    exporter    = True
    encryption  = True


    def __init__(self):
        base.DataHandler.__init__(self)


    def check(self, input):
        "Checks if the data is valid"

        if input is None:
            raise base.FormatError

        if len(input) < 56:
            raise base.FormatError

        if (len(input) - 56) % 8 != 0:
            raise base.FormatError


    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        # serialize data
        enc = locale.getpreferredencoding()
        db = b""
        iter = entrystore.iter_children(None)

        while iter is not None:
            e = entrystore.get_entry(iter)

            if type(e) != entry.FolderEntry:
                e = e.convert_generic()

                edata = b""
                edata += create_field(e.name.encode(enc, "replace") + b"\xAD" + e[entry.UsernameField].encode("iso-8859-1"))
                edata += create_field(e[entry.PasswordField].encode(enc, "replace"))
                edata += create_field(e.description.encode(enc, "replace"))

                db += edata

            iter = entrystore.iter_traverse_next(iter)


        # encrypt data
        rand = Random.new()
        random = rand.read(8)
        salt   = rand.read(20)
        iv     = rand.read(8)

        testhash    = generate_testhash(password, random)
        ciphertext  = encrypt(SHA(password.encode() + salt).digest(), db, iv)

        return random + testhash + salt + iv + ciphertext


    def import_data(self, input, password):
        "Imports data into an entrystore"

        # read header and test password
        if password is None:
            raise base.PasswordError

        random      = input[0:8]
        testhash    = input[8:28]
        salt        = input[28:48]
        iv      = input[48:56]

        if testhash != generate_testhash(password, random):
            raise base.PasswordError

        # load data
        db      = decrypt(SHA(password.encode() + salt).digest(), input[56:], iv)
        entrystore  = data.EntryStore()

        while len(db) > 0:

            dbentry = { "name" : "", "username" : "", "password" : "", "note" : "" }

            for f in ( "name", "password", "note" ):
                flen, ftype = parse_field_header(db[:8])
                value = db[8:8 + flen]

                if f == "name" and b"\xAD" in value:
                    value, dbentry["username"] = value.split(b"\xAD", 1)

                dbentry[f] = value
                db = db[8 + flen:]

            e = entry.GenericEntry()
            e.name          = normalize_field(dbentry["name"])
            e.description       = normalize_field(dbentry["note"])
            e[entry.UsernameField]  = normalize_field(dbentry["username"])
            e[entry.PasswordField]  = normalize_field(dbentry["password"])

            entrystore.add_entry(e)

        return entrystore



class PasswordSafe2(base.DataHandler):
    "Data handler for PasswordSafe 2.x data"

    name        = "Password Safe 2.x"
    importer    = True
    exporter    = True
    encryption  = True


    def __init__(self):
        base.DataHandler.__init__(self)


    def __get_group(self, entrystore, iter):
        "Returns the group path for an iter"

        path = []

        iter = entrystore.iter_parent(iter)

        while iter is not None:
            path.append(entrystore.get_entry(iter).name)
            iter = entrystore.iter_parent(iter)

        path.reverse()

        return ".".join(path)


    def __setup_group(self, entrystore, groupmap, group):
        "Sets up a group folder, or returns an existing one"

        if group in ( None, "" ):
            return None

        if group in groupmap:
            return groupmap[group]

        if "." in group:
            parent, groupname = group.rsplit(".", 1)
            parentiter = self.__setup_group(entrystore, groupmap, parent)

        else:
            groupname = group
            parentiter = None

        e = entry.FolderEntry()
        e.name = groupname

        iter = entrystore.add_entry(e, parentiter)
        groupmap[group] = iter

        return iter


    def check(self, input):
        "Checks if the data is valid"

        if input is None:
            raise base.FormatError

        if len(input) < 56:
            raise base.FormatError

        if (len(input) - 56) % 8 != 0:
            raise base.FormatError


    def export_data(self, entrystore, password):
        "Exports data from an entrystore"

        # set up magic entry at start of database
        db = b""
        db += b"\x48\x00\x00\x00\x00\x00\x00\x00"
        db += b" !!!Version 2 File Format!!! Please upgrade to PasswordSafe 2.0 or later"
        db += b"\x03\x00\x00\x00\x06\x00\x00\x00"
        db += b"2.0\x00\x00\x00\x00\x00"
        db += b"\x00\x00\x00\x00\x06\x00\x00\x00"
        db += b"\x00\x00\x00\x00\x00\x00\x00\x00"

        # serialize data
        uuids = []
        iter = entrystore.iter_children(None)

        enc = locale.getpreferredencoding()
        rand = Random.new()

        while iter is not None:
            e = entrystore.get_entry(iter)

            if type(e) != entry.FolderEntry:
                e = e.convert_generic()

                uuid = rand.read(16)

                while uuid in uuids:
                    uuid = rand.read(16)

                edata = b""
                edata += create_field(uuid, FIELDTYPE_UUID)
                edata += create_field(self.__get_group(entrystore, iter), FIELDTYPE_GROUP)
                edata += create_field(e.name.encode(enc, "replace"), FIELDTYPE_TITLE)
                s = e[entry.UsernameField]
                if s is None:
                    s = ""
                edata += create_field(s.encode(enc, "replace"), FIELDTYPE_USER)
                edata += create_field(e[entry.PasswordField].encode(enc, "replace"), FIELDTYPE_PASSWORD)
                edata += create_field(e.description.encode(enc, "replace"), FIELDTYPE_NOTES)
                edata += create_field("", FIELDTYPE_END)

                db += edata

            iter = entrystore.iter_traverse_next(iter)


        # encrypt data
        rand = Random.new()
        random  = rand.read(8)
        salt    = rand.read(20)
        iv      = rand.read(8)

        testhash    = generate_testhash(password, random)
        ciphertext  = encrypt(SHA(password.encode() + salt).digest(), db, iv)

        return random + testhash + salt + iv + ciphertext


    def import_data(self, input, password):
        "Imports data into an entrystore"

        # read header and test password
        if password is None:
            raise base.PasswordError

        random      = input[0:8]
        testhash    = input[8:28]
        salt        = input[28:48]
        iv      = input[48:56]

        if testhash != generate_testhash(password, random):
            raise base.PasswordError

        # load data
        db      = decrypt(SHA(password.encode() + salt).digest(), input[56:], iv)
        entrystore  = data.EntryStore()


        # read magic entry
        for f in "magic", "version", "prefs":
            flen, ftype = parse_field_header(db)
            value = db[8:8 + flen]

            if f == "magic" and value != b" !!!Version 2 File Format!!! Please upgrade to PasswordSafe 2.0 or later":
                raise base.FormatError

            db = db[8 + flen:]

        # import entries
        e = entry.GenericEntry()
        group = None
        groupmap = {}

        while len(db) > 0:
            flen, ftype = parse_field_header(db)
            value = normalize_field(db[8:8 + flen])

            if ftype == FIELDTYPE_NAME:
                if b"\xAD" not in value:
                    e.name = value

                else:
                    n, u = value.split(b"\xAD", 1)

                    e.name = normalize_field(n)
                    e[entry.UsernameField] = normalize_field(u)

            elif ftype == FIELDTYPE_TITLE:
                e.name = value

            elif ftype == FIELDTYPE_USER:
                e[entry.UsernameField] = value

            elif ftype == FIELDTYPE_PASSWORD:
                e[entry.PasswordField] = value

            elif ftype == FIELDTYPE_NOTES:
                e.description = value

            elif ftype == FIELDTYPE_UUID:
                pass

            elif ftype == FIELDTYPE_GROUP:
                group = value

            elif ftype == FIELDTYPE_END:
                if group not in ( None, "" ):
                    parent = self.__setup_group(entrystore, groupmap, group)

                else:
                    parent = None

                entrystore.add_entry(e, parent)

                e = entry.GenericEntry()
                group = None

            else:
                pass

            db = db[8 + flen:]

        return entrystore



class MyPasswordSafe(PasswordSafe2):
    "Data handler for MyPasswordSafe data"

    name        = "MyPasswordSafe"
    importer    = True
    exporter    = True
    encryption  = True



class MyPasswordSafeOld(PasswordSafe1):
    "Data handler for old MyPasswordSafe data"

    name        = "MyPasswordSafe (old format)"
    importer    = True
    exporter    = True
    encryption  = True



class PasswordGorilla(PasswordSafe2):
    "Data handler for Password Gorilla data"

    name        = "Password Gorilla"
    importer    = True
    exporter    = True
    encryption  = True

