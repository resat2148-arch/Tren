"""Figuren: Gelenk-Hierarchie aus Empties (robust, ohne Armature), Körperteile daran gehängt.
Gesicht mit beweglichen Augen, Lidern, Brauen und Mund-Shape-Keys.

Konvention: Figur blickt nach -Y, links = +X. Wurzel (Root) steht am Boden.
Gelenke tragen die Custom-Property "joint", die Wurzel "char".
"""
import math
import os

import bpy
from mathutils import Vector

from . import common as c

# Gelenke: name -> (parent, Position relativ zum Parent)
def skeleton(spec):
    sh = spec.get('shoulder', 0.2)
    hip = spec.get('hip', 0.09)
    return [
        ('hips', None, (0, 0, 0.95)),
        ('spine', 'hips', (0, 0, 0.10)),
        ('chest', 'spine', (0, 0, 0.17)),
        ('neck', 'chest', (0, 0, 0.25)),
        ('head', 'neck', (0, 0, 0.035)),
        ('face', 'head', (0, -0.11, 0.12)),
        ('eye.L', 'head', (0.036, -0.088, 0.135)),
        ('eye.R', 'head', (-0.036, -0.088, 0.135)),
        ('lid.L', 'head', (0.036, -0.088, 0.135)),
        ('lid.R', 'head', (-0.036, -0.088, 0.135)),
        ('brow.L', 'head', (0.038, -0.101, 0.168)),
        ('brow.R', 'head', (-0.038, -0.101, 0.168)),
        ('upper_arm.L', 'chest', (sh, 0, 0.165)),
        ('forearm.L', 'upper_arm.L', (0, 0, -0.28)),
        ('hand.L', 'forearm.L', (0, 0, -0.255)),
        ('upper_arm.R', 'chest', (-sh, 0, 0.165)),
        ('forearm.R', 'upper_arm.R', (0, 0, -0.28)),
        ('hand.R', 'forearm.R', (0, 0, -0.255)),
        ('thigh.L', 'hips', (hip, 0, -0.03)),
        ('shin.L', 'thigh.L', (0, 0, -0.43)),
        ('foot.L', 'shin.L', (0, 0, -0.43)),
        ('thigh.R', 'hips', (-hip, 0, -0.03)),
        ('shin.R', 'thigh.R', (0, 0, -0.43)),
        ('foot.R', 'shin.R', (0, 0, -0.43)),
    ]


