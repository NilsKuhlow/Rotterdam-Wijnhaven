# -*- coding: utf-8 -*-
"""Zwei gemeinfreie Karten fuer die offene Seite aufbereiten.

Der Auftrag war, Grundrisse und historische Karten herauszusuchen. Das
Ergebnis faellt besser aus als erwartet: Die beiden wichtigsten Blaetter
sind gemeinfrei und gehoeren damit nicht hinter das Schloss, sondern
offen in die Seite.

  Gemeente Rotterdam en omgeving, 1:10.000, 1940
      Die Vorkriegsstadt mit Strassennamen. Vom Stadsarchief Rotterdam
      ausdruecklich als gemeinfrei freigegeben. Das Blatt zeigt die ganze
      Gemeinde, 9894 x 7900 Bildpunkte; gebraucht wird die Innenstadt,
      also wird zugeschnitten statt verkleinert. Sonst waere der
      Wijnhaven ein Fleck von zwanzig Bildpunkten.

  Oud en nieuw Rotterdam, 1:5.000, 18. Mai 1955
      Der Vorkriegsgrundriss, darueber der Plan der neuen Stadtkerns und
      der Stand des Wiederaufbaus, dazu die Brandgrenze in Gelb.
      Anonymes Werk, Schutzfrist siebzig Jahre nach Veroeffentlichung,
      also seit 2025 abgelaufen.

Damit faellt auch ein Mangel weg, den dieses Projekt lange mit sich
trug: Es gab keinen Plan der Vorkriegsstadt. Einmal wurde dafuer sogar
eine Platzhalterzeichnung erfunden und wieder entfernt. Jetzt steht das
Blatt da, auf dem es wirklich steht.
"""
import io
import os

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

QUELLE = r'C:\Temp\wij3d\karten'
ZIEL = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven\img")

BREITE = 2200          # Bildpunkte; die Karte soll sich vergroessern lassen
GUETE = 84


def speichern(im, name, guete=GUETE):
    if im.width > BREITE:
        k = BREITE / im.width
        im = im.resize((BREITE, round(im.height * k)), Image.LANCZOS)
    p = os.path.join(ZIEL, name)
    im.save(p, 'WEBP', quality=guete, method=6)
    print('  %-26s %4d x %4d  %6.0f KB'
          % (name, im.width, im.height, os.path.getsize(p) / 1024))
    return im.width, im.height


def main():
    masse = {}

    # ── 1940: Zuschnitt auf die Innenstadt ──
    im = Image.open(os.path.join(QUELLE, 'plan1940.jpg')).convert('RGB')
    k = im.width / 1100.0            # Faktor der Vorschau, an der gemessen wurde
    zuschnitt = im.crop((int(430 * k), int(230 * k), int(680 * k), int(390 * k)))
    masse['plan-1940'] = speichern(zuschnitt, 'plan-1940.webp')

    # ── 1955: ganzes Blatt, es zeigt genau die Innenstadt ──
    im = Image.open(os.path.join(QUELLE, 'oudnieuw1955.jpg')).convert('RGB')
    # Farbiger Steindruck mit feiner Schrift: tiefer gehen bringt wenig
    # (q70 733 KB, q84 1016 KB), q78 ist der Punkt, an dem die
    # Strassennamen noch stehen.
    masse['oud-en-nieuw-1955'] = speichern(im, 'oud-en-nieuw-1955.webp', 78)

    print('\nMasse fuer index.html:')
    for n, (w, h) in masse.items():
        print('  %-20s w=%d h=%d' % (n, w, h))


if __name__ == '__main__':
    main()
