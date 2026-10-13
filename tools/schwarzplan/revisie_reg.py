# -*- coding: utf-8 -*-
"""Die Revisiekarte auf den Schwarzplan einmessen.

Die Karte ist nordgerichtet (Nordpfeil zeigt nach oben) und massstabstreu,
sie traegt einen Massstabsbalken. Zu bestimmen sind deshalb nur Massstab und
Versatz, keine Drehung.

Gemessen wird am Wasser, wie bei allen Karten dieses Projekts: Die blaue
Flaeche der Revisiekarte wird gegen die graue Wasserflaeche des Schwarzplans
kreuzkorreliert, mittelwertfrei und oertlich normiert. Wasser ist dafuer der
beste Zeuge, weil Maas und Hafenbecken in beiden Karten dieselben sind und
sich seit 1613 nicht verschoben haben.
"""
import pickle

import numpy as np
from PIL import Image

REVISIE = r"C:\Temp\wij3d\revisie.jpg"
HEUTE = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven\img\schwarzplan.webp"
ZIEL = r"C:\Temp\wij3d\revisie_reg.pkl"

MAP_VW = 3010.0                 # Zeicheneinheiten der Karte in der Breite
M_JE_PX_HEUTE = 0.8580          # Meter je Bildpunkt des Schwarzplans
ARBEIT = 3.0                    # Meter je Rasterpunkt der Suche


def masken():
    h = Image.open(HEUTE).convert('L')
    a = np.asarray(h)
    wasser_h = ((a > 185) & (a < 215)).astype(np.float32)
    r = Image.open(REVISIE).convert('RGB')
    b = np.asarray(r).astype(np.int16)
    R, G, B = b[:, :, 0], b[:, :, 1], b[:, :, 2]
    wasser_r = ((B > 140) & (B - R > 50) & (B - G > 25)).astype(np.float32)
    return wasser_h, wasser_r, h.size, r.size


def auf_raster(m, m_je_px, ziel_m):
    f = m_je_px / ziel_m
    h, w = m.shape
    nh, nw = max(8, int(h * f)), max(8, int(w * f))
    im = Image.fromarray((m * 255).astype(np.uint8)).resize((nw, nh), Image.BILINEAR)
    return (np.asarray(im, dtype=np.float32) / 255.0 > 0.5).astype(np.float32)


def main():
    wasser_h, wasser_r, groesse_h, groesse_r = masken()
    I = auf_raster(wasser_h, M_JE_PX_HEUTE, ARBEIT)
    gh, gw = I.shape
    print('Schwarzplan %dx%d px -> Raster %dx%d (%.1f m je Rasterpunkt)'
          % (groesse_h[0], groesse_h[1], gw, gh, ARBEIT))
    print('Revisiekarte %dx%d px, Wasseranteil %.1f %%'
          % (groesse_r[0], groesse_r[1], 100 * wasser_r.mean()))
    F_I, F_I2 = np.fft.rfft2(I), np.fft.rfft2(I * I)

    beste = []
    for m_je_px in np.arange(1.40, 3.60, 0.01):
        T = auf_raster(wasser_r, m_je_px, ARBEIT)
        n_h, n_w = T.shape
        if n_h >= gh or n_w >= gw:
            continue
        maske = np.ones_like(T)
        N = maske.sum()
        anteil = T.mean()
        if anteil < 0.03 or anteil > 0.9:
            continue
        T0 = T - anteil

        def kk(F, k):
            g = np.zeros(I.shape, dtype=np.float32)
            g[:n_h, :n_w] = k
            return np.fft.irfft2(F * np.conj(np.fft.rfft2(g)), I.shape)

        sI, sI2 = kk(F_I, maske), kk(F_I2, maske)
        nenner = np.sqrt(np.maximum(sI2 - sI * sI / N, 1e-6)) * np.sqrt((T0 ** 2).sum())
        ncc = kk(F_I, T0) / nenner
        i = int(np.argmax(ncc))
        dy, dx = divmod(i, I.shape[1])
        if dx > gw // 2: dx -= gw
        if dy > gh // 2: dy -= gh
        beste.append((float(ncc.flat[i]), float(m_je_px), dx, dy, n_w, n_h))

    beste.sort(reverse=True)
    print('\nbeste sechs:')
    for wv, mpp, dx, dy, nw_, nh_ in beste[:6]:
        print('  NCC %.4f  %.3f m je Bildpunkt  Versatz (%d, %d) Rasterpunkte  Vorlage %dx%d'
              % (wv, mpp, dx, dy, nw_, nh_))

    wv, mpp, dx, dy, nw_, nh_ = beste[0]
    # Versatz in Bildpunkte des Schwarzplans, dann in Zeicheneinheiten
    svg_je_px = MAP_VW / groesse_h[0]
    ox_px = dx * ARBEIT / M_JE_PX_HEUTE
    oy_px = dy * ARBEIT / M_JE_PX_HEUTE
    tx, ty = ox_px * svg_je_px, oy_px * svg_je_px
    s = mpp / M_JE_PX_HEUTE * svg_je_px          # Zeicheneinheiten je Bildpunkt der Revisie
    print('\nErgebnis')
    print('  NCC %.4f' % wv)
    print('  %.3f m je Bildpunkt  ->  Karte deckt %.0f x %.0f m'
          % (mpp, groesse_r[0] * mpp, groesse_r[1] * mpp))
    print('  transform: translate(%.1f %.1f) scale(%.5f)' % (tx, ty, s))
    pickle.dump({'ncc': wv, 'm_je_px': mpp, 'tx': tx, 'ty': ty, 's': s,
                 'w': groesse_r[0], 'h': groesse_r[1]}, open(ZIEL, 'wb'))
    print('\n->', ZIEL)


if __name__ == '__main__':
    main()
