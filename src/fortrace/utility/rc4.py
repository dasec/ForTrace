#!/usr/bin/env python
#
#       rc4.py - RC4, ARC4, ARCFOUR algorithm with random salt
#
#       Copyright (c) 2009 joonis new media
#       Author: Thimo Kraemer <thimo.kraemer@joonis.de>
#       Modified: 2016 Sascha Kopp <sascha.kopp@stud.h-da.de>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#

from __future__ import absolute_import
from __future__ import print_function
import random, base64
from hashlib import sha1
from six.moves import range

__all__ = ['crypt', 'encrypt', 'decrypt']


def crypt(data, key):
    """RC4 algorithm

    :param key: key used for crypto
    :param data: data to crypt
    """
    x = 0
    box = list(range(256))
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

    return ''.join(out)


def encrypt(data, key, encode=base64.b64encode, salt_length=16):
    """RC4 encryption with random salt and final encoding

    :param salt_length: length of salt
    :param encode: encoding algorithm
    :param key: key used for encryption
    :param data: data to encrypt
    """
    salt = ''
    for n in range(salt_length):
        salt += chr(random.randrange(256))
    data = salt + crypt(data, sha1(key + salt).digest())
    if encode:
        data = encode(data)
    return data


def decrypt(data, key, decode=base64.b64decode, salt_length=16):
    """RC4 decryption of encoded data

    :param salt_length: length of salt
    :param decode: decoding algorithm
    :param key: key used for decryption
    :param data: data to decrypt
    """
    if decode:
        data = decode(data)
    salt = data[:salt_length]
    return crypt(data[salt_length:], sha1(key + salt).digest())


if __name__ == '__main__':
    for i in range(10):
        data = encrypt('secret message', 'my-key')
        print(data)
        print(decrypt(data, 'my-key'))
