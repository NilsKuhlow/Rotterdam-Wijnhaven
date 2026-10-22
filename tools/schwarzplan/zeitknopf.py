# -*- coding: utf-8 -*-
"""Die Regler raus, ein Zeitknopf rein.

Der Stapel aus drei Schichten mit Reglern war zu viel Apparat fuer das,
was er leistete. Eine halb aufgedrehte Karte ist weder die eine noch
die andere; lesbar ist immer nur ein Stand. Und einen Palimpsest liest
man ohnehin im Hin und Her, nicht im Dazwischen. Also: ein Knopf, der
an derselben Stelle bleibt und zwischen heute und 1940 umschlaegt.

Die Revisie-Ebene aus dem Seminarbereich faellt damit weg. Sie war die
dritte Schicht und hat ohne Regler keinen Ort mehr; ihre Zeichnung
steht weiterhin als Abbildung im Kapitel Basisplan.
"""
import io
import re

R = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
     r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
     r"\Rotterdam-Wijnhaven\index.html")

s = io.open(R, encoding='utf-8-sig').read()
n0 = len(s)


def tausche(alt, neu, wie_oft=1):
    """Ersetzen und dabei nachzaehlen. Lieber hier scheitern als spaeter
    im Browser."""
    global s
    c = s.count(alt)
    assert c == wie_oft, 'erwartet %d, gefunden %d: %r' % (wie_oft, c, alt[:70])
    s = s.replace(alt, neu)


# -- 1. Die verschluesselte Ebene aus dem SVG nehmen --
tausche("""<!-- Zuschaltbare Kartenebene, zuoberst. Ohne Schluessel bleibt sie leer:
     kein Bild, keine Quelle, keine Lage. Beides setzt _semEbene() aus dem
     verschluesselten Verzeichnis. -->
<image id="ov-ebene" x="0" y="0" opacity="0" preserveAspectRatio="none"
       aria-hidden="true"/>
""", '')

# -- 2. Die drei Zeilen durch einen Knopf ersetzen --
tausche("""  <!-- Schalter fuer die Kartenebenen. Stehen im Kartenfeld, erscheinen mit ihm. -->
  <!-- Regler fuer die Wiederaufbauschicht und der Griff zum Kapitel. Ein
       Regler statt eines Schalters, weil sich zwei Schichten nur im
       Uebergang vergleichen lassen. Startwert 0. -->
""", """  <!-- Schalter fuer die Kartenebenen. Stehen im Kartenfeld, erscheinen mit ihm. -->
""")

alt_zeilen = re.search(
    r"    <!-- Die Schichten, in der Reihenfolge des Stapels.*?"
    r"    <p class=\"eb-quelle\" id=\"eb-quelle\" hidden></p>\n",
    s, re.S)
assert alt_zeilen, 'Schichtzeilen nicht gefunden'
neu_zeilen = """    <!-- Ein Knopf, zwei Staende: der Schwarzplan von heute und die Stadt
         vor dem 14. Mai 1940. Er bleibt an derselben Stelle, denn einen
         Palimpsest liest man im Hin und Her und nicht im Zielen auf zwei
         Knoepfe. Beschriftet ist er mit dem Stand, den der naechste Druck
         zeigt; den Text setzt _standAnwenden() dreisprachig. Keine Regler
         mehr: halb aufgedreht war keine der beiden Karten lesbar. -->
    <button class="eb-schalt eb-zeit" type="button" id="eb-zeit"
            data-i18n-aria="eb_stand" aria-label="Kartenstand wechseln"
            onclick="kartenWechseln()">Stadt 1940</button>
    <!-- Herkunft des gezeigten Standes. Steht nur da, wo es etwas zu
         nennen gibt; der Schwarzplan von heute ist unsere eigene
         Zeichnung. -->
    <p class="eb-quelle" id="eb-quelle" hidden></p>
"""
s = s[:alt_zeilen.start()] + neu_zeilen + s[alt_zeilen.end():]

# -- 3. CSS: Regler und Wertanzeige raus, Zeitknopf rein --
alt_css = re.search(
    r"/\* Eine Zeile je Schicht: Schalter, Regler, Wert\..*?"
    r"\.eb-zeile input\[type=\"range\"\]\[disabled\] \{ opacity:\.3; cursor:default; \}\n",
    s, re.S)
assert alt_css, 'Schicht-CSS nicht gefunden'
neu_css = """/* Der Zeitknopf. Dieselbe Sprache wie die Kapitelknoepfe daneben,
   aber gelb hinterlegt: Er ist der eine Griff, der aendert, was man
   sieht, und die beiden anderen fuehren nur weiter. Die Mindestbreite
   haelt ihn ruhig, wenn die Beschriftung zwischen den Staenden und
   zwischen den Sprachen wechselt. */
.eb-schalt {
  font-family:var(--font-mono); font-size:.54rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-1); white-space:nowrap;
  background:var(--paper-0); border:1px solid var(--ink-1); border-radius:0;
  padding:.44rem .6rem; cursor:pointer; min-width:8.4em; text-align:left;
  -webkit-tap-highlight-color:transparent; touch-action:manipulation;
  transition:background .18s;
}
.eb-zeit { background:var(--accent); font-weight:600; }
.eb-schalt:hover, .eb-schalt:focus-visible { outline:none; box-shadow:inset 0 0 0 2px var(--ink-1); }
"""
s = s[:alt_css.start()] + neu_css + s[alt_css.end():]

