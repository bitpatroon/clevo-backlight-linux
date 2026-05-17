# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Keyboard backlight control for the **Clevo X370SNx** laptop on Linux. The backlight is driven by an ITE 8297 chip connected via USB (ID `048d:8910`), exposed as a HID device (`/dev/hidraw4`). No kernel module is needed.

The main tool is `clevo_backlight.py` — Python 3, standard library only.

## Running

```bash
sudo python3 clevo_backlight.py solid 255 0 0       # alles rood
sudo python3 clevo_backlight.py color blue           # voorinstelling
sudo python3 clevo_backlight.py off                  # uit
sudo python3 clevo_backlight.py brightness 128       # helderheid 0-255
sudo python3 clevo_backlight.py --dev /dev/hidrawN <cmd>  # ander device
```

## Protocol (bevestigd via HID Feature Reports)

- **Per toets**: `[0xCF, 0x01, <idx>, R, G, B]` + nul-padding tot 65 bytes
  - Verzonden met `fcntl.ioctl(fd, HIDIOCSFEATURE(65), buf)`
- **Commit**: `[0xCE, 0x01, <brightness>]` (3 bytes), brightness 0=uit, 0xFF=max
  - Verzonden met `fcntl.ioctl(fd, HIDIOCSFEATURE(3), buf)`
- **ioctl berekening**: `HIDIOCSFEATURE(n) = (3 << 30) | (n << 16) | (ord('H') << 8) | 6`

## Toetsindices

- Geldige indices: **0–191** (192 toetsen, 6 blokken van 32)
- Blokken: 0-31, 32-63, 64-95, 96-127, 128-159, 160-191
- Indices 192–255: geen fysieke toets (worden genegeerd door het device)

Bevestigd via experiment: blokken van 32 indices elk een andere kleur gegeven — 6 van de 8 kleuren waren zichtbaar, paars (192-223) en wit (224-255) niet.

## HID-device vinden

```bash
for d in /sys/class/hidraw/*/device/..;  do
    vid=$(cat "$d/idVendor" 2>/dev/null)
    pid=$(cat "$d/idProduct" 2>/dev/null)
    [ "$vid:$pid" = "048d:8910" ] && ls "${d%device/..}/hidraw/"
done
```

## Testscripts (historisch)

De `test_hid*.py` scripts zijn gebruikt om het protocol te ontdekken:
- `test_hid6.py` — definitief experiment dat indices 0–191 bevestigde
- Overige `test_hid*.py` — eerdere iteraties, niet meer nodig

## Wat NIET werkt op de X370SNx

- ACPI/WMI via `clevo-xsm-wmi` kernel module
- EC-mailbox (`0xCA`/`0xC4` via ECMD): retourneert AE_OK maar LED reageert niet
- `ECOK` in de DSDT is structureel 0 op dit systeem

De EC-route is dood code voor de X370SNx. De ITE-chip is een apart USB-apparaat.
