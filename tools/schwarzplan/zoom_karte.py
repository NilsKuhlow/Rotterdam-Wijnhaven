# -*- coding: utf-8 -*-
"""Die Karte lässt sich jetzt vergroessern und verkleinern.

Bisher ging das nur im Smart-Track, also mit eingeschalteter Ortung,
ueber eine Vollbildebene mit Fingergesten. Im normalen Durchblaettern
stand die Karte fest. Seit sie eine Zeichnung ist und nicht mehr ein
Bild, lohnt sich das Hineingehen aber erst richtig: scharf auf jeder
Stufe.

Nebenbei faellt ein alter Fehler auf. Die Gestenebene rechnete noch mit
einem Plan von 1000 x 750 Einheiten, dem Zuschnitt von vor dem Wechsel
auf die weite Karte. Der Plan ist seit September 3010 x 2175 gross. Das
Schieben war dadurch auf das linke obere Neuntel eingesperrt, und
MAX_VB_W von 900 liess ein Herauszoomen auf die ganze Karte gar nicht
zu. Beides wird hier mitgerichtet.

Die Gesten sind bewusst nur solche, die dem Blaettern nicht in die Quere
kommen: zwei Finger auf der Karte, am Rechner das Rad mit Strg oder
Befehlstaste und das Ziehen mit der Maus. Ein Finger bleibt dem Scrollen
vorbehalten; sonst sperrt sich die Seite selbst ein, weil die Karte das
ganze Fenster fuellt.
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
CSS_ANKER = "#ebenen.show { opacity:1; pointer-events:auto; }"
CSS_NEU = """#ebenen.show { opacity:1; pointer-events:auto; }

/* Zoom. Die Karte ist eine Zeichnung und bleibt auf jeder Stufe scharf,
   also darf man auch wirklich hineingehen. Die Knoepfe stehen rechts,
   gegenueber den Kapiteln, und erscheinen mit der Karte. Quadratisch,
   weiss, eine Haarlinie Rand: dieselbe Sprache wie die Kapitelknoepfe,
   nur ohne Wort. Die Raender liegen auf Stoss, darum der negative
   Abstand. */
#zoom-stapel {
  position:absolute; right:max(1rem, env(safe-area-inset-right)); bottom:1rem; z-index:7;
  display:flex; flex-direction:column; align-items:flex-end;
  opacity:0; pointer-events:none; transition:opacity .4s;
}
#zoom-stapel.show { opacity:1; pointer-events:auto; }
.zoom-knopf {
  width:2.2rem; height:2.2rem; margin-bottom:-1px;
  display:flex; align-items:center; justify-content:center;
  background:var(--paper-0); color:var(--ink-1);
  border:1px solid var(--ink-1); border-radius:0;
  font-family:var(--font-mono); font-size:.95rem; font-weight:500; line-height:1;
  cursor:pointer; -webkit-tap-highlight-color:transparent;
  touch-action:manipulation; transition:background .2s, opacity .2s;
}
.zoom-knopf:last-child { margin-bottom:0; font-size:.5rem; letter-spacing:var(--tr-label); }
.zoom-knopf:hover, .zoom-knopf:focus-visible { background:var(--accent); outline:none; }
.zoom-knopf[disabled] { opacity:.3; cursor:default; background:var(--paper-0); }

/* Ein Finger blaettert die Seite, zwei Finger bedienen die Karte. Darum
   pan-y und nicht none: Sonst sperrt sich die Seite selbst ein, weil die
   Karte das ganze Fenster fuellt. */
#map-svg-wrap { touch-action:pan-y; user-select:none; -webkit-user-select:none; }"""

# ── 2. Markup ───────────────────────────────────────────────────────────
MARKUP_ANKER = """            onclick="openBasisplan()">Basisplan 1946</button>
  </div>"""
MARKUP_NEU = """            onclick="openBasisplan()">Basisplan 1946</button>
  </div>
  <!-- Zoom. Drei Knoepfe, weil Gesten allein zu viel voraussetzen: Plus,
       Minus und zurueck auf die ganze Karte. -->
  <div id="zoom-stapel">
    <button class="zoom-knopf" type="button" id="zoom-rein" aria-hidden="false"
            data-i18n-aria="zoom_in" aria-label="Karte vergrößern"
            onclick="kartenZoom(0.625)">+</button>
    <button class="zoom-knopf" type="button" id="zoom-raus"
            data-i18n-aria="zoom_out" aria-label="Karte verkleinern"
            onclick="kartenZoom(1.6)">&#8722;</button>
    <button class="zoom-knopf" type="button" id="zoom-ganz"
            data-i18n-aria="zoom_all" aria-label="Ganze Karte zeigen"
            onclick="kartenGanz()">GANZ</button>
  </div>"""

