#!/usr/bin/env python3
"""
ITE 048d:8910 — vind het volledige bereik van toetsindices.

We weten al:
  0-63:   bovenste 2 rijen
  64-127: rijen 3-4
  128+:   onderste rijen (nog onbekend)
"""
import fcntl, time, sys

HIDRAW = '/dev/hidraw4'
R = int(sys.argv[1]) if len(sys.argv) > 1 else 255
G = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 0

def HIDIOCSFEATURE(n):
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 6

def set_key(fd, idx, r, g, b):
    buf = (bytearray([0xCF, 0x01, idx, r, g, b]) + bytearray(65))[:65]
    fcntl.ioctl(fd, HIDIOCSFEATURE(65), buf)

def commit(fd, brightness=0xFF):
    buf = bytearray([0xCE, 0x01, brightness])
    fcntl.ioctl(fd, HIDIOCSFEATURE(3), buf)

def all_keys(fd, r, g, b, max_idx=255):
    for i in range(max_idx + 1):
        set_key(fd, i, r, g, b)
    commit(fd)

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()

    # Stap 2: kleur per blok van 32 om rijen te identificeren
    colors = [
        (0, 0, 255),  # blok 224-255: wit
        (0, 0, 255),  # blok 224-255: wit
        (0, 0, 255),  # blok 224-255: wit
        (0, 0, 255),  # blok 224-255: wit
        (0, 0, 255),  # blok 224-255: wit
        (0, 0, 255),  # blok 224-255: wit
    ]
    print("[2] Kleurblokken per 32 indices (om rijen te mappen)...")
    for blok, (r, g, b) in enumerate(colors):
        start = blok * 32
        for i in range(start, start + 32):
            set_key(fd, i, r, g, b)
    commit(fd)
    print("Klaar!")
