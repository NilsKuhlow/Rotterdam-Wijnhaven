# -*- coding: utf-8 -*-
"""Die Stadt von 1940 als zweite Kartenebene, oeffentlich.

Damit wird aus der Karte ein Palimpsest: unten der Schwarzplan von
heute, darueber die Stadt vor dem 14. Mai 1940, darueber, wer den
Schluessel hat, die vom Basisplan ausgefuehrten Bauten. Drei Schichten,
zwei Regler, und dazwischen liegt die ganze Geschichte des Ortes.

Das Blatt ist gemeinfrei, vom Stadsarchief Rotterdam ausdruecklich
freigegeben. Diese Ebene braucht also kein Schloss.

Die Einmessung hat sieben Anlaeufe gekostet, und der Grund war eine
falsche Annahme: Das Blatt bei Wikimedia entspricht 200 dpi und nicht
300, bei 1:10.000 also 1,270 m je Bildpunkt statt 0,847. Alle Suchen
lagen damit um den Faktor 1,5 daneben. Mit dem richtigen Wert rastet es
sofort ein, Jaccard der Wasserflaechen 0,692 mit sauberem Anstieg und
Abfall zu beiden Seiten.

Geladen wird erst beim ersten Aufdrehen. 861 KB sollen nicht jeden
kosten, der die Ebene nie anfasst.
"""
import io
import json
import os
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')

# ── 1. Die Ebene in das Karten-SVG, unter die Wiederaufbauschicht ──────
SVG_ANKER = """<!-- Zuschaltbare Kartenebene. Ohne Schluessel bleibt sie leer: kein Bild,
     keine Quelle, keine Lage. Beides setzt _semEbene() aus dem
     verschluesselten Verzeichnis. -->
<image id="ov-ebene" x="0" y="0" opacity="0" preserveAspectRatio="none"
       aria-hidden="true"/>"""
SVG_NEU = """<!-- Die Stadt vor dem 14. Mai 1940. Deckt den viewBox-Raum genau ab, das
     Blatt ist dafuer eingemessen und gedreht worden. href wird erst beim
     ersten Aufdrehen gesetzt: 861 KB soll nicht jeder laden, der die Ebene
     nie anfasst. -->
<image id="ov-1940" x="0" y="0" width="3010" height="2175" opacity="0"
       preserveAspectRatio="none" aria-hidden="true"/>
<!-- Zuschaltbare Kartenebene. Ohne Schluessel bleibt sie leer: kein Bild,
     keine Quelle, keine Lage. Beides setzt _semEbene() aus dem
     verschluesselten Verzeichnis. -->
<image id="ov-ebene" x="0" y="0" opacity="0" preserveAspectRatio="none"
       aria-hidden="true"/>"""

# ── 2. Der zweite Regler, oeffentlich ──────────────────────────────────
LEISTE_ANKER = """    <!-- Regler statt Schalter: zwei Schichten vergleicht man im Uebergang.
         Startwert null, die Karte sieht also zunaechst aus wie immer. -->
    <div class="eb-regler" id="eb-regler" hidden>
      <label class="eb-mark" id="eb-mark" for="eb-deckung"></label>
      <input type="range" id="eb-deckung" min="0" max="100" step="1" value="0"
             oninput="ebeneDeckung(this.value)"/>
      <output class="eb-wert" id="eb-wert" for="eb-deckung">0 %</output>
    </div>"""
LEISTE_NEU = """    <!-- Regler statt Schalter: zwei Schichten vergleicht man im Uebergang.
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
    </div>
    <!-- Herkunft der aufgedrehten Schichten. Steht nur da, solange eine
         zu sehen ist; wer nichts aufdreht, braucht die Zeile nicht. -->
    <p class="eb-quelle" id="eb-quelle" hidden></p>"""

# ── 3. CSS fuer die Quellenzeile ───────────────────────────────────────
CSS_ANKER = """.eb-regler input[type="range"]:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }"""
CSS_NEU = CSS_ANKER + """
/* Die Herkunft der Schichten. Schmal, leise, aber da. */
.eb-quelle {
  flex-basis:100%; margin:0; max-width:46ch;
  font-family:var(--font-mono); font-size:.5rem; line-height:1.7;
  letter-spacing:.06em; color:var(--ink-1);
  background:var(--paper-0); border:1px solid var(--ink-1);
  padding:.35rem .6rem;
}
.eb-quelle[hidden] { display:none; }"""

# ── 4. JavaScript: zwei Ebenen statt einer ─────────────────────────────
JS_ALT = """/* Deckung setzen. Auch bei Aufrufen aus dem Code soll der Griff
   mitwandern, sonst zeigt er etwas anderes an als die Karte. */
function ebeneDeckung(v){
  var p = Math.max(0, Math.min(100, parseInt(v, 10) || 0));
  var img = document.getElementById('ov-ebene');
  if (img) img.setAttribute('opacity', (p / 100).toFixed(3));
  var w = document.getElementById('eb-wert');
  if (w) w.textContent = p + ' %';
  var r = document.getElementById('eb-deckung');
  if (r && String(p) !== r.value) r.value = String(p);
}"""

