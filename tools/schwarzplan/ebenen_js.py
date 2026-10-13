# -*- coding: utf-8 -*-
"""Das Verhalten der Ebenen, und die Karte ein Stueck weiter aufziehen.

  ebeneUm()   schaltet eine Ebene ein und die andere aus. Zwei zugleich
              waeren nicht lesbar. Zu jeder Ebene erscheint eine Quellen-
              zeile; bei der historischen Karte nennt sie Herkunft, Lizenz
              und den Umstand, dass sie eingepasst und nicht vermessen ist.

  LUFT        zieht den statischen Ausschnitt um ein Viertel auf. Die Route
              stand bisher bildfuellend im Rahmen; mit mehr Luft sieht man,
              woran sie liegt, was der eigentliche Zweck des groesseren
              Plans war.
"""
import io
import os
import sys

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
P = os.path.join(REPO, 'index.html')

JS = r"""
/* ── Kartenebenen ──
   Zwei zuschaltbare Ebenen ueber dem Schwarzplan: das Schema des Basisplans
   von 1946 als eigene Zeichnung und der Plan von 1913 als gefundene
   historische Karte. Immer nur eine; zwei uebereinander sind nicht lesbar. */
var EBENEN_QUELLE = {
  'ov-1946': {
    de: 'Eigene Zeichnung, schematisch: Achsen, Hofplein, Fenster zum Fluss und das Wijnhavengebiet als Bueroquartier. Kein Abbild des Originalplans.',
    nl: 'Eigen tekening, schematisch: assen, Hofplein, venster naar de rivier en het Wijnhavengebied als kantoorwijk. Geen afbeelding van het originele plan.',
    en: 'Own drawing, schematic: axes, Hofplein, window to the river and the Wijnhaven area as an office quarter. Not a reproduction of the original plan.'
  },
  'ov-hist': {
    de: 'Plan tot verbetering van de verkeerswegen in de binnenstad, 1913, 1:2500. Stadsarchief Rotterdam ueber Wikimedia Commons, gemeinfrei. Ueber zwei Passpunkte eingepasst, nicht vermessen.',
    nl: 'Plan tot verbetering van de verkeerswegen in de binnenstad, 1913, 1:2500. Stadsarchief Rotterdam via Wikimedia Commons, publiek domein. Op twee passpunten ingepast, niet ingemeten.',
    en: 'Plan tot verbetering van de verkeerswegen in de binnenstad, 1913, 1:2500. Stadsarchief Rotterdam via Wikimedia Commons, public domain. Fitted on two control points, not surveyed.'
  }
};
var _ebeneAktiv = null;

function ebeneUm(id){
  var neu = (_ebeneAktiv === id) ? null : id;
  ['ov-1946', 'ov-hist'].forEach(function(k){
    var el = document.getElementById(k);
    if (el) el.hidden = (k !== neu);
    var kn = document.querySelector('.eb-schalter[data-ebene="' + k + '"]');
    if (kn) kn.setAttribute('aria-pressed', String(k === neu));
  });
  _ebeneAktiv = neu;
  _ebeneQuelle();
}

function _ebeneQuelle(){
  var p = document.getElementById('eb-quelle');
  if (!p) return;
  var q = _ebeneAktiv && EBENEN_QUELLE[_ebeneAktiv];
  p.textContent = q ? (q[currentLang] || q.de) : '';
  p.hidden = !q;
}

/* Die Schalter erscheinen mit der Karte, wie die Leiste darueber. */
(function _ebenenZeigen(){
  var box = document.getElementById('ebenen');
  if (!box) return;
  var beob = function(){
    var an = document.getElementById('nav-crumb');
    box.classList.toggle('show', !!(an && an.classList.contains('show')));
  };
  window.addEventListener('scroll', beob, { passive: true });
  beob();
})();
"""


def main():
    s = io.open(P, encoding='utf-8').read()
    log = []

    def tausch(alt, neu, was, mal=1):
        nonlocal s
        if s.count(alt) != mal:
            sys.exit('FEHLER: %d statt %d Treffer: %r' % (s.count(alt), mal, alt[:70]))
        s = s.replace(alt, neu)
        log.append(was)

    # ── JS hinter die Kartenhelfer ──
    anker = '/* ── Kommentar absenden ──'
    tausch(anker, JS.strip() + '\n\n' + anker, 'JS: ebeneUm und Quellenzeile')

    # ── Sprachwechsel zieht die Quellenzeile mit ──
    tausch("  if (typeof _stFormText === 'function') _stFormText();",
           "  if (typeof _stFormText === 'function') _stFormText();\n"
           "  if (typeof _ebeneQuelle === 'function') _ebeneQuelle();",
           'JS: Quellenzeile wechselt mit der Sprache')

    # ── Statischen Ausschnitt aufziehen ──
    tausch("""  var x1 = Math.min.apply(null, xs) - 70, x2 = Math.max.apply(null, xs) + 150;
  var y1 = Math.min.apply(null, ys) - 80, y2 = Math.max.apply(null, ys) + 80;
  MAP_STATIC_VB = _vbFit((x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1);""",
"""  var x1 = Math.min.apply(null, xs) - 70, x2 = Math.max.apply(null, xs) + 150;
  var y1 = Math.min.apply(null, ys) - 80, y2 = Math.max.apply(null, ys) + 80;
  /* Ein Viertel mehr Luft als der blosse Rahmen um die Route. Der groessere
     Plan ist dafuer da, dass man sieht, woran die Route liegt. */
  var LUFT = 1.25;
  MAP_STATIC_VB = _vbFit((x1 + x2) / 2, (y1 + y2) / 2,
                         (x2 - x1) * LUFT, (y2 - y1) * LUFT);""",
           'JS: statischer Ausschnitt mit einem Viertel mehr Luft')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\n'.join('OK  ' + x for x in log))


if __name__ == '__main__':
    main()