class Builder:
    def __init__(self, cid, spec):
        self.cid, self.spec = cid, spec
        self.coll = c.make_collection(f'CHR_{cid}')
        self.root = c.empty(cid, coll=self.coll, size=0.3, kind='ARROWS')
        self.root['char'] = cid
        self.root['display_name'] = spec.get('name', cid)
        self.j = {}
        for name, parent, loc in skeleton(spec):
            e = c.empty(f'{cid}.{name}', loc, coll=self.coll, parent=self.j.get(parent, self.root), size=0.05)
            e.rotation_mode = 'XYZ'
            e['joint'] = name
            self.j[name] = e
        s = spec
        self.skin = c.mat(f'Haut_{cid}', s['skin'], rough=0.5, sss=0.12)
        self.top = c.mat(f'Oberteil_{cid}', s['top']['color'], rough=0.85, fabric=0.5)
        self.inner = c.mat(f'Innen_{cid}', s['top'].get('inner', '#E9E6E0'), rough=0.8, fabric=0.4)
        self.pants = c.mat(f'Hose_{cid}', s['pants'], rough=0.85, fabric=0.4)
        self.shoes = c.mat(f'Schuhe_{cid}', s['shoes'], rough=0.45, coat=0.2)
        self.sole = c.mat('Sohle', '#E6E3DC' if s.get('sneakers') else '#1A1A1B', rough=0.7)
        self.hair = c.mat(f'Haar_{cid}', s['hair']['color'], rough=0.55, bump=0.5, bump_scale=260, spec=0.6)
        self.brow = c.mat(f'Braue_{cid}', s.get('brow', s['hair']['color']), rough=0.7)
        self.eyewhite = c.mat('Augapfel', '#F2EFEA', rough=0.08, sss=0.05)
        self.iris = c.mat(f'Iris_{cid}', s.get('eyes', '#4B3A2A'), rough=0.1, coat=1.0)
        self.pupil = c.mat('Pupille', '#050505', rough=0.05, coat=1.0)
        self.mouth = c.mat('Mund', '#4A1518', rough=0.4)
        self.teeth = c.mat('Zaehne', '#EEE9DF', rough=0.3)
        self.accent = c.mat(f'Akzent_{cid}', s['top'].get('accent', '#FF9F1C'), rough=0.5)

    def part(self, kind, joint, name, *args, **kw):
        """Teil am Gelenk erzeugen; loc ist relativ zum Gelenk (Ruhelage)."""
        loc = Vector(kw.pop('loc', (0, 0, 0)))
        fn = {'box': c.box, 'cyl': c.cyl, 'sphere': c.sphere, 'torus': c.torus, 'loft': c.loft}[kind]
        ob = fn(f'{self.cid}.{name}', *args, loc=loc, coll=self.coll, parent=self.j[joint], **kw)
        return ob

    # -------------------------------------------------------------- Körper
    def body(self):
        s = self.spec
        sh, hip = s.get('shoulder', 0.2), s.get('hip', 0.09)
        belly = s.get('belly', 0.0)
        bust = s.get('chest', 0.0)
        w = sh / 0.2  # Schulterbreite skaliert den Oberkörper
        long_sleeve = s['top'].get('sleeves', 'long') == 'long'
        # Becken/Hose (am Hüftgelenk)
        hw = hip / 0.09
        self.part('loft', 'hips', 'becken', [(-0.14, 0.12 * hw, 0.09), (-0.07, 0.16 * hw, 0.108),
                                              (0.02, 0.165 * hw, 0.112 + belly * 0.4), (0.09, 0.155 * hw + belly * 0.3,
                                                                                         0.108 + belly * 0.7, 0,
                                                                                         -belly * 0.4)],
                  material=self.pants, n=24, power=2.4)
        # Rumpf als ein Stück (an der Wirbelsäule), Querschnitte relativ zum Gelenk (z=1.05)
        self.part('loft', 'spine', 'rumpf', [
            (-0.05, 0.150 * hw + belly * 0.3, 0.105 + belly * 0.7, 0, -belly * 0.45),
            (0.05, 0.150 * w + belly * 0.6, 0.11 + belly, 0, -belly * 0.6),
            (0.16, 0.165 * w + belly * 0.3, 0.118 + bust + belly * 0.5, 0, -(bust + belly) * 0.4),
            (0.26, 0.180 * w, 0.122 + bust * 0.8, 0, -bust * 0.4),
            (0.34, 0.182 * w, 0.112, 0, 0.0),
            (0.395, 0.150 * w, 0.090, 0, 0.005),
            (0.43, 0.075, 0.062, 0, 0.008),
        ], material=self.top, n=28, power=2.3)
        for side, x in (('L', sh - 0.015), ('R', -sh + 0.015)):
            self.part('sphere', 'chest', f'schulter.{side}', (0.058, 0.062, 0.056), material=self.top,
                      loc=(x * 0.96, 0.0, 0.15), seg=18, rings=10)
        self.part('cyl', 'neck', 'hals', 0.048, 0.052, 0.12, material=self.skin, loc=(0, 0.006, 0.0))
        for side in ('L', 'R'):
            sleeve = self.top if long_sleeve else self.skin
            self.part('loft', f'upper_arm.{side}', 'oberarm', [(0.035, 0.058, 0.06), (-0.06, 0.056, 0.058),
                                                                (-0.2, 0.047, 0.049), (-0.29, 0.044, 0.046)],
                      material=self.top, n=18)
            self.part('loft', f'forearm.{side}', 'unterarm', [(0.03, 0.045, 0.047), (-0.07, 0.046, 0.046),
                                                               (-0.2, 0.036, 0.033), (-0.25, 0.034, 0.03)],
                      material=sleeve, n=18)
            if long_sleeve:
                self.part('cyl', f'forearm.{side}', 'buendchen', 0.038, 0.038, 0.025, material=self.inner if
                          s['top'].get('cuffs') else self.top, loc=(0, 0, -0.237))
            sx = 1 if side == 'L' else -1
            self.part('loft', f'hand.{side}', 'hand', [(0.01, 0.03, 0.017), (-0.035, 0.038, 0.016),
                                                        (-0.075, 0.036, 0.013), (-0.095, 0.03, 0.011)],
                      material=self.skin, n=16, power=2.6)
            self.part('loft', f'hand.{side}', 'daumen', [(0.0, 0.011, 0.011), (-0.05, 0.009, 0.009)],
                      material=self.skin, n=10, loc=(sx * 0.026, -0.016, -0.02), rot=(0.35, 0, sx * 0.5))
            self.part('loft', f'thigh.{side}', 'oberschenkel', [(0.04, 0.092, 0.095), (-0.08, 0.09, 0.094),
                                                                 (-0.3, 0.072, 0.076), (-0.44, 0.06, 0.063)],
                      material=self.pants, n=20)
            self.part('loft', f'shin.{side}', 'unterschenkel', [(0.02, 0.061, 0.064), (-0.1, 0.06, 0.068),
                                                                 (-0.3, 0.049, 0.051), (-0.42, 0.045, 0.047)],
                      material=self.pants, n=20)
            self.part('loft', f'foot.{side}', 'schuh', [(0.03, 0.045, 0.06, 0, -0.02), (-0.02, 0.052, 0.11, 0, -0.06),
                                                         (-0.055, 0.052, 0.135, 0, -0.065)],
                      material=self.shoes, n=20, power=2.6)
            self.part('box', f'foot.{side}', 'sohle', (0.108, 0.275, 0.022), material=self.sole,
                      loc=(0, -0.065, -0.062), bevel=0.01)
        self.clothing()

    def clothing(self):
        t = self.spec['top']
        kind = t['kind']
        sh = self.spec.get('shoulder', 0.2)
        if kind == 'hoodie':
            self.part('torus', 'chest', 'kapuze', 0.075, 0.03, material=self.top, loc=(0, 0.06, 0.26),
                      rot=(math.radians(60), 0, 0), scale=(1.2, 1, 1))
            self.part('box', 'spine', 'tasche', (0.24, 0.02, 0.1), material=self.top, loc=(0, -0.118, 0.04),
                      bevel=0.01)
            for x in (0.03, -0.03):
                self.part('cyl', 'chest', f'kordel{x}', 0.004, 0.004, 0.12, material=self.inner,
                          loc=(x, -0.135, 0.13))
        if kind in ('jacket', 'uniform', 'blazer'):
            # Hemd-Einsatz + Revers
            self.part('box', 'chest', 'hemd', (0.11, 0.02, 0.22), material=self.inner, loc=(0, -0.122, 0.12),
                      taper=(1.4, 1), bevel=0.005)
            for sx in (1, -1):
                self.part('box', 'chest', f'revers{sx}', (0.06, 0.012, 0.2), material=self.top,
                          loc=(sx * 0.06, -0.13, 0.13), rot=(0, sx * 0.35, 0), bevel=0.004)
            self.part('torus', 'chest', 'kragen', 0.062, 0.011, material=self.top, loc=(0, 0.012, 0.265),
                      rot=(math.radians(14), 0, 0), scale=(1, 1.1, 1))
        if t.get('tie'):
            self.part('box', 'chest', 'krawatte', (0.035, 0.01, 0.2), material=c.mat(f'Krawatte_{self.cid}', t['tie'],
                                                                                      rough=0.4), loc=(0, -0.134, 0.1),
                      taper=(0.6, 1), bevel=0.003)
        if kind == 'uniform':
            for sx in (1, -1):
                self.part('box', 'chest', f'paspel{sx}', (0.008, 0.008, 0.26), material=self.accent,
                          loc=(sx * 0.1, -0.128, 0.08))
                self.part('box', 'chest', f'epaulette{sx}', (0.09, 0.05, 0.012), material=self.top,
                          loc=(sx * (sh - 0.05), 0, 0.245), bevel=0.005)
            self.part('box', 'chest', 'namensschild', (0.07, 0.006, 0.02), material=self.accent,
                      loc=(0.09, -0.13, 0.17))
            for z in (0.05, -0.02):
                self.part('sphere', 'spine', f'knopf{z}', (0.009, 0.005, 0.009), material=self.accent,
                          loc=(0, -0.118, 0.07 + z), seg=10, rings=6)
        if kind == 'sweater':
            self.part('torus', 'chest', 'rollkragen', 0.052, 0.018, material=self.top, loc=(0, 0.004, 0.262),
                      scale=(1, 1.1, 1))
        if kind == 'cardigan':
            self.part('box', 'chest', 'hemd', (0.12, 0.02, 0.24), material=self.inner, loc=(0, -0.122, 0.11),
                      taper=(1.3, 1), bevel=0.005)
            for z in (0.0, 0.07, 0.14):
                self.part('sphere', 'chest', f'knopf{z}', (0.008, 0.005, 0.008), material=self.brow,
                          loc=(0.07, -0.13, z), seg=10, rings=6)

    # -------------------------------------------------------------- Kopf
    def head(self):
        s = self.spec
        jaw = s.get('jaw', 0.25)

        def head_shape(v):
            if v.z < 0:
                v.x *= 1 + jaw * v.z * 0.9
                v.y *= 1 + jaw * v.z * 0.25
            if v.z < -0.55 and v.y < 0:
                v.y -= 0.06 * (-v.z - 0.55)
        hr = s.get('head', (0.098, 0.112, 0.125))
        self.part('sphere', 'head', 'kopf', hr, material=self.skin, loc=(0, -0.002, 0.115), seg=40, rings=24,
                  shape=head_shape)
        self.part('sphere', 'head', 'nase', s.get('nose', (0.017, 0.026, 0.024)), material=self.skin,
                  loc=(0, -0.111, 0.103), seg=16, rings=10, rot=(0.25, 0, 0))
        for sx in (1, -1):
            self.part('sphere', 'head', f'ohr{sx}', (0.012, 0.026, 0.036), material=self.skin,
                      loc=(sx * 0.096, 0.004, 0.11), seg=14, rings=8, rot=(0, sx * 0.25, 0))
        for side in ('L', 'R'):
            self.part('sphere', f'eye.{side}', 'auge', (0.021, 0.021, 0.021), material=self.eyewhite, seg=20,
                      rings=12)
            self.part('sphere', f'eye.{side}', 'iris', (0.0118, 0.004, 0.0118), material=self.iris,
                      loc=(0, -0.019, 0), seg=20, rings=8)
            self.part('sphere', f'eye.{side}', 'pupille', (0.0058, 0.0025, 0.0058), material=self.pupil,
                      loc=(0, -0.0222, 0), seg=14, rings=6)
            self.part('sphere', f'lid.{side}', 'lid', (0.0232, 0.0232, 0.0232), material=self.skin, seg=20,
                      rings=12, half='top')
            sx = 1 if side == 'L' else -1
            bt = s.get('brow_thick', 0.009)
            self.part('box', f'brow.{side}', 'braue', (0.036, 0.01, bt), material=self.brow,
                      rot=(0, -sx * 0.12, 0), bevel=0.003)
        # Mund mit Shape Keys
        mouth = self.part('sphere', 'head', 'mund', (0.025, 0.008, 0.0045), material=self.mouth,
                          loc=(0, -0.1005, 0.062), seg=24, rings=12)
        mouth['mouth'] = True
        self._mouth_keys(mouth)
        self.part('box', 'head', 'zaehne', (0.03, 0.006, 0.007), material=self.teeth, loc=(0, -0.0985, 0.0655))
        self.part('sphere', 'head', 'unterlippe', (0.02, 0.006, 0.004), material=c.mat(f'Lippe_{self.cid}',
                  s.get('lips', '#B5675F'), rough=0.4, sss=0.1), loc=(0, -0.1015, 0.054), seg=16, rings=8)
        self.hair_style()
        for extra in s.get('extras', []):
            getattr(self, f'extra_{extra}')()

    def _mouth_keys(self, ob):
        ob.shape_key_add(name='Basis')

        def key(name, fn):
            k = ob.shape_key_add(name=name, from_mix=False)
            for p in k.data:
                co = p.co.copy()
                fn(co)
                p.co = co

        def open_(co):
            if co.z < 0:
                co.z *= 6.5
            else:
                co.z *= 1.6
            co.x *= 0.82

        def smile(co):
            co.z += (co.x / 0.025) ** 2 * 0.006
            co.x *= 1.12

        def frown(co):
            co.z -= (co.x / 0.025) ** 2 * 0.006
            co.x *= 0.95

        def wide(co):
            co.x *= 1.3

        key('open', open_)
        key('smile', smile)
        key('frown', frown)
        key('wide', wide)

    def hair_style(self):
        h = self.spec['hair']
        style = h['style']
        hm = self.hair
        base = (0, 0.004, 0.122)
        R = (0.106, 0.121, 0.132)

        def front_line(front, back):
            return lambda co: co.z > front + (back - front) * (co.y + 1) / 2

        if style == 'short':
            self.part('sphere', 'head', 'haar', R, material=hm, loc=base, seg=32, rings=18,
                      keep=front_line(0.45, -0.45), solidify=0.008)
        elif style == 'slick':
            self.part('sphere', 'head', 'haar', (0.104, 0.12, 0.133), material=hm, loc=base, seg=32, rings=18,
                      keep=front_line(0.5, -0.4), solidify=0.008,
                      shape=lambda v: v.__setitem__(0, v.x * (1.04 if v.x > 0 else 1.0)))
        elif style == 'bob':
            def flare(v):
                if v.z < 0:
                    v.x *= 1 + 0.12 * -v.z
                    v.y *= 1 + 0.05 * -v.z
            self.part('sphere', 'head', 'haar', (0.112, 0.126, 0.134), material=hm, loc=(0, 0.006, 0.118), seg=32,
                      rings=20, keep=lambda co: (co.z > 0.38 or co.y > -0.62) and co.z > -0.62, shape=flare,
                      solidify=0.01)
        elif style == 'ponytail':
            self.part('sphere', 'head', 'haar', R, material=hm, loc=base, seg=32, rings=18,
                      keep=front_line(0.42, -0.5), solidify=0.008)
            self.part('sphere', 'head', 'zopf', (0.035, 0.04, 0.11), material=hm, loc=(0, 0.13, 0.08),
                      rot=(-0.4, 0, 0), seg=16, rings=10)
            self.part('torus', 'head', 'gummi', 0.022, 0.006, material=c.mat('Haargummi', '#C9302C', rough=0.5),
                      loc=(0, 0.118, 0.155), rot=(1.1, 0, 0), seg=16, mseg=6)
        elif style == 'bald_ring':
            self.part('sphere', 'head', 'haar', (0.104, 0.12, 0.13), material=hm, loc=base, seg=32, rings=18,
                      keep=lambda co: -0.55 < co.z < 0.22 and co.y > -0.35, solidify=0.008)
        elif style == 'curly':
            self.part('sphere', 'head', 'haar', (0.112, 0.126, 0.136), material=hm, loc=base, seg=32, rings=18,
                      keep=front_line(0.42, -0.5), solidify=0.01)
            rnd = c.seeded(len(self.cid))
            for i in range(26):
                a = rnd.uniform(0, 2 * math.pi)
                el = rnd.uniform(0.15, 1.2)
                v = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
                if v.y < -0.4 and v.z < 0.6:
                    continue
                p = Vector((v.x * 0.112, v.y * 0.126 + 0.004, v.z * 0.136 + 0.122))
                self.part('sphere', 'head', f'locke{i}', (0.03, 0.03, 0.028), material=hm, loc=p, seg=10, rings=6)
        if h.get('bun'):
            self.part('sphere', 'head', 'dutt', (0.045, 0.045, 0.04), material=hm, loc=(0, 0.07, 0.235), seg=16,
                      rings=10)

    # -------------------------------------------------------------- Extras
    def extra_glasses(self):
        frame = c.mat(f'Brille_{self.cid}', self.spec.get('glasses_color', '#2A2420'), rough=0.3, coat=0.5)
        lens = c.mat('Brillenglas', '#C8D6E0', rough=0.02, alpha=0.15)
        for sx in (1, -1):
            self.part('torus', 'head', f'brillenrand{sx}', 0.021, 0.0028, material=frame,
                      loc=(sx * 0.037, -0.118, 0.134), rot=(math.pi / 2, 0, 0), seg=24, mseg=6, scale=(1.1, 0.85, 1))
            self.part('cyl', 'head', f'brillenbuegel{sx}', 0.002, 0.002, 0.11, material=frame,
                      loc=(sx * 0.093, -0.065, 0.136), rot=(math.pi / 2, 0, 0), verts=6)
            self.part('cyl', 'head', f'brillenglas{sx}', 0.021, 0.021, 0.002, material=lens,
                      loc=(sx * 0.037, -0.118, 0.134), rot=(math.pi / 2, 0, 0), verts=20)
        self.part('cyl', 'head', 'brillensteg', 0.0025, 0.0025, 0.03, material=frame, loc=(0, -0.121, 0.138),
                  rot=(0, math.pi / 2, 0), verts=6)

    def extra_mustache(self):
        self.part('sphere', 'head', 'schnurrbart', (0.034, 0.013, 0.011), material=self.hair, loc=(0, -0.112, 0.079),
                  seg=18, rings=8, shape=lambda v: v.__setitem__(2, v.z - 0.6 * v.x * v.x))

    def extra_beard(self):
        self.part('sphere', 'head', 'bart', (0.1, 0.112, 0.125), material=self.hair, loc=(0, -0.004, 0.113), seg=32,
                  rings=18, keep=lambda co: co.z < -0.25 and co.y < 0.3, solidify=0.01)

    def extra_cap(self):
        """Dienstmütze, eigenes Design (dunkles Petrol, Amber-Band)."""
        cap = c.mat(f'Muetze_{self.cid}', self.spec['top']['color'], rough=0.6, fabric=0.3)
        visor = c.mat('Schirm', '#111214', rough=0.2, coat=0.8)
        self.part('cyl', 'head', 'muetze', 0.108, 0.112, 0.065, material=cap, loc=(0, 0.004, 0.225), verts=32)
        self.part('cyl', 'head', 'muetze_deckel', 0.122, 0.12, 0.025, material=cap, loc=(0, 0.0, 0.265), verts=32,
                  rot=(-0.08, 0, 0))
        self.part('cyl', 'head', 'muetze_band', 0.11, 0.11, 0.018, material=self.accent, loc=(0, 0.004, 0.205),
                  verts=32)
        self.part('sphere', 'head', 'schirm', (0.095, 0.07, 0.008), material=visor, loc=(0, -0.105, 0.198),
                  rot=(0.25, 0, 0), half='front', seg=24, rings=8)

    def extra_beanie(self):
        knit = c.mat(f'Muetze_{self.cid}', self.spec.get('beanie', '#C9731A'), rough=0.9, fabric=0.7, bump=0.4,
                     bump_scale=180)
        self.part('sphere', 'head', 'beanie', (0.112, 0.126, 0.13), material=knit, loc=(0, 0.004, 0.14), seg=32,
                  rings=18, keep=lambda co: co.z > 0.1, solidify=0.012)
        self.part('torus', 'head', 'beanie_rand', 0.105, 0.016, material=knit, loc=(0, 0.004, 0.158),
                  scale=(1, 1.12, 1), rot=(-0.12, 0, 0))

    def extra_headphones(self):
        hp = c.mat('Kopfhoerer', '#1C1D20', rough=0.35)
        self.part('torus', 'neck', 'kopfhoerer_buegel', 0.09, 0.008, material=hp, loc=(0, 0.01, -0.01),
                  rot=(math.radians(-15), 0, 0), scale=(1, 1.1, 1))
        for sx in (1, -1):
            self.part('cyl', 'neck', f'kopfhoerer_muschel{sx}', 0.035, 0.035, 0.025, material=hp,
                      loc=(sx * 0.07, -0.06, -0.03), rot=(0.5, sx * 0.8, 0))

    def extra_lanyard(self):
        band = c.mat('Lanyard', '#FF9F1C', rough=0.6)
        self.part('torus', 'chest', 'lanyard', 0.08, 0.004, material=band, loc=(0, -0.06, 0.18),
                  rot=(math.radians(-55), 0, 0), scale=(1, 1.5, 1))
        self.part('box', 'chest', 'ausweis', (0.05, 0.004, 0.07), material=c.mat('Ausweis', '#E9E6E0', rough=0.4),
                  loc=(0, -0.135, 0.03))

    def extra_scarf(self):
        sc = c.mat(f'Schal_{self.cid}', self.spec.get('scarf', '#8E3B2E'), rough=0.9, fabric=0.6)
        self.part('torus', 'neck', 'schal', 0.058, 0.024, material=sc, loc=(0, -0.002, -0.005), scale=(1, 1.1, 1))
        self.part('box', 'chest', 'schal_ende', (0.06, 0.02, 0.2), material=sc, loc=(0.04, -0.135, 0.12),
                  bevel=0.008, rot=(0, 0.1, 0))