# -- 4. _semEbene() faellt weg --
alt_sem = re.search(
    r"/\* .. Die Kartenebene ..\n.*?\n  _ebeneAnwenden\('revisie'\);\n\}\n\n", s, re.S)
assert alt_sem, '_semEbene nicht gefunden'
s = s[:alt_sem.start()] + s[alt_sem.end():]
tausche("""    b.textContent = '';
    b.hidden = true;
  }
  _semEbene();
}""", """    b.textContent = '';
    b.hidden = true;
  }
}""")

# -- 5. Das Schichtmodell durch zwei Staende ersetzen --
alt_js = re.search(
    r"/\* .. Die Kartenebenen ..\n.*?\n  z\.hidden = !t\.length;\n\}\n", s, re.S)
assert alt_js, 'Schicht-JS nicht gefunden'
neu_js = """/* \u2500\u2500 Der Kartenstand \u2500\u2500
   Zwei Staende, kein Dazwischen: der Schwarzplan von heute oder die
   Stadt vor dem 14. Mai 1940. Beide liegen im SVG uebereinander, 1940
   zuunterst; zu sehen ist immer genau einer. Vorher liess sich jede
   Schicht einzeln aufdrehen, und genau das war der Fehler: Bei 40 oder
   60 Prozent las man keine der beiden Karten mehr, sondern ein Rauschen
   aus beiden. Der Palimpsest entsteht im Wechsel. */
var KARTEN_STAND = 'heute';
var KARTEN_STAENDE = {
  'heute': { knoten:'ov-heute' },
  '1940':  { knoten:'ov-1940', quelle:'img/plan-1940-ebene.webp',
             name:'eb_1940', quellzeile:'eb_1940_quelle' }
};
var STAND_FOLGE = ['heute', '1940'];

/* Den Stand zeichnen: eine Schicht sichtbar, die andere nicht, dazu die
   Beschriftung des Knopfs und die Quellenzeile. */
function _standAnwenden(){
  for (var k in KARTEN_STAENDE){
    var e = KARTEN_STAENDE[k];
    var n = document.getElementById(e.knoten);
    if (!n) continue;
    var an = (k === KARTEN_STAND);
    /* Erst beim ersten Umschalten laden. Wer nie wechselt, soll die
       861 KB der Karte von 1940 auch nicht bezahlen. */
    if (an && e.quelle && !n.getAttribute('href'))
      n.setAttribute('href', e.quelle);
    n.setAttribute('opacity', an ? '1.00' : '0.00');
  }
  /* Der Knopf nennt, was der naechste Druck zeigt, mit Pfeil davor:
     ohne ihn liest man die Beschriftung als den gegenwaertigen Stand. */
  var b = document.getElementById('eb-zeit');
  if (b){
    var t = KARTEN_STAENDE[_standNaechster()].name;
    b.textContent = '\\u2192 ' + uiT(t || 'eb_heute');
  }
  var z = document.getElementById('eb-quelle');
  if (z){
    var q = KARTEN_STAENDE[KARTEN_STAND].quellzeile;
    z.textContent = q ? uiT(q) : '';
    z.hidden = !q;
  }
}

function _standNaechster(){
  var i = STAND_FOLGE.indexOf(KARTEN_STAND);
  return STAND_FOLGE[(i + 1) % STAND_FOLGE.length];
}

/* Umschlagen. Bei zwei Staenden ist das Weiterzaehlen dasselbe wie das
   Hin und Her; drei waeren ein Karussell und brauchten wieder eine
   Liste. */
function kartenWechseln(){
  KARTEN_STAND = _standNaechster();
  _standAnwenden();
}
"""
s = s[:alt_js.start()] + neu_js + s[alt_js.end():]

# -- 6. Reste: Sperren, Sprachwechsel, Einblenden --
tausche("""  SEMINAR = { auf:false, schluessel:null, inhalt:null, blobs:[] };
  EBENEN['revisie'].an = false;
  _semKnopf();""", """  SEMINAR = { auf:false, schluessel:null, inhalt:null, blobs:[] };
  _semKnopf();""")
tausche("  if (typeof _semKnopf === 'function') _semKnopf();\n}",
        "  if (typeof _semKnopf === 'function') _semKnopf();\n"
        "  if (typeof _standAnwenden === 'function') _standAnwenden();\n}")
tausche("  if (an && typeof _ebenenAlleAnwenden === 'function') _ebenenAlleAnwenden();",
        "  if (an && typeof _standAnwenden === 'function') _standAnwenden();")

# -- 7. Der Name des Knopfs fuer Hilfsmittel --
tausche('{"key": "eb_heute",',
        '{"key": "eb_stand", "de": "Kartenstand wechseln", '
        '"nl": "Kaartstand wisselen", "en": "Switch the map state"},'
        '{"key": "eb_heute",')

io.open(R, 'w', encoding='utf-8-sig', newline='\r\n').write(s)
print('index.html: %d -> %d Zeichen' % (n0, len(s)))
for w in ('ov-ebene', 'eb-zeile', 'eb-regler', 'eb-zahl', 'eb-wert', 'EBENEN',
          'ebeneSchalten', 'ebeneDeckung', '_semEbene', '_ebeneQuelle',
          '_ebenenAlleAnwenden', 'type="range"'):
    c = s.count(w)
    print('  %-22s %s' % (w, 'weg' if not c else 'NOCH %d DA' % c))
