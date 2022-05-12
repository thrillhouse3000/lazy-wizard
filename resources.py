from fractions import Fraction

creature_types = ['any', 'aberration', 'beast', 'celestial', 'construct', 'dragon', 'elemental', 'fey', 'fiend', 'giant', 'humanoid', 'monstrosity', 'ooze', 'plant', 'swarm', 'undead']

terrain_types = ['arctic', 'aquatic', 'coastal', 'desert', 'forest', 'grassland', 'mountain', 'swamp', 'underdark', 'urban']

num_of_monsters = {
    '1': 1,
    '2': 1.5,
    '3': 2,
    '4': 2,
    '5': 2,
    '6': 2,
    '7': 2.5,
    '8': 2.5,
    '9': 2.5,
    '10': 2.5,
    '11': 3,
    '12': 3,
    '13': 3,
    '14': 3,
    '15': 4,
}

exp_to_cr = [
    (0, 10),
    (1/8, 25),
    (1/4, 50),
    (1/2, 100),
    (1, 200),
    (2, 450),
    (3, 700),
    (4, 1100),
    (5, 1800),
    (6, 2300),
    (7, 2900),
    (8, 3900),
    (9, 5000),
    (10, 5900),
    (11, 7200),
    (12, 8400),
    (13, 10000),
    (14, 11500),
    (15, 13000),
    (16, 15000),
    (17, 18000),
    (18, 20000),
    (19, 22000),
    (20, 25000),
    (21, 33000),
    (22, 41000),
    (23, 50000),
    (24, 62000),
    (25, 75000),
    (26, 90000),
    (27, 105000),
    (28, 120000),
    (29, 135000),
    (30, 155000)
]

cr_list = [i for i in reversed(exp_to_cr)]

def calc_crs(xp, mod, limit):
    crs = []
    i = 0
    n = 1
    m = mod
    while i < len(cr_list):
        cr = cr_list[i][0]
        exp_val = cr_list[i][1]
        multiplier = num_of_monsters[str(n)]
        if n <= limit and (xp * m) - (exp_val * multiplier) >= 0:
            if cr > 0 and cr < 1:
                crs.append(str(Fraction(cr)))
                xp -= (exp_val * multiplier)
                m += mod
                n += 1
                i -= 1
            else:
                crs.append(str(cr))    
                xp -= (exp_val * multiplier)
                m += mod
                n += 1
                i -= 1
        else:
            i += 1
    return crs  

def convert_xp_to_cr(xp, density):
    """take XP budget and convert to corresponding monster CRs"""
    if density == 'one':
        return calc_crs(xp, 1, 1)
    elif density == 'few':
        return calc_crs(xp, 0.35, 5)
    elif density == 'many':
        return calc_crs(xp, 0.25, 10)
    elif density == 'horde':
        return calc_crs(xp, 0.1, 15)
    
