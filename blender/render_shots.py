"""Rendert die Shots einer Folge aus episodes/<id>.json.

  blender -b -P blender/render_shots.py -- day-01 [--shots s02,s06] [--quality draft|preview|final]
                                                  [--step 2] [--stills] [--save-blend]

Ausgabe: public/renders/<id>/<shot>/0001.jpg … und public/renders/<id>/manifest.json (für Remotion).
--stills rendert nur ein Kontrollbild pro Shot nach out/stills/<id>/.
"""
import json
import math
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

from lib import character as ch  # noqa: E402
from lib import common as c  # noqa: E402
from lib import world  # noqa: E402

ARGS = c.script_args()


def opt(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


_pos, _skip = [], False
for _a in ARGS:
    if _skip:
        _skip = False
    elif _a in ('--shots', '--quality', '--step'):
        _skip = True
    elif not _a.startswith('--'):
        _pos.append(_a)
EP_ID = _pos[0] if _pos else 'day-01'
QUALITY = opt('--quality', 'preview')
STEP = int(opt('--step', '1'))
ONLY = opt('--shots', '').split(',') if '--shots' in ARGS else None
STILLS = '--stills' in ARGS
SAVE_BLEND = '--save-blend' in ARGS

EP = json.load(open(os.path.join(c.ROOT, 'episodes', f'{EP_ID}.json'), encoding='utf-8'))
FPS = EP.get('fps', 30)
OUT = os.path.join(c.ROOT, 'public', 'renders', EP_ID)
STILL_DIR = os.path.join(c.ROOT, 'out', 'stills', EP_ID)
INTERIOR_LIMIT_X = 1.26


def stable(*x):
    """reproduzierbarer Hash (Python-hash() ist pro Prozess zufällig)"""
    return zlib.crc32(repr(x).encode()) % 100000


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, w):
    return a + (b - a) * w


def wave(seed, t, freqs=(0.7, 1.3, 2.9)):
    """glattes Pseudo-Rauschen in [-1, 1]"""
    r = c.seeded(seed)
    return sum(math.sin(t * f * 2 * math.pi + r.uniform(0, 6.28)) for f in freqs) / len(freqs)


# ====================================================================== Set laden

class Stage:
    def __init__(self, shot):
        self.shot = shot
        self.set = shot['set']
        self.interior = self.set != 'aussen'
        c.reset()
        env = c.append_collection(os.path.join(c.ASSETS, 'sets', 'umgebung.blend'), 'ENV')
        self.env_root = next(o for o in env.all_objects if o.get('env_root'))
        self.coll = c.append_collection(os.path.join(c.ASSETS, 'sets', f'{self.set}.blend'), f'SET_{self.set}')
        self.marks = {o['mark']: o for o in self.coll.all_objects if 'mark' in o}
        self.cams = {o['campreset']: o for o in self.coll.all_objects if 'campreset' in o}
        world.build_sky()
        world.apply_time(shot.get('time', 'tag'))
        self.scene = c.setup_render(quality=QUALITY, fps=FPS)
        self.frames = int(round(shot['duration'] * FPS))
        self.scene.frame_start, self.scene.frame_end = 1, self.frames
        self.scene.frame_step = STEP
        for o in self.coll.all_objects:
            if o.get('display') and o.type == 'FONT':
                o.data.body = shot.get('display', 'HAMBURG HBF')
        self.train_root = None
        if not self.interior:
            self.train_root = c.empty('TRAIN_ROOT', size=1)
            for o in self.coll.all_objects:
                if o.parent is None and o.type != 'CAMERA':
                    o.parent = self.train_root

    def mark(self, mid):
        m = self.marks.get(mid)
        if not m:
            raise KeyError(f'Marke {mid} gibt es in {self.set} nicht. Vorhanden: {sorted(self.marks)[:40]} …')
        return m.location.copy(), math.degrees(m.rotation_euler.z)

    def point(self, spec):
        if isinstance(spec, str) and spec.startswith('mark:'):
            return self.mark(spec[5:])[0]
        return Vector(spec)


# ====================================================================== Figuren

