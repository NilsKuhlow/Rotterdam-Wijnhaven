# -*- coding: utf-8 -*-
"""Die Wiederaufbauschicht als Ebene, mit Regler statt Schalter.

Was weicht: die eigenen Skizzen zum Basisplan. Sie waren von Hand aus
Koordinaten gesetzt und blieben schematisch. An ihrer Stelle liegt jetzt
eine Karte, die den Wiederaufbau tatsaechlich verzeichnet.

Was kommt: aus der Revisiekarte der Wiederaufbau von Rotterdam (Frans Blok,
3develop.nl) sind die roten Bauten geloest, alles andere ist durchsichtig.
Die Ebene liegt massstabs- und lagerichtig auf dem Schwarzplan; eingemessen
am Wasser, nordgerichtet, 2,27 m je Bildpunkt, Korrelation 0,44.

Statt eines Schalters ein Regler fuer die Deckung, Startwert 0 Prozent. Die
Ebene liegt also da und wird aufgedreht, so weit man sie braucht; das ist
die einzige Bedienung, mit der sich zwei Schichten wirklich vergleichen
lassen.

Dazu wird der Basisplan vom Seitenabschnitt zum Kapitel: Er oeffnet sich im
selben Fenster wie die sieben Bauten und kostet in der Seite keine Zeile.
"""
import io
import json
import os
import re
import sys

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
P = os.path.join(REPO, 'index.html')
T = json.load(io.open(r'C:\Temp\wij3d\basisplan_texte.json', encoding='utf-8'))
import pickle
R = pickle.load(open(r'C:\Temp\wij3d\revisie_reg.pkl', 'rb'))

KOPFBILD = {'de': 'Die Innenstadt 1950: die ausgeräumte Fläche, auf der der Basisplan baute.',
            'nl': 'De binnenstad in 1950: het geruimde vlak waarop het Basisplan bouwde.',
            'en': 'The inner city in 1950: the cleared ground the Basisplan built on.'}
UNTER = {'de': 'Cornelis van Traa · angenommen 28. Mai 1946',
         'nl': 'Cornelis van Traa · aangenomen 28 mei 1946',
         'en': 'Cornelis van Traa · adopted 28 May 1946'}
KNOPF = {'de': 'Kapitel 1946', 'nl': 'Hoofdstuk 1946', 'en': 'Chapter 1946'}
REGLER = {'de': 'Wiederaufbau', 'nl': 'Wederopbouw', 'en': 'Reconstruction'}
QUELLE_EBENE = {
 'de': 'Rot: was nach 1940 neu gebaut wurde. Aus der Revisiekarte der Wiederaufbau von '
       'Rotterdam, Frans Blok, 3develop.nl, mit freundlicher Genehmigung. Am Wasser '
       'eingemessen, nordgerichtet, 2,27 m je Bildpunkt.',
 'nl': 'Rood: wat na 1940 nieuw werd gebouwd. Uit de Revisiekaart van de Wederopbouw van '
       'Rotterdam, Frans Blok, 3develop.nl, met vriendelijke toestemming. Op het water '
       'ingemeten, noordgericht, 2,27 m per beeldpunt.',
 'en': 'Red: what was newly built after 1940. From the revision map of the reconstruction '
       'of Rotterdam, Frans Blok, 3develop.nl, by kind permission. Fitted on the water, '
       'north-up, 2.27 m per pixel.',
}


def js_str(t):
    return t.replace('\\', '\\\\').replace("'", "\\'")