JS_NEU = """/* ── Die Kartenebenen ──
   Zwei Schichten ueber dem Schwarzplan: die Stadt vor dem 14. Mai 1940,
   oeffentlich, und darueber die vom Basisplan ausgefuehrten Bauten, die
   dem Seminarbereich gehoeren. Aufgedreht statt geschaltet, weil man
   Schichten im Uebergang vergleicht und nicht im Entweder-oder. */
var EBENEN = {
  '1940':    { bild:'ov-1940',  regler:'eb-1940',     wert:'eb-wert-1940',
               quelle:'img/plan-1940-ebene.webp' },
  'revisie': { bild:'ov-ebene', regler:'eb-deckung',  wert:'eb-wert' }
};

/* Deckung setzen. Auch bei Aufrufen aus dem Code soll der Griff
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
}

/* Die Quellenzeile nennt nur, was gerade zu sehen ist. */
function _ebeneQuelle(){
  var z = document.getElementById('eb-quelle');
  if (!z) return;
  var t = [];
  var r1 = document.getElementById('eb-1940');
  if (r1 && parseInt(r1.value, 10) > 0) t.push(uiT('eb_1940_quelle'));
  var r2 = document.getElementById('eb-deckung');
  if (r2 && parseInt(r2.value, 10) > 0 && SEMINAR.auf && SEMINAR.inhalt){
    var e = (SEMINAR.inhalt.bilder || []).filter(function(b){
      return b.ziel === 'ebene';
    })[0];
    if (e) t.push(((e[currentLang] || e.de || {}).cap || '') + ' ' + (e.credit || ''));
  }
  z.textContent = t.join('  ·  ');
  z.hidden = !t.length;
}"""

# ── 5. Aufrufe nachziehen ──────────────────────────────────────────────
RUF_ALT = """  /* Stand des Reglers wiederherstellen, falls die Sprache gewechselt hat. */
  var r = document.getElementById('eb-deckung');
  ebeneDeckung(r ? r.value : 0);"""
RUF_NEU = """  /* Stand des Reglers wiederherstellen, falls die Sprache gewechselt hat. */
  var r = document.getElementById('eb-deckung');
  ebeneDeckung('revisie', r ? r.value : 0);"""

ZU_ALT = """  if (!e){
    img.removeAttribute('href');
    img.setAttribute('opacity', '0');
    box.hidden = true;
    return;
  }"""
ZU_NEU = """  if (!e){
    img.removeAttribute('href');
    img.setAttribute('opacity', '0');
    box.hidden = true;
    _ebeneQuelle();
    return;
  }"""

UI_NEU = [
    {"key": "eb_1940", "de": "Stadt 1940", "nl": "Stad 1940", "en": "City 1940"},
    {"key": "eb_1940_quelle",
     "de": "Stadt 1940: Gemeente Rotterdam en omgeving, 1:10.000, "
           "Gemeentelijke Technische Dienst. Stadsarchief Rotterdam, gemeinfrei. "
           "Eingemessen am Wasser, 1,27 m je Bildpunkt.",
     "nl": "Stad 1940: Gemeente Rotterdam en omgeving, 1:10.000, "
           "Gemeentelijke Technische Dienst. Stadsarchief Rotterdam, publiek domein. "
           "Ingemeten op het water, 1,27 m per beeldpunt.",
     "en": "City 1940: Gemeente Rotterdam en omgeving, 1:10,000, municipal technical "
           "service. Stadsarchief Rotterdam, public domain. Fitted on the water, "
           "1.27 m per pixel."},
]


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(SVG_ANKER, SVG_NEU, 'Ebene 1940 im Karten-SVG')
    tausch(LEISTE_ANKER, LEISTE_NEU, 'zweiter Regler und Quellenzeile')
    tausch(CSS_ANKER, CSS_NEU, 'CSS fuer die Quellenzeile')
    tausch(JS_ALT, JS_NEU, 'ebeneDeckung() fuer zwei Ebenen')
    tausch(RUF_ALT, RUF_NEU, 'Aufruf aus _semEbene() nachgezogen')
    tausch(ZU_ALT, ZU_NEU, 'Quellenzeile beim Sperren nachziehen')

    marke = '"ui":['
    i = s.find(marke)
    if i < 0:
        sys.exit('FEHLER: I18N.ui nicht gefunden')
    zusatz = ''.join(json.dumps(u, ensure_ascii=False) + ',' for u in UI_NEU)
    s = s[:i + len(marke)] + zusatz + s[i + len(marke):]
    print('OK  %d Oberflaechentexte' % len(UI_NEU))

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
