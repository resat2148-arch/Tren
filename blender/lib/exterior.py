"""Der Zug von außen (eigenes Design: silbergrau, Fensterband, Amber-Zierlinie)."""
import math

import bpy

from . import common as c
from .wagon import L, WINDOWS, WINDOW_W

CAR_GAP = 1.2
PITCH = L + CAR_GAP
# Reihenfolge von vorn (-Y, Richtung Hamburg) nach hinten; Wagen 6 steht bei y=0 wie im Innen-Set
TRAIN = [('wagen1', -2), ('wagen7', -1), ('wagen6', 0), ('wagen5', 1)]

PROFILE = [(-1.30, -0.85), (-1.46, -0.6), (-1.485, 0.3), (-1.475, 1.6), (-1.40, 2.3), (-1.15, 2.62),
           (-0.6, 2.75), (0, 2.78), (0.6, 2.75), (1.15, 2.62), (1.40, 2.3), (1.475, 1.6), (1.485, 0.3),
           (1.46, -0.6), (1.30, -0.85)]


def _mats():
    paint = c.mat('Lack', '#D7DBDE', rough=0.28, metal=0.35, coat=1.0)
    skirt = c.mat('Schuerze', '#3A3E44', rough=0.5, metal=0.2)
    band = c.mat('Fensterband', '#10161C', rough=0.05, coat=1.0, emit='#FFD6A0', emit_strength=0.0)
    band['emit_base'] = 2.2
    band['night_only'] = 1
    stripe = c.mat('Zierlinie', '#FF9F1C', rough=0.35, coat=0.6)
    dark = c.mat('Fahrwerk', '#1C1D20', rough=0.7, metal=0.3)
    rubber = c.mat('Faltenbalg', '#232427', rough=0.9)
    door = c.mat('Tuerfuge', '#55595F', rough=0.4)
    head = c.mat('Scheinwerfer', '#FFFFFF', emit='#FFF4DC', emit_strength=25)
    head['emit_base'] = 25
    head['night_only'] = 1
    tail = c.mat('Schlusslicht', '#300000', emit='#FF3B1F', emit_strength=12)
    tail['emit_base'] = 12
    tail['night_only'] = 1
    wind = c.mat('Frontscheibe', '#0B0F14', rough=0.02, coat=1.0, metal=0.4)
    return locals()


def car(coll, name, y0, m, nose=None):
    parts = []
    parts.append(c.profile_extrude(f'{name}_kasten', PROFILE, L + 0.4, (0, y0, 0), m['paint'], coll, closed=True,
                                   cap=True))
    for s in (-1, 1):
        parts.append(c.box(f'{name}_band_{s}', (0.03, L - 1.0, 0.86), (s * 1.488, y0, 1.21), m['band'], coll))
        for wy in WINDOWS:
            for e in (-1, 1):
                parts.append(c.box(f'{name}_steg_{s}_{wy}_{e}', (0.035, 0.18, 0.86),
                                   (s * 1.49, y0 + wy + e * (WINDOW_W / 2 + 0.09), 1.21), m['paint'], coll))
        parts.append(c.box(f'{name}_linie_{s}', (0.03, L + 0.3, 0.07), (s * 1.488, y0, 0.62), m['stripe'], coll))
        parts.append(c.box(f'{name}_schuerze_{s}', (0.04, L - 0.4, 0.42), (s * 1.42, y0, -0.62), m['skirt'], coll))
        for e in (-1, 1):
            dy = y0 + e * (L / 2 - 1.0)
            for dz, h in ((1.15, 0.02),):
                parts.append(c.box(f'{name}_tuer_o_{s}_{e}', (0.02, 0.95, 0.02), (s * 1.49, dy, 1.97), m['door'],
                                   coll))
            for ey in (-1, 1):
                parts.append(c.box(f'{name}_tuer_s_{s}_{e}_{ey}', (0.02, 0.02, 2.6), (s * 1.488, dy + ey * 0.475,
                                                                                    0.68), m['door'], coll))
    # Drehgestelle
    for e in (-1, 1):
        by = y0 + e * (L / 2 - 2.6)
        parts.append(c.box(f'{name}_dg_{e}', (2.3, 2.9, 0.55), (0, by, -0.95), m['dark'], coll, bevel=0.05))
        for wy in (-1.25, 1.25):
            for s in (-1, 1):
                parts.append(c.cyl(f'{name}_rad_{e}_{wy}_{s}', 0.46, 0.46, 0.12, (s * 0.72, by + wy, -0.72 - 0.0),
                                   m['dark'], coll, rot=(0, math.pi / 2, 0), verts=20))
    # Dachaufbauten
    parts.append(c.box(f'{name}_klima', (1.4, 3.2, 0.2), (0, y0 + L / 2 - 3.5, 2.78), m['skirt'], coll, bevel=0.06))
    ob = c.merge(parts, name, coll, origin=(0, y0, 0))
    if nose:
        _nose(coll, name, y0, nose, m)
    return ob


def _nose(coll, name, y0, direction, m):
    """direction -1: Spitze nach -Y (vorn), +1: nach +Y (hinten)."""
    yb = y0 + direction * (L / 2 + 0.2)
    half = 'front' if direction < 0 else 'back'

    def squash(v):
        if v.z < -0.5:
            v.z = -0.5
    parts = [
        c.sphere(f'{name}_nase', (1.47, 6.5, 1.9), (0, yb, 0.95), m['paint'], coll, seg=40, rings=20, half=half,
                 shape=squash),
        c.sphere(f'{name}_scheibe', (1.2, 4.0, 0.9), (0, yb + direction * 1.9, 1.75), m['wind'], coll, seg=32,
                 rings=16, half=half),
        c.box(f'{name}_nase_linie', (2.4, 0.05, 0.07), (0, yb + direction * 1.5, 0.62), m['stripe'], coll),
    ]
    light = m['head'] if direction < 0 else m['tail']
    for s in (-1, 1):
        parts.append(c.box(f'{name}_licht_{s}', (0.32, 0.05, 0.09), (s * 0.78, yb + direction * 4.2, 0.35), light,
                           coll, rot=(0, 0, s * direction * -0.5), bevel=0.02))
    c.merge(parts, f'{name}_nase', coll, origin=(0, yb, 0))


def build_aussen():
    coll = c.make_collection('SET_aussen')
    cams = c.make_collection('CAMS_aussen', coll)
    m = _mats()
    for i, (wid, slot) in enumerate(TRAIN):
        nose = -1 if i == 0 else (1 if i == len(TRAIN) - 1 else None)
        car(coll, f'Zug_{wid}', slot * PITCH, m, nose)
        if i < len(TRAIN) - 1:
            c.box(f'Balg_{wid}', (2.4, CAR_GAP + 0.1, 2.5), (0, slot * PITCH + PITCH / 2, 1.0), m['rubber'], coll)
    c.camera_preset(cams, 'drohne', (-26, 34, 15), (0, -12, 0), 32)
    c.camera_preset(cams, 'gleis_tief', (2.9, -95, -0.55), (0, -40, 0.6), 55)
    c.camera_preset(cams, 'feld_weit', (-70, 18, 0.4), (0, -14, 0.8), 55)
    c.camera_preset(cams, 'fenster_w6', (-4.2, 2.6, 1.0), (-1.4, 0.0, 1.25), 35)
    return coll
