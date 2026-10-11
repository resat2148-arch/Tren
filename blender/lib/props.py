"""Requisiten: Sitze, Tische, Anzeigen, Gepäck, Kleinkram. Jede Funktion liefert ein gebackenes Mesh-Objekt
(Ursprung am Boden bzw. Auflagepunkt), das per linked_copy vielfach platziert werden kann."""
import math

import bpy

from . import common as c

PLASTIC_GREY = '#B9BCBF'
DARK_FRAME = '#2D3034'


def seat_unit(name, fabric, accent, coll, n=2, width=0.5, airline=True, shell='#C9CCCF', recline=0.17):
    """n Sitze nebeneinander, Blick nach -Y. Ursprung: Boden unter Sitzkissen-Mitte."""
    parts = []
    shell_m = c.mat(f'Sitzschale_{shell}', shell, rough=0.45)
    frame = c.mat('Sitzgestell', DARK_FRAME, rough=0.5, metal=0.6)
    arm_m = c.mat('Armlehne', '#3A3D42', rough=0.55)
    tray_m = c.mat('Klapptisch', '#5B5F66', rough=0.5)
    for i in range(n):
        x = (i - (n - 1) / 2) * width
        parts.append(c.box(f'{name}_kissen{i}', (width - 0.04, 0.50, 0.13), (x, 0, 0.415), fabric, coll,
                           bevel=0.045, bevel_seg=3, taper=(0.98, 0.96)))
        parts.append(c.box(f'{name}_lehne{i}', (width - 0.05, 0.14, 0.76), (x, 0.31, 0.87), fabric, coll,
                           rot=(-recline, 0, 0), bevel=0.055, bevel_seg=3, taper=(0.9, 0.8)))
        parts.append(c.box(f'{name}_kopf{i}', (width * 0.66, 0.05, 0.18), (x, 0.262, 1.16), accent, coll,
                           rot=(-recline, 0, 0), bevel=0.02))
        parts.append(c.box(f'{name}_schale{i}', (width - 0.03, 0.035, 0.80), (x, 0.395, 0.86), shell_m, coll,
                           rot=(-recline, 0, 0), bevel=0.015))
        if airline:
            parts.append(c.box(f'{name}_tray{i}', (width * 0.72, 0.02, 0.26), (x, 0.42, 0.90), tray_m, coll,
                               rot=(-recline, 0, 0), bevel=0.008))
    for k in range(n + 1):
        xa = (k - n / 2) * width
        parts.append(c.box(f'{name}_arm{k}', (0.055, 0.40, 0.05), (xa, 0.0, 0.67), arm_m, coll, bevel=0.02))
        parts.append(c.box(f'{name}_armstuetze{k}', (0.04, 0.06, 0.19), (xa, 0.15, 0.575), arm_m, coll))
    parts.append(c.box(f'{name}_rahmen', (n * width - 0.08, 0.42, 0.06), (0, 0.02, 0.33), frame, coll))
    for sx in (-1, 1):
        parts.append(c.box(f'{name}_fuss{sx}', (0.08, 0.32, 0.31), (sx * (n * width / 2 - 0.16), 0.05, 0.155),
                           frame, coll))
    return c.merge(parts, name, coll)


def table(name, coll, w=0.96, d=0.74, top='#B9AE9C'):
    """Wandtisch, Ursprung am Boden unter Tischmitte, Bein am +X-Ende (Gangseite)."""
    top_m = c.mat(f'Tisch_{top}', top, rough=0.35, coat=0.3)
    edge = c.mat('Tischkante', '#3A3D42', rough=0.5)
    frame = c.mat('Sitzgestell', DARK_FRAME, rough=0.5, metal=0.6)
    parts = [
        c.box(f'{name}_platte', (w, d, 0.03), (0, 0, 0.745), top_m, coll, bevel=0.01),
        c.box(f'{name}_kante', (w + 0.012, d + 0.012, 0.022), (0, 0, 0.722), edge, coll, bevel=0.008),
        c.cyl(f'{name}_bein', 0.028, 0.028, 0.71, (w / 2 - 0.13, 0, 0.355), frame, coll, verts=16),
        c.cyl(f'{name}_fussplatte', 0.12, 0.12, 0.012, (w / 2 - 0.13, 0, 0.006), frame, coll, verts=24),
        c.box(f'{name}_wandhalter', (0.06, d * 0.6, 0.05), (-w / 2 + 0.03, 0, 0.69), frame, coll),
    ]
    return c.merge(parts, name, coll)


