# -*- coding: utf-8 -*-
"""Den Lageplan einmessen, ohne ihn zu rendern.

Gerastert wird nur die Wasserlage, und zwar selbst: 6.098 Dreiecke in
eine Maske zeichnen geht in Sekunden, wo Chrome an der ganzen Datei
eine Viertelstunde scheitert.

Die Annahme, die geprueft wird: Der Rahmen der Zeichnung
(x 4375.84..5456.87, y 4524.04..5304.74) ist derselbe Ausschnitt wie
der bisherige Rasterplan, deckt also 0..3010 / 0..2175 im Koordinaten-
raum der Seite ab. Gemessen werden Massstab und Versatz dagegen.
"""
import pickle

import numpy as np
from PIL import Image, ImageDraw

AKT = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
       r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
       r"\Rotterdam-Wijnhaven\img\schwarzplan.webp")
LAGEN = r"C:\Temp\wij3d\lp\lagen.pkl"

RAHMEN = (4375.84, 4524.04, 5456.87, 5304.74)   # x0, y0, x1, y1 der Zeichnung
M_AKT = 0.858                                   # Meter je Bildpunkt heute


def maske(formen, W, H, k, tx, ty):
    """Die Wasserlage in eine Maske zeichnen."""
    bild = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(bild)
    for art, f in formen:
        if art == 'kreis' or len(f) < 3:
            continue
        d.polygon([(x * k + tx, y * k + ty) for x, y in f], fill=255)
    return np.asarray(bild) > 127


def gipfel(a, b):
    H = max(a.shape[0], b.shape[0]) * 2
    W = max(a.shape[1], b.shape[1]) * 2
    A = np.zeros((H, W)); B = np.zeros((H, W))
    A[:a.shape[0], :a.shape[1]] = a - a.mean()
    B[:b.shape[0], :b.shape[1]] = b - b.mean()
    c = np.fft.irfft2(np.fft.rfft2(A) * np.conj(np.fft.rfft2(B)), s=(H, W))
    i = int(np.argmax(c))
    dy, dx = divmod(i, W)
    if dy > H // 2: dy -= H
    if dx > W // 2: dx -= W
    return dx, dy


def main():
    akt = Image.open(AKT).convert('RGB')
    AW, AH = akt.size
    a = np.asarray(akt).astype(np.int16)
    w_akt = np.abs(a - 199).max(2) < 14
    print('heute %d x %d, Wasser %.1f %%' % (AW, AH, 100 * w_akt.mean()))

    lagen = pickle.load(open(LAGEN, 'rb'))
    wasser = lagen[0]['formen']

    # Annahme: Rahmen der Zeichnung = Rahmen des Rasterplans
    x0, y0, x1, y1 = RAHMEN
    k0 = AW / (x1 - x0)
    print('Annahme: %.5f Bildpunkte je Zeicheneinheit, Rahmen %.1f x %.1f'
          % (k0, (x1 - x0) * k0, (y1 - y0) * k0))

    bestes = None
    for rel in np.arange(0.97, 1.0305, 0.005):
        k = k0 * rel
        m = maske(wasser, AW, AH, k, -x0 * k, -y0 * k)
        dx, dy = gipfel(w_akt.astype(float), m.astype(float))
        mm = np.roll(np.roll(m, dy, 0), dx, 1)
        j = (mm & w_akt).sum() / max((mm | w_akt).sum(), 1)
        print('  Massstab x%.4f -> Versatz %+4d %+4d, Jaccard %.3f' % (rel, dx, dy, j))
        if bestes is None or j > bestes[0]:
            bestes = (j, rel, dx, dy)

    j, rel, dx, dy = bestes
    for rel2 in np.arange(rel - 0.005, rel + 0.0051, 0.001):
        k = k0 * rel2
        m = maske(wasser, AW, AH, k, -x0 * k, -y0 * k)
        d2x, d2y = gipfel(w_akt.astype(float), m.astype(float))
        mm = np.roll(np.roll(m, d2y, 0), d2x, 1)
        j2 = (mm & w_akt).sum() / max((mm | w_akt).sum(), 1)
        print('  fein x%.4f -> Versatz %+4d %+4d, Jaccard %.3f' % (rel2, d2x, d2y, j2))
        if j2 > j:
            j, rel, dx, dy = j2, rel2, d2x, d2y

    k = k0 * rel
    print('\nBestes: Massstab %.5f Bildpunkte je Einheit (x%.4f), Versatz %+d %+d px'
          % (k, rel, dx, dy))
    print('        das sind %+.1f / %+.1f m' % (dx * M_AKT, dy * M_AKT))
    print('        Jaccard der Wasserflaechen %.3f' % j)

    pickle.dump({'k': k, 'dx': dx, 'dy': dy, 'x0': x0, 'y0': y0,
                 'rahmen': RAHMEN, 'jaccard': j},
                open(r'C:\Temp\wij3d\lp\passung.pkl', 'wb'))

    # Belegbild
    m = maske(wasser, AW, AH, k, -x0 * k + dx, -y0 * k + dy)
    p = np.asarray(akt.resize((AW // 4, AH // 4), Image.LANCZOS)).copy()
    mk = np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                    .resize((AW // 4, AH // 4), Image.BILINEAR)) > 110
    p[mk] = (220, 30, 40)
    Image.fromarray(p).save(r'C:\Temp\wij3d\pres\L3_passung.png')
    print('Belegbild: pres/L3_passung.png')


if __name__ == '__main__':
    main()
