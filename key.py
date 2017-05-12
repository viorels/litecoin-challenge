#!/usr/bin/env python
from __future__ import print_function
import re
import sys

from electrum_ltc import bitcoin
from multiprocessing import Pool, TimeoutError

TARGET = 'LartGjF6UjmvmF1JXBhFf5wtM9uZX7LzeS'

def read_bitmap(f):
    bitmap = {}
    for line in open(f):
	initial, color, to = line.split()
	initial, to = int(initial), int(to)
	bitmap[color] = to
        bitmap[(color, initial)] = to
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
        print("*** FOUND !!!", secret, address)
        print("*** FOUND !!!", secret, address, file=sys.stderr)
        return secret

def map_colors(colors, start_bit):
    bit = start_bit
    bits = []
    for i, color in enumerate(colors):
        #print(i, color, bit)
        bits.append(bit)
        bit = bitmap[color]
    assert bit == start_bit
    return bits

bitmap = read_bitmap('map.txt')
ext_right = read_colors('ext0.txt') # ed does not map to last 0
ext_left = list(reversed(rotate(ext_right, 1)))
int_right = rotate(read_colors('int1.txt'), -1)
int_left = list(reversed(rotate(int_right, 1)))

ext_bits_left = map_colors(ext_left, 0)
int_bits_left = map_colors(int_left, 1)
int_bits_right = map_colors(int_right, 1)

def try_rotate(first, second):
    for r1 in range(128):
        first_bits = rotate(first, r1)
        for r2 in range(128):
            allbits = first_bits + rotate(second, r2)
            print(r1, r2, ''.join(str(b) for b in allbits))
            secret = test(allbits)
            if secret:
                return secret

# TODO
# 2 ext + int | int + ext
# 2 ext_left + (int_right | int_left)
# 128^2 rotate(ext) * rotate(int)

combinations = [(ext_bits_left, int_bits_right), (ext_bits_left, int_bits_left), (int_bits_right, ext_bits_left), (int_bits_left, ext_bits_left)]

if __name__ == '__main__':
    pool = Pool(4)
    results = []
    for first, second in combinations:
        results.append(pool.apply_async(try_rotate, (first, second)))

    done = False
    while not done:
        for res in results:
            try:
                if res.get(1):
                    done = True
            except TimeoutError:
                pass
    pool.terminate()

