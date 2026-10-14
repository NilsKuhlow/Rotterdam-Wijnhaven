# -*- coding: utf-8 -*-
"""Die Marken sollen beim Hineinzoomen nicht mitwachsen.

Mit dem Zoom faellt auf, was vorher nicht auffallen konnte: Punkte,
Ringe und Beschriftungen liegen im Koordinatenraum des Plans. Wer naeher
herangeht, vergroessert sie mit. Bei vierfacher Vergroesserung deckt
"05 Red Apple" das halbe Bild zu.

Groessen werden deshalb gegengerechnet, Strichstaerken dagegen nicht:
fuer die genuegt vector-effect, das haelt sie ohnehin in Bildpunkten
fest und laesst die Zustaende fuer Zeiger und aktive Station in Ruhe.

Angestossen wird das von einem Beobachter auf der viewBox. Der fasst
alle Wege zusammen, auf denen sie gesetzt wird: Knopf, Geste, Schwung,
Sprung zur Station und die weichen Ueberblendungen. Ein Aufruf an jeder
einzelnen Stelle waere einer zu wenig gewesen.
"""
import io
import os
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')

# ── Strichstaerken in Bildpunkten festhalten ────────────────────────────
ALT_CSS = """.route-trail { fill:none; stroke:var(--ink-1); stroke-width:3; stroke-linecap:round; stroke-linejoin:round; opacity:.92; }
.stop-ring   { fill:none; stroke:var(--ink-1); stroke-width:1; opacity:.16; }"""
NEU_CSS = """/* vector-effect haelt die Strichstaerke in Bildpunkten fest. Ohne das
   wuerde die Route beim Hineinzoomen zum Balken. Groessen (r, font-size)
   kann es nicht halten, die rechnet _markenMass() gegen. */
.route-trail { fill:none; stroke:var(--ink-1); stroke-width:3; stroke-linecap:round; stroke-linejoin:round; opacity:.92;
               vector-effect:non-scaling-stroke; }
.stop-ring   { fill:none; stroke:var(--ink-1); stroke-width:1; opacity:.16; vector-effect:non-scaling-stroke; }"""

ALT_DOT = """.stop-dot    { fill:var(--stop-c, var(--ink-1)); stroke:var(--ink-1); stroke-width:1.4; cursor:pointer; }"""
NEU_DOT = """.stop-dot    { fill:var(--stop-c, var(--ink-1)); stroke:var(--ink-1); stroke-width:1.4; cursor:pointer;
               vector-effect:non-scaling-stroke; }"""

ALT_FUTURE = """.route-future{ fill:none; stroke:var(--ink-1); stroke-width:1.4; stroke-dasharray:1 7; stroke-linecap:round; opacity:.30; }"""
NEU_FUTURE = """.route-future{ fill:none; stroke:var(--ink-1); stroke-width:1.4; stroke-dasharray:1 7; stroke-linecap:round; opacity:.30;
               vector-effect:non-scaling-stroke; }"""

ALT_GPS = """      <circle id="gps-acc"   cx="0" cy="0" r="24" fill="none" stroke="var(--here)" stroke-opacity=".38" stroke-width="1"/>
      <circle id="gps-halo"  cx="0" cy="0" r="12" fill="var(--here)" fill-opacity=".28"/>
      <circle id="gps-outer" cx="0" cy="0" r="10" fill="var(--paper)" stroke="var(--ink-1)" stroke-width="1"/>
      <circle id="gps-inner" cx="0" cy="0" r="6.5" fill="var(--here)"/>"""
NEU_GPS = """      <circle id="gps-acc"   cx="0" cy="0" r="24" fill="none" stroke="var(--here)" stroke-opacity=".38" stroke-width="1" vector-effect="non-scaling-stroke"/>
      <circle id="gps-halo"  cx="0" cy="0" r="12" fill="var(--here)" fill-opacity=".28"/>
      <circle id="gps-outer" cx="0" cy="0" r="10" fill="var(--paper)" stroke="var(--ink-1)" stroke-width="1" vector-effect="non-scaling-stroke"/>
      <circle id="gps-inner" cx="0" cy="0" r="6.5" fill="var(--here)"/>"""

