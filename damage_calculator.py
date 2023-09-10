import copy
import json
from equipments import load_equipments
from enchantments import *
from supports import link_support
from simulate_battle import activate_master_class_effect, add_teamwise_buffs

ally_base_status = {
    'class': None,
    'master_class_lv': 0,
    'double_normal_atk_rate': 0,
    'atk': None,
    'mag': None,
    'def': 0,
    'res': 0,
    'tec': 0,
    'enchant_atk_percent_n_2set': [],
    'enchant_mag_percent_n_2set': [],
    'enchant_flat_atk': [],
    'enchant_flat_mag': [],
    'equip_atk': [],
    'equip_mag': [],
    'equip_def': [],
    'equip_res': [],
    'equip_tec': [],
    'atk_buffs': [],
    'mag_buffs': [],
    'def_buffs': [],
    'res_buffs': [],
    'tec_buffs': [],
    'crit_rate_buffs': [],
    'crit_dmg_buffs': [],
    'battle_atk_buffs': [],
    'battle_mag_buffs': [],
    'battle_crit_rate_buffs': [],
    'dmg_dealt_buffs': [],
    'atk_dmg_dealt_buffs': [],
    'mag_dmg_dealt_buffs': [],
    'skill_dmg_dealt_buffs': [],
    'st_skill_dmg_dealt_buffs': [],
    'aoe_skill_dmg_dealt_buffs': [],
    'battle_dmg_dealt_buffs': [],
    'dmg_res_buffs': [],
    'atk_dmg_res_buffs': [],
    'mag_dmg_res_buffs': [],
    'battle_dmg_res_buffs': [],
    'mov_buffs': [],
    'fixed_dmg_skill': [],
    'fixed_dmg_atk': [],
    'fixed_dmg_res': [],
    'fixed_dmg_battle_res': [],
}

enemy_base_status = {
    'def': 300,
    'res': 300,
    'def_buffs': [],
    'res_buffs': [],
    'crit_rate_res_buffs': [],
    'dmg_res_buffs': [],
    'atk_dmg_res_buffs': [],
    'mag_dmg_res_buffs': [],
    'skill_dmg_res_buffs': [],
    'st_skill_dmg_res_buffs': [],
    'aoe_skill_dmg_res_buffs': [],
    'battle_dmg_res_buffs': [],
}

def get_full_buff(buff): # [buff value, duration, frame, condition, buff turn]
    if not isinstance(buff, list):
        buff = [buff]
    else:
        buff = copy.deepcopy(buff)
    if len(buff) < 2:
        buff.append(99)
    if len(buff) < 3:
        buff.append(None)
    if len(buff) < 4:
        buff.append(None)
    if len(buff) < 5:
        buff.append(0)
    return buff

def sum_buffs(status, buff_type):
    if buff_type not in status:
        return 0
    s = 0
    buff_by_frame = {}
    for b in status[buff_type]:
        buff = get_full_buff(b)
        if buff[1] != 0: # buffs that are still in effect
            if buff[2] is None: # no frame
                s += buff[0]
            else:
                if buff[2] not in buff_by_frame:
                    buff_by_frame[buff[2]] = buff # only one buff per frame
                elif buff[1] > 20 and buff_by_frame[buff[2]][1] > 20: # buffs that never expire but vary
                    buff_by_frame[buff[2]] = buff
                else:
                    if abs(buff[0]) > abs(buff_by_frame[buff[2]][0]): # higher effect value
                        buff_by_frame[buff[2]] = buff
                    elif buff[0] == buff_by_frame[buff[2]][0]:
                        if abs(buff[1]) > abs(buff_by_frame[buff[2]][1]): # longer duration
                            buff_by_frame[buff[2]] = buff
    for frame in buff_by_frame:
        s += buff_by_frame[frame][0]
    return s
    
