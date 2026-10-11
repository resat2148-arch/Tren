"""Gemeinsame Helfer für alle Blender-Skripte (Blender 4.2+ / 5.x, auch als bpy-Modul)."""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(ROOT, 'assets')


def script_args():
    """Argumente nach '--' (blender -b -P x.py -- a b) bzw. direkt (python x.py a b)."""
    if '--' in sys.argv:
        return sys.argv[sys.argv.index('--') + 1:]
    return sys.argv[1:]


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()


def make_collection(name, parent=None):
    coll = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(coll)
    else:
        parent.children.link(coll)
    return coll


# ---------------------------------------------------------------- Materialien

_MATS = {}


def _principled(m):
    if bpy.app.version < (5, 0, 0):
        m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    return nt, bsdf


def _set(bsdf, name, value):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = value


def hex_rgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    # sRGB -> linear
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def mat(name, color='#808080', rough=0.5, metal=0.0, emit=None, emit_strength=0.0, sss=0.0,
        fabric=0.0, bump=0.0, bump_scale=60.0, coat=0.0, spec=0.5, alpha=1.0, noise_color=0.0):
    """Principled-Material, gecacht nach Name.
    fabric: Sheen + feine Webstruktur, bump: allgemeine Unebenheit, noise_color: leichte Farbvariation."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nt, bsdf = _principled(m)
    rgb = hex_rgb(color) if isinstance(color, str) else color
    _set(bsdf, 'Base Color', (*rgb, 1))
    _set(bsdf, 'Roughness', rough)
    _set(bsdf, 'Metallic', metal)
    _set(bsdf, 'Specular IOR Level', spec)
    if emit:
        e = hex_rgb(emit) if isinstance(emit, str) else emit
        _set(bsdf, 'Emission Color', (*e, 1))
        _set(bsdf, 'Emission Strength', emit_strength)
    if sss:
        _set(bsdf, 'Subsurface Weight', sss)
        _set(bsdf, 'Subsurface Radius', (0.9, 0.35, 0.2))
        _set(bsdf, 'Subsurface Scale', 0.02)
    if coat:
        _set(bsdf, 'Coat Weight', coat)
    if fabric:
        _set(bsdf, 'Sheen Weight', fabric)
        _set(bsdf, 'Sheen Roughness', 0.4)
    if alpha < 1:
        _set(bsdf, 'Alpha', alpha)
        if hasattr(m, 'surface_render_method'):
            m.surface_render_method = 'DITHERED'
    m.diffuse_color = (*rgb, 1)

    if fabric or bump or noise_color:
        coord = nt.nodes.new('ShaderNodeTexCoord')
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = bump_scale if not fabric else 900.0
        noise.inputs['Detail'].default_value = 4.0
        nt.links.new(coord.outputs['Object'], noise.inputs['Vector'])
        if fabric or bump:
            b = nt.nodes.new('ShaderNodeBump')
            b.inputs['Strength'].default_value = max(bump, 0.25 if fabric else 0)
            b.inputs['Distance'].default_value = 0.002
            nt.links.new(noise.outputs['Fac'], b.inputs['Height'])
            nt.links.new(b.outputs['Normal'], bsdf.inputs['Normal'])
        if noise_color:
            n2 = nt.nodes.new('ShaderNodeTexNoise')
            n2.inputs['Scale'].default_value = 3.0
            nt.links.new(coord.outputs['Object'], n2.inputs['Vector'])
            mix = nt.nodes.new('ShaderNodeMix')
            mix.data_type = 'RGBA'
            mix.inputs['Factor'].default_value = noise_color
            mix.inputs['A'].default_value = (*rgb, 1)
            mix.inputs['B'].default_value = (rgb[0] * 0.75, rgb[1] * 0.75, rgb[2] * 0.75, 1)
            nt.links.new(n2.outputs['Fac'], mix.inputs['Factor'])
            mix.inputs['Factor'].default_value = noise_color
            nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    _MATS[name] = m
    return m


def emission_mat(name, color, strength):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    nt, bsdf = _principled(m)
    rgb = hex_rgb(color)
    _set(bsdf, 'Base Color', (0, 0, 0, 1))
    _set(bsdf, 'Emission Color', (*rgb, 1))
    _set(bsdf, 'Emission Strength', strength)
    _set(bsdf, 'Roughness', 0.4)
    m.diffuse_color = (*rgb, 1)
    _MATS[name] = m
    return m


# ---------------------------------------------------------------- Geometrie

def _finish(name, bm, material, coll, loc, rot, parent, smooth, bevel, bevel_seg, subsurf):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if material:
        me.materials.append(material)
    ob.location = loc
    if rot:
        ob.rotation_euler = Euler(rot, 'XYZ')
    if parent:
        ob.parent = parent
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if bevel:
        mod = ob.modifiers.new('Bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = bevel_seg
        mod.limit_method = 'ANGLE'
        mod.harden_normals = False
        if not smooth:
            for p in me.polygons:
                p.use_smooth = True
            _auto_smooth(ob)
    if subsurf:
        mod = ob.modifiers.new('Subsurf', 'SUBSURF')
        mod.levels = subsurf
        mod.render_levels = subsurf
    return ob


def _auto_smooth(ob):
    # Blender 4.1+: "Smooth by Angle" ist ein Modifier; einfacher: Kanten über Winkel markieren
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    for e in bm.edges:
        if e.is_manifold and e.calc_face_angle(0) > math.radians(40):
            e.smooth = False
    bm.to_mesh(me)
    bm.free()


def box(name, size, loc=(0, 0, 0), material=None, coll=None, rot=None, parent=None, bevel=0.0,
        bevel_seg=3, taper=None, subsurf=0, smooth=False):
    """Quader mit Maßen size=(x,y,z), Mittelpunkt loc. taper=(sx,sy) skaliert die Oberseite."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
        if taper and v.co.z > 0:
            v.co.x *= taper[0]
            v.co.y *= taper[1]
    return _finish(name, bm, material, coll, loc, rot, parent, smooth, bevel, bevel_seg, subsurf)


