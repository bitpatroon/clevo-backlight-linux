#!/usr/bin/env python3
"""
ITE 048d:8910 — gerichte LED test op basis van read-back resultaten.

Huidige device state (gelezen):
  0xCE: 01 10
  0xCF: 01 10 00 00 00 ... (mode=0x01, param=0x10, kleur=zwart)

Hypothese: 0xCF formaat = [mode, brightness, R1, G1, B1, R2, G2, B2, ...]
"""
import fcntl
import time
import sys

HIDRAW = '/dev/hidraw4'

R = int(sys.argv[1]) if len(sys.argv) > 1 else 255
G = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 0
print(f"Kleur: R={R} G={G} B={B}")

def HIDIOCSFEATURE(n):
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 6

def send(fd, data):
    buf = bytearray(data)
    try:
        fcntl.ioctl(fd, HIDIOCSFEATURE(len(buf)), buf)
        return True
    except OSError as e:
        print(f"  fout: {e}")
        return False

def pad(lst, total):
    return lst + [0] * (total - len(lst))

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()

    # Test A: header bewaard (01 10), kleurdata = RGB voor alle zones
    print("\n[A] 0xCF header=0x01,0x10 + RED×20 + commit 0xCE")
    data = pad([0xCF, 0x01, 0x10] + [R, G, B] * 20, 65)
    send(fd, data)
    send(fd, [0xCE, 0x01, 0x10])
    time.sleep(2)

    # Test B: zelfde maar brightness verhoogd naar 0xFF
    print("[B] 0xCF header=0x01,0xFF + RED×20 + commit 0xCE")
    data = pad([0xCF, 0x01, 0xFF] + [R, G, B] * 20, 65)
    send(fd, data)
    send(fd, [0xCE, 0x01, 0xFF])
    time.sleep(2)

    # Test C: mode=0x00 (reset?) daarna mode=0x01
    print("[C] reset 0x00 + herstart 0x01 + kleur")
    send(fd, pad([0xCF, 0x00, 0x00], 65))
    time.sleep(0.1)
    data = pad([0xCF, 0x01, 0xFF] + [R, G, B] * 20, 65)
    send(fd, data)
    send(fd, [0xCE, 0x01, 0xFF])
    time.sleep(2)

    # Test D: 0x5A aanpassen — bewaar FF patroon maar test RED in eerste 3 bytes
    print("[D] 0x5A met RED×4 zones (4 bytes per zone: R,G,B,brightness)")
    data = pad([0x5A,
                R, G, B, 0xFF,   # zone 1
                R, G, B, 0xFF,   # zone 2
                R, G, B, 0xFF,   # zone 3
                R, G, B, 0xFF],  # zone 4
               17)
    send(fd, data)
    send(fd, [0xCE, 0x01, 0x10])
    time.sleep(2)

    # Test E: 0x5A exact zoals gelezen (alles FF behalve byte 16=0x00)
    # maar dan 0xCF mode+kleur daarna
    print("[E] 0x5A=FF..FF + 0xCF kleur + 0xCE commit")
    send(fd, [0x5A] + [0xFF] * 15 + [0x00])
    time.sleep(0.05)
    data = pad([0xCF, 0x01, 0xFF] + [R, G, B] * 20, 65)
    send(fd, data)
    send(fd, [0xCE, 0x01, 0xFF])
    time.sleep(2)

    # Test F: probeer 0xCE met 0x01,0x00 (enable zonder mode?)
    print("[F] 0xCE = 01 00 (andere enable byte)")
    send(fd, [0xCE, 0x01, 0x00])
    time.sleep(1)

    print("\nKlaar. Welke test veranderde de LED?")
