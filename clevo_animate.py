#!/usr/bin/env python3
"""
Clevo animatie-daemon — roept clevo_backlight.py animate aan elke <interval> ms.
Pauzeert automatisch als er geen actieve animatie in de state staat.
Schakelt backlight uit na <idle-timeout> seconden inactiviteit op toetsenbord/muis.

Gebruik:
  sudo python3 clevo_animate.py
  sudo python3 clevo_animate.py --interval 200       # ms tussen stappen (standaard: 200)
  sudo python3 clevo_animate.py --dev /dev/hidrawN
  sudo python3 clevo_animate.py --idle-timeout 180   # seconden; 0 = uitgeschakeld (standaard: 180)

Stop met Ctrl+C of SIGTERM.
"""
import sys, os, time, signal, json, subprocess, glob, select

SCRIPT_DIR       = os.path.dirname(os.path.abspath(__file__))
STATE_FILE       = os.path.join(SCRIPT_DIR, 'clevo_backlight.json')
BACKLIGHT        = os.path.join(SCRIPT_DIR, 'clevo_backlight.py')
DEFAULT_MS       = 200
DEFAULT_IDLE_S   = 60
INPUT_EVENT_SIZE = 24  # 64-bit Linux: timeval(8+8) + type(2) + code(2) + value(4)

def active_preset():
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get('preset')
    except Exception:
        return None

def open_input_devices():
    fds = []
    for path in sorted(glob.glob('/dev/input/event*')):
        try:
            fds.append(open(path, 'rb', buffering=0))
        except OSError:
            pass
    return fds

def drain_input(input_fds):
    """Verwijder pending input-events; geeft True als er activiteit was."""
    if not input_fds:
        return False
    readable, _, _ = select.select(input_fds, [], [], 0)
    for f in readable:
        try:
            f.read(INPUT_EVENT_SIZE)
        except OSError:
            pass
    return bool(readable)

def main():
    args = sys.argv[1:]
    interval_ms  = DEFAULT_MS
    idle_timeout = DEFAULT_IDLE_S
    dev_args     = []

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
    v = pop('--idle-timeout')
    if v:
        idle_timeout = int(v)

    running = True
    def stop(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    interval      = interval_ms / 1000.0
    was_animating = False
    is_idle       = False
    last_activity = time.time()
    input_fds     = open_input_devices() if idle_timeout > 0 else []

    while running:
        if idle_timeout > 0:
            if drain_input(input_fds):
                last_activity = time.time()
                if is_idle:
                    is_idle = False
                    subprocess.run(
                        [sys.executable, BACKLIGHT] + dev_args + ['reload'],
                        check=False
                    )

            if not is_idle and (time.time() - last_activity) > idle_timeout:
                is_idle = True
                subprocess.run(
                    [sys.executable, BACKLIGHT] + dev_args + ['idle-off'],
                    check=False
                )

        if not is_idle:
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
