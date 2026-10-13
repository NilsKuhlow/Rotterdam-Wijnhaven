# -*- coding: utf-8 -*-
"""Die neue, weiter gefasste Karte georeferenzieren.

Wie bei den Vorgaengern gemessen und nicht geschaetzt: Die Wasserflaeche der
Karte wird gegen die Wasserflaeche der bekannten OSM-Projektion
kreuzkorreliert, mittelwertfrei und oertlich normiert, auf einer Kreisscheibe
um die Wijnhaven.

Neu ist der groessere Ausschnitt. Deshalb zwei Anpassungen:

  * Der Suchbereich fuer den Massstab ist weit geoeffnet, von rund 0,3 bis
    1,7 m je Bildpunkt. Welcher Massstab es ist, soll die Messung sagen.
  * Die Vorlage wird nicht mehr mit festem Radius in Metern gebaut, sondern
    mit festem Radius im Suchraster. So bleibt sie bei jedem Massstab gleich
    gross und gleich aussagekraeftig; in Metern waechst sie mit.

Das Wasser traegt in dieser Karte den Grauwert 199, 15 % der Flaeche und
27 % der unteren Bildhaelfte, wo die Maas liegt.
"""
import pickle

import numpy as np
from PIL import Image, ImageDraw

BILD = r"C:\Temp\wij3d\neu_roh.png"
ALT = r"C:\Temp\wij3d\alt_geom.pkl"
ZIEL = r"C:\Temp\wij3d\neu_reg.pkl"

K = 0.7664240847195386
LON0, LAT0 = 4.4795, 51.9225
MLON, MLAT = 68671.61405376215, 110540.0
MITTE = ((4.4888 - LON0) * MLON, (LAT0 - 51.9180) * MLAT)

RASTER = 4.0            # Bildpunkte je Rasterpunkt der Suche
R_RASTER = 330.0        # Radius der Vorlage, in Rasterpunkten


def main():
    a = np.asarray(Image.open(BILD).convert('L'))
    h, w = a.shape
    wasser = ((a > 185) & (a < 215)).astype(np.float32)
    gh, gw = int(h / RASTER), int(w / RASTER)
    I = np.asarray(Image.fromarray((wasser * 255).astype(np.uint8)).resize((gw, gh), Image.BILINEAR),
                   dtype=np.float32) / 255.0
    I = (I > 0.5).astype(np.float32)
    print('Bild %dx%d px -> Suchraster %dx%d, Wasseranteil %.1f %%'
          % (w, h, gw, gh, 100 * I.mean()))
    F_I, F_I2 = np.fft.rfft2(I), np.fft.rfft2(I * I)

    alt = pickle.load(open(ALT, 'rb'))
    alt_w = [np.asarray([(x / K - MITTE[0], y / K - MITTE[1]) for x, y in r])
             for r in alt['ebenen']['water-fill']]

    n = int(2 * R_RASTER) + 4
    if n >= min(gw, gh):
        raise SystemExit('Vorlage zu gross fuer das Suchraster')
    yy, xx = np.mgrid[0:n, 0:n]
    scheibe = (((xx - n / 2) ** 2 + (yy - n / 2) ** 2) <= R_RASTER ** 2).astype(np.float32)
    N = scheibe.sum()

    def kk(F, k):
        g = np.zeros(I.shape, dtype=np.float32)
        g[:n, :n] = k
        return np.fft.irfft2(F * np.conj(np.fft.rfft2(g)), I.shape)

    sI, sI2 = kk(F_I, scheibe), kk(F_I2, scheibe)
    nenner_bild = np.sqrt(np.maximum(sI2 - sI * sI / N, 1e-6))

    beste = []
    for theta in (-1.0, -0.5, 0.0, 0.5, 1.0):
        c, s_ = np.cos(np.radians(theta)), np.sin(np.radians(theta))
        for m_je_px in np.arange(1.2, 7.0, 0.04):       # Meter je Rasterpunkt
            skala = 1.0 / m_je_px                        # Rasterpunkte je Meter
            bild = Image.new('L', (n, n), 0)
            dd = ImageDraw.Draw(bild)
            for p in alt_w:
                x = (p[:, 0] * c - p[:, 1] * s_) * skala + n / 2
                y = (p[:, 0] * s_ + p[:, 1] * c) * skala + n / 2
                dd.polygon(list(zip(x, y)), fill=255)
            T = np.asarray(bild, dtype=np.float32) / 255.0
            anteil = (T * scheibe).sum() / N
            if anteil < 0.05 or anteil > 0.9:
                continue                                  # Vorlage fast leer oder fast voll
            T0 = (T - anteil) * scheibe
            normT = np.sqrt((T0 ** 2).sum())
            if normT < 1e-6:
                continue
            ncc = kk(F_I, T0) / (normT * nenner_bild)
            i = int(np.argmax(ncc))
            dy, dx = divmod(i, I.shape[1])
            if dx > gw // 2: dx -= gw
            if dy > gh // 2: dy -= gh
            beste.append((float(ncc.flat[i]), theta, float(m_je_px),
                          n / 2 + dx, n / 2 + dy))

    beste.sort(reverse=True)
    print('\nbeste acht:')
    for wv, th, mpp, ox, oy in beste[:8]:
        m_je_bp = mpp / RASTER
        # Massstab: 1 Bildpunkt = 1/300 Zoll = 0.0846667 mm Papier
        massstab = m_je_bp * 1000.0 / (25.4 / 300.0)
        print('  NCC %.4f  Drehung %+.1f  %.4f m je Bildpunkt  -> 1:%.0f'
              % (wv, th, m_je_bp, massstab))

    wv, th, mpp, ox, oy = beste[0]
    m_je_bp = mpp / RASTER
    bx = (ox - MITTE[0] / mpp) * RASTER
    by = (oy - MITTE[1] / mpp) * RASTER
    print('\nUrsprung lon %.4f / lat %.4f liegt bei (%.0f, %.0f) Bildpunkten' % (LON0, LAT0, bx, by))
    for name, (x, y) in (('links oben', (0, 0)), ('rechts unten', (w, h))):
        lon = LON0 + (x - bx) * m_je_bp / MLON
        lat = LAT0 - (y - by) * m_je_bp / MLAT
        print('  %-13s lon %.5f  lat %.5f' % (name, lon, lat))
    print('  Abdeckung %.0f x %.0f m' % (w * m_je_bp, h * m_je_bp))

    pickle.dump({'ncc': wv, 'theta': th, 'm_je_bildpunkt': m_je_bp,
                 'bx': bx, 'by': by, 'bild': [h, w]}, open(ZIEL, 'wb'))
    print('\n->', ZIEL)


if __name__ == '__main__':
    main()
