# Key mapping notatie — Clevo X370SNx

Key-namen worden opgeslagen in `mapping.json`. Dit bestand koppelt elke naam aan één of meerdere LED-indices (0–191).

## Notatie

| Type | Notatie | Voorbeelden |
|---|---|---|
| Letters | hoofdletter | `A`, `Z`, `Q` |
| Cijfers (hoofdrij) | `N` + cijfer | `N1`, `N0`, `N5` |
| Functietoetsen | `F` + nummer | `F1`, `F12` |
| Speciale toetsen | afkorting hoofdletters | `ESC`, `TAB`, `CAPS`, `ENTER`, `BACKSPACE`, `SPACE` |
| Modificateurs | hoofdletters | `LSHIFT`, `RSHIFT`, `LCTRL`, `RCTRL`, `ALT`, `ALTGR`, `FN`, `WIN`, `MENU` |
| Navigatie | hoofdletters | `INS`, `DEL`, `HOME`, `END`, `PGUP`, `PGDN`, `PRTSC` |
| Pijltoetsen | richting | `UP`, `DOWN`, `LEFT`, `RIGHT` |
| Symbooltoetsen | uitgeschreven naam | zie tabel hieronder |
| Numpad | `KP` + waarde | `KP0`–`KP9`, `KP_PLUS`, `KP_MINUS`, `KP_MUL`, `KP_SLASH`, `KP_ENTER`, `KP_DOT` |
| Numlock | `NUMLK` | |

### Symbooltoetsen

| Toets | Naam |
|---|---|
| `` ` `` | `GRAVE` |
| `-` | `MINUS` |
| `=` | `EQUALS` |
| `[` | `LBRACKET` |
| `]` | `RBRACKET` |
| `\` | `BACKSLASH` |
| `;` | `SEMICOLON` |
| `'` | `QUOTE` |
| `,` | `COMMA` |
| `.` | `DOT` |
| `/` | `SLASH` |

## Toetsen met meerdere LED's

Sommige toetsen beslaan fysiek meerdere LED-indices. Een naam spreekt alle bijbehorende indices aan tegelijk:

| Naam | Indices |
|---|---|
| `BACKSPACE` | 46, 47 |
| `TAB` | 64, 65 |
| `CAPS` | 96, 97 |
| `ENTER` | 110, 111 |
| `LSHIFT` | 128, 130 |
| `RSHIFT` | 141, 142 |
| `LCTRL` | 160, 161 |
| `RCTRL` | 172, 173 |
| `SPACE` | 165, 166, 168, 169 |
| `KP_PLUS` | 83, 115 |
| `KP_ENTER` | 147, 179 |

## Gebruik

```bash
# Per naam (mapping.json vereist)
sudo python3 clevo_backlight.py key A 255 0 0
sudo python3 clevo_backlight.py key ENTER 0 255 0
sudo python3 clevo_backlight.py key KP_PLUS 0 0 255

# Per index (altijd beschikbaar, zonder mapping.json)
sudo python3 clevo_backlight.py key 98 255 0 0
```

## State

Ingestelde per-toets kleuren worden opgeslagen in `clevo_backlight.json` onder de sleutel `keys`:

```json
{
  "color": [0, 0, 255],
  "brightness": 255,
  "default_color": [0, 0, 255],
  "keys": {
    "A": [255, 0, 0],
    "ENTER": [0, 255, 0]
  }
}
```

## Onbekende indices

Indices zonder naam in `mapping.json` (bijv. 20–31, 52–63) zijn onbekend — mogelijk decoratieve LED's of ongebruikte posities. Deze zijn direct via index benaderbaar:

```bash
sudo python3 clevo_backlight.py key 20 255 255 0
```
