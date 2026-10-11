"""Besetzung. Jede Figur wird einmal gebaut und als assets/characters/<id>.blend gespeichert."""

CAST = {
    'platz47': dict(
        name='Platz 47', shoulder=0.185, hip=0.09, scale=0.98,
        skin='#D9A27E', lips='#B86A62', eyes='#3F6B4A',
        hair=dict(style='bob', color='#3A2519'), brow='#2E1C12',
        top=dict(kind='jacket', color='#3E5A78', inner='#E8E2D6', accent='#FF9F1C'),
        pants='#2A2D33', shoes='#ECEAE4', sneakers=True,
        extras=['scarf'], scarf='#C9731A',
    ),
    'zugchef': dict(
        name='Der Zugchef', shoulder=0.21, hip=0.095, belly=0.05, scale=1.03,
        skin='#C98A66', lips='#A85E55', eyes='#4B3A2A', jaw=0.18,
        hair=dict(style='short', color='#4A3A2E'), brow='#3A2B20',
        top=dict(kind='uniform', color='#1E3B44', inner='#DDE3E6', accent='#FF9F1C', tie='#1E3B44'),
        pants='#1E3B44', shoes='#151515',
        extras=['cap', 'mustache'],
    ),
    'rentner': dict(
        name='Der Rentner (BahnCard 100)', shoulder=0.2, hip=0.095, belly=0.07, scale=0.97,
        skin='#DDAA8A', lips='#B07068', eyes='#5A7A96', jaw=0.15, brow_thick=0.012,
        hair=dict(style='bald_ring', color='#C9C6C0'), brow='#B9B5AE',
        top=dict(kind='jacket', color='#B8A47E', inner='#8FA6B8', accent='#7A6A50'),
        pants='#55524C', shoes='#4A3423',
        extras=['glasses', 'mustache'], glasses_color='#6B5A44',
    ),
    'businessmann': dict(
        name='Businessmann', shoulder=0.21, hip=0.09, scale=1.04,
        skin='#B97F5A', lips='#9C5A50', eyes='#3A2A1E', jaw=0.3,
        hair=dict(style='slick', color='#1F1712'),
        top=dict(kind='blazer', color='#2B2F38', inner='#DCE6F0', tie='#7A2A2A'),
        pants='#2B2F38', shoes='#1A1310',
    ),
    'studentin': dict(
        name='Studentin', shoulder=0.18, hip=0.09, scale=0.95,
        skin='#8D5A3B', lips='#7A4038', eyes='#2A1A10',
        hair=dict(style='curly', color='#1A110C'), brow='#1A110C',
        top=dict(kind='hoodie', color='#6B8F5E', inner='#EDE7DA'),
        pants='#33405A', shoes='#E9E6E0', sneakers=True,
        extras=['glasses'], glasses_color='#C9302C',
    ),
    # Statisten
    'fahrgast_a': dict(
        name='Fahrgast A', shoulder=0.2, hip=0.09, scale=1.0,
        skin='#DBA585', hair=dict(style='short', color='#8A6A45'),
        top=dict(kind='sweater', color='#7A2E35'), pants='#3B4250', shoes='#2A2A2A', extras=['beard'],
    ),
    'fahrgast_b': dict(
        name='Fahrgast B', shoulder=0.18, hip=0.09, scale=0.96,
        skin='#E2AE8E', hair=dict(style='ponytail', color='#C79A5A'),
        top=dict(kind='cardigan', color='#CDB79A', inner='#3D4A5C'), pants='#2C2F3A', shoes='#6B4A33',
    ),
    'fahrgast_c': dict(
        name='Fahrgast C', shoulder=0.2, hip=0.09, belly=0.04, scale=1.0,
        skin='#A8724F', hair=dict(style='short', color='#2A2420'),
        top=dict(kind='hoodie', color='#3A3F47', inner='#C9C4BA'), pants='#4A4F57', shoes='#E6E3DC', sneakers=True,
        extras=['beanie'], beanie='#2F6B6B',
    ),
    'fahrgast_d': dict(
        name='Fahrgast D', shoulder=0.18, hip=0.095, scale=0.94,
        skin='#DDAE90', hair=dict(style='bob', color='#8E8A85', bun=True),
        top=dict(kind='cardigan', color='#5C6E8A', inner='#EEE8DD'), pants='#5A5048', shoes='#2A2420',
        extras=['glasses'],
    ),
}
