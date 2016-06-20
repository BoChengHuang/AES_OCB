#!/usr/bin/python
#
#  AES - Advanced Encryption Standard in pure Python
# 
# Based on code by:
#             Josh Davis ( http://www.josh-davis.org ),
#             Laurent Haan ( http://www.progressive-coding.com )
#             Alex Martelli ( http://www.aleax.it )
# Author:
#             Pawel Krawczyk (http://ipsec.pl)
# Features:
#    1) very extensive testing included
#    2) consistent interface
# 
# Licensed under GNU General Public License (GPL)
# Version 3, 29 June 2007
# http://www.gnu.org/licenses/gpl.html

import math

class AES:
    """
    AES encryption/decryption class with support for keylength 128, 192, 256 bits. 
    Data is represented as bytearray objects. This class operates on single AES
    block which is 16 bytes, so plaintext for encryption and ciphertext for 
    decryption must be exactly 16 bytes long.
    
    Usage:
    
        >>> a = AES(128)
        >>> key = bytearray().fromhex('A45F5FDEA5C088D1D7C8BE37CABC8C5C')
        >>> a.setKey(key)
        >>> plaintext = bytearray('The Magic Words ')
        >>> len(plaintext)
        16
        >>> ciphertext = a.encrypt(plaintext)
        >>> ciphertext
        bytearray(b'\xe6\xb7\x97\xf9\x01\x88\x1e"\xf0\xfb\xd4\xebM\xc0\x8cD')
        >>> plaintext2 = a.decrypt(ciphertext)
        >>> plaintext2
        bytearray(b'The Magic Words ')
    """
    # keysize in bits -> rounds mapping
    keySizeRounds = { 128 : 10, 192 : 12, 256 : 14 }

    def __init__(self, keyBitSize=128):
        """
        Initialize new AES object. Default key lenght is 128 bits.
        Number of rounds and size of expanded key are calculated.
        """
        assert keyBitSize in (128, 192, 256)

        self.keyBitSize = keyBitSize
        self.nbrRounds = self.keySizeRounds[keyBitSize]
        self.expandedKeySize = (16 * (self.nbrRounds + 1))
        self.expandedKey = bytearray()

    def setKey(self, key):
        """
        Set AES key with expansion. 
        Input: bytearray. 
        Length must be 16, 24, 32 depending on keys size.
        """
        assert self.keyBitSize == len(key) * 8
        self.expandedKey = self._expandKey(key)

    def getKeySize(self):
        """
        Return AES key length as arrays size (bytes).
        """
        return self.keyBitSize / 8

    def getBlockSize(self):
        """
        Return AES block size as array size (bytes)
        """
        return 128 / 8

    def getRounds(self):
        """
        Return AES rounds number for currently configured key length.
        """
        return self.nbrRounds

    #Rijndael S-box
    _sbox = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16 ]
    # Rijndael Inverted S-box
    _rsbox = [ 0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb
    , 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb
    , 0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e
    , 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25
    , 0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92
    , 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84
    , 0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06
    , 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b
    , 0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73
    , 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e
    , 0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b
    , 0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4
    , 0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f
    , 0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef
    , 0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61
    , 0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d ]

    def _getSBoxValue(self, num):
        """ retrieves a given S-Box Value """
        assert num < len(self._sbox)
        return self._sbox[num]

    def _getSBoxInvert(self, num):
        """ Retrieves a given Inverted S-Box Value """
        assert num < len(self._sbox)
        return self._rsbox[num]

    def _rotate(self, word):
        """
        Rijndael's key schedule rotate operation
        rotate the word eight bits to the left
        
        rotate(1d2c3a4f) = 2c3a4f1d
   
        word is an char array of size 4 (32 bit)
        >>> aes = AES(128)
        >>> aes._rotate('abcd')
        'bcda'
        """
        return word[1:] + word[:1]

    # Rijndael Rcon
    _Rcon = [0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8,
    0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3,
    0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f,
    0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d,
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab,
    0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d,
    0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25,
    0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01,
    0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d,
    0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa,
    0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a,
    0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02,
    0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a,
    0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef,
    0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94,
    0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04,
    0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f,
    0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5,
    0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33,
    0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb ]

    def _getRconValue(self, num):
        """ Gets a given Rcon value """
        return self._Rcon[num]

    def _core(self, word, iteration):
        """ Key Schedule Core """
        # rotate the 32-bit word 8 bits to the left
        word = self._rotate(word)
        # apply S-Box substitution on all 4 parts of the 32-bit word
        for i in range(4):
            word[i] = self._getSBoxValue(word[i])
        # XOR the output of the rcon operation with i to the first part (leftmost) only
        word[0] = word[0] ^ self._getRconValue(iteration)
        return word

    def _expandKey(self, key):
        """
        Rijndael's key expansion
        expands an 128,192,256 key into an 176,208,240 bytes key
 
        expandedKey is a pointer to an char array of large enough size
        key is a pointer to a non-expanded key
        """
        size = self.keyBitSize / 8

        # current expanded keySize, in bytes
        currentSize = 0
        rconIteration = 1
        # temporary 4-byte variable
        t = bytearray([0, 0, 0, 0])

        assert self.expandedKeySize
        expandedKey = bytearray(self.expandedKeySize)

        # set the 16,24,32 bytes of the expanded key to the input key
        for j in range(size):
            expandedKey[j] = key[j]
        currentSize += size

        while currentSize < self.expandedKeySize:
            # assign the previous 4 bytes to the temporary value t
            for k in range(4): t[k] = expandedKey[(currentSize - 4) + k]
            #
            # every 16,24,32 bytes we apply the core schedule to t
            # and increment rconIteration afterwards
            #
            if currentSize % size == 0:
                t = self._core(t, rconIteration)
                rconIteration += 1;
            # For 256-bit keys, we add an extra sbox to the calculation
            if size == (256 / 8) and ((currentSize % size) == 16):
                for l in range(4): t[l] = self._getSBoxValue(t[l])

            #
            # We XOR t with the four-byte block 16,24,32 bytes before the new expanded key.
            # This becomes the next four bytes in the expanded key.
            #
            for m in range(4):
                expandedKey[currentSize] = expandedKey[currentSize - size] ^ t[m]
                currentSize += 1
        return expandedKey

    # Adds (XORs) the round key to the state
    def _addRoundKey(self, state, roundKey):
        for i in range(16):
            state[i] ^= roundKey[i]
        return state

    # Creates a round key from the given expanded key and the
    # position within the expanded key.
    def _createRoundKey(self, expandedKey, roundKeyPointer):
        roundKey = bytearray(16)
        for i in range(4):
            for j in range(4):
                roundKey[j * 4 + i] = expandedKey[roundKeyPointer + i * 4 + j]
        return roundKey

    def _galois_multiplication(self, a, b):
        """Galois multiplication of 8 bit characters a and b."""
        p = 0
        for counter in range(8):
            if b & 1: p ^= a
            hi_bit_set = a & 0x80
            a <<= 1
            # keep a 8 bit
            a &= 0xFF
            if hi_bit_set:
                a ^= 0x1b
            b >>= 1
        return p

    def _subBytes(self, state, isInv):
        """
        Substitute all the values from the state with the value in the SBox
        using the state value as index for the SBox
        """
        for i in range(16):
            if isInv: state[i] = self._getSBoxInvert(state[i])
            else: state[i] = self._getSBoxValue(state[i])
        return state

    def _shiftRows(self, state, isInv):
        """ Iterate over the 4 rows and call shiftRow() with that row """
        for i in range(4):
            state = self._shiftRow(state, i * 4, i, isInv)
        return state

    def _shiftRow(self, state, statePointer, nbr, isInv):
        """ Each iteration shifts the row to the left by 1 """
        for i in range(nbr):
            if isInv:
                state[statePointer:statePointer + 4] = \
                        state[statePointer + 3:statePointer + 4] + \
                        state[statePointer:statePointer + 3]
            else:
                state[statePointer:statePointer + 4] = \
                        state[statePointer + 1:statePointer + 4] + \
                        state[statePointer:statePointer + 1]
        return state

    def _mixColumns(self, state, isInv):
        """ Galois multipication of the 4x4 matrix """
        column = bytearray([0, 0, 0, 0])
        # iterate over the 4 columns
        for i in range(4):
            # construct one column by iterating over the 4 rows
            for j in range(4): column[j] = state[(j * 4) + i]
            # apply the mixColumn on one column
            column = self._mixColumn(column, isInv)
            # put the values back into the state
            for k in range(4): state[(k * 4) + i] = column[k]

        return state

    def _mixColumn(self, column, isInv):
        """ Galois multipication of 1 column of the 4x4 matrix """
        if isInv:
            mult = bytearray([14, 9, 13, 11])
        else: 
            mult = bytearray([2, 1, 1, 3])
        cpy = list(column)
        g = self._galois_multiplication

        column[0] = g(cpy[0], mult[0]) ^ g(cpy[3], mult[1]) ^ \
                    g(cpy[2], mult[2]) ^ g(cpy[1], mult[3])
        column[1] = g(cpy[1], mult[0]) ^ g(cpy[0], mult[1]) ^ \
                    g(cpy[3], mult[2]) ^ g(cpy[2], mult[3])
        column[2] = g(cpy[2], mult[0]) ^ g(cpy[1], mult[1]) ^ \
                    g(cpy[0], mult[2]) ^ g(cpy[3], mult[3])
        column[3] = g(cpy[3], mult[0]) ^ g(cpy[2], mult[1]) ^ \
                    g(cpy[1], mult[2]) ^ g(cpy[0], mult[3])
        return column

    def _aes_round(self, state, roundKey):
        """ Applies the 4 operations of the forward round in sequence """
        state = self._subBytes(state, False)
        state = self._shiftRows(state, False)
        state = self._mixColumns(state, False)
        state = self._addRoundKey(state, roundKey)
        return state

    def _aes_invRound(self, state, roundKey):
        """ Applies the 4 operations of the inverse round in sequence """
        state = self._shiftRows(state, True)
        state = self._subBytes(state, True)
        state = self._addRoundKey(state, roundKey)
        state = self._mixColumns(state, True)
        return state

    def _aes_main(self, state, expandedKey, nbrRounds):
        """
        Perform the initial operations, the standard round, and the final operations
        of the forward aes, creating a round key for each round
        """
        state = self._addRoundKey(state, self._createRoundKey(expandedKey, 0))
        i = 1
        while i < nbrRounds:
            state = self._aes_round(state, self._createRoundKey(expandedKey, 16 * i))
            i += 1
        state = self._subBytes(state, False)
        state = self._shiftRows(state, False)
        state = self._addRoundKey(state, self._createRoundKey(expandedKey, 16 * nbrRounds))
        return state

    def _aes_invMain(self, state, expandedKey, nbrRounds):
        """
        Perform the initial operations, the standard round, and the final operations
        of the inverse aes, creating a round key for each round
        """
        state = self._addRoundKey(state, self._createRoundKey(expandedKey, 16 * nbrRounds))
        i = nbrRounds - 1
        while i > 0:
            state = self._aes_invRound(state, self._createRoundKey(expandedKey, 16 * i))
            i -= 1
        state = self._shiftRows(state, True)
        state = self._subBytes(state, True)
        state = self._addRoundKey(state, self._createRoundKey(expandedKey, 0))
        return state

    def _blockMap(self, iput):
        """
        Set the block values, for the block:
        a0,0 a0,1 a0,2 a0,3
        a1,0 a1,1 a1,2 a1,3
        a2,0 a2,1 a2,2 a2,3
        a3,0 a3,1 a3,2 a3,3
        the mapping order is a0,0 a1,0 a2,0 a3,0 a0,1 a1,1 ... a2,3 a3,3
        """
        block = bytearray(16)

        for i in range(4):
            # iterate over the rows
            for j in range(4):
                block[(i + (j * 4))] = iput[(i * 4) + j]
        return block

    def _blockUnmap(self, block):
        output = bytearray(16)
        for k in range(4):
            # iterate over the rows
            for l in range(4):
                output[(k * 4) + l] = block[(k + (l * 4))]
        return output

    def encrypt(self, input):
        """ encrypts a 128 bit input block """
        assert len(self.expandedKey) == self.expandedKeySize
        assert len(input) == self.getBlockSize()

        output = bytearray(16)
        block = self._blockMap(input)
        block = self._aes_main(block, self.expandedKey, self.nbrRounds)
        output = self._blockUnmap(block)
        return output

    def decrypt(self, input):
        """ decrypts a 128 bit input block """
        assert self.expandedKey
        assert len(input) == self.getBlockSize()

        output = bytearray(16)
        block = self._blockMap(input)
        block = self._aes_invMain(block, self.expandedKey, self.nbrRounds)
        output = self._blockUnmap(block)
        return output

