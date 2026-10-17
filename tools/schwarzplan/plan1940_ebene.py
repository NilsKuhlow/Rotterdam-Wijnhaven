# -*- coding: utf-8 -*-
"""Den Plan von 1940 in den Kartenrahmen rechnen.

Nach sieben Anlaeufen die Aufloesung des Raetsels: Das Blatt bei
Wikimedia ist kein 300-dpi-Scan, wie die Metadaten an einer Stelle
behaupten, sondern entspricht 200 dpi. Bei 1:10.000 sind das
1,270 m je Bildpunkt statt der angenommenen 0,847. Alle meine Suchen
lagen damit um den Faktor 1,5 im Massstab daneben, und deshalb ist nie
etwas eingerastet.

Mit dem richtigen Wert rastet es sofort ein: Jaccard der
Wasserflaechen 0,692, mit sauberem Anstieg und Abfall zu beiden Seiten.
Was uebrig bleibt, ist kein Fehler, sondern Geschichte: die seither
zugeschuetteten Grachten und die nach dem Krieg veraenderten Kaikanten.

Gerechnet wird genau die Kette, mit der gemessen wurde: Blatt um 0,4
Grad drehen, Rahmen ausschneiden, auf die Zielbreite bringen. Das Bild
deckt danach den viewBox-Raum ohne eigene Transformation ab, wie der
Schwarzplan auch.
"""
import io
import os
import pickle

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

QUELLE = r'C:\Temp\wij3d\karten\plan1940.jpg'
REG = r'C:\Temp\wij3d\karten\final1940.pkl'
ZIEL = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven\img\plan-1940-ebene.webp")

VW, VH = 3010.0, 2175.0
BREITE = 3000            # Zielbreite; die Quelle gibt 3093 her, mehr waere erfunden


def main():
    r = pickle.load(open(REG, 'rb'))
    px = r['px_je_einheit'] / r['s']          # Blattpunkte je Zeicheneinheit
    fp = r['festpunkt_blatt']
    fs = r['festpunkt_seite']
    ux = fp[0] - (fs[0] + r['dx']) * px
    uy = fp[1] - (fs[1] + r['dy']) * px
    print('Einmessung: %.4f m je Bildpunkt, Drehung %+.1f Grad, Jaccard %.3f'
          % (r['m_je_px'], r['grad'], r['jaccard']))
    print('Rahmen im Blatt: (%.0f, %.0f) bis (%.0f, %.0f), also %.0f x %.0f Punkte'
          % (ux, uy, ux + VW * px, uy + VH * px, VW * px, VH * px))

    blatt = Image.open(QUELLE).convert('RGB')
    if r['grad']:
        blatt = blatt.rotate(r['grad'], Image.BICUBIC, center=fp, fillcolor=(255, 255, 255))
    hoehe = int(round(BREITE * VH / VW))
    aus = blatt.resize((BREITE, hoehe), Image.LANCZOS,
                       box=(ux, uy, ux + VW * px, uy + VH * px))

    for q in (72, 78, 84):
        b = io.BytesIO()
        aus.save(b, 'WEBP', quality=q, method=6)
        print('  q%-3d %6.0f KB' % (q, len(b.getvalue()) / 1024))
    aus.save(ZIEL, 'WEBP', quality=78, method=6)
    print('\n%s: %d x %d, %.0f KB'
          % (os.path.basename(ZIEL), aus.width, aus.height,
             os.path.getsize(ZIEL) / 1024))
    print('Aufloesung: %.3f m je Bildpunkt' % (VW / BREITE / 0.7664240847195386))


if __name__ == '__main__':
    main()
