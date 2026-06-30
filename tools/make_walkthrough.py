# -*- coding: utf-8 -*-
"""Beispiel-Walkthrough-Modell (glb) fuer die 3D-Ansicht.
   Namenskonvention der antippbaren Objekte:
     building_<N>  -> oeffnet Eintrag N (0..6)
     person_<id>   -> zeigt Interview/Zitat zu <id> (siehe TOUR_PEOPLE im HTML)
   Alles andere (ground, scenery_*) ist nur Kulisse.
   Wird spaeter durch das selbst gebaute Modell ersetzt (gleiche Namenskonvention)."""
import os, math, numpy as np, trimesh

OUT = r'C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output\Rotterdam-Wijnhaven\models'
os.makedirs(OUT, exist_ok=True)

INK    = [26, 26, 26, 255]
PAPER2 = [235, 235, 235, 255]
GREY   = [200, 200, 200, 255]
YELLOW = [255, 237, 41, 255]

def col(m, rgba):
    m.visual.vertex_colors = np.tile(np.array(rgba, np.uint8), (len(m.vertices), 1))
    return m

def box(sx, sy, sz, pos, rgba):
    m = trimesh.creation.box(extents=[sx, sy, sz])
    m.apply_translation(pos)
    return col(m, rgba)

def person(pos, rgba=YELLOW):
    # einzelner Mesh-Koerper (Kapsel) damit der Klick eindeutig ist
    c = trimesh.creation.capsule(height=1.1, radius=0.32)         # Achse entlang Z
    c.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0]))  # aufrecht (Y)
    c.apply_translation([pos[0], 0.95, pos[2]])
    return col(c, rgba)

scene = trimesh.Scene()
def add(mesh, name): scene.add_geometry(mesh, node_name=name, geom_name=name)

# Boden
add(box(46, 0.4, 46, [0, -0.2, 0], PAPER2), 'ground')

# Antippbare Gebaeude (Index = Eintrag)
add(box(3.2, 13, 3.2, [-12, 6.5, -7],  INK), 'building_0')   # Witte Huis (schlanker Turm)
add(box(11, 7.5, 6,   [9, 3.75, -9],   INK), 'building_2')   # Markthal (Block)
add(box(4, 17, 4,     [7, 8.5, 7],     INK), 'building_3')   # Red Apple (Turm)

# Kulisse (nicht klickbar)
add(box(5, 4, 5,   [-4, 2, -14], GREY), 'scenery_a')
add(box(6, 6, 4,   [16, 3, 4],   GREY), 'scenery_b')
add(box(4, 9, 4,   [-14, 4.5, 8], GREY), 'scenery_c')
add(box(7, 3, 5,   [0, 1.5, 14], GREY), 'scenery_d')

# Antippbare Personen (Zitat/Interview)
add(person([-3, 0, 2]), 'person_kai')
add(person([4, 0, 1]),  'person_bewohner')

path = os.path.join(OUT, 'walkthrough.glb')
scene.export(path)
print('wrote', path, os.path.getsize(path), 'bytes')
print('nodes:', [n for n in scene.graph.nodes_geometry])
