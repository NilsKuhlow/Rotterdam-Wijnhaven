# -*- coding: utf-8 -*-
"""Liest die Vertexpositionen aus dem UNKOMPRIMIERTEN Original-GLB und baut
ein Hoehenraster (DSM) in Modellkoordinaten X/Z. Grundlage fuer die Registrierung
gegen die OSM-Grundrisse."""
import json, struct, sys
import numpy as np

SRC = r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Gefixte_map.glb"
OUT = r"C:\Temp\wij3d\geo\dsm.npz"
CELL = 2.0          # Meter pro Rasterzelle

with open(SRC, 'rb') as f:
    magic, ver, total = struct.unpack('<III', f.read(12))
    clen, ctype = struct.unpack('<II', f.read(8))
    js = json.loads(f.read(clen).decode('utf-8'))
    blen, btype = struct.unpack('<II', f.read(8))
    bin_off = f.tell()
    buf = np.memmap(SRC, dtype=np.uint8, mode='r', offset=bin_off, shape=(blen,))

acc, bvs = js['accessors'], js['bufferViews']
NTYPE = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}

def read_acc(i):
    a = acc[i]
    bv = bvs[a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n, nc = a['count'], NCOMP[a['type']]
    dt = NTYPE[a['componentType']]
    stride = bv.get('byteStride')
    itemsize = np.dtype(dt).itemsize
    if stride and stride != nc * itemsize:
        out = np.empty((n, nc), dtype=dt)
        for k in range(n):
            s = off + k * stride
            out[k] = np.frombuffer(buf[s:s + nc * itemsize].tobytes(), dtype=dt)
        return out
    return np.frombuffer(buf[off:off + n * nc * itemsize].tobytes(), dtype=dt).reshape(n, nc)

pos_accs = []
for m in js['meshes']:
    for p in m['primitives']:
        if 'POSITION' in p['attributes']:
            pos_accs.append(p['attributes']['POSITION'])
print('Primitives mit POSITION:', len(pos_accs))

xs, ys, zs = [], [], []
for k, ai in enumerate(pos_accs):
    v = read_acc(ai)
    xs.append(v[:, 0].astype(np.float32)); ys.append(v[:, 1].astype(np.float32)); zs.append(v[:, 2].astype(np.float32))
    if k % 100 == 0:
        print('  %d/%d' % (k, len(pos_accs)), flush=True)
X = np.concatenate(xs); Y = np.concatenate(ys); Z = np.concatenate(zs)
del xs, ys, zs
print('Vertices:', X.size)
print('X %.2f .. %.2f   Y %.2f .. %.2f   Z %.2f .. %.2f' % (X.min(), X.max(), Y.min(), Y.max(), Z.min(), Z.max()))
q = np.percentile(Y, [1, 5, 10, 25, 50, 75, 90, 99])
print('Y-Perzentile 1/5/10/25/50/75/90/99:', np.round(q, 1))

x0, z0 = float(X.min()), float(Z.min())
nx = int(np.ceil((X.max() - x0) / CELL)) + 1
nz = int(np.ceil((Z.max() - z0) / CELL)) + 1
ix = np.clip(((X - x0) / CELL).astype(np.int32), 0, nx - 1)
iz = np.clip(((Z - z0) / CELL).astype(np.int32), 0, nz - 1)
flat = iz.astype(np.int64) * nx + ix

dsm = np.full(nx * nz, -1e9, dtype=np.float32)
np.maximum.at(dsm, flat, Y)
dtm = np.full(nx * nz, 1e9, dtype=np.float32)
np.minimum.at(dtm, flat, Y)
dsm = dsm.reshape(nz, nx); dtm = dtm.reshape(nz, nx)
leer = dsm < -1e8
dsm[leer] = np.nan; dtm[leer] = np.nan

np.savez_compressed(OUT, dsm=dsm, dtm=dtm, x0=x0, z0=z0, cell=CELL)
print('Raster %dx%d  Zellen belegt: %d  gespeichert: %s' % (nx, nz, int((~leer).sum()), OUT))
