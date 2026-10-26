# -*- coding: utf-8 -*-
"""Die Fuellungen aus der Vektor-PDF holen.

Die erste Fassung hat sie aus dem gescannten Blatt nach Farbe geholt.
Das war falsch, und der Auftraggeber hat es gesehen: Das Blatt faerbt
nach eigener Konvention, im Zentrum nur einzelne oeffentliche Bauten,
in den aeusseren Vierteln ganze Bloecke. Was dabei herauskam, war die
Legende des Blattes und nicht die Zeichnung, die er angelegt hat.

Die gelieferte Vektor-PDF enthaelt genau diese Zeichnung: einen
gefuellten Pfad mit rund 2000 Strecken, also die Bloecke, die auch in
der DWG stehen.

Die Lage ergibt sich aus der zweiten PDF, die dieselbe Seite benutzt
und zusaetzlich das Blatt als Bild traegt. Das Bild misst 3093 x 2235
Punkte und ist der Ausschnitt, der dem Rahmen der Seite entspricht; es
liegt mit 1,8 Punkten je Bildpunkt an einer bekannten Stelle. Damit
laesst sich jeder Punkt der Zeichnung ueber das Bild in den
Koordinatenraum der Seite rechnen, ohne irgendetwas zu suchen.
"""
import io
import os

import fitz

VEKTOR = r'C:\Temp\wij3d\dwg\fill_vektor.pdf'
MIT_BILD = r'C:\Temp\wij3d\dwg\fill.pdf'
AUS = r'C:\Temp\wij3d\dwg'

VW, VH = 3010.0, 2175.0
BAU = '#C06A2E'
GLAETTE = 0.35          # Punkte, nur gegen doppelte Stuetzstellen


def bildlage():
    """Wo liegt das Blatt auf der Seite, und wie gross ist es?"""
    p = fitz.open(MIT_BILD)[0]
    inf = p.get_image_info(xrefs=True)[0]
    x0, y0, x1, y1 = inf['bbox']
    return (x0, y0, (x1 - x0) / inf['width'], (y1 - y0) / inf['height'],
            inf['width'], inf['height'])


def pfade():
    """Die Teilpfade des gefuellten Pfades als Punktfolgen."""
    p = fitz.open(VEKTOR)[0]
    raus = []
    for z in p.get_drawings():
        if not z.get('fill'):
            continue
        lauf = []
        for it in z['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if not lauf:
                    lauf = [(a.x, a.y)]
                elif abs(lauf[-1][0] - a.x) > 0.01 or abs(lauf[-1][1] - a.y) > 0.01:
                    if len(lauf) >= 3:
                        raus.append(lauf)
                    lauf = [(a.x, a.y)]
                lauf.append((b.x, b.y))
        if len(lauf) >= 3:
            raus.append(lauf)
    return raus


def main():
    bx, by, sx, sy, bw, bh = bildlage()
    print('Blatt auf der Seite: Ursprung (%.2f, %.2f), %.4f x %.4f Punkte je Bildpunkt, %d x %d'
          % (bx, by, sx, sy, bw, bh))

    # Seite -> Bildpunkt -> viewBox, in einem Schritt.
    kx = (VW / bw) / sx
    ky = (VH / bh) / sy
    ox = -bx * kx
    oy = -by * ky
    print('Abbildung: vx = %.6f * X %+0.2f   vy = %.6f * Y %+0.2f' % (kx, ox, ky, oy))

    teile = pfade()
    n = sum(len(t) for t in teile)
    print('Teilpfade: %d mit zusammen %d Punkten' % (len(teile), n))

    xs = [p[0] for t in teile for p in t]
    ys = [p[1] for t in teile for p in t]
    vx0, vx1 = min(xs) * kx + ox, max(xs) * kx + ox
    vy0, vy1 = min(ys) * ky + oy, max(ys) * ky + oy
    print('Ausdehnung in viewBox-Einheiten: x %.0f..%.0f  y %.0f..%.0f  (%.0f x %.0f)'
          % (vx0, vx1, vy0, vy1, vx1 - vx0, vy1 - vy0))

    d = []
    for t in teile:
        q = [(x * kx + ox, y * ky + oy) for x, y in t]
        # doppelte Stuetzstellen wegnehmen, sonst blaeht der Pfad auf
        s = [q[0]]
        for pt in q[1:]:
            if abs(pt[0] - s[-1][0]) > GLAETTE or abs(pt[1] - s[-1][1]) > GLAETTE:
                s.append(pt)
        if len(s) < 3:
            continue
        d.append('M%.1f %.1f' % s[0] + ''.join('L%.1f %.1f' % p for p in s[1:]) + 'Z')

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" '
           'width="%g" height="%g" fill-rule="evenodd">'
           '<title>Palimpsest: die Stadt vor dem 14. Mai 1940</title>'
           '<desc>Bebaute Flaechen, gezeichnet nach dem Blatt Gemeente Rotterdam en '
           'omgeving, 1:10.000, Stadsarchief Rotterdam, gemeinfrei. Im Koordinatenraum '
           'der Seite, 1 Einheit = 1,3048 m.</desc>'
           '<g fill="%s"><path d="%s"/></g></svg>'
           % (VW, VH, VW, VH, BAU, ' '.join(d)))
    ziel = os.path.join(AUS, 'palimpsest.svg')
    io.open(ziel, 'w', encoding='utf-8', newline='\n').write(svg)
    print('palimpsest.svg: %d Flaechen, %.0f KB' % (len(d), os.path.getsize(ziel) / 1024))


if __name__ == '__main__':
    main()
