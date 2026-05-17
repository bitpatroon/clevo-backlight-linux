#!/usr/bin/env python3
"""
Clevo animatie-daemon — roept clevo_backlight.py animate aan elke <interval> ms.
Pauzeert automatisch als er geen actieve animatie in de state staat.

Gebruik:
  sudo python3 clevo_animate.py
  sudo python3 clevo_animate.py --interval 200   # ms tussen stappen (standaard: 200)
  sudo python3 clevo_animate.py --dev /dev/hidrawN

Stop met Ctrl+C of SIGTERM.
"""
import sys, os, time, signal, json, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, 'clevo_backlight.json')
BACKLIGHT  = os.path.join(SCRIPT_DIR, 'clevo_backlight.py')
DEFAULT_MS = 200

def active_preset():
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get('preset')
    except Exception:
        return None

def main():
    args = sys.argv[1:]
    interval_ms = DEFAULT_MS
    dev_args = []

    def pop(flag):
        if flag in args:
            i = args.index(flag)
            val = args[i + 1]
            del args[i:i + 2]
            return val
        return None

    v = pop('--interval')
    if v:
        interval_ms = int(v)
    v = pop('--dev')
    if v:
        dev_args = ['--dev', v]

    running = True
    def stop(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    interval = interval_ms / 1000.0
    was_animating = False

    while running:
        if active_preset():
            subprocess.run(
                [sys.executable, BACKLIGHT] + dev_args + ['animate'],
                check=False
            )
            was_animating = True
        elif was_animating:
            subprocess.run(
                [sys.executable, BACKLIGHT] + dev_args + ['reload'],
                check=False
            )
            was_animating = False
        time.sleep(interval)

if __name__ == '__main__':
    main()
