# -*- coding: utf-8 -*-
"""Schwarzplan-PDF georeferenzieren und in SVG-Pfade fuer index.html uebersetzen.

Wird nur gebraucht, wenn der Plan neu gezeichnet oder neu exportiert wird.

    python schwarzplan.py Probe_Schwarzplan_Rotterdam.pdf

Ablauf
------
1. Geometrie aus dem PDF holen. Der Plan ist ein reines Vektor-PDF ohne
   Rasterbilder: eine Wasserflaeche, rund 1700 schwarze Baukoerper und rund
   18000 gestrichene Strassen- und Parzellenkanten.

2. Georeferenzieren. Das PDF traegt keine Georeferenz. Sie wird gemessen,
   indem die Wasserflaeche gegen die des alten OSM-Schwarzplans
   kreuzkorreliert wird, dessen Projektion bekannt ist. Bewertet wird mit
   mittelwertfreier, oertlich normierter Korrelation auf einer Kreisscheibe
   um die Wijnhaven; ohne diese Normierung gewinnt sonst stets die groesste
   Schablone. Ergebnis fuer die Probe vom September 2026: 0 Grad Drehung,
   0,5669 pt je Meter (also genau 1:5000), Korrelation 0,90.

3. In SVG-Einheiten umrechnen. Eine Einheit bleibt bewusst 1,3048 m wie im
   alten Plan, damit Punktgroessen, Strichstaerken, Beschriftungen und der
   50-m-Radius unveraendert weitergelten. Nur der Ursprung wandert.

Fallgruben, beide schon einmal zugeschlagen
-------------------------------------------
* Rundung: '%.0f' liefert bei ganzen Zahlen keinen Dezimalpunkt. Ein
  anschliessendes rstrip('0') frisst dann die Null am Wortende, aus 180 wird
  18. Die Karte sah danach aus wie ein Wollknaeuel. Siehe runde().
* Ungefuellte Objekte sind Striche, keine Flaechen. Sie muessen als
  Polylinien heraus, nicht als Polygone.
"""
import gzip
import pickle
import sys

import numpy as np
from PIL import Image, ImageDraw

try:
    import fitz                      # PyMuPDF
except ImportError:
    sys.exit('PyMuPDF fehlt:  pip install pymupdf')

# Projektion des alten OSM-Schwarzplans, Bezugssystem der Messung
LON0_ALT, LAT0_ALT = 4.4795, 51.9225
MLON, MLAT = 68671.61405376215, 110540.0
K = 0.7664240847195386               # SVG-Einheiten je Meter, bleibt wie gehabt

WASSER = (0.0, 0.204, 0.298)         # Fuellfarbe der Wasserflaeche im PDF
SCHWARZ = (0.0, 0.0, 0.0)
SKALA_5000 = 0.2 / 25.4 * 72.0       # pt je Meter bei 1:5000


# ── Rundung ────────────────────────────────────────────────────────────────
def runde(v, n):
    """Kurze Dezimalzahl. Der Punkt muss stehen bleiben, sonst frisst das
       Abschneiden der Nullen die letzte Stelle der ganzen Zahl."""
    s = '%.*f' % (n, v)
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '', '-') else s


assert runde(180, 0) == '180'
assert runde(120.0, 1) == '120'