def remove_one_time_buffs(status):
    new_status = {}
    for key in status:
        if key.endswith('buffs'):
            new_status[key] = []
            for buff in status[key]:
                if (not isinstance(buff, list)) or len(buff) < 2:
                    new_status[key].append(buff)
                else:
                    if buff[1] > 0:
                        new_status[key].append(copy.deepcopy(buff))
        else:
            new_status[key] = status[key]
    
    return new_status
    
def get_base_stat(raw_status_gacha, stat_type):
    base_stat = raw_status_gacha[stat_type] if stat_type in raw_status_gacha else 0
    if stat_type in {'atk', 'mag'}:
        base_stat = base_stat / (1 + 0.3) * (1 + 0.3 + 0.3 + 0.2 + 0.2)
        if stat_type == 'atk':
            base_stat *= (1 + sum_buffs(raw_status_gacha, 'enchant_atk_percent_n_2set'))
            base_stat += sum_buffs(raw_status_gacha, 'enchant_flat_atk')
            base_stat += sum_buffs(raw_status_gacha, 'equip_atk')
        else:
            base_stat *= (1 + sum_buffs(raw_status_gacha, 'enchant_mag_percent_n_2set'))
            base_stat += sum_buffs(raw_status_gacha, 'enchant_flat_mag')
            base_stat += sum_buffs(raw_status_gacha, 'equip_mag')
    elif stat_type in {'def', 'res'}:
        base_stat = base_stat / (1 + 0.3) * (1 + 0.3 + 0.2 + 0.2 + 0.2)
        if stat_type == 'def':
            base_stat *= (1 + sum_buffs(raw_status_gacha, 'enchant_def_percent_n_2set'))
            base_stat += sum_buffs(raw_status_gacha, 'enchant_flat_def')
            base_stat += sum_buffs(raw_status_gacha, 'equip_def')
        else:
            base_stat *= (1 + sum_buffs(raw_status_gacha, 'enchant_res_percent_n_2set'))
            base_stat += sum_buffs(raw_status_gacha, 'enchant_flat_res')
            base_stat += sum_buffs(raw_status_gacha, 'equip_res')
    elif stat_type == 'tec':
        base_stat += sum_buffs(raw_status_gacha, 'equip_tec')
    else:
        return None
    return base_stat
    
def get_crit_rate(attacker_status, defender_status, skill_detail=None, use_base_stat=False):
    if not use_base_stat:
        tec = get_base_stat(attacker_status, 'tec')
    else:
        tec = attacker_status['tec']
    tec *= (1 + sum_buffs(attacker_status, 'tec_buffs'))
    cr = tec / 1000.0 + sum_buffs(attacker_status, 'crit_rate_buffs')
    if skill_detail is None or 'area' not in skill_detail or skill_detail['area'] == 'st':
        cr += sum_buffs(attacker_status, 'battle_crit_rate_buffs')
    cr -= sum_buffs(defender_status, 'crit_rate_res_buffs')
    return max(0, min(cr, 1))
    
def get_stat_dif(attacker_status, defender_status, attack_detail, skill_detail=None):
    if attack_detail['type'] == 'attack':
        atk_multiplier = sum_buffs(attacker_status, 'atk_buffs')
        if skill_detail is None or 'area' not in skill_detail or skill_detail['area'] == 'st':
            atk_multiplier += sum_buffs(attacker_status, 'battle_atk_buffs')
        attacker_atk = attacker_status['atk'] * (1 + max(atk_multiplier, -0.7))
        defender_def = defender_status['def'] * (1 + max(sum_buffs(defender_status, 'def_buffs'), -0.7))
        stat_dif = attacker_atk - defender_def
    elif attack_detail['type'] == 'magic':
        mag_multiplier = sum_buffs(attacker_status, 'mag_buffs')
        if skill_detail is None or 'area' not in skill_detail or skill_detail['area'] == 'st':
            mag_multiplier += sum_buffs(attacker_status, 'battle_mag_buffs')
        attacker_mag = attacker_status['mag'] * (1 + max(mag_multiplier, -0.7))
        defender_res = defender_status['res'] * (1 + max(sum_buffs(defender_status, 'res_buffs'), -0.7))
        stat_dif = attacker_mag - defender_res
    else:
        return None
    return max(stat_dif, 0)
    
