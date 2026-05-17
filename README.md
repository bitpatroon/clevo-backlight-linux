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
sudo python3 clevo_backlight.py animate rainbow          # animatie starten (zie ## Animaties)
sudo python3 clevo_backlight.py reload                   # herstel laatste opgeslagen state
sudo python3 clevo_backlight.py --dev /dev/hidraw5 color green  # ander device
```

**Voorinstelling kleuren:** `red`, `green`, `blue`, `white`, `yellow`, `cyan`, `magenta`, `orange`, `purple`

## Vlagkleuren

```bash
sudo python3 clevo_backlight.py flag nl   # Nederlandse vlag
sudo python3 clevo_backlight.py flag de   # Duitse vlag
sudo python3 clevo_backlight.py flag us   # Amerikaanse vlag
```

Vlagkleuren zijn opgeslagen als zones in `flags.json` (ISO 3166-1 alpha-2 codes). Horizontale vlaggen gebruiken `row1`–`row6`, verticale vlaggen `left`/`middle`/`right`. Complexe vlaggen (kruis, wapen) zijn vereenvoudigd tot de dominante kleuren.

**Beschikbare landen (73):**

| Regio | Codes |
|---|---|
| Europa | `al` `ad` `am` `at` `az` `ba` `be` `bg` `by` `ch` `cy` `cz` `de` `dk` `ee` `es` `fi` `fr` `gb` `ge` `gr` `hr` `hu` `ie` `is` `it` `li` `lt` `lu` `lv` `mc` `md` `me` `mk` `mt` `nl` `no` `pl` `pt` `ro` `rs` `ru` `se` `si` `sk` `sm` `tr` `ua` `va` `xk` |
| Noord-Amerika | `ag` `bb` `bs` `bz` `ca` `cr` `cu` `dm` `do` `gd` `gt` `hn` `ht` `jm` `kn` `lc` `mx` `ni` `pa` `sv` `tt` `us` `vc` |

De staat wordt opgeslagen als zone-configuratie, zodat `reload` de vlag herstelt.

## Animaties

Animaties worden in één stap per aanroep bijgezet. Eénmalig aanroepen zet één frame; de [animatie-daemon](#animatie-daemon) roept dit automatisch herhaaldelijk aan.

```bash
sudo python3 clevo_backlight.py animate rainbow              # één stap vooruit
sudo python3 clevo_backlight.py animate rainbow --reverse    # één stap achteruit
sudo python3 clevo_backlight.py animate                      # volgende stap van huidige animatie
sudo python3 clevo_backlight.py animate --reverse            # richting omdraaien
sudo python3 clevo_backlight.py animate ticker "HALLO!"      # ticker met eigen tekst
```

De richting (`--reverse`) wordt opgeslagen en blijft actief totdat je hem expliciet wijzigt — de daemon hoeft niets te weten van de richting.

### Beschikbare animaties

| Naam | Omschrijving |
|---|---|
| `rainbow` | Horizontale regenboog: elke kolom krijgt een andere tint uit het HSV-spectrum. De kleuren verschuiven één kolom per stap. |
| `wave` | Sinusgolf van helderheid over de kolommen. De basiskleur wordt overgenomen van de staat op het moment dat de animatie start (stel in met `solid` of `color`). |
| `matrix` | Vallende groene druppels, één per kolom. Elke druppel heeft een eigen willekeurige snelheid. Kop is helder wit-groen, staart vervaagt naar donkergroen. `--reverse` laat de druppels omhoog bewegen. |
| `pong` | Pong-simulatie over het volledige toetsenbord (20×6). Cyaanblauw batje links (kolom 0), oranje batje rechts (kolom 19), wit balletje. Beide batjes worden bestuurd door een AI die de bal volgt met beperkte snelheid. Het balletje kaatst af op de wanden en batjes; de hoek verandert afhankelijk van het raakpunt. |
| `ticker` | Scrollende tekstbalk (van rechts naar links) in een 3×5 pixel font. Standaardtekst: `CLEVO`. Tekstkleur is gebaseerd op de actieve kleur op het moment dat de animatie start. Rij 5 (onderste rij) blijft donker als baseline. |

### Basiskleur instellen voor wave

`wave` gebruikt de kleur die actief was vóór de animatie startte:

```bash
sudo python3 clevo_backlight.py solid 255 50 0   # oranje instellen
sudo python3 clevo_backlight.py animate wave      # oranje sinusgolf
```

### Animatie stoppen

```bash
sudo python3 clevo_backlight.py off     # stopt animatie en zet backlight uit
sudo python3 clevo_backlight.py solid 0 0 255  # stopt animatie, alles blauw
```

### Nieuwe animatie toevoegen

1. Schrijf een functie `apply_<naam>(fd, params=None)` in `clevo_backlight.py`
2. Voeg `'<naam>': apply_<naam>` toe aan de `ANIMATIONS`-dict

De functie ontvangt `params` met minimaal `phase` (float 0–1, stap 1/20 per aanroep) en `step` (richting: +1/20 of −1/20). Voor `wave` bevat `params` ook `color`.

---

## Animatie-daemon

`clevo_animate.py` roept automatisch `animate` aan met een vaste interval. Hij loopt alleen door als er een actieve animatie in de state staat — bij `off`, `solid` of `color` pauzeert hij vanzelf.

```bash
sudo python3 clevo_animate.py                       # standaard 200ms per stap
sudo python3 clevo_animate.py --interval 500        # 500ms per stap
sudo python3 clevo_animate.py --idle-timeout 60     # idle-timeout in seconden (standaard: 60)
sudo python3 clevo_animate.py --idle-timeout 0      # idle-timeout uitschakelen
sudo python3 clevo_animate.py --dev /dev/hidrawN
```

### Als systemd-service

```bash
sudo bash install.sh                                        # standaard 200ms, 1 min idle
sudo bash install.sh --interval 300                         # andere interval
sudo bash install.sh --idle-timeout 300                     # 5 minuten idle-timeout
sudo bash install.sh --idle-timeout 0                       # idle-timeout uitschakelen
sudo bash install.sh --interval 200 --dev /dev/hidrawN

sudo bash uninstall.sh                                      # verwijder service
```

De service start automatisch mee bij opstarten. De daemon bewaakt de state en gedraagt zich als volgt:

| Toestand | Actie |
|---|---|
| Animatie actief | Elke tick `animate` aanroepen |
| Animatie zojuist gestopt | Eénmalig `reload` uitvoeren (herstelt de vorige staat) |
| Geen animatie | Niets doen, gewoon wachten |
| Idle (geen input gedurende timeout) | Backlight uitzetten zonder state te wijzigen |
| Eerste invoer na idle | `reload` uitvoeren — herstelt exacte vorige staat |

Zo wordt bij `off` het backlight uit gezet zodra de animatie stopt, en bij `solid blue` keert de blauwe kleur terug.

### Idle-timeout

De daemon luistert via `/dev/input/event*` naar toetsenbord- en muisactiviteit. Na de ingestelde tijd zonder invoer (standaard 3 minuten) gaat het backlight uit. Bij de eerste toetsaanslag of muisbeweging wordt de vorige staat exact hersteld — inclusief animaties, zones en per-toets kleuren.

Handige commando's na installatie:

```bash
systemctl status clevo-animate
journalctl -u clevo-animate -f
systemctl stop clevo-animate
systemctl start clevo-animate
```

Workflow:

```bash
sudo python3 clevo_backlight.py animate rainbow  # animatie activeren
# daemon pikt dit op bij de volgende tick
sudo python3 clevo_backlight.py off              # daemon pauzeert vanzelf
```

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
