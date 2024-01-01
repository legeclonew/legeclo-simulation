import itertools
import copy
from utils import deep_merge
import math
from teamwise_buffs import add_teamwise_buffs

ally_base_status = {
    'atk': 877,
    'mag': 818,
    'atk_buffs': [0.1, 0.08, 0.2],
    'mag_buffs': [],
    'dmg_dealt_buffs': [0.1, 0.11],
    'crit_dmg_buffs': [0.1],
}

enemy_base_status = {
    'def': 100,
    'res': 100,
    'def_buffs': [],
    'res_buffs': [],
    'dmg_res_buffs': [],
}

skill_detail = {
    'dmg_modifier': 0.45
}

def get_all_skill_sets(skill_list, must_include_skill_ids=[]):
    skill_dict = {}
    for skill in skill_list:
        if 'id' in skill:
            skill_dict[skill['id']] = skill
    skill_pool = []
    must_include_skills = []
    for skill_id in must_include_skill_ids:
        must_include_skills.append(skill_dict[skill_id])
    for skill in skill_list:
        if not('id' in skill and skill['id'] in must_include_skill_ids):
            skill_pool.append(skill)
    skill_sets = []
    for ss in itertools.combinations(skill_pool, 3 - len(must_include_skills)):
        skill_sets.append(must_include_skills + list(ss))
    return skill_sets

def put_skill_on_cooldown(skill_list, skill_id):
    for skill in skill_list:
        if skill['id'] == skill_id:
            if skill['type'] == 'active':
                skill['cd'] = skill['ct'] + 1
            else:
                skill['cd'] = skill['ct']
            break
            
def reduce_skill_cooldown(skill_list, skill_id, amount=1):
    for skill in skill_list:
        if skill['id'] == skill_id:
            if skill['type'] == 'active':
                skill['cd'] = max(skill['cd'] - amount, 0)
            break

def reduce_cooldown(skill_list, sub_turn, inplace=False):
    if not inplace:
        skill_list = copy.deepcopy(skill_list)
    for skill in skill_list:
        if 'ct' in skill and 'cd' not in skill:
            skill['cd'] = 0
        if skill['type'] == 'active':
            skill['cd'] = max(skill['cd'] - 1, 0)
        else:
            if 'cd' in skill and sub_turn == 0:
                skill['cd'] = max(skill['cd'] - 1, 0)
    return skill_list
    
def is_skill_ready(skill_list, skill_id):
    for skill in skill_list:
        if 'id' in skill and skill['id'] == skill_id:
            return skill['cd'] == 0
    return False
    
def find_avail_skills(skill_list):
    avail_skills = [None] # Normal attack
    for skill in skill_list:
        if skill['type'] == 'active' and skill['cd'] == 0:
            avail_skills.append(skill)
    return avail_skills
    
def find_avail_skills_and_use(skill_list):
    avail_skills = []
    for skill in skill_list:
        if skill['type'] == 'active' and skill['cd'] == 0:
            avail_skills.append(skill)
    if len(avail_skills) == 0:
        avail_skills.append(None)
    return avail_skills
    
def summon(summoner_status, minion_status):
    if "minions" not in summoner_status:
        summoner_status["minions"] = []
    summoner_status["minions"].append(minion_status)
    
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
    
def update_start_of_turn(status, turn_num):
    if 'delayed_buffs_turn' not in status:
        return
    for trigger_turns in status['delayed_buffs_turn']:
        for trigger_turn in trigger_turns:
            if turn_num == trigger_turn:
                status = deep_merge(status, status['delayed_buffs_turn'][trigger_turns])
    
def update_duration(status, turn_num):
    new_status = {}
    for key in status:
        if key.endswith('buffs'):
            new_status[key] = []
            for buff in status[key]:
                if (not isinstance(buff, list)) or len(buff) < 2:
                    new_status[key].append(buff)
                else:
                    if buff[1] >= 1:
                        if len(buff) > 4 and buff[4] == turn_num:
                            new_status[key].append(copy.deepcopy(buff))
                            continue
                        if buff[1] > 1:
                            new_status[key].append(copy.deepcopy(buff))
                            new_status[key][-1][1] -= 1
                    elif buff[1] < -1: # consumed by action
                        new_status[key].append(copy.deepcopy(buff))
                        new_status[key][-1][1] += 1
        else:
            new_status[key] = status[key]
    
    return new_status
    