# ── 3. Die alten Masse in der Gestenebene richten ───────────────────────
ALT_MASSE = """  var CANVAS_W = 1000, CANVAS_H = 750;
  var MIN_VB_W = 80,   MAX_VB_W = 900;"""
NEU_MASSE = """  /* Der Plan, nicht ein alter Zuschnitt. Hier standen bis Oktober 2026
     noch 1000 x 750 und ein MAX_VB_W von 900, die Masse der engen Karte
     von davor. Das Schieben war dadurch auf das linke obere Neuntel
     eingesperrt und ein Herauszoomen auf die ganze Karte unmoeglich. */
  var CANVAS_W = MAP_VW, CANVAS_H = MAP_VH;
  var MIN_VB_W = KARTE_MIN_VB;"""

ALT_APPLY = """  function applyVB(x, y, w, h){
    var aspect = _vb0 ? _vb0.h / _vb0.w : (CANVAS_H / CANVAS_W);
    w = clamp(w, MIN_VB_W, MAX_VB_W);
    h = clamp(h, MIN_VB_W * aspect, MAX_VB_W * aspect);
    x = clamp(x, 0, Math.max(0, CANVAS_W - w));
    y = clamp(y, 0, Math.max(0, CANVAS_H - h));
    svg.setAttribute('viewBox',
      x.toFixed(2)+' '+y.toFixed(2)+' '+w.toFixed(2)+' '+h.toFixed(2));
    return { x:x, y:y, w:w, h:h };
  }"""
NEU_APPLY = """  function applyVB(x, y, w, h){
    var r = kartenVBSetzen(x, y, w, _vb0 ? _vb0.h / _vb0.w : (CANVAS_H / CANVAS_W));
    return r || { x:x, y:y, w:w, h:h };
  }"""

# ── 4. Das neue Stueck JavaScript ───────────────────────────────────────
JS_ANKER = """/* ── stopMapInertia: von resetMapView() gebraucht, um Schwung zu stoppen ── */
var stopMapInertia = function(){};"""

