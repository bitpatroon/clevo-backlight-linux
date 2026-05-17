#!/usr/bin/env python3
"""Lees huidige Feature Report state van ITE 048d:8910 terug."""
import fcntl

HIDRAW = '/dev/hidraw4'

def HIDIOCGFEATURE(n):
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 7

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()
    for rid, size in [(0x5A, 17), (0xCE, 3), (0xCF, 65)]:
        buf = bytearray(size)
        buf[0] = rid
        try:
            fcntl.ioctl(fd, HIDIOCGFEATURE(size), buf)
            print(f'Report 0x{rid:02X} ({size-1} bytes): {buf[1:].hex()}')
        except OSError as e:
            print(f'Report 0x{rid:02X}: error {e}')