def update_duration_enemy(status, sub_turn):
    new_status = {}
    for key in status:
        if key.endswith('buffs'):
            new_status[key] = []
            for buff in status[key]:
                if (not isinstance(buff, list)) or len(buff) < 2:
                    new_status[key].append(buff)
                else:
                    if buff[1] >= 1:
                        if sub_turn > 0:
                            new_status[key].append(copy.deepcopy(buff))
                            continue
                        if buff[1] > 1:
                            new_status[key].append(copy.deepcopy(buff))
                            new_status[key][-1][1] -= 1
                    elif buff[1] < -1: # consumed by action
                        new_status[key].append(copy.deepcopy(buff))
                        new_status[key][-1][1] += 1
        else:
            new_status[key] = status[key]
    
    return new_status
                    
def add_buff(status, buff_type, new_buff, turn_num=None):
    if buff_type not in status:
        status[buff_type] = []
    if isinstance(new_buff, list) and len(new_buff) > 1 and 0 < new_buff[1] <= 20:
        new_buff = get_full_buff(new_buff)
        if turn_num is None:
            raise Exception('turn_num must not be None')
        new_buff[4] = turn_num
    status[buff_type].append(new_buff)
    
def add_buff_including_minions(status, buff_type, new_buff, turn_num=None):
    add_buff(status, buff_type, new_buff, turn_num)
    if "minions" in status:
        for minion in status["minions"]:
            add_buff(minion, buff_type, new_buff, turn_num)
    
def remove_buff(status):
    for key in status:
        if key.endswith('dmg_res_buffs'):
            for buff in status[key]:
                if isinstance(buff, list) and len(buff) > 2 and buff[2] == 'Main/A' and buff[0] > 0 and buff[1] != 0:
                    buff[0] = 0
                    return
    for key in status:
        if key in ['def_buffs', 'res_buffs']:
            for buff in status[key]:
                if isinstance(buff, list) and len(buff) > 2 and buff[2] == 'Main/A' and buff[0] > 0 and buff[1] != 0:
                    buff[0] = 0
                    return
    
def use_support_skill(ally_status, enemy_status, turn_num):
    if 'support_active' not in ally_status:
        return
        
    if 'ally' in ally_status['support_active']:
        for key in ally_status['support_active']['ally']:
            buff_list = ally_status['support_active']['ally'][key]
            for i in range(len(buff_list)):
                buff_list[i] = get_full_buff(buff_list[i])
                buff_list[i][4] = turn_num
        deep_merge(ally_status, ally_status['support_active']['ally'])
    if 'enemy' in ally_status['support_active']:
        deep_merge(enemy_status, ally_status['support_active']['enemy'])
    ally_status.pop('support_active')
    
def match_support_class(ally_status):
    if 'class' not in ally_status:
        return None
    if 'support_class' not in ally_status:
        return False
    return ally_status['class'] == ally_status['support_class']
    
def activate_master_class_effect(ally_status, enemy_status, skill_list):
    if 'master_class_lv' not in ally_status or ally_status['master_class_lv'] == 0:
        return
    mc_lv = ally_status['master_class_lv']
    if ally_status['class'] == 'soldier':
        if len(skill_list) == 0 or 'id' in skill_list[-1]:
            skill_list.append({'type': 'passive', 'ct': 5 - mc_lv, 'effect': 'act again'})
    elif ally_status['class'] == 'lancer':
        pass
    elif ally_status['class'] == 'rider':
        pass
    elif ally_status['class'] == 'aerial':
        add_buff(ally_status, 'atk_buffs', [0.05 + 0.05 * mc_lv, 99, 'mc'])
        add_buff(ally_status, 'mag_buffs', [0.05 + 0.05 * mc_lv, 99, 'mc'])
        add_buff(ally_status, 'tec_buffs', [0.05 + 0.05 * mc_lv, 99, 'mc'])
        add_buff(ally_status, 'def_buffs', [0.05 + 0.05 * mc_lv, 99, 'mc'])
        add_buff(ally_status, 'res_buffs', [0.05 + 0.05 * mc_lv, 99, 'mc'])
    elif ally_status['class'] == 'sorcerer':
        add_buff(enemy_status, 'res_buffs', [-0.05 * mc_lv, 99, 'mc'])
    elif ally_status['class'] == 'saint':
        pass
    elif ally_status['class'] == 'shooter':
        add_buff(enemy_status, 'def_buffs', [-0.05 * mc_lv, 99, 'mc'])
    elif ally_status['class'] == 'assassin':
        add_buff(ally_status, 'double_normal_atk_rate', [0.1 + 0.3 * mc_lv, 99, 'mc'])
    else:
        raise Exception('Class %s not supported')
    
