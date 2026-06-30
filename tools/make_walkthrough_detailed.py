# -*- coding: utf-8 -*-
"""Detailliertes (realistisch-leichtes) Walkthrough-Modell fuer die 3D-Ansicht im Browser.
   Gleiche Namenskonvention wie das abstrakte Modell, damit Antippen + Positionen passen:
     building_<N>  -> oeffnet Eintrag N (0..6)
     person_<id>   -> zeigt Interview/Zitat (siehe TOUR_PEOPLE im HTML)
     ground, water, scenery_* -> Kulisse
   Farbige Fassaden mit Fensterbaendern (Stockwerke), Strassen, Wasser, Baeume.
   Nur Vertexfarben -> sehr kleines glb, laedt direkt in der Website.
   Spaeter durch das echte, hochdetaillierte Modell ersetzen (gleiche Namen)."""
import os, math, numpy as np, trimesh

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
os.makedirs(OUT, exist_ok=True)

def rgba(hex_str, a=255):
    h = hex_str.lstrip('#')
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), a]

def col(m, c):
    m.visual.vertex_colors = np.tile(np.array(c, np.uint8), (len(m.vertices), 1))
    return m

def box(sx, sy, sz, pos, c):
    m = trimesh.creation.box(extents=[sx, sy, sz]); m.apply_translation(pos); return col(m, c)

def building(cx, cz, w, d, h, wall, win, name, scene, floor=1.4, roof=None):
    """Stapel aus Wand- und Fensterbaendern -> Stockwerk-Optik. Ein Knoten (antippbar)."""
    parts, y, i = [], 0.0, 0
    while y < h - 0.01:
        seg = min(floor, h - y)
        c = win if (i % 2 == 1) else wall
        parts.append(box(w, seg, d, [cx, y + seg/2, cz], c))
        y += seg; i += 1
    parts.append(box(w*1.02, 0.25, d*1.02, [cx, h+0.12, cz], roof or wall))  # Dachkante
    m = trimesh.util.concatenate(parts)
    scene.add_geometry(m, node_name=name, geom_name=name)

def tree(cx, cz, scene, name):
    t = box(0.35, 1.6, 0.35, [cx, 0.8, cz], rgba('#6b4b33'))
    c = trimesh.creation.icosphere(subdivisions=1, radius=1.15); c.apply_translation([cx, 2.4, cz]); col(c, rgba('#3f7d4f'))
    scene.add_geometry(trimesh.util.concatenate([t, c]), node_name=name, geom_name=name)

def person(cx, cz, scene, name, c=None):
    cap = trimesh.creation.capsule(height=1.1, radius=0.32)
    cap.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1,0,0]))
    cap.apply_translation([cx, 0.95, cz])
    scene.add_geometry(col(cap, c or rgba('#FFED29')), node_name=name, geom_name=name)

scene = trimesh.Scene()

# ── Boden + Wasser + Strassen ──
scene.add_geometry(box(46, 0.4, 46, [0, -0.2, 0], rgba('#9a9a92')), node_name='ground', geom_name='ground')   # Pflaster
scene.add_geometry(box(46, 0.42, 11, [0, -0.18, 19], rgba('#3f6b86')), node_name='water', geom_name='water')   # Hafenbecken
for i, x in enumerate([-15, -4, 7, 18]):
    scene.add_geometry(box(3.4, 0.44, 38, [x, -0.16, -3], rgba('#7c7c76')), node_name='scenery_road_v%d'%i, geom_name='scenery_road_v%d'%i)
for i, z in enumerate([-12, 2]):
    scene.add_geometry(box(40, 0.44, 3.4, [0, -0.16, z], rgba('#7c7c76')), node_name='scenery_road_h%d'%i, geom_name='scenery_road_h%d'%i)

WALL  = {'concrete':rgba('#cdc7ba'), 'brick':rgba('#9a5240'), 'sand':rgba('#d9cdb0'), 'white':rgba('#e9e7e0'), 'dark':rgba('#5a5f66')}
GLASS = {'sky':rgba('#7fa6c4'), 'teal':rgba('#5f93a0'), 'warm':rgba('#caa86a'), 'steel':rgba('#8fa3b4'), 'dark':rgba('#3a4a57')}

# ── Antippbare Hauptbauten (Positionen wie im abstrakten Modell) ──
building(-12, -7, 3.4, 3.4, 15.0, WALL['white'],    GLASS['sky'],  'building_0', scene)   # 0 Witte Huis (heller Turm)
building(  9, -9, 11.0, 6.0,  8.5, WALL['brick'],    GLASS['warm'], 'building_2', scene)   # 2 Markthal (Block)
building(  7,  7, 4.2, 4.2, 18.0, rgba('#b23a2e'),   GLASS['dark'], 'building_3', scene)   # 3 Red Apple (rot)

# ── Kulisse: weitere Tuerme + Bloecke fuer Strassenraum ──
ctx = [
    (-4, -14, 5,5, 11, 'concrete','steel'), (16, 4, 6,4, 14, 'dark','teal'),
    (-14, 8, 4,4, 9, 'sand','warm'), (0, 14, 7,5, 6, 'concrete','sky'),
    (-8, 3, 4.5,4.5, 12, 'brick','warm'), (4, -2, 4,4, 16, 'dark','steel'),
    (18, -10, 5,5, 13, 'concrete','teal'), (-18, -4, 4,5, 10, 'sand','sky'),
    (16, 14, 5,4, 8, 'white','steel'), (-16, 16, 4,4, 7, 'concrete','warm'),
    (10, 2, 3.6,3.6, 17, 'steel' if False else 'dark','sky'),
]
for i, (x,z,w,d,h,wk,gk) in enumerate(ctx):
    building(x, z, w, d, h, WALL[wk], GLASS[gk], 'scenery_b%d'%i, scene)

for i, (x,z) in enumerate([(-9,-3),(2,-6),(13,0),(-13,1),(6,12),(-2,9),(12,9)]):
    tree(x, z, scene, 'scenery_tree%d'%i)

# ── Antippbare Personen ──
person(-3, 2, scene, 'person_kai')
person( 4, 1, scene, 'person_bewohner')

path = os.path.join(OUT, 'walkthrough_detailed.glb')
scene.export(path)
print('wrote', path, os.path.getsize(path), 'bytes')
print('nodes:', [n for n in scene.graph.nodes_geometry])
