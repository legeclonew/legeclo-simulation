import copy
from utils import deep_merge

teamwise_buffs = {
    'azur sword': {
        'delayed_buffs_turn': {
            (1, 2, 3, 4, 5): {
                'crit_rate_buffs': [[0.1, 2, 'azur sword']],
                'crit_dmg_buffs': [[0.1, 2, 'azur sword']],
            },
        }
    },
    'azur sword after': {
        'delayed_buffs_turn': {
            (2, 3, 4, 5): {
                'crit_rate_buffs': [[0.1, 2, 'azur sword']],
                'crit_dmg_buffs': [[0.1, 2, 'azur sword']],
            },
        }
    },
    'cleared quest effect': {
        'atk_buffs': [0.3],
        'mag_buffs': [0.3],
        'tec_buffs': [0.3],
        'def_buffs': [0.3],
        'res_buffs': [0.3],
    },
    'symbol skill': {
        'delayed_buffs_turn': {
            (1, 3): {
                'atk_buffs': [[0.2, 4, 'Main/A']],
                'mag_buffs': [[0.2, 4, 'Main/A']],
                'def_buffs': [[0.2, 4, 'Main/A']],
                'res_buffs': [[0.3, 4, 'Main/A']],
                'dmg_dealt_buffs': [[0.12, 4, 'Guild']],
            },
        }
    },
    'mc ex symbol': {
        'atk_buffs': [[0.1, 99, 'attack blessing']],
        'mag_buffs': [[0.1, 99, 'attack blessing']],
        'delayed_buffs_turn': {
            (1, 3): {
                'battle_dmg_dealt_buffs': [[0.15, 4, 'blessing of nadia']],
            },
        }
    },
    'mc': ['symbol skill', 'mc ex symbol'],
    'xanastasia ex symbol': {
        'atk_buffs': [[0.15, 99, 'cheer dance']],
        'mag_buffs': [[0.15, 99, 'cheer dance']],
        'delayed_buffs_turn': {
            (1, 3): {
                'battle_crit_rate_buffs': [[0.1, 4, 'blessing of origin']],
                'crit_dmg_buffs': [[0.15, 4, 'blessing of origin']],
            },
        }
    },
    'xanastasia': ['symbol skill', 'xanastasia ex symbol'],
    'canastasia': ['xanastasia'],
    'xarthur ex symbol': {
        'delayed_buffs_turn': {
            (1, 3): {
                'battle_dmg_dealt_buffs': [[0.15, 4, 'blessing of origin']],
                'battle_dmg_res_buffs': [[0.1, 4, 'blessing of origin']],
            },
        }
    },
    'xarthur': ['symbol skill', 'xarthur ex symbol'],
    'carthur': ['xarthur'],
}

def add_teamwise_buffs(buff_names, status):
    if status is None:
        status = {}
    new_status = copy.deepcopy(status)
    for buff_name in buff_names:
        if buff_name in teamwise_buffs:
            if isinstance(teamwise_buffs[buff_name], dict):
                new_status = deep_merge(new_status, teamwise_buffs[buff_name])
            else:
                new_status = add_teamwise_buffs(teamwise_buffs[buff_name], new_status)
        else:
            raise Exception('Buff name %s not found' % buff_name)
    return new_status