# -*- coding: utf-8 -*-
"""Ein Platzhalter fuer die Stadt vor 1940.

Ausdruecklich erfunden, nicht erhoben. Er soll eine Sache zeigen, und die
ist unstrittig: Die Innenstadt vor dem 14. Mai 1940 war **feinkoernig**.
Schmale Parzellen, geschlossene Blockraender, enge Strassen, Hoefe im
Inneren. Der Wiederaufbau hat daraus grobe, freistehende Koerper gemacht.
Dieser Unterschied im Korn ist der Punkt, und er traegt auch dann, wenn die
einzelnen Haeuser hier nicht die richtigen sind.

Gezeichnet wird in das Gebiet, das 1940 ausbrannte, abzueglich des heutigen
Wassers. Das Muster folgt zwei Richtungen: der Hafenkante im Sueden und dem
aelteren Raster im Norden. Blockgroesse rund 70 x 45 m, Strassen 13 m, Hof
innen. Das sind Groessenordnungen der europaeischen Vorkriegsstadt, keine
Messwerte.

Wird ersetzt, sobald die wirklichen Grundrisse vorliegen: Dieselbe Datei,
dieselbe Lage, nur ein anderes Bild.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
HEUTE = os.path.join(REPO, 'img', 'schwarzplan.webp')
ZIEL = os.path.join(REPO, 'img', 'vorkrieg.webp')

LON0, LAT0 = 4.460351, 51.931723
MLON, MLAT = 68671.61405376215, 110540.0
M_JE_PX = 0.8580                       # Meter je Bildpunkt des Schwarzplans

# Die 1940 ausgebrannte Flaeche, schematisch (wie in der Zeichnung zuvor)
BRANDGRENS = [
 (51.92490, 4.47400), (51.92470, 4.48100), (51.92320, 4.48780), (51.92120, 4.49420),
 (51.91780, 4.49580), (51.91500, 4.48900), (51.91350, 4.48400), (51.91390, 4.48200),
 (51.91680, 4.47800), (51.91780, 4.47450), (51.92050, 4.47120), (51.92320, 4.47000),
]

BLOCK_L, BLOCK_B = 70.0, 45.0          # Meter
STRASSE = 13.0                         # Meter
TIEFE = 12.0                           # Bautiefe am Blockrand, Meter
GRENZE_LAT = 51.9205                   # darunter die Hafenrichtung, darueber das Raster
WINKEL_SUED, WINKEL_NORD = 24.0, -6.0  # Grad


def px(lat, lon):
    return ((lon - LON0) * MLON / M_JE_PX, (LAT0 - lat) * MLAT / M_JE_PX)


def main():
    heute = Image.open(HEUTE).convert('L')
    W, H = heute.size
    a = np.asarray(heute)
    wasser = (a > 185) & (a < 215)

    # Maske des Brandgebiets
    maske = Image.new('L', (W, H), 0)
    ImageDraw.Draw(maske).polygon([px(*p) for p in BRANDGRENS], fill=255)
    innen = np.asarray(maske) > 127
    innen &= ~wasser
    print('Brandgebiet ohne Wasser: %.0f ha' % (innen.sum() * M_JE_PX ** 2 / 10000))

    # Zwei Richtungen, getrennt an einer Breite
    grenze_y = px(GRENZE_LAT, LON0)[1]
    bild = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(bild)
    schritt_l = (BLOCK_L + STRASSE) / M_JE_PX
    schritt_b = (BLOCK_B + STRASSE) / M_JE_PX
    bl, bb = BLOCK_L / M_JE_PX, BLOCK_B / M_JE_PX
    tiefe = TIEFE / M_JE_PX

    rng = np.random.default_rng(1946)
    for winkel, (y_von, y_bis) in ((WINKEL_NORD, (-H, grenze_y)),
                                   (WINKEL_SUED, (grenze_y, 2 * H))):
        r = math.radians(winkel)
        c, s = math.cos(r), math.sin(r)
        # Gitter im gedrehten System, weit genug ueber das Bild hinaus
        reich = int(math.hypot(W, H) / min(schritt_l, schritt_b)) + 4
        for i in range(-reich, reich):
            for j in range(-reich, reich):
                u, v = i * schritt_l, j * schritt_b
                # leichte Unregelmaessigkeit, sonst sieht es nach Tapete aus
                du = float(rng.normal(0, 3.0 / M_JE_PX))
                dv = float(rng.normal(0, 2.0 / M_JE_PX))
                ecken_uv = [(u + du, v + dv), (u + du + bl, v + dv),
                            (u + du + bl, v + dv + bb), (u + du, v + dv + bb)]
                aussen = [(W / 2 + e[0] * c - e[1] * s, H / 2 + e[0] * s + e[1] * c)
                          for e in ecken_uv]
                ys = [p[1] for p in aussen]
                if max(ys) < y_von or min(ys) > y_bis:
                    continue
                if max(p[0] for p in aussen) < 0 or min(p[0] for p in aussen) > W:
                    continue
                innen_uv = [(ecken_uv[0][0] + tiefe, ecken_uv[0][1] + tiefe),
                            (ecken_uv[1][0] - tiefe, ecken_uv[1][1] + tiefe),
                            (ecken_uv[2][0] - tiefe, ecken_uv[2][1] - tiefe),
                            (ecken_uv[3][0] + tiefe, ecken_uv[3][1] - tiefe)]
                hof = [(W / 2 + e[0] * c - e[1] * s, H / 2 + e[0] * s + e[1] * c)
                       for e in innen_uv]
                d.polygon(aussen, fill=255)
                if bl > 2 * tiefe + 4 and bb > 2 * tiefe + 4:
                    d.polygon(hof, fill=0)

    gebaut = (np.asarray(bild) > 127) & innen
    print('bebaut: %.1f %% des Brandgebiets' % (100 * gebaut.sum() / max(innen.sum(), 1)))

    aus = np.zeros((H, W, 4), dtype=np.uint8)
    aus[gebaut] = (26, 26, 26, 255)
    Image.fromarray(aus).save(ZIEL, 'WEBP', lossless=True, quality=100, method=6)
    print('img/vorkrieg.webp: %d x %d px, %.0f KB' % (W, H, os.path.getsize(ZIEL) / 1024))

    v = Image.fromarray(aus)
    weiss = Image.new('RGB', v.size, (255, 255, 255))
    weiss.paste(v, (0, 0), v)
    weiss.resize((W // 4, H // 4), Image.LANCZOS).save(r'C:\Temp\wij3d\pres\X1_vorkrieg.png')


if __name__ == '__main__':
    main()