def main():
    s = io.open(P, encoding='utf-8').read()
    log = []

    # ══ 1. Basisplan: Abschnitt raus, Kapitel rein ═══════════════════════
    a = s.index('<!-- Der Basisplan von 1946')
    b = s.index('<section class="stimmen"')
    s = s[:a] + s[b:]
    log.append('Seitenabschnitt Basisplan entfernt')

    kap = ['/* ── Der Basisplan als Kapitel ──',
           '   Kein Abschnitt in der Seite mehr, sondern ein Eintrag wie die sieben',
           '   Bauten: Er oeffnet sich im selben Fenster und kostet in der Seite keine',
           '   Zeile. Die Texte stehen hier dreisprachig. */',
           'var BASISPLAN_TEXTE = {']
    for sp in ('de', 'nl', 'en'):
        t = T[sp]
        kap.append('  %s: {' % sp)
        kap.append("    name: '%s'," % js_str(t['titel']))
        kap.append("    sub: '%s'," % js_str(UNTER[sp]))
        kap.append("    kopf: '%s'," % js_str(KOPFBILD[sp]))
        kap.append("    bildunter: '%s'," % js_str(t['bildunter']))
        kap.append("    bildquelle: '%s'," % js_str(t['bildquelle']))
        kap.append("    quelle: '%s'," % js_str(t['quelle']))
        kap.append('    paras: [')
        for p in t['absaetze'] + [t['urteil']]:
            kap.append("      '%s'," % js_str(p))
        kap.append('    ]')
        kap.append('  }%s' % ('' if sp == 'en' else ','))
    kap += ['};', '',
            'var BASISPLAN = { slug: "basisplan" };', '',
            'function _basisplanFuellen(){',
            '  var t = BASISPLAN_TEXTE[currentLang] || BASISPLAN_TEXTE.de;',
            '  BASISPLAN.name = t.name;',
            '  BASISPLAN.sub = t.sub;',
            '  BASISPLAN.paras = t.paras.slice();',
            '  BASISPLAN.slides = [{ bg: "url(\'img/wederopbouw-1950.webp\') center/cover no-repeat",',
            '                        cap: t.kopf }];',
            '  BASISPLAN.figures = [{ src: "img/plan-1913.webp", w: 1233, h: 1403,',
            '                         alt: t.bildunter, cap: t.bildunter }];',
            '  BASISPLAN.facts = [];',
            '  BASISPLAN.sources = [{ c: t.bildquelle, u: "" }, { c: t.quelle, u: "" }];',
            '}', '',
            'function openBasisplan(){ _basisplanFuellen(); openModal(-99, BASISPLAN); }', '']
    anker = '/* ── Kartenebenen ──'
    if s.count(anker) != 1:
        sys.exit('FEHLER: Anker Kartenebenen fehlt')
    s = s.replace(anker, '\n'.join(kap) + anker)
    log.append('Kapitel Basisplan als Eintrag')

    alt_h = "    if (typeof BYSLUG!=='undefined' && BYSLUG[h]){ openModal(-99, BYSLUG[h]); return true; }"
    if s.count(alt_h) != 1:
        sys.exit('FEHLER: Hash-Router fehlt')
    s = s.replace(alt_h, "    if (h === 'basisplan'){ openBasisplan(); return true; }\n" + alt_h)
    log.append('Anker #basisplan oeffnet das Kapitel')

    # ══ 2. Die eigenen Skizzen entfernen ═════════════════════════════════
    m = re.search(r'[ \t]*<g id="ov-1946".*?</g>\n', s, re.S)
    if not m:
        sys.exit('FEHLER: Zeichnung ov-1946 fehlt')
    skizze_pos = m.start()
    s = s[:m.start()] + s[m.end():]
    log.append('Zeichnung ov-1946 entfernt')

    a = s.index('/* Die Zeichnung von 1946. Mittel einer Planzeichnung')
    b = s.index('/* ═══════════════════════════════════════════\n   BASISPLAN + FAZIT')
    s = s[:a] + s[b:]
    log.append('CSS der Zeichnung entfernt')

    for muster in (r'function _ebeneRahmen\(id\)\{.*?\n\}\n\n',
                   r'/\* Beim Einschalten auf den Umfang der Zeichnung aufziehen.*?\n'):
        s = re.sub(muster, '', s, flags=re.S)
    s = s.replace('  _ebeneRahmen(neu);\n', '')
    log.append('Aufziehen auf die Zeichnung entfernt')

    # ══ 3. Die neue Ebene in das SVG ═════════════════════════════════════
    bildzeile = [z for z in s.split('\n') if 'class="plan-bild"' in z]
    if len(bildzeile) != 1:
        sys.exit('FEHLER: Kartenbild nicht eindeutig')
    bildzeile = bildzeile[0]
    ebene = (
     '    <!-- Wiederaufbauschicht: die roten Bauten der Revisiekarte, aus ihr\n'
     '         geloest, alles andere durchsichtig. Am Wasser eingemessen,\n'
     '         nordgerichtet, %.3f m je Bildpunkt, Korrelation %.2f. Die Deckung\n'
     '         stellt der Regler unter der Karte, Startwert 0. -->\n'
     '    <image id="ov-revisie" href="img/wiederaufbau.webp" x="0" y="0"\n'
     '           width="%d" height="%d" opacity="0"\n'
     '           transform="translate(%.1f %.1f) scale(%.5f)" aria-hidden="true"/>'
     % (R['m_je_px'], R['ncc'], R['w'], R['h'], R['tx'], R['ty'], R['s']))
    s = s.replace(bildzeile, bildzeile + '\n' + ebene)
    log.append('Ebene ov-revisie im SVG')

    # ══ 4. Regler statt Schalter ═════════════════════════════════════════
    a = s.index('  <div id="ebenen">')
    b = s.index('</div><!-- /map-panel -->')
    leiste = """  <!-- Regler fuer die Wiederaufbauschicht und der Griff zum Kapitel. Ein
       Regler statt eines Schalters, weil sich zwei Schichten nur im
       Uebergang vergleichen lassen. Startwert 0. -->
  <div id="ebenen">
    <div class="eb-regler">
      <label class="eb-mark" for="eb-deckung" id="eb-mark">Wiederaufbau</label>
      <input type="range" id="eb-deckung" min="0" max="100" step="1" value="0"
             aria-describedby="eb-quelle" oninput="deckungSetzen(this.value)"/>
      <output class="eb-wert" id="eb-wert" for="eb-deckung">0 %</output>
    </div>
    <button class="eb-schalter eb-kapitel" type="button" id="eb-kapitel"
            onclick="openBasisplan()">Kapitel 1946</button>
    <p class="eb-quelle" id="eb-quelle"></p>
  </div>
"""
    s = s[:a] + leiste + s[b:]
    log.append('Regler und Kapitelknopf')

    # ══ 5. CSS ═══════════════════════════════════════════════════════════
    a = s.index('#ebenen {')
    b = s.index('/* ═══════════════════════════════════════════\n   BASISPLAN + FAZIT')
    css = """#ebenen {
  position:absolute; left:max(1rem, env(safe-area-inset-left)); bottom:1rem; z-index:7;
  display:flex; gap:.5rem; flex-wrap:wrap; align-items:center;
  max-width:calc(100% - 2rem);
  opacity:0; pointer-events:none; transition:opacity .4s;
}
#ebenen.show { opacity:1; pointer-events:auto; }
.eb-regler {
  display:flex; align-items:center; gap:.55rem;
  background:rgba(255,255,255,.95); border:1px solid var(--ink-1);
  padding:.4rem .7rem;
}
.eb-mark, .eb-wert {
  font-family:var(--font-mono); font-size:.56rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-1); white-space:nowrap;
}
.eb-wert { min-width:4.2ch; text-align:right; font-variant-numeric:tabular-nums; }
/* Der Regler. Eigene Spur und eigener Griff, damit er zum Haus passt:
   rechte Winkel, Haarlinie, Gelb nur fuer den Griff. */
#eb-deckung {
  -webkit-appearance:none; appearance:none; width:min(42vw, 9rem); height:16px;
  background:none; cursor:pointer; margin:0;
}
#eb-deckung::-webkit-slider-runnable-track {
  height:4px; background:var(--paper-3); border:1px solid var(--ink-1);
}
#eb-deckung::-moz-range-track {
  height:4px; background:var(--paper-3); border:1px solid var(--ink-1);
}
#eb-deckung::-webkit-slider-thumb {
  -webkit-appearance:none; width:14px; height:14px; margin-top:-6px;
  background:var(--accent); border:1px solid var(--ink-1); border-radius:0;
}
#eb-deckung::-moz-range-thumb {
  width:14px; height:14px; background:var(--accent);
  border:1px solid var(--ink-1); border-radius:0;
}
#eb-deckung:focus-visible { outline:2px solid var(--ink-1); outline-offset:3px; }
.eb-schalter {
  font-family:var(--font-mono); font-size:.56rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; border-radius:0; padding:.45rem .8rem; cursor:pointer;
  -webkit-tap-highlight-color:transparent; touch-action:manipulation; white-space:nowrap;
}
/* Der Kapitelknopf schaltet nichts, er oeffnet. Deshalb ohne Zustand. */
.eb-kapitel { background:var(--ink-1); color:var(--paper-0); border:1px solid var(--ink-1); }
.eb-kapitel:hover, .eb-kapitel:focus-visible { background:var(--accent); color:var(--ink-1); outline:none; }
.eb-quelle {
  font-family:var(--font-mono); font-size:.5rem; letter-spacing:.06em;
  color:var(--ink-2); background:rgba(255,255,255,.92); padding:.3rem .5rem;
  max-width:28rem; line-height:1.55; text-transform:none; margin:0;
}

"""
    s = s[:a] + css + s[b:]
    log.append('CSS des Reglers')

    # ══ 6. JS ════════════════════════════════════════════════════════════
    a = s.index('/* ── Kartenebenen ──')
    b = s.index('/* ── Kommentar absenden ──')
    js = """/* ── Kartenebene: Wiederaufbau ──
   Die roten Bauten der Revisiekarte liegen als Bild im Koordinatenraum der
   Karte. Geregelt wird nur ihre Deckung; ein Schalter waere hier das
   falsche Werkzeug, weil man die beiden Schichten im Uebergang vergleicht
   und nicht im Entweder-oder. */
var EBENE_QUELLE = %s;
var EBENE_MARKE = %s;

function deckungSetzen(v){
  var p = Math.max(0, Math.min(100, parseInt(v, 10) || 0));
  var el = document.getElementById('ov-revisie');
  if (el) el.setAttribute('opacity', (p / 100).toFixed(3));
  var w = document.getElementById('eb-wert');
  if (w) w.textContent = p + ' %%';
}

function _ebeneTexte(){
  var q = document.getElementById('eb-quelle');
  if (q) q.textContent = EBENE_QUELLE[currentLang] || EBENE_QUELLE.de;
  var m = document.getElementById('eb-mark');
  if (m) m.textContent = EBENE_MARKE[currentLang] || EBENE_MARKE.de;
  var k = document.getElementById('eb-kapitel');
  if (k) k.textContent = (%s)[currentLang] || 'Kapitel 1946';
}

/* Die Leiste erscheint mit der Karte. */
function _ebenenZeigen(an){
  var box = document.getElementById('ebenen');
  if (box) box.classList.toggle('show', !!an);
}

_ebeneTexte();

""" % (json.dumps(QUELLE_EBENE, ensure_ascii=False),
       json.dumps(REGLER, ensure_ascii=False),
       json.dumps(KNOPF, ensure_ascii=False))
    s = s[:a] + js + s[b:]
    log.append('JS: deckungSetzen und Beschriftung')

    s = s.replace("  if (typeof _ebeneQuelle === 'function') _ebeneQuelle();",
                  "  if (typeof _ebeneTexte === 'function') _ebeneTexte();")
    log.append('Sprachwechsel zieht die Beschriftung mit')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\n'.join('OK  ' + x for x in log))
    t = io.open(P, encoding='utf-8').read()
    for w in ('ov-1946', 'ebeneUm', 'eb-legende', 'lg-eintrag', 'ov-band', 'ov-brand'):
        if w in t:
            print('  Rueckstand: %s (%d)' % (w, t.count(w)))


if __name__ == '__main__':
    main()
