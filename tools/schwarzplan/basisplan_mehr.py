# -*- coding: utf-8 -*-
"""Mehr vom Basisplan in die Zeichnung.

Bisher standen drei Achsen, eine Zone und zwei Zeichen darin. Der Plan von
1946 besteht aber aus mehr, und vor allem fehlte das, was ihn ueberhaupt
erklaert: die Grenze des zerstoerten Gebiets.

Neu in der Zeichnung:

  Brandgrens   der Umriss der Flaeche, die am 14. Mai 1940 ausbrannte. Sie
               ist der Grund fuer alles Folgende: Der Basisplan baut genau
               das wieder auf, was hier verbrannte. Rotterdam markiert sie
               heute mit einer Lichtlinie im Pflaster.
  Weena        die Nord-Achse zum Hauptbahnhof
  Westblaak    die Fortsetzung des Blaak nach Westen
  Goudsesingel die Nordost-Achse
  Lijnbaan     das Einkaufszentrum, 1953 als erste Fussgaengergeschaeftsstrasse
               Europas gebaut und unmittelbares Ergebnis des Plans

Alle Verlaeufe sind von Hand aus Koordinaten gesetzt und schematisch. Die
Quellenzeile sagt das; die Zeichnung zeigt das Prinzip des Plans, nicht
seine Parzellen.
"""
import io
import os
import re
import sys

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
P = os.path.join(REPO, 'index.html')

LON0, LAT0 = 4.460351, 51.931723
MLON, MLAT = 68671.61405376215, 110540.0
K = 0.7664240847195386


def xy(lat, lon):
    return ((lon - LON0) * MLON * K, (LAT0 - lat) * MLAT * K)


def d(punkte, zu=False):
    s = ' '.join(('M' if i == 0 else 'L') + '%.0f %.0f' % xy(*p)
                 for i, p in enumerate(punkte))
    return s + (' Z' if zu else '')


# ── Die Brandgrenze, Umriss der 1940 ausgebrannten Innenstadt ────────────
BRANDGRENS = [
 (51.92490, 4.47400), (51.92470, 4.48100), (51.92320, 4.48780), (51.92120, 4.49420),
 (51.91780, 4.49580), (51.91500, 4.48900), (51.91350, 4.48400), (51.91390, 4.48200),
 (51.91680, 4.47800), (51.91780, 4.47450), (51.92050, 4.47120), (51.92320, 4.47000),
]

# ── Achsen ───────────────────────────────────────────────────────────────
COOLSINGEL = [(51.92530, 4.47400), (51.92280, 4.47470), (51.92010, 4.47530),
              (51.91800, 4.47570), (51.91690, 4.47600)]
BLAAK = [(51.91780, 4.47180), (51.91870, 4.47700), (51.91930, 4.48200),
         (51.91960, 4.48800), (51.92040, 4.49360), (51.92150, 4.49620)]
BOOMPJES = [(51.91380, 4.48430), (51.91450, 4.48780), (51.91560, 4.49180),
            (51.91660, 4.49560)]
WEENA = [(51.92450, 4.46900), (51.92480, 4.47400), (51.92460, 4.47900),
         (51.92420, 4.48280)]
GOUDSESINGEL = [(51.92470, 4.48100), (51.92320, 4.48780), (51.92180, 4.49280)]
LEUVEHAVEN = [(51.91780, 4.48330), (51.91430, 4.48380)]

# ── Zonen ────────────────────────────────────────────────────────────────
WIJNHAVEN = [(51.91880, 4.48520), (51.91930, 4.48960), (51.91700, 4.49090),
             (51.91530, 4.48800), (51.91620, 4.48520)]
LIJNBAAN = [(51.92400, 4.47150), (51.92400, 4.47460), (51.92060, 4.47490),
            (51.92060, 4.47180)]

HOFPLEIN = (51.92530, 4.47400)


def beschriftung(lat, lon, text, klein=False, anker='middle', dx=0, dy=0, fuehr=None):
    x, y = xy(lat, lon)
    z = []
    if fuehr:
        fx, fy = xy(*fuehr)
        z.append('      <path class="ov-fuehr" d="M%.0f %.0f L%.0f %.0f"/>'
                 % (fx, fy, x + dx, y + dy))
    z.append('      <text class="ov-text%s" x="%.0f" y="%.0f" text-anchor="%s">%s</text>'
             % (' klein' if klein else '', x + dx, y + dy, anker, text))
    return z


