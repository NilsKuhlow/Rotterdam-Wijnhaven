# -*- coding: utf-8 -*-
"""Die Zeichnung von 1946 neu zeichnen.

Die erste Fassung waren drei dicke Leuchtbalken und eine getoente Flaeche:
ein Textmarker ueber dem Plan, keine Zeichnung. Diese Fassung arbeitet mit
den Mitteln, die eine Planzeichnung hat.

  Achsen      ein breites Band in Hausgelb, darin die Achslinie als feiner
              Strich. Das Band traegt die Breite, die Linie die Fuehrung.
              Der Coolsingel bekommt seine belegten 80 m massstaeblich,
              Blaak und Boompjes bleiben schmaler und behaupten kein Mass.
  Zone        Schraffur statt Tonflaeche. Eine Schraffur bezeichnet eine
              Festlegung und laesst den Schwarzplan darunter stehen.
  Hofplein    ein Ring mit Kern, das uebliche Zeichen fuer einen Kreisel.
  Fenster     zwei Linien, die sich zur Maas hin oeffnen, mit Pfeilspitze.
  Legende     als HTML neben den Schaltern, nicht im Koordinatenraum. Eine
              Legende im Plan wuerde beim Zoomen mitwachsen.

Alle Masse in Zeicheneinheiten, 1 m = 0,7664 Einheiten.
"""
import io
import os
import re
import sys

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
P = os.path.join(REPO, 'index.html')

M = 0.7664240847195386          # Zeicheneinheiten je Meter

COOLSINGEL = "M718 544 L755 756 L787 985 L808 1163 L824 1256"
BLAAK = "M603 1180 L876 1103 L1139 1052 L1455 1027 L1750 959 L1887 866"
BOOMPJES = "M1260 1518 L1445 1459 L1655 1366 L1855 1281"
ZONE = "M1308 1095 L1539 1052 L1608 1247 L1455 1391 L1308 1315 Z"

CSS_NEU = """
/* Die Zeichnung von 1946. Mittel einer Planzeichnung: Band und Achslinie,
   Schraffur fuer die Festlegung, Ring fuer den Kreisel. */
.ov-band   { fill:none; stroke:var(--accent); stroke-opacity:.42;
             stroke-linecap:butt; stroke-linejoin:round; }
.ov-achse  { fill:none; stroke:var(--ink-1); stroke-opacity:.55; stroke-width:1.6;
             stroke-dasharray:22 10 4 10; stroke-linecap:butt; }
.ov-zone   { fill:url(#ov-schraffur); stroke:var(--ink-1); stroke-width:2.2; }
.ov-ring   { fill:var(--paper-0); stroke:var(--ink-1); stroke-width:3.5; }
.ov-kern   { fill:var(--accent); stroke:none; }
.ov-korr   { fill:none; stroke:var(--ink-1); stroke-width:2.2; }
.ov-text   { font-family:var(--font-mono); font-size:17px; letter-spacing:1.4px;
             fill:var(--ink-1); paint-order:stroke; stroke:var(--paper-0);
             stroke-width:5; stroke-linejoin:round; }
.ov-text.klein { font-size:14px; }
.ov-fuehr  { stroke:var(--ink-1); stroke-width:1.4; fill:none; }
/* Legende, als HTML neben den Schaltern: im Plan wuerde sie mitzoomen. */
#eb-legende { display:none; gap:.5rem 1rem; flex-wrap:wrap; align-items:center;
  background:rgba(255,255,255,.92); padding:.45rem .6rem; max-width:26rem; }
#ebenen.zeigt-1946 #eb-legende { display:flex; }
.lg-eintrag { display:flex; align-items:center; gap:.4rem;
  font-family:var(--font-mono); font-size:.52rem; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-2); white-space:nowrap; }
.lg-probe { width:22px; height:11px; flex:0 0 auto; border:1px solid var(--ink-1); }
.lg-probe.band { background:rgba(255,237,41,.45); border-color:rgba(10,10,10,.25); }
.lg-probe.zone { background:repeating-linear-gradient(45deg, var(--ink-1) 0 1px,
  transparent 1px 5px); }
.lg-probe.ring { border-radius:50%; width:12px; height:12px; background:var(--accent); }
"""

