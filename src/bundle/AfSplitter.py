"""Implementation of anti-forensic information splitting

The AFsplitter supports secure data destruction crucial for secure on-disk key
management. The key idea is to bloat information and therefor improving the
chance of destroying a single bit of it. The information is bloated in such a
way, that a single missing bit causes the original information become
unrecoverable. The theory behind AFsplitter is presented in TKS1.

The interface is simple. It consists of two functions:

AFSplit(data, stripes, digestmod=sha)
AFMerge(data, stripes, digestmod=sha)

AFSplit operates on data and returns information splitted data.  AFMerge does
just the opposite: uses the information stored in data to recover the original
splitted data.

http://clemens.endorphin.org/AFsplitter
TKS1 paper from http://clemens.endorphin.org/publications

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


import sha, string, math, struct
from Crypto.Util.randpool import RandomPool
from Crypto.Cipher import XOR

def _xor(a, b):
	"""Internal function to performs XOR on two strings a and b"""

	xor = XOR.new(a)
	return xor.encrypt(b)

def _diffuse(block, size, digest):
	"""Internal function to diffuse information inside a buffer"""

	# Compute the number of full blocks, and the size of the leftover block
	full_blocks = int(math.floor(float(len(block)) / float(digest.digest_size)))
	padding = len(block) % digest.digest_size

	# hash the full blocks
	ret = ""
	for i in range(0, full_blocks):

		hash = digest.new()
		hash.update(struct.pack(">I", i))
		hash.update(block[i*digest.digest_size:(i+1)*digest.digest_size])
		ret += hash.digest()

	# Hash the remaining data
	if padding > 0:
		hash = digest.new()
		hash.update(struct.pack(">I", full_blocks))
		hash.update(block[full_blocks * digest.digest_size:])
		ret += hash.digest()[:padding]

	return ret

def AFSplit(data, stripes, digestmod=sha):
	"""AF-Split data using digestmod.  Returned data size will be len(data) * stripes"""

	blockSize = len(data)

	rand = RandomPool()

	bufblock = "\x00" * blockSize

	ret = ""
	for i in range(0, stripes-1):

		# Get some random data
		rand.randomize()
		rand.stir()
		r = rand.get_bytes(blockSize)
		if rand.entropy < 0:
			print "Warning: RandomPool entropy dropped below 0"

		ret += r
		bufblock = _xor(r, bufblock)
		bufblock = _diffuse(bufblock, blockSize, digestmod)
		rand.add_event(bufblock)

	ret += _xor(bufblock, data)
	return ret

def AFMerge(data, stripes, digestmod=sha):
	"""AF-Merge data using digestmod.  len(data) must be a multiple of stripes"""

	if len(data) % stripes != 0:
		raise "ERROR: data is not a multiple of strips"

	blockSize = len(data) / stripes

	bufblock = "\x00" * blockSize
	for i in range(0, stripes - 1):
		bufblock = _xor(data[i*blockSize:(i+1)*blockSize], bufblock)
		bufblock = _diffuse(bufblock, blockSize, digestmod)

	return _xor(data[(stripes-1)*blockSize:], bufblock)