def main():
    s = io.open(P, encoding='utf-8').read()

    g = ['<g id="ov-1946" hidden aria-hidden="true">',
         '      <defs>',
         '        <pattern id="ov-schraffur" patternUnits="userSpaceOnUse" width="14" height="14"',
         '                 patternTransform="rotate(45)">',
         '          <line x1="0" y1="0" x2="0" y2="14" stroke="#0A0A0A" stroke-width="1.4" stroke-opacity=".5"/>',
         '        </pattern>',
         '        <pattern id="ov-schraffur2" patternUnits="userSpaceOnUse" width="14" height="14"',
         '                 patternTransform="rotate(-45)">',
         '          <line x1="0" y1="0" x2="0" y2="14" stroke="#0A0A0A" stroke-width="1.4" stroke-opacity=".5"/>',
         '        </pattern>',
         '        <marker id="ov-pfeil" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5"',
         '                markerHeight="5" orient="auto-start-reverse">',
         '          <path d="M0 1 L9 5 L0 9 Z" fill="#0A0A0A"/>',
         '        </marker>',
         '      </defs>',
         '',
         '      <!-- Die Flaeche, die am 14. Mai 1940 ausbrannte. Sie ist der Grund fuer',
         '           alles Weitere: Der Basisplan baut genau dieses Gebiet wieder auf.',
         '           Verlauf schematisch, aus Koordinaten gesetzt. -->',
         '      <path class="ov-brand" d="%s"/>' % d(BRANDGRENS, zu=True),
         '',
         '      <!-- Die Achsen. Band = Breite, Strichpunktlinie = Fuehrung. Der',
         '           Coolsingel traegt seine belegten 80 m massstaeblich. -->']
    for name, pfad, breite in (('Coolsingel', COOLSINGEL, 61.3), ('Blaak', BLAAK, 34.5),
                               ('Boompjes', BOOMPJES, 30.7), ('Weena', WEENA, 38.3),
                               ('Goudsesingel', GOUDSESINGEL, 26.8)):
        g.append('      <path class="ov-band" style="stroke-width:%.1f" d="%s"/>' % (breite, d(pfad)))
    for pfad in (COOLSINGEL, BLAAK, BOOMPJES, WEENA, GOUDSESINGEL):
        g.append('      <path class="ov-achse" d="%s"/>' % d(pfad))

    g += ['',
          '      <!-- Zweckbestimmungen: das Wijnhavengebiet den Bueros der Schifffahrt,',
          '           die Lijnbaan dem Einkaufen. Schraffur statt Tonflaeche, damit der',
          '           Schwarzplan darunter lesbar bleibt. -->',
          '      <path class="ov-zone" d="%s"/>' % d(WIJNHAVEN, zu=True),
          '      <path class="ov-zone2" d="%s"/>' % d(LIJNBAAN, zu=True),
          '',
          '      <!-- Hofplein, Kreisel am Kopf des Coolsingel -->']
    hx, hy = xy(*HOFPLEIN)
    g.append('      <circle class="ov-ring" cx="%.0f" cy="%.0f" r="26"/>' % (hx, hy))
    g.append('      <circle class="ov-kern" cx="%.0f" cy="%.0f" r="9"/>' % (hx, hy))

    g += ['',
          '      <!-- Fenster zum Fluss am Leuvehaven: der Plan hielt hier die Sicht frei. -->']
    lx1, ly1 = xy(*LEUVEHAVEN[0]); lx2, ly2 = xy(*LEUVEHAVEN[1])
    g.append('      <path class="ov-korr" d="M%.0f %.0f L%.0f %.0f"/>' % (lx1 - 29, ly1, lx2 - 33, ly2))
    g.append('      <path class="ov-korr" d="M%.0f %.0f L%.0f %.0f"/>' % (lx1 + 29, ly1, lx2 + 33, ly2))
    g.append('      <path class="ov-korr" marker-end="url(#ov-pfeil)" style="stroke-dasharray:9 7"'
             ' d="M%.0f %.0f L%.0f %.0f"/>' % (lx1, ly1 + 35, lx2, ly2 - 25))

    g += ['', '      <!-- Beschriftung -->']
    g += beschriftung(51.92530, 4.47400, 'HOFPLEIN', anker='start', dx=100, dy=-26,
                      fuehr=(51.92530, 4.47400))
    g += beschriftung(51.92010, 4.47530, 'COOLSINGEL 80 M', anker='start', dx=76, dy=-16,
                      fuehr=(51.92010, 4.47530))
    g += beschriftung(51.92040, 4.49360, 'BLAAK', dx=0, dy=-30)
    g += beschriftung(51.91560, 4.49180, 'BOOMPJES', dx=96, dy=46)
    g += beschriftung(51.92460, 4.47900, 'WEENA', dx=0, dy=-28)
    g += beschriftung(51.92320, 4.48780, 'GOUDSESINGEL', dx=86, dy=-20, anker='start')
    g += beschriftung(51.91620, 4.48330, 'FENSTER ZUM FLUSS', klein=True, anker='end',
                      dx=-52, dy=4, fuehr=(51.91620, 4.48330))
    g += beschriftung(51.91700, 4.48760, 'WIJNHAVEN', klein=True, dx=0, dy=0)
    g += beschriftung(51.91700, 4.48760, 'B\u00dcROQUARTIER', klein=True, dx=0, dy=22)
    g += beschriftung(51.92230, 4.47320, 'LIJNBAAN', klein=True, dx=0, dy=0)
    g += beschriftung(51.92230, 4.47320, 'EINKAUFEN', klein=True, dx=0, dy=22)
    g += beschriftung(51.92490, 4.48100, 'BRANDGRENZE 14. MAI 1940', klein=True,
                      anker='start', dx=24, dy=-22)
    g.append('    </g>')

    m = re.search(r'<g id="ov-1946".*?</g>\n', s, re.S)
    if not m:
        sys.exit('FEHLER: Zeichnung nicht gefunden')
    s = s[:m.start()] + '\n'.join(g) + '\n' + s[m.end():]

    # ── CSS: Brandgrenze und zweite Schraffur ──
    alt = '.ov-zone   { fill:url(#ov-schraffur); stroke:var(--ink-1); stroke-width:2.2; }'
    neu = ('.ov-zone   { fill:url(#ov-schraffur); stroke:var(--ink-1); stroke-width:2.2; }\n'
           '.ov-zone2  { fill:url(#ov-schraffur2); stroke:var(--ink-1); stroke-width:2.2; }\n'
           '/* Die Brandgrenze von 1940: die eine Linie, die den ganzen Plan erklaert. */\n'
           '.ov-brand  { fill:none; stroke:var(--ink-1); stroke-width:4.5;\n'
           '             stroke-dasharray:26 12; stroke-linejoin:round; }')
    if s.count(alt) != 1:
        sys.exit('FEHLER: CSS der Zone nicht gefunden')
    s = s.replace(alt, neu)

    # ── Legende erweitern ──
    alt_l = '    <span class="lg-eintrag"><span class="lg-probe ring"></span>Hofplein</span>'
    neu_l = ('    <span class="lg-eintrag"><span class="lg-probe ring"></span>Hofplein</span>\n'
             '    <span class="lg-eintrag"><span class="lg-probe brand"></span>Brandgrenze 1940</span>')
    if s.count(alt_l) != 1:
        sys.exit('FEHLER: Legende nicht gefunden')
    s = s.replace(alt_l, neu_l)
    s = s.replace(".lg-probe.ring { border-radius:50%; width:12px; height:12px; background:var(--accent); }",
                  ".lg-probe.ring { border-radius:50%; width:12px; height:12px; background:var(--accent); }\n"
                  ".lg-probe.brand { border:none; height:0; border-top:3px dashed var(--ink-1); }")

    # ── Quellenzeile praeziser ──
    for sp, t in (
      ('de', 'Eigene Zeichnung, schematisch: die Brandgrenze vom 14. Mai 1940, die Achsen '
             'Coolsingel, Weena, Blaak, Goudsesingel und Boompjes, das Hofplein, das Fenster '
             'zum Fluss und die Zweckbestimmungen Wijnhaven und Lijnbaan. Verl\\u00e4ufe von Hand '
             'gesetzt, kein Abbild des Originalplans.'),
      ('nl', 'Eigen tekening, schematisch: de brandgrens van 14 mei 1940, de assen Coolsingel, '
             'Weena, Blaak, Goudsesingel en Boompjes, het Hofplein, het venster naar de rivier '
             'en de bestemmingen Wijnhaven en Lijnbaan. Trac\\u00e9s met de hand gezet, geen '
             'afbeelding van het originele plan.'),
      ('en', 'Own drawing, schematic: the fire boundary of 14 May 1940, the axes Coolsingel, '
             'Weena, Blaak, Goudsesingel and Boompjes, the Hofplein, the window to the river '
             'and the designations Wijnhaven and Lijnbaan. Alignments set by hand, not a '
             'reproduction of the original plan.')):
        muster = re.compile(r"(\n    %s: ')[^']*(',?\n)" % sp)
        teil = s[s.index("'ov-1946': {"):s.index("};", s.index("'ov-1946': {"))]
        neu_teil = muster.sub(lambda mm: mm.group(1) + t + mm.group(2), teil, count=1)
        s = s.replace(teil, neu_teil)

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('OK  Brandgrenze, Weena, Goudsesingel, Lijnbaan ergaenzt')
    print('OK  CSS: zweite Schraffur und Brandgrenze')
    print('OK  Legende um die Brandgrenze erweitert')
    print('OK  Quellenzeile nennt jetzt, was gezeigt wird')


if __name__ == '__main__':
    main()
