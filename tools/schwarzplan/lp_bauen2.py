# -*- coding: utf-8 -*-
"""Die Kartendatei der Seite bauen, aus den vereinigten Flaechen.

Die Messung hat ergeben, was man sich nur wuenschen kann: Der Rahmen der
gelieferten Zeichnung ist genau derselbe Ausschnitt wie der bisherige
Rasterplan. Massstab 1,0000, Versatz 0/0 Bildpunkte, Jaccard der
Wasserflaechen 0,947. Es ist also nichts einzupassen, nur umzurechnen:

    Rahmen 4375,84..5456,87 / 4524,04..5304,74   ->   0..3010 / 0..2175

Das ist dieselbe Abbildung, die preserveAspectRatio="none" dem
Rasterbild angetan hat. Darum bleiben alle Stationsnadeln genau auf den
Hauskoerpern, auf denen sie heute sitzen.

Die gefuellten Lagen kommen als vereinigte Umrisse herein, nicht mehr
als Dreiecksuppe: 167.458 statt 516.864 Punkte bei den Hauskoerpern.
Geschrieben wird mit relativen Wegstuecken, auf 0,1 Einheiten gerundet,
das sind 13 cm. Jede Koordinate wird einzeln gerundet und die
Verschiebung daraus gebildet, damit sich der Fehler ueber einen langen
Zug nicht aufsummiert.
"""
import gzip
import io
import os
import pickle

RAHMEN = (4375.84, 4524.04, 5456.87, 5304.74)
VW, VH = 3010.0, 2175.0
LAGEN = r"C:\Temp\wij3d\lp\lagen.pkl"
UNION = r"C:\Temp\wij3d\lp\union.pkl"
ZIEL = r"C:\Temp\wij3d\lp\schwarzplan.svg"

KX = VW / (RAHMEN[2] - RAHMEN[0])
KY = VH / (RAHMEN[3] - RAHMEN[1])

FARBE = {'rgb(192,192,192)': '#C7C7C7',    # Wasser, wie im Rasterplan
         'rgb(128,128,128)': '#808080',    # Strassenkanten
         'rgb(137,137,137)': '#898989',
         'rgb(0,0,0)': '#000000'}
# Reihenfolge wie in der Quelle. Die roten Lagen sind Nordpfeil und
# Massstab neben der Zeichnung, Lage 10 ist der Rahmen selbst: beides faellt weg.
NEHMEN = [0, 1, 2, 3, 4, 5]


def zahl(v):
    s = '%.1f' % v
    return s[:-2] if s.endswith('.0') else s


def zug(punkte, zu):
    teile = []
    lx = ly = None
    kopf = ''
    for x, y in punkte:
        rx, ry = round(x, 1), round(y, 1)
        if lx is None:
            kopf = 'M%s %s' % (zahl(rx), zahl(ry))
        else:
            dx, dy = round(rx - lx, 1), round(ry - ly, 1)
            if dx == 0 and dy == 0:
                continue
            teile.append('%s %s' % (zahl(dx), zahl(dy)))
        lx, ly = rx, ry
    if not teile:
        return ''
    return kopf + 'l' + ' '.join(teile) + ('z' if zu else '')


def main():
    lagen = pickle.load(open(LAGEN, 'rb'))
    union = pickle.load(open(UNION, 'rb'))
    x0, y0 = RAHMEN[0], RAHMEN[1]

    def um(p):
        return ((p[0] - x0) * KX, (p[1] - y0) * KY)

    teile = ['<rect x="0" y="0" width="3010" height="2175" fill="#FFFFFF"/>']
    bericht = []
    for i in NEHMEN:
        st = lagen[i]['stil']
        f = st.get('fill', 'none')
        s = st.get('stroke', 'none')
        fill = FARBE.get(f, 'none') if f != 'none' else 'none'
        stroke = FARBE.get(s, 'none') if s != 'none' else 'none'
        sw = float(st.get('stroke-width', 0.1)) * KX
        d = []
        kreise = []
        if i in union:
            for r in union[i]:
                t = zug([um(p) for p in r], True)
                if t:
                    d.append(t)
        else:
            for art, form in lagen[i]['formen']:
                if art == 'kreis':
                    cx, cy, rr = form
                    px, py = um((cx, cy))
                    kreise.append('<circle cx="%s" cy="%s" r="%s"/>'
                                  % (zahl(px), zahl(py), zahl(rr * KX)))
                    continue
                if len(form) < 2:
                    continue
                t = zug([um(p) for p in form], art == 'zu')
                if t:
                    d.append(t)
        if not d and not kreise:
            continue
        g = ('<g fill="%s" stroke="%s" stroke-width="%.2f">' % (fill, stroke, sw)
             + ('<path d="%s"/>' % ''.join(d) if d else '')
             + ''.join(kreise) + '</g>')
        teile.append(g)
        bericht.append('  Lage %2d  %-9s %-9s sw %.2f  %6d Zuege  %8d Zeichen'
                       % (i, fill, stroke, sw, len(d), len(g)))

    kopf = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3010 2175" '
            'width="3010" height="2175" fill-rule="evenodd" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<title>Schwarzplan Rotterdam, Wijnhaven und Umgebung</title>'
            '<desc>Vektorzeichnung im Koordinatenraum der Seite, '
            '1 Einheit = 1,3048 m. Derselbe Ausschnitt wie der bisherige '
            'Rasterplan: Massstab 1,0000, Versatz 0/0 Bildpunkte.</desc>')
    svg = kopf + ''.join(teile) + '</svg>'
    io.open(ZIEL, 'w', encoding='utf-8', newline='\n').write(svg)
    print('\n'.join(bericht))
    roh = len(svg.encode('utf-8'))
    gz = len(gzip.compress(svg.encode('utf-8'), 9))
    print('\n%s: %.2f MB roh, %.0f KB gezippt'
          % (os.path.basename(ZIEL), roh / 1e6, gz / 1024))


if __name__ == '__main__':
    main()
