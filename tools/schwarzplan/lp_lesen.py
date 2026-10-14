# -*- coding: utf-8 -*-
"""Den gelieferten Lageplan einlesen und in Lagen zerlegen.

Die Datei ist ein CAD-Export: 172.525 Polygone, 7.206 Polylinien, 6.103
Pfade, alles in flachen <g>-Lagen, die sich nur durch Farbe und
Strichstaerke unterscheiden. Die Geometrie ist einfach, jeder Pfad nur
ein M mit nachfolgenden Punkten und einem z.

Chrome auf diese Datei loszulassen, um sie zu messen, hat sich als
Sackgasse erwiesen: Bei 4578 x 3307 Bildpunkten kam der Schuss nach
einer Viertelstunde noch nicht zurueck. Also wird hier selbst gelesen
und selbst gerastert. Das dauert Sekunden.
"""
import io
import pickle
import re

QUELLE = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
          r"\2026_WS2627_HochschuleWismar\STÄDTEBAU + GEBÄUDELEHRE II"
          r"\10_SONSTIGES\Wijnhaven\Lageplan_groß.svg")
ZIEL = r"C:\Temp\wij3d\lp\lagen.pkl"

ZAHL = re.compile(r'-?\d+(?:\.\d+)?')
MARKE = re.compile(r'<g\s([^>]*?)(/?)>|<(polygon|polyline|path|circle)\s([^>]*?)/>|</g>')
ATTR = re.compile(r'([\w:-]+)="([^"]*)"')


def punkte(text):
    v = [float(x) for x in ZAHL.findall(text)]
    return list(zip(v[0::2], v[1::2]))


def main():
    s = io.open(QUELLE, encoding='utf-8', errors='replace').read()
    lagen = []
    offen = None
    for m in MARKE.finditer(s):
        if m.group(0) == '</g>':
            if offen is not None:
                lagen.append(offen)
                offen = None
            continue
        if m.group(1) is not None:                       # <g ...>
            a = dict(ATTR.findall(m.group(1)))
            if m.group(2) == '/':                        # <g .../> leer
                continue
            offen = {'stil': a, 'formen': []}
            continue
        art, roh = m.group(3), m.group(4)
        if offen is None:
            continue
        a = dict(ATTR.findall(roh))
        if art == 'circle':
            offen['formen'].append(('kreis', (float(a['cx']), float(a['cy']),
                                              float(a['r']))))
        elif art == 'polygon':
            offen['formen'].append(('zu', punkte(a.get('points', ''))))
        elif art == 'polyline':
            offen['formen'].append(('auf', punkte(a.get('points', ''))))
        else:                                            # path
            d = a.get('d', '')
            offen['formen'].append(('zu' if d.rstrip().endswith('z') else 'auf',
                                    punkte(d)))

    print('%d Lagen' % len(lagen))
    for i, l in enumerate(lagen):
        xs = [p[0] for art, f in l['formen'] if art != 'kreis' for p in f]
        ys = [p[1] for art, f in l['formen'] if art != 'kreis' for p in f]
        print('  %2d  %-22s %-22s sw %-5s  %6d Formen  %7d Punkte  x %.0f..%.0f y %.0f..%.0f'
              % (i, l['stil'].get('fill', '-'), l['stil'].get('stroke', '-'),
                 l['stil'].get('stroke-width', '-'), len(l['formen']),
                 len(xs), min(xs or [0]), max(xs or [0]), min(ys or [0]), max(ys or [0])))
    pickle.dump(lagen, open(ZIEL, 'wb'), protocol=4)
    print('\ngesichert: %s' % ZIEL)


if __name__ == '__main__':
    main()