def build(cid, spec):
    b = Builder(cid, spec)
    b.body()
    b.head()
    b.root.scale = (spec.get('scale', 1.0),) * 3
    b.j['head'].scale = (spec.get('head_scale', 1.1),) * 3
    for ob in b.coll.objects:
        if ob.type == 'MESH':
            ob['char_part'] = cid
    apply_pose(b.root, 'stand')
    apply_expression(b.root, 'neutral')
    return b.root


# ================================================================== Posen & Mimik

def joints(root):
    return {o['joint']: o for o in root.children_recursive if 'joint' in o}


def mouth_of(root):
    return next(o for o in root.children_recursive if o.get('mouth'))


# Rotation in Grad (X, Y, Z) für die linke Seite; rechts wird gespiegelt (Y, Z negiert),
# außer es steht explizit ".R"/".L" dabei. hips_z: Höhe des Beckens über der Wurzel.
POSES = {
    'stand': {'upper_arm': (2, -5, 0), 'forearm': (-10, 0, 0), 'hips_z': 0.95},
    'stand_talk': {'upper_arm.L': (2, -5, 0), 'forearm.L': (-10, 0, 0), 'upper_arm.R': (-28, 8, 0),
                   'forearm.R': (-75, 0, 20), 'hand.R': (0, 0, -20), 'hips_z': 0.95},
    'stand_talk2': {'upper_arm': (-25, -10, 0), 'forearm': (-70, 0, -20), 'hips_z': 0.95},
    'arms_crossed': {'upper_arm': (-22, -12, 0), 'forearm': (-100, 0, -75), 'spine': (-4, 0, 0), 'hips_z': 0.95},
    'point': {'upper_arm.L': (2, -5, 0), 'forearm.L': (-10, 0, 0), 'upper_arm.R': (-85, 0, 8),
              'forearm.R': (-5, 0, 0), 'hips_z': 0.95},
    'raise_card': {'upper_arm.L': (-10, -8, 0), 'forearm.L': (-30, 0, 0), 'upper_arm.R': (-155, 0, -5),
                   'forearm.R': (-25, 0, 0), 'hand.R': (0, 90, 0), 'spine': (-6, 0, 0), 'hips_z': 0.95},
    'hands_up': {'upper_arm': (-150, -25, 0), 'forearm': (-25, 0, 0), 'spine': (6, 0, 0), 'hips_z': 0.95},
    'shrug': {'upper_arm': (-15, -22, 0), 'forearm': (-85, 0, 35), 'hand': (0, 0, 30), 'chest': (0, 0, 0),
              'hips_z': 0.95},
    'pull': {'upper_arm': (-55, -4, 0), 'forearm': (-35, 0, -10), 'spine': (-14, 0, 0), 'thigh.L': (-12, 0, 0),
             'shin.L': (8, 0, 0), 'thigh.R': (14, 0, 0), 'hips_z': 0.93},
    'lean_in': {'upper_arm': (-35, -6, 0), 'forearm': (-60, 0, -15), 'spine': (14, 0, 0), 'chest': (6, 0, 0),
                'hips_z': 0.95},
    'jolt': {'upper_arm': (-55, -15, 0), 'forearm': (-30, 0, 0), 'spine': (24, 0, 0), 'chest': (10, 0, 0),
             'head': (14, 0, 0), 'hips_z': 0.95},
    'walk_a': {'thigh.L': (-24, 0, 0), 'shin.L': (12, 0, 0), 'thigh.R': (18, 0, 0), 'shin.R': (28, 0, 0),
               'upper_arm.L': (18, -5, 0), 'upper_arm.R': (-20, 5, 0), 'forearm': (-18, 0, 0), 'hips_z': 0.935},
    'walk_b': {'thigh.R': (-24, 0, 0), 'shin.R': (12, 0, 0), 'thigh.L': (18, 0, 0), 'shin.L': (28, 0, 0),
               'upper_arm.R': (18, 5, 0), 'upper_arm.L': (-20, -5, 0), 'forearm': (-18, 0, 0), 'hips_z': 0.935},
    'run_a': {'thigh.L': (-50, 0, 0), 'shin.L': (40, 0, 0), 'thigh.R': (30, 0, 0), 'shin.R': (70, 0, 0),
              'upper_arm.L': (40, -8, 0), 'upper_arm.R': (-45, 8, 0), 'forearm': (-80, 0, 0), 'spine': (14, 0, 0),
              'hips_z': 0.9},
    'run_b': {'thigh.R': (-50, 0, 0), 'shin.R': (40, 0, 0), 'thigh.L': (30, 0, 0), 'shin.L': (70, 0, 0),
              'upper_arm.R': (40, 8, 0), 'upper_arm.L': (-45, -8, 0), 'forearm': (-80, 0, 0), 'spine': (14, 0, 0),
              'hips_z': 0.9},
    'sit': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'foot': (2, 0, 0), 'spine': (-5, 0, 0),
            'upper_arm': (-22, -6, 0), 'forearm': (-60, 0, -14), 'hips_z': 0.1},
    'sit_table': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'spine': (6, 0, 0), 'chest': (3, 0, 0),
                  'upper_arm': (-38, -10, 0), 'forearm': (-52, 0, -28), 'hand': (-10, 0, 0), 'hips_z': 0.1},
    'sit_cup': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'spine': (4, 0, 0),
                'upper_arm.L': (-38, -10, 0), 'forearm.L': (-52, 0, -28),
                'upper_arm.R': (-30, 10, 0), 'forearm.R': (-100, 0, 25), 'hand.R': (0, 0, 70), 'hips_z': 0.1},
    'sit_phone': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'spine': (8, 0, 0), 'head': (14, 0, 0),
                  'upper_arm': (-18, -6, 0), 'forearm': (-95, 0, -38), 'hand': (-20, 0, 0), 'hips_z': 0.1},
    'sit_back': {'thigh': (-86, -5, 0), 'shin': (80, 0, 0), 'spine': (-12, 0, 0), 'upper_arm': (-8, -10, 0),
                 'forearm': (-45, 0, -18), 'hips_z': 0.1},
    'sit_arms_crossed': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'spine': (-8, 0, 0),
                         'upper_arm': (-22, -12, 0), 'forearm': (-100, 0, -75), 'hips_z': 0.1},
    'sit_talk': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'spine': (4, 0, 0),
                 'upper_arm.L': (-38, -10, 0), 'forearm.L': (-52, 0, -28),
                 'upper_arm.R': (-35, 12, 0), 'forearm.R': (-85, 0, 30), 'hand.R': (0, 0, -30), 'hips_z': 0.1},
    'sit_jolt': {'thigh': (-88, -3, 0), 'shin': (86, 0, 0), 'spine': (26, 0, 0), 'chest': (8, 0, 0),
                 'head': (10, 0, 0), 'upper_arm': (-60, -18, 0), 'forearm': (-40, 0, 0), 'hips_z': 0.1},
}