class Actor:
    def __init__(self, stage, spec, all_specs):
        self.stage, self.spec = stage, spec
        self.id = spec['id']
        coll = c.append_collection(os.path.join(c.ASSETS, 'characters', f'{self.id}.blend'), f'CHR_{self.id}')
        self.root = next(o for o in coll.all_objects if o.get('char') == self.id)
        self.J = ch.joints(self.root)
        self.mouth = ch.mouth_of(self.root).data.shape_keys.key_blocks
        self.scale = self.root.scale.z
        pos, facing = stage.mark(spec['mark'])
        if not spec.get('pose', 'stand').startswith('sit'):
            pos.z = 0.0  # stehend auf einer Sitzmarke: auf den Boden
        self.home = pos
        self.facing0 = spec.get('facing', facing)
        self.rnd = c.seeded(stable(self.id))
        self.blinks = []
        t = self.rnd.uniform(0.3, 1.8)
        while t < 60:
            self.blinks.append(t)
            t += self.rnd.uniform(2.2, 4.5)
        # Ereignisse
        keys = sorted(spec.get('keys', []), key=lambda k: k['t'])
        self.poses = [(0.0, spec.get('pose', 'stand'))] + [(k['t'], k['pose']) for k in keys if 'pose' in k]
        self.exprs = [(0.0, spec.get('expr', 'neutral'))] + [(k['t'], k['expr']) for k in keys if 'expr' in k]
        self.looks = [(0.0, spec.get('look'))] + [(k['t'], k['look']) for k in keys if 'look' in k]
        self.facings = [(0.0, self.facing0)] + [(k['t'], k['facing']) for k in keys if 'facing' in k]
        self.moves = []
        p = self.home.copy()
        for k in keys:
            if 'move' in k:
                tgt = stage.mark(k['move'])[0] if isinstance(k['move'], str) else Vector(k['move'])
                tgt.z = 0.0
                self.moves.append(dict(t0=k['t'], t1=k['t'] + k.get('dur', 1.0), a=p.copy(), b=tgt,
                                       gait=k.get('gait', 'walk')))
                p = tgt
        self.lines = []

    # -------------------------------------------------- Zeitachse
    @staticmethod
    def _seg(events, t, trans):
        """(vorheriger Wert, aktueller Wert, Gewicht) für Ereignislisten [(t, v)]."""
        cur, prev, tk = events[0][1], events[0][1], 0.0
        for i, (te, v) in enumerate(events):
            if te <= t:
                prev = events[i - 1][1] if i > 0 else v
                cur, tk = v, te
        w = smooth((t - tk) / trans) if tk > 0 else 1.0
        return prev, cur, w

    def position(self, t):
        p = self.home.copy()
        for m in self.moves:
            if t >= m['t1']:
                p = m['b'].copy()
            elif t >= m['t0']:
                w = (t - m['t0']) / (m['t1'] - m['t0'])
                w = w * w * (3 - 2 * w) if m['gait'] == 'walk' else min(1.0, w * 1.15) ** 0.9
                p = m['a'].lerp(m['b'], w)
        return p

    def active_move(self, t):
        for m in self.moves:
            if m['t0'] <= t < m['t1']:
                return m
        return None

    def facing(self, t):
        m = self.active_move(t)
        if m:
            d = m['b'] - m['a']
            return math.degrees(math.atan2(d.x, -d.y))
        a, b, w = self._seg(self.facings, t, 0.35)
        diff = (b - a + 180) % 360 - 180
        return a + diff * w

    def hips_z(self, t):
        a, b, w = self._seg(self.poses, t, 0.3)
        return lerp(ch.POSES[a].get('hips_z', 0.95), ch.POSES[b].get('hips_z', 0.95), w)

    def face_pos(self, t):
        p = self.position(t)
        return Vector((p.x, p.y, p.z + (self.hips_z(t) + 0.72) * self.scale))

    def target_point(self, look, t, actors, cam_pos):
        f = self.face_pos(t)
        fr = math.radians(self.facing(t))
        fwd = Vector((math.sin(fr), -math.cos(fr), 0))
        if look is None:
            return f + fwd * 2
        if isinstance(look, list):
            return Vector(look)
        if look == 'camera':
            return cam_pos
        if look == 'window':
            side = -1 if f.x < 0 else 1
            return Vector((side * 4.0, f.y - 1.5, f.z - 0.1))
        if look == 'ceiling':
            return Vector((f.x * 0.3, f.y - 1.2, 2.6))
        if look == 'down':
            return f + fwd * 0.45 + Vector((0, 0, -0.6))
        if look in actors:
            return actors[look].face_pos(t)
        return self.stage.point(look)

    def look_rot(self, look, t, actors, cam_pos):
        tgt = self.target_point(look, t, actors, cam_pos)
        f = self.face_pos(t)
        d = tgt - f
        fr = math.radians(self.facing(t))
        local = Matrix.Rotation(-fr, 3, 'Z') @ d
        yaw = math.degrees(math.atan2(local.x, -local.y))
        pitch = math.degrees(math.atan2(local.z, math.hypot(local.x, local.y)))
        yaw = max(-80, min(80, yaw))
        pitch = max(-40, min(40, pitch))
        return yaw, pitch

    # -------------------------------------------------- Pose pro Frame
    def pose_at(self, t):
        a, b, w = self._seg(self.poses, t, 0.35)
        ra, za = ch.pose_rotations(a)
        rb, zb = ch.pose_rotations(b)
        rot = {}
        for jn in ch.BODY_JOINTS:
            va, vb = ra.get(jn, (0, 0, 0)), rb.get(jn, (0, 0, 0))
            rot[jn] = [lerp(x, y, w) for x, y in zip(va, vb)]
        hz = lerp(za, zb, w)
        m = self.active_move(t)
        if m:
            dist = (self.position(t) - m['a']).length
            stride = 0.62 if m['gait'] == 'walk' else 0.95
            phase = dist / stride * math.pi
            ga, gb = (('walk_a', 'walk_b') if m['gait'] == 'walk' else ('run_a', 'run_b'))
            wa, za2 = ch.pose_rotations(ga)
            wb, _ = ch.pose_rotations(gb)
            mix = 0.5 + 0.5 * math.sin(phase)
            ramp = smooth(min((t - m['t0']) / 0.15, (m['t1'] - t) / 0.15, 1.0))
            for jn in ch.BODY_JOINTS:
                g = [lerp(x, y, mix) for x, y in zip(wb.get(jn, (0, 0, 0)), wa.get(jn, (0, 0, 0)))]
                rot[jn] = [lerp(x, y, ramp) for x, y in zip(rot[jn], g)]
            hz = lerp(hz, za2 + 0.02 * abs(math.sin(phase)), ramp)
        return rot, hz

    def expr_at(self, t):
        a, b, w = self._seg(self.exprs, t, 0.25)
        ea, eb = ch.EXPRESSIONS[a], ch.EXPRESSIONS[b]
        keys = set(ea) | set(eb)
        return {k: lerp(ea.get(k, 0.0), eb.get(k, 0.0), w) for k in keys}

    def apply(self, f, t, actors, cam_pos, jolt):
        J = self.J
        rot, hz = self.pose_at(t)
        # Blick
        la, lb, lw = self._seg(self.looks, t, 0.3)
        ya, pa = self.look_rot(la, t, actors, cam_pos)
        yb, pb = self.look_rot(lb, t, actors, cam_pos)
        yaw, pitch = lerp(ya, yb, lw), lerp(pa, pb, lw)
        rot['neck'][0] += -pitch * 0.35
        rot['neck'][2] += yaw * 0.3
        rot['head'][0] += -pitch * 0.55
        rot['head'][2] += yaw * 0.5
        if abs(yaw) > 35:
            rot['chest'][2] += (yaw - math.copysign(35, yaw)) * 0.35
        # Atmen und kleine Kopfbewegungen
        rot['chest'][0] += 0.8 * math.sin(t * 2 * math.pi / 3.6)
        rot['head'][0] += 1.2 * wave(stable(self.id) + 1, t * 0.4)
        rot['head'][1] += 1.5 * wave(stable(self.id) + 2, t * 0.3)
        # Sprechen: Kopfnicken
        talking = [ln for ln in self.lines if ln['t'] <= t <= ln['t'] + ln['d']]
        if talking:
            rot['head'][0] += 2.5 * math.sin(t * 9.0) + 1.5 * wave(stable(self.id) + 3, t * 2)
        # Ruck beim Bremsen
        if jolt:
            j = jolt(t)
            seated = hz < 0.5
            rot['spine'][0] += 24 * j if seated else 12 * j
            rot['chest'][0] += 8 * j
            rot['head'][0] += 14 * j
            for s in ('L', 'R'):
                rot[f'upper_arm.{s}'][0] += -40 * j
                rot[f'forearm.{s}'][0] += 20 * j
            if not seated:
                hz -= 0.03 * j
        for jn in ch.BODY_JOINTS:
            J[jn].rotation_euler = [math.radians(v) for v in rot[jn]]
            J[jn].keyframe_insert('rotation_euler', frame=f)
        J['hips'].location.z = hz
        J['hips'].keyframe_insert('location', frame=f)
        # Wurzel
        p = self.position(t)
        self.root.location = p
        self.root.rotation_euler = (0, 0, math.radians(self.facing(t)))
        self.root.keyframe_insert('location', frame=f)
        self.root.keyframe_insert('rotation_euler', frame=f)
        # Augen folgen dem Rest des Blicks
        for s in ('L', 'R'):
            J[f'eye.{s}'].rotation_euler = (math.radians(-pitch * 0.25), 0, math.radians(max(-25, min(25, yaw * 0.3))))
            J[f'eye.{s}'].keyframe_insert('rotation_euler', frame=f)
        # Mimik + Blinzeln + Lippen
        e = self.expr_at(t)
        blink = 0.0
        for bt in self.blinks:
            if 0 <= t - bt < 0.16:
                blink = 1 - abs((t - bt) / 0.08 - 1)
        lid = max(e.get('lid', 0.0), blink) if blink > 0 else e.get('lid', 0.0)
        lid_angle = (ch.LID_OPEN + (ch.LID_CLOSED - ch.LID_OPEN) * lid) if lid >= 0 else ch.LID_OPEN + 0.35 * lid
        for s, sx in (('L', 1), ('R', -1)):
            J[f'lid.{s}'].rotation_euler = (lid_angle, 0, 0)
            J[f'lid.{s}'].keyframe_insert('rotation_euler', frame=f)
            J[f'brow.{s}'].location.z = 0.168 + e.get('brow', 0.0) + (0.003 * math.sin(t * 7) if talking else 0)
            J[f'brow.{s}'].rotation_euler = (0, sx * e.get('inner', 0.0), 0)
            J[f'brow.{s}'].keyframe_insert('location', frame=f)
            J[f'brow.{s}'].keyframe_insert('rotation_euler', frame=f)
        mouth_open = e.get('open', 0.0)
        if talking:
            ln = talking[0]
            seg = int((t - ln['t']) * FPS / 3)
            r1 = c.seeded(stable(self.id, seg)).uniform(0.15, 0.85)
            r2 = c.seeded(stable(self.id, seg + 1)).uniform(0.15, 0.85)
            frac = ((t - ln['t']) * FPS / 3) % 1
            env = smooth(min((t - ln['t']) / 0.08, (ln['t'] + ln['d'] - t) / 0.08, 1))
            mouth_open = max(mouth_open, lerp(r1, r2, frac) * env)
        for k in ('open', 'smile', 'frown', 'wide'):
            self.mouth[k].value = mouth_open if k == 'open' else e.get(k, 0.0)
            self.mouth[k].keyframe_insert('value', frame=f)