import unittest

class AesTestCase(unittest.TestCase):

    def setUp(self):
        """ 
        NIST AES Known Answer Test (KAT)
        Test vectors taken from NIST Cryptographic Algorithm Validation Program (CAVP)
            http://csrc.nist.gov/groups/STM/cavp/index.html
        Specific test values used:
            http://csrc.nist.gov/groups/STM/cavp/documents/aes/KAT_AES.zip
        """
        self.nistE = (# KAT ENCRYPTION - key, KAT file, input, output
            (128, 'f34481ec3cc627bacd5dc3fb08f273e6', '0336763e966d92595a567cc9ce537f5e'),
            (128, '9798c4640bad75c7c3227db910174e72', 'a9a1631bf4996954ebc093957b234589'),
            (192, '1b077a6af4b7f98229de786d7516b639', '275cfc0413d8ccb70513c3859b1d0f72'),
            (192, '9c2d8842e5f48f57648205d39a239af1', 'c9b8135ff1b5adc413dfd053b21bd96d'),
            (256, '014730f80ac625fe84f026c60bfd547d', '5c9d844ed46f9885085e5d6a4f94c7d7'),
            (256, '0b24af36193ce4665f2825d7b4749c98', 'a9ff75bd7cf6613d3731c77c3b6d0c04')
            )
        self.nistD = (# KAT DECRYPTION - key, KAT file, input, output
             (128, '0336763e966d92595a567cc9ce537f5e', 'f34481ec3cc627bacd5dc3fb08f273e6'),
             (128, 'a9a1631bf4996954ebc093957b234589', '9798c4640bad75c7c3227db910174e72'),
             (192, '275cfc0413d8ccb70513c3859b1d0f72', '1b077a6af4b7f98229de786d7516b639'),
             (192, 'c9b8135ff1b5adc413dfd053b21bd96d', '9c2d8842e5f48f57648205d39a239af1'),
             (256, '5c9d844ed46f9885085e5d6a4f94c7d7', '014730f80ac625fe84f026c60bfd547d'),
             (256, 'a9ff75bd7cf6613d3731c77c3b6d0c04', '0b24af36193ce4665f2825d7b4749c98')
             )
        """ http://blogs.msdn.com/si_team/archive/2006/05/19/aes-test-vectors.aspx """
        self.msResults = (# MICROSOFT AES TEST VECTORS
            (128, [0xbd, 0x88, 0x3f, 0x01, 0x03, 0x5e, 0x58, 0xf4, 0x2f, 0x9d, 0x81, 0x2f, 0x2d, 0xac, 0xbc, 0xd8]),
            (192, [0x41, 0xaf, 0xb1, 0x00, 0x4c, 0x07, 0x3d, 0x92, 0xfd, 0xef, 0xa8, 0x4a, 0x4a, 0x6b, 0x26, 0xad]),
            (256, [0xc8, 0x4b, 0x0f, 0x3a, 0x2c, 0x76, 0xdd, 0x98, 0x71, 0x90, 0x0b, 0x07, 0xf0, 0x9b, 0xdd, 0x3e])
            )

    def test_kat_encryption(self):
        for (keyLen, plainText, expectedCipherText) in self.nistE:
            key = bytearray((keyLen / 8))
            aes = AES(keyLen)
            aes.setKey(key)
            cipherText = aes.encrypt(bytearray.fromhex((plainText)))
            self.assertEqual(cipherText, bytearray().fromhex(expectedCipherText))
            del aes

    def test_kat_decryption(self):
        for (keyLen, cipherText, expectedPlainText) in self.nistD:
            key = bytearray((keyLen / 8))
            aes = AES(keyLen)
            aes.setKey(key)
            plainText = aes.decrypt(bytearray.fromhex((cipherText)))
            self.assertEqual(plainText, bytearray().fromhex(expectedPlainText))
            del aes

    def test_ms(self):
        for (keyLen, result) in self.msResults:
            b = 16
            k = keyLen / 8
            aes = AES(keyLen)
            S = bytearray((k + b))
            for i in range(1000):
                n = len(S)
                K = S[-k:]
                #print "K=", a2h(K)
                aes.setKey(K)
                P = S[-(k + b):-(k)]
                #print "P=", a2h(P)
                S += aes.encrypt(aes.encrypt(P))
            vector = S[-b:]
            expectedVector = bytearray(result)
            self.assertEqual(vector, expectedVector)

if __name__ == "__main__":
    unittest.main()
