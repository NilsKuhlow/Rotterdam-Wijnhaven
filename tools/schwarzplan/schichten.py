# -*- coding: utf-8 -*-
"""Die Karte als Schichtstapel, zum An- und Ausschalten.

Bisher lagen die beiden historischen Schichten ueber dem Plan von heute
und wurden eingeblendet. Das ist die falsche Reihenfolge: Die aelteste
Karte gehoert nach ganz unten, und was darueber liegt, blendet man weg,
um sie freizulegen. Genau so liest man ein Palimpsest.

Von unten nach oben:

  Stadt 1940      die aelteste Karte, zuunterst
  Heute           der Schwarzplan, laesst sich wegblenden
  Wiederaufbau    durchsichtig, liegt oben, weil man sie gegen heute
                  liest und nicht gegen das Papier

Jede Schicht hat einen Schalter und einen Regler. Der Regler laeuft in
Schritten von 20 Prozent: Beim stufenlosen Ziehen malte der Browser bei
jedem Zwischenwert eine mehrere Megabyte grosse Ebene neu, was auf dem
Telefon ruckelte und Strom kostete. Sechs Stufen reichen voellig, und
die Bedienung wird dadurch sicherer statt aermer.
"""
import io
import json
import os
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')

# ── 1. Der Stapel im SVG, neu geordnet ─────────────────────────────────
SVG_ALT = """    <g class="plan-layer">
<!-- Der Schwarzplan als Zeichnung, nicht mehr als Bild. Die Datei deckt
     den viewBox-Raum genau ab, darum preserveAspectRatio="none"; verzerrt
     wird dabei nichts, der Ausschnitt ist derselbe wie zuvor.
     Zuerst steht sie als verwiesenes Bild da, damit die Karte ohne Umweg
     erscheint. Gleich danach schreibt planVektorInline() dieselbe Datei in
     das <g> darunter und nimmt das Bild weg: Ob ein Browser ein verwiesenes
     SVG beim Zoomen neu rastert, ist nicht garantiert, inline gilt es. -->
<image class="plan-bild" href="img/schwarzplan.svg" x="0" y="0" width="3010" height="2175" preserveAspectRatio="none"/>
<g id="plan-vektor" aria-hidden="true"></g>
<!-- Die Stadt vor dem 14. Mai 1940. Deckt den viewBox-Raum genau ab, das
     Blatt ist dafuer eingemessen und gedreht worden. href wird erst beim
     ersten Aufdrehen gesetzt: 861 KB soll nicht jeder laden, der die Ebene
     nie anfasst. -->
<image id="ov-1940" x="0" y="0" width="3010" height="2175" opacity="0"
       preserveAspectRatio="none" aria-hidden="true"/>
<!-- Zuschaltbare Kartenebene. Ohne Schluessel bleibt sie leer: kein Bild,
     keine Quelle, keine Lage. Beides setzt _semEbene() aus dem
     verschluesselten Verzeichnis. -->
<image id="ov-ebene" x="0" y="0" opacity="0" preserveAspectRatio="none"
       aria-hidden="true"/>
    <!-- Zuschaltbare Ebenen. Die historische Karte liegt als Bild, das Schema
         von 1946 als eigene Zeichnung im selben Koordinatenraum. -->
    </g>"""

