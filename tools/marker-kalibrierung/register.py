# -*- coding: utf-8 -*-
"""Registriert das Modell-Hoehenraster gegen die OSM-Grundrisse der Website.
Ergebnis: die Verschiebung, mit der sich Modellkoordinaten in GPS umrechnen lassen."""
import json, re, sys
import numpy as np
from PIL import Image, ImageDraw

CELL = 2.0
# Projektion der Website (gpsToSvg in index.html), exakt uebernommen
KLON = 68671.61405376215
KLAT = 110540.0
S    = 0.7664240847195386        # SVG-Einheiten pro Meter
LON_REF, LAT_REF = 4.4795, 51.9225

# ── 1. Modellraster laden, Gebaeudemaske bilden ─────────────────────────────
d = np.load(r"C:\Temp\wij3d\geo\dsm.npz")
dsm, x0, z0 = d['dsm'], float(d['x0']), float(d['z0'])
nz, nx = dsm.shape
filled = ~np.isnan(dsm)
dsm_f = np.where(filled, dsm, np.nanmax(dsm))

def block_min(a, k):
    """Grober Bodenschaetzer: Minimum je k x k Block, danach wieder aufgeblasen."""
    H, W = a.shape
    Hp, Wp = -(-H // k) * k, -(-W // k) * k
    p = np.full((Hp, Wp), np.nanmax(a), dtype=np.float32)
    p[:H, :W] = a
    b = p.reshape(Hp // k, k, Wp // k, k).min(axis=(1, 3))
    return np.repeat(np.repeat(b, k, axis=0), k, axis=1)[:H, :W]

ground = block_min(dsm_f, 50)                      # 100 m Fenster
ndsm = np.where(filled, dsm_f - ground, 0.0)
A = (ndsm > 8.0).astype(np.float32)                # Modell: Gebaeude
print('Modellraster %dx%d, Gebaeudezellen %d (%.1f%%)' % (nx, nz, A.sum(), 100 * A.mean()))

# ── 2. OSM-Grundrisse rastern (metrisch, Ursprung = SVG 0,0) ────────────────
paths = json.load(open(r"C:\Temp\wij3d\map\paths.json", encoding='utf-8'))
d_str = paths['buildings']
OSM_W_M, OSM_H_M = 1000.0 / S, 1949.0 / S
bw, bh = int(OSM_W_M / CELL) + 1, int(OSM_H_M / CELL) + 1
img = Image.new('1', (bw, bh), 0)
dr = ImageDraw.Draw(img)
subs = [s for s in d_str.replace('Z', 'Z|').split('|') if 'M' in s]
num = re.compile(r'-?\d+(?:\.\d+)?')
poly_n = 0
for s in subs:
    v = [float(t) for t in num.findall(s)]
    if len(v) < 6:
        continue
    pts = [(v[i] / S / CELL, v[i + 1] / S / CELL) for i in range(0, len(v) - 1, 2)]
    dr.polygon(pts, fill=1)
    poly_n += 1
B = np.array(img, dtype=np.float32)
print('OSM-Raster %dx%d, %d Polygone, Gebaeudezellen %d (%.1f%%)' % (bw, bh, poly_n, B.sum(), 100 * B.mean()))

# ── 3. Kreuzkorrelation per FFT ────────────────────────────────────────────
H = 1 << int(np.ceil(np.log2(max(nz, bh) + max(nz, bh) // 2)))
W = 1 << int(np.ceil(np.log2(max(nx, bw) + max(nx, bw) // 2)))
print('FFT-Groesse %dx%d' % (H, W))
Ap = np.zeros((H, W), np.float32); Ap[:nz, :nx] = A - A.mean()
Bp = np.zeros((H, W), np.float32); Bp[:bh, :bw] = B - B.mean()
corr = np.fft.irfft2(np.fft.rfft2(Bp) * np.conj(np.fft.rfft2(Ap)), s=(H, W))
k = int(np.argmax(corr)); sz, sx = k // W, k % W
if sz > H // 2: sz -= H
if sx > W // 2: sx -= W
peak = corr.max(); mu, sd = corr.mean(), corr.std()
print('Bestes Versatz: sx=%d Zellen, sz=%d Zellen   Peak %.1f  (%.1f Sigma ueber Mittel)'
      % (sx, sz, peak, (peak - mu) / sd))

# ── 4. Umrechnung ableiten und pruefen ─────────────────────────────────────
# Modellzelle (0,0) entspricht OSM-Zelle (sz, sx) -> Metern ab SVG-Ursprung
east_of_x0  = sx * CELL
south_of_z0 = sz * CELL
# Modell X -> Meter Ost:  east = (X - x0) + east_of_x0
# Modell Z -> Meter Sued: south = (Z - z0) + south_of_z0
EX = east_of_x0 - x0
EZ = south_of_z0 - z0
print('\nModell -> Meter ab SVG-Ursprung:  east = X + %.2f   south = Z + %.2f' % (EX, EZ))
lon_of_X0 = LON_REF + EX / KLON
lat_of_Z0 = LAT_REF - EZ / KLAT
print('Modell (0,0,0) liegt bei  lat %.6f  lon %.6f' % (lat_of_Z0, lon_of_X0))
print('\nUmrechnung fuer die Website:')
print('  X = (lon - %.6f) * %.5f' % (lon_of_X0, KLON))
print('  Z = (%.6f - lat) * %.5f' % (lat_of_Z0, KLAT))

np.savez_compressed(r"C:\Temp\wij3d\geo\reg.npz", A=A, B=B, sx=sx, sz=sz,
                    EX=EX, EZ=EZ, lon0=lon_of_X0, lat0=lat_of_Z0, x0=x0, z0=z0, cell=CELL)

# Kontrollbild: Modellmaske rot ueber OSM-Maske schwarz
ov = np.zeros((bh, bw, 3), np.uint8)
ov[..., :] = np.where(B[..., None] > 0, 40, 255)
ys, xs = np.nonzero(A)
oy, ox = ys + sz, xs + sx
m = (oy >= 0) & (oy < bh) & (ox >= 0) & (ox < bw)
ov[oy[m], ox[m], 0] = 255; ov[oy[m], ox[m], 1] = 60; ov[oy[m], ox[m], 2] = 60
y1, y2 = max(0, sz - 40), min(bh, sz + nz + 40)
x1, x2 = max(0, sx - 40), min(bw, sx + nx + 40)
Image.fromarray(ov[y1:y2, x1:x2]).save(r"C:\Temp\wij3d\geo\_overlay.png")
print('\nKontrollbild: C:\\Temp\\wij3d\\geo\\_overlay.png')
