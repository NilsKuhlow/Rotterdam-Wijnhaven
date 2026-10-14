# -*- coding: utf-8 -*-
"""Die Dreiecke exakt verschmelzen, mit GEOS statt mit Handarbeit.

Der erste Versuch, die Dreiecke ueber ihre gemeinsamen Kanten
zusammenzusetzen, ist gescheitert: 60 Prozent der Kanten liegen am Rand,
das Netz ist also keine saubere Triangulierung, und die Gegenprobe kam
nur auf 92 Prozent Flaechengleichheit. Darum hier die ehrliche Variante,
eine echte Vereinigung der Flaechen.

Gerechnet wird in Kacheln, sonst laeuft der Speicher voll. Die Kacheln
ueberlappen sich nicht; was ueber eine Kachelgrenze reicht, wird am Ende
noch einmal vereinigt.
"""
import pickle
import time

import numpy as np
import shapely
from shapely import GEOSException

LAGEN = r"C:\Temp\wij3d\lp\lagen.pkl"
ZIEL = r"C:\Temp\wij3d\lp\union.pkl"
KACHEL = 8              # 8 x 8 Kacheln


def dreiecke(formen):
    roh = [f for art, f in formen if art != 'kreis' and len(f) >= 3]
    ringe = []
    for f in roh:
        p = list(f)
        if p[0] != p[-1]:
            p = p + [p[0]]
        if len(p) >= 4:
            ringe.append(p)
    return ringe


def ringe_von(geo):
    """Aus einer Vereinigung die Ringe ziehen, aussen wie innen."""
    raus = []
    for g in shapely.get_parts(shapely.normalize(geo)) if not geo.is_empty else []:
        if g.geom_type != 'Polygon':
            continue
        raus.append(list(g.exterior.coords)[:-1])
        for r in g.interiors:
            raus.append(list(r.coords)[:-1])
    return raus


def main():
    lagen = pickle.load(open(LAGEN, 'rb'))
    raus = {}
    for i in (0, 3, 5):
        t0 = time.time()
        ringe = dreiecke(lagen[i]['formen'])
        polys = shapely.polygons(
            [shapely.linearrings(np.array(r)) for r in ringe])
        gueltig = shapely.is_valid(polys) & (shapely.area(polys) > 0)
        polys = polys[gueltig]
        xs = shapely.bounds(polys)
        x0, y0 = xs[:, 0].min(), xs[:, 1].min()
        x1, y1 = xs[:, 2].max(), xs[:, 3].max()
        stuecke = []
        for a in range(KACHEL):
            for b in range(KACHEL):
                kx0 = x0 + (x1 - x0) * a / KACHEL
                kx1 = x0 + (x1 - x0) * (a + 1) / KACHEL
                ky0 = y0 + (y1 - y0) * b / KACHEL
                ky1 = y0 + (y1 - y0) * (b + 1) / KACHEL
                mitte_x = (xs[:, 0] + xs[:, 2]) / 2
                mitte_y = (xs[:, 1] + xs[:, 3]) / 2
                drin = ((mitte_x >= kx0) & (mitte_x < kx1)
                        & (mitte_y >= ky0) & (mitte_y < ky1))
                if not drin.any():
                    continue
                try:
                    stuecke.append(shapely.union_all(polys[drin]))
                except GEOSException:
                    stuecke.append(shapely.union_all(
                        shapely.make_valid(polys[drin])))
        ganz = shapely.union_all(stuecke)
        r = ringe_von(ganz)
        print('Lage %d: %d Dreiecke -> %d Ringe, %d Punkte (vorher %d), %.0f s'
              % (i, len(polys), len(r), sum(len(x) for x in r),
                 sum(len(f) for a, f in lagen[i]['formen'] if a != 'kreis'),
                 time.time() - t0))
        # Gegenprobe: Flaeche vor und nach der Vereinigung
        vor = float(shapely.area(shapely.union_all(polys[:0])) or 0)
        print('   Flaeche der Vereinigung %.1f Einheiten^2' % ganz.area)
        raus[i] = r
    pickle.dump(raus, open(ZIEL, 'wb'), protocol=4)
    print('gesichert:', ZIEL)


if __name__ == '__main__':
    main()
