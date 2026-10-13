# -*- coding: utf-8 -*-
"""Schiefe Aufnahmen beim Aufbereiten geradestellen.

Die Originale in "Fotos Export" bleiben unberuehrt. Gedreht wird erst auf dem
Weg zur Website, damit der Eingriff jederzeit ruecknehmbar ist: Winkel aus der
Tabelle streichen, Bilder neu erzeugen, fertig.

Die Winkel sind gemessen und von Hand nachgeprueft. Gemessen wurde mit zwei
voneinander unabhaengigen Zeugen: der Richtung der fast senkrechten und der
der fast waagerechten Kanten. Eine echte Kameradrehung verdreht beide um
denselben Betrag, Perspektive und Dachschraegen nicht. Nur wo beide Zeugen
innerhalb von 1,2 Grad uebereinstimmten, gilt der Wert; jede Korrektur wurde
danach mit einem Gitter im Bild gegengeprueft.

Warum nicht alle 58: Die Kubuswoningen bestehen aus um 45 Grad gekippten
Wuerfeln, und die meisten Aufnahmen blicken nach oben. Dort gibt es keine
Senkrechte, an der sich eine Messung festhalten koennte. Was dort schief
aussieht, ist die Sache selbst.
"""
import math

from PIL import Image

# Datei aus "Fotos Export" -> Drehung in Grad (positiv: gegen den Uhrzeigersinn)
WINKEL = {
    'Rotterdam-14.jpg': +3.19,   # Kubuswoningen, Blick die Wohnstrasse entlang
    'Rotterdam-59.jpg': -3.07,   # EY, Lochfassade
    'Rotterdam-41.jpg': +1.86,   # Wijnhaveneiland, Hafenbecken
    'Rotterdam-33.jpg': -1.20,   # Witte Huis, vom Kai
    'Rotterdam-39.jpg': +0.69,   # Witte Huis, Oude Haven
    'Rotterdam-43.jpg': -0.60,   # Kubuswoningen, ueber der Oude Haven
    'Rotterdam-27.jpg': -0.51,   # Kubuswoningen, Ladenzeile
}


def _kasten(w, h, grad):
    """Groesstes zentriertes Rechteck gleichen Seitenverhaeltnisses im gedrehten Bild.

    Ohne diesen Zuschnitt staenden nach dem Drehen leere Ecken im Bild.
    """
    a = abs(math.radians(grad))
    lang, kurz = (w, h) if w >= h else (h, w)
    sa, ca = abs(math.sin(a)), abs(math.cos(a))
    if kurz <= 2 * sa * ca * lang or abs(sa - ca) < 1e-10:
        x = 0.5 * kurz
        return (x / sa, x / ca) if w >= h else (x / ca, x / sa)
    c = ca * ca - sa * sa
    return (w * ca - h * sa) / c, (h * ca - w * sa) / c


def geraderuecken(im, datei):
    """Bild drehen und auf den vollen Rahmen zuschneiden. Unbekannte bleiben, wie sie sind."""
    g = WINKEL.get(datei)
    if not g:
        return im, 0.0
    w, h = im.size
    gedreht = im.rotate(g, resample=Image.BICUBIC, expand=False)
    wr, hr = _kasten(w, h, g)
    cx, cy = w / 2.0, h / 2.0
    zu = gedreht.crop((int(round(cx - wr / 2)), int(round(cy - hr / 2)),
                       int(round(cx + wr / 2)), int(round(cy + hr / 2))))
    # Seitenverhaeltnis exakt halten, damit die Masse in index.html stimmen
    return zu.resize((w, h), Image.LANCZOS), g
