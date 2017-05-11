#!/usr/bin/env python
from __future__ import print_function
import re
import sys

from electrum_ltc import bitcoin

TARGET = 'LartGjF6UjmvmF1JXBhFf5wtM9uZX7LzeS'

def read_bitmap(f):
    bitmap = {} # initial, color => to
    for line in open(f):
	initial, color, to = line.split()
	initial, to = int(initial), int(to)
	if (initial, color) in bitmap:
	    print("duplicate", initial, color)
	bitmap[(initial, color)] = to
    return bitmap

def read_colors(f):
    a = []
    for line in open(f):
	color = line[1:3]
	if not (color == line[3:5] == line[5:7]):
	    print("bad color", line)
	a.append(color)
    return a

def rotate(l, n):
    return l[n:] + l[:n]

def int_bits_to_secret(int_bits):
    key_bits_str = ''.join(str(bit) for bit in int_bits)
    key_int = [int(byte, 2) for byte in re.findall('.{8}', key_bits_str)]
    key_str = ''.join(chr(byte) for byte in key_int)
    secret = bitcoin.SecretToASecret(key_str)
    return secret 

def secret_to_address(secret):
    return bitcoin.address_from_private_key(secret)

def test(int_bits):
    secret = int_bits_to_secret(int_bits)
    address = secret_to_address(secret)
    if address == TARGET:
        print("*** FOUND !!!", secret, address, file=sys.stderr)
    return address

bitmap = read_bitmap('map.txt')
ext0 = read_colors('ext0.txt')
int1 = read_colors('int1.txt')

#print(set(ext0) - set(bitmap[0].keys()))
#print(set(bitmap[0].keys()) - set(ext0))
#print(set(int1) - set(bitmap[1].keys()))
#print(set(bitmap[1].keys()) - set(int1))

# transform
allbits = []
for i, color in enumerate(ext0 + int1):
    bit = i / 128
    new_bit = bitmap.get((bit, color), bit)
    print(i, color, bit, new_bit)
    allbits.append(new_bit)
print(test(allbits))

