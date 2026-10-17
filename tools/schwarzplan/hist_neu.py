# -*- coding: utf-8 -*-
"""Den Plan von 1940 einmessen, nachdem der Fehler gefunden ist.

Sechs Anlaeufe sind gescheitert, und der Grund lag nicht in der Suche,
sondern in der Maske. Ich hatte das Blatt erst verkleinert und dann die
Wasserfarbe geschwellt. Die Becken der Innenstadt sind aber nur 40 bis
80 m breit, also 50 bis 95 Bildpunkte im Blatt und nach dem Verkleinern
ein Dutzend; im Papierton des Rasterdrucks verschwinden sie dabei. An
der Wijnhaven fand die Maske null Wasser. Uebrig blieb die Maas, und an
einem Fluss allein rutscht jede Korrelation entlang, genau wie gesehen.

Richtig herum: erst in voller Aufloesung schwellen, dann die fertige
Maske zusammenfassen. Die Mittelung ueber 4x4 Punkte glaettet den
Druckraster und haelt die schmalen Becken, weil sie im Block die
Mehrheit stellen.

Gesucht wird um die Nominallage: 1:10.000 bei 300 dpi, Festpunkt die
beschriftete Wijnhaven. Gewertet wird Jaccard der Wasserflaechen, beide
auf den Kartenrahmen beschnitten.
"""
import itertools
import pickle

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None

QUELLE = r'C:\Temp\wij3d\karten\plan1940.jpg'
UNION = r'C:\Temp\wij3d\lp\union.pkl'
RAHMEN = (4375.84, 4524.04, 5456.87, 5304.74)
VW, VH = 3010.0, 2175.0
K = 0.7664240847195386
M_JE_PX = 10000 * 0.0254 / 300
PX_JE_EINHEIT = (1 / K) / M_JE_PX
FESTPUNKT_BLATT = (4898.0, 2919.0)
FESTPUNKT_SEITE = (1434.0, 1281.0)

VIERTEL = 4          # Zusammenfassung NACH dem Schwellen
AUFL = 0.5           # Bildpunkte je Zeicheneinheit beim Messen
RAND = 600           # Zugabe am Blattrand, in Punkten der zusammengefassten Maske


def seite_maske(px_je_einheit):
    W = int(round(VW * px_je_einheit)); H = int(round(VH * px_je_einheit))
    kx = VW / (RAHMEN[2] - RAHMEN[0]) * px_je_einheit
    ky = VH / (RAHMEN[3] - RAHMEN[1]) * px_je_einheit
    bild = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(bild)
    for ring in pickle.load(open(UNION, 'rb'))[0]:
        if len(ring) >= 3:
            d.polygon([((x - RAHMEN[0]) * kx, (y - RAHMEN[1]) * ky)
                       for x, y in ring], fill=255)
    return np.asarray(bild) > 127


