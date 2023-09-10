import copy
import json
from damage_calculator import calc_damage, get_crit_rate
from simulate_battle import *
from equipments import load_equipments
from enchantments import *
from supports import link_support
from enemies import get_generator

enemy_generator = get_generator('gex3')
enemy_generator.default_def = 100
enemy_generator.is_silenced = True
enemy_generator.num_new_mobs_per_turn = 2
best_action_list = []
best_skill_set = None

def recur_lia(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
    if match_support_class(ally_status) and turn_num == 1 and sub_turn == 0:
        activate_master_class_effect(ally_status, enemies_status['boss'], skill_list)

    if turn_num > 5:
        global best_action_list
        global best_skill_set
        if sum_dmg(action_list) > sum_dmg(best_action_list):
            best_action_list = copy.deepcopy(action_list)
            best_skill_set = skill_list
            #print get_crit_rate(ally_status, enemies_status['boss'])
        return 0
                
    total_dmg = 0
    
    skill_list = reduce_cooldown(skill_list, sub_turn)
    avail_skills = find_avail_skills(skill_list)
    if (turn_num % 2 == 1) and sub_turn == 0:
        avail_skills = [skill_list[0]]
    # elif (turn_num == 1) and sub_turn == 1:
        # avail_skills = [skill_list[2]]
        
    for skill in avail_skills:
        act_again = False
        new_enemies_status = enemy_generator.update_enemies(enemies_status, turn_num, sub_turn)
        new_ally_status = copy.deepcopy(ally_status)
        target_status = new_enemies_status['boss']
        kill_mob = len(new_enemies_status['mobs']) > 0
        #kill_mob = kill_mob and skill != None and skill['id'] == 5 and turn_num % 2 == 1
        kill_mob = False
        #kill_mob = kill_mob and (skill is None or 'dmg_modifier' in skill)
        if kill_mob:
            target_status = new_enemies_status['mobs'][-1]
            if match_support_class(ally_status):
                activate_master_class_effect(ally_status, target_status, skill_list)
        
        # if turn_num == 1:
           # use_support_skill(new_ally_status, target_status, turn_num)
        
        add_buff(target_status, 'def_buffs', [-0.1, 99, 'lia/T'])
        add_buff(new_ally_status, 'atk_dmg_dealt_buffs', [0.2, -1, 'lia/T'], turn_num)
        add_buff(target_status, 'atk_dmg_res_buffs', [-0.2, -1, 'lia/T'])
        add_buff(new_ally_status, 'atk_buffs', [0.1, 99, 'lia/T'])
        add_buff(new_ally_status, 'mag_buffs', [0.1, 99, 'lia/T'])
        add_buff(new_ally_status, 'tec_buffs', [0.1, 99, 'lia/T'])
        add_buff(new_ally_status, 'def_buffs', [0.1, 99, 'lia/T'])
        add_buff(new_ally_status, 'res_buffs', [0.1, 99, 'lia/T'])
        for _skill in skill_list:
            if 'id' in _skill:
                if _skill['id'] == 1:
                    if skill is None or 'dmg_modifier' in skill:
                        remove_buff(target_status)
                        add_buff(new_ally_status, 'fixed_dmg_atk', [1, -1, 'lia/P2'])
                elif _skill['id'] == 4:
                    add_buff(new_ally_status, 'battle_atk_buffs', [0.15, 99, 'overflow'])
                    add_buff(new_ally_status, 'tec_buffs', [0.15, 99, 'overflow'])
                    add_buff(new_ally_status, 'def_buffs', [-0.1, 99, 'overflow'])
                    add_buff(new_ally_status, 'res_buffs', [-0.1, 99, 'overflow'])
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                remove_buff(target_status)
                remove_buff(target_status)
            elif skill['id'] == 2:
                pass
            elif skill['id'] == 3:
                add_buff(new_ally_status, 'atk_buffs', [0.2, 3, 'Main/A'], turn_num)
                add_buff(new_ally_status, 'atk_dmg_dealt_buffs', [0.2, 3, 'Main/A'], turn_num)
            elif skill['id'] == 5:
                pass
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'attack'}, _skill)
        dmg = dmg[dmg_type] if dmg != None else 0
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
            if _skill['id'] == 3:
                act_again = True
            elif _skill['id'] == 5:
                if kill_mob:
                    reduce_skill_cooldown(new_skill_list, 5, 3)
        for _skill in new_skill_list:
            if 'effect' in _skill and _skill['effect'].startswith('act again') and _skill['cd'] == 0 and not act_again:
                _skill['cd'] = _skill['ct']
                act_again = True
        activate_after_action_effects(new_ally_status, target_status, new_skill_list, skill, turn_num, kill_enemy=kill_mob)
        
        if kill_mob:
            new_enemies_status['mobs'].pop()
        if not act_again:
            dmg_enemy_turn = 0
            #dmg_enemy_turn = calc_damage(new_ally_status, new_enemies_status['boss'], {'type': 'attack', on_enemy_turn=True}, None)[2]
            for mob in new_enemies_status['mobs']:
                dmg_enemy_turn += calc_damage(new_ally_status, mob, {'type': 'attack'}, None, on_enemy_turn=True)[2]
            new_enemies_status['mobs'][:] = []
            action_list[-1].append(dmg_enemy_turn)
        
        new_sub_turn = 0 if not act_again else sub_turn + 1
        new_ally_status = update_duration(new_ally_status, turn_num)
        total_dmg = max(total_dmg, dmg + recur_lia(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
lia_stats = {
                    'class': 'soldier',
                    'master_class_lv': 3,
                    'atk': 568,
                    'tec': 333,
                    'def': 254,
                }
lia_status = lia_stats
lia_status = add_teamwise_buffs(['symbol skill'], lia_stats)
#print json.dumps(lia_status, indent=2)
lia_skills = [
                    {'id': 0, 'type': 'active', 'ct': 2, 'dmg_modifier': 1.3},
                    {'id': 1, 'type': 'passive'},
                    {'id': 2, 'type': 'active', 'ct': 5, 'dmg_modifier': 1.7},
                    {'id': 3, 'type': 'active', 'ct': 3},
                    {'id': 4, 'type': 'passive'},
                    {'id': 5, 'type': 'active', 'ct': 5, 'dmg_modifier': 2},
                 ]
lia_skill_sets = get_all_skill_sets(lia_skills, must_include_skill_ids=[3, 2, 5])

lia_status = load_equipments(['executioner', "zenith's wings", "thymos helm", 'zenith amulet'], lia_status)
lia_status = load_enchantments(['strike'], lia_status)
lia_status = load_enchantment_random_stats('max_atk_percent', lia_status)
lia_status = link_support('apollo', lia_status)
lia_dmg = 0
for skill_set in lia_skill_sets:
    lia_dmg = max(lia_dmg,
        recur_lia(
            1,
            lia_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print lia_dmg
print [skill['id'] for skill in best_skill_set if 'id' in skill]
print best_action_list
lia_dmg_enemy_turn = 0
for action in best_action_list:
    if len(action) > 3:
        lia_dmg_enemy_turn += action[3]
print lia_dmg_enemy_turn

# print recur_lia(
            # 1,
            # lia_status,
            # {
                # 'boss': {
                    # 'dmg_res_buffs': [-0.35],
                # },
                # 'mobs': [],
            # },
            # lia_skills[1:2] + lia_skills[0:1] + lia_skills[5:6],
            # [],
            # 2)