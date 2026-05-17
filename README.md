# Clevo X370SNx Keyboard Backlight

Keyboard backlight control for the Clevo X370SNx laptop on Linux.

## How it works

On the X370SNx, keyboard backlight is controlled by an ITE 8297 chip connected via USB (ID `048d:8910`). The device appears as `/dev/hidraw4`. **No kernel module required.**

`clevo_backlight.py` uses Python 3 (standard library only) and sends HID Feature Reports directly to the chip.

## Usage

```bash
sudo python3 clevo_backlight.py solid 255 0 0       # alle toetsen rood (R G B, 0-255)
sudo python3 clevo_backlight.py color blue           # voorinstelling
sudo python3 clevo_backlight.py off                  # backlight uit
sudo python3 clevo_backlight.py brightness 128       # helderheid (0-255)
sudo python3 clevo_backlight.py --dev /dev/hidraw5 color green  # ander device
```

**Voorinstelling kleuren:** `red`, `green`, `blue`, `white`, `yellow`, `cyan`, `magenta`, `orange`, `purple`

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

## License

GPL v2+