# ====================================================================== Kamera

def build_camera(stage, actors, spec):
    cam_data = bpy.data.cameras.new('SHOT_CAM')
    cam = bpy.data.objects.new('SHOT_CAM', cam_data)
    stage.scene.collection.objects.link(cam)
    stage.scene.camera = cam
    cam_data.clip_start = spec.get('clip', 0.05)
    cam_data.lens = spec.get('lens', 35)
    kind = spec.get('type', 'preset' if 'preset' in spec else 'free')
    focus = None

    # Bezugszeitpunkt: wo stehen die Figuren, wenn der Shot "sitzt" (nach Gängen/Drehungen)
    t_ref = spec.get('at', stage.shot['duration'] * 0.6)

    def F(aid, t=None):
        return actors[aid].face_pos(t_ref if t is None else t)

    if kind == 'preset':
        src = stage.cams[spec['preset']]
        pos = src.location.copy()
        aim = Vector(src['target'])
        cam_data.lens = spec.get('lens', src.data.lens)
    elif kind == 'free':
        pos = Vector(spec['pos'])
        tgt = spec['target']
        aim = F(tgt) if isinstance(tgt, str) else Vector(tgt)
        focus = tgt if isinstance(tgt, str) else None
    elif kind == 'close':
        a = actors[spec['on']]
        f = F(spec['on'])
        fr = math.radians(a.facing(t_ref) + spec.get('angle', 0))
        d = Vector((math.sin(fr), -math.cos(fr), 0))
        pos = f + d * spec.get('dist', 0.9) + Vector((0, 0, spec.get('height', 0.0)))
        aim = f + Vector((0, 0, -0.07))
        focus = spec['on']
    elif kind == 'ots':
        fa, fb = F(spec['from']), F(spec['to'])
        d = fb - fa
        d.z = 0
        d.normalize()
        perp = Vector((d.y, -d.x, 0)) * spec.get('side', 1)
        pos = fa - d * spec.get('back', 0.55) + perp * spec.get('offset', 0.3) + Vector((0, 0, spec.get('height', 0.08)))
        aim = fb + Vector((0, 0, -0.06))
        focus = spec['to']
    elif kind == 'two':
        fa, fb = F(spec['a']), F(spec['b'])
        mid = (fa + fb) / 2
        d = fb - fa
        d.z = 0
        d.normalize()
        perp = Vector((-d.y, d.x, 0)) * spec.get('side', 1)
        pos = mid + perp * spec.get('dist', 2.0) + Vector((0, 0, spec.get('height', 0.0)))
        aim = mid + Vector((0, 0, -0.12))
        focus = spec['a']
    else:
        raise ValueError(f'Kameratyp {kind}?')

    if stage.interior:
        pos.x = max(-INTERIOR_LIMIT_X, min(INTERIOR_LIMIT_X, pos.x))
        pos.z = max(0.35, min(2.05, pos.z))
    end = pos + (aim - pos) * spec.get('push', 0.0) + Vector(spec.get('drift', (0, 0, 0)))
    if stage.interior:
        end.x = max(-INTERIOR_LIMIT_X, min(INTERIOR_LIMIT_X, end.x))
    fstop = spec.get('fstop')
    if fstop:
        cam_data.dof.use_dof = True
        cam_data.dof.aperture_fstop = fstop
    shakes = spec.get('shake', [])
    seed = stable(stage.shot['id'])

    def at(f, t):
        w = smooth(t / max(stage.shot['duration'], 0.01))
        p = pos.lerp(end, w)
        target = aim
        if spec.get('track') and focus:
            target = actors[focus].face_pos(t) + Vector((0, 0, -0.07))
        cam.location = p
        q = (target - p).to_track_quat('-Z', 'Y').to_euler()
        amp = 0.25  # immer leicht "Handkamera"
        for sh in shakes:
            if sh['t'] <= t <= sh['t'] + sh['dur']:
                k = (t - sh['t']) / sh['dur']
                amp += sh['amp'] * (1 - k) ** 1.5
        q.x += math.radians(amp * wave(seed + 1, t * 2.2, (1.1, 2.3, 4.7)))
        q.y += math.radians(amp * 0.6 * wave(seed + 2, t * 2.2, (0.9, 2.9, 5.3)))
        q.z += math.radians(amp * wave(seed + 3, t * 2.2, (1.3, 2.1, 4.1)))
        cam.rotation_euler = q
        cam.keyframe_insert('location', frame=f)
        cam.keyframe_insert('rotation_euler', frame=f)
        if cam_data.dof.use_dof:
            fp = actors[focus].face_pos(t) if focus in actors else target
            cam_data.dof.focus_distance = (fp - p).length
            cam_data.dof.keyframe_insert('focus_distance', frame=f)
        return p
    return cam, at


