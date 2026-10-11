"""Die Wagen als Sets. Jeder Wagen: Innenraum 20 m lang, Boden z=0, Fahrtrichtung -Y.

Marken (MARK_*) zeigen, wo Figuren sitzen/stehen können:
  Tischgruppen  T{n}{L|R}{a|b|c|d}  a=Fenster vorwärts, b=Gang vorwärts, c=Fenster rückwärts, d=Gang rückwärts
  Reihen        R{n}{L|R}{w|a}      w=Fenster, a=Gang
  Gang          G{y}                stehend im Gang, y in Metern (z. B. G0, G-3, G4)
  Bistro        BAR_*, STEH*, ...
"""
import math

import bpy

from . import common as c
from . import props as P

L = 20.0           # Länge Innenraum
HALF_W = 1.38      # Innenwand
WIN_LO, WIN_HI = 0.80, 1.62
WINDOW_W = 1.55
WINDOW_PITCH = 1.9
WINDOWS = [i * WINDOW_PITCH for i in range(-4, 5)]   # Fenstermitten (y)


class WagonKit:
    def __init__(self, cid, palette):
        self.cid = cid
        self.coll = c.make_collection(f'SET_{cid}')
        self.proto = c.make_collection(f'PROTO_{cid}', self.coll)
        self.marks = c.make_collection(f'MARKS_{cid}', self.coll)
        self.cams = c.make_collection(f'CAMS_{cid}', self.coll)
        self.pal = palette
        self.m = dict(
            wall=c.mat(f'Wand_{cid}', palette.get('wall', '#D9D7D1'), rough=0.55, bump=0.05),
            panel=c.mat(f'Paneel_{cid}', palette.get('panel', '#C4C2BC'), rough=0.45),
            ceiling=c.mat(f'Decke_{cid}', '#ECEBE6', rough=0.6),
            floor=c.mat(f'Boden_{cid}', palette.get('floor', '#4A4F57'), rough=0.6, bump=0.08, bump_scale=40,
                        noise_color=0.12),
            lower=c.mat(f'Wand_unten_{cid}', palette.get('lower', '#8F949A'), rough=0.5),
            seam=c.mat('Fuge', '#9A9890', rough=0.6),
            frame=c.mat('Fensterrahmen', '#3B3F45', rough=0.5),
            rubber=c.mat('Gummi', '#151618', rough=0.8),
            metal=c.mat('Edelstahl', '#A9ADB2', rough=0.3, metal=1.0),
            rack=c.mat('Gepaeckablage', '#8E959D', rough=0.25, metal=0.5),
            glass=c.mat('Tuerglas', '#1D2730', rough=0.05, metal=0.3, coat=1.0),
            duct=c.mat('Heizkanal', '#7C8087', rough=0.5),
            accent=c.mat('Akzent_amber', '#FF9F1C', rough=0.4),
        )
        self.lightstrip = c.mat(f'Lichtband_{cid}', '#FFFFFF', rough=0.5, emit=palette.get('light', '#FFE9C8'),
                                emit_strength=3.0)
        self.lightstrip['emit_base'] = 3.0

    # ---------------------------------------------------------- Hülle
    def shell(self, windows_left=True, windows_right=True, closed_right=None):
        """closed_right: (y0, y1)-Bereich ohne Fenster auf der rechten Seite (z. B. Bistro-Theke)."""
        m, coll = self.m, self.coll
        c.box('Boden', (HALF_W * 2, L, 0.04), (0, 0, -0.02), m['floor'], coll)
        for s, has_win in ((-1, windows_left), (1, windows_right)):
            x = s * (HALF_W + 0.04)
            c.box(f'Wand_unten_{s}', (0.08, L, WIN_LO), (x, 0, WIN_LO / 2), m['lower'], coll)
            c.box(f'Wand_oben_{s}', (0.08, L, 2.05 - WIN_HI), (x, 0, (WIN_HI + 2.05) / 2), m['wall'], coll)
            c.box(f'Heizkanal_{s}', (0.12, L, 0.24), (s * (HALF_W - 0.06), 0, 0.12), m['duct'], coll, bevel=0.02)
            c.box(f'Fensterbank_{s}', (0.1, L, 0.025), (s * (HALF_W - 0.05), 0, WIN_LO), m['panel'], coll,
                  bevel=0.008)
            # Pfeiler + Fensterlaibungen
            edges = []
            for wy in WINDOWS:
                closed = (not has_win) or (s == 1 and closed_right and closed_right[0] <= wy <= closed_right[1])
                if closed:
                    continue
                edges.append((wy - WINDOW_W / 2, wy + WINDOW_W / 2))
                fx = s * (HALF_W - 0.02)
                h = WIN_HI - WIN_LO
                c.box(f'Laibung_o_{s}_{wy}', (0.1, WINDOW_W + 0.06, 0.05), (fx, wy, WIN_HI - 0.01), m['frame'], coll,
                      bevel=0.012)
                c.box(f'Laibung_u_{s}_{wy}', (0.1, WINDOW_W + 0.06, 0.04), (fx, wy, WIN_LO + 0.02), m['frame'], coll,
                      bevel=0.012)
                for e in (-1, 1):
                    c.box(f'Laibung_s_{s}_{wy}_{e}', (0.1, 0.05, h), (fx, wy + e * (WINDOW_W / 2 + 0.005),
                                                                       (WIN_LO + WIN_HI) / 2), m['frame'], coll,
                          bevel=0.012)
            y = -L / 2
            for a, b in edges + [(L / 2, L / 2)]:
                if a - y > 0.01:
                    c.box(f'Pfeiler_{s}_{y:.2f}', (0.08, a - y, WIN_HI - WIN_LO), (x, (a + y) / 2,
                                                                                 (WIN_LO + WIN_HI) / 2), m['wall'],
                          coll)
                y = b
        # Decke (Bogen) + Lichtbänder
        prof = []
        for i in range(25):
            t = math.pi * i / 24
            prof.append((-HALF_W * math.cos(t) * 1.03, 2.05 + 0.27 * math.sin(t)))
        c.profile_extrude('Decke', prof, L, material=m['ceiling'], coll=self.coll)
        for s in (-1, 1):
            xs = s * 0.62
            zs = 2.05 + 0.27 * math.sqrt(max(0, 1 - (xs / (HALF_W * 1.03)) ** 2)) - 0.015
            c.box(f'Lichtband_{s}', (0.07, L - 0.6, 0.012), (xs, 0, zs), self.lightstrip, coll,
                  rot=(0, s * 0.22, 0))
        for i in range(-5, 6):
            c.profile_extrude(f'Deckenfuge_{i}', [(x * 0.985, z - 0.004) for x, z in prof], 0.012, (0, i * 1.9, 0),
                              m['seam'], coll)
        # Gepäckablagen
        for s in (-1, 1):
            c.box(f'Ablage_{s}', (0.36, L - 1.2, 0.025), (s * (HALF_W - 0.18), 0, 1.93), m['rack'], coll,
                  bevel=0.008)
            c.cyl(f'Ablage_rohr_{s}', 0.014, 0.014, L - 1.2, (s * (HALF_W - 0.37), 0, 1.955), m['metal'], coll,
                  rot=(math.pi / 2, 0, 0), verts=12)
            for wy in WINDOWS + [WINDOWS[0] - 0.95, WINDOWS[-1] + 0.95]:
                c.box(f'Ablage_halter_{s}_{wy}', (0.36, 0.03, 0.12), (s * (HALF_W - 0.18), wy + WINDOW_PITCH / 2,
                                                                       1.88), m['frame'], coll, bevel=0.01)
        # Stirnwände mit Glastür + Anzeige
        for e in (-1, 1):
            y = e * (L / 2 + 0.05)
            c.box(f'Stirn_l_{e}', (HALF_W - 0.5, 0.1, 2.3), (-(HALF_W + 0.5) / 2 - 0.0, y, 1.15), m['wall'], coll)
            c.box(f'Stirn_r_{e}', (HALF_W - 0.5, 0.1, 2.3), ((HALF_W + 0.5) / 2, y, 1.15), m['wall'], coll)
            c.box(f'Stirn_o_{e}', (1.0, 0.1, 0.3), (0, y, 2.15), m['wall'], coll)
            c.box(f'Tuer_{e}', (1.0, 0.03, 2.0), (0, y, 1.0), m['glass'], coll)
            c.box(f'Tuerrahmen_{e}', (1.06, 0.12, 0.05), (0, y - e * 0.0, 2.0), m['frame'], coll, bevel=0.01)
            disp = P.led_display(f'Anzeige_{e}', coll)
            disp.location = (0, y - e * 0.09, 2.17 - 0.05)
            disp.rotation_euler = (0, 0, 0 if e > 0 else math.pi)
            t = c.text(f'DISPLAY_TEXT_{e}', 'HAMBURG HBF  +20', 0.075, (0, y - e * 0.13, 2.115), P.led_material(),
                       coll, rot=(math.pi / 2, 0, 0 if e > 0 else math.pi))
            t['display'] = True
        # Deckenleuchten (Flächenlichter, Stärke über Tageszeit)
        for i, y in enumerate((-6.5, 0.0, 6.5)):
            ld = bpy.data.lights.new(f'Deckenlicht_{i}', 'AREA')
            ld.shape = 'RECTANGLE'
            ld.size, ld.size_y = 0.9, 5.5
            ld.color = c.hex_rgb(self.pal.get('light', '#FFE9C8'))
            ld.energy = 260
            lo = bpy.data.objects.new(f'Deckenlicht_{i}', ld)
            self.coll.objects.link(lo)
            lo.location = (0, y, 2.22)
            lo['interior'] = 260.0
        # Gang-Marken
        for gy in range(-8, 9):
            c.mark(self.marks, f'G{gy}', (0, gy, 0), 0, 'stand')

    # ---------------------------------------------------------- Bestuhlung
    def seat_rows(self, y0, y1, fabric, accent, label_start=11, pitch=0.95):
        unit = P.seat_unit(f'{self.cid}_reihe', fabric, accent, self.proto)
        self._hide_proto(unit)
        n = 0
        y = y1 - 0.4
        while y > y0:
            n += 1
            for s, side in ((-1, 'L'), (1, 'R')):
                ux = s * 0.86
                c.linked_copy(unit, f'Reihe_{n}{side}', (ux, y, 0), coll=self.coll)
                win, aisle = ux + s * 0.25, ux - s * 0.25
                c.mark(self.marks, f'R{n}{side}w', (win, y, 0.48), 0)
                c.mark(self.marks, f'R{n}{side}a', (aisle, y, 0.48), 0)
            y -= pitch
        return n

    def table_bays(self, centers, fabric, accent, sides=('L', 'R')):
        unit = P.seat_unit(f'{self.cid}_tischplatz', fabric, accent, self.proto, airline=False)
        tab = P.table(f'{self.cid}_tisch', self.proto, top=self.pal.get('table', '#B9AE9C'))
        self._hide_proto(unit, tab)
        for n, yc in enumerate(centers, 1):
            for s, side in ((-1, 'L'), (1, 'R')):
                if side not in sides:
                    continue
                ux = s * 0.86
                c.linked_copy(unit, f'Tisch{n}{side}_vor', (ux, yc + 0.95, 0), coll=self.coll)
                c.linked_copy(unit, f'Tisch{n}{side}_rueck', (ux, yc - 0.95, 0), (0, 0, math.pi), coll=self.coll)
                c.linked_copy(tab, f'Tisch{n}{side}', (s * 0.88, yc, 0), (0, 0, 0 if s < 0 else math.pi),
                              coll=self.coll)
                win, aisle = ux + s * 0.25, ux - s * 0.25
                c.mark(self.marks, f'T{n}{side}a', (win, yc + 0.95, 0.48), 0)
                c.mark(self.marks, f'T{n}{side}b', (aisle, yc + 0.95, 0.48), 0)
                c.mark(self.marks, f'T{n}{side}c', (win, yc - 0.95, 0.48), 180)
                c.mark(self.marks, f'T{n}{side}d', (aisle, yc - 0.95, 0.48), 180)
                c.mark(self.marks, f'T{n}{side}tisch', (s * 0.88, yc, 0.76), 0, 'table')

    def seat_numbers(self, plates):
        """Platznummern-Schildchen an der Gepäckablage: [(x, y, "47 48"), ...]."""
        plate = c.mat('Nummernschild', '#1C1F23', rough=0.4)
        ink = c.mat('Nummer', '#F2EFE8', rough=0.5)
        for x, y, label in plates:
            c.box(f'Schild_{label}', (0.012, 0.16, 0.05), (x, y, 1.885), plate, self.coll, bevel=0.004)
            c.text(f'Nummer_{label}', label, 0.03, (x - math.copysign(0.008, x), y, 1.885), ink, self.coll,
                   rot=(math.pi / 2, 0, -math.copysign(math.pi / 2, x)))

    def luggage(self, seed, density=0.5):
        rnd = c.seeded(seed)
        colors = ['#2E3440', '#6B2D2D', '#3C5A73', '#7A7368', '#1F1F22', '#8C6A3A', '#355E3B', '#C9C4BA']
        protos = []
        for i, col in enumerate(colors):
            if i % 2:
                protos.append(P.suitcase(f'{self.cid}_koffer{i}', self.proto, col,
                                         (0.42, 0.25, rnd.uniform(0.45, 0.65))))
            else:
                protos.append(P.bag(f'{self.cid}_tasche{i}', self.proto, col))
        self._hide_proto(*protos)
        for s in (-1, 1):
            y = -L / 2 + 1.0
            while y < L / 2 - 1.0:
                if rnd.random() < density:
                    p = rnd.choice(protos)
                    lying = 'koffer' in p.name
                    ob = c.linked_copy(p, f'Gepaeck_{s}_{y:.1f}', (s * (HALF_W - 0.2), y, 1.945),
                                       (math.pi / 2 if lying else 0, 0, rnd.uniform(-0.15, 0.15) + math.pi / 2),
                                       coll=self.coll)
                    if lying:
                        ob.location.z += 0.13
                y += rnd.uniform(0.6, 1.4)

    def _hide_proto(self, *obs):
        for o in obs:
            o.hide_render = True
            o.hide_viewport = True

    def cam(self, name, loc, target, lens=28):
        return c.camera_preset(self.cams, name, loc, target, lens)


