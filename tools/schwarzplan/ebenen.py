# -*- coding: utf-8 -*-
"""Zwei zuschaltbare Ebenen ueber der Karte.

  1946  eine eigene Zeichnung: das Schema des Basisplans von Van Traa, die
        breiten Achsen, das Hofplein, das Fenster zum Fluss am Leuvehaven
        und die Zweckbestimmung des Wijnhavengebiets als Bueroquartier.
        Bewusst ein Schema und keine Kopie des Originalplans: Die Zeichnung
        zeigt das Prinzip, nicht die Parzellen.

  1913  eine gefundene historische Karte, kein eigenes Werk: der Plan zur
        Verbesserung der Verkehrswege in der Innenstadt, 1913, 1:2500.
        Gemeinfrei (anonym, Schutzfrist abgelaufen), aus der Sammlung des
        Stadsarchief Rotterdam ueber Wikimedia Commons. Er deckt die
        noerdliche Haelfte des Ausschnitts ab, also Coolsingel, Blaak und
        Waterstad; das ist genau die Stadt, die 1940 verbrannte.

Beide liegen im Koordinatenraum der Karte und werden ueber zwei Schalter
unter der Karte ein- und ausgeblendet. Nur eine Ebene zugleich: zwei
uebereinander waeren nicht mehr lesbar.
"""
import io
import os
import sys

REPO = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven"
P = os.path.join(REPO, 'index.html')

# Lage des Plans von 1913, aus zwei Passpunkten gemessen
TX1913, TY1913, S1913 = 797.0250, 476.5110, 0.623103
W1913, H1913 = 1233, 1403

# Projektion der aktuellen Karte
LON0, LAT0 = 4.460351, 51.931723
MLON, MLAT = 68671.61405376215, 110540.0
K = 0.7664240847195386


def xy(lat, lon):
    return ((lon - LON0) * MLON * K, (LAT0 - lat) * MLAT * K)


def pfad(punkte):
    return ' '.join(('M' if i == 0 else 'L') + '%.0f %.0f' % xy(*p)
                    for i, p in enumerate(punkte))


# ── Die Achsen des Basisplans, als Linienzug in GPS ───────────────────────
COOLSINGEL = [(51.92530, 4.47400), (51.92280, 4.47470), (51.92010, 4.47530),
              (51.91800, 4.47570), (51.91690, 4.47600)]
BLAAK = [(51.91780, 4.47180), (51.91870, 4.47700), (51.91930, 4.48200),
         (51.91960, 4.48800), (51.92040, 4.49360), (51.92150, 4.49620)]
BOOMPJES = [(51.91380, 4.48430), (51.91450, 4.48780), (51.91560, 4.49180),
            (51.91660, 4.49560)]
LEUVEHAVEN = [(51.91780, 4.48330), (51.91620, 4.48350), (51.91430, 4.48380)]
HOFPLEIN = (51.92530, 4.47400)
# Das Wijnhavengebiet, als Flaeche
WIJNHAVEN = [(51.91880, 4.48520), (51.91930, 4.48960), (51.91700, 4.49090),
             (51.91530, 4.48800), (51.91620, 4.48520)]


