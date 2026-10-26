# -*- coding: utf-8 -*-
"""Der Palimpsest bekommt seine eigene Ebene: nur die Fuellungen.

Bisher lag im Palimpsest das ganze gescannte Blatt von 1940, also auch
Papier, Liniennetz und Beschriftung. Darunter war der heutige Plan
kaum noch zu erkennen.

Jetzt liegt dort eine eigene Ebene mit durchsichtigem Grund, auf der
nur die Fuellungen stehen: die Bebauung orange, das Wasser gruen. Der
heutige Schwarzplan scheint ueberall dazwischen durch, und genau das
macht den Palimpsest lesbar.

Die Ebene steht im Markup zwischen dem heutigen Plan und der
Routenlinie. Damit faellt auch das Umhaengen des Knotens weg, das die
alte Loesung noch brauchte: die Karte von 1940 bleibt zuunterst, wo
sie hingehoert.
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


# ── 1. Die Ebene in das SVG, ueber den heutigen Plan ──
t("""    </g>
    <path class="route-trail" id="routeTrail" d=""/>""",
  """    </g>
<!-- Die Fuellungen der Stadt von 1940, auf durchsichtigem Grund. Sie
     liegt ueber dem heutigen Plan und unter Route und Marken, denn
     der Palimpsest soll den Weg nicht zudecken. Geladen wird sie erst,
     wenn der Knopf gedrueckt wird. -->
<image id="ov-palimpsest" x="0" y="0" width="3010" height="2175" opacity="0"
       preserveAspectRatio="none" aria-hidden="true"/>
    <path class="route-trail" id="routeTrail" d=""/>""")

# ── 2. Das Umhaengen faellt weg ──
t("""/* Die Reihenfolge im Stapel. Normal liegt 1940 zuunterst, im
   Palimpsest muss sie ueber den heutigen Plan, aber unter Route und
   Marken. Der weisse Grund des Schwarzplans deckt sonst alles zu. */
function _stapelOrdnen(){
  var svg = document.getElementById('mapSvg');
  var alt = document.getElementById('ov-1940');
  if (!svg || !alt) return;
  var ziel = PALIMPSEST ? document.getElementById('routeTrail')
                        : svg.firstElementChild;
  if (ziel && alt.nextElementSibling !== ziel) svg.insertBefore(alt, ziel);
}

function _standAnwenden(){
  _stapelOrdnen();
  for (var k in KARTEN_STAENDE){""",
  """function _standAnwenden(){
  for (var k in KARTEN_STAENDE){""")

# ── 3. Die eigene Ebene statt der unteren Schicht ──
t("""    /* Im Palimpsest sind beide Schichten zu sehen, sonst genau eine. */
    var deckung = PALIMPSEST
      ? (k === '1940' ? PALIMPSEST_DECKUNG : 1)
      : (k === KARTEN_STAND ? 1 : 0);
    /* Erst beim ersten Zeigen laden. Wer nie wechselt, soll die
       861 KB der Karte von 1940 auch nicht bezahlen. */
    if (deckung > 0 && e.quelle && !n.getAttribute('href'))
      n.setAttribute('href', e.quelle);
    n.setAttribute('opacity', deckung.toFixed(2));
  }""",
  """    /* Im Palimpsest steht der heutige Plan, darueber die eigene
       Fuellungsebene. Sonst ist genau ein Stand zu sehen. */
    var deckung = PALIMPSEST ? (k === 'heute' ? 1 : 0)
                             : (k === KARTEN_STAND ? 1 : 0);
    /* Erst beim ersten Zeigen laden. Wer nie wechselt, soll die
       861 KB der Karte von 1940 auch nicht bezahlen. */
    if (deckung > 0 && e.quelle && !n.getAttribute('href'))
      n.setAttribute('href', e.quelle);
    n.setAttribute('opacity', deckung.toFixed(2));
  }
  /* Die Fuellungsebene, 1,2 MB, deshalb ebenfalls erst auf Verlangen. */
  var pal = document.getElementById('ov-palimpsest');
  if (pal){
    if (PALIMPSEST && !pal.getAttribute('href'))
      pal.setAttribute('href', PALIMPSEST_QUELLE);
    pal.setAttribute('opacity', PALIMPSEST ? PALIMPSEST_DECKUNG.toFixed(2) : '0.00');
  }""")

t("""var PALIMPSEST = false;
var PALIMPSEST_DECKUNG = 0.70;""",
  """var PALIMPSEST = false;
var PALIMPSEST_DECKUNG = 0.70;
var PALIMPSEST_QUELLE = 'img/palimpsest.webp';""")

# ── 4. Die Quellenzeile nennt jetzt auch das Blatt ──
t('{"key": "eb_palimpsest_quelle", '
  '"de": "Palimpsest: die Stadt von 1940 mit 70 Prozent Deckung \\u00fcber dem heutigen Schwarzplan.", '
  '"nl": "Palimpsest: de stad van 1940 met 70 procent dekking over de huidige zwartplattegrond.", '
  '"en": "Palimpsest: the city of 1940 at 70 per cent over today\\u2019s figure-ground plan."},',
  '{"key": "eb_palimpsest_quelle", '
  '"de": "Palimpsest: die bebauten und die bewasserten Fl\\u00e4chen vor dem 14. Mai 1940, mit 70 Prozent Deckung '
  '\\u00fcber dem heutigen Schwarzplan. Fl\\u00e4chen nach dem Blatt Gemeente Rotterdam en omgeving, 1:10.000, '
  'Stadsarchief Rotterdam, gemeinfrei.", '
  '"nl": "Palimpsest: de bebouwde en de bewaterde vlakken van v\\u00f3\\u00f3r 14 mei 1940, met 70 procent dekking '
  'over de huidige zwartplattegrond. Vlakken naar het blad Gemeente Rotterdam en omgeving, 1:10.000, '
  'Stadsarchief Rotterdam, publiek domein.", '
  '"en": "Palimpsest: the built and the watered areas before 14 May 1940, at 70 per cent over today\\u2019s '
  'figure-ground plan. Areas after the sheet Gemeente Rotterdam en omgeving, 1:10,000, '
  'Stadsarchief Rotterdam, public domain."},')

io.open(R, 'w', encoding='utf-8-sig', newline='\r\n').write(s)
print('Fuellungsebene eingebaut')