# ============================================================== die vier Wagen

def build_wagen5():
    """Großraum 2. Klasse, 2+2 Reihen. Revier des BahnCard-100-Rentners."""
    k = WagonKit('wagen5', dict(wall='#D8D6D0', floor='#4C525B', light='#FFF1DC'))
    k.shell()
    fabric = c.mat('Bezug_w5', '#2F3D55', rough=0.85, fabric=0.6)
    accent = c.mat('Kopfteil_w5', '#9AA3AD', rough=0.8, fabric=0.4)
    n = k.seat_rows(-9.2, 9.2, fabric, accent)
    k.seat_numbers([(s * (HALF_W - 0.02), y, f'{21 + 4 * i + (s > 0) * 2} {22 + 4 * i + (s > 0) * 2}')
                    for i, y in enumerate((-6, -2, 2, 6)) for s in (-1, 1)])
    k.luggage(5)
    for i in range(3):
        sock = P.socket(f'w5_steckdose_{i}', k.coll)
        sock.location = (-HALF_W + 0.01, -5 + i * 5, 0.55)
        sock.rotation_euler = (0, 0, -math.pi / 2)
    k.cam('weit_gang', (0.0, 9.2, 1.55), (0, -2, 1.05), 22)
    k.cam('weit_gang_rueck', (0.0, -9.2, 1.55), (0, 2, 1.05), 22)
    return k