# ====================================================================== Bewegung / Requisiten

def motion_fn(spec, duration):
    if not spec:
        return None
    v0 = spec.get('speed', 45.0)
    br = spec.get('brake')
    dt = 1.0 / FPS
    pos, out = 0.0, []
    for i in range(int(duration * FPS) + 2):
        t = i * dt
        v = v0
        if br and t >= br['t']:
            k = min(1.0, (t - br['t']) / br['dur'])
            v = v0 * (1 - k) ** 1.6
        out.append(pos)
        pos += v * dt
    return lambda t: out[min(len(out) - 1, int(round(t * FPS)))]


def jolt_fn(spec):
    if not spec:
        return None

    def j(t):
        x = t - spec['t']
        if x < 0 or x > spec['dur']:
            return 0.0
        rise = min(1.0, x / 0.12)
        return rise * math.exp(-max(0, x - 0.12) * 4.5) * (1 + 0.15 * math.sin(x * 25))
    return j


def place_props(stage, actors, specs):
    for p in specs or []:
        coll = c.append_collection(os.path.join(c.ASSETS, 'props', 'props.blend'), f'PROP_{p["prop"]}')
        ob = next(o for o in coll.objects if o.type == 'MESH')
        off = Vector(p.get('offset', (0, 0, 0)))
        rot = [math.radians(a) for a in p.get('rot', (0, 0, 0))]
        if 'attach' in p:
            aid, joint = p['attach'].split('.', 1)
            parent = actors[aid].J[joint]
            ob.parent = parent
            ob.location = off
            ob.rotation_euler = rot
        else:
            base, _ = stage.mark(p['mark'])
            ob.location = base + off
            ob.rotation_euler = rot


