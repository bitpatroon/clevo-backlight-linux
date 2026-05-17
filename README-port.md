# Nieuw model toevoegen

Stappenplan om `clevo_backlight.py` werkend te krijgen op een ander Clevo-model (of een andere laptop met een ITE-backlight-chip via USB HID).

## Aannames

Het script gaat ervan uit dat de backlight-chip:
- als USB HID-apparaat verschijnt (te zien via `lsusb`)
- Feature Reports accepteert op report-IDs `0xCF` (toetskleur) en `0xCE` (commit)

Als het apparaat een andere aansturing gebruikt (ACPI, WMI, EC), werkt dit script niet zonder aanpassingen. Zie de sectie **Wat NIET werkt** in `README.md` voor achtergrond.

---

## Stap 1: HID-apparaat vinden

Zoek het USB-apparaat:

```bash
lsusb | grep -i ITE
lsusb | grep -i keyboard
```

Noteer de `idVendor:idProduct` (bijv. `048d:6004`). Zoek dan het bijbehorende hidraw-apparaat:

```bash
for d in /sys/class/hidraw/*/device/..; do
    vid=$(cat "$d/idVendor" 2>/dev/null)
    pid=$(cat "$d/idProduct" 2>/dev/null)
    echo "$vid:$pid  →  $(ls "${d%device/..}/hidraw/" 2>/dev/null)"
done
```

Noteer het hidraw-pad (bijv. `/dev/hidraw2`). Test of je er toegang toe hebt:

```bash
sudo python3 -c "open('/dev/hidrawN', 'rb+')"
```

---

## Stap 2: Protocol testen

Probeer het bestaande protocol. Zet alle toetsen op rood:

```bash
sudo python3 clevo_backlight.py --dev /dev/hidrawN solid 255 0 0
```

**Werkt het?** Dan is de ITE-chip compatibel en kun je doorgaan naar stap 3.

**Geen reactie?** Gebruik `archive/test_hid.py` als diagnostisch startpunt. Het script test meerdere report-varianten en toont welke een `ioctl`-fout geeft. Pas het device-pad bovenin het bestand aan:

```bash
sudo python3 archive/test_hid.py 255 0 0
```

Als geen enkel report reageert, heeft dit model waarschijnlijk een ander protocol. Gebruik dan `usbhid-dump` om de HID-descriptor te inspecteren:

```bash
sudo usbhid-dump -d <vid>:<pid>
```

---

## Stap 3: Index-bereik bepalen

Bepaal hoeveel toets-indices het keyboard heeft. Gebruik de blok-test techniek uit `archive/test_hid6.py`: geef elke 32 indices een andere kleur en tel hoeveel blokken zichtbaar zijn.

Pas het script tijdelijk aan voor het juiste device-pad en voer het uit:

```bash
sudo python3 archive/test_hid6.py
```

Tel de zichtbare kleuren. 6 kleuren = 192 indices (0–191), 8 kleuren = 256 indices, enz. Noteer de waarde als `NUM_KEYS`.

---

## Stap 4: Indices mappen

Breng in kaart welke index bij welke toets hoort. Gebruik `test.sh` om per index een toets op te lichten:

```bash
bash test.sh <startindex> <seconden>   # bijv. test.sh 0 2
```

Het script licht 10 opeenvolgende indices op. Noteer per index welke toets brandt. Leg de volledige lijst vast in `docs/mappings_<model>.txt` (zie `docs/mappings2.txt` als voorbeeld).

Sommige indices hebben geen fysieke toets — sla deze over.

---

## Stap 5: mapping.json aanmaken

Maak een `mapping.json` op basis van je bevindingen. Volg de naamconventie uit `README-keymappings.md`:

```json
{
  "_comment": "Key name → lijst van LED-indices. Model: <modelnaam>",

  "ESC":   [0],
  "F1":    [1],
  "A":     [30],
  "ENTER": [55, 56]
}
```

Toetsen met meerdere indices (grote toetsen zoals ENTER, SHIFT, SPACE) krijgen een lijst van alle bijbehorende indices.

Verifieer de mapping:

```bash
sudo python3 clevo_backlight.py --dev /dev/hidrawN key A 255 0 0
sudo python3 clevo_backlight.py --dev /dev/hidrawN key ENTER 0 255 0
```

---

## Stap 6: zones.json aanmaken

Definieer zones als lijsten van key-namen. Gebruik dezelfde zonenamen als het bestaande bestand (`left`, `middle`, `right`) zodat scripts herbruikbaar blijven, of voeg modelspecifieke zones toe:

```json
{
  "_comment": "Zone-definities. Model: <modelnaam>",

  "left":   ["ESC", "F1", "F2", "TAB", "Q", "W", ...],
  "middle": ["F5", "F6", "T", "Y", "G", "H", ...],
  "right":  ["F9", "F10", "F11", "F12", "P", ...]
}
```

Verifieer:

```bash
sudo python3 clevo_backlight.py --dev /dev/hidrawN zone left red
sudo python3 clevo_backlight.py --dev /dev/hidrawN zone right blue
```

---

## Stap 7: Script aanpassen

Pas de twee constanten bovenin `clevo_backlight.py` aan:

```python
HIDRAW_DEFAULT = '/dev/hidrawN'   # jouw hidraw-pad
NUM_KEYS       = 192              # jouw index-bereik uit stap 3
```

Test daarna zonder `--dev`:

```bash
sudo python3 clevo_backlight.py color green
sudo python3 clevo_backlight.py off
```

---

## Checklist

- [ ] HID-apparaat gevonden (`/dev/hidrawN`, VID:PID genoteerd)
- [ ] Protocol reageert (`solid` commando werkt)
- [ ] Index-bereik bepaald (`NUM_KEYS` ingesteld)
- [ ] Alle indices gemapped in `docs/mappings_<model>.txt`
- [ ] `mapping.json` aangemaakt en getest met `key`-commando
- [ ] `zones.json` aangemaakt en getest met `zone`-commando
- [ ] `HIDRAW_DEFAULT` en `NUM_KEYS` bijgewerkt in `clevo_backlight.py`
