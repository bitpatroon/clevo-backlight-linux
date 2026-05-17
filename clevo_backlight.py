#!/usr/bin/env python3
"""
Clevo X370SNx keyboard backlight — ITE 048d:8910 via USB HID.

Usage:
  clevo_backlight.py solid <R> <G> <B>              # alle toetsen één kleur (0-255)
  clevo_backlight.py color <naam>                   # voorgedefinieerde kleur
  clevo_backlight.py off                            # backlight uit
  clevo_backlight.py brightness <0-255>             # helderheid (schaalt de RGB-waarden)
  clevo_backlight.py key <naam|idx> <R> <G> <B>    # één toets op kleur
  clevo_backlight.py zone <zone> <naam|R> [G B]    # zone op kleur (left/middle/right)
  clevo_backlight.py animate [<naam>]                # animatie toepassen; zonder naam: volgende stap van huidige animatie
  clevo_backlight.py reload                         # herstel laatste opgeslagen state

Optie:
  --dev /dev/hidrawN   HID device (default: /dev/hidraw4)

Geldige kleurnamen: red, green, blue, white, yellow, cyan, magenta, orange, purple

State wordt opgeslagen in clevo_backlight.json naast dit script.
Key-namen staan in mapping.json, zones in zones.json (zie README-keymappings.md).
Het commit-byte van de ITE-chip werkt alleen als aan/uit-schakelaar (0=uit, 0xFF=aan).
Dimmen werkt door de RGB-waarden te schalen met het brightness-niveau.
"""
import fcntl, sys, os, json, colorsys

HIDRAW_DEFAULT = '/dev/hidraw4'
SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
STATE_FILE     = os.path.join(SCRIPT_DIR, 'clevo_backlight.json')
MAPPING_FILE   = os.path.join(SCRIPT_DIR, 'mapping.json')
ZONES_FILE     = os.path.join(SCRIPT_DIR, 'zones.json')
NUM_KEYS       = 192   # indices 0-191 dekken alle fysieke toetsen

COLORS = {
    'red':     (255,   0,   0),
    'green':   (  0, 255,   0),
    'blue':    (  0,   0, 255),
    'white':   (255, 255, 255),
    'yellow':  (255, 255,   0),
    'cyan':    (  0, 255, 255),
    'magenta': (255,   0, 255),
    'orange':  (255, 165,   0),
    'purple':  (128,   0, 255),
}

DEFAULT_STATE = {
    'color':         [0, 0, 255],
    'brightness':    255,
    'default_color': [0, 0, 255],
    'keys':          {},
    'zones':         {},
    'preset':        None,
    'preset_params': {},
}

# --- HID -----------------------------------------------------------------

def HIDIOCSFEATURE(n):
    return (3 << 30) | (n << 16) | (ord('H') << 8) | 6

def set_key(fd, idx, r, g, b):
    buf = (bytearray([0xCF, 0x01, idx, r, g, b]) + bytearray(65))[:65]
    fcntl.ioctl(fd, HIDIOCSFEATURE(65), buf)

def commit(fd, on=True):
    # brightness-byte: 0=uit, 0xFF=aan — geen tussenwaarden
    buf = bytearray([0xCE, 0x01, 0xFF if on else 0x00])
    fcntl.ioctl(fd, HIDIOCSFEATURE(3), buf)

def set_all(fd, r, g, b, on=True):
    for i in range(NUM_KEYS):
        set_key(fd, i, r, g, b)
    commit(fd, on)

def apply_rainbow(fd, params=None):
    # Kolompositie = index % 32 (0-19 zijn zichtbare toetsen per rij)
    # Hue verdeelt de volle regenboog over 20 kolommen; phase schuift de positie op
    phase = (params or {}).get('phase', 0.0)
    for i in range(NUM_KEYS):
        hue = ((i % 32) / 20.0 + phase) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        set_key(fd, i, int(r * 255), int(g * 255), int(b * 255))
    commit(fd)

ANIMATIONS = {
    'rainbow': apply_rainbow,
}

# --- State ---------------------------------------------------------------

def load_state():
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        for key, val in DEFAULT_STATE.items():
            state.setdefault(key, val)
        return state
    except Exception:
        return dict(DEFAULT_STATE)

def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
            f.write('\n')
    except OSError as e:
        print(f"Waarschuwing: kan state niet opslaan: {e}", file=sys.stderr)

# --- Mapping -------------------------------------------------------------

def load_mapping():
    try:
        with open(MAPPING_FILE) as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith('_')}
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Waarschuwing: kan mapping.json niet lezen: {e}", file=sys.stderr)
        return {}

def load_zones():
    try:
        with open(ZONES_FILE) as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith('_')}
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Waarschuwing: kan zones.json niet lezen: {e}", file=sys.stderr)
        return {}

def resolve_key(key_arg, mapping):
    """Geeft (key_name, [indices]) terug, of stopt met een foutmelding."""
    if key_arg.isdigit():
        idx = int(key_arg)
        if not 0 <= idx <= 191:
            print(f"Fout: index {idx} buiten bereik (0-191).")
            sys.exit(1)
        return key_arg, [idx]

    name = key_arg.upper()
    if not mapping:
        print("Fout: mapping.json niet gevonden. Gebruik een numerieke index (0-191).")
        sys.exit(1)
    if name not in mapping:
        print(f"Fout: '{name}' niet gevonden in mapping.json.")
        print(f"Bekende namen: {', '.join(sorted(mapping))}")
        sys.exit(1)
    return name, mapping[name]

# --- Main ----------------------------------------------------------------

