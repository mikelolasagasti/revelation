"""
Implements the LUKS (Linux Unified Key Setup) Version 1.0
on disk specification inside a file.

http://luks.endorphin.org/

LUKS offers:
    * compatiblity via standardization,
    * secure against low entropy attacks,
    * support for multiple keys,
    * effective passphrase revocation,

This module is compatible with dm-crypt and cryptsetup tools for the Linux
kernel, as long as hashSpec="sha1" is used. Loopback files or partitions created
with the linux kernel can be decrypted using this module.  FreeOTFE
(http://www.freeotfe.org/) should provide support for reading and writing on
Windows.

This module has one class LuksFile.

Loading a LUKS disk image (use both, one after another):
- load_from_file(file)
- open_any_key(password)

Creating a new LUKS disk image (use both):
- create(file, cipherName, cipherMode, hashSpec, masterSize, stripes)
- set_key(0, password, iterations)

Once a file is unlocked (either because it was just created or
open_any_key() returned True), you can perform the key operations:
- enabled_key_count()
- key_information(keyIndex)
- set_key(keyIndex, password, iterations)
- delete_key(keyIndex)

Once a file is unlocked, you can perform data encryption/decryption with
- data_length()
- encrypt_data(offset, data)
- decrypt_data(offset, length)
- truncate(length)

Finally, to close the file:
- close()

Copyright 2006 John Lenz <lenz@cs.wisc.edu>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA

http://www.gnu.org/copyleft/gpl.html
"""

import os, math, struct, stat, sha, md5

from Crypto.Util.randpool import RandomPool
from Crypto.Cipher import *
from Crypto.Hash import *
import PBKDFv2, AfSplitter