SVG_NEU = """    <!-- Der Schichtstapel, von unten nach oben. Die aelteste Karte liegt
         zuunterst; was darueber liegt, blendet man weg, um sie freizulegen.
         Die Wiederaufbauschicht bleibt oben: Sie ist bis auf die roten
         Bauten durchsichtig und wird gegen heute gelesen, nicht gegen das
         Papier. -->
<!-- Die Stadt vor dem 14. Mai 1940, zuunterst. Deckt den viewBox-Raum genau
     ab, das Blatt ist dafuer eingemessen und gedreht worden. href wird erst
     beim ersten Aufdrehen gesetzt: 861 KB soll nicht jeder laden, der die
     Ebene nie anfasst. -->
<image id="ov-1940" x="0" y="0" width="3010" height="2175" opacity="0"
       preserveAspectRatio="none" aria-hidden="true"/>
    <g class="plan-layer" id="ov-heute">
<!-- Der Schwarzplan als Zeichnung, nicht mehr als Bild. Die Datei deckt
     den viewBox-Raum genau ab, darum preserveAspectRatio="none"; verzerrt
     wird dabei nichts, der Ausschnitt ist derselbe wie zuvor.
     Zuerst steht sie als verwiesenes Bild da, damit die Karte ohne Umweg
     erscheint. Gleich danach schreibt planVektorInline() dieselbe Datei in
     das <g> darunter und nimmt das Bild weg: Ob ein Browser ein verwiesenes
     SVG beim Zoomen neu rastert, ist nicht garantiert, inline gilt es. -->
<image class="plan-bild" href="img/schwarzplan.svg" x="0" y="0" width="3010" height="2175" preserveAspectRatio="none"/>
<g id="plan-vektor" aria-hidden="true"></g>
    </g>
<!-- Zuschaltbare Kartenebene, zuoberst. Ohne Schluessel bleibt sie leer:
     kein Bild, keine Quelle, keine Lage. Beides setzt _semEbene() aus dem
     verschluesselten Verzeichnis. -->
<image id="ov-ebene" x="0" y="0" opacity="0" preserveAspectRatio="none"
       aria-hidden="true"/>"""

# ── 2. Die Bedienung ───────────────────────────────────────────────────
LEISTE_ALT = """    <!-- Regler statt Schalter: zwei Schichten vergleicht man im Uebergang.
         Startwert null, die Karte sieht also zunaechst aus wie immer.
         Der erste ist oeffentlich, das Blatt von 1940 ist gemeinfrei. -->
    <div class="eb-regler" id="eb-regler-1940">
      <label class="eb-mark" id="eb-mark-1940" for="eb-1940"
             data-i18n="eb_1940">Stadt 1940</label>
      <input type="range" id="eb-1940" min="0" max="100" step="1" value="0"
             aria-describedby="eb-quelle" oninput="ebeneDeckung('1940', this.value)"/>
      <output class="eb-wert" id="eb-wert-1940" for="eb-1940">0 %</output>
    </div>
    <div class="eb-regler" id="eb-regler" hidden>
      <label class="eb-mark" id="eb-mark" for="eb-deckung"></label>
      <input type="range" id="eb-deckung" min="0" max="100" step="1" value="0"
             aria-describedby="eb-quelle" oninput="ebeneDeckung('revisie', this.value)"/>
      <output class="eb-wert" id="eb-wert" for="eb-deckung">0 %</output>
    </div>"""

LEISTE_NEU = """    <!-- Die Schichten, in der Reihenfolge des Stapels: oben zuerst, die
         aelteste zuletzt. Jede mit Schalter und Regler; der Regler laeuft
         in Schritten von 20 Prozent, weil das stufenlose Ziehen bei
         mehrere Megabyte grossen Ebenen ruckelte und Strom kostete. -->
    <div class="eb-zeile" id="eb-zeile-revisie" hidden>
      <button class="eb-schalt" type="button" id="eb-an-revisie" role="switch"
              aria-checked="false" onclick="ebeneSchalten('revisie')"></button>
      <input type="range" id="eb-regler-revisie" min="0" max="100" step="20" value="60"
             aria-label="Deckung" aria-describedby="eb-quelle"
             oninput="ebeneDeckung('revisie', this.value)"/>
      <output class="eb-wert" id="eb-zahl-revisie">0 %</output>
    </div>
    <div class="eb-zeile" id="eb-zeile-heute">
      <button class="eb-schalt" type="button" id="eb-an-heute" role="switch"
              aria-checked="true" onclick="ebeneSchalten('heute')"
              data-i18n="eb_heute">Heute</button>
      <input type="range" id="eb-regler-heute" min="0" max="100" step="20" value="100"
             aria-label="Deckung" aria-describedby="eb-quelle"
             oninput="ebeneDeckung('heute', this.value)"/>
      <output class="eb-wert" id="eb-zahl-heute">100 %</output>
    </div>
    <div class="eb-zeile" id="eb-zeile-1940">
      <button class="eb-schalt" type="button" id="eb-an-1940" role="switch"
              aria-checked="false" onclick="ebeneSchalten('1940')"
              data-i18n="eb_1940">Stadt 1940</button>
      <input type="range" id="eb-regler-1940" min="0" max="100" step="20" value="60"
             aria-label="Deckung" aria-describedby="eb-quelle"
             oninput="ebeneDeckung('1940', this.value)"/>
      <output class="eb-wert" id="eb-zahl-1940">0 %</output>
    </div>"""

