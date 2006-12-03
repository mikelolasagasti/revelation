#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
  - Implements the PKCS#5 v2.0: Password-Based Cryptography Standard
    from RSA Laboratories. RFC2898 http://www.rfc-editor.org/rfc/rfc2898.txt

Modifications by John Lenz <lenz@cs.wisc.edu>, April 2006
  + Fix the PBKDFv2 algorithm so it is correct
  + Use Cipher.XOR instead of slow python xor
  + other performance improvements

Original Code written by:

Copyright (C) 2004 - Lars Strand <lars strand at gnist org>
 
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

import struct, string, math, sha, hmac # RFC2104
from Crypto.Cipher import XOR

################ PBKDFv2
class PBKDFv2:
    """Implements the PKCS#5 v2.0: Password-Based Cryptography Standard
    from RSA Laboratories. RFC2898

    http://www.rfc-editor.org/rfc/rfc2898.txt
    """

    ################ init
    def __init__(self):

        # length of pseudorandom function: 20 for SHA-1, 16 for MD5
        self.hLen = 20
        
    ################ makeKey
    def makeKey(self, P, S, c, dkLen, digestmod=sha):
        """
           Input:   P         password, an octet string
                    S         salt, an octet string
                    c         iteration count, a positive integer (>1000)
                    dkLen     intended length on octets of the derived key, a positive integer,
                              at most (2^32 - 1) * hLen
                    digestmod Digest used, passed to hmac module

           Output   DK    derived key, a dkLen-octet string
           """

        # do some sanity checks
        try:
            str(P); str(S); int(c); float(dkLen); int(c)
        except:
            print "P = %s, S = %s, c = %s, dkLen = %s:" % (P, S, c, dkLen)
            raise "ERROR! Input is not correct!"

        # Step 1: if dkLen is larger than maximum possible key - exit
        if dkLen > ((2^32 - 1) * self.hLen):
            maxlength = (2^32 - 1) * self.hLen
            raise "ERROR! Key is to large! Maxlength is", str(maxlength)

        # Step 2:
        # Let l be the number of hLen-octet blocks in the derived key, rounding up
        # and let r be the number of octets in the last block
        l = math.ceil(dkLen / float(self.hLen))
        #if (dkLen % float(self.hLen)): l = int(l) + 1 # round up if necessary
        r = dkLen - (l - 1) * self.hLen

        # Step 3:
        # For each block of the derived key, apply the function F to the
        # password P, the salt S, the iteration count c, and the block index
        # to compute the block
        T = ""
        for blockindex in range(int(l)):
            T += self.F(P, S, c, blockindex, digestmod)
        # Step 4 - extract the first dkLen octet to produce a derived key DK
        DK = T[:dkLen]

        # Step 5 - return the derived key DK
        return DK
            
    ################ F
    def F(self, P, S, c, i, digest):
        """For each block of the derived key, apply this function.

        Notation:
        ||   = concatenation operator
        PRF  = Underlying pseudorandom function
        
        The function F is defined as the exclusive-or sum of the first c
        iterates if the underlying pseudorandom function PRF applied to
        the password P and the concatenation of the salt S and the block
        index i:

        F(P, S, c, i) = U1 XOR U2 XOR ... XOR Uc

        where

        U1 = PRF(P, S || INT(i)),
        U2 = PRF(P, U1)
        ...
        Uc = PRF(P, Uc-1)
        """

        # The pseudorandom function, PRF, used is HMAC-SHA1 (rfc2104)
        iteration = 1

        # the first iteration; P is the key, and a concatination of
        # S and blocknumber is the message
	istr = struct.pack(">I", i+1)
	PRFMaster = hmac.new(P,digestmod=digest)
	PRF = PRFMaster.copy()
	PRF.update(S)
	PRF.update(istr)
        U = PRF.digest() # the first iteration

	Fbuf = U

        while iteration < c:                  # loop through all iterations
	    PRF = PRFMaster.copy()
	    PRF.update(U)
            U = PRF.digest()
            Fbuf = self._xor(U, Fbuf)    # XOR this new iteration with the old one
            iteration += 1
        return Fbuf

    ################ xor
    def _xor(self, a, b):
        """Performs XOR on two strings a and b"""

        if len(a) != len(b):
            raise "ERROR: Strings are of different size! %s %s" % (len(a), len(b))

	xor = XOR.new(a)
	return xor.encrypt(b)
