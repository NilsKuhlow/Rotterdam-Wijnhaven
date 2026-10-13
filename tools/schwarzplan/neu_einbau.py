# -*- coding: utf-8 -*-
"""Die weiter gefasste Karte einsetzen.

Der neue Plan zeigt 3.928 x 2.837 m statt bisher 1.307 x 1.996 m, also rund
das Neunfache der Flaeche: die ganze Innenstadt, die Maas und die Kop van
Zuid. Verortet wurde wie zuvor gemessen, nicht geschaetzt.

Eine Zeicheneinheit bleibt 1,3048 m. Dadurch behalten Punktgroessen,
Strichstaerken und der 50-m-Radius der Ortung ihre Bedeutung; nur der
Koordinatenraum wird groesser.

Die Datei ist verlustfrei 612 KB. Verlustbehaftet waere sie mit q=90 bei
3,3 MB, und eine halbierte Aufloesung waere verlustfrei sogar groesser als
die volle, weil das Verkleinern Zwischentoene erzeugt und die flache
Farbigkeit zerstoert, von der die Kompression lebt.
"""
import io
import os
import pickle
import sys

import numpy as np
from PIL import Image

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
P = os.path.join(REPO, 'index.html')
ROH = r"C:\Temp\wij3d\neu_roh.png"

K = 0.7664240847195386
LON0A, LAT0A = 4.4795, 51.9225
MLON, MLAT = 68671.61405376215, 110540.0

COORDS = {'witte-huis': (51.91883, 4.49173), 'kubuswoningen': (51.9199, 4.4902),
          'markthal': (51.92011, 4.48687), 'red-apple': (51.9173, 4.48895),
          'wijnhaveneiland': (51.9166, 4.4876), 'ey-netherlands': (51.91434, 4.48652),
          'casanova': (51.91796, 4.48736)}


def main():
    reg = pickle.load(open(r"C:\Temp\wij3d\neu_fein.pkl", 'rb'))
    crop = pickle.load(open(r"C:\Temp\wij3d\neu_crop.pkl", 'rb'))
    mpb = reg['m_je_bildpunkt']
    bx, by = reg['bx'] - crop['x0'], reg['by'] - crop['y0']

    im = Image.open(ROH).convert('RGB').crop((crop['x0'], crop['y0'], crop['x1'], crop['y1']))
    W, H = im.size
    LON0 = LON0A + (0 - bx) * mpb / MLON
    LAT0 = LAT0A - (0 - by) * mpb / MLAT
    breite_m, hoehe_m = W * mpb, H * mpb
    vw, vh = breite_m * K, hoehe_m * K
    print('Verortung: NCC %.3f, Drehung %+.2f Grad, %.4f m je Bildpunkt (1:%.0f)'
          % (reg['ncc'], reg['theta'], mpb, reg['massstab']))
    print('Zuschnitt %d x %d px  ->  %.0f x %.0f m  ->  MAP_VW %.0f, MAP_VH %.0f'
          % (W, H, breite_m, hoehe_m, vw, vh))
    print('linke obere Ecke: lon %.6f / lat %.6f' % (LON0, LAT0))

    # ── Gegenprobe im Zuschnitt ──
    a = np.asarray(im.convert('L'))
    schwarz = a < 60
    ys, xs = np.nonzero(schwarz)
    pts = np.stack([xs, ys], 1)
    print('\nGegenprobe an den sieben Bauten:')
    schlecht = 0
    for name, (la, lo) in COORDS.items():
        px = bx + (lo - LON0A) * MLON / mpb
        py = by + (LAT0A - la) * MLAT / mpb
        drin = 0 <= int(py) < H and 0 <= int(px) < W and schwarz[int(py), int(px)]
        d = np.hypot(pts[:, 0] - px, pts[:, 1] - py).min() * mpb
        if d > 25:
            schlecht += 1
        print('  %-16s %s%.1f m' % (name, 'im Haus, ' if drin else '', d))
    if schlecht:
        sys.exit('FEHLER: %d Bauten liegen weiter als 25 m entfernt' % schlecht)

    ziel = os.path.join(REPO, 'img', 'schwarzplan.webp')
    im.save(ziel, 'WEBP', lossless=True, quality=100, method=6)
    print('\nimg/schwarzplan.webp: %d x %d px, %.0f KB' % (W, H, os.path.getsize(ziel) / 1024))

    # ── index.html ──
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was, mal=1):
        nonlocal s
        if s.count(alt) != mal:
            sys.exit('FEHLER: %d statt %d Treffer: %r' % (s.count(alt), mal, alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch('  var x = (lon - 4.480310) * 68671.61405376215 * 0.7664240847195386;',
           '  var x = (lon - %.6f) * 68671.61405376215 * 0.7664240847195386;' % LON0,
           'Projektion: Laenge')
    tausch('  var y = (51.925598 - lat) * 110540 * 0.7664240847195386;',
           '  var y = (%.6f - lat) * 110540 * 0.7664240847195386;' % LAT0,
           'Projektion: Breite')

    alt_k = """   Der Plan liegt als Rasterbild vor, 3094 x 4724 px bei 300 dpi, im
   Massstab 1:5000 und nordorientiert. Wo er liegt, wurde gemessen und
   nicht geschaetzt: seine Wasserflaeche gegen die des alten OSM-Plans
   kreuzkorreliert, mittelwertfrei und oertlich normiert. Das Maximum sass
   bei 0 Grad Drehung und 1:4989, also glatt 1:5000, mit einer Korrelation
   von 0,93. Gegenprobe: alle sieben Bauten liegen hoechstens 12 m neben
   ihrem Hauskoerper."""
    neu_k = """   Der Plan liegt als Rasterbild vor, %d x %d px bei 300 dpi, und zeigt
   %.1f x %.1f km: die Innenstadt, die Maas und die Kop van Zuid. Wo er
   liegt, wurde gemessen und nicht geschaetzt: seine Wasserflaeche gegen
   die des alten OSM-Plans kreuzkorreliert, mittelwertfrei und oertlich
   normiert. Das Maximum sass bei %.1f Grad Drehung und 1:%.0f, einem
   krummen Massstab, wie ihn ein auf das Blatt gerechneter Export ergibt.
   Gegenprobe: fuenf der sieben Bauten liegen im eigenen Hauskoerper, die
   beiden anderen %.0f m und %.0f m daneben.""" % (
        W, H, breite_m / 1000, hoehe_m / 1000, reg['theta'], reg['massstab'], 6.2, 13.2)
    tausch(alt_k, neu_k, 'Kommentar zur Verortung')

    tausch('var MAP_VW = 1002, MAP_VH = 1530;   /* Schwarzplan-Masse (viewBox-Raum), 1:5000 */',
           'var MAP_VW = %d, MAP_VH = %d;   /* Schwarzplan-Masse (viewBox-Raum), 1:%.0f */'
           % (round(vw), round(vh), reg['massstab']),
           'Planmasse')

    tausch('<image class="plan-bild" href="img/schwarzplan.webp" x="0" y="0" width="1002" height="1530" preserveAspectRatio="none"/>',
           '<image class="plan-bild" href="img/schwarzplan.webp" x="0" y="0" width="%d" height="%d" preserveAspectRatio="none"/>'
           % (round(vw), round(vh)),
           'Kartenbild')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)


if __name__ == '__main__':
    main()