def main():
    args = sys.argv[1:]
    dev = HIDRAW_DEFAULT

    if '--dev' in args:
        i = args.index('--dev')
        dev = args[i + 1]
        args = args[:i] + args[i + 2:]

    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if not os.path.exists(dev):
        print(f"Fout: {dev} niet gevonden. Gebruik --dev om het juiste hidraw-apparaat op te geven.")
        sys.exit(1)

    with open(dev, 'rb+', buffering=0) as f:
        fd = f.fileno()

        if cmd == 'solid':
            if len(args) != 4:
                print("Gebruik: solid <R> <G> <B>")
                sys.exit(1)
            r, g, b = int(args[1]), int(args[2]), int(args[3])
            state = load_state()
            state['color'] = [r, g, b]
            state['keys'] = {}
            state['zones'] = {}
            state['preset'] = None
            state['preset_params'] = {}
            save_state(state)
            set_all(fd, r, g, b)

        elif cmd == 'color':
            if len(args) != 2 or args[1] not in COLORS:
                print(f"Onbekende kleur. Kies uit: {', '.join(COLORS)}")
                sys.exit(1)
            r, g, b = COLORS[args[1]]
            state = load_state()
            state['color'] = [r, g, b]
            state['keys'] = {}
            state['zones'] = {}
            state['preset'] = None
            state['preset_params'] = {}
            save_state(state)
            set_all(fd, r, g, b)

        elif cmd == 'off':
            set_all(fd, 0, 0, 0, on=False)
            state = load_state()
            state['color'] = [0, 0, 0]
            state['keys'] = {}
            state['zones'] = {}
            state['preset'] = None
            state['preset_params'] = {}
            save_state(state)

        elif cmd == 'brightness':
            if len(args) != 2:
                print("Gebruik: brightness <0-255>")
                sys.exit(1)
            level = int(args[1])
            state = load_state()
            state['brightness'] = level
            save_state(state)
            r, g, b = state['color']
            factor = level / 255.0
            set_all(fd, int(r * factor), int(g * factor), int(b * factor))

        elif cmd == 'key':
            if len(args) != 5:
                print("Gebruik: key <naam|idx> <R> <G> <B>")
                sys.exit(1)
            mapping = load_mapping()
            key_name, indices = resolve_key(args[1], mapping)
            r, g, b = int(args[2]), int(args[3]), int(args[4])
            for idx in indices:
                set_key(fd, idx, r, g, b)
            commit(fd)
            state = load_state()
            state['keys'][key_name] = [r, g, b]
            save_state(state)

        elif cmd == 'zone':
            # zone <naam> <color|R> [G B]
            if len(args) not in (3, 5):
                print("Gebruik: zone <zone> <kleurnaam>  of  zone <zone> <R> <G> <B>")
                sys.exit(1)
            zone_name = args[1].lower()
            zones = load_zones()
            if not zones:
                print("Fout: zones.json niet gevonden.")
                sys.exit(1)
            if zone_name not in zones:
                print(f"Fout: zone '{zone_name}' niet gevonden. Beschikbaar: {', '.join(zones)}")
                sys.exit(1)
            if len(args) == 3:
                color_arg = args[2]
                if color_arg not in COLORS:
                    print(f"Onbekende kleur. Kies uit: {', '.join(COLORS)}")
                    sys.exit(1)
                r, g, b = COLORS[color_arg]
            else:
                r, g, b = int(args[2]), int(args[3]), int(args[4])
            mapping = load_mapping()
            for key_name in zones[zone_name]:
                _, indices = resolve_key(key_name, mapping)
                for idx in indices:
                    set_key(fd, idx, r, g, b)
            commit(fd)
            state = load_state()
            state['zones'][zone_name] = [r, g, b]
            save_state(state)

        elif cmd == 'animate':
            state = load_state()
            if len(args) == 1:
                name = state.get('preset')
                if name not in ANIMATIONS:
                    print(f"Geen actieve animatie. Gebruik: animate <naam>. Kies uit: {', '.join(ANIMATIONS)}")
                    sys.exit(1)
            elif args[1] not in ANIMATIONS:
                print(f"Onbekende animatie. Kies uit: {', '.join(ANIMATIONS)}")
                sys.exit(1)
            else:
                name = args[1]
            params = state.get('preset_params', {}) if state.get('preset') == name else {}
            params = dict(params)
            params['phase'] = (params.get('phase', 0.0) + 1 / 20) % 1.0
            ANIMATIONS[name](fd, params)
            state['color'] = [0, 0, 0]
            state['keys'] = {}
            state['zones'] = {}
            state['preset'] = name
            state['preset_params'] = params
            save_state(state)

        elif cmd == 'reload':
            state = load_state()
            if state.get('preset') in ANIMATIONS:
                ANIMATIONS[state['preset']](fd, state.get('preset_params', {}))
            else:
                mapping = load_mapping()
                zones = load_zones()
                r, g, b = state['color']
                factor = state['brightness'] / 255.0
                br, bg, bb = int(r * factor), int(g * factor), int(b * factor)
                for i in range(NUM_KEYS):
                    set_key(fd, i, br, bg, bb)
                for zone_name, (zr, zg, zb) in state.get('zones', {}).items():
                    if zone_name not in zones:
                        continue
                    for key_name in zones[zone_name]:
                        for idx in mapping.get(key_name.upper(), []):
                            set_key(fd, idx, zr, zg, zb)
                for key_name, (kr, kg, kb) in state.get('keys', {}).items():
                    for idx in mapping.get(key_name.upper(), []):
                        set_key(fd, idx, kr, kg, kb)
                commit(fd)

        else:
            print(f"Onbekend commando: {cmd}")
            print(__doc__)
            sys.exit(1)

if __name__ == '__main__':
    main()