ZEICHNUNG = """<g id="ov-1946" hidden aria-hidden="true">
  <defs>
    <pattern id="ov-schraffur" patternUnits="userSpaceOnUse" width="14" height="14"
             patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="14" stroke="#0A0A0A" stroke-width="1.4" stroke-opacity=".5"/>
    </pattern>
    <marker id="ov-pfeil" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5"
            markerHeight="5" orient="auto-start-reverse">
      <path d="M0 1 L9 5 L0 9 Z" fill="#0A0A0A"/>
    </marker>
  </defs>

  <!-- Die drei Achsen des Basisplans. Band = Breite, Linie = Fuehrung.
       Der Coolsingel traegt seine belegten 80 m massstaeblich (61 Einheiten). -->
  <path class="ov-band"  style="stroke-width:61.3" d="{cool}"/>
  <path class="ov-band"  style="stroke-width:34.5" d="{blaak}"/>
  <path class="ov-band"  style="stroke-width:30.7" d="{boomp}"/>
  <path class="ov-achse" d="{cool}"/>
  <path class="ov-achse" d="{blaak}"/>
  <path class="ov-achse" d="{boomp}"/>

  <!-- Das Wijnhavengebiet, im Basisplan den Bueros der Schifffahrt zugewiesen.
       Schraffur statt Tonflaeche: der Schwarzplan bleibt darunter lesbar. -->
  <path class="ov-zone" d="{zone}"/>

  <!-- Hofplein, Kreisel am Kopf des Coolsingel -->
  <circle class="ov-ring" cx="718" cy="544" r="26"/>
  <circle class="ov-kern" cx="718" cy="544" r="9"/>

  <!-- Fenster zum Fluss am Leuvehaven: der Plan hielt hier die Sicht frei. -->
  <path class="ov-korr" marker-end="url(#ov-pfeil)" d="M1168 1150 L1150 1500"/>
  <path class="ov-korr" marker-end="url(#ov-pfeil)" d="M1262 1140 L1286 1492"/>

  <!-- Beschriftung. Fuehrungsstriche, damit die Worte neben der Sache stehen
       und nicht auf den Stationspunkten. -->
  <path class="ov-fuehr" d="M744 544 L812 520"/>
  <text class="ov-text" x="820" y="524" text-anchor="start">HOFPLEIN</text>
  <path class="ov-fuehr" d="M800 900 L872 884"/>
  <text class="ov-text" x="880" y="888" text-anchor="start">COOLSINGEL 80 M</text>
  <text class="ov-text" x="1700" y="968" text-anchor="middle">BLAAK</text>
  <text class="ov-text" x="1772" y="1318" text-anchor="middle">BOOMPJES</text>
  <path class="ov-fuehr" d="M1150 1330 L1066 1330"/>
  <text class="ov-text klein" x="1058" y="1334" text-anchor="end">FENSTER ZUM FLUSS</text>
  <text class="ov-text klein" x="1455" y="1232" text-anchor="middle">WIJNHAVEN</text>
  <text class="ov-text klein" x="1455" y="1254" text-anchor="middle">BUEROQUARTIER 1946</text>
</g>""".format(cool=COOLSINGEL, blaak=BLAAK, boomp=BOOMPJES, zone=ZONE)

LEGENDE = """  <div id="eb-legende" aria-hidden="true">
    <span class="lg-eintrag"><span class="lg-probe band"></span>Verkehrsachse</span>
    <span class="lg-eintrag"><span class="lg-probe zone"></span>Bueroquartier</span>
    <span class="lg-eintrag"><span class="lg-probe ring"></span>Hofplein</span>
  </div>
"""


def main():
    s = io.open(P, encoding='utf-8').read()
    log = []

    # ── 1. Alte Zeichnung ersetzen ───────────────────────────────────────
    m = re.search(r'<g id="ov-1946".*?</g>\n', s, re.S)
    if not m:
        sys.exit('FEHLER: alte Zeichnung nicht gefunden')
    einzug = '\n'.join('    ' + z if z.strip() else z for z in ZEICHNUNG.split('\n'))
    s = s[:m.start()] + einzug.lstrip() + '\n' + s[m.end():]
    log.append('Zeichnung neu: Band und Achse, Schraffur, Ring, Fuehrungsstriche')

    # ── 2. Altes CSS der Ebene ersetzen ──────────────────────────────────
    a = s.index('/* Die Zeichnung selbst */')
    b = s.index('/* ═══════════════════════════════════════════\n   BASISPLAN + FAZIT')
    s = s[:a] + CSS_NEU.strip() + '\n\n' + s[b:]
    log.append('CSS der Zeichnung ersetzt, Legende ergaenzt')

    # ── 3. Legende in die Schalterleiste ─────────────────────────────────
    anker = '  <p class="eb-quelle" id="eb-quelle" hidden></p>'
    if s.count(anker) != 1:
        sys.exit('FEHLER: Quellenzeile nicht eindeutig')
    s = s.replace(anker, LEGENDE + anker)
    log.append('Legende in die Schalterleiste')

    # ── 4. Legende mit der Ebene schalten ────────────────────────────────
    alt = """  _ebeneAktiv = neu;
  _ebeneQuelle();"""
    neu = """  _ebeneAktiv = neu;
  var box = document.getElementById('ebenen');
  if (box) box.classList.toggle('zeigt-1946', neu === 'ov-1946');
  _ebeneQuelle();"""
    if s.count(alt) != 1:
        sys.exit('FEHLER: ebeneUm nicht gefunden')
    s = s.replace(alt, neu)
    log.append('JS: Legende folgt der Ebene')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\n'.join('OK  ' + x for x in log))


if __name__ == '__main__':
    main()
