import copy
from utils import deep_merge

supports = {
    'amaterasu_newyear': {
        'class': 'rider',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05, 0.15],
            'battle_atk_buffs': [0.15],
        },
        'active': {
            'ally': {
                'atk_buffs': [[0.25, 2, 'Support/A']],
                'def_buffs': [[0.25, 2, 'Support/A']],
                'mov_buffs': [[1, 2, 'Support/A']],
            }
        }
    },
    'apollo': {
        'class': 'soldier',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05],
            'battle_dmg_dealt_buffs': [0.2],
            'battle_dmg_res_buffs': [0.1],
        },
        'active': {
            'ally': {
                'atk_buffs': [[0.3, 2, 'Support/A']],
            }
        }
    },
    'artemis_half': {
        'class': 'shooter',
        'passive': {
            'skill_dmg_dealt_buffs': [0.35],
        },
    },
    'bacchus': {
        'class': 'assassin',
        'passive': {
            'crit_rate_buffs': [0.05],
            'crit_dmg_buffs': [0.25],
        },
    },
    'byakko': {
        'class': 'assassin',
        'passive': {
            'crit_rate_buffs': [0.05],
            'crit_dmg_buffs': [0.1],
        },
        'active': {
            'ally': {
                'dmg_res_buffs': [[0.3, 2, 'Support/A']],
            }
        }
    },
    'cupid': {
        'class': 'shooter',
        'passive': {
            'crit_rate_buffs': [0.05, 0.1],
        },
        'active': {
            'ally': {
                'atk_buffs': [[0.2, 1, 'Support/A']],
                'crit_rate_buffs': [[0.2, 1, 'Support/A']],
            }
        }
    },
    'hades': {
        'class': 'assassin',
        'passive': {
            'crit_rate_buffs': [0.05],
            'before_battle': {
                'enemy': {
                    'def_buffs': [[-0.1, -1, 'underworld curse']],
                    'atk_dmg_res_buffs': [[-0.1, -1, 'underworld curse']],
                }
            }
        },
        'active': {
            'enemy': {
                'atk_buffs': [[-0.3, 2, 'Support/A']],
                'mag_buffs': [[-0.3, 2, 'Support/A']],
            }
        }
    },
    'isis': {
        'class': 'sorcerer',
        'passive': {
            'mag_buffs': [0.05, [0.2, 99, 'isis', 'hp 100%']],
        },
    },
    'kikimora': {
        'class': 'sorcerer',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05],
            'mag_buffs': [0.1],
        },
        'active': {
            'enemy': {
                'res_buffs': [[-0.25, 2, 'Support/A']]
            }
        }
    },
    'nirai_kanai': {
        'class': 'assassin',
        'passive': {
            'atk_buffs': [0.05],
            'battle_dmg_dealt_buffs': [0.05],
            'battle_crit_rate_buffs': [0.1],
        },
        'active': {
            'enemy': {
                'def_buffs': [[-0.15, 2, 'Support/A']],
                'res_buffs': [[-0.15, 2, 'Support/A']],
            }
        }
    },
    'nuwa_yukata': {
        'class': 'assassin',
        'passive': {
            'atk_buffs': [0.05],
            'battle_dmg_dealt_buffs': [0.2],
        },
        'active': {
            'ally': {
                'atk_buffs': [[0.3, 2, 'Support/A']],
                'crit_rate_buffs': [[0.25, 2, 'Support/A']],
            }
        }
    },
    'nyarlathotep': {
        'class': 'sorcerer',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05, 0.15],
        },
        'active': {
            'ally': {
                'res_buffs': [[0.2, 3, 'Support/A']],
                'def_buffs': [[0.2, 3, 'Support/A']],
            }
        }
    },
    'odin': {
        'class': 'rider',
        'passive': {
            'atk_buffs': [0.05],
            #'battle_def_buffs': [0.1],
            #'battle_res_buffs': [0.1],
        }
    },
    'odin_valentine': {
        'class': 'soldier',
        'passive': {
            'battle_dmg_dealt_buffs': [0.15],
            'battle_dmg_res_buffs': [0.15],
        },
        'active': {
            'ally': {
                'atk_buffs': [[0.3, 2, 'Support/A']],
                'dmg_res_buffs': [[0.3, 2, 'Support/A']],
            }
        }
    },
    'raphael': {
        'class': 'soldier',
        'passive': {
            'battle_dmg_dealt_buffs': [0.25],
        },
        'active': {
            'enemy': {
                'def_buffs': [[-0.3, 2, 'Support/A']],
                'res_buffs': [[-0.3, 2, 'Support/A']],
            }
        }
    },
    'rusalka': {
        'class': 'assassin',
        'passive': {
            'crit_rate_buffs': [0.05, 0.1],
        },
        'active': {
            'ally': {
                'crit_rate_buffs': [[0.25, 2, 'Support/A']],
            }
        }
    },
    'rusalka_christmas': {
        'class': 'rider',
        'passive': {
            'crit_rate_buffs': [0.05],
            'after_action': {
                'ally': {
                    'weak_buff_success_rate': [[1, 2, 'cristmas resolution']],
                }
            }
        },
    },
    'seiryu': {
        'class': 'sorcerer',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05],
            'battle_mag_buffs': [[0.1, 99, 'seiryu', 'long range']],
        },
    },
    'smichael': {
        'class': 'soldier',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05],
            'battle_atk_buffs': [0.15],
            'battle_crit_rate_buffs': [0.15],
        },
        'active': {
            'ally': {
                'atk_dmg_dealt_buffs': [[0.3, 2, 'Support/A']],
                'def_buffs': [[0.3, 2, 'Support/A']],
            }
        }
    },
    'sol': {
        'class': 'shooter',
        'passive': {
            'skill_dmg_dealt_buffs': [0.05],
            'after_action': {
                'ally': {
                    'skill_dmg_dealt_buffs': [[0.2, 2, 'sunshine blessing']],
                }
            }
        },
        'active': {
            'ally': {
                'atk_buffs': [[0.3, 2, 'Support/A']],
                'mag_buffs': [[0.3, 2, 'Support/A']],
            }
        }
    },
    'thor': {
        'class': 'soldier',
        'passive': {
            'atk_buffs': [0.05],
            'battle_atk_buffs': [0.15],
        },
    },
}

def link_support(support, status):
    if status is None:
        status = {}
    new_status = copy.deepcopy(status)
    new_status['support_class'] = supports[support]['class']
    new_status = deep_merge(new_status, supports[support]['passive'])
    if 'active' in supports[support]:
        new_status['support_active'] = supports[support]['active']
    return new_status