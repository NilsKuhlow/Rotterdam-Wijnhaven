# -*- coding: utf-8 -*-
"""Die Wiederaufbauschicht aus der Revisiekarte neu herausloesen.

Aus der Revisiekarte wird allein das Rote gezogen, also die Bauten, die
vom Basisplan tatsaechlich ausgefuehrt wurden. Alles andere wird
durchsichtig; was bleibt, ist eine Schicht, die sich ueber den
Schwarzplan legen laesst.

Die Lage stammt nicht aus diesem Lauf, sondern aus der Einmessung vom
13. Oktober, gespeichert in revisie_reg.pkl: 2,27 m je Bildpunkt,
nordgerichtet, translate(442,3 -93,8) scale(1,73952) im Koordinatenraum
der Seite. Sie wurde damals mit drei Verfahren geprueft, und der
verbleibende Rest von rund 10 m ist die Aufloesung der Vorlage selbst,
1600 Bildpunkte auf 3,6 km, nicht ein Fehler der Einpassung.

Der Unterschied zum Blatt von 1940, an dem ich heute gescheitert bin:
Diese Vorlage ist eine am Rechner gezeichnete Karte in einem festen
Raster, kein abfotografiertes Papier mit Verzug.
"""
import os
import pickle

import numpy as np
from PIL import Image

QUELLE = r'C:\Temp\wij3d\revisie.jpg'
REG = r'C:\Temp\wij3d\revisie_reg.pkl'
ZIEL = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Input\Privat"
        r"\revisie-ebene.png")

ROT = (198, 22, 30)          # Signalrot der Seite, nicht das der Vorlage


def main():
    r = pickle.load(open(REG, 'rb'))
    im = Image.open(QUELLE).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    # Dieselbe Schwelle wie im Oktober: deutlich rot, nicht nur waermer.
    rot = (R > 135) & ((R - G) > 55) & ((R - B) > 55)
    print('Vorlage %d x %d, rote Flaeche %.2f %%' % (im.width, im.height,
                                                     100 * rot.mean()))

    aus = np.zeros((im.height, im.width, 4), np.uint8)
    aus[rot] = ROT + (255,)
    bild = Image.fromarray(aus)
    bild.save(ZIEL)
    print('%s: %d x %d, %.0f KB' % (os.path.basename(ZIEL), bild.width,
                                    bild.height, os.path.getsize(ZIEL) / 1024))
    print('\nLage aus der Einmessung:')
    print('  %.2f m je Bildpunkt, NCC %.3f' % (r['m_je_px'], r['ncc']))
    print('  translate(%.1f %.1f) scale(%.5f)' % (r['tx'], r['ty'], r['s']))
    print('  Breite in Einheiten: %.0f  (= %.0f m)'
          % (im.width * r['s'], im.width * r['m_je_px']))


if __name__ == '__main__':
    main()