def build_wagen6():
    """2. Klasse mit Tischgruppen. Platz 47 sitzt am Tisch T3La."""
    k = WagonKit('wagen6', dict(wall='#DAD8D2', floor='#475059', light='#FFEBD0', table='#BFB4A2'))
    k.shell()
    fabric = c.mat('Bezug_w6', '#1E5257', rough=0.85, fabric=0.6)
    accent = c.mat('Kopfteil_w6', '#A9B2B2', rough=0.8, fabric=0.4)
    k.table_bays([-7.6, -3.8, 0.0, 3.8, 7.6], fabric, accent)
    # Tisch 3 links trägt die Plätze 47/48 (Platz 47 = Fenster vorwärts, T3La)
    k.seat_numbers([(s * (HALF_W - 0.02), y, f'{37 + 4 * i + (s > 0) * 2 + 2} {38 + 4 * i + (s > 0) * 2 + 2}')
                    for i, y in enumerate((-7.6, -3.8, 0.0, 3.8, 7.6)) for s in (-1, 1)])
    k.luggage(6)
    for n, yc in enumerate([-7.6, -3.8, 0.0, 3.8, 7.6]):
        for s in (-1, 1):
            sock = P.socket(f'w6_steckdose_{n}_{s}', k.coll)
            sock.location = (s * (HALF_W - 0.01), yc, 0.70)
            sock.rotation_euler = (0, 0, s * math.pi / 2)
    k.cam('weit_gang', (0.0, 9.2, 1.55), (0, -2, 1.05), 22)
    k.cam('tisch3_totale', (0.55, 2.3, 1.45), (-0.9, -0.2, 0.95), 24)
    return k


def build_wagen7():
    """Bordbistro (vordere Hälfte, y<0) + Bistrotische (hintere Hälfte)."""
    k = WagonKit('wagen7', dict(wall='#D3CBBE', floor='#3F3A36', light='#FFDDB0', table='#6E4B35',
                                panel='#B9A991'))
    k.shell(closed_right=(-9.5, -1.5))
    wood = c.mat('Holz_dunkel', '#4A3324', rough=0.45, bump=0.15, bump_scale=30, noise_color=0.4)
    stone = c.mat('Theke_platte', '#2B2B2D', rough=0.2, coat=0.6, noise_color=0.3)
    steel = k.m['metal']
    glass = c.mat('Vitrine_glas', '#DDE6EE', rough=0.02, alpha=0.18)
    coll = k.coll
    # Theke (Kundenseite x<0.7), Gang fürs Personal, Rückbuffet an der Wand
    c.box('Theke', (0.6, 6.0, 1.0), (0.42, -5.6, 0.5), wood, coll, bevel=0.02)
    c.box('Theke_platte', (0.72, 6.1, 0.05), (0.40, -5.6, 1.025), stone, coll, bevel=0.01)
    c.box('Theke_sockel', (0.62, 6.0, 0.08), (0.42, -5.6, 0.04), c.mat('Sockel', '#1C1C1E', rough=0.6), coll)
    c.box('Rueckbuffet', (0.3, 7.4, 0.95), (HALF_W - 0.15, -5.6, 0.475), wood, coll, bevel=0.015)
    c.box('Rueckbuffet_platte', (0.32, 7.4, 0.04), (HALF_W - 0.16, -5.6, 0.97), steel, coll)
    # Vitrine mit Brezeln
    c.box('Vitrine_boden', (0.5, 1.4, 0.02), (0.42, -4.2, 1.06), steel, coll)
    c.box('Vitrine_glas', (0.52, 1.42, 0.32), (0.42, -4.2, 1.23), glass, coll, bevel=0.01)
    vit_light = c.mat('Vitrinenlicht', '#FFFFFF', emit='#FFE2B0', emit_strength=4.0)
    vit_light['emit_base'] = 4.0
    c.box('Vitrine_licht', (0.4, 1.3, 0.01), (0.42, -4.2, 1.385), vit_light, coll)
    br = P.pretzel('w7_brezel', k.proto)
    k._hide_proto(br)
    rnd = c.seeded(12)
    for i in range(12):
        row, col = divmod(i, 6)
        c.linked_copy(br, f'Brezel_{i}', (0.32 + row * 0.2 + rnd.uniform(-0.02, 0.02), -4.75 + col * 0.21, 1.075),
                      (0, 0, rnd.uniform(-0.3, 0.3)), coll=coll)
    # Kaffeemaschine
    chrome = c.mat('Chrom', '#D5D8DC', rough=0.12, metal=1.0)
    black = c.mat('Maschine_schwarz', '#151517', rough=0.35)
    disp = c.mat('Maschine_display', '#000000', emit='#FF9F1C', emit_strength=3.0)
    disp['emit_base'] = 3.0
    disp['emit_follows_time'] = 0
    c.box('Kaffeemaschine', (0.42, 0.62, 0.62), (HALF_W - 0.2, -7.2, 1.30), black, coll, bevel=0.03)
    c.box('Kaffeemaschine_front', (0.02, 0.5, 0.18), (HALF_W - 0.42, -7.2, 1.45), chrome, coll, bevel=0.005)
    c.box('Kaffeemaschine_display', (0.005, 0.12, 0.05), (HALF_W - 0.435, -7.0, 1.52), disp, coll)
    for dy in (-0.1, 0.1):
        c.cyl(f'Bruehgruppe_{dy}', 0.03, 0.03, 0.08, (HALF_W - 0.42, -7.2 + dy, 1.2), chrome, coll)
    # Kasse
    c.box('Kasse', (0.25, 0.3, 0.06), (0.5, -6.5, 1.08), black, coll, bevel=0.01)
    scr = c.mat('Kasse_screen', '#0A0D12', emit='#A8C8F0', emit_strength=1.5)
    scr['emit_base'] = 1.5
    scr['emit_follows_time'] = 0
    c.box('Kasse_screen', (0.02, 0.26, 0.18), (0.45, -6.5, 1.2), scr, coll, rot=(0, -0.35, 0))
    # Regal mit Flaschen und Bechern
    shelf = c.mat('Regal', '#2E2621', rough=0.5)
    for zi, z in enumerate((1.45, 1.75)):
        c.box(f'Regal_{zi}', (0.22, 5.0, 0.025), (HALF_W - 0.11, -4.8, z), shelf, coll)
        for j in range(18):
            col = ['#3E6B3A', '#7A2A20', '#C9A23A', '#E8E4DC'][(j + zi) % 4]
            c.cyl(f'Flasche_{zi}_{j}', 0.032, 0.03, 0.22, (HALF_W - 0.11, -7.0 + j * 0.25, z + 0.11),
                  c.mat(f'Flasche_{col}', col, rough=0.15, coat=0.8), coll, verts=12)
    # Menütafeln (eigenes Design)
    board = c.mat('Menue_grund', '#121315', rough=0.4)
    c.box('Menue', (0.03, 2.4, 0.5), (HALF_W - 0.02, -2.6, 1.72), board, coll, bevel=0.01)
    ink = c.mat('Menue_schrift', '#F2EFE8', emit='#F2EFE8', emit_strength=1.2)
    ink['emit_base'] = 1.2
    led = P.led_material()
    rot = (math.pi / 2, 0, -math.pi / 2)
    c.text('Menue_titel', 'BORDBISTRO', 0.09, (HALF_W - 0.045, -2.6, 1.88), led, coll, rot=rot)
    for i, line in enumerate(('Kaffee ............ 3,90', 'Brezel ............ 2,80', 'Bier 0,33 ......... 4,50')):
        c.text(f'Menue_{i}', line, 0.055, (HALF_W - 0.045, -2.6, 1.76 - i * 0.09), ink, coll, rot=rot)
    # Stehtische mit Steckdosen an der linken Fensterseite
    for i, y in enumerate((-8.0, -5.6, -3.2)):
        c.box(f'Stehtisch_{i}', (0.36, 1.3, 0.04), (-HALF_W + 0.18, y, 1.06), stone, coll, bevel=0.01)
        c.box(f'Stehtisch_stuetze_{i}', (0.05, 0.06, 1.04), (-HALF_W + 0.33, y, 0.52), steel, coll)
        sock = P.socket(f'Steh_steckdose_{i}', coll)
        sock.location = (-HALF_W + 0.01, y + 0.35, 1.15)
        sock.rotation_euler = (0, 0, -math.pi / 2)
        sock['socket'] = i + 1
        c.mark(k.marks, f'STEH{i + 1}', (-0.62, y, 0), -90, 'stand')
        c.mark(k.marks, f'STEH{i + 1}b', (-0.62, y + 0.6, 0), -90, 'stand')
    # Personal und Kundschaft an der Theke
    c.mark(k.marks, 'BAR_personal', (0.98, -5.6, 0), -90, 'stand')
    for i, y in enumerate((-7.0, -5.6, -4.2)):
        c.mark(k.marks, f'BAR{i + 1}', (-0.12, y, 0), 90, 'stand')
    # hintere Hälfte: Bistrotische
    fabric = c.mat('Bezug_w7', '#6E3B26', rough=0.6, coat=0.15)
    accent = c.mat('Kopfteil_w7', '#C9B79A', rough=0.7, fabric=0.3)
    k.table_bays([2.2, 6.0], fabric, accent)
    k.luggage(7, density=0.35)
    k.cam('bistro_totale', (-0.6, 0.2, 1.6), (0.3, -6.0, 1.05), 22)
    k.cam('theke', (-0.75, -3.0, 1.35), (0.45, -5.0, 1.15), 32)
    return k