def get_dmg_dealt_multiplier(attacker_status, attack_detail, skill_detail=None):
    dmg_dealt_multiplier = sum_buffs(attacker_status, 'dmg_dealt_buffs')
    if attack_detail['type'] == 'attack':
        dmg_dealt_multiplier += sum_buffs(attacker_status, 'atk_dmg_dealt_buffs')
    elif attack_detail['type'] == 'magic':
        dmg_dealt_multiplier += sum_buffs(attacker_status, 'mag_dmg_dealt_buffs')
    if skill_detail != None:
        dmg_dealt_multiplier += sum_buffs(attacker_status, 'skill_dmg_dealt_buffs')
        if 'area' in skill_detail and skill_detail['area'] == 'aoe':
            dmg_dealt_multiplier += sum_buffs(attacker_status, 'aoe_skill_dmg_dealt_buffs')
        else:
            dmg_dealt_multiplier += sum_buffs(attacker_status, 'st_skill_dmg_dealt_buffs')
            dmg_dealt_multiplier += sum_buffs(attacker_status, 'battle_dmg_dealt_buffs')
    else:
        dmg_dealt_multiplier += sum_buffs(attacker_status, 'battle_dmg_dealt_buffs')
    return max(dmg_dealt_multiplier, -0.7)
    
def get_dmg_res_multiplier(defender_status, attack_detail, skill_detail=None):
    dmg_res_multiplier = sum_buffs(defender_status, 'dmg_res_buffs')
    if attack_detail['type'] == 'attack':
        dmg_res_multiplier += sum_buffs(defender_status, 'atk_dmg_res_buffs')
    elif attack_detail['type'] == 'magic':
        dmg_res_multiplier += sum_buffs(defender_status, 'mag_dmg_res_buffs')
    if skill_detail != None:
        dmg_res_multiplier += sum_buffs(defender_status, 'skill_dmg_res_buffs')
        if 'area' in skill_detail and skill_detail['area'] == 'aoe':
            dmg_res_multiplier += sum_buffs(defender_status, 'aoe_skill_dmg_res_buffs')
        else:
            dmg_res_multiplier += sum_buffs(defender_status, 'st_skill_dmg_res_buffs')
            dmg_res_multiplier += sum_buffs(defender_status, 'battle_dmg_res_buffs')
    else:
        dmg_res_multiplier += sum_buffs(defender_status, 'battle_dmg_res_buffs')
    return min(dmg_res_multiplier, 0.7)
    
def get_fixed_dmg(ally_status, skill_detail=None, use_base_stat=False):
    fixed_dmg = 0
    if 'fixed_dmg_atk' in ally_status:
        if not use_base_stat:
            ally_atk = get_base_stat(ally_status, 'atk')
        else:
            ally_atk = ally_status['atk']
        ally_atk *= (1 + max(sum_buffs(ally_status, 'atk_buffs'), -0.7))
        fixed_dmg += ally_atk * sum_buffs(ally_status, 'fixed_dmg_atk')
    if 'fixed_dmg_res' in ally_status or 'fixed_dmg_battle_res' in ally_status:
        if not use_base_stat:
            ally_res = get_base_stat(ally_status, 'res')
        else:
            ally_res = ally_status['res']
        ally_res *= (1 + max(sum_buffs(ally_status, 'res_buffs'), -0.7))
        fixed_dmg += ally_res * sum_buffs(ally_status, 'fixed_dmg_res')
        if skill_detail is None or 'area' not in skill_detail or skill_detail['area'] == 'st':
            fixed_dmg += ally_res * sum_buffs(ally_status, 'fixed_dmg_battle_res')
    return fixed_dmg
        
