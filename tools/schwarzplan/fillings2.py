# -*- coding: utf-8 -*-
"""Die Fuellungen sauber und durchgehend, als Vektor.

Der erste Versuch hat die Flaechen punktweise nach Farbe aus dem
gescannten Blatt geholt. Das Ergebnis war fleckig: das Blatt ist
gedruckt, die Bauflaechen tragen eine Textur, und das Liniennetz
schneidet quer durch. Genau das hat der Auftraggeber gesehen.

Jetzt wird in drei Schritten gearbeitet:

  1. Maske nach Farbe wie bisher, denn die Trennung selbst stimmt.
  2. Morphologisch schliessen und oeffnen. Das Schliessen zieht die
     gedruckten Linien und die Hoefe zu, das Oeffnen wirft Sprenkel
     weg. Danach sind die Flaechen durchgehend.
  3. Umrisse nachziehen und als Polygone vereinfachen. Das Ergebnis
     ist eine SVG-Zeichnung: gestochen scharf auf jeder Zoomstufe,
     wie der Schwarzplan daneben, und ein Bruchteil der 1,3 MB.

Das Blatt liegt bereits im Rahmen der Seite: sein Bild misst
3093 x 2235 Punkte, und genau dieser Ausschnitt entspricht der viewBox
von 3010 x 2175 Einheiten. Es ist also nur umzurechnen, nicht
einzumessen.
"""
import io
import os

import cv2
import numpy as np
from PIL import Image

BLATT = r'C:\Temp\wij3d\dwg\fill_roh.png'
AUS = r'C:\Temp\wij3d\dwg'
VW, VH = 3010.0, 2175.0
BAU = '#C06A2E'        # Bebauung, aus dem Blatt genommen und gesaettigt
WASSER = '#78A29E'     # Wasser

# Die Zahlen sind an diesem Blatt gemessen, nicht geraten: bei 3093
# Punkten Breite ist eine gedruckte Strassenlinie 3 bis 5 Punkte breit,
# ein Hof 10 bis 25. Mit 13 Punkten zieht das Schliessen die Linien und
# die kleinen Hoefe zu, ohne benachbarte Bloecke zu verschmelzen.
SCHLIESSEN = 13
OEFFNEN = 7
KLEINST = 900          # Flaechen darunter sind Rauschen, in Punkten
GLAETTE = 1.6          # Douglas-Peucker, in Punkten


def masken():
    a = np.asarray(Image.open(BLATT).convert('RGB'), dtype=np.float32) / 255
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bau = (r > g + 0.03) & (g > b + 0.02) & ((r - b) > 0.22)
    wasser = (g >= r - 0.005) & (g > b + 0.01)
    return bau, wasser


def saeubern(m, schliessen, oeffnen, kleinst):
    u = (m * 255).astype(np.uint8)
    ks = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (schliessen, schliessen))
    ko = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (oeffnen, oeffnen))
    u = cv2.morphologyEx(u, cv2.MORPH_CLOSE, ks)
    u = cv2.morphologyEx(u, cv2.MORPH_OPEN, ko)
    # Splitter und Loecher unter der Mindestgroesse verschwinden lassen.
    for wert in (255, 0):
        n, lab, stats, _ = cv2.connectedComponentsWithStats(
            (u == wert).astype(np.uint8), 8)
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] < kleinst:
                u[lab == i] = 0 if wert == 255 else 255
    return u


def wege(u):
    """Umrisse mit Loechern, vereinfacht, in SVG-Pfade uebersetzt."""
    k = VW / u.shape[1]
    konturen, hier = cv2.findContours(u, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    pfade = []
    for c in konturen:
        if cv2.contourArea(c) < KLEINST:
            continue
        c = cv2.approxPolyDP(c, GLAETTE, True)
        if len(c) < 3:
            continue
        p = ['M%.1f %.1f' % (c[0][0][0] * k, c[0][0][1] * k)]
        p += ['L%.1f %.1f' % (q[0][0] * k, q[0][1] * k) for q in c[1:]]
        pfade.append(''.join(p) + 'Z')
    return pfade


def main():
    bau, wasser = masken()
    print('roh:        Bebauung %.1f %%  Wasser %.1f %%'
          % (100 * bau.mean(), 100 * wasser.mean()))

    ub = saeubern(bau, SCHLIESSEN, OEFFNEN, KLEINST)
    # Wasser ist grossflaechig und darf kraeftiger geschlossen werden.
    uw = saeubern(wasser, 21, 9, 4000)
    uw[ub > 0] = 0
    print('gesaeubert: Bebauung %.1f %%  Wasser %.1f %%'
          % (100 * (ub > 0).mean(), 100 * (uw > 0).mean()))

    pb, pw = wege(ub), wege(uw)
    print('Umrisse: %d Bebauung, %d Wasser' % (len(pb), len(pw)))

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
        'width="%g" height="%g" fill-rule="evenodd">' % (VW, VH, VW, VH),
        '<title>Palimpsest: die Stadt vor dem 14. Mai 1940</title>',
        '<desc>Bebaute und bewasserte Flaechen nach dem Blatt Gemeente Rotterdam '
        'en omgeving, 1:10.000, Stadsarchief Rotterdam, gemeinfrei. '
        'Im Koordinatenraum der Seite, 1 Einheit = 1,3048 m.</desc>',
        '<g fill="%s"><path d="%s"/></g>' % (WASSER, ' '.join(pw)),
        '<g fill="%s"><path d="%s"/></g>' % (BAU, ' '.join(pb)),
        '</svg>',
    ]
    ziel = os.path.join(AUS, 'palimpsest.svg')
    io.open(ziel, 'w', encoding='utf-8', newline='\n').write(''.join(svg))
    print('palimpsest.svg: %.0f KB' % (os.path.getsize(ziel) / 1024))

    # Sichtprobe aus den Masken, ohne Umweg ueber einen SVG-Renderer.
    h, w = ub.shape
    rgb = np.full((h, w, 3), 255, dtype=np.uint8)
    for i, c in enumerate((0x78, 0xA2, 0x9E)):
        rgb[:, :, i] = np.where(uw > 0, c, rgb[:, :, i])
    for i, c in enumerate((0xC0, 0x6A, 0x2E)):
        rgb[:, :, i] = np.where(ub > 0, c, rgb[:, :, i])
    Image.fromarray(rgb).resize((900, round(900 * h / w))).save(
        os.path.join(AUS, 'fuellung_sauber.png'))
    print('fuellung_sauber.png geschrieben')


if __name__ == '__main__':
    main()