def build_wagen_1klasse():
    """1. Klasse, 2+1 Leder, Glastrennwand mit Schiebetür (Tür offen/zu per DOOR_1K)."""
    k = WagonKit('wagen1', dict(wall='#D9D2C6', floor='#2C2723', light='#FFE2BA', table='#6A4A33',
                                panel='#B5A48C'))
    k.shell()
    leather = c.mat('Leder_1k', '#6B3F2A', rough=0.45, coat=0.2, bump=0.15, bump_scale=200)
    accent = c.mat('Kopfteil_1k', '#E3DCCF', rough=0.7, fabric=0.3)
    carpet = c.mat('Teppich_1k', '#3A2F2A', rough=0.95, fabric=0.5)
    c.box('Teppich', (2.2, 15.5, 0.012), (0, 2.0, 0.006), carpet, k.coll)
    double = P.seat_unit('w1_doppel', leather, accent, k.proto, n=2, width=0.56, airline=False, shell='#5A4E44')
    single = P.seat_unit('w1_einzel', leather, accent, k.proto, n=1, width=0.62, airline=False, shell='#5A4E44')
    tab = P.table('w1_tisch', k.proto, top='#6A4A33')
    k._hide_proto(double, single, tab)
    for n, yc in enumerate([-2.0, 2.0, 6.0], 1):
        c.linked_copy(double, f'1K_{n}L_vor', (-0.82, yc + 1.0, 0), coll=k.coll)
        c.linked_copy(double, f'1K_{n}L_rueck', (-0.82, yc - 1.0, 0), (0, 0, math.pi), coll=k.coll)
        c.linked_copy(single, f'1K_{n}R_vor', (1.03, yc + 1.0, 0), coll=k.coll)
        c.linked_copy(single, f'1K_{n}R_rueck', (1.03, yc - 1.0, 0), (0, 0, math.pi), coll=k.coll)
        c.linked_copy(tab, f'1K_tisch_{n}L', (-0.86, yc, 0), coll=k.coll)
        c.linked_copy(tab, f'1K_tisch_{n}R', (1.0, yc, 0), (0, 0, math.pi), coll=k.coll)
        for side, xs in (('L', (-1.1, -0.54)), ('R', (1.03,))):
            for j, x in enumerate(xs):
                tag = 'ab'[j]
                c.mark(k.marks, f'K{n}{side}{tag}', (x, yc + 1.0, 0.48), 0)
                c.mark(k.marks, f'K{n}{side}{"cd"[j]}', (x, yc - 1.0, 0.48), 180)
    # Leselampen
    brass = c.mat('Messing', '#B08D57', rough=0.3, metal=1.0)
    lamp = c.mat('Leselampe', '#FFFFFF', emit='#FFD9A0', emit_strength=8.0)
    lamp['emit_base'] = 8.0
    for yc in (-2.0, 2.0, 6.0):
        for s in (-1, 1):
            c.cyl(f'Lampe_{yc}_{s}', 0.05, 0.035, 0.08, (s * (HALF_W - 0.06), yc, 1.72), brass, k.coll,
                  rot=(0, s * 1.2, 0))
            c.sphere(f'Lampe_licht_{yc}_{s}', (0.03, 0.03, 0.02), (s * (HALF_W - 0.1), yc, 1.69), lamp, k.coll)
    # Glastrennwand mit Schiebetür und großer "1"
    frame = k.m['frame']
    glass = c.mat('Trennglas', '#C9D6DE', rough=0.03, alpha=0.22)
    c.box('Trennwand_l', (HALF_W - 0.45, 0.06, 2.1), (-(HALF_W + 0.45) / 2, -4.6, 1.05), glass, k.coll)
    c.box('Trennwand_r', (HALF_W - 0.45, 0.06, 2.1), ((HALF_W + 0.45) / 2, -4.6, 1.05), glass, k.coll)
    c.box('Trennwand_rahmen', (HALF_W * 2, 0.08, 0.08), (0, -4.6, 2.1), frame, k.coll)
    door = c.box('DOOR_1K', (0.9, 0.04, 2.0), (0, -4.65, 1.0), glass, k.coll)
    door['door_open_x'] = -0.95
    c.box('Tuergriff_1k', (0.03, 0.06, 0.4), (0.38, -4.68, 1.05), brass, k.coll, parent=None)
    one = c.mat('Eins', '#E8D9B8', rough=0.3, metal=0.6)
    c.text('Schild_1', '1', 0.5, (0.8, -4.64, 1.25), one, k.coll)
    c.text('Schild_1_rueck', '1', 0.5, (0.8, -4.56, 1.25), one, k.coll, rot=(math.pi / 2, 0, math.pi))
    k.luggage(1, density=0.3)
    k.cam('weit_gang', (0.1, 9.2, 1.55), (0, -2, 1.05), 22)
    k.cam('tuer', (0.2, -8.5, 1.5), (0, -4.6, 1.2), 28)
    return k


WAGONS = {
    'wagen5': build_wagen5,
    'wagen6': build_wagen6,
    'wagen7': build_wagen7,
    'wagen1': build_wagen_1klasse,
}