def main():
    s = io.open(P, encoding='utf-8').read()

    # ── CSS ──────────────────────────────────────────────────────────────
    css = """
/* ═══════════════════════════════════════════
   KARTENEBENEN
   Zwei Schalter unter der Karte: das Schema des Basisplans von 1946 und
   eine gemeinfreie Karte von 1913. Immer nur eine, zwei uebereinander
   waeren nicht mehr lesbar.
═══════════════════════════════════════════ */
#ebenen {
  position:absolute; left:max(1rem, env(safe-area-inset-left)); bottom:1rem; z-index:7;
  display:flex; gap:.4rem; flex-wrap:wrap; max-width:calc(100%% - 2rem);
}
.eb-schalter {
  font-family:var(--font-mono); font-size:.56rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-1);
  background:rgba(255,255,255,.95); border:1px solid var(--ink-1); border-radius:0;
  padding:.42rem .7rem; cursor:pointer; -webkit-tap-highlight-color:transparent;
  touch-action:manipulation; white-space:nowrap;
  opacity:0; pointer-events:none; transition:opacity .4s, background .2s;
}
#nav-crumb.show ~ #map-panel #ebenen .eb-schalter,
#ebenen.show .eb-schalter { opacity:1; pointer-events:auto; }
.eb-schalter[aria-pressed="true"] { background:var(--accent); }
.eb-schalter:hover, .eb-schalter:focus-visible { background:var(--accent); outline:none; }
.eb-quelle {
  font-family:var(--font-mono); font-size:.5rem; letter-spacing:.08em;
  color:var(--ink-2); background:rgba(255,255,255,.9); padding:.3rem .5rem;
  max-width:26rem; line-height:1.5; text-transform:none;
}
.eb-quelle[hidden] { display:none; }
/* Die Zeichnung selbst */
.ov-achse { fill:none; stroke:var(--accent); stroke-opacity:.85; stroke-linecap:round;
  stroke-linejoin:round; }
.ov-kante { fill:none; stroke:var(--ink-1); stroke-width:2; stroke-dasharray:10 7; }
.ov-flaeche { fill:var(--accent); fill-opacity:.22; stroke:var(--ink-1);
  stroke-width:2; stroke-dasharray:6 5; }
.ov-punkt { fill:var(--accent); stroke:var(--ink-1); stroke-width:3; }
.ov-text { font-family:var(--font-mono); font-size:26px; letter-spacing:2px;
  fill:var(--ink-1); paint-order:stroke; stroke:var(--paper-0); stroke-width:6; }
.ov-text.klein { font-size:20px; }
"""
    anker = '/* ═══════════════════════════════════════════\n   BASISPLAN + FAZIT'
    if s.count(anker) != 1:
        sys.exit('FEHLER: CSS-Anker nicht eindeutig')
    s = s.replace(anker, css.strip() + '\n\n' + anker)

    # ── Die Ebenen in das SVG, direkt hinter das Kartenbild ──────────────
    bild = [z for z in s.split('\r\n') if 'class="plan-bild"' in z]
    if len(bild) != 1:
        sys.exit('FEHLER: Kartenbild nicht eindeutig')
    bild = bild[0]

    g = []
    g.append('<!-- Zuschaltbare Ebenen. Die historische Karte liegt als Bild, das Schema')
    g.append('     von 1946 als eigene Zeichnung im selben Koordinatenraum. -->')
    # Der Plan von 1913 liegt nordgerichtet, Massstab und Versatz aus zwei
    # Passpunkten: dem Raadhuis und der Laurenskerk, die als einziges Bauwerk
    # von 1913 heute noch steht. Das ist eine Einpassung, keine Vermessung.
    g.append('<image id="ov-hist" href="img/plan-1913.webp" x="0" y="0" width="%d" height="%d"'
             % (W1913, H1913))
    g.append('       transform="translate(%.1f %.1f) scale(%.5f)" opacity=".9" hidden/>'
             % (TX1913, TY1913, S1913))
    g.append('<g id="ov-1946" hidden aria-hidden="true">')
    g.append('  <path class="ov-achse" style="stroke-width:46" d="%s"/>' % pfad(COOLSINGEL))
    g.append('  <path class="ov-achse" style="stroke-width:40" d="%s"/>' % pfad(BLAAK))
    g.append('  <path class="ov-achse" style="stroke-width:34" d="%s"/>' % pfad(BOOMPJES))
    g.append('  <path class="ov-flaeche" d="%s Z"/>' % pfad(WIJNHAVEN))
    g.append('  <path class="ov-kante" d="%s"/>' % pfad(LEUVEHAVEN))
    hx, hy = xy(*HOFPLEIN)
    g.append('  <circle class="ov-punkt" cx="%.0f" cy="%.0f" r="30"/>' % (hx, hy))
    for lat, lon, t, kl, dx, dy in (
            (51.92530, 4.47400, 'HOFPLEIN', '', 44, 10),
            (51.92100, 4.47530, 'COOLSINGEL 80 M', '', 36, 0),
            (51.91960, 4.48800, 'BLAAK', '', 0, -32),
            (51.91560, 4.49180, 'BOOMPJES', '', 0, 44),
            (51.91620, 4.48350, 'FENSTER ZUM FLUSS', 'klein', -36, 0),
            (51.91720, 4.48780, 'WIJNHAVEN: BUEROS', 'klein', 0, 0)):
        x, y = xy(lat, lon)
        anker_t = 'end' if dx < 0 else ('middle' if dx == 0 else 'start')
        g.append('  <text class="ov-text %s" x="%.0f" y="%.0f" text-anchor="%s">%s</text>'
                 % (kl, x + dx, y + dy, anker_t, t))
    g.append('</g>')
    s = s.replace(bild, bild + '\r\n' + '\r\n'.join(g))

    # ── Die Schalter unter die Karte ─────────────────────────────────────
    a = '<div id="map-touch-layer"></div>'
    if s.count(a) != 1:
        sys.exit('FEHLER: map-touch-layer nicht eindeutig')
    schalter = [
     '<!-- Schalter fuer die Kartenebenen. Stehen im Kartenfeld, erscheinen mit ihm. -->',
     '<div id="ebenen">',
     '  <button class="eb-schalter" type="button" data-ebene="ov-1946" aria-pressed="false"',
     '          onclick="ebeneUm(\'ov-1946\')">1946 Basisplan</button>',
     '  <button class="eb-schalter" type="button" data-ebene="ov-hist" aria-pressed="false"',
     '          onclick="ebeneUm(\'ov-hist\')">1913 Plan</button>',
     '  <p class="eb-quelle" id="eb-quelle" hidden></p>',
     '</div>',
    ]
    s = s.replace(a, '\r\n'.join(schalter) + '\r\n' + a)

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('OK  CSS der Ebenen')
    print('OK  Zeichnung 1946 und Platzhalter fuer 1913 im SVG')
    print('OK  Schalter unter der Karte')
    print('\nnoch offen: JS (ebeneUm), Bild plan-1913.webp samt Verortung')


if __name__ == '__main__':
    main()