JS_NEU = """/* ── stopMapInertia: von resetMapView() gebraucht, um Schwung zu stoppen ── */
var stopMapInertia = function(){};

/* ═══════════════════════════════════════════════════════════════
   KARTE VERGROESSERN UND VERKLEINERN

   Die Grundkarte ist seit Oktober 2026 eine Zeichnung und kein Bild
   mehr; sie bleibt auf jeder Stufe scharf, also lohnt das Hineingehen.
   Bedient wird mit drei Knoepfen, und zusaetzlich mit Gesten, aber nur
   mit solchen, die dem Blaettern nicht in die Quere kommen:

     zwei Finger auf der Karte   Groesse und Lage zugleich
     Rad mit Strg oder Befehl    Groesse, am Zeiger verankert
     Ziehen mit der Maus         Lage, sobald hineingezoomt ist
     Doppelklick                 eine Stufe naeher

   Ein Finger bleibt dem Scrollen vorbehalten. Die Karte fuellt das
   ganze Fenster; wer ihr den einen Finger nimmt, sperrt die Seite ein.
   ═══════════════════════════════════════════════════════════════ */
var KARTE_MIN_VB = 60;          /* engste Stufe: 60 Einheiten = 78 m Bildbreite */

function _kartenSvg(){ return document.getElementById('mapSvg'); }

function _kartenVB(){
  var s = _kartenSvg();
  if (!s) return null;
  var b = s.viewBox.baseVal;
  return { x:b.x, y:b.y, w:b.width, h:b.height };
}

/* Die groesste sinnvolle Breite: mehr als den Plan gibt es nicht, und
   hoeher als der Plan darf die viewBox auch nicht werden, sonst stuende
   sie teilweise im Leeren. */
function _kartenMaxVB(v){
  return Math.min(MAP_VW, MAP_VH / v);
}

/* Eine viewBox setzen, die im Plan bleibt. Das Seitenverhaeltnis des
   Kartenfensters wird nie verlassen: preserveAspectRatio="slice" wuerde
   sonst am Rand beschneiden und Stationen verschwinden lassen. */
function kartenVBSetzen(x, y, w, v){
  var svg = _kartenSvg();
  if (!svg) return null;
  var jetzt = _kartenVB();
  if (!v) v = jetzt ? jetzt.h / jetzt.w : (MAP_VH / MAP_VW);
  var wMax = _kartenMaxVB(v);
  w = Math.max(KARTE_MIN_VB, Math.min(w, wMax));
  var h = w * v;
  x = Math.max(0, Math.min(x, MAP_VW - w));
  y = Math.max(0, Math.min(y, MAP_VH - h));
  svg.setAttribute('viewBox',
    x.toFixed(2) + ' ' + y.toFixed(2) + ' ' + w.toFixed(2) + ' ' + h.toFixed(2));
  _zoomKnoepfeStand(w, wMax);
  return { x:x, y:y, w:w, h:h };
}

/* Die Knoepfe sagen, wo die Grenze ist, statt sie nur stumm zu halten. */
function _zoomKnoepfeStand(w, wMax){
  var rein = document.getElementById('zoom-rein');
  var raus = document.getElementById('zoom-raus');
  if (rein) rein.disabled = w <= KARTE_MIN_VB + 0.5;
  if (raus) raus.disabled = w >= wMax - 0.5;
}

/* Um einen Punkt herum zoomen. Ohne Punkt um die Bildmitte. Der Punkt
   unter dem Zeiger bleibt dabei stehen, das ist die ganze Rechnung. */
function kartenZoom(faktor, px, py){
  var svg = _kartenSvg();
  var vb = _kartenVB();
  if (!svg || !vb) return;
  if (typeof cancelAnimVB === 'function') cancelAnimVB();
  if (typeof stopMapInertia === 'function') stopMapInertia();
  var fx = 0.5, fy = 0.5;
  if (px !== undefined && py !== undefined){
    var r = svg.getBoundingClientRect();
    fx = Math.max(0, Math.min(1, (px - r.left) / r.width));
    fy = Math.max(0, Math.min(1, (py - r.top) / r.height));
  }
  var v = vb.h / vb.w;
  var ax = vb.x + fx * vb.w, ay = vb.y + fy * vb.h;
  var wNeu = vb.w * faktor;
  kartenVBSetzen(ax - fx * wNeu, ay - fy * wNeu * v, wNeu, v);
}

/* Zurueck auf die Gesamtansicht, die _computeStaticVB() errechnet hat. */
function kartenGanz(){
  if (typeof stopMapInertia === 'function') stopMapInertia();
  if (typeof applyStaticVB === 'function') applyStaticVB(true);
  setTimeout(function(){
    var vb = _kartenVB();
    if (vb) _zoomKnoepfeStand(vb.w, _kartenMaxVB(vb.h / vb.w));
  }, 600);
}

(function(){
  var wrap = document.getElementById('map-svg-wrap');
  if (!wrap) return;

  /* ── Rad: nur mit Strg oder Befehlstaste, und das ist auch die Geste,
        die ein Mausfeld beim Zusammenziehen schickt. Das blosse Rad
        bleibt dem Blaettern. ── */
  wrap.addEventListener('wheel', function(e){
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    var f = Math.exp(Math.max(-60, Math.min(60, e.deltaY)) * 0.01);
    kartenZoom(f, e.clientX, e.clientY);
  }, { passive:false });

  /* ── Doppelklick: eine Stufe naeher, am Zeiger ── */
  wrap.addEventListener('dblclick', function(e){
    kartenZoom(0.55, e.clientX, e.clientY);
  });

  /* ── Ziehen mit der Maus. Erst ab vier Bildpunkten gilt es als Ziehen,
        damit ein Klick auf eine Station ein Klick bleibt. ── */
  var zieht = false, gezogen = false, zx = 0, zy = 0, zvb = null;
  wrap.addEventListener('pointerdown', function(e){
    if (e.pointerType === 'touch') return;      /* Finger macht der Block unten */
    zvb = _kartenVB();
    if (!zvb) return;
    zieht = true; gezogen = false; zx = e.clientX; zy = e.clientY;
  });
  wrap.addEventListener('pointermove', function(e){
    if (!zieht || !zvb) return;
    var dx = e.clientX - zx, dy = e.clientY - zy;
    if (!gezogen){
      if (dx * dx + dy * dy < 16) return;
      gezogen = true;
      wrap.style.cursor = 'grabbing';
      if (typeof cancelAnimVB === 'function') cancelAnimVB();
    }
    e.preventDefault();
    var r = wrap.getBoundingClientRect();
    kartenVBSetzen(zvb.x - dx * (zvb.w / r.width),
                   zvb.y - dy * (zvb.h / r.height),
                   zvb.w, zvb.h / zvb.w);
  });
  function zugEnde(){
    zieht = false; zvb = null;
    wrap.style.cursor = '';
    if (gezogen) setTimeout(function(){ gezogen = false; }, 0);
  }
  wrap.addEventListener('pointerup', zugEnde);
  wrap.addEventListener('pointercancel', zugEnde);
  wrap.addEventListener('pointerleave', zugEnde);
  /* Ein Zug darf nicht als Klick auf eine Station enden. */
  wrap.addEventListener('click', function(e){
    if (gezogen){ e.stopPropagation(); e.preventDefault(); }
  }, true);

  /* ── Zwei Finger: Groesse und Lage zugleich. Der Punkt zwischen den
        Fingern bleibt stehen. Ein Finger wird nicht angefasst, der
        blaettert weiter die Seite. ── */
  var g0 = null;
  function abstand(a, b){
    var dx = a.clientX - b.clientX, dy = a.clientY - b.clientY;
    return Math.sqrt(dx * dx + dy * dy) || 1;
  }
  wrap.addEventListener('touchstart', function(e){
    if (e.touches.length < 2){ g0 = null; return; }
    var vb = _kartenVB();
    if (!vb) return;
    e.preventDefault();
    if (typeof cancelAnimVB === 'function') cancelAnimVB();
    if (typeof stopMapInertia === 'function') stopMapInertia();
    var r = wrap.getBoundingClientRect();
    var mx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
    var my = (e.touches[0].clientY + e.touches[1].clientY) / 2;
    g0 = { vb:vb, d:abstand(e.touches[0], e.touches[1]),
           ax: vb.x + (mx - r.left) / r.width * vb.w,
           ay: vb.y + (my - r.top) / r.height * vb.h };
  }, { passive:false });

  wrap.addEventListener('touchmove', function(e){
    if (!g0 || e.touches.length < 2) return;
    e.preventDefault();
    var r = wrap.getBoundingClientRect();
    var f = g0.d / abstand(e.touches[0], e.touches[1]);
    var wNeu = g0.vb.w * f;
    var v = g0.vb.h / g0.vb.w;
    var mx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
    var my = (e.touches[0].clientY + e.touches[1].clientY) / 2;
    var fx = (mx - r.left) / r.width, fy = (my - r.top) / r.height;
    kartenVBSetzen(g0.ax - fx * wNeu, g0.ay - fy * wNeu * v, wNeu, v);
  }, { passive:false });

  wrap.addEventListener('touchend', function(e){
    if (e.touches.length < 2) g0 = null;
  }, { passive:true });
})();"""

