# -*- coding: utf-8 -*-
"""Die Wiederaufbauschicht als Kartenebene, mit Regler.

Ein Regler und kein Schalter, weil man zwei Schichten im Uebergang
vergleicht und nicht im Entweder-oder. Startwert null: Die Karte sieht
zunaechst aus wie immer, die Schicht wird aufgedreht, so weit man sie
braucht.

Ebene und Regler gehoeren dem Seminarbereich. Zugesperrt gibt es beides
nicht, und zwar wirklich nicht: kein Bild ohne Quelle, kein Regler, kein
Hinweis im Quelltext, worum es sich handelt. Die Beschriftung des
Reglers steht im verschluesselten Verzeichnis.

Die Lage kommt ebenfalls von dort, nicht aus dieser Datei. Sie stammt
aus der Einmessung vom 13. Oktober, geprueft mit drei Verfahren:
2,27 m je Bildpunkt, nordgerichtet, Rest rund 10 m, und das ist die
Aufloesung der Vorlage, nicht ein Fehler der Einpassung.
"""
import io
import json
import os
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')

# ── 1. CSS ──────────────────────────────────────────────────────────────
CSS_ANKER = ".zoom-knopf[disabled] { opacity:.3; cursor:default; background:var(--paper-0); }"
CSS_NEU = CSS_ANKER + """

/* Der Regler fuer die Kartenebene. Steht bei den Kapitelknoepfen, in
   derselben Sprache: weiss, Haarlinie, keine Rundung. Erscheint nur im
   aufgeschlossenen Zustand, weil die Ebene dem Seminarbereich gehoert. */
.eb-regler {
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
.eb-regler input[type="range"] {
  -webkit-appearance:none; appearance:none; width:7rem; height:1px;
  background:var(--ink-1); border:none; cursor:pointer; margin:0;
}
.eb-regler input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance:none; width:.85rem; height:.85rem; border-radius:0;
  background:var(--accent); border:1px solid var(--ink-1); cursor:pointer;
}
.eb-regler input[type="range"]::-moz-range-thumb {
  width:.85rem; height:.85rem; border-radius:0;
  background:var(--accent); border:1px solid var(--ink-1); cursor:pointer;
}
.eb-regler input[type="range"]:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }"""

# ── 2. Die Ebene in das Karten-SVG ─────────────────────────────────────
SVG_ANKER = """<image class="plan-bild" href="img/schwarzplan.svg" x="0" y="0" width="3010" height="2175" preserveAspectRatio="none"/>
<g id="plan-vektor" aria-hidden="true"></g>"""
SVG_NEU = """<image class="plan-bild" href="img/schwarzplan.svg" x="0" y="0" width="3010" height="2175" preserveAspectRatio="none"/>
<g id="plan-vektor" aria-hidden="true"></g>
<!-- Zuschaltbare Kartenebene. Ohne Schluessel bleibt sie leer: kein Bild,
     keine Quelle, keine Lage. Beides setzt _semEbene() aus dem
     verschluesselten Verzeichnis. -->
<image id="ov-ebene" x="0" y="0" opacity="0" preserveAspectRatio="none"
       aria-hidden="true"/>"""

# ── 3. Der Regler in die Leiste ────────────────────────────────────────
LEISTE_ANKER = """    <button class="eb-schalter eb-kapitel" type="button" id="eb-plaene"
            hidden onclick="openPlaene()"></button>
  </div>"""
LEISTE_NEU = """    <button class="eb-schalter eb-kapitel" type="button" id="eb-plaene"
            hidden onclick="openPlaene()"></button>
    <!-- Regler statt Schalter: zwei Schichten vergleicht man im Uebergang.
         Startwert null, die Karte sieht also zunaechst aus wie immer. -->
    <div class="eb-regler" id="eb-regler" hidden>
      <label class="eb-mark" id="eb-mark" for="eb-deckung"></label>
      <input type="range" id="eb-deckung" min="0" max="100" step="1" value="0"
             oninput="ebeneDeckung(this.value)"/>
      <output class="eb-wert" id="eb-wert" for="eb-deckung">0 %</output>
    </div>
  </div>"""