def socket(name, coll):
    white = c.mat('Steckdose', '#E8E6E1', rough=0.4)
    hole = c.mat('Steckdose_loch', '#1A1A1A', rough=0.6)
    amber = c.emission_mat('Steckdose_led', '#FF9F1C', 3.0)
    parts = [c.box(f'{name}_platte', (0.09, 0.02, 0.07), (0, 0, 0), white, coll, bevel=0.006)]
    for dx in (-0.015, 0.015):
        parts.append(c.cyl(f'{name}_loch{dx}', 0.004, 0.004, 0.005, (dx, -0.011, 0), hole, coll,
                           rot=(math.pi / 2, 0, 0), verts=8))
    parts.append(c.box(f'{name}_led', (0.008, 0.004, 0.004), (0.035, -0.011, 0.025), amber, coll))
    return c.merge(parts, name, coll)


def pretzel(name, coll):
    dough = c.mat('Brezel', '#7A3E14', rough=0.35, coat=0.6, bump=0.4, bump_scale=120, noise_color=0.5)
    parts = [
        c.torus(f'{name}_ring', 0.055, 0.014, (0, 0, 0.014), dough, coll, scale=(1, 0.82, 1), seg=28, mseg=10),
    ]
    for a in (0.6, -0.6):
        parts.append(c.cyl(f'{name}_arm{a}', 0.012, 0.012, 0.085, (a * 0.03, -0.012, 0.016), dough, coll,
                           rot=(math.pi / 2, 0, a), verts=10))
    parts.append(c.sphere(f'{name}_knoten', (0.018, 0.014, 0.014), (0, 0.012, 0.018), dough, coll, seg=12,
                          rings=8))
    return c.merge(parts, name, coll)


def cup(name, coll):
    paper = c.mat('Becher', '#EDEAE4', rough=0.6)
    sleeve = c.mat('Becher_band', '#C9731A', rough=0.7, fabric=0.2)
    lid = c.mat('Becher_deckel', '#26282B', rough=0.4)
    parts = [
        c.cyl(f'{name}_k', 0.03, 0.04, 0.11, (0, 0, 0.055), paper, coll, verts=24),
        c.cyl(f'{name}_b', 0.0365, 0.0405, 0.045, (0, 0, 0.06), sleeve, coll, verts=24),
        c.cyl(f'{name}_d', 0.042, 0.04, 0.012, (0, 0, 0.116), lid, coll, verts=24),
    ]
    return c.merge(parts, name, coll)


def laptop(name, coll, open_deg=105):
    alu = c.mat('Alu', '#A7ABB0', rough=0.3, metal=0.9)
    keys = c.mat('Tasten', '#1E1F22', rough=0.6)
    screen = c.mat('Bildschirm', '#0B0F14', rough=0.15, emit='#7FA6D9', emit_strength=1.2)
    screen['emit_base'] = 1.2
    screen['emit_follows_time'] = 0
    a = math.radians(open_deg)
    parts = [
        c.box(f'{name}_basis', (0.32, 0.22, 0.014), (0, 0, 0.007), alu, coll, bevel=0.004),
        c.box(f'{name}_tasten', (0.28, 0.1, 0.002), (0, -0.01, 0.0145), keys, coll),
        c.box(f'{name}_deckel', (0.32, 0.008, 0.21), (0, 0.11 + 0.105 * math.cos(a) * -1, 0.105 * math.sin(a)),
              alu, coll, rot=(-(a - math.pi / 2), 0, 0), bevel=0.003),
    ]
    disp = c.box(f'{name}_display', (0.29, 0.002, 0.18), (0, 0.11 - 0.105 * math.cos(a) - 0.005, 0.105 * math.sin(a)),
                 screen, coll, rot=(-(a - math.pi / 2), 0, 0))
    parts.append(disp)
    return c.merge(parts, name, coll)


def phone(name, coll):
    body = c.mat('Handy', '#16171A', rough=0.25, coat=0.5)
    screen = c.mat('Handy_screen', '#0A0D12', rough=0.1, emit='#9CC2F0', emit_strength=1.5)
    screen['emit_base'] = 1.5
    screen['emit_follows_time'] = 0
    parts = [
        c.box(f'{name}_k', (0.072, 0.15, 0.008), (0, 0, 0), body, coll, bevel=0.006),
        c.box(f'{name}_s', (0.064, 0.138, 0.001), (0, 0, 0.0045), screen, coll),
    ]
    return c.merge(parts, name, coll)


def card100(name, coll):
    """Neutrale Jahreskarte – bewusst ohne Bahn-Logo."""
    plastic = c.mat('Karte', '#C8CCD0', rough=0.25, metal=0.4, coat=0.8)
    ink = c.mat('Karte_schrift', '#1B1D20', rough=0.4)
    stripe = c.mat('Karte_streifen', '#FF9F1C', rough=0.4)
    parts = [
        c.box(f'{name}_k', (0.086, 0.002, 0.054), (0, 0, 0), plastic, coll, bevel=0.002),
        c.box(f'{name}_st', (0.086, 0.0025, 0.008), (0, 0, -0.018), stripe, coll),
        c.text(f'{name}_t', '100', 0.026, (0.01, -0.0015, 0.004), ink, coll),
    ]
    return c.merge(parts, name, coll)


def suitcase(name, coll, color, size=(0.42, 0.26, 0.6)):
    shell = c.mat(f'Koffer_{color}', color, rough=0.35, coat=0.3)
    dark = c.mat('Koffer_griff', '#1E1F22', rough=0.6)
    parts = [
        c.box(f'{name}_k', size, (0, 0, size[2] / 2), shell, coll, bevel=0.035, bevel_seg=3),
        c.box(f'{name}_g', (0.14, 0.03, 0.03), (0, 0, size[2] + 0.02), dark, coll, bevel=0.01),
    ]
    for dx in (-1, 1):
        parts.append(c.box(f'{name}_r{dx}', (0.012, size[1] + 0.006, size[2] * 0.92), (dx * size[0] * 0.25, 0,
                                                                                    size[2] / 2), shell, coll,
                           bevel=0.004))
    return c.merge(parts, name, coll)


def bag(name, coll, color, size=(0.45, 0.28, 0.25)):
    fab = c.mat(f'Tasche_{color}', color, rough=0.8, fabric=0.5)
    strap = c.mat('Gurt', '#202124', rough=0.7)
    parts = [
        c.sphere(f'{name}_k', (size[0] / 2, size[1] / 2, size[2] / 2), (0, 0, size[2] / 2), fab, coll, seg=16,
                 rings=10, shape=lambda v: v.__setitem__(2, max(v.z, -0.75))),
        c.torus(f'{name}_g', size[0] * 0.25, 0.01, (0, 0, size[2] * 0.95), strap, coll, rot=(math.pi / 2, 0, 0),
                seg=16, mseg=6, scale=(1, 0.6, 1)),
    ]
    return c.merge(parts, name, coll)


def led_display(name, coll, width=1.0):
    """Fahrgastinfo-Anzeige (eigenes Design). Text separat als DISPLAY_TEXT, wird pro Shot gesetzt."""
    housing = c.mat('Anzeige_gehaeuse', '#141619', rough=0.3, coat=0.5)
    glass = c.mat('Anzeige_grund', '#07090C', rough=0.15)
    parts = [
        c.box(f'{name}_g', (width, 0.07, 0.2), (0, 0, 0), housing, coll, bevel=0.012),
        c.box(f'{name}_s', (width - 0.06, 0.005, 0.14), (0, -0.036, 0), glass, coll),
    ]
    return c.merge(parts, name, coll)


def led_material():
    m = c.mat('LED_amber', '#000000', rough=0.4, emit='#FF9F1C', emit_strength=6.0)
    m['emit_base'] = 6.0
    m['emit_follows_time'] = 0
    return m


def cable(name, coll, points, radius=0.004, color='#E6E4DE'):
    """Ladekabel als Kurve durch Punkte."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    sp = cu.splines.new('NURBS')
    sp.points.add(len(points) - 1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1)
    sp.use_endpoint_u = True
    sp.order_u = 3
    ob = bpy.data.objects.new(name, cu)
    coll.objects.link(ob)
    cu.materials.append(c.mat(f'Kabel_{color}', color, rough=0.5))
    return ob
