# -*- coding: utf-8 -*-
"""Aus dem gefuellten Blatt nur die Fuellungen herausloesen.

Die PDF-Seite enthaelt ein Bild von 3093 x 2235 Punkten. Das ist genau
der Rahmen der Website: bei der Einmessung im Oktober ergab sich fuer
die viewBox von 3010 x 2175 Einheiten ein Ausschnitt von 3092 x 2234
Blattpunkten. Die Zeichnung liegt also bereits richtig, und es ist
nichts mehr einzumessen.

Zu trennen sind drei Dinge: die orange Bebauung, das gruene Wasser und
das Papier mit dem Liniennetz. Nach Farbe geht das sauber, denn die
drei liegen im Farbraum weit auseinander:

  Bebauung  R > G > B, Abstand R minus B deutlich
  Wasser    G ueber R und ueber B
  Papier    warmes Grau, R > G > B, aber mit kleinem Abstand

Gefuellt wird flaechig und nicht mit der Textur des Blattes. Im
Palimpsest liegt die alte Stadt dadurch als Figur ueber dem heutigen
Plan, und nicht als zweites Blatt Papier darueber.
"""
import io
import os

import numpy as np
from PIL import Image, ImageFilter

QUELLE = r'C:\Temp\wij3d\dwg\fill_roh.png'
AUS = r'C:\Temp\wij3d\dwg'

# Die Farben der Ebene. Orange und Gruen stammen aus dem Blatt selbst,
# nur gesaettigter, damit sie bei 70 Prozent Deckung noch tragen.
BAU = (198, 112, 48)
WASSER = (120, 162, 158)


def masken(a):
    f = a.astype(float) / 255
    r, g, b = f[:, :, 0], f[:, :, 1], f[:, :, 2]
    bau = (r > g + 0.03) & (g > b + 0.02) & ((r - b) > 0.22)
    wasser = (g >= r - 0.005) & (g > b + 0.01)
    return bau, wasser


def saeubern(m, runden=1):
    """Einzelne Punkte und Loecher von der Rasterung des Drucks
    wegnehmen, ohne die Figuren zu verformen."""
    k = Image.fromarray((m * 255).astype('uint8'))
    for _ in range(runden):
        k = k.filter(ImageFilter.MedianFilter(3))
    return np.asarray(k) > 127


def main():
    im = Image.open(QUELLE).convert('RGB')
    a = np.asarray(im)
    print('Blatt: %d x %d' % im.size)

    bau, wasser = masken(a)
    print('roh:      Bebauung %.1f %%  Wasser %.1f %%'
          % (100 * bau.mean(), 100 * wasser.mean()))
    bau, wasser = saeubern(bau), saeubern(wasser)
    wasser &= ~bau
    print('gesaeubert: Bebauung %.1f %%  Wasser %.1f %%'
          % (100 * bau.mean(), 100 * wasser.mean()))

    h, w = bau.shape
    rgba = np.zeros((h, w, 4), dtype='uint8')
    for i, c in enumerate(WASSER):
        rgba[:, :, i] = np.where(wasser, c, 0)
    for i, c in enumerate(BAU):
        rgba[:, :, i] = np.where(bau, c, rgba[:, :, i])
    rgba[:, :, 3] = np.where(bau | wasser, 255, 0)

    voll = Image.fromarray(rgba)
    voll.save(os.path.join(AUS, 'palimpsest_voll.png'))

    # Fuer die Seite auf 3000 Punkte Breite, wie die bisherige Ebene.
    netz = voll.resize((3000, round(3000 * h / w)), Image.LANCZOS)
    for q in (72, 80, 88):
        b = io.BytesIO()
        netz.save(b, 'WEBP', quality=q, method=6)
        print('  q%-3d %6.0f KB' % (q, len(b.getvalue()) / 1024))
    ziel = os.path.join(AUS, 'palimpsest.webp')
    netz.save(ziel, 'WEBP', quality=80, method=6)
    print('palimpsest.webp: %d x %d, %.0f KB'
          % (netz.width, netz.height, os.path.getsize(ziel) / 1024))

    # Sichtprobe auf weissem Grund.
    probe = Image.new('RGB', netz.size, 'white')
    probe.paste(netz, (0, 0), netz)
    probe.resize((900, round(900 * netz.height / netz.width))).save(
        os.path.join(AUS, 'palimpsest_blick.png'))


if __name__ == '__main__':
    main()
