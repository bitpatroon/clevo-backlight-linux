#!/usr/bin/env python3
"""
ITE Device(829x) 048d:8910  —  test keyboard LED via /dev/hidraw4

Feature Reports (uit HID descriptor):
  ID 0x5A: 1+16 = 17 bytes   — mode/command
  ID 0xCC: 1+6  =  7 bytes   — 3-bit packed waarden
  ID 0xCE: 1+2  =  3 bytes   — trigger/commit
  ID 0xCF: 1+64 = 65 bytes   — hoofd kleur-data

Gebruik:
  sudo python3 test_hid.py [R G B]
  sudo python3 test_hid.py 255 0 0    # rood
  sudo python3 test_hid.py 0 255 0    # groen
  sudo python3 test_hid.py 0 0 255    # blauw
"""
import fcntl
import sys
import time

HIDRAW = '/dev/hidraw4'

def HIDIOCSFEATURE(n):
    # _IOC(_IOC_WRITE|_IOC_READ, 'H', 0x06, n)
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 6

def send_feature(fd, data):
    buf = bytearray(data)
    try:
        fcntl.ioctl(fd, HIDIOCSFEATURE(len(buf)), buf)
        return True
    except OSError as e:
        print(f"  ioctl fout: {e}")
        return False

R = int(sys.argv[1]) if len(sys.argv) > 1 else 255
G = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 0
print(f"Kleur: R={R} G={G} B={B}")

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()

    # --- Test A: Report 0xCF (64 bytes) vol met kleur ---
    # 64 bytes = 21× RGB + 1 padding
    payload = ([R, G, B] * 21 + [0])[:64]
    ok = send_feature(fd, [0xCF] + payload)
    print(f"[A] Report 0xCF solid color: {'OK' if ok else 'FAIL'}")
    time.sleep(1.5)

    # --- Test B: Report 0x5A mode=0x01 (static?) + kleur ---
    payload = [0x01, R, G, B] + [0] * 12  # 16 bytes
    ok = send_feature(fd, [0x5A] + payload)
    print(f"[B] Report 0x5A mode=01+color: {'OK' if ok else 'FAIL'}")
    time.sleep(1.5)

    # --- Test C: Report 0xCE commit=0x01 ---
    ok = send_feature(fd, [0xCE, 0x01, 0x00])
    print(f"[C] Report 0xCE commit: {'OK' if ok else 'FAIL'}")
    time.sleep(0.5)

    # --- Test D: Combinatie: 0x5A mode + 0xCF data + 0xCE commit ---
    print("\n[D] Combinatie: init → kleur → commit")
    send_feature(fd, [0x5A, 0x01] + [0] * 15)          # init mode
    time.sleep(0.1)
    payload = ([R, G, B] * 21 + [0])[:64]
    send_feature(fd, [0xCF] + payload)                  # kleur data
    time.sleep(0.1)
    ok = send_feature(fd, [0xCE, 0x01, 0x00])           # commit
    print(f"[D] commit: {'OK' if ok else 'FAIL'}")
    time.sleep(1.5)

    # --- Test E: Report 0x5A met mode-byte varianten ---
    print("\n[E] Probeer 0x5A met mode bytes 0x00..0x0F ...")
    for mode in [0x00, 0x01, 0x02, 0x03, 0x08, 0x10, 0x40, 0x80]:
        payload = [mode, R, G, B] + [0] * 12
        ok = send_feature(fd, [0x5A] + payload)
        print(f"    mode=0x{mode:02X}: {'OK' if ok else 'FAIL'}")
        time.sleep(0.3)

print("\nKlaar. Is de LED veranderd?")
