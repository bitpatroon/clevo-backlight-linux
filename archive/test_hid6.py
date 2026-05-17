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

    # Stap 1: alles rood 0-255
    print("[1] Indices 0-255 allemaal rood...")
    all_keys(fd, R, G, B, 255)
    print("    Zijn nu ALLE toetsen rood?")
    time.sleep(4)

    # Stap 2: kleur per blok van 32 om rijen te identificeren
    colors = [
        (255,   0,   0),  # blok 0-31:   rood
        (255, 165,   0),  # blok 32-63:  oranje
        (255, 255,   0),  # blok 64-95:  geel
        (  0, 255,   0),  # blok 96-127: groen
        (  0, 255, 255),  # blok 128-159: cyaan
        (  0,   0, 255),  # blok 160-191: blauw
        (128,   0, 255),  # blok 192-223: paars
        (255, 255, 255),  # blok 224-255: wit
    ]
    print("[2] Kleurblokken per 32 indices (om rijen te mappen)...")
    for blok, (r, g, b) in enumerate(colors):
        start = blok * 32
        for i in range(start, start + 32):
            set_key(fd, i, r, g, b)
    commit(fd)
    print("    Welke kleur heeft welke rij?")
    print("    Rood=0-31, Oranje=32-63, Geel=64-95, Groen=96-127")
    print("    Cyaan=128-159, Blauw=160-191, Paars=192-223, Wit=224-255")
    time.sleep(8)

    # Stap 3: alles uit
    print("[3] Alles uit")
    all_keys(fd, 0, 0, 0, 255)
    print("Klaar!")