# ====================================================================== Hauptschleife

def render_shot(shot):
    stage = Stage(shot)
    actors = {}
    for spec in shot.get('cast', []):
        actors[spec['id']] = Actor(stage, spec, shot['cast'])
    for ln in shot.get('lines', []):
        if ln.get('kind', 'say') == 'say' and ln['who'] in actors:
            actors[ln['who']].lines.append(ln)
    place_props(stage, actors, shot.get('props'))
    cam, cam_at = build_camera(stage, actors, shot.get('camera', {}))
    mot = motion_fn(shot.get('motion'), shot['duration'])
    jolt = jolt_fn(shot.get('jolt'))
    mode = (shot.get('motion') or {}).get('mode', 'env')

    frames = stage.frames
    for f in range(1, frames + 1):
        t = (f - 1) / FPS
        cam_pos = cam_at(f, t)
        for a in actors.values():
            a.apply(f, t, actors, cam_pos, jolt)
        if mot:
            s = mot(t)
            if mode == 'train' and stage.train_root:
                stage.train_root.location.y = -s
                stage.train_root.keyframe_insert('location', frame=f)
            else:
                stage.env_root.location.y = s % 600.0
                stage.env_root.keyframe_insert('location', frame=f)
    # Bewegungen ohne Glättung zwischen den Frames
    for ob in bpy.data.objects:
        ad = ob.animation_data
        if ad and ad.action:
            try:
                for fc in ad.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'LINEAR'
            except AttributeError:
                pass

    sc = stage.scene
    if SAVE_BLEND:
        c.save(os.path.join(c.ROOT, 'out', 'shots', EP_ID, f'{shot["id"]}.blend'))
    if STILLS:
        f = max(1, min(frames, int(round(shot.get('still', 0.7) * frames))))
        sc.frame_set(f)
        sc.render.filepath = os.path.join(STILL_DIR, f'{shot["id"]}.jpg')
        bpy.ops.render.render(write_still=True)
        print('still', sc.render.filepath, flush=True)
        return None
    sc.render.filepath = os.path.join(OUT, shot['id'], '')
    sc.render.use_file_extension = True
    bpy.ops.render.render(animation=True)
    print('shot fertig', shot['id'], flush=True)
    return dict(frames=frames, step=STEP, res=list(c.QUALITY[QUALITY]['res']), quality=QUALITY)


def main():
    os.makedirs(OUT, exist_ok=True)
    man_path = os.path.join(OUT, 'manifest.json')
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {'shots': {}}
    for shot in EP['shots']:
        if ONLY and shot['id'] not in ONLY:
            continue
        info = render_shot(shot)
        if info:
            manifest['shots'][shot['id']] = info
            json.dump(manifest, open(man_path, 'w'), indent=2)


main()
