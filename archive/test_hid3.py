#!/usr/bin/env python3
"""
ITE 048d:8910 — per-key RGB, meerdere chunks proberen.

Hypothese: byte 2 van 0xCF payload = chunk/page nummer.
Elke chunk dekt ~20 toetsen (3 bytes per toets = 60 bytes kleur + 2 header).
6 chunks = 120 toetsen → volledig toetsenbord.
"""
import fcntl
import time
import sys

HIDRAW = '/dev/hidraw4'

R = int(sys.argv[1]) if len(sys.argv) > 1 else 255
G = int(sys.argv[2]) if len(sys.argv) > 2 else 0
B = int(sys.argv[3]) if len(sys.argv) > 3 else 0

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
    return (lst + [0] * total)[:total]

with open(HIDRAW, 'rb+', buffering=0) as f:
    fd = f.fileno()

    # --- Test A: stuur 8 chunks met oplopende chunk-byte (byte index 2) ---
    print("[A] 8 chunks: byte2 = 0x00..0x07, elk 20 toetsen rood")
    for chunk in range(8):
        payload = pad([0xCF, 0x01, chunk] + [R, G, B] * 20, 65)
        send(fd, payload)
        time.sleep(0.05)
    send(fd, [0xCE, 0x01, 0xFF])
    print("  → Hoeveel toetsen zijn nu rood?")
    time.sleep(3)

    # --- Test B: alles uit, dan chunks met byte2 = 0x10..0x17 ---
    print("[B] alles uit + chunks 0x10..0x17")
    send(fd, pad([0xCF, 0x01, 0x00] + [0, 0, 0] * 20, 65))
    time.sleep(0.2)
    for chunk in range(0x10, 0x18):
        payload = pad([0xCF, 0x01, chunk] + [R, G, B] * 20, 65)
        send(fd, payload)
        time.sleep(0.05)
    send(fd, [0xCE, 0x01, 0xFF])
    print("  → Andere toetsen rood dan bij A?")
    time.sleep(3)

    # --- Test C: chunks met byte1=0x00 (niet 0x01) ---
    print("[C] mode byte=0x00, chunks 0x00..0x07")
    for chunk in range(8):
        payload = pad([0xCF, 0x00, chunk] + [R, G, B] * 20, 65)
        send(fd, payload)
        time.sleep(0.05)
    send(fd, [0xCE, 0x00, 0xFF])
    print("  → Iets anders?")
    time.sleep(3)

    # --- Test D: reset (alles zwart) ---
    print("[D] reset: alles zwart")
    for chunk in range(8):
        payload = pad([0xCF, 0x01, chunk] + [0, 0, 0] * 20, 65)
        send(fd, payload)
        time.sleep(0.05)
    send(fd, [0xCE, 0x01, 0x00])
    time.sleep(1)

    # --- Test E: één toets tegelijk (positie 0..19 in chunk 0) ---
    print("[E] één toets tegelijk in chunk 0 (identificeer key-mapping)")
    print("  Elke 0.8s verandert één toets naar rood. Let op welke!")
    for key_idx in range(20):
        colors = [0, 0, 0] * 20
        colors[key_idx * 3]     = R
        colors[key_idx * 3 + 1] = G
        colors[key_idx * 3 + 2] = B
        payload = pad([0xCF, 0x01, 0x00] + colors, 65)
        send(fd, payload)
        send(fd, [0xCE, 0x01, 0xFF])
        print(f"    key_idx={key_idx:2d} → welke toets?")
        time.sleep(0.8)

    print("\nKlaar!")
