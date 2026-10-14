# -*- coding: utf-8 -*-
"""Die Vektorkarte in die Seite setzen.

Bisher lag der Schwarzplan als Rasterbild vor, 4578 x 3307 Bildpunkte
fuer 3,9 x 2,8 km, also 0,86 m je Bildpunkt. Beim Hineinzoomen auf eine
Station zeigte die Karte darum Treppen statt Kanten.

Der gelieferte Lageplan ist derselbe Ausschnitt, nur als Zeichnung.
Gemessen, nicht angenommen: Wasserflaeche gegen Wasserflaeche
kreuzkorreliert, Maximum bei Massstab 1,0000 und Versatz 0/0
Bildpunkten, Jaccard 0,947. Die Hauskoerper kommen auf 0,912, und alle
sieben Stationen liegen hoechstens 12 m von einem Koerper entfernt,
fuenf davon mitten darauf. Das ist genau die Lagegenauigkeit, die der
Rasterplan auch hatte.

Angezeigt wird die Datei zuerst als verwiesenes Bild, damit die Karte
ohne Umweg da ist. Danach wird dieselbe Datei im Leerlauf geholt und in
das Karten-SVG hineingeschrieben, und das Bild faellt weg. Grund: Ob
ein Browser ein verwiesenes SVG beim Zoomen neu rastert, ist nicht
garantiert. Chrome tut es, gemessen an einer Zoomprobe; inline gilt es
ueberall.
"""
import io
import os
import shutil
import subprocess
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')
SW = os.path.join(REPO, 'sw.js')
QUELLE = r"C:\Temp\wij3d\lp\schwarzplan.svg"
ZIEL = os.path.join(REPO, 'img', 'schwarzplan.svg')

ALT_BILD = """<!-- Der Schwarzplan als Bild. Diese Fassung kam als Raster, nicht als
     Vektor; verlustfrei als WebP sind es 250 KB, verlustbehaftet waere
     es ein Vielfaches. preserveAspectRatio="none" ist richtig: Das Bild
     deckt den viewBox-Raum genau ab, es wird nichts verzerrt. -->
<image class="plan-bild" href="img/schwarzplan.webp" x="0" y="0" width="3010" height="2175" preserveAspectRatio="none"/>"""

NEU_BILD = """<!-- Der Schwarzplan als Zeichnung, nicht mehr als Bild. Die Datei deckt
     den viewBox-Raum genau ab, darum preserveAspectRatio="none"; verzerrt
     wird dabei nichts, der Ausschnitt ist derselbe wie zuvor.
     Zuerst steht sie als verwiesenes Bild da, damit die Karte ohne Umweg
     erscheint. Gleich danach schreibt planVektorInline() dieselbe Datei in
     das <g> darunter und nimmt das Bild weg: Ob ein Browser ein verwiesenes
     SVG beim Zoomen neu rastert, ist nicht garantiert, inline gilt es. -->
<image class="plan-bild" href="img/schwarzplan.svg" x="0" y="0" width="3010" height="2175" preserveAspectRatio="none"/>
<g id="plan-vektor" aria-hidden="true"></g>"""

ALT_KOMMENTAR = """   Der Plan liegt als Rasterbild vor, 4578 x 3307 px bei 300 dpi, und zeigt
   3.9 x 2.8 km: die Innenstadt, die Maas und die Kop van Zuid. Wo er
   liegt, wurde gemessen und nicht geschaetzt: seine Wasserflaeche gegen
   die des alten OSM-Plans kreuzkorreliert, mittelwertfrei und oertlich
   normiert. Das Maximum sass bei -0.1 Grad Drehung und 1:10134, einem
   krummen Massstab, wie ihn ein auf das Blatt gerechneter Export ergibt.
   Gegenprobe: fuenf der sieben Bauten liegen im eigenen Hauskoerper, die
   beiden anderen 6 m und 13 m daneben."""

