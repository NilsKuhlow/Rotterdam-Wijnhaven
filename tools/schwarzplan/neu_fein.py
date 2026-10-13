# -*- coding: utf-8 -*-
"""Feinsuche um das grobe Ergebnis, danach die Gegenprobe an den sieben Bauten.

Die Grobsuche lief in Schritten von 0,01 m je Bildpunkt und 0,5 Grad. Hier
wird in 0,002 m und 0,1 Grad nachgefasst. Die Gegenprobe fragt dann, ob die
sieben bekannten Koordinaten im Bild auf einem Baukoerper landen; das ist der
Test, der zaehlt, denn er benutzt andere Information als die Korrelation.
"""
import pickle

import numpy as np
from PIL import Image, ImageDraw

BILD = r"C:\Temp\wij3d\neu_roh.png"
ALT = r"C:\Temp\wij3d\alt_geom.pkl"
GROB = r"C:\Temp\wij3d\neu_reg.pkl"
ZIEL = r"C:\Temp\wij3d\neu_fein.pkl"

K = 0.7664240847195386
LON0, LAT0 = 4.4795, 51.9225
MLON, MLAT = 68671.61405376215, 110540.0
MITTE = ((4.4888 - LON0) * MLON, (LAT0 - 51.9180) * MLAT)
RASTER = 4.0
R_RASTER = 330.0

COORDS = {'witte-huis': (51.91883, 4.49173), 'kubuswoningen': (51.9199, 4.4902),
          'markthal': (51.92011, 4.48687), 'red-apple': (51.9173, 4.48895),
          'wijnhaveneiland': (51.9166, 4.4876), 'ey-netherlands': (51.91434, 4.48652),
          'casanova': (51.91796, 4.48736)}


def main():
    grob = pickle.load(open(GROB, 'rb'))
    a = np.asarray(Image.open(BILD).convert('L'))
    h, w = a.shape
    wasser = ((a > 185) & (a < 215)).astype(np.float32)
    gh, gw = int(h / RASTER), int(w / RASTER)
    I = np.asarray(Image.fromarray((wasser * 255).astype(np.uint8)).resize((gw, gh), Image.BILINEAR),
                   dtype=np.float32) / 255.0
    I = (I > 0.5).astype(np.float32)
    F_I, F_I2 = np.fft.rfft2(I), np.fft.rfft2(I * I)

    alt = pickle.load(open(ALT, 'rb'))
    alt_w = [np.asarray([(x / K - MITTE[0], y / K - MITTE[1]) for x, y in r])
             for r in alt['ebenen']['water-fill']]

    n = int(2 * R_RASTER) + 4
    yy, xx = np.mgrid[0:n, 0:n]
    scheibe = (((xx - n / 2) ** 2 + (yy - n / 2) ** 2) <= R_RASTER ** 2).astype(np.float32)
    N = scheibe.sum()

    def kk(F, k):
        g = np.zeros(I.shape, dtype=np.float32); g[:n, :n] = k
        return np.fft.irfft2(F * np.conj(np.fft.rfft2(g)), I.shape)

    sI, sI2 = kk(F_I, scheibe), kk(F_I2, scheibe)
    nenner = np.sqrt(np.maximum(sI2 - sI * sI / N, 1e-6))

    mpp0 = grob['m_je_bildpunkt'] * RASTER
    beste = []
    for theta in np.arange(-1.0, 1.001, 0.1):
        c, s_ = np.cos(np.radians(theta)), np.sin(np.radians(theta))
        for mpp in np.arange(mpp0 - 0.08, mpp0 + 0.081, 0.008):
            skala = 1.0 / mpp
            bild = Image.new('L', (n, n), 0)
            dd = ImageDraw.Draw(bild)
            for p in alt_w:
                x = (p[:, 0] * c - p[:, 1] * s_) * skala + n / 2
                y = (p[:, 0] * s_ + p[:, 1] * c) * skala + n / 2
                dd.polygon(list(zip(x, y)), fill=255)
            T = np.asarray(bild, dtype=np.float32) / 255.0
            anteil = (T * scheibe).sum() / N
            T0 = (T - anteil) * scheibe
            normT = np.sqrt((T0 ** 2).sum())
            if normT < 1e-6:
                continue
            ncc = kk(F_I, T0) / (normT * nenner)
            i = int(np.argmax(ncc)); dy, dx = divmod(i, I.shape[1])
            if dx > gw // 2: dx -= gw
            if dy > gh // 2: dy -= gh
            beste.append((float(ncc.flat[i]), float(theta), float(mpp),
                          n / 2 + dx, n / 2 + dy))
    beste.sort(reverse=True)
    wv, th, mpp, ox, oy = beste[0]
    m_je_bp = mpp / RASTER
    massstab = m_je_bp * 1000.0 / (25.4 / 300.0)
    print('fein: NCC %.4f  Drehung %+.2f Grad  %.4f m je Bildpunkt  -> 1:%.0f'
          % (wv, th, m_je_bp, massstab))

    bx = (ox - MITTE[0] / mpp) * RASTER
    by = (oy - MITTE[1] / mpp) * RASTER

    # ── Gegenprobe: liegen die sieben Bauten auf Schwarz? ──
    schwarz = a < 60
    ys, xs = np.nonzero(schwarz)
    pts = np.stack([xs, ys], 1)
    print('\nGegenprobe an den sieben Bauten:')
    schlecht = 0
    for name, (la, lo) in COORDS.items():
        px = bx + (lo - LON0) * MLON / m_je_bp
        py = by + (LAT0 - la) * MLAT / m_je_bp
        drin = 0 <= int(py) < h and 0 <= int(px) < w and schwarz[int(py), int(px)]
        d = np.hypot(pts[:, 0] - px, pts[:, 1] - py).min() * m_je_bp
        if d > 25:
            schlecht += 1
        print('  %-16s %s%.1f m' % (name, 'im Haus, ' if drin else '', d))
    print('%d von 7 liegen weiter als 25 m entfernt' % schlecht)

    LON_LO = LON0 + (0 - bx) * m_je_bp / MLON
    LAT_LO = LAT0 - (0 - by) * m_je_bp / MLAT
    print('\nlinke obere Ecke: lon %.6f / lat %.6f' % (LON_LO, LAT_LO))
    print('Abdeckung %.0f x %.0f m' % (w * m_je_bp, h * m_je_bp))

    pickle.dump({'ncc': wv, 'theta': th, 'm_je_bildpunkt': m_je_bp, 'massstab': massstab,
                 'bx': bx, 'by': by, 'bild': [h, w]}, open(ZIEL, 'wb'))
    print('\n->', ZIEL)


if __name__ == '__main__':
    main()
