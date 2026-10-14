# -*- coding: utf-8 -*-
"""Gegenprobe: die neue Vektorkarte gegen den bisherigen Rasterplan.

Gerastert wird selbst, nicht im Browser. Verglichen werden zwei Dinge
getrennt, weil sie verschieden empfindlich sind: die Wasserflaeche, die
gross und eindeutig ist, und die Hauskoerper, bei denen schon ein
abweichender Datenstand einzelne Grundrisse verschiebt.

Zusaetzlich wird gemessen, was fuer die Seite zaehlt: Liegen die sieben
Stationen weiterhin auf einem Hauskoerper?
"""
import pickle

import numpy as np
from PIL import Image, ImageDraw

AKT = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
       r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
       r"\Rotterdam-Wijnhaven\img\schwarzplan.webp")
UNION = r"C:\Temp\wij3d\lp\union.pkl"
LAGEN = r"C:\Temp\wij3d\lp\lagen.pkl"

RAHMEN = (4375.84, 4524.04, 5456.87, 5304.74)
VW, VH = 3010.0, 2175.0
KX = VW / (RAHMEN[2] - RAHMEN[0])
KY = VH / (RAHMEN[3] - RAHMEN[1])

# Projektion der Seite
LON0, LAT0 = 4.460351, 51.931723
MLON, MLAT = 68671.61405376215, 110540.0
K = 0.7664240847195386
BAUTEN = {'Witte Huis': (51.91883, 4.49173), 'Kubuswoningen': (51.9199, 4.4902),
          'Markthal': (51.92011, 4.48687), 'CasaNova': (51.91796, 4.48736),
          'Red Apple': (51.9173, 4.48895), 'Wijnhaveneiland': (51.9166, 4.4876),
          'EY Netherlands': (51.91434, 4.48652)}


def malen(ringe, W, H, s, strich=0.0):
    bild = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(bild)
    for r in ringe:
        p = [(((x - RAHMEN[0]) * KX) * s, ((y - RAHMEN[1]) * KY) * s) for x, y in r]
        if len(p) >= 3:
            d.polygon(p, fill=255, outline=255,
                      width=max(1, int(round(strich * s)))) if strich else d.polygon(p, fill=255)
    return np.asarray(bild) > 127


def main():
    akt = Image.open(AKT).convert('RGB')
    W, H = akt.size
    a = np.asarray(akt).astype(np.int16)
    w_akt = np.abs(a - 199).max(2) < 14
    s_akt = a.max(2) < 60
    s = W / VW                      # Zeicheneinheiten -> Bildpunkte
    print('Raster %d x %d, %.4f Bildpunkte je Einheit' % (W, H, s))

    u = pickle.load(open(UNION, 'rb'))
    w_neu = malen(u[0], W, H, s)
    s_neu = malen(u[3], W, H, s) | malen(u[5], W, H, s)

    for name, x, y in (('Wasser', w_akt, w_neu), ('Hauskoerper', s_akt, s_neu)):
        j = (x & y).sum() / max((x | y).sum(), 1)
        print('%-12s alt %5.2f %%, neu %5.2f %%, Jaccard %.3f, nur alt %4.2f %%, nur neu %4.2f %%'
              % (name, 100 * x.mean(), 100 * y.mean(), j,
                 100 * (x & ~y).mean(), 100 * (y & ~x).mean()))

    # Liegen die sieben Bauten auf einem Koerper?
    ys, xs = np.nonzero(s_neu)
    pts = np.stack([xs, ys], 1)
    print('\nDie sieben Stationen im neuen Plan:')
    weit = 0
    for name, (la, lo) in BAUTEN.items():
        px = (lo - LON0) * MLON * K * s
        py = (LAT0 - la) * MLAT * K * s
        drin = (0 <= int(py) < H and 0 <= int(px) < W and s_neu[int(py), int(px)])
        d = np.hypot(pts[:, 0] - px, pts[:, 1] - py).min() * (VW / W / K)
        if d > 25:
            weit += 1
        print('  %-16s %s%.1f m' % (name, 'im Haus, ' if drin else '', d))
    print('%d Stationen weiter als 25 m entfernt' % weit)

    # Belegbild: alt grau, neue Hauskoerper rot
    p = np.asarray(akt.resize((W // 4, H // 4), Image.LANCZOS)).copy()
    mk = np.asarray(Image.fromarray((s_neu * 255).astype(np.uint8))
                    .resize((W // 4, H // 4), Image.BILINEAR)) > 110
    p[mk & ~np.asarray(Image.fromarray((s_akt * 255).astype(np.uint8))
                       .resize((W // 4, H // 4), Image.BILINEAR)) > 110] = (220, 30, 40)
    Image.fromarray(p).save(r'C:\Temp\wij3d\pres\L4_bauten.png')
    print('Belegbild: pres/L4_bauten.png')


if __name__ == '__main__':
    main()