def apply_random_buff(ally_status, turn_num):
    if 'weak_buff_success_rate' in ally_status:
        for attempt in ally_status['weak_buff_success_rate']:
            if turn_num > math.ceil(attempt[0] * 3 / 7.0 * 8):
                continue
            if turn_num == 1:
                add_buff(ally_status, 'dmg_dealt_buffs', [0.1, attempt[1], attempt[2]], turn_num)
            elif turn_num == 2:
                add_buff(ally_status, 'atk_buffs', [0.1, attempt[1], attempt[2]], turn_num)
                add_buff(ally_status, 'mag_buffs', [0.1, attempt[1], attempt[2]], turn_num)
            elif turn_num == 3:
                add_buff(ally_status, 'dmg_dealt_buffs', [0.1, attempt[1], attempt[2]], turn_num)
            elif turn_num == 4:
                add_buff(ally_status, 'atk_buffs', [0.1, attempt[1], attempt[2]], turn_num)
                add_buff(ally_status, 'mag_buffs', [0.1, attempt[1], attempt[2]], turn_num)
        ally_status.pop('weak_buff_success_rate')

    if 'mid_buff_success_rate' in ally_status:
        for attempt in ally_status['mid_buff_success_rate']:
            if turn_num > math.ceil(attempt[0] * 3 / 7.0 * 8):
                continue
            if turn_num == 1:
                add_buff(ally_status, 'dmg_dealt_buffs', [0.15, attempt[1], attempt[2]], turn_num)
            elif turn_num == 2:
                add_buff(ally_status, 'atk_buffs', [0.15, attempt[1], attempt[2]], turn_num)
                add_buff(ally_status, 'mag_buffs', [0.15, attempt[1], attempt[2]], turn_num)
            elif turn_num == 3:
                add_buff(ally_status, 'dmg_dealt_buffs', [0.15, attempt[1], attempt[2]], turn_num)
            elif turn_num == 4:
                add_buff(ally_status, 'atk_buffs', [0.15, attempt[1], attempt[2]], turn_num)
                add_buff(ally_status, 'mag_buffs', [0.15, attempt[1], attempt[2]], turn_num)
        ally_status.pop('mid_buff_success_rate')
    
def apply_random_debuff(ally_status, enemy_status, turn_num):
    if 'weak_debuff_success_rate' not in ally_status:
        return
        
    for attempt in ally_status['weak_debuff_success_rate']:
        if turn_num > math.ceil(attempt[0] * 3 / 6.0 * 5):
            continue
        if turn_num == 1:
            add_buff(enemy_status, 'dmg_res_buffs', [-0.1, attempt[1], attempt[2]], turn_num)
        elif turn_num == 2:
            add_buff(enemy_status, 'def_buffs', [-0.1, attempt[1], attempt[2]], turn_num)
            add_buff(enemy_status, 'res_buffs', [-0.2, attempt[1], attempt[2]], turn_num)
    ally_status.pop('weak_debuff_success_rate')
    
def activate_before_attack_effects(ally_status, enemy_status, skill_detail, turn_num):
    if skill_detail != None and 'dmg_modifier' not in skill_detail:
        return
    if skill_detail is None or 'area' not in skill_detail or skill_detail['area'] == 'st':
        if 'before_battle' in ally_status:
            if 'ally' in ally_status['before_battle']:
                deep_merge(ally_status, ally_status['before_battle']['ally'])
            if 'enemy' in ally_status['before_battle']:
                deep_merge(enemy_status, ally_status['before_battle']['enemy'])
                
    apply_random_debuff(ally_status, enemy_status, turn_num)
                
