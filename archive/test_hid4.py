#!/usr/bin/env python3
"""
ITE 048d:8910 — broadcast protocol verificatie.

Protocol:
  0xCF [0x00, 0x00, R, G, B, ...] = alle toetsen zelfde kleur
  0xCE [0x01, brightness]          = permanent commit
  0xCE [0x00, brightness]          = tijdelijke flash
"""
import fcntl, time, sys

HIDRAW = '/dev/hidraw4'
R = int(sys.argv[1]) if len(sys.argv) > 1 else 255
G = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 0

def HIDIOCSFEATURE(n):
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 6

def send(fd, data):
    buf = (bytearray(data) + bytearray(65))[:max(len(data), 3)]
    fcntl.ioctl(fd, HIDIOCSFEATURE(len(buf)), buf)

def broadcast(fd, r, g, b, brightness=0xFF):
    """Zet alle toetsen op kleur r,g,b."""
    buf = bytearray(65)
    buf[0] = 0xCF
    buf[1] = 0x00   # broadcast mode
    buf[2] = 0x00   # key index (genegeerd bij broadcast)
    buf[3] = r
    buf[4] = g
    buf[5] = b
    fcntl.ioctl(fd, HIDIOCSFEATURE(65), buf)
    send(fd, [0xCE, 0x01, brightness])

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()

    print(f"[1] Alle toetsen ROOD (2 sec)")
    broadcast(fd, 255, 0, 0)
    time.sleep(2)

    print(f"[2] Alle toetsen GROEN (2 sec)")
    broadcast(fd, 0, 255, 0)
    time.sleep(2)

    print(f"[3] Alle toetsen BLAUW (2 sec)")
    broadcast(fd, 0, 0, 255)
    time.sleep(2)

    print(f"[4] Alle toetsen WIT (2 sec)")
    broadcast(fd, 255, 255, 255)
    time.sleep(2)

    print(f"[5] Gewenste kleur: R={R} G={G} B={B}")
    broadcast(fd, R, G, B)
    time.sleep(2)

    print(f"[6] Helderheid 50% (0x80)")
    broadcast(fd, R, G, B, brightness=0x80)
    time.sleep(2)

    print(f"[7] Uit (brightness=0)")
    send(fd, [0xCE, 0x01, 0x00])
    time.sleep(1)

    print("Klaar!")