# ── 5. Leiste und Stapel zusammen einblenden ────────────────────────────
ALT_ZEIGEN = """function _ebenenZeigen(an){
  var box = document.getElementById('ebenen');
  if (box) box.classList.toggle('show', !!an);
}"""
NEU_ZEIGEN = """function _ebenenZeigen(an){
  var box = document.getElementById('ebenen');
  if (box) box.classList.toggle('show', !!an);
  var zoom = document.getElementById('zoom-stapel');
  if (zoom) zoom.classList.toggle('show', !!an);
  if (an && typeof _kartenVB === 'function'){
    var vb = _kartenVB();
    if (vb) _zoomKnoepfeStand(vb.w, _kartenMaxVB(vb.h / vb.w));
  }
}"""

# ── 6. aria-label uebersetzen ───────────────────────────────────────────
ALT_I18N = """  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var key = el.getAttribute('data-i18n');
    if (t[key] !== undefined) el.textContent = t[key];
  });"""
NEU_I18N = """  document.querySelectorAll('[data-i18n]').forEach(function(el){
    var key = el.getAttribute('data-i18n');
    if (t[key] !== undefined) el.textContent = t[key];
  });

  /* Beschriftungen, die nur Hilfsmittel hoeren. Die Zoomknoepfe tragen
     ein Zeichen und kein Wort, ihr Name steht im aria-label. */
  document.querySelectorAll('[data-i18n-aria]').forEach(function(el){
    el.setAttribute('aria-label', uiT(el.getAttribute('data-i18n-aria')));
  });"""

UI_NEU = [
    {"key": "zoom_in", "de": "Karte vergrößern", "nl": "Kaart vergroten",
     "en": "Zoom in"},
    {"key": "zoom_out", "de": "Karte verkleinern", "nl": "Kaart verkleinen",
     "en": "Zoom out"},
    {"key": "zoom_all", "de": "Ganze Karte zeigen", "nl": "Hele kaart tonen",
     "en": "Show whole map"},
]


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(CSS_ANKER, CSS_NEU, 'CSS fuer den Zoomstapel')
    tausch(MARKUP_ANKER, MARKUP_NEU, 'die drei Knoepfe')
    tausch(ALT_MASSE, NEU_MASSE, 'Planmasse in der Gestenebene gerichtet')
    tausch(ALT_APPLY, NEU_APPLY, 'applyVB benutzt dieselbe Klemmung')
    tausch(JS_ANKER, JS_NEU, 'kartenZoom, kartenGanz und die Gesten')
    tausch(ALT_ZEIGEN, NEU_ZEIGEN, 'Stapel erscheint mit der Karte')
    tausch(ALT_I18N, NEU_I18N, 'aria-label wird uebersetzt')

    # Die drei Oberflaechentexte in den I18N-Block
    marke = '"ui":['
    i = s.find(marke)
    if i < 0:
        sys.exit('FEHLER: I18N.ui nicht gefunden')
    zusatz = ''.join(json.dumps(u, ensure_ascii=False) + ',' for u in UI_NEU)
    s = s[:i + len(marke)] + zusatz + s[i + len(marke):]
    print('OK  drei Oberflaechentexte')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