def activate_after_attack_effects(ally_status, enemy_status, skill_list, skill_detail, turn_num, kill_enemy=False):
    if skill_detail != None and 'dmg_modifier' not in skill_detail:
        return
    if 'after_dmg' in ally_status:
        if 'ally' in ally_status['after_dmg']:
            deep_merge(ally_status, ally_status['after_dmg']['ally'])
        if 'enemy' in ally_status['after_dmg']:
            deep_merge(enemy_status, ally_status['after_dmg']['enemy'])
    if 'after_crit' in ally_status:
        if 'ally' in ally_status['after_crit']:
            deep_merge(ally_status, ally_status['after_crit']['ally'])
        if 'enemy' in ally_status['after_crit']:
            deep_merge(enemy_status, ally_status['after_crit']['enemy'])
    if skill_detail != None:
        if 'after_skill' in ally_status:
            if 'ally' in ally_status['after_skill']:
                deep_merge(ally_status, ally_status['after_skill']['ally'])
            if 'enemy' in ally_status['after_skill']:
                deep_merge(enemy_status, ally_status['after_skill']['enemy'])
    if skill_detail is None or 'area' not in skill_detail or skill_detail['area'] == 'st':
        if 'after_battle' in ally_status:
            if 'ally' in ally_status['after_battle']:
                deep_merge(ally_status, ally_status['after_battle']['ally'])
            if 'enemy' in ally_status['after_battle']:
                deep_merge(enemy_status, ally_status['after_battle']['enemy'])
    if kill_enemy:
        if 'after_defeat' in ally_status:
            if 'ally' in ally_status['after_defeat']:
                deep_merge(ally_status, ally_status['after_defeat']['ally'])
            if 'enemy' in ally_status['after_defeat']:
                deep_merge(enemy_status, ally_status['after_defeat']['enemy'])
                
    apply_random_buff(ally_status, turn_num)
    apply_random_debuff(ally_status, enemy_status, turn_num)
    if 'cd_reduction_rate' in ally_status:
        if skill_detail != None:
            reduce_skill_cooldown(skill_list, skill_detail['id'])
    if 'special_effects' in ally_status:
        for effect in ally_status['special_effects']:
            if effect[0] == 'reduce_cd_all':
                #if turn_num >= 2:
                if True:
                    if kill_enemy:
                        reduce_cooldown(skill_list, True, inplace=True)
            elif effect[0] == 'reduce_cd':
                if skill_detail != None:
                    reduce_skill_cooldown(skill_list, skill_detail['id'])
        ally_status.pop('special_effects')
        
def activate_after_action_effects(ally_status, enemy_status, skill_list, skill_detail, turn_num, kill_enemy=False):
    activate_after_attack_effects(ally_status, enemy_status, skill_list, skill_detail, turn_num, kill_enemy)
    if 'after_action' in ally_status:
        if 'ally' in ally_status['after_action']:
            deep_merge(ally_status, ally_status['after_action']['ally'])
        if 'enemy' in ally_status['after_action']:
            deep_merge(enemy_status, ally_status['after_action']['enemy'])

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
    
def debug_buffs(status):
    new_status = {}
    for key in status:
        if isinstance(status[key], list):
            buffs = []
            buff_by_frame = {}
            for buff in status[key]:
                if isinstance(buff, list):
                    if len(buff) > 2 and buff[2] != None:
                        if buff[1] != 0:
                            if buff[2] not in buff_by_frame:
                                buff_by_frame[buff[2]] = buff
                            else:
                                if buff[0] > buff_by_frame[buff[2]][0]:
                                    buff_by_frame[buff[2]] = buff
                                elif buff[0] == buff_by_frame[buff[2]][0]:
                                    if abs(buff[1]) > abs(buff_by_frame[buff[2]][1]):
                                        buff_by_frame[buff[2]] = buff
                    elif len(buff) < 2 or buff[1] != 0:
                        buffs.append(buff)
            for frame in buff_by_frame:
                buffs.append(buff_by_frame[frame])
            if len(buffs) > 0:
                new_status[key] = str(buffs)
    return new_status
    
def sum_dmg(action_list):
    s = 0
    for action in action_list:
        s += action[2]
    return s
    
def log_skill_set(skill_set):
    print "Skill set: ",
    print [skill['id'] for skill in skill_set if 'id' in skill]

def log_action_list(action_list, player_turn_only=True):
    print "Actions:"
    i = 0
    while i < len(action_list):
        j = i
        print "  Turn %d:" % action_list[i][0]
        while j < len(action_list) and action_list[j][0] == action_list[i][0]:
            print "    Action: %s" % (("skill id %d" % action_list[j][1]) if action_list[j][1] != None else "normal attack")
            if len(action_list[j]) > 4 and action_list[j][4] > 0:
                if (action_list[j][2] - action_list[j][4]) > 0:
                    print "    Damage: %f" % (action_list[j][2] - action_list[j][4])
                print "    Minions' damage: %f" % action_list[j][4]
            else:
                if action_list[j][2] > 0:
                    print "    Damage: %f" % action_list[j][2]
            if not player_turn_only:
                if len(action_list[j]) > 3 and action_list[j][3] > 0:
                    print "    Damage on enemy turn: %f" % action_list[j][3]
            print
            j = j + 1
        i = j
        
        toshizou_dmg_enemy_turn = 0
        
def log_total_dmg_enemy_turn(action_list):
    dmg = 0
    for action in action_list:
        if len(action) > 3:
            dmg += action[3]
    print "Total damage on enemy turns: %f" % dmg