# ── 4. JavaScript ──────────────────────────────────────────────────────
JS_ANKER = """function _semKnopf(){
  var b = document.getElementById('eb-plaene');
  if (!b) return;
  if (SEMINAR.auf){
    b.textContent = _semKapitelText().name || '';
    b.hidden = false;
  } else {
    b.textContent = '';
    b.hidden = true;
  }
}"""
JS_NEU = """function _semKnopf(){
  var b = document.getElementById('eb-plaene');
  if (!b) return;
  if (SEMINAR.auf){
    b.textContent = _semKapitelText().name || '';
    b.hidden = false;
  } else {
    b.textContent = '';
    b.hidden = true;
  }
  _semEbene();
}

/* ── Die Kartenebene ──
   Bild, Lage und Beschriftung kommen aus dem verschluesselten
   Verzeichnis. Zugesperrt wird alles wieder abgeraeumt; im Quelltext
   der Seite steht zu keinem Zeitpunkt, was die Ebene zeigt. */
function _semEbene(){
  var img = document.getElementById('ov-ebene');
  var box = document.getElementById('eb-regler');
  if (!img || !box) return;
  var e = null;
  if (SEMINAR.auf && SEMINAR.inhalt){
    e = (SEMINAR.inhalt.bilder || []).filter(function(b){
      return b.ziel === 'ebene' && b.lage;
    })[0] || null;
  }
  if (!e){
    img.removeAttribute('href');
    img.setAttribute('opacity', '0');
    box.hidden = true;
    return;
  }
  var l = e.lage;
  img.setAttribute('href', e.url);
  img.setAttribute('width', l.w);
  img.setAttribute('height', l.h);
  img.setAttribute('transform',
    'translate(' + l.tx + ' ' + l.ty + ') scale(' + l.s + ')');
  var t = e[currentLang] || e.de || {};
  var m = document.getElementById('eb-mark');
  if (m) m.textContent = t.name || '';
  box.hidden = false;
  /* Stand des Reglers wiederherstellen, falls die Sprache gewechselt hat. */
  var r = document.getElementById('eb-deckung');
  ebeneDeckung(r ? r.value : 0);
}

/* Deckung setzen. Auch bei Aufrufen aus dem Code soll der Griff
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

# ── 5. Beim Sperren auch die Ebene abraeumen ───────────────────────────
SPERR_ANKER = """  SEMINAR = { auf:false, schluessel:null, inhalt:null, blobs:[] };
  _semKnopf();"""
SPERR_NEU = """  SEMINAR = { auf:false, schluessel:null, inhalt:null, blobs:[] };
  var r = document.getElementById('eb-deckung');
  if (r) r.value = '0';
  _semKnopf();"""

# ── 6. Quellenzeile der Ebene in das Kapitel ───────────────────────────
KAP_ANKER = """  PLAENE.figures = _semFiguren('plaene');"""
KAP_NEU = """  PLAENE.figures = _semFiguren('plaene');
  /* Die Kartenebene ist keine Abbildung im Kapitel, ihre Herkunft muss
     aber genannt werden. Sie steht deshalb in den Quellen. */
  var eb = (SEMINAR.inhalt && SEMINAR.inhalt.bilder || []).filter(function(b){
    return b.ziel === 'ebene';
  })[0];
  PLAENE.sources = eb
    ? [{ c: ((eb[currentLang] || eb.de || {}).cap || '') + ' ' + (eb.credit || ''),
         u: eb.creditUrl || '' }]
    : [];"""

KAP_ALT_SRC = """  PLAENE.facts = [];
  PLAENE.sources = [];
}"""
KAP_NEU_SRC = """  PLAENE.facts = [];
}"""


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(CSS_ANKER, CSS_NEU, 'CSS fuer den Regler')
    tausch(SVG_ANKER, SVG_NEU, 'Ebene im Karten-SVG')
    tausch(LEISTE_ANKER, LEISTE_NEU, 'Regler in der Leiste')
    tausch(JS_ANKER, JS_NEU, '_semEbene() und ebeneDeckung()')
    tausch(SPERR_ANKER, SPERR_NEU, 'Sperren stellt den Regler zurueck')
    tausch(KAP_ALT_SRC, KAP_NEU_SRC, 'alte leere Quellenliste raus')
    tausch(KAP_ANKER, KAP_NEU, 'Herkunft der Ebene in den Quellen')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