def blatt_maske():
    """Wassermaske des Blattes: schwellen, dann zusammenfassen."""
    a = np.asarray(Image.open(QUELLE).convert('RGB')).astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    m = (B - R > -16) & (G - R > -8)
    del a, R, G, B
    # Mittelung ueber 4x4: glaettet den Druckraster, haelt die Becken.
    h = (m.shape[0] // VIERTEL) * VIERTEL
    w = (m.shape[1] // VIERTEL) * VIERTEL
    mm = m[:h, :w].reshape(h // VIERTEL, VIERTEL, w // VIERTEL, VIERTEL)
    anteil = mm.mean(axis=(1, 3))
    k = anteil > 0.35
    k = ndimage.binary_closing(k, np.ones((3, 3)), iterations=1)
    k = ndimage.binary_opening(k, np.ones((2, 2)), iterations=1)
    return k


def main():
    heute = seite_maske(AUFL)
    H, W = heute.shape
    roh = blatt_maske()
    print('Blattmaske %s, Wasser %.2f %%' % (roh.shape, 100 * roh.mean()))
    print('Rahmen %d x %d, Wasser heute %.2f %%' % (W, H, 100 * heute.mean()))

    pad = Image.new('L', (roh.shape[1] + 2 * RAND, roh.shape[0] + 2 * RAND), 0)
    pad.paste(Image.fromarray((roh * 255).astype(np.uint8)), (RAND, RAND))
    FP = (FESTPUNKT_BLATT[0] / VIERTEL + RAND, FESTPUNKT_BLATT[1] / VIERTEL + RAND)

    def legen(dx, dy, s, grad):
        px = PX_JE_EINHEIT / s / VIERTEL
        ux = FP[0] - (FESTPUNKT_SEITE[0] + dx) * px
        uy = FP[1] - (FESTPUNKT_SEITE[1] + dy) * px
        if ux < 0 or uy < 0:
            return None
        c = pad.rotate(grad, Image.BILINEAR, center=FP) if grad else pad
        return np.asarray(c.resize((W, H), Image.BILINEAR,
                                   box=(ux, uy, ux + VW * px, uy + VH * px))) > 110

    def jac(p):
        m = legen(*p)
        if m is None:
            return 0.0
        return (m & heute).sum() / max((m | heute).sum(), 1)

    print('Nominallage: Jaccard %.3f' % jac((0, 0, 1.0, 0.0)))

    netz = list(itertools.product(range(-200, 201, 20), range(-200, 201, 20),
                                  (0.99, 1.0, 1.01), (0.0,)))
    bestes = max(netz, key=jac); j = jac(bestes)
    print('grob (%d Lagen): %+d %+d, x%.2f, Jaccard %.3f' % (len(netz), *bestes[:3], j))

    for weite, schritt, ss, gg in ((20, 5, (0.99, 0.995, 1.0, 1.005, 1.01),
                                    (-0.5, -0.25, 0.0, 0.25, 0.5)),
                                   (6, 2, None, None)):
        dx0, dy0, s0, g0 = bestes
        sl = ss if ss else np.round(np.arange(s0 - 0.004, s0 + 0.0041, 0.002), 4)
        gl = gg if gg else np.round(np.arange(g0 - 0.2, g0 + 0.21, 0.1), 2)
        netz = list(itertools.product(
            range(dx0 - weite, dx0 + weite + 1, schritt),
            range(dy0 - weite, dy0 + weite + 1, schritt), sl, gl))
        k = max(netz, key=jac)
        if jac(k) > j:
            bestes, j = k, jac(k)
        print('fein (Schritt %d): %+d %+d, x%.4f, %+.2f Grad, Jaccard %.3f'
              % (schritt, *bestes, j))

    dx, dy, s, grad = bestes
    rand = abs(dx) >= 200 or abs(dy) >= 200
    print('\nOptimum %s' % ('AM RAND' if rand else 'im Inneren'))
    print('Verschiebung %+.0f / %+.0f m gegenueber der Nominallage' % (dx / K, dy / K))
    print('Massstab %.4f m je Bildpunkt, Drehung %+.2f Grad' % (M_JE_PX * s, grad))

    pickle.dump({'dx': dx, 'dy': dy, 's': s, 'grad': grad, 'jaccard': j,
                 'px_je_einheit': PX_JE_EINHEIT, 'viertel': VIERTEL,
                 'festpunkt_blatt': FESTPUNKT_BLATT,
                 'festpunkt_seite': FESTPUNKT_SEITE},
                open(r'C:\Temp\wij3d\karten\neu1940.pkl', 'wb'))

    m = legen(*bestes)
    p = np.full((H, W, 3), 255, np.uint8)
    p[heute] = (205, 205, 205)
    p[m & ~heute] = (220, 30, 40)
    p[m & heute] = (110, 110, 170)
    Image.fromarray(p).save(r'C:\Temp\wij3d\pres\N0_passung.png')
    print('Belegbild: pres/N0_passung.png')


if __name__ == '__main__':
    main()