ALL_SIDED = ['upper_arm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'eye', 'lid', 'brow']


def pose_rotations(name):
    p = POSES[name]
    out = {}
    for key, val in p.items():
        if key == 'hips_z':
            continue
        if key.endswith('.L') or key.endswith('.R'):
            out[key] = val
        elif key in ALL_SIDED:
            out.setdefault(f'{key}.L', val)
            out.setdefault(f'{key}.R', (val[0], -val[1], -val[2]))
        else:
            out[key] = val
    # explizite Seitenangaben gewinnen
    for key, val in p.items():
        if key.endswith('.L') or key.endswith('.R'):
            out[key] = val
    return out, p.get('hips_z', 0.95)


BODY_JOINTS = ['hips', 'spine', 'chest', 'neck', 'head', 'upper_arm.L', 'forearm.L', 'hand.L', 'upper_arm.R',
               'forearm.R', 'hand.R', 'thigh.L', 'shin.L', 'foot.L', 'thigh.R', 'shin.R', 'foot.R']


def apply_pose(root, name, frame=None, extra=None):
    """Pose setzen (und optional keyen). extra: zusätzliche Rotationen in Grad, z. B. für Blickrichtung."""
    J = joints(root)
    rots, hips_z = pose_rotations(name)
    extra = extra or {}
    for jn in BODY_JOINTS:
        r = rots.get(jn, (0, 0, 0))
        e = extra.get(jn, (0, 0, 0))
        J[jn].rotation_euler = tuple(math.radians(a + b) for a, b in zip(r, e))
        if frame is not None:
            J[jn].keyframe_insert('rotation_euler', frame=frame)
    J['hips'].location.z = hips_z + extra.get('hips_dz', 0.0)
    J['hips'].location.y = extra.get('hips_dy', 0.0)
    if frame is not None:
        J['hips'].keyframe_insert('location', frame=frame)


EXPRESSIONS = {
    'neutral': {},
    'smile': dict(smile=0.7, brow=0.002),
    'grin': dict(smile=1.0, open=0.25, wide=0.25, brow=0.004),
    'happy': dict(smile=0.9, open=0.3, brow=0.006),
    'annoyed': dict(frown=0.45, inner=-0.22, lid=0.35),
    'angry': dict(frown=0.7, inner=-0.4, brow=-0.004, lid=0.22, wide=0.25),
    'surprised': dict(open=0.55, brow=0.012, lid=-0.4),
    'shocked': dict(open=1.0, brow=0.014, inner=0.2, lid=-0.5),
    'worried': dict(frown=0.35, inner=0.35, brow=0.004),
    'smug': dict(smile=0.55, lid=0.32, brow=0.003),
    'tired': dict(lid=0.5, frown=0.15, inner=0.12),
    'determined': dict(frown=0.15, inner=-0.25, lid=0.15),
    'panic': dict(open=0.9, inner=0.45, brow=0.012, wide=0.35, lid=-0.4),
    'sceptical': dict(frown=0.2, inner=-0.1, lid=0.25, brow=0.003),
}

LID_OPEN, LID_CLOSED = -0.28, 1.45


def apply_expression(root, name, frame=None, blink=False):
    J = joints(root)
    e = EXPRESSIONS[name]
    lid = 1.0 if blink else e.get('lid', 0.0)
    lid_angle = LID_OPEN + (LID_CLOSED - LID_OPEN) * max(lid, 0) if lid >= 0 else LID_OPEN + 0.35 * lid
    for side, sx in (('L', 1), ('R', -1)):
        J[f'lid.{side}'].rotation_euler = (lid_angle, 0, 0)
        b = J[f'brow.{side}']
        b.location.z = 0.168 + e.get('brow', 0.0) - (0.004 if lid > 0.3 and not blink else 0)
        b.rotation_euler = (0, sx * e.get('inner', 0.0), 0)
        if frame is not None:
            J[f'lid.{side}'].keyframe_insert('rotation_euler', frame=frame)
            b.keyframe_insert('location', frame=frame)
            b.keyframe_insert('rotation_euler', frame=frame)
    keys = mouth_of(root).data.shape_keys.key_blocks
    for k in ('open', 'smile', 'frown', 'wide'):
        keys[k].value = e.get(k, 0.0)
        if frame is not None:
            keys[k].keyframe_insert('value', frame=frame)


# ================================================================== Lookdev

def lookdev(cid, path, quality='preview'):
    """Figur in neutralem Studio: Ganzkörper (3/4) + Porträt nebeneinander als zwei Bilder."""
    from . import world
    sc = c.setup_render(quality=quality)
    root = bpy.data.objects[cid]
    world.build_sky()
    world.apply_time('tag')
    sc.world.node_tree.nodes['SKY_BG'].inputs['Strength'].default_value = 0.4
    floor = c.plane('Studio_boden', (8, 8), (0, 0, 0), c.mat('Studio', '#5B6068', rough=0.8))
    back = c.plane('Studio_wand', (8, 4), (0, 2.5, 2), c.mat('Studio', '#5B6068'), rot=(math.pi / 2, 0, 0))
    for name, loc, energy, size in (('Key', (-1.6, -2.2, 2.6), 300, 1.5), ('Fill', (2.0, -1.8, 1.6), 120, 2.0),
                                    ('Rim', (0.8, 1.6, 2.4), 200, 1.0)):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.energy, ld.size = energy, size
        lo = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(lo)
        lo.location = loc
        c.look_at(lo, (0, 0, 1.2))
    apply_expression(root, 'smile')
    cam_d = bpy.data.cameras.new('LD')
    cam = bpy.data.objects.new('LD', cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    h = root.scale.z
    for suffix, loc, target, lens in (('ganz', (-1.5, -3.6, 1.15 * h), (0, 0, 0.88 * h), 40),
                                      ('portrait', (-0.32, -0.95, 1.67 * h), (0, 0, 1.63 * h), 65)):
        cam.location = loc
        cam_d.lens = lens
        c.look_at(cam, target)
        sc.render.filepath = path.replace('.jpg', f'_{suffix}.jpg')
        bpy.ops.render.render(write_still=True)
        print('lookdev', sc.render.filepath, flush=True)