# ── 3. CSS ─────────────────────────────────────────────────────────────
CSS_ALT = """.eb-regler {
  display:flex; align-items:center; gap:.5rem;
  background:var(--paper-0); border:1px solid var(--ink-1);
  padding:.35rem .6rem;
}
.eb-regler[hidden] { display:none; }
.eb-mark, .eb-wert {
  font-family:var(--font-mono); font-size:.56rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-1); white-space:nowrap;
}
.eb-wert { min-width:2.6em; text-align:right; color:var(--ink-3); }
.eb-regler input[type="range"] {"""
CSS_NEU = """/* Eine Zeile je Schicht: Schalter, Regler, Wert. Der Schalter traegt den
   Namen und zeigt seinen Zustand als Flaeche, wie die Kapitelknoepfe. */
.eb-zeile {
  display:flex; align-items:center; gap:.45rem;
  background:var(--paper-0); border:1px solid var(--ink-1);
  padding:.3rem .45rem;
}
.eb-zeile[hidden] { display:none; }
.eb-schalt {
  font-family:var(--font-mono); font-size:.54rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-1); white-space:nowrap;
  background:var(--paper-0); border:1px solid var(--ink-1); border-radius:0;
  padding:.3rem .5rem; cursor:pointer; min-width:7.4em; text-align:left;
  -webkit-tap-highlight-color:transparent; touch-action:manipulation;
  transition:background .18s;
}
.eb-schalt[aria-checked="true"] { background:var(--accent); font-weight:600; }
.eb-schalt:hover, .eb-schalt:focus-visible { outline:none; box-shadow:inset 0 0 0 2px var(--ink-1); }
.eb-wert {
  font-family:var(--font-mono); font-size:.54rem; letter-spacing:var(--tr-label);
  min-width:3.1em; text-align:right; color:var(--ink-3);
}
.eb-zeile input[type="range"] {"""

CSS_ALT2 = """.eb-regler input[type="range"]::-webkit-slider-thumb {"""
CSS_NEU2 = """.eb-zeile input[type="range"]::-webkit-slider-thumb {"""
CSS_ALT3 = """.eb-regler input[type="range"]::-moz-range-thumb {"""
CSS_NEU3 = """.eb-zeile input[type="range"]::-moz-range-thumb {"""
CSS_ALT4 = """.eb-regler input[type="range"]:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }"""
CSS_NEU4 = """.eb-zeile input[type="range"]:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
.eb-zeile input[type="range"][disabled] { opacity:.3; cursor:default; }"""

# ── 4. Das Modell ──────────────────────────────────────────────────────
JS_ALT_ANFANG = """var EBENEN = {
  '1940':    { bild:'ov-1940',  regler:'eb-1940',     wert:'eb-wert-1940',
               quelle:'img/plan-1940-ebene.webp' },
  'revisie': { bild:'ov-ebene', regler:'eb-deckung',  wert:'eb-wert' }
};"""
JS_NEU_ANFANG = """var EBENEN = {
  'heute':   { knoten:'ov-heute', an:true,  wert:100 },
  '1940':    { knoten:'ov-1940',  an:false, wert:60,
               quelle:'img/plan-1940-ebene.webp' },
  'revisie': { knoten:'ov-ebene', an:false, wert:60, gesperrt:true }
};
var EBENEN_FOLGE = ['revisie', 'heute', '1940'];
var EBENE_VORGABE = 60;        /* womit eine Schicht aufgeht, die bei 0 stand */"""