class LuksFile:
	"""Implements the LUKS (Linux Unified Key Setup) Version 1.0 http://luks.endorphin.org/"""

	LUKS_FORMAT = ">6sH32s32s32sII20s32sI40s"
	LUKS_MAGIC = "LUKS\xba\xbe"

	LUKS_KEY_DISABLED = 0x0000DEAD
	LUKS_KEY_ENABLED = 0x00AC71F3

	SECTOR_SIZE = 512.0

	KEY_STRIPES = 4000
	SALT_SIZE = 32
	DIGEST_SIZE = 20

	def __init__(self):
		self.file = None
		self.masterKey = None
		self.ivGen = None

	# Read the header from the file descriptor
	def load_from_file(self, file):
		"""Initialize this LuksFile class from the file.

		The file parameter should be an object implementing the File Object API
        	This function will error if the file is not a LUKS partition (the LUKS_MAGIC does not match)
		"""

		if self.file != None:
			raise "This LuksFile has already been initialized"

		# Read the main parameters
		self.file = file
		self.file.seek(0)

		self.magic, \
		self.version, \
		cipherName, \
		cipherMode, \
		hashSpec, \
		self.payloadOffset, \
		self.keyBytes, \
		self.mkDigest, \
		self.mkDigestSalt, \
		self.mkDigestIterations, \
		self.uuid = \
		struct.unpack(self.LUKS_FORMAT, self.file.read(208))

		# check magic
		if self.magic != self.LUKS_MAGIC:
			self.file = None
			raise "%s is not a LUKS data file" % filename

		# Check the hash and cipher
		self.hashSpec = hashSpec.strip(" \x00")
		self.hash = self._check_hash(self.hashSpec)
		self._check_cipher(cipherName.strip(" \x00"), cipherMode.strip(" \x00"))
		
		# Load the key information
		self.keys = [None] * 8
		for i in range(0, 8):
			self.keys[i] = self._key_block()
			self.keys[i].load_from_str(self.file.read(48))

		# set the digest to be the correct size
		self.mkDigest = self.mkDigest[:self.hash.digest_size]

		self.masterKey = None

	# Generate a new header
	def create(self, file, cipherName, cipherMode, hashSpec, masterSize, stripes):
		"""Initializes the file class passed in with the LUKS header

        	Parameters
		   cipherName: aes, cast5, blowfish
		   cipherMode: cbc-plain, cbc-essiv:<hash>
		   hashSpec: sha1, sha256, md5, ripemd160
		   masterSize: length of the master key in bytes (must match cipher)
		   stripes: number of stripes when Af Splitting keys

		For compatibility with the Linux kernel dm-crypt, hashSpec must equal "sha1"

		cbc-plain uses the sector number as the IV.  This has a weakness: an attacker
		may be able to detect the existance of watermarked files.
		cbc-essiv:<hash> protects against the weakness in cbc-plain, but is 
		slightly slower. The digest size of the hash function passed to cbc-essiv
		must match the key size of the cipher.  
		aes-cbc-essiv:sha256 works, while aes-cbc-essiv:sha1 does not

		For more information about the details of the attacks and risk assesment, see
		http://clemens.endorphin.org/LinuxHDEncSettings
		"""

		if self.file != None:
			raise "This LuksFile has already been initialized"

		self._check_cipher(cipherName, cipherMode)

		self.magic = self.LUKS_MAGIC
		self.version = 1
		self.mkDigestIterations = 10
		self.keyBytes = masterSize
		self.hashSpec = hashSpec
		self.hash = self._check_hash(hashSpec)

		rand = RandomPool(self.SALT_SIZE + 16 + masterSize)

		# Generate the salt
		self.mkDigestSalt = rand.get_bytes(self.SALT_SIZE)

		# Generate a random master key
		self.masterKey = rand.get_bytes(self.keyBytes)
		self.ivGen.set_key(self.masterKey)

		# generate the master key digest
		pbkdf = PBKDFv2.PBKDFv2()
		self.mkDigest = pbkdf.makeKey(self.masterKey, self.mkDigestSalt, self.mkDigestIterations, self.hash.digest_size, self.hash)

		# init the key information
		currentSector = math.ceil(592.0 / self.SECTOR_SIZE)
		alignSectors = 4096 / self.SECTOR_SIZE
		blocksPerStripe = math.ceil(float(self.keyBytes * stripes) / self.SECTOR_SIZE)

		self.keys = [None] * 8
		for i in range(0, 8):
			if currentSector % alignSectors > 0:
				currentSector += alignSectors - currentSector % alignSectors
			self.keys[i] = self._key_block()
			self.keys[i].create(currentSector, stripes, self.LUKS_KEY_DISABLED)
			currentSector += blocksPerStripe

		# Set the data offset
		if currentSector % alignSectors > 0:
			currentSector += alignSectors - currentSector % alignSectors
		self.payloadOffset = currentSector

		# Generate a UUID for this file
		self._uuidgen(rand)

		# Create a new file, and save the header into it
		self.file = file
		self._save_header()

		# Write FF into all the key slots
		FFData = "\xFF" * int(self.SECTOR_SIZE)
		for i in range(0, 8):
			self.file.seek(int(self.keys[i].keyMaterialOffset))
			for sector in range(0, int(blocksPerStripe)):
				self.file.write(FFData)

		# Flush the file to disk
		try:
			self.file.flush()
			os.fsync(self.file.fileno())
		except:
			# We might get an error because self.file.fileno() does not exist on StringIO
			pass

	def set_key(self, keyIndex, password, iterations, checkMinStripes=0):
		"""Sets the key block at keyIndex using password

		Sets the key block at keyIndex using password, hashed iterations
		times using PBKDFv2 (RFC2104).  This LuksFile must be unlocked by
		calling open_any_key() before calling this function.
		checkMinStripes is used to detect basic header manipulation, since
		the number of stripes for the key is set by create(), before
		we write a password to disk we make sure the key is not weak because
		of a small number of stripes.

		This function will raise an error if the key is already enabled.
		"""

		# Some checks
		if self.masterKey == None:
			raise "A key has not been unlocked.  Call open_any_key() first."

		if keyIndex < 0 or keyIndex > 7:
			raise "keyIndex out of range"

		key = self.keys[keyIndex]
		if key.active != self.LUKS_KEY_DISABLED:
			raise "Key is active.  Delete the key and try again"

		if checkMinStripes == 0: checkMinStripes = self.KEY_STRIPES
		if key.stripes < checkMinStripes:
			raise "Key section %i contains too few stripes.  Header manipulation?" % keyIndex

		key.passwordIterations = iterations

		# Generate a random salt for this key
		rand = RandomPool(self.SALT_SIZE)
		key.passwordSalt = rand.get_bytes(self.SALT_SIZE)

		# Hash the key using PBKDFv2
		pbkdf = PBKDFv2.PBKDFv2()
		derived_key = pbkdf.makeKey(password, key.passwordSalt, key.passwordIterations, self.keyBytes, self.hash)

		# Split the key into key.stripes
		AfKey = AfSplitter.AFSplit(self.masterKey, key.stripes, self.hash)

		AfKeySize = len(AfKey)
		if AfKeySize != key.stripes * self.keyBytes:
			raise "ERROR: AFSplit did not return the correct length of key"

		# Set the key for IV generation
		self.ivGen.set_key(derived_key)

		# Encrypt the splitted key using the hashed password
		AfSectors = int(math.ceil(float(AfKeySize) / self.SECTOR_SIZE))
		for sector in range(0, AfSectors):
			self._encrypt_sector(derived_key, key.keyMaterialOffset + sector, sector, \
                               AfKey[int(sector*self.SECTOR_SIZE):int((sector+1)*self.SECTOR_SIZE)])

		key.active = self.LUKS_KEY_ENABLED

		# Reset the key used for to IV generation in data mode
		self.ivGen.set_key(self.masterKey)

		self._save_header()

	def open_key(self, keyIndex, password):
		"""Open a specific keyIndex using password.  Returns True on success"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		if keyIndex < 0 or keyIndex > 7:
			raise "keyIndex is out of range"

		key = self.keys[keyIndex]

		if key.active != self.LUKS_KEY_ENABLED:
			return False

		# Hash the password using PBKDFv2
		pbkdf = PBKDFv2.PBKDFv2()
		derived_key = pbkdf.makeKey(password, key.passwordSalt, key.passwordIterations, self.keyBytes, self.hash)

		# Setup the IV generation to use this key
		self.ivGen.set_key(derived_key)

		# Decrypt the master key data using the hashed password
		AfKeySize = key.stripes * self.keyBytes
		AfSectors = int(math.ceil(float(AfKeySize) / self.SECTOR_SIZE))
		AfKey = ""
		for sector in range(0, AfSectors):
			AfKey += self._decrypt_sector(derived_key, key.keyMaterialOffset + sector, sector)
		AfKey = AfKey[0:AfKeySize]

		# Merge the decrypted master key
		masterKey = AfSplitter.AFMerge(AfKey, key.stripes, self.hash)

		# Check if the password was the correct one, by checking the master key digest
		checkDigest = pbkdf.makeKey(masterKey, self.mkDigestSalt, self.mkDigestIterations, self.hash.digest_size, self.hash)
		
		# Since the header only stores DIGEST_SIZE (which is smaller than sha256 digest size)
		#   trim the digest to DIGEST_SIZE
		checkDigest = checkDigest[:self.DIGEST_SIZE]

		if checkDigest != self.mkDigest:
			return False

		self.masterKey = masterKey
		self.ivGen.set_key(self.masterKey)
		return True
		

	def open_any_key(self, password):
		"""Try to open any enabled key using the provided password.  Returns index number on success, or None"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		for i in range(0, 8):
			if self.open_key(i, password):
				return i
		return None

	def enabled_key_count(self):
		"""Returns the number of enabled key slots"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		cnt = 0
		for i in range(0, 8):
			if self.keys[i].active == self.LUKS_KEY_ENABLED:
				cnt += 1
		return cnt

	def key_information(self, keyIndex):
		"""Returns a tuple of information about the key at keyIndex (enabled, iterations, stripes)"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		if keyIndex < 0 or keyIndex > 7:
			raise "keyIndex out of range"

		key = self.keys[keyIndex]
		active = (key.active == self.LUKS_KEY_ENABLED)
		return (active, key.passwordIterations, key.stripes)

	def delete_key(self, keyIndex):
		"""Delete the key located in slot keyIndex.  WARNING! This is NOT a secure delete

		Warning! If keyIndex is the last enabled key, the data will become unrecoverable

		This function will not securely delete the key.  Because this class is designed
		for reading and writing to a file, there is no guarante that writing over the data
		inside the file will destroy it.  If you have a key leaked, you need to investigate
		other methods of securely destroying data, including destroying the entire file system
		and disk this file was located on, and any backups of this file that were created
		(depending on your needs).  The good news is, because of the way LUKS encrypts the
		master key, only one bit in the master key needs to be destoryed.  But the same bit
		needs to be destroyed in all copies, including (possibly) the journal, bad remapped
		blocks on the disk, etc.

		If you would like to continue using this encrypted file, you need to set_key() a new
		key, delete_key() the leaked key, and then copy the file into a new file on a
		different disk and filesystem.  This class writes "FF" to the key location during
		delete_key(), so during the copy the new disk will just get "FF" in the key location,
		which will be unrecoverable on the new disk.
		"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		if keyIndex < 0 or keyIndex > 7:
			raise "keyIndex out of range"

		key = self.keys[keyIndex]

		# Start and end offset of the key material
		startOffset = key.keyMaterialOffset
		endOffset = startOffset + int(math.ceil((self.keyBytes * key.stripes) / self.SECTOR_SIZE))

		# Just write "FF" into the locations
		for i in range(startOffset, endOffset):
			self.file.seek(int(i * self.SECTOR_SIZE))
			self.file.write("\xFF" * int(self.SECTOR_SIZE))

		try:
			self.file.flush()
			os.fsync(self.file.fileno())
		except:
			# We might get an error because self.file.fileno() does not exist on StringIO
			pass
		
		key.active = self.LUKS_KEY_DISABLED
		key.passwordIterations = 0
		key.passwordSalt = ''

		self._save_header()

	def close(self):
		"""Close the underlying file descriptor, and discard the cached master key used for decryption"""

		if self.ivGen != None:
			self.ivGen.set_key("")
		if self.file != None:
			self.file.close()

		self.file = None
		self.masterKey = None
		self.ivGen = None

	def data_length(self):
		"""Returns the total data length"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		# Seek to the end of the file, and use tell()
		self.file.seek(0, 2)
		fLen = self.file.tell()
		return fLen - int(self.payloadOffset * self.SECTOR_SIZE)

	def truncate(self, length):
		"""Truncate the file so that the data is maximum of length in size"""

		if self.file == None:
			raise "LuksFile has not been initialized"

		if length % self.SECTOR_SIZE != 0:
			raise "length must be a multiple of %s" % self.SECTOR_SIZE

		if length < 0:
			raise "length must be positive"

		self.file.truncate(int(self.payloadOffset * self.SECTOR_SIZE) + length)

	def encrypt_data(self, offset, data):
		"""Encrypt data into the file.

		Offset is a zero indexed location in the data to write.
		Both offset and len(data) must be multiples of 512.
		"""

		# Check conditions
		if self.masterKey == None:
			raise "A key has not been unlocked.  Call open_any_key() first."

		if offset % self.SECTOR_SIZE != 0:
			raise "offset must be a multiple of %s" % self.SECTOR_SIZE

		dataLen = len(data)
		if dataLen % self.SECTOR_SIZE != 0:
			raise "data length must be a multiple of %s" % self.SECTOR_SIZE

		# Encrypt all the data
		startSector = int(offset / self.SECTOR_SIZE)
		endSector = int((offset + dataLen) / self.SECTOR_SIZE)
		for sector in range(startSector, endSector):
			dslice_sector = sector - startSector
			dslice = data[int(dslice_sector * self.SECTOR_SIZE):int((dslice_sector+1)*self.SECTOR_SIZE)]
			self._encrypt_sector(self.masterKey, self.payloadOffset + sector, sector, dslice)

	def decrypt_data(self, offset, length):
		"""Decrypt data from the file.

		Offset is a zero indexed location into the data, and length is
		the ammout of data to return.  offset and length can be any value,
		but multiples of 512 are the most efficient.
		"""
		
		if self.masterKey == None:
			raise "A key has not been unlocked.  Call open_any_key() first."

		frontPad = int(offset % self.SECTOR_SIZE)
		startSector = int(math.floor(offset / self.SECTOR_SIZE))
		endSector = int(math.ceil((offset + length) / self.SECTOR_SIZE))
		ret = ""
		for sector in range(startSector, endSector):
			ret += self._decrypt_sector(self.masterKey, self.payloadOffset + sector, sector)

		return ret[frontPad:frontPad+length]

	##### Private functions

	class _key_block:
		"""Internal class, used to store the key information about each key."""

		LUKS_KEY_FORMAT = ">II32sII"

		def load_from_str(self,str):
			"""Unpack the key information from a string"""
			self.active, \
			self.passwordIterations, \
			self.passwordSalt, \
			self.keyMaterialOffset, \
			self.stripes =  \
			struct.unpack(self.LUKS_KEY_FORMAT,str)

		def create(self,offset, stripes, disabled):
			"""Create a new set of key information.  Called from LuksFile.create()"""
			self.active = disabled
			self.passwordIterations = 0
			self.passwordSalt = ''
			self.keyMaterialOffset = offset
			self.stripes = stripes

		def save(self):
			"""Pack the key information into a string"""
			return struct.pack(self.LUKS_KEY_FORMAT, self.active, self.passwordIterations, \
                                    self.passwordSalt, self.keyMaterialOffset, self.stripes)

	def _check_hash(self, hashSpec):
		"""Internal function to check for a valid hash specification"""
		if hashSpec == "sha1":
			hash = sha
		elif hashSpec == "sha256":
			hash = SHA256
		elif hashSpec == "md5":
			hash = md5
		elif hashSpec == "ripemd160":
			hash = RIPEMD
		else:
			raise "invalid hash %s" % hashSpec

		return hash

	class _plain_iv_gen:
		"""Internal class to represent cbc-plain cipherMode"""

		def set_key(self, key):
			# plain IV generation does not use the key in any way
			pass

		def generate(self, sectorOffset, size):
			istr = struct.pack("<I", sectorOffset)
			return istr + "\x00" * (size - 4)

	class _essiv_gen:
		"""Internal class to represent cbc-essiv:<hash> cipherMode"""

		# essiv mode is defined by 
		# SALT=Hash(KEY)
		# IV=E(SALT,sectornumber)
		def __init__(self, str, cipher, luksParent):
			self.hashSpec = str[1:]
			self.hash = luksParent._check_hash(self.hashSpec)
			self.cipher = cipher

		def set_key(self, key):
			h = self.hash.new(key)
			self.salt = h.digest()
			self.encr = self.cipher.new(self.salt, self.cipher.MODE_ECB)

		def generate(self, sectorOffset, size):
			istr = struct.pack("<I", sectorOffset) + "\x00" * (size - 4)
			return self.encr.encrypt(istr)

	def _check_cipher(self, cipherName, cipherMode):
		"""Internal function to check for a valid cipherName and cipherMode"""
		if cipherName == "aes":
			self.cipher = AES
		elif cipherName == "cast5":
			self.cipher = CAST
		elif cipherName == "blowfish":
			self.cipher = Blowfish
		else:
			raise "invalid cipher %s" % cipherName

		# All supported ciphers are block ciphers, so modes are the same (CBC)
		self.mode = self.cipher.MODE_CBC

		if cipherMode == "cbc-plain":
			self.ivGen = self._plain_iv_gen()
		elif cipherMode[:10] == "cbc-essiv:":
			self.ivGen = self._essiv_gen(cipherMode[9:], self.cipher, self)
		else:
			raise "invalid cipher mode %s" % cipherName

		self.cipherName = cipherName
		self.cipherMode = cipherMode

	def _uuidgen(self, rand):
		"""Internal function to generate a UUID"""

		# I copied this code (and slightly modified it) from a module written
		# by Denys Duchier http://ofxsuite.berlios.de/uuid.py  (which is under the GPL)

		buf = rand.get_bytes(16)
		low,mid,hi_and_version,seq,node = struct.unpack(">IHHH6s",buf)
		seq = (seq & 0x3FFF) | 0x8000
		hi_and_version = (hi_and_version & 0x0FFF) | 0x4000
		uuid = struct.pack(">IHHH6s",low,mid,hi_and_version,seq,node)
		low,mid,hi,seq,b5,b4,b3,b2,b1,b0 = struct.unpack(">IHHHBBBBBB",uuid)
		self.uuid =  "%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x" % (low,mid,hi,seq>>8,seq&0xFF,b5,b4,b3,b2,b1,b0)

	def _save_header(self):
		"""Internal function to save the header info into the file"""

		str=struct.pack(self.LUKS_FORMAT, self.magic, self.version, self.cipherName, self.cipherMode, self.hashSpec, \
                         self.payloadOffset, self.keyBytes, self.mkDigest, self.mkDigestSalt, self.mkDigestIterations, self.uuid)
		self.file.seek(0)
		self.file.write(str)

		for i in range(0, 8):
			self.file.write(self.keys[i].save())

		try:
			self.file.flush()
			os.fsync(self.file.fileno())
		except:
			# We might get an error because self.file.fileno() does not exist on StringIO
			pass

	def _encrypt_sector(self, key, sector, sectorOffset, data):
		"""Internal function to encrypt a single sector"""

		if len(data) > self.SECTOR_SIZE:
			raise "_encrypt_page only accepts data of size <= %i" % self.SECTOR_SIZE

		# Encrypt the data using the cipher, iv generation, and mode
		IV = self.ivGen.generate(sectorOffset, self.cipher.block_size)
		cipher = self.cipher.new(key, self.mode, IV)
		encrData = cipher.encrypt(data)

		# Write the encrypted data to disk
		self.file.seek(int(sector * self.SECTOR_SIZE))
		self.file.write(encrData)

	def _decrypt_sector(self, key, sector, sectorOffset):
		"""Internal function to decrypt a single sector"""

		# Read the ciphertext from disk
		self.file.seek(int(sector * self.SECTOR_SIZE))
		encrData = self.file.read(int(self.SECTOR_SIZE))

		# Decrypt the data using cipher, iv generation, and mode
		IV = self.ivGen.generate(sectorOffset, self.cipher.block_size)
		cipher = self.cipher.new(key, self.mode, IV)
		return cipher.decrypt(encrData)