NEU_KOMMENTAR = """   Der Plan liegt seit Oktober 2026 als Zeichnung vor und nicht mehr als
   Bild: 19.146 Zuege statt 4578 x 3307 Bildpunkten, also scharf auf jeder
   Zoomstufe. Er zeigt 3,9 x 2,8 km, die Innenstadt, die Maas und die Kop
   van Zuid. Wo er liegt, wurde gemessen und nicht angenommen: seine
   Wasserflaeche gegen die des bisherigen Rasterplans kreuzkorreliert. Das
   Maximum sass bei Massstab 1,0000 und Versatz 0/0 Bildpunkten, Jaccard
   0,947; der Ausschnitt ist also derselbe. Die Hauskoerper kommen auf
   0,912. Gegenprobe: fuenf der sieben Bauten liegen im eigenen
   Hauskoerper, die beiden anderen 12 m und 5 m daneben."""

ALT_JS = """window.addEventListener('load', function(){
  (window.requestIdleCallback || function(f){ setTimeout(f, 1400); })(loadModelViewer);
});"""

NEU_JS = """window.addEventListener('load', function(){
  (window.requestIdleCallback || function(f){ setTimeout(f, 1400); })(loadModelViewer);
});

/* ── Den Schwarzplan aus dem verwiesenen Bild in das Karten-SVG holen.
      Dieselbe Datei, nur inline: Erst dann ist sicher, dass jeder Browser
      sie beim Zoomen neu zeichnet statt ein einmal gerastertes Bild zu
      vergroessern. Schlaegt es fehl, bleibt das Bild stehen und die Karte
      sieht aus wie zuvor. Der Service Worker hat die Datei zu diesem
      Zeitpunkt schon im Cache, es geht also kein zweiter Abruf ins Netz. ── */
function planVektorInline(){
  var ziel = document.getElementById('plan-vektor');
  if (!ziel || ziel.firstChild) return;
  fetch('img/schwarzplan.svg')
    .then(function(r){ return r.ok ? r.text() : null; })
    .then(function(t){
      if (!t) return;
      var doc = new DOMParser().parseFromString(t, 'image/svg+xml');
      if (doc.querySelector('parsererror')) return;
      /* Nur die Zeichnung uebernehmen. title und desc der Datei blieben
         sonst als Kurzhinweis ueber der ganzen Karte haengen. */
      var zeichnung = doc.documentElement.querySelectorAll(':scope > g, :scope > rect');
      if (!zeichnung.length) return;
      for (var i = 0; i < zeichnung.length; i++)
        ziel.appendChild(document.importNode(zeichnung[i], true));
      ziel.setAttribute('fill-rule', 'evenodd');
      ziel.setAttribute('stroke-linecap', 'round');
      ziel.setAttribute('stroke-linejoin', 'round');
      var bild = document.querySelector('.plan-bild');
      if (bild && bild.parentNode) bild.parentNode.removeChild(bild);
    })
    .catch(function(){ /* Bild bleibt stehen */ });
}
window.addEventListener('load', function(){
  (window.requestIdleCallback || function(f){ setTimeout(f, 900); })(planVektorInline);
});"""


def main():
    shutil.copyfile(QUELLE, ZIEL)
    kb = os.path.getsize(ZIEL) / 1024
    alt_kb = os.path.getsize(os.path.join(REPO, 'img', 'schwarzplan.webp')) / 1024
    print('img/schwarzplan.svg: %.0f KB (bisher als WebP %.0f KB)' % (kb, alt_kb))

    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(ALT_BILD, NEU_BILD, 'Plan als Zeichnung statt als Bild')
    tausch(ALT_KOMMENTAR, NEU_KOMMENTAR, 'Kommentar zur Verortung')
    tausch(ALT_JS, NEU_JS, 'planVektorInline()')
    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)

    w = io.open(SW, encoding='utf-8', newline='').read()
    a = "  '/img/schwarzplan.webp',      /* die Karte selbst, 253 KB */"
    if w.count(a) != 1:
        sys.exit('FEHLER: Zeile im sw.js nicht gefunden')
    w = w.replace(a, "  '/img/schwarzplan.svg',       /* die Karte selbst, %.0f KB als Zeichnung */" % kb)
    io.open(SW, 'w', encoding='utf-8', newline='').write(w)
    print('OK  sw.js laedt die Zeichnung vor')

    os.remove(os.path.join(REPO, 'img', 'schwarzplan.webp'))
    print('OK  img/schwarzplan.webp geloescht')


if __name__ == '__main__':
    main()