JS_ALT = """/* Deckung setzen. Auch bei Aufrufen aus dem Code soll der Griff
   mitwandern, sonst zeigt er etwas anderes an als die Karte. */
function ebeneDeckung(welche, v){
  var e = EBENEN[welche];
  if (!e) return;
  var p = Math.max(0, Math.min(100, parseInt(v, 10) || 0));
  var img = document.getElementById(e.bild);
  if (img){
    /* Erst beim ersten Aufdrehen laden. Wer die Ebene nie anfasst, soll
       die 861 KB auch nicht bezahlen. */
    if (p > 0 && e.quelle && !img.getAttribute('href'))
      img.setAttribute('href', e.quelle);
    img.setAttribute('opacity', (p / 100).toFixed(3));
  }
  var w = document.getElementById(e.wert);
  if (w) w.textContent = p + ' %';
  var r = document.getElementById(e.regler);
  if (r && String(p) !== r.value) r.value = String(p);
  _ebeneQuelle();
}"""

JS_NEU = """/* Eine Schicht so zeichnen, wie ihr Zustand es sagt. Ausgeschaltet ist
   sie durchsichtig, bleibt aber mit ihrem Wert stehen, damit das
   Wiedereinschalten dort weitermacht, wo man aufgehoert hat. */
function _ebeneAnwenden(welche){
  var e = EBENEN[welche];
  if (!e) return;
  var sicht = e.an ? e.wert : 0;
  var k = document.getElementById(e.knoten);
  if (k){
    /* Erst beim ersten Aufdrehen laden. Wer die Ebene nie anfasst, soll
       die 861 KB auch nicht bezahlen. */
    if (sicht > 0 && e.quelle && !k.getAttribute('href'))
      k.setAttribute('href', e.quelle);
    k.setAttribute('opacity', (sicht / 100).toFixed(2));
  }
  var s = document.getElementById('eb-an-' + welche);
  if (s) s.setAttribute('aria-checked', e.an ? 'true' : 'false');
  var r = document.getElementById('eb-regler-' + welche);
  if (r){
    if (String(e.wert) !== r.value) r.value = String(e.wert);
    r.disabled = !e.an;
  }
  var z = document.getElementById('eb-zahl-' + welche);
  if (z) z.textContent = sicht + ' %';
}

/* Schalter. Eine Schicht, die bei null stand, geht mit einem sinnvollen
   Wert auf; sonst waere der Schalter ohne Wirkung. */
function ebeneSchalten(welche){
  var e = EBENEN[welche];
  if (!e) return;
  e.an = !e.an;
  if (e.an && e.wert === 0) e.wert = EBENE_VORGABE;
  _ebeneAnwenden(welche);
  _ebeneQuelle();
}

/* Regler. Auf null gezogen heisst aus; das ist dieselbe Aussage und
   soll nicht zwei verschiedene Zustaende ergeben. */
function ebeneDeckung(welche, v){
  var e = EBENEN[welche];
  if (!e) return;
  e.wert = Math.max(0, Math.min(100, parseInt(v, 10) || 0));
  e.an = e.wert > 0;
  _ebeneAnwenden(welche);
  _ebeneQuelle();
}

function _ebenenAlleAnwenden(){
  for (var k in EBENEN) _ebeneAnwenden(k);
}"""

# ── 5. Quellenzeile auf das neue Modell ────────────────────────────────
QUELLE_ALT = """  var t = [];
  var r1 = document.getElementById('eb-1940');
  if (r1 && parseInt(r1.value, 10) > 0) t.push(uiT('eb_1940_quelle'));
  var r2 = document.getElementById('eb-deckung');
  if (r2 && parseInt(r2.value, 10) > 0 && SEMINAR.auf && SEMINAR.inhalt){"""
QUELLE_NEU = """  var t = [];
  if (EBENEN['1940'].an && EBENEN['1940'].wert > 0) t.push(uiT('eb_1940_quelle'));
  if (EBENEN['revisie'].an && EBENEN['revisie'].wert > 0
      && SEMINAR.auf && SEMINAR.inhalt){"""

