# -*- coding: utf-8 -*-
"""Den Versatz direkt messen, statt ihn aus einem Korrelationsgipfel zu raten.

Die Korrelation sagt nur, wo ihr Gipfel liegt, nicht wie weit daneben sie
liegt. Hier wird stattdessen gemessen, wie weit die Wasserkante der
Revisiekarte von der Wasserkante des Schwarzplans entfernt ist, Punkt fuer
Punkt, und daraus der mittlere Verschiebungsvektor gebildet.

Der Median ist dabei das Werkzeug: Wo die beiden Karten wirklich
verschiedene Dinge zeigen, etwa an zugeschuetteten Becken, laufen die
Abstaende auseinander; der Median ignoriert das und folgt der Mehrheit der
Kante, die in beiden Karten dieselbe ist.

Das Ergebnis ist eine Korrektur in Metern, kein neuer Gipfel.
"""
import os
import pickle

import numpy as np
from PIL import Image
from scipy import ndimage

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
HEUTE = os.path.join(REPO, 'img', 'schwarzplan.webp')
REVISIE = r"C:\Temp\wij3d\revisie.jpg"

MAP_VW, M_HEUTE = 3010.0, 0.8580
# aktuelle Lage in der Seite (Bild 3200 x 2496)
TX, TY, S = 442.3, -93.8, 0.86976


def main():
    h = Image.open(HEUTE).convert('L')
    W, H = h.size
    a = np.asarray(h)
    wh = (a > 185) & (a < 215)
    svg_je_px = MAP_VW / W

    r = Image.open(REVISIE).convert('RGB')
    b = np.asarray(r).astype(np.int16)
    wr = (b[:, :, 2] > 140) & (b[:, :, 2] - b[:, :, 0] > 50) & (b[:, :, 2] - b[:, :, 1] > 25)

    # Die Revisiemaske so legen, wie sie in der Seite liegt.
    f = (S / svg_je_px) * 2.0          # das Bild in der Seite ist doppelt so gross
    nw, nh = int(round(r.width * f)), int(round(r.height * f))
    m = np.asarray(Image.fromarray((wr * 255).astype(np.uint8)).resize((nw, nh), Image.BILINEAR)) > 127
    ox, oy = int(round(TX / svg_je_px)), int(round(TY / svg_je_px))
    gelegt = np.zeros_like(wh)
    y0, x0 = max(0, oy), max(0, ox)
    y1, x1 = min(H, oy + nh), min(W, ox + nw)
    gelegt[y0:y1, x0:x1] = m[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    print('Revisie-Wasser gelegt: %.1f %% der Flaeche' % (100 * gelegt.mean()))
    print('Schwarzplan-Wasser:    %.1f %%' % (100 * wh.mean()))

    # Kanten
    kante_r = gelegt ^ ndimage.binary_erosion(gelegt, iterations=1)
    # Abstandsbild und Richtung zur naechsten Schwarzplan-Wasserkante
    kante_h = wh ^ ndimage.binary_erosion(wh, iterations=1)
    dist, idx = ndimage.distance_transform_edt(~kante_h, return_indices=True)

    ys, xs = np.nonzero(kante_r)
    if len(xs) < 500:
        raise SystemExit('zu wenig Kantenpunkte')
    # auf eine handliche Menge ausduennen
    schritt = max(1, len(xs) // 40000)
    ys, xs = ys[::schritt], xs[::schritt]
    zy, zx = idx[0][ys, xs], idx[1][ys, xs]
    dy, dx = zy - ys, zx - xs
    d = np.hypot(dx, dy) * M_HEUTE
    print('\n%d Kantenpunkte verglichen' % len(xs))
    print('Abstand zur naechsten Wasserkante:')
    for p in (10, 25, 50, 75, 90):
        print('   %2d %% liegen unter %6.1f m' % (p, np.percentile(d, p)))

    nah = d < 60                     # nur die Kante, die wirklich dieselbe ist
    print('\n%d Punkte naeher als 60 m, daraus der Versatz:' % nah.sum())
    mx, my = float(np.median(dx[nah])), float(np.median(dy[nah]))
    print('   Median  %+.1f / %+.1f Bildpunkte  =  %+.1f / %+.1f m'
          % (mx, my, mx * M_HEUTE, my * M_HEUTE))
    print('   Streuung (MAD) %.1f / %.1f m'
          % (np.median(np.abs(dx[nah] - mx)) * M_HEUTE,
             np.median(np.abs(dy[nah] - my)) * M_HEUTE))

    neu_tx = TX + mx * svg_je_px
    neu_ty = TY + my * svg_je_px
    print('\nKorrigierte Lage:  translate(%.1f %.1f) scale(%.5f)' % (neu_tx, neu_ty, S))
    pickle.dump({'tx': neu_tx, 'ty': neu_ty, 's': S,
                 'dx_m': mx * M_HEUTE, 'dy_m': my * M_HEUTE},
                open(r'C:\Temp\wij3d\passung.pkl', 'wb'))


if __name__ == '__main__':
    main()
