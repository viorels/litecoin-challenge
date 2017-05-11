#!/usr/bin/env python
from __future__ import print_function
import re

from electrum_ltc import bitcoin

TARGET = 'LartGjF6UjmvmF1JXBhFf5wtM9uZX7LzeS'

def read_bitmap(f):
    bitmap = [{}, {}]
    for line in open(f):
	group, color, to = line.split()
	group, to = int(group), int(to)
	if color in bitmap[group]:
	    print("duplicate", group, color, to)
	bitmap[group][color] = to
    return bitmap

def read_colors(f):
    a = []
    for line in open(f):
	color = line[1:3]
	if not (color == line[3:5] == line[5:7]):
	    print("bad color", line)
	a.append(color)
    return a

def int_bits_to_secret(int_bits):
    key_bits_str = ''.join(str(bit) for bit in int_bits)
    key_int = [int(byte, 2) for byte in re.findall('.{8}', key_bits_str)]
    key_str = ''.join(chr(byte) for byte in key_int)
    secret = bitcoin.SecretToASecret(key_str)
    return secret 

def int_bits_to_address(int_bits):
    secret = int_bits_to_secret(int_bits)
    return bitcoin.address_from_private_key(secret)

bitmap = read_bitmap('map.txt')
ext0 = read_colors('ext0.txt')
int1 = read_colors('int1.txt')

#print(set(ext0) - set(bitmap[0].keys()))
#print(set(bitmap[0].keys()) - set(ext0))
#print(set(int1) - set(bitmap[1].keys()))
#print(set(bitmap[1].keys()) - set(int1))

# transform
extbits = [bitmap[0].get(color, 0) for color in ext0]
intbits = [bitmap[1].get(color, 1) for color in int1]
print(int_bits_to_address(extbits + intbits))

