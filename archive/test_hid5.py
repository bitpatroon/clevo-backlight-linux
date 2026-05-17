#!/usr/bin/env python3
"""
ITE 048d:8910 — zet ALLE toetsen op kleur via per-key protocol.

Protocol:
  [0xCF, 0x01, key_idx, R, G, B, 0..0]  → één toets
  [0xCE, 0x01, brightness]               → commit

Stuur voor alle key_idx 0..127 om alle toetsen te dekken.
"""
import fcntl, time, sys

HIDRAW = '/dev/hidraw4'
R = int(sys.argv[1]) if len(sys.argv) > 1 else 255
G = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 0

def HIDIOCSFEATURE(n):
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 6

def send(fd, data):
    buf = (bytearray(data) + bytearray(65))[:65]
    fcntl.ioctl(fd, HIDIOCSFEATURE(len(buf)), buf)

def set_key(fd, key_idx, r, g, b):
    send(fd, [0xCF, 0x01, key_idx, r, g, b])

def commit(fd, brightness=0xFF):
    buf = bytearray([0xCE, 0x01, brightness])
    fcntl.ioctl(fd, HIDIOCSFEATURE(3), buf)

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()

    print(f"Alle toetsen (0..127) instellen op R={R} G={G} B={B}...")
    for i in range(128):
        set_key(fd, i, R, G, B)
    commit(fd, 0xFF)
    print("Commit gedaan. Hoeveel toetsen zijn rood?")
    time.sleep(4)

    print("\nNu: helft rood, helft blauw (0..63 rood, 64..127 blauw)")
    for i in range(64):
        set_key(fd, i, 255, 0, 0)
    for i in range(64, 128):
        set_key(fd, i, 0, 0, 255)
    commit(fd, 0xFF)
    time.sleep(4)

    print("\nNu: uit")
    for i in range(128):
        set_key(fd, i, 0, 0, 0)
    commit(fd, 0xFF)
    print("Klaar!")
