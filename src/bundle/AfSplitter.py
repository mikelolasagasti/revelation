"""Implementation of anti-forensic information splitting

The AFsplitter supports secure data destruction crucial for secure on-disk key
management. The key idea is to bloat information and therefor improving the
chance of destroying a single bit of it. The information is bloated in such a
way, that a single missing bit causes the original information become
unrecoverable. The theory behind AFsplitter is presented in TKS1.

The interface is simple. It consists of two functions:

AFSplit(data, stripes, digesttype='sha1')
AFMerge(data, stripes, digesttype='sha1')

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
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

http://www.gnu.org/copyleft/gpl.html
"""


import hashlib, string, math, struct

import Cryptodome.Random as Random

def _xor(a, b):
    """Internal function to performs XOR on two strings a and b"""

    return bytes([x ^ y for (x, y) in zip(a, b)])

def _diffuse(block, size, digest):
    """Internal function to diffuse information inside a buffer"""

    # Compute the number of full blocks, and the size of the leftover block
    digest_size = hashlib.new(digest).digest_size
    full_blocks = int(math.floor(float(len(block)) / float(digest_size)))
    padding = len(block) % digest_size

    # hash the full blocks
    ret = b""
    for i in range(0, full_blocks):
        hash = hashlib.new(digest)
        hash.update(struct.pack(">I", i))
        hash.update(block[i*digest_size:(i+1)*digest_size])
        ret += hash.digest()

    # Hash the remaining data
    if padding > 0:
        hash = hashlib.new(digest)
        hash.update(struct.pack(">I", full_blocks))
        hash.update(block[full_blocks * digest_size:])
        ret += hash.digest()[:padding]

    return ret

def AFSplit(data, stripes, digesttype='sha1'):
    """AF-Split data using digesttype.  Returned data size will be len(data) * stripes"""

    blockSize = len(data)

    rand = Random.new()

    bufblock = [0] * blockSize

    ret = b""
    for i in range(0, stripes-1):

        # Get some random data
        r = rand.read(blockSize)

        ret += r
        bufblock = _xor(r, bufblock)
        bufblock = _diffuse(bufblock, blockSize, digesttype)

    ret += _xor(bufblock, data)
    return ret

def AFMerge(data, stripes, digesttype='sha1'):
    """AF-Merge data using digesttype.  len(data) must be a multiple of stripes"""

    if len(data) % stripes != 0:
        raise ValueError("ERROR: data is not a multiple of strips")

    blockSize = len(data) // stripes

    bufblock = [0] * blockSize
    for i in range(0, stripes - 1):
        bufblock = _xor(data[i*blockSize:(i+1)*blockSize], bufblock)
        bufblock = _diffuse(bufblock, blockSize, digesttype)

    return _xor(data[(stripes-1)*blockSize:], bufblock)