# ── Die Gegenrechnung ───────────────────────────────────────────────────
ALT_JS = """(function(){
  var wrap = document.getElementById('map-svg-wrap');
  if (!wrap) return;"""

NEU_JS = """/* Die Marken liegen im Koordinatenraum des Plans und wuerden beim
   Hineinzoomen mitwachsen. Hier bekommen sie ihr Mass zurueck: Bezug ist
   die Gesamtansicht, naeher heran werden sie im selben Verhaeltnis
   kleiner gerechnet. Weiter heraus bleiben sie, wie sie sind; sonst
   waeren sie irgendwann nicht mehr zu treffen. */
var MARKEN_MASS = {
  ring: 14, punkt: 9, schrift: 11, kontur: 4, versatzX: 12, versatzY: 4,
  gps: { 'gps-acc': 24, 'gps-halo': 12, 'gps-outer': 10, 'gps-inner': 6.5 }
};

function _markenMass(){
  var svg = _kartenSvg();
  if (!svg || !svg.viewBox || !svg.viewBox.baseVal) return;
  var b = svg.viewBox.baseVal;
  if (!b.width) return;
  var basis = parseFloat(String(MAP_STATIC_VB).split(/\\s+/)[2]) || b.width;
  var m = b.width / basis;
  if (m > 1) m = 1;
  var M = MARKEN_MASS;

  var g = document.getElementById('stop-markers');
  if (g){
    var ringe = g.querySelectorAll('.stop-ring');
    for (var i = 0; i < ringe.length; i++)
      ringe[i].setAttribute('r', (M.ring * m).toFixed(2));
    var punkte = g.querySelectorAll('.stop-dot');
    for (i = 0; i < punkte.length; i++)
      punkte[i].setAttribute('r', (M.punkt * m).toFixed(2));
    /* font-size steht im Stylesheet, eine Praesentationsangabe kaeme
       dagegen nicht an. Also inline. */
    var lbl = g.querySelectorAll('.stop-lbl');
    for (i = 0; i < lbl.length; i++){
      lbl[i].style.fontSize = (M.schrift * m).toFixed(2) + 'px';
      lbl[i].style.strokeWidth = (M.kontur * m).toFixed(2) + 'px';
      if (typeof WAYPOINTS !== 'undefined' && WAYPOINTS[i]){
        lbl[i].setAttribute('x', (WAYPOINTS[i].x + M.versatzX * m).toFixed(2));
        lbl[i].setAttribute('y', (WAYPOINTS[i].y + M.versatzY * m).toFixed(2));
      }
    }
  }
  for (var k in M.gps){
    var e = document.getElementById(k);
    if (e) e.setAttribute('r', (M.gps[k] * m).toFixed(2));
  }
}

(function(){
  var svg = document.getElementById('mapSvg');
  if (!svg || typeof MutationObserver !== 'function') return;
  new MutationObserver(_markenMass)
    .observe(svg, { attributes:true, attributeFilter:['viewBox'] });
  _markenMass();
})();

(function(){
  var wrap = document.getElementById('map-svg-wrap');
  if (!wrap) return;"""


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(ALT_CSS, NEU_CSS, 'Route und Ring halten ihre Strichstaerke')
    tausch(ALT_DOT, NEU_DOT, 'Stationspunkt haelt seine Strichstaerke')
    tausch(ALT_FUTURE, NEU_FUTURE, 'gestrichelter Rest der Route ebenso')
    tausch(ALT_GPS, NEU_GPS, 'eigener Standort ebenso')
    tausch(ALT_JS, NEU_JS, '_markenMass() und der Beobachter')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