def calc_damage(ally_status, enemy_status, attack_detail, skill_detail=None, use_base_stat=False, dmg_penalty=False, include_fixed_dmg=True, on_enemy_turn=False):
    if not on_enemy_turn:
        ally_status = copy.deepcopy(ally_status)
    else:
        ally_status = remove_one_time_buffs(ally_status)
    if not use_base_stat:
        if attack_detail['type'] == 'attack':
            ally_status['atk'] = get_base_stat(ally_status, 'atk')
        elif attack_detail['type'] == 'magic':
            ally_status['mag'] = get_base_stat(ally_status, 'mag')
            
    dmg = 1.0
    dmg *= get_stat_dif(ally_status, enemy_status, attack_detail, skill_detail)
    
    hit_cnt = attack_detail['num_of_hits'] if 'num_of_hits' in attack_detail else 10
    if skill_detail is None:
        hit_cnt = round(hit_cnt * (1 + sum_buffs(ally_status, 'double_normal_atk_rate')))
    dmg *= hit_cnt
    
    dmg *= (1 + get_dmg_dealt_multiplier(ally_status, attack_detail, skill_detail))
    dmg *= (1 - get_dmg_res_multiplier(enemy_status, attack_detail, skill_detail))
    
    if skill_detail != None:
        if 'dmg_modifier' not in skill_detail:
            return None
        dmg *= skill_detail['dmg_modifier']
        
    if dmg_penalty:
        dmg *= 0.6
    
    if skill_detail != None:
        dmg *= (1 + sum_buffs(ally_status, 'fixed_dmg_skill'))
    
    crit_rate = get_crit_rate(ally_status, enemy_status, skill_detail, use_base_stat)
    crit_dmg_modifier = 1.3 + sum_buffs(ally_status, 'crit_dmg_buffs')
    crit_dmg = dmg * crit_dmg_modifier
    ev_dmg = dmg * (1 - crit_rate) + crit_dmg * crit_rate
    
    dmg_dealt = [dmg, crit_dmg, ev_dmg]
    if crit_rate <= 0:
        dmg_dealt[1] = dmg_dealt[0]
    if crit_rate >= 1:
        dmg_dealt[0] = dmg_dealt[1]
    if include_fixed_dmg:
        dmg_dealt = [d + get_fixed_dmg(ally_status, skill_detail, use_base_stat) for d in dmg_dealt]
    return dmg_dealt
    
# attacker_stats = {
                    # 'class': 'archer',
                    # 'master_class_lv': 3,
                    # 'atk': 490,
                    # 'tec': 321,
                    # 'atk_buffs': [[0.2, 99, 'Beet/Talent']],
                    # 'dmg_dealt_buffs': [[0.1, 1, 'Main/A'], [0.2, 1, 'tracking headband']], # Accel step
                    # 'crit_rate_buffs': [[0.5, -1, 'Main/A']], # Obliviator
                    # 'skill_dmg_dealt_buffs': [[0.2, 2, 'sunshine blessing']], # sol
                # }
# attacker_status = load_equipments(['double longshot',
                                   # "assassin's vest",
                                   # "tracking headband",
                                   # "nadia amulet"],
                                   # attacker_stats)
# attacker_status = load_enchantments(['strike'], attacker_status)
# attacker_status = load_enchantment_random_stats('max_atk_percent', attacker_status)
# attacker_status = link_support('sol', attacker_status)
# defender_status = {
                    # 'def': 441,
                    # 'aoe_skill_dmg_res_buffs': [0.5],
                # }
# if attacker_status['class'] == attacker_status['support_class']:
    # activate_master_class_effect(attacker_status, defender_status, [])
# attacker_status = add_teamwise_buffs(['symbol skill', 'cleared quest effect'], attacker_status)
# #print(json.dumps(attacker_status, indent=2))
# print(calc_damage(
                    # attacker_status,
                    # defender_status,
                    # {'type': 'attack'},
                    # {'dmg_modifier': 0.5, 'area': 'aoe'},
                    # use_base_stat=False,
                    # include_fixed_dmg=False)[:3])