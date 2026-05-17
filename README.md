# Clevo X370SNx Keyboard Backlight

Keyboard backlight control for the Clevo X370SNx laptop on Linux.

## How it works

On the X370SNx, keyboard backlight is controlled by an ITE 8297 chip connected via USB (ID `048d:8910`). The device appears as `/dev/hidraw4`. **No kernel module required.**

`clevo_backlight.py` uses Python 3 (standard library only) and sends HID Feature Reports directly to the chip.

## Usage

```bash
sudo python3 clevo_backlight.py solid 255 0 0           # alle toetsen één kleur (R G B)
sudo python3 clevo_backlight.py color blue              # voorinstelling
sudo python3 clevo_backlight.py off                     # backlight uit
sudo python3 clevo_backlight.py brightness 128          # helderheid (0-255)
sudo python3 clevo_backlight.py key W 255 0 0           # één toets op kleur (naam of index)
sudo python3 clevo_backlight.py zone gaming green       # zone op voorinstelling
sudo python3 clevo_backlight.py zone left 255 128 0     # zone op RGB
sudo python3 clevo_backlight.py reload                  # herstel laatste opgeslagen state
sudo python3 clevo_backlight.py --dev /dev/hidraw5 color green  # ander device
```

**Voorinstelling kleuren:** `red`, `green`, `blue`, `white`, `yellow`, `cyan`, `magenta`, `orange`, `purple`

## Shell-aliassen

Voeg dit toe aan `~/.bashrc` of `~/.zshrc` voor snelle toegang:

```bash
CLEVO="sudo python3 /pad/naar/clevo_backlight.py"

alias backlight-off="$CLEVO off"
alias backlight-white="$CLEVO color white"

alias gaming-red="$CLEVO zone gaming red"
alias gaming-green="$CLEVO zone gaming green"
alias gaming-blue="$CLEVO zone gaming blue"
alias gaming-white="$CLEVO zone gaming white"

alias left-red="$CLEVO zone left red"
alias left-green="$CLEVO zone left green"

alias numpad-cyan="$CLEVO zone numpad cyan"
alias numpad-off="$CLEVO zone numpad 0 0 0"
```

Herlaad daarna je shell: `source ~/.bashrc`

## HID-device vinden

```bash
for d in /sys/class/hidraw/*/device/..;  do
    vid=$(cat "$d/idVendor" 2>/dev/null)
    pid=$(cat "$d/idProduct" 2>/dev/null)
    [ "$vid:$pid" = "048d:8910" ] && ls "${d%device/..}/hidraw/"
done
```

Standaard is `/dev/hidraw4`. Gebruik `--dev` om dit te overschrijven.

## Protocol

| Operatie | HID Feature Report |
|---|---|
| Toetskleur instellen | `[0xCF, 0x01, <idx>, R, G, B, 0…]` uitgevuld tot 65 bytes |
| Commit (toepassen) | `[0xCE, 0x01, <brightness>]` — brightness: 0=uit, 0xFF=max |

Geldige toetsindices: **0–191** (192 toetsen totaal). Indices 192–255 hebben geen fysieke toets.

## ioctl

```python
HIDIOCSFEATURE(n) = (3 << 30) | (n << 16) | (ord('H') << 8) | 6
```

## Configuratiebestanden

### mapping.json

Koppelt key-namen aan één of meer LED-indices. Alle namen zijn hoofdletters.

```json
{
  "W":         [67],
  "ENTER":     [110, 111],
  "SPACE":     [165, 166, 168, 169]
}
```

Toetsen die fysiek meerdere LED's beslaan (TAB, CAPS, ENTER, SHIFT, SPACE, RCTRL, LCTRL, KP_PLUS, KP_ENTER) hebben meerdere indices — bij een `key`-commando worden ze allemaal tegelijk gezet. Zie `README-keymappings.md` voor de volledige naamconventie.

Indices 0–191 zijn geldig. Indices zonder naam (20–31, 52–63, 79, enz.) zijn onbekend of ongebruikt en zijn direct via numerieke index benaderbaar:

```bash
sudo python3 clevo_backlight.py key 20 255 255 0
```

### zones.json

Definieert zones als lijsten van key-namen. Zones worden gebruikt met het `zone`-commando:

```bash
sudo python3 clevo_backlight.py zone left red
sudo python3 clevo_backlight.py zone gaming 255 0 0
```

Beschikbare zones:

| Zone | Inhoud |
|---|---|
| `left` | ESC, F1–F4, cijferrij 1–4, QWER, ASDF, ZXCV, LCTRL/FN/WIN/ALT |
| `middle` | F5–F8, cijferrij 5–8, TYUI, GHJK, VBNM, SPACE |
| `right` | F9–F12, navigatieblok, cijferrij 9–0, PUIOP-rij, L-rij, numpad, pijltjes |
| `numpad` | NUMLK, KP_SLASH/MUL/MINUS, KP7–KP9, KP_PLUS, KP4–KP6, KP1–KP3, KP_ENTER, KP0, KP_DOT |
| `gaming` | TAB, QWER, ASDF, ZXCV, LSHIFT, LCTRL, ALT, SPACE, N1–N5, CAPS, G, pijltjes |
| `arrow` | WASD, pijltjes, KP2/4/6/8 |
| `functions` | F1–F12 |
| `special` | PRTSC, INS, DEL, HOME, END, PGUP, PGDN |
| `row1` | ESC, F1–F12, PRTSC, INS, DEL, HOME, END, PGUP, PGDN |
| `row2` | GRAVE, N1–N0, MINUS, EQUALS, BACKSPACE, NUMLK, KP_SLASH/MUL/MINUS |
| `row3` | TAB, Q–P, LBRACKET, RBRACKET, BACKSLASH, KP7–KP9, KP_PLUS |
| `row4` | CAPS, A–L, SEMICOLON, QUOTE, ENTER, KP4–KP6 |
| `row5` | LSHIFT, Z–M, COMMA, DOT, SLASH, RSHIFT, UP, KP1–KP3, KP_ENTER |
| `row6` | LCTRL, FN, WIN, ALT, SPACE, ALTGR, MENU, RCTRL, LEFT, DOWN, RIGHT, KP0, KP_DOT |

### clevo_backlight.json

Persistente state, opgeslagen naast het script. Wordt automatisch aangemaakt en bijgewerkt na elk commando.

```json
{
  "color":         [0, 0, 255],
  "brightness":    255,
  "default_color": [0, 0, 255],
  "keys": {
    "W": [255, 0, 0],
    "A": [255, 255, 0]
  },
  "zones": {
    "left":   [255, 0, 0],
    "middle": [255, 255, 255]
  }
}
```

`brightness` heeft geen directe hardware-waarde — het ITE-chip commit-byte kent alleen aan (0xFF) en uit (0x00). Dimmen werkt door de RGB-waarden te schalen met `brightness / 255`.

## License

GPL v2+