# ── 1. Geometrie ───────────────────────────────────────────────────────────
def bez(p0, p1, p2, p3, n=6):
    aus = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        aus.append((u**3 * p0[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * p3[1]))
    return aus


def ringe(gruppe):
    aus, akt = [], []
    for it in gruppe['items']:
        art = it[0]
        if art == 'l':
            a, b = it[1], it[2]
            if not akt:
                akt.append((a.x, a.y))
            akt.append((b.x, b.y))
        elif art == 'c':
            a, b, c, d = it[1], it[2], it[3], it[4]
            if not akt:
                akt.append((a.x, a.y))
            akt.extend(bez((a.x, a.y), (b.x, b.y), (c.x, c.y), (d.x, d.y)))
        elif art in ('re', 'qu'):
            if akt:
                aus.append(akt); akt = []
            if art == 're':
                r = it[1]
                aus.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
            else:
                q = it[1]
                aus.append([(p.x, p.y) for p in (q.ul, q.ur, q.lr, q.ll)])
    if akt:
        aus.append(akt)
    return [r for r in aus if len(r) >= 2]


def lies(pdf):
    seite = fitz.open(pdf)[0]
    ebenen = {'wasser': [], 'bau': [], 'linie': []}
    for g in seite.get_drawings():
        c = g.get('fill')
        f = tuple(round(v, 3) for v in c) if c else None
        ziel = 'wasser' if f == WASSER else 'bau' if f == SCHWARZ else 'linie' if f is None else None
        if ziel:
            ebenen[ziel].extend(ringe(g))
    return (seite.rect.width, seite.rect.height), ebenen


# ── 2. Georeferenz ─────────────────────────────────────────────────────────
def messe_lage(wasser_neu, wasser_alt_m, seite, skala=SKALA_5000, px=0.5, radius=620.0):
    """Wo liegt der Plan? Rueckgabe: Planpunkt des alten Projektionsursprungs."""
    mitte = ((4.4888 - LON0_ALT) * MLON, (LAT0_ALT - 51.9180) * MLAT)
    W, H = seite
    gw, gh = int(W / px) + 2, int(H / px) + 2
    im = Image.new('L', (gw, gh), 0); d = ImageDraw.Draw(im)
    for r in wasser_neu:
        d.polygon([(x / px, y / px) for x, y in r], fill=255)
    I = np.asarray(im, dtype=np.float32) / 255.0
    F_I, F_I2 = np.fft.rfft2(I), np.fft.rfft2(I * I)

    r_px = radius * skala / px
    n = int(2 * r_px) + 4
    im2 = Image.new('L', (n, n), 0); d2 = ImageDraw.Draw(im2)
    for r in wasser_alt_m:
        a = np.asarray(r) - np.asarray(mitte)
        d2.polygon(list(zip(a[:, 0] * skala / px + n / 2, a[:, 1] * skala / px + n / 2)), fill=255)
    T = np.asarray(im2, dtype=np.float32) / 255.0
    yy, xx = np.mgrid[0:n, 0:n]
    scheibe = (((xx - n / 2) ** 2 + (yy - n / 2) ** 2) <= r_px ** 2).astype(np.float32)
    N = scheibe.sum()
    T0 = (T - (T * scheibe).sum() / N) * scheibe
    normT = np.sqrt((T0 ** 2).sum())

    def kk(F, k):
        g = np.zeros(I.shape, dtype=np.float32); g[:n, :n] = k
        return np.fft.irfft2(F * np.conj(np.fft.rfft2(g)), I.shape)
    sI, sI2 = kk(F_I, scheibe), kk(F_I2, scheibe)
    ncc = kk(F_I, T0) / (normT * np.sqrt(np.maximum(sI2 - sI * sI / N, 1e-6)))
    i = int(np.argmax(ncc)); dy, dx = divmod(i, I.shape[1])
    if dx > gw // 2: dx -= gw
    if dy > gh // 2: dy -= gh
    ox, oy = (n / 2 + dx) * px, (n / 2 + dy) * px
    return ox - mitte[0] * skala, oy - mitte[1] * skala, float(ncc.flat[i])


# ── 3. SVG ─────────────────────────────────────────────────────────────────
def flaechen(ringe_, f, n=1):
    t = []
    for r in ringe_:
        if len(r) >= 3:
            t.append('M' + ' '.join('%s %s' % (runde(x * f, n), runde(y * f, n)) for x, y in r) + 'Z')
    return ''.join(t)


def linien(ringe_, f, n=0, raster=0.15, mindest=0.5):
    """Strecken an eindeutigen Knoten zu Polylinien verketten. Nur wo genau
       zwei Strecken zusammentreffen, sonst wuerde an Kreuzungen beliebig
       weitergelaufen."""
    st = []
    for r in ringe_:
        if len(r) < 2:
            continue
        a = (r[0][0] * f, r[0][1] * f); b = (r[-1][0] * f, r[-1][1] * f)
        if abs(a[0] - b[0]) < mindest and abs(a[1] - b[1]) < mindest:
            continue
        st.append((a, b))
    sch = lambda p: (round(p[0] / raster), round(p[1] / raster))
    knoten = {}
    for i, (a, b) in enumerate(st):
        knoten.setdefault(sch(a), []).append(i); knoten.setdefault(sch(b), []).append(i)
    benutzt = [False] * len(st); ketten = []
    for i in range(len(st)):
        if benutzt[i]:
            continue
        benutzt[i] = True
        a, b = st[i]; k = [a, b]
        for _ in (0, 1):
            k.reverse()
            while True:
                s = sch(k[-1]); nb = knoten.get(s, [])
                if len(nb) != 2:
                    break
                j = next((x for x in nb if not benutzt[x]), None)
                if j is None:
                    break
                p, q = st[j]; w = q if sch(p) == s else p
                if sch(w) == s:
                    break
                benutzt[j] = True; k.append(w)
        ketten.append(k)
    # strenge Gegenprobe: jeder Schritt muss eine Strecke der Vorlage sein
    orig = set()
    for a, b in st:
        orig.add((sch(a), sch(b))); orig.add((sch(b), sch(a)))
    schlecht = sum(1 for k in ketten for u, v in zip(k, k[1:]) if (sch(u), sch(v)) not in orig)
    if schlecht:
        sys.exit('FEHLER: %d verkettete Schritte stehen nicht in der Vorlage' % schlecht)
    print('  Linien: %d Strecken zu %d Ketten, Gegenprobe ohne Befund' % (len(st), len(ketten)))
    return ''.join('M' + ' '.join('%s %s' % (runde(x, n), runde(y, n)) for x, y in k)
                   for k in ketten if len(k) >= 2)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pdf = sys.argv[1]
    seite, ebenen = lies(pdf)
    print('Plan %.1f x %.1f pt' % seite)
    for k, v in ebenen.items():
        print('  %-7s %6d Ringe' % (k, len(v)))

    alt = pickle.load(open('alt_wasser.pkl', 'rb'))     # Wasser des alten Plans, in Metern
    px0, py0, ncc = messe_lage(ebenen['wasser'], alt, seite)
    print('\nGeoreferenz: 1:5000, nordorientiert, Korrelation %.3f' % ncc)
    LON0 = LON0_ALT - px0 / (MLON * SKALA_5000)
    LAT0 = LAT0_ALT + py0 / (MLAT * SKALA_5000)
    f = K / SKALA_5000
    print('linke obere Ecke: lon %.6f / lat %.6f' % (LON0, LAT0))
    print('MAP_VW %d, MAP_VH %d' % (round(seite[0] * f), round(seite[1] * f)))

    print('\nPfade:')
    aus = {'wasser': flaechen(ebenen['wasser'], f),
           'bau': flaechen(ebenen['bau'], f),
           'linie': linien(ebenen['linie'], f)}
    for k, v in aus.items():
        print('  %-7s %7.1f KB roh, %6.1f KB gzip'
              % (k, len(v.encode()) / 1024, len(gzip.compress(v.encode(), 9)) / 1024))
    aus.update({'LON0': LON0, 'LAT0': LAT0,
                'MAP_VW': round(seite[0] * f), 'MAP_VH': round(seite[1] * f)})
    pickle.dump(aus, open('schwarzplan_svg.pkl', 'wb'))
    print('\ngeschrieben: schwarzplan_svg.pkl')


if __name__ == '__main__':
    main()