def cyl(name, r1, r2, depth, loc=(0, 0, 0), material=None, coll=None, rot=None, parent=None, verts=24,
        bevel=0.0, smooth=True, subsurf=0, cap=True):
    """Kegelstumpf entlang Z, r1 unten, r2 oben, Mittelpunkt loc."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=verts, radius1=r1, radius2=r2, depth=depth)
    return _finish(name, bm, material, coll, loc, rot, parent, smooth, bevel, 2, subsurf)


def sphere(name, radii, loc=(0, 0, 0), material=None, coll=None, rot=None, parent=None, seg=32, rings=16,
           half=None, subsurf=0, shape=None, keep=None, solidify=0.0):
    """Ellipsoid. half='top'/'bottom'/'front'/'back' behält nur eine Hälfte, keep(co) ein beliebiges Stück
    (Einheitskugel-Koordinaten). shape(v) verformt Vertices. solidify gibt Schalen eine Dicke."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    if half or keep:
        kill = []
        for v in bm.verts:
            c = v.co
            if (half == 'top' and c.z < -1e-4) or (half == 'bottom' and c.z > 1e-4) or \
               (half == 'front' and c.y > 1e-4) or (half == 'back' and c.y < -1e-4) or (keep and not keep(c)):
                kill.append(v)
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
    for v in bm.verts:
        if shape:
            shape(v.co)
        v.co.x *= radii[0]
        v.co.y *= radii[1]
        v.co.z *= radii[2]
    ob = _finish(name, bm, material, coll, loc, rot, parent, True, 0, 0, subsurf)
    if solidify:
        mod = ob.modifiers.new('Dicke', 'SOLIDIFY')
        mod.thickness = solidify
    return ob


