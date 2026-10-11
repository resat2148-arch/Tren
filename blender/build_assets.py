"""Baut die Asset-Bibliothek einmalig und speichert sie als .blend:

  assets/sets/umgebung.blend      Feld, Gleis, Masten, Bäume
  assets/sets/<wagen>.blend       wagen5, wagen6, wagen7 (Bistro), wagen1 (1. Klasse)
  assets/sets/aussen.blend        der Zug von außen
  assets/props/props.blend        Becher, Laptop, Handy, Karte, Brezel
  assets/characters/<id>.blend    alle Figuren (siehe lib/cast.py)

Aufruf:
  blender -b -P blender/build_assets.py -- [sets|chars|props|all] [--only wagen6,platz47] [--lookdev]
  python blender/build_assets.py ...      (mit pip-Paket "bpy")
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402

from lib import common as c  # noqa: E402
from lib import world  # noqa: E402

ARGS = c.script_args()
_pos, _skip = [], False
for _a in ARGS:
    if _skip:
        _skip = False
    elif _a in ('--only', '--quality'):
        _skip = True
    elif not _a.startswith('--'):
        _pos.append(_a)
WHAT = _pos[0] if _pos else 'all'
ONLY = ARGS[ARGS.index('--only') + 1].split(',') if '--only' in ARGS else None
LOOKDEV = '--lookdev' in ARGS
QUALITY = ARGS[ARGS.index('--quality') + 1] if '--quality' in ARGS else 'preview'
LOOKDEV_DIR = os.path.join(c.ROOT, 'out', 'lookdev')


def wanted(name):
    return ONLY is None or name in ONLY


def set_path(name):
    return os.path.join(c.ASSETS, 'sets', f'{name}.blend')


def lookdev_set(name, times=('tag',)):
    """Set + Umgebung laden und jede gespeicherte Kamera rendern."""
    for t in times:
        c.reset()
        c.append_collection(set_path('umgebung'), 'ENV')
        coll = c.append_collection(set_path(name), f'SET_{name}')
        world.build_sky()
        world.apply_time(t)
        sc = c.setup_render(quality=QUALITY)
        for ob in coll.all_objects:
            if ob.type == 'CAMERA':
                sc.camera = ob
                sc.render.filepath = os.path.join(LOOKDEV_DIR, f'{name}_{ob["campreset"]}_{t}.jpg')
                bpy.ops.render.render(write_still=True)
                print('lookdev', sc.render.filepath, flush=True)


def build_sets():
    from lib import exterior, wagon
    if wanted('umgebung'):
        c.reset()
        coll = c.make_collection('ENV')
        world.build_environment(coll)
        c.save(set_path('umgebung'))
        print('gespeichert: umgebung', flush=True)
    for name, fn in wagon.WAGONS.items():
        if not wanted(name):
            continue
        c.reset()
        fn()
        c.save(set_path(name))
        print('gespeichert:', name, flush=True)
        if LOOKDEV:
            lookdev_set(name)
    if wanted('aussen'):
        c.reset()
        exterior.build_aussen()
        c.save(set_path('aussen'))
        print('gespeichert: aussen', flush=True)
        if LOOKDEV:
            lookdev_set('aussen', ('tag', 'abend', 'nacht'))


def build_props():
    from lib import props as P
    c.reset()
    coll = c.make_collection('PROPS')
    makers = {
        'becher': lambda: P.cup('becher', coll),
        'laptop': lambda: P.laptop('laptop', coll),
        'handy': lambda: P.phone('handy', coll),
        'karte100': lambda: P.card100('karte100', coll),
        'brezel': lambda: P.pretzel('brezel', coll),
    }
    for name, fn in makers.items():
        sub = c.make_collection(f'PROP_{name}')
        ob = fn()
        coll.objects.unlink(ob)
        sub.objects.link(ob)
    c.save(os.path.join(c.ASSETS, 'props', 'props.blend'))
    print('gespeichert: props', flush=True)


def build_chars():
    from lib import cast, character
    for cid, spec in cast.CAST.items():
        if not wanted(cid):
            continue
        c.reset()
        character.build(cid, spec)
        c.save(os.path.join(c.ASSETS, 'characters', f'{cid}.blend'))
        print('gespeichert:', cid, flush=True)
        if LOOKDEV:
            character.lookdev(cid, os.path.join(LOOKDEV_DIR, f'figur_{cid}.jpg'), QUALITY)


if WHAT in ('sets', 'all'):
    build_sets()
if WHAT in ('props', 'all'):
    build_props()
if WHAT in ('chars', 'all'):
    build_chars()
