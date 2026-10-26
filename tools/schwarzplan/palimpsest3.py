# -*- coding: utf-8 -*-
"""Die Fuellungen als Vektor statt als Bild.

Der Auftraggeber hat gesehen, was auch zu sehen war: die aus dem Scan
geholten Flaechen waren fleckig und nicht durchgehend. Das lag an der
Methode, nicht an der Lage. Das Blatt ist gedruckt, die Bauflaechen
tragen eine Textur, und das Liniennetz schneidet quer durch.

Jetzt sind die Flaechen morphologisch geschlossen, von Sprenkeln
befreit und als Polygone nachgezogen. Das Ergebnis ist eine SVG von
87 KB statt eines Bildes von 1,3 MB, und sie bleibt auf jeder
Zoomstufe scharf.

Eingehaengt wird sie beim ersten Druck auf den Knopf und zwar inline.
Ob ein Browser ein verwiesenes SVG beim Zoomen neu rastert, ist nicht
garantiert; inline gilt es. Dieselbe Ueberlegung steht schon beim
Schwarzplan im Quelltext.
"""
import io

R = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
     r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
     r"\Rotterdam-Wijnhaven\index.html")
s = io.open(R, encoding='utf-8-sig').read()


def t(alt, neu):
    global s
    assert s.count(alt) == 1, (s.count(alt), alt[:70])
    s = s.replace(alt, neu)


# ── 1. Aus dem Bild wird eine Gruppe ──
t("""<!-- Die Fuellungen der Stadt von 1940, auf durchsichtigem Grund. Sie
     liegt ueber dem heutigen Plan und unter Route und Marken, denn
     der Palimpsest soll den Weg nicht zudecken. Geladen wird sie erst,
     wenn der Knopf gedrueckt wird. -->
<image id="ov-palimpsest" x="0" y="0" width="3010" height="2175" opacity="0"
       preserveAspectRatio="none" aria-hidden="true"/>""",
  """<!-- Die Fuellungen der Stadt von 1940. Sie liegen ueber dem heutigen
     Plan und unter Route und Marken, denn der Palimpsest soll den Weg
     nicht zudecken. Die Gruppe bleibt leer, bis der Knopf gedrueckt
     wird; dann wird die Zeichnung geholt und hier eingehaengt. Inline
     und nicht als verwiesenes Bild: ob ein Browser ein verwiesenes SVG
     beim Zoomen neu rastert, ist nicht garantiert. -->
<g id="ov-palimpsest" opacity="0" aria-hidden="true"></g>""")

# ── 2. Laden und Einhaengen ──
t("""var PALIMPSEST_QUELLE = 'img/palimpsest.webp';""",
  """var PALIMPSEST_QUELLE = 'img/palimpsest.svg';
var _palimpsestLaeuft = false;

/* Die Zeichnung einmal holen und in die Gruppe haengen. Ihre viewBox
   ist dieselbe wie die der Karte, also braucht es keine Umrechnung. */
function _palimpsestLaden(){
  var g = document.getElementById('ov-palimpsest');
  if (!g || _palimpsestLaeuft || g.childElementCount) return;
  _palimpsestLaeuft = true;
  fetch(PALIMPSEST_QUELLE)
    .then(function(r){ return r.text(); })
    .then(function(txt){
      var doc = new DOMParser().parseFromString(txt, 'image/svg+xml');
      var teile = doc.documentElement.querySelectorAll('g');
      for (var i = 0; i < teile.length; i++)
        g.appendChild(document.importNode(teile[i], true));
    })
    .catch(function(){ _palimpsestLaeuft = false; });
}""")

t("""  /* Die Fuellungsebene, 1,2 MB, deshalb ebenfalls erst auf Verlangen. */
  var pal = document.getElementById('ov-palimpsest');
  if (pal){
    if (PALIMPSEST && !pal.getAttribute('href'))
      pal.setAttribute('href', PALIMPSEST_QUELLE);
    pal.setAttribute('opacity', PALIMPSEST ? PALIMPSEST_DECKUNG.toFixed(2) : '0.00');
  }""",
  """  /* Die Fuellungsebene wird erst auf Verlangen geholt. */
  var pal = document.getElementById('ov-palimpsest');
  if (pal){
    if (PALIMPSEST) _palimpsestLaden();
    pal.setAttribute('opacity', PALIMPSEST ? PALIMPSEST_DECKUNG.toFixed(2) : '0.00');
  }""")

io.open(R, 'w', encoding='utf-8-sig', newline='\r\n').write(s)
print('Fuellungen als Vektor eingehaengt')