# The following was copied from the reference implementation of LUKS in cryptsetup-luks-1.0.1 from
# http://luks.endorphin.org/dm-crypt

#define LUKS_CIPHERNAME_L 32
#define LUKS_CIPHERMODE_L 32
#define LUKS_HASHSPEC_L 32
#define LUKS_DIGESTSIZE 20 // since SHA1
#define LUKS_HMACSIZE 32
#define LUKS_SALTSIZE 32
#define LUKS_NUMKEYS 8
#define LUKS_MAGIC_L 6

#/* Actually we need only 37, but we don't want struct autoaligning to kick in */
#define UUID_STRING_L 40

#struct luks_phdr {
#	char		magic[LUKS_MAGIC_L];
#	uint16_t	version;
#	char		cipherName[LUKS_CIPHERNAME_L];
#	char		cipherMode[LUKS_CIPHERMODE_L];
#	char            hashSpec[LUKS_HASHSPEC_L];
#	uint32_t	payloadOffset;
#	uint32_t	keyBytes;
#	char		mkDigest[LUKS_DIGESTSIZE];
#	char		mkDigestSalt[LUKS_SALTSIZE];
#	uint32_t	mkDigestIterations;
#	char            uuid[UUID_STRING_L];
#
#	struct {
#		uint32_t active;
#	
#		/* parameters used for password processing */
#		uint32_t passwordIterations;
#		char     passwordSalt[LUKS_SALTSIZE];
#		
#		/* parameters used for AF store/load */		
#		uint32_t keyMaterialOffset;
#		uint32_t stripes;		
#	} keyblock[LUKS_NUMKEYS];
#};

# size is 208 bytes + 48 * LUKS_NUMKEYS  = 592 bytes
