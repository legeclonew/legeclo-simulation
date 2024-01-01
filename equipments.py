import copy
from utils import deep_merge

equipments = {
    'weapon': {
        'atomical fire': {
            'equip_atk': [116],
            'equip_tec': [46],
            'atk_buffs': [0.05, 0.15],
            'def_buffs': [0.05],
        },
        'azure sword': {
            'equip_atk': [141],
            'atk_buffs': [0.1],
            'after_action': {
                'ally': {
                    'crit_rate_buffs': [[0.1, 2, 'azur sword']],
                    'crit_dmg_buffs': [[0.1, 2, 'azur sword', 'hp 80%']],
                }
            }
        },
        'beckoning staff': {
            'equip_mag': [141],
            'equip_tec': [60],
            'mag_buffs': [0.1],
            #'fixed_dmg_battle_mag': [1.5],
        },
        'bejeweled sword': {
            'equip_atk': [141],
            'equip_tec': [60],
            'atk_buffs': [0.1],
            'before_battle': {
                'ally': {
                    'dmg_dealt_buffs': [[0.1, -1, 'bejeweled sword']],
                }
            }
        },
        'blue planet': {
            'equip_atk': [116],
            'atk_buffs': [0.05],
            'battle_atk_buffs': [0.15],
            'battle_crit_rate_buffs': [0.1],
        },
        'buster cannon': {
            'equip_atk': [116],
            'equip_tec': [46],
            'atk_buffs': [0.1],
            'crit_rate_buffs': [0.05],
        },
        'crimson lotus sword': {
            'equip_atk': [116],
            'equip_tec': [46],
            'atk_buffs': [0.05],
            'before_battle': {
                'enemy': {
                    'dmg_res_buffs': [[-0.2, 1, 'crimson']],
                }
            }
        },
        'double longshot': {
            'equip_atk': [141],
            'equip_tec': [60],
            'atk_buffs': [0.1],
            'aoe_skill_dmg_dealt_buffs': [0.1],
        },
        'double-edged spear': {
            'equip_atk': [131],
            'atk_buffs': [0.1],
            'crit_dmg_buffs': [0.15],
            'before_battle': {
                'ally': {
                    'crit_rate_buffs': [[0.05 * 4, -1, 'double-edged spear']],
                }
            }
        },
        'elder blade': {
            'equip_atk': [141],
            'atk_buffs': [0.1],
            'st_skill_dmg_dealt_buffs': [0.1],
            'after_defeat': {
                'ally': {
                    'mov_buffs': [[1, 2, 'elder blade']],
                }
            }
        },
        'executioner': {
            'equip_atk': [141],
            'equip_tec': [60],
            'atk_buffs': [0.1],
            'mag_buffs': [0.1],
            'skill_dmg_dealt_buffs': [[0.15, 99, 'executioner', '4 buff']],
        },
        "expert's staff": {
            'equip_mag': [111],
            'atk_buffs': [0.1],
            'mag_buffs': [0.1],
        },
        'fox sword': {
            'equip_atk': [141],
            'equip_tec': [60],
            'atk_buffs': [0.1],
            'fixed_dmg_atk': [1, 1],
        },
        'gem book of magic': {
            'equip_mag': [116],
            'equip_tec': [46],
            'st_skill_dmg_dealt_buffs': [0.15],
            'before_battle': {
                'ally': {
                    'weak_debuff_success_rate': [[0.5, 2, 'GBoM']],
                }
            }
        },
        'judgement heart': {
            'equip_atk': [131],
            'crit_rate_buffs': [0.1],
            'crit_dmg_buffs': [0.15],
            'after_crit': {
                'ally': {
                    'mid_buff_success_rate': [[1, 2, 'judgement heart']],
                }
            }
        },
        'john dillinger': {
            'equip_atk': [141],
            'equip_tec': [60],
            'atk_buffs': [0.1],
            'dmg_dealt_buffs': [[0.3, 99, 'john dillinger', 'enemy within 1 sq']],
        },
        'light maxim': {
            'equip_atk': [141],
            'equip_atk': [60],
            'atk_buffs': [0.1],
            'fixed_dmg_skill': [0.1],
        },
        'moon-splitting cleaver': {
            'equip_atk': [141],
            'atk_buffs': [0.1],
            'after_skill': {
                'ally': {
                    'dmg_dealt_buffs': [[0.1, 2, 'moon-splitting cleaver']],
                }
            }
        },
        'sacred orb of the abyss': {
            'equip_mag': [116],
            'equip_tec': [46],
            'aoe_skill_dmg_dealt_buffs': [0.15],
            'after_dmg': {
                'ally': {
                    'weak_debuff_success_rate': [[0.3, 2, 'SOOTA']],
                }
            }
        },
        'striding long bow': {
            'equip_atk': [141],
            'atk_buffs': [0.1], 
            'battle_crit_rate_buffs': [0.2],
        },
        'vase of unwanted encounters': {
            'equip_mag': [141],
            'mag_buffs': [0.1],
            'after_dmg': {
                'ally': {
                    'weak_debuff_success_rate': [[1, 2, 'VOUE']],
                }
            }
        },
        'yata no kagami': {
            'equip_mag': [141],
            'mag_buffs': [0.1],
            'fixed_dmg_skill': [0.1],
        },
        'zion jabana': {
            'equip_mag': [141],
            'mag_buffs': [0.1],
            'after_battle': {
                'ally': {
                    'weak_debuff_success_rate': [[1, 2, 'zion jabana']],
                }
            }
        },
    },
    'armor': {
        "assassin's vest": {
            'equip_def': [45],
            'atk_buffs': [[0.1, 99, 'assassin vest', 'hp 80%']],
        },
        'everlasting darkness ceremonial dress': {
            'equip_def': [64],
            'battle_mag_buffs': [0.1],
        },
        'fluted armor': {
            'equip_def': [75],
            'res_buffs': [0.1],
            'fixed_dmg_battle_res': [3],
        },
        "golden conscious": {
            'equip_def': [67],
            'atk_dmg_dealt_buffs': [0.1],
            'after_defeat': {
                'ally': {
                    'atk_buffs': [[0.12, 2, 'golden conscious']],
                }
            }
        },
        "leo's heavenly armor": {
            'equip_def': [67],
            'dmg_dealt_buffs': [0.15],
        },
        "nadia's wings": {
            'equip_def': [84],
            'atk_buffs': [0.1],
            'mag_buffs': [0.1],
            'def_buffs': [0.1],
            'res_buffs': [0.1],
        },
        "origin's wings": {
            'equip_def': [84],
            'atk_buffs': [0.1],
            'mag_buffs': [0.1],
            'def_buffs': [0.1],
            'res_buffs': [0.1],
        },
        "red emperor's feather robe": {
            'equip_def': [64],
            'mag_buffs': [[0.1, 99, "REFR", 'hp 100%']],
        },
        'soldier armor': {
            'equip_def': [53],
            #'battle_atk_buffs': [[0.15, 99, 'soldier armor', 'enemy turn']]
        },
        'thymos surcoat': {
            'equip_def': [75],
            'before_battle': {
                'ally': {
                    'def_buffs': [[0.1, 1, 'thymos']],
                }
            }
        },
        "warrior princess's armor": {
            'equip_def': [75],
            'def_buffs': [0.1],
        },
        "zenith's wings": {
            'equip_def': [84],
            'atk_buffs': [0.1],
            'mag_buffs': [0.1],
            'def_buffs': [0.1],
            'res_buffs': [0.1],
        },
    },
    'helmet': {
        'elemental hat': {
            'equip_res': [77],
            'res_buffs': [0.1],
            'fixed_dmg_res': [2.5],
        },
        "emperor's spiked helm": {
            'equip_res': [57],
            'def_buffs': [0.1],
        },
        "leo's heavenly crown": {
            'equip_res': [73],
            'crit_rate_buffs': [0.5],
            'dmg_dealt_buffs': [-0.2],
        },
        "rakshasa's hairpin": {
            'equip_res': [57],
            'def_buffs': [0.05],
            'atk_dmg_res_buffs': [[0.1, 99, 'rakshasa hairpin', 'hp 80%']],
        },
        "tracking headband": {
            'equip_res': [69],
            'after_action': {
                'ally': {
                    'dmg_dealt_buffs': [[0.2, 1, 'tracking headban']],
                }
            }
        },
        'thymos helm': {
            'equip_res': [57],
            'fixed_dmg_atk': [1, 1],
        },
        "warrior princess's helm": {
            'equip_res': [57],
            'after_action': {
                'enemy': {
                    'def_buffs': [[-0.2, 1, 'WPH']],
                }
            }
        },
    },
    'accessory': {
        'crimson pendant': {
            'equip_atk': [100],
            'atk_buffs': [0.05],
            'before_battle': {
                'enemy': {
                    'def_buffs': [[-0.08, 99, 'crimson pendant']],
                }
            }
        },
        'heavenly ring': {
            'equip_atk': [100],
            'equip_mag': [100],
            'crit_rate_buffs': [0.1],
            'crit_dmg_buffs': [0.1],
        },
        'leaf of the sarced tree': {
            'equip_mag': [86],
            'equip_res': [56],
            'mag_buffs': [0.08],
        },
        'mystic barrette': {
            'equip_atk': [100],
            'atk_buffs': [[0.12, 99, 'mystic barrette', 'no ally within 1 sq']],
            'dmg_dealt_buffs': [[0.12, 99, 'mystic barrette', 'no ally within 1 sq']],
        },
        'nadia amulet': {
            'equip_atk': [100],
            'equip_mag': [100],
            'atk_buffs': [0.08],
            'mag_buffs': [0.08],
            'def_buffs': [0.08],
            'res_buffs': [0.08],
            'tec_buffs': [0.08],
            'crit_dmg_buffs': [0.1],
            'mov_buffs': [1],
        },
        'necklace of everlasting darkness': {
            'equip_mag': [86],
            'mag_buffs': [0.05],
            'after_skill': {
                'ally': {
                    'special_effects': [['reduce_cd_all', 'defeat']]
                }
            }
        },
        'orichalcon ring': {
            'equip_mag': [86],
            'equip_res': [56],
            'mag_buffs': [0.05],
            'after_battle': {
                'enemy': {
                    'dmg_res_buffs': [[-0.15, 1, 'orichalcon ring']],
                }
            }
        },
        'origin amulet': {
            'equip_atk': [100],
            'equip_mag': [100],
            'atk_buffs': [0.08],
            'mag_buffs': [0.08],
            'def_buffs': [0.08],
            'res_buffs': [0.08],
            'tec_buffs': [0.08],
            'crit_dmg_buffs': [0.1],
            'mov_buffs': [1],
        },
        "rakshasa's earrings": {
            'equip_atk': [86],
            'equip_def': [57],
            'atk_buffs': [0.08],
        },
        'ring of life': {
            'equip_atk': [100],
            'equip_mag': [100],
            'atk_buffs': [0.08],
            'mag_buffs': [0.08],
            'skill_dmg_dealt_buffs': [0.1],
        },
        "shield of the warrior princess": {
            'equip_atk': [86],
            'equip_def': [57],
            'atk_buffs': [0.08],
        },
        'ultimate ring': {
            'equip_atk': [86],
            'atk_buffs': [0.05],
            'mag_buffs': [0.05],
            'def_buffs': [0.05],
            'res_buffs': [0.05],
            'tec_buffs': [0.05],
        },
        'zenith amulet': {
            'equip_atk': [100],
            'equip_mag': [100],
            'atk_buffs': [0.08],
            'mag_buffs': [0.08],
            'def_buffs': [0.08],
            'res_buffs': [0.08],
            'tec_buffs': [0.08],
            'crit_dmg_buffs': [0.1],
            'mov_buffs': [1],
        },
    }
}

def load_equipments(equipment_list, status):
    if status is None:
        status = {}
    new_status = copy.deepcopy(status)
    for equip_name in equipment_list:
        equip_found = False
        for equip_type in equipments:
            if equip_name in equipments[equip_type]:
                new_status = deep_merge(new_status, equipments[equip_type][equip_name])
                equip_found = True
                break
        if not equip_found:
            raise Exception('Equipment %s not found' % equip_name)
    return new_status
    