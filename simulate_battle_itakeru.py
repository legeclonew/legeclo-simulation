import copy
import json
from damage_calculator import calc_damage, get_crit_rate
from simulate_battle import *
from equipments import load_equipments
from enchantments import *
from supports import link_support
from enemies import get_generator

enemy_generator = get_generator('gex3')
enemy_generator.default_res = 100
enemy_generator.is_silenced = True
enemy_generator.num_new_mobs_per_turn = 2
best_action_list = []
best_skill_set = None

def recur_itakeru(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
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
    # if len(action_list) == 0:
        # avail_skills = [skill_list[0]]
    # elif len(action_list) == 1:
        # avail_skills = [None]
    # elif len(action_list) == 2:
        # avail_skills = [skill_list[0]]
    # elif len(action_list) == 3:
        # avail_skills = [skill_list[2]]
    # elif len(action_list) == 4:
        # avail_skills = [skill_list[0]]
    # elif len(action_list) == 5:
        # avail_skills = [None]
    # elif len(action_list) == 6:
        # avail_skills = [skill_list[0]]
    # elif len(action_list) == 7:
        # avail_skills = [skill_list[2]]     
    for skill in avail_skills:
        act_again = False
        new_enemies_status = enemy_generator.update_enemies(enemies_status, turn_num, sub_turn)
        new_ally_status = copy.deepcopy(ally_status)
        target_status = new_enemies_status['boss']
        kill_mob = len(new_enemies_status['mobs']) > 0
        #kill_mob = kill_mob and (turn_num == 2 or turn_num == 4)
        kill_mob = False
        if kill_mob:
            target_status = new_enemies_status['mobs'][-1]
            if match_support_class(ally_status):
                activate_master_class_effect(ally_status, target_status, skill_list)
        
        if turn_num == 2:
           use_support_skill(new_ally_status, target_status, turn_num)
        
        add_buff(target_status, 'mag_dmg_res_buffs', [-0.15, 99, 'yamatotakeru_half/T'])
        for _skill in skill_list:
            if _skill['id'] == 1:
                add_buff(new_ally_status, 'atk_buffs', [0.1, 1, 'yamatotakeru_half/P2'], turn_num)
                add_buff(new_ally_status, 'mag_buffs', [0.1, 1, 'yamatotakeru_half/P2'], turn_num)
            elif _skill['id'] == 2:
                add_buff(new_ally_status, 'dmg_dealt_buffs', [0.1, 99, 'hit & away'])
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                pass
            elif skill['id'] == 3:
                if 'mov_buffs' in new_ally_status:
                    add_buff(new_ally_status, 'skill_dmg_dealt_buffs', [0.3, -1, 'Main/A'])
                else:
                    add_buff(new_ally_status, 'skill_dmg_dealt_buffs', [0.24, -1, 'Main/A'])
            elif skill['id'] == 4:
                pass
            elif skill['id'] == 5:
                add_buff(target_status, 'def_buffs', [-0.2, 2, 'Main/A'], turn_num)
                add_buff(target_status, 'res_buffs', [-0.2, 2, 'Main/A'], turn_num)
        talent_stack_cnt = min(sum_buffs(new_ally_status, 'talent_buffs'), 3)
        if talent_stack_cnt > 0:
            add_buff(new_ally_status, 'atk_buffs', [0.1 * talent_stack_cnt, 1, 'yamatotakeru_half/T'], turn_num)
            add_buff(new_ally_status, 'mag_buffs', [0.1 * talent_stack_cnt, 1, 'yamatotakeru_half/T'], turn_num)
            add_buff(new_ally_status, 'tec_buffs', [0.1 * talent_stack_cnt, 1, 'yamatotakeru_half/T'], turn_num)
            add_buff(new_ally_status, 'def_buffs', [0.1 * talent_stack_cnt, 1, 'yamatotakeru_half/T'], turn_num)
            add_buff(new_ally_status, 'res_buffs', [0.1 * talent_stack_cnt, 1, 'yamatotakeru_half/T'], turn_num)
        if talent_stack_cnt >= 1:
                add_buff(new_ally_status, 'mag_dmg_dealt_buffs', [0.1, 1, 'yamatotakeru_half/T'], turn_num)
        if talent_stack_cnt >= 2:
            add_buff(new_ally_status, 'dmg_dealt_buffs', [0.1, 1, 'yamatotakeru_half/T'], turn_num)
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        if _skill != None and _skill['id'] == 5:
            _skill['dmg_modifier'] = 1.6 + 0.2 * min(talent_stack_cnt, 2)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        # print json.dumps(debug_buffs(new_ally_status), indent=2)
        # print json.dumps(debug_buffs(target_status), indent=2)
        # print
        dmg = calc_damage(new_ally_status, target_status, {'type': 'magic'}, _skill)[dmg_type]
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
                   
            if 'dmg_modifier' in skill:
                add_buff(new_ally_status, 'talent_buffs', [1, 4], turn_num)
                for _skill in new_skill_list:
                    if _skill['id'] == 1 and _skill['cd'] == 0:
                        _skill['cd'] = _skill['ct']
                        act_again = True
        activate_after_action_effects(new_ally_status, target_status, new_skill_list, skill, turn_num, kill_enemy=kill_mob)
        
        if kill_mob:
            new_enemies_status['mobs'].pop()
        if not act_again:
            dmg_enemy_turn = 0
            #dmg_enemy_turn = calc_damage(new_ally_status, new_enemies_status['boss'], {'type': 'magic', on_enemy_turn=True}, None)[2]
            for mob in new_enemies_status['mobs']:
                dmg_enemy_turn += calc_damage(new_ally_status, mob, {'type': 'magic'}, None, dmg_penalty=True, on_enemy_turn=True)[2]
            new_enemies_status['mobs'][:] = []
            action_list[-1].append(dmg_enemy_turn)
        
        new_sub_turn = 0 if not act_again else sub_turn + 1
        new_ally_status = update_duration(new_ally_status, turn_num)
        total_dmg = max(total_dmg, dmg + recur_itakeru(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
itakeru_stats = {
                    'class': 'sorcerer',
                    'master_class_lv': 3,
                    'mag': 580,
                    'tec': 126,
                    'res': 254,
                }
itakeru_status = add_teamwise_buffs(['symbol skill'], itakeru_stats)
#print json.dumps(itakeru_status, indent=2)
itakeru_skills = [
                    {'id': 0, 'type': 'active', 'ct': 1, 'dmg_modifier': 1.5},
                    {'id': 1, 'type': 'passive', 'ct': 2},
                    {'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'active', 'ct': 3, 'dmg_modifier': 1.6},
                    {'id': 4, 'type': 'active', 'ct': 2, 'dmg_modifier': 1.5},
                    {'id': 5, 'type': 'active', 'ct': 5, 'dmg_modifier': 1.6},
                 ]
itakeru_skill_sets = get_all_skill_sets(itakeru_skills, must_include_skill_ids=[1])
itakeru_dmg = 0
for skill_set in itakeru_skill_sets:
    itakeru_dmg = max(itakeru_dmg,
        recur_itakeru(
            1,
            itakeru_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print itakeru_dmg

itakeru_status = load_equipments(['yata no kagami', 'everlasting darkness ceremonial dress', 'elemental hat', 'origin amulet'], itakeru_status)
itakeru_status = load_enchantments(['break'], itakeru_status)
itakeru_status = load_enchantment_random_stats('max_mag_percent', itakeru_status)
itakeru_status = link_support('nyarlathotep', itakeru_status)
itakeru_dmg = 0
for skill_set in itakeru_skill_sets:
    itakeru_dmg = max(itakeru_dmg,
        recur_itakeru(
            1,
            itakeru_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print itakeru_dmg
print [skill['id'] for skill in best_skill_set if 'id' in skill]
print best_action_list
itakeru_dmg_enemy_turn = 0
for action in best_action_list:
    if len(action) > 3:
        itakeru_dmg_enemy_turn += action[3]
print itakeru_dmg_enemy_turn

# print recur_itakeru(
            # 1,
            # itakeru_status,
            # {
                # 'boss': {
                    # 'dmg_res_buffs': [-0.35],
                # },
                # 'mobs': [],
            # },
            # itakeru_skills[1:2] + itakeru_skills[0:1] + itakeru_skills[5:6],
            # [],
            # 2)