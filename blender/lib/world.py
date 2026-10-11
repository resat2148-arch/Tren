"""Außenwelt (Feld, Gleis, Masten, Bäume), Himmel und Tageszeiten.

Koordinaten (für alle Sets gleich):
  Fahrzeugboden innen  z = 0
  Schienenoberkante    z = -1.10
  Gelände              z = -1.25
  Gleisachse           x = 0, Fahrtrichtung Hamburg = -Y
"""
import math

import bpy
from mathutils import Vector

from . import common as c

GROUND_Z = -1.25
RAIL_Z = -1.10


def field_material():
    """Feld mit Saatreihen parallel zum Gleis und großen Flächenwechseln (Raps / Weizen / Wiese)."""
    if 'Feld' in bpy.data.materials:
        return bpy.data.materials['Feld']
    m = bpy.data.materials.new('Feld')
    nt, bsdf = c._principled(m)
    N = nt.nodes
    L = nt.links
    coord = N.new('ShaderNodeTexCoord')
    # Reihen
    wave = N.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'X'
    wave.inputs['Scale'].default_value = 0.9
    wave.inputs['Distortion'].default_value = 1.5
    wave.inputs['Detail'].default_value = 2.0
    L.new(coord.outputs['Object'], wave.inputs['Vector'])
    # große Parzellen
    patch = N.new('ShaderNodeTexVoronoi')
    patch.inputs['Scale'].default_value = 0.012
    patch.feature = 'F1'
    L.new(coord.outputs['Object'], patch.inputs['Vector'])
    ramp_patch = N.new('ShaderNodeValToRGB')
    cr = ramp_patch.color_ramp
    cr.interpolation = 'CONSTANT'
    cr.elements[0].color = (*c.hex_rgb('#4E6B26'), 1)  # Wiese
    cr.elements[1].position = 0.33
    cr.elements[1].color = (*c.hex_rgb('#B39A3A'), 1)  # Weizen
    e = cr.elements.new(0.66)
    e.color = (*c.hex_rgb('#C8B52A'), 1)  # Raps
    L.new(patch.outputs['Color'], ramp_patch.inputs['Fac'])
    # Reihen abdunkeln
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 0.45
    L.new(ramp_patch.outputs['Color'], mix.inputs['A'])
    L.new(wave.outputs['Color'], mix.inputs['B'])
    # feine Unruhe
    noise = N.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 0.6
    noise.inputs['Detail'].default_value = 6
    L.new(coord.outputs['Object'], noise.inputs['Vector'])
    mix2 = N.new('ShaderNodeMix')
    mix2.data_type = 'RGBA'
    mix2.blend_type = 'OVERLAY'
    mix2.inputs['Factor'].default_value = 0.35
    L.new(mix.outputs['Result'], mix2.inputs['A'])
    L.new(noise.outputs['Color'], mix2.inputs['B'])
    L.new(mix2.outputs['Result'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.95
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    L.new(wave.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def build_environment(coll):
    """Gelände, Gleis, Oberleitung, Baumreihen. Alles hängt an ENV_ROOT (für Fahrt animierbar)."""
    root = c.empty('ENV_ROOT', coll=coll, size=1)
    root['env_root'] = True

    c.plane('Gelaende', (900, 900), (0, 0, GROUND_Z), field_material(), coll, parent=root)

    ballast = c.mat('Schotter', '#6E6A64', rough=0.95, bump=1.0, bump_scale=40, noise_color=0.4)
    sleeper = c.mat('Schwelle', '#55514C', rough=0.85, bump=0.3)
    steel = c.mat('Schiene', '#8C8F94', rough=0.35, metal=1.0)
    rust = c.mat('Schiene_Rost', '#5A3E2E', rough=0.8, metal=0.3)
    mast_m = c.mat('Mast', '#7D848C', rough=0.5, metal=0.8)
    wire_m = c.mat('Draht', '#2B2B2B', rough=0.5, metal=0.6)

    length = 900
    c.profile_extrude('Schotterbett', [(-2.6, GROUND_Z), (-1.7, -1.16), (1.7, -1.16), (2.6, GROUND_Z)], length,
                      material=ballast, coll=coll, parent=root, smooth=False)
    for sx in (-0.7175, 0.7175):
        c.box(f'Schiene_{sx}', (0.07, length, 0.1), (sx, 0, RAIL_Z - 0.05), steel, coll, parent=root)
        c.box(f'Schienenfuss_{sx}', (0.15, length, 0.03), (sx, 0, RAIL_Z - 0.115), rust, coll, parent=root)
    # Schwellen als Array
    sl = c.box('Schwellen', (2.6, 0.26, 0.12), (0, -length / 2, -1.19), sleeper, coll, parent=root)
    arr = sl.modifiers.new('Array', 'ARRAY')
    arr.count = int(length / 0.65)
    arr.relative_offset_displace = (0, 0.65 / 0.26, 0)

    # Oberleitungsmasten (rechts der Fahrtrichtung) alle 60 m
    for i in range(-7, 8):
        y = i * 60.0
        c.box(f'Mast_{i}', (0.22, 0.22, 8.2), (3.4, y, GROUND_Z + 4.1), mast_m, coll, parent=root, bevel=0.01)
        c.box(f'Ausleger_{i}', (3.6, 0.08, 0.08), (1.7, y, 4.6), mast_m, coll, parent=root)
        c.cyl(f'Isolator_{i}', 0.05, 0.05, 0.4, (0.1, y, 4.35), wire_m, coll, parent=root, verts=8)
    c.cyl('Fahrdraht', 0.008, 0.008, length, (0, 0, 4.15), wire_m, coll, rot=(math.pi / 2, 0, 0), parent=root,
          verts=6)
    c.cyl('Tragseil', 0.008, 0.008, length, (0, 0, 4.6), wire_m, coll, rot=(math.pi / 2, 0, 0), parent=root,
          verts=6)

    # Baumreihen / Hecken in der Ferne
    leaf = c.mat('Laub', '#2F4A22', rough=0.9, bump=1.2, bump_scale=8, noise_color=0.6)
    leaf_dark = c.mat('Laub_dunkel', '#22361A', rough=0.9, bump=1.2, bump_scale=8, noise_color=0.6)
    bark = c.mat('Rinde', '#3B2E22', rough=0.9)
    rnd = c.seeded(47)
    proto = c.sphere('Baum_Krone', (3.2, 3.2, 3.8), (0, 0, 0), leaf, coll, seg=10, rings=7, parent=root,
                     shape=lambda v: v.__setitem__(2, v.z + 0.15 * math.sin(v.x * 7) * math.cos(v.y * 5)))
    proto2 = c.sphere('Baum_Krone2', (2.4, 2.4, 3.0), (0, 0, 0), leaf_dark, coll, seg=10, rings=7, parent=root,
                      shape=lambda v: v.__setitem__(2, v.z + 0.12 * math.sin(v.x * 9)))
    trunk = c.cyl('Stamm', 0.25, 0.18, 3.0, (0, 0, 0), bark, coll, parent=root, verts=8)
    proto.hide_render = proto2.hide_render = trunk.hide_render = True
    proto.hide_viewport = proto2.hide_viewport = trunk.hide_viewport = True

    def tree(name, x, y, s, kind):
        src = proto if kind else proto2
        crown = c.instance(src, name, (x, y, GROUND_Z + 3.0 * s + 3.0 * s), coll=coll, parent=root)
        crown.scale = (s, s * rnd.uniform(0.85, 1.15), s)
        crown.hide_render = crown.hide_viewport = False
        t = c.instance(trunk, f'{name}_Stamm', (x, y, GROUND_Z + 1.5 * s), coll=coll, parent=root)
        t.scale = (s, s, s)
        t.hide_render = t.hide_viewport = False

    for side, base in ((-1, 70), (1, 95)):
        y = -420.0
        n = 0
        while y < 420:
            x = side * (base + rnd.uniform(-8, 8))
            tree(f'Baum_{side}_{n}', x, y, rnd.uniform(0.9, 1.6), rnd.random() > 0.4)
            y += rnd.uniform(5, 11) if rnd.random() > 0.15 else rnd.uniform(30, 60)
            n += 1
    # Einzelbäume näher am Gleis
    for n in range(14):
        x = rnd.choice((-1, 1)) * rnd.uniform(14, 40)
        y = rnd.uniform(-400, 400)
        tree(f'Solitaer_{n}', x, y, rnd.uniform(1.0, 1.4), True)

    # Bauernhof in der Ferne
    wall = c.mat('Hof_Wand', '#8A5A44', rough=0.9, bump=0.5, bump_scale=20)
    roof = c.mat('Hof_Dach', '#3D3433', rough=0.8)
    for n, (x, y, rot) in enumerate(((-130, -60, 0.2), (-145, -35, 0.2), (160, 120, -0.4))):
        c.box(f'Hof_{n}', (14, 9, 6), (x, y, GROUND_Z + 3), wall, coll, rot=(0, 0, rot), parent=root)
        c.profile_extrude(f'Hof_Dach_{n}', [(-7.6, 0), (0, 4.5), (7.6, 0)], 10, (x, y, GROUND_Z + 6), roof, coll,
                          parent=root, smooth=False).rotation_euler = (0, 0, rot + math.pi / 2)
    return root


# ---------------------------------------------------------------- Himmel / Tageszeit

TIMES = {
    # zenit, horizont, Himmelshelligkeit, Sonnenfarbe, Sonnenstärke, Sonnenhöhe°, Innenlicht-Faktor
    'tag': dict(zenith='#4F7FBF', horizon='#CFE0EE', sky=1.0, sun='#FFF3E0', sun_strength=3.2, sun_elev=38,
                sun_az=120, interior=0.6),
    'nachmittag': dict(zenith='#5A84B8', horizon='#E8DCC4', sky=0.9, sun='#FFE2B8', sun_strength=2.8, sun_elev=22,
                       sun_az=220, interior=0.7),
    'abend': dict(zenith='#2B3C66', horizon='#F09A50', sky=0.55, sun='#FF8A3A', sun_strength=2.2, sun_elev=4,
                  sun_az=260, interior=1.0),
    'nacht': dict(zenith='#0B1530', horizon='#26395C', sky=0.45, sun='#9DB4FF', sun_strength=0.25, sun_elev=35,
                  sun_az=200, interior=1.35),
}


def build_sky(scene=None):
    sc = scene or bpy.context.scene
    world = bpy.data.worlds.new('Himmel')
    sc.world = world
    if bpy.app.version < (5, 0, 0):
        world.use_nodes = True
    nt = world.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new('ShaderNodeOutputWorld')
    bg = N.new('ShaderNodeBackground')
    bg.name = 'SKY_BG'
    coord = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    ramp = N.new('ShaderNodeValToRGB')
    ramp.name = 'SKY_RAMP'
    L.new(coord.outputs['Generated'], sep.inputs['Vector'])
    L.new(sep.outputs['Z'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 0.55
    L.new(ramp.outputs['Color'], bg.inputs['Color'])
    L.new(bg.outputs['Background'], out.inputs['Surface'])

    sun_data = bpy.data.lights.new('Sonne', 'SUN')
    sun_data.angle = math.radians(1.5)
    sun = bpy.data.objects.new('Sonne', sun_data)
    sc.collection.objects.link(sun)
    return world, sun


def apply_time(name, scene=None):
    """Tageszeit setzen: Himmel, Sonne, Innenbeleuchtung (Lichter mit 'interior'), Nachtfenster."""
    sc = scene or bpy.context.scene
    t = TIMES[name]
    world = sc.world
    ramp = world.node_tree.nodes['SKY_RAMP'].color_ramp
    # Generated in der Welt = Blickrichtung, Z = 0 am Horizont
    ramp.elements[0].position = 0.0
    ramp.elements[0].color = (*c.hex_rgb(t['horizon']), 1)
    ramp.elements[1].position = 0.45
    ramp.elements[1].color = (*c.hex_rgb(t['zenith']), 1)
    world.node_tree.nodes['SKY_BG'].inputs['Strength'].default_value = t['sky']
    sun = bpy.data.objects.get('Sonne')
    if sun:
        sun.data.color = c.hex_rgb(t['sun'])
        sun.data.energy = t['sun_strength']
        el, az = math.radians(t['sun_elev']), math.radians(t['sun_az'])
        d = Vector((math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)))
        sun.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    for ob in sc.objects:
        if ob.type == 'LIGHT' and 'interior' in ob:
            ob.data.energy = ob['interior'] * t['interior']
    for m in bpy.data.materials:
        if 'emit_base' in m:
            bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            factor = t['interior'] if m.get('emit_follows_time', 1) else 1
            if m.get('night_only'):
                factor = 1.0 if name == 'nacht' else (0.6 if name == 'abend' else 0.0)
            bsdf.inputs['Emission Strength'].default_value = m['emit_base'] * factor
    return t