# ── 6. _semEbene auf die neue Zeile ────────────────────────────────────
SEM_ALT = """function _semEbene(){
  var img = document.getElementById('ov-ebene');
  var box = document.getElementById('eb-regler');"""
SEM_NEU = """function _semEbene(){
  var img = document.getElementById('ov-ebene');
  var box = document.getElementById('eb-zeile-revisie');"""

SEM_ALT2 = """  var t = e[currentLang] || e.de || {};
  var m = document.getElementById('eb-mark');
  if (m) m.textContent = t.name || '';
  box.hidden = false;
  /* Stand des Reglers wiederherstellen, falls die Sprache gewechselt hat. */
  var r = document.getElementById('eb-deckung');
  ebeneDeckung('revisie', r ? r.value : 0);"""
SEM_NEU2 = """  var t = e[currentLang] || e.de || {};
  var s = document.getElementById('eb-an-revisie');
  if (s) s.textContent = t.name || '';
  box.hidden = false;
  _ebeneAnwenden('revisie');"""

SEM_ALT3 = """  if (!e){
    img.removeAttribute('href');
    img.setAttribute('opacity', '0');
    box.hidden = true;
    _ebeneQuelle();
    return;
  }"""
SEM_NEU3 = """  if (!e){
    img.removeAttribute('href');
    EBENEN['revisie'].an = false;
    _ebeneAnwenden('revisie');
    box.hidden = true;
    _ebeneQuelle();
    return;
  }"""

# ── 7. Beim Sperren ────────────────────────────────────────────────────
SPERR_ALT = """  var r = document.getElementById('eb-deckung');
  if (r) r.value = '0';
  _semKnopf();"""
SPERR_NEU = """  EBENEN['revisie'].an = false;
  _semKnopf();"""

UI_NEU = [{"key": "eb_heute", "de": "Heute", "nl": "Vandaag", "en": "Today"}]


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(SVG_ALT, SVG_NEU, 'Stapel neu geordnet, 1940 zuunterst')
    tausch(LEISTE_ALT, LEISTE_NEU, 'drei Zeilen mit Schalter und Regler')
    tausch(CSS_ALT, CSS_NEU, 'CSS fuer die Zeilen')
    tausch(CSS_ALT2, CSS_NEU2, 'CSS Griff (WebKit)')
    tausch(CSS_ALT3, CSS_NEU3, 'CSS Griff (Gecko)')
    tausch(CSS_ALT4, CSS_NEU4, 'CSS Fokus und gesperrter Regler')
    tausch(JS_ALT_ANFANG, JS_NEU_ANFANG, 'Modell der Schichten')
    tausch(JS_ALT, JS_NEU, 'Schalten und Regeln')
    tausch(QUELLE_ALT, QUELLE_NEU, 'Quellenzeile am Modell')
    tausch(SEM_ALT, SEM_NEU, '_semEbene: neue Zeile')
    tausch(SEM_ALT3, SEM_NEU3, '_semEbene: zugesperrt abraeumen')
    tausch(SEM_ALT2, SEM_NEU2, '_semEbene: Name auf den Schalter')
    tausch(SPERR_ALT, SPERR_NEU, 'Sperren schaltet die Schicht aus')

    marke = '"ui":['
    i = s.find(marke)
    if i < 0:
        sys.exit('FEHLER: I18N.ui nicht gefunden')
    s = s[:i + len(marke)] + ''.join(
        json.dumps(u, ensure_ascii=False) + ',' for u in UI_NEU) + s[i + len(marke):]
    print('OK  Oberflaechentext fuer Heute')

    # Beim Erscheinen der Karte den Stapel einmal anwenden
    alt = """  var zoom = document.getElementById('zoom-stapel');
  if (zoom) zoom.classList.toggle('show', !!an);"""
    neu = """  var zoom = document.getElementById('zoom-stapel');
  if (zoom) zoom.classList.toggle('show', !!an);
  if (an && typeof _ebenenAlleAnwenden === 'function') _ebenenAlleAnwenden();"""
    tausch(alt, neu, 'Stapel beim Erscheinen der Karte anwenden')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
