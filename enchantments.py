import copy
from utils import deep_merge

enchantments = {
    'buster': {
        2: {
            'enchant_atk_percent_n_2set': [0.05],
            'enchant_mag_percent_n_2set': [0.05],
        },
        4: {
            'atk_buffs': [0.15],
            'dmg_res_buffs': [0.15],
        }
    },
    'break': {
        2: {
            'crit_rate_buffs': [0.07],
        },
        4: {
            'dmg_dealt_buffs': [0.2],
        }
    },
    'charge': {
        2: {
            'enchant_atk_percent_n_2set': [0.05],
            'enchant_mag_percent_n_2set': [0.05],
        },
        4: {
            'atk_buffs': [0.1],
            'mag_buffs': [0.1],
            'def_buffs': [0.1],
            'res_buffs': [0.1],
        }
    },
    'feather': {
        2: {
            'enchant_atk_percent_n_2set': [0.05],
            'enchant_mag_percent_n_2set': [0.05],
        },
        4: {
            'dmg_dealt_buffs': [0.1],
            'mov_buffs': [1],
        }
    },
    'nova': {
        2: {
            'enchant_atk_percent_n_2set': [0.05],
            'enchant_mag_percent_n_2set': [0.05],
        },
        4: {
            'skill_dmg_dealt_buffs': [0.1],
            'aoe_skill_dmg_dealt_buffs': [0.1],
        }
    },
    'quick': {
        2: {
            'enchant_atk_percent_n_2set': [0.05],
            'enchant_mag_percent_n_2set': [0.05],
        },
        4: {
            'cd_reduction_rate': [0.5],
        }
    },
    'strike': {
        2: {
            'crit_rate_buffs': [0.07],
        },
        4: {
            'crit_dmg_buffs': [0.3],
        }
    },
}

enchanment_random_stats = {
    'max_atk_percent': {
        'enchant_atk_percent_n_2set': [0.15, 0.05, 0.05, 0.1],
    },
    'max_mag_percent': {
        'enchant_mag_percent_n_2set': [0.15, 0.05, 0.05, 0.1],
    },
    'max_flat_atk': {
        'enchant_flat_atk': [31, 11, 11, 21],
    },
    'max_flat_mag': {
        'enchant_flat_mag': [31, 11, 11, 21],
    },
    'max_crit': {
        'crit_rate_buffs': [0.15],
    },
    'avg': {
        'enchant_atk_percent_n_2set': [0.17],
        'enchant_mag_percent_n_2set': [0.17],
        'enchant_flat_atk': [37],
        'enchant_flat_mag': [37],
        'crit_rate_buffs': [0.07],
    }
}

def load_enchantments(enchanment_list, status):
    if status is None:
        status = {}
    new_status = copy.deepcopy(status)
    if len(enchanment_list) <= 2:
        for enchant in enchanment_list:
            new_status = deep_merge(new_status, enchantments[enchant][2])
    else:
        raise Exception('More than 2 enchanment types found')
    if len(enchanment_list) <= 1:
        for enchant in enchanment_list:
            new_status = deep_merge(new_status, enchantments[enchant][4])
    return new_status
    
def load_enchantment_random_stats(settings, status):
    if status is None:
        status = {}
    new_status = copy.deepcopy(status)
    if settings in enchanment_random_stats:
        l = [settings]
    elif settings == 'max_atk':
        l = ['max_atk_percent', 'max_flat_atk']
    elif settings == 'max_mag':
        l = ['max_mag_percent', 'max_flat_mag']
    elif settings == 'max_atk_percent_and_crit':
        l = ['max_atk_percent', 'max_crit']
    elif settings == 'max_mag_percent_and_crit':
        l = ['max_mag_percent', 'max_crit']
    elif settings == 'max_atk_and_crit':
        l = ['max_atk_percent', 'max_flat_atk', 'max_crit']
    elif settings == 'max_mag_and_crit':
        l = ['max_mag_percent', 'max_flat_mag', 'max_crit']
    else:
        raise Exception('Settings %s is not supported' % settings)
    for s in l:
        new_status = deep_merge(new_status, enchanment_random_stats[s])
    return new_status