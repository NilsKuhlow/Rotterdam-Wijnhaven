# -*- coding: utf-8 -*-
"""Rechnet fuer die 7 Bauten GPS -> Modellkoordinate und liest die Dachhoehe
aus dem Hoehenraster, damit die Marker ueber dem Gebaeude schweben."""
import numpy as np

KLON, KLAT = 68671.61405376215, 110540.0
LON0, LAT0 = 4.486400, 51.916868          # aus register.py

d = np.load(r"C:\Temp\wij3d\geo\dsm.npz")
dsm, x0, z0, cell = d['dsm'], float(d['x0']), float(d['z0']), float(d['cell'])
nz, nx = dsm.shape

STOPS = [
    ('01', 'witte-huis',       'Witte Huis',       51.91883, 4.49173),
    ('02', 'kubuswoningen',    'Kubuswoningen',    51.92029, 4.49047),
    ('03', 'markthal',         'Markthal',         51.92011, 4.48687),
    ('04', 'red-apple',        'Red Apple',        51.9173,  4.48895),
    ('05', 'wijnhaveneiland',  'Wijnhaveneiland',  51.9166,  4.4876),
    ('06', 'ey-netherlands',   'EY Netherlands',   51.91434, 4.48652),
    ('07', 'casanova',         'CasaNova',         51.91796, 4.48736),
]

def gps_to_model(lat, lon):
    return (lon - LON0) * KLON, (LAT0 - lat) * KLAT

def roof(X, Z, radius_m=28.0):
    """Hoechster Punkt im Umkreis; Naeherung fuer die Dachhoehe."""
    r = int(radius_m / cell)
    cx, cz = int((X - x0) / cell), int((Z - z0) / cell)
    x1, x2 = max(0, cx - r), min(nx, cx + r + 1)
    z1, z2 = max(0, cz - r), min(nz, cz + r + 1)
    w = dsm[z1:z2, x1:x2]
    if w.size == 0 or np.all(np.isnan(w)):
        return None, None
    return float(np.nanmax(w)), float(np.nanpercentile(w, 5))

# Bodenniveau grob: 5. Perzentil ueber das ganze Modell
grund = float(np.nanpercentile(dsm, 2))
print('Bodenniveau (2. Perzentil): %.1f' % grund)
print()
print('%-4s %-17s %9s %9s %8s %8s %8s' % ('Nr', 'Slug', 'X', 'Z', 'Dach', 'Hoehe', 'PinY'))
rows = []
for num, slug, name, lat, lon in STOPS:
    X, Z = gps_to_model(lat, lon)
    top, lo = roof(X, Z)
    h = (top - grund) if top else 0
    pin_y = (top if top else grund) + 18.0          # 18 m Luft ueber dem Dach
    rows.append((num, slug, name, X, pin_y, Z, h))
    print('%-4s %-17s %9.1f %9.1f %8.1f %8.1f %8.1f' % (num, slug, X, Z, top or -1, h, pin_y))

print()
print('// data-position / data-normal fuer <model-viewer>')
for num, slug, name, X, Y, Z, h in rows:
    print('  { num:"%s", slug:"%s", pos:"%.1fm %.1fm %.1fm" },' % (num, slug, X, Y, Z))