def loft(name, sections, loc=(0, 0, 0), material=None, coll=None, rot=None, parent=None, n=24, power=2.2,
         subsurf=1, cap=True):
    """Glatter Körper aus Querschnitten [(z, rx, ry[, cx, cy]), ...] (Superellipsen, von oben nach unten egal)."""
    bm = bmesh.new()
    rings = []
    for sec in sections:
        z, rx, ry = sec[:3]
        cx, cy = (sec[3], sec[4]) if len(sec) > 3 else (0.0, 0.0)
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            ca, sa = math.cos(a), math.sin(a)
            x = rx * math.copysign(abs(ca) ** (2 / power), ca)
            y = ry * math.copysign(abs(sa) ** (2 / power), sa)
            ring.append(bm.verts.new((cx + x, cy + y, z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    if cap:
        for ring, nxt in ((rings[0], rings[1]), (rings[-1], rings[-2])):
            cz = ring[0].co.z
            dz = cz - nxt[0].co.z
            ctr = sum((v.co for v in ring), Vector()) / n
            # gewölbter Deckel
            inner = [bm.verts.new(ctr + (v.co - ctr) * 0.6 + Vector((0, 0, dz * 0.35))) for v in ring]
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((ring[i], ring[j], inner[j], inner[i]))
            tip = bm.verts.new(ctr + Vector((0, 0, dz * 0.5)))
            for i in range(n):
                bm.faces.new((inner[i], inner[(i + 1) % n], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, material, coll, loc, rot, parent, True, 0, 0, subsurf)


def torus(name, major, minor, loc=(0, 0, 0), material=None, coll=None, rot=None, parent=None, seg=32, mseg=10,
          scale=(1, 1, 1)):
    bm = bmesh.new()
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(mseg):
            b = 2 * math.pi * j / mseg
            r = major + minor * math.cos(b)
            bm.verts.new((r * math.cos(a) * scale[0], r * math.sin(a) * scale[1], minor * math.sin(b) * scale[2]))
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(mseg):
            a = i * mseg + j
            b = ((i + 1) % seg) * mseg + j
            c = ((i + 1) % seg) * mseg + (j + 1) % mseg
            d = i * mseg + (j + 1) % mseg
            bm.faces.new((bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]))
    return _finish(name, bm, material, coll, loc, rot, parent, True, 0, 0, 0)


def profile_extrude(name, profile, length, loc=(0, 0, 0), material=None, coll=None, parent=None, smooth=True,
                    closed=False, cap=False):
    """Profil in der XZ-Ebene entlang Y extrudieren (Länge zentriert)."""
    bm = bmesh.new()
    a = [bm.verts.new((x, -length / 2, z)) for x, z in profile]
    b = [bm.verts.new((x, length / 2, z)) for x, z in profile]
    n = len(profile)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap and closed:
        bm.faces.new(list(reversed(a)))
        bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(name, bm, material, coll, loc, None, parent, smooth, 0, 0, 0)


def plane(name, size, loc=(0, 0, 0), material=None, coll=None, rot=None, parent=None):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
    return _finish(name, bm, material, coll, loc, rot, parent, False, 0, 0, 0)


def text(name, body, size, loc=(0, 0, 0), material=None, coll=None, rot=(math.pi / 2, 0, 0), align='CENTER',
         extrude=0.0, parent=None):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = 'CENTER'
    cu.extrude = extrude
    ob = bpy.data.objects.new(name, cu)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if material:
        cu.materials.append(material)
    ob.location = loc
    ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), coll=None, parent=None, size=0.1, kind='PLAIN_AXES'):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    (coll or bpy.context.scene.collection).objects.link(ob)
    if parent:
        ob.parent = parent
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def mark(coll, mid, loc, facing_deg=0.0, kind='seat'):
    """Regiemarke: Position für Figuren. facing_deg 0 = Blick nach -Y (Fahrtrichtung)."""
    ob = empty(f'MARK_{mid}', loc, (0, 0, math.radians(facing_deg)), coll, size=0.25, kind='SINGLE_ARROW')
    ob['mark'] = mid
    ob['kind'] = kind
    return ob


def camera_preset(coll, name, loc, target, lens=28):
    cam = bpy.data.cameras.new(f'CAM_{name}')
    cam.lens = lens
    ob = bpy.data.objects.new(f'CAM_{name}', cam)
    coll.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    ob['campreset'] = name
    ob['target'] = list(target)
    return ob


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def instance(src, name, loc, rot=(0, 0, 0), coll=None, parent=None):
    """Leichte Kopie (gleiches Mesh) eines Objekts samt Kindern."""
    ob = src.copy()
    ob.name = name
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.parent = parent
    for ch in src.children:
        c = instance(ch, f'{name}.{ch.name}', ch.location.copy(), ch.rotation_euler.copy(), coll, ob)
        c.scale = ch.scale.copy()
    return ob


def merge(objs, name, coll=None, origin=(0, 0, 0), keep=False):
    """Objekte (inkl. Modifier) zu einem Mesh backen. Ergebnis-Ursprung = origin (Weltkoordinaten)."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    mats = []
    shift = Matrix.Translation(-Vector(origin))
    for o in objs:
        if o.type not in ('MESH', 'FONT', 'CURVE'):
            continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(shift @ o.matrix_world)
        remap = []
        for m in me.materials:
            if m not in mats:
                mats.append(m)
            remap.append(mats.index(m))
        for p in me.polygons:
            p.material_index = remap[p.material_index] if remap else 0
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new(name)
    bm.to_mesh(out)
    bm.free()
    for m in mats:
        out.materials.append(m)
    ob = bpy.data.objects.new(name, out)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = origin
    if not keep:
        for o in objs:
            bpy.data.objects.remove(o, do_unlink=True)
    return ob


def linked_copy(src, name, loc, rot=(0, 0, 0), coll=None, parent=None):
    """Neues Objekt mit demselben Mesh (spart Speicher, z. B. für Sitzreihen)."""
    ob = bpy.data.objects.new(name, src.data)
    (coll or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    return ob


# ---------------------------------------------------------------- Render

def eevee_id():
    items = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    return 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in items else 'BLENDER_EEVEE'


QUALITY = {
    # Vorschau hier auf CPU, final auf dem eigenen Rechner mit Grafikkarte
    'draft': dict(res=(360, 640), samples=6, raytrace=False, blur=False),
    'preview': dict(res=(540, 960), samples=12, raytrace=False, blur=False),
    'final': dict(res=(1080, 1920), samples=64, raytrace=True, blur=True),
}


def setup_render(scene=None, quality='preview', fps=30):
    sc = scene or bpy.context.scene
    q = QUALITY[quality]
    sc.render.engine = eevee_id()
    sc.render.resolution_x, sc.render.resolution_y = q['res']
    sc.render.resolution_percentage = 100
    sc.render.fps = fps
    ee = sc.eevee
    ee.taa_render_samples = q['samples']
    if hasattr(ee, 'use_raytracing'):
        ee.use_raytracing = q['raytrace']
        if q['raytrace'] and hasattr(ee, 'use_fast_gi'):
            ee.use_fast_gi = True
    if hasattr(ee, 'use_shadows'):
        ee.use_shadows = True
    if hasattr(ee, 'shadow_resolution_scale'):
        ee.shadow_resolution_scale = 1.0 if quality == 'final' else 0.5
    sc.render.use_motion_blur = q['blur']
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 90
    return sc


def save(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)


def append_collection(path, name):
    """Sammlung aus einer .blend anhängen (Kopie) und in die Szene hängen."""
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        if name not in src.collections:
            raise RuntimeError(f'{name} nicht in {path} (vorhanden: {list(src.collections)})')
        dst.collections = [name]
    coll = dst.collections[0]
    bpy.context.scene.collection.children.link(coll)
    return coll


def seeded(seed):
    return random.Random(seed)
