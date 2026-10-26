# -*- coding: utf-8 -*-
"""Ein dritter Knopf: Palimpsest.

Bisher zeigt die Karte entweder heute oder 1940. Der neue Knopf legt
die historische Karte mit 70 Prozent Deckung ueber den heutigen
Schwarzplan, sodass beide zugleich zu sehen sind.

Das ist nicht der alte Regler zurueck. Der liess jeden Wert zu, und bei
40 oder 60 Prozent las man keine der beiden Karten mehr. Hier gibt es
genau einen Wert, und er ist gewaehlt: bei 70 Prozent bleibt die alte
Stadt lesbar und der heutige Plan scheint als Raster durch.

Der Zeitknopf und der Palimpsest schliessen einander aus. Wer den
Zeitknopf drueckt, verlaesst den Palimpsest; wer den Palimpsest
einschaltet, sieht beide Staende.
"""
import io

R = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
     r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
     r"\Rotterdam-Wijnhaven\index.html")

s = io.open(R, encoding='utf-8-sig').read()


def t(alt, neu, n=1):
    global s
    assert s.count(alt) == n, (s.count(alt), alt[:70])
    s = s.replace(alt, neu)


# ── 1. Der Knopf ──
t("""    <button class="eb-schalt eb-zeit" type="button" id="eb-zeit"
            data-i18n-aria="eb_stand" aria-label="Kartenstand wechseln"
            onclick="kartenWechseln()">Stadt 1940</button>""",
  """    <button class="eb-schalt eb-zeit" type="button" id="eb-zeit"
            data-i18n-aria="eb_stand" aria-label="Kartenstand wechseln"
            onclick="kartenWechseln()">Stadt 1940</button>
    <!-- Der dritte Knopf legt beide Staende uebereinander, die alte
         Karte mit 70 Prozent Deckung. Ein Schalter und kein Regler:
         der Wert ist gewaehlt und nicht dem Zufall des Ziehens
         ueberlassen. -->
    <button class="eb-schalt eb-palimpsest" type="button" id="eb-palimpsest"
            aria-pressed="false"
            data-i18n-aria="eb_palimpsest_hilfe" aria-label="Beide Karten übereinander legen"
            data-i18n="eb_palimpsest" onclick="palimpsestSchalten()">Palimpsest</button>""")

# ── 2. Die Oberflaechentexte ──
t('{"key": "eb_stand",',
  '{"key": "eb_palimpsest", "de": "Palimpsest", "nl": "Palimpsest", "en": "Palimpsest"},'
  '{"key": "eb_palimpsest_hilfe", "de": "Beide Karten \\u00fcbereinander legen", '
  '"nl": "Beide kaarten over elkaar leggen", '
  '"en": "Lay both maps over each other"},'
  '{"key": "eb_palimpsest_quelle", '
  '"de": "Palimpsest: die Stadt von 1940 mit 70 Prozent Deckung \\u00fcber dem heutigen Schwarzplan.", '
  '"nl": "Palimpsest: de stad van 1940 met 70 procent dekking over de huidige zwartplattegrond.", '
  '"en": "Palimpsest: the city of 1940 at 70 per cent over today\\u2019s figure-ground plan."},'
  '{"key": "eb_stand",')

# ── 3. Das Zustandsmodell ──
t("""var KARTEN_STAND = 'heute';""",
  """var KARTEN_STAND = 'heute';
/* Der Palimpsest ist ein eigener Zustand neben dem Stand: beide
   Schichten zugleich, die alte mit 70 Prozent Deckung. */
var PALIMPSEST = false;
var PALIMPSEST_DECKUNG = 0.70;""")

t("""function _standAnwenden(){
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
}""",
  """function _standAnwenden(){
  for (var k in KARTEN_STAENDE){
    var e = KARTEN_STAENDE[k];
    var n = document.getElementById(e.knoten);
    if (!n) continue;
    /* Im Palimpsest sind beide Schichten zu sehen, sonst genau eine. */
    var deckung = PALIMPSEST
      ? (k === '1940' ? PALIMPSEST_DECKUNG : 1)
      : (k === KARTEN_STAND ? 1 : 0);
    /* Erst beim ersten Zeigen laden. Wer nie wechselt, soll die
       861 KB der Karte von 1940 auch nicht bezahlen. */
    if (deckung > 0 && e.quelle && !n.getAttribute('href'))
      n.setAttribute('href', e.quelle);
    n.setAttribute('opacity', deckung.toFixed(2));
  }
  /* Der Knopf nennt, was der naechste Druck zeigt, mit Pfeil davor:
     ohne ihn liest man die Beschriftung als den gegenwaertigen Stand. */
  var b = document.getElementById('eb-zeit');
  if (b){
    var t = KARTEN_STAENDE[_standNaechster()].name;
    b.textContent = '\\u2192 ' + uiT(t || 'eb_heute');
  }
  var pb = document.getElementById('eb-palimpsest');
  if (pb) pb.setAttribute('aria-pressed', PALIMPSEST ? 'true' : 'false');
  var z = document.getElementById('eb-quelle');
  if (z){
    var q = PALIMPSEST ? 'eb_palimpsest_quelle'
                       : KARTEN_STAENDE[KARTEN_STAND].quellzeile;
    z.textContent = q ? uiT(q) : '';
    z.hidden = !q;
  }
}

/* Palimpsest an oder aus. Er schliesst den Wechsel der Staende nicht
   aus, ueberschreibt ihn aber, solange er an ist. */
function palimpsestSchalten(){
  PALIMPSEST = !PALIMPSEST;
  _standAnwenden();
}""")

# Der Zeitknopf verlaesst den Palimpsest.
t("""function kartenWechseln(){
  KARTEN_STAND = _standNaechster();
  _standAnwenden();
}""",
  """function kartenWechseln(){
  /* Wer den Stand wechselt, will einen Stand sehen und nicht beide. */
  PALIMPSEST = false;
  KARTEN_STAND = _standNaechster();
  _standAnwenden();
}""")

# ── 4. Das Aussehen: gedrueckt wird gelb, wie die uebrigen Schalter ──
t(".eb-zeit { background:var(--accent); font-weight:600; min-width:11.9em; }",
  """.eb-zeit { background:var(--accent); font-weight:600; min-width:11.9em; }
/* Der Palimpsest ist ein Schalter und kein Weg: weiss, solange er aus
   ist, gelb, sobald beide Karten uebereinander liegen. */
.eb-palimpsest { min-width:7.4em; }
.eb-palimpsest[aria-pressed="true"] { background:var(--accent); font-weight:600; }""")

io.open(R, 'w', encoding='utf-8-sig', newline='\r\n').write(s)
print('Palimpsest-Knopf eingebaut')
