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

def recur_sjeanne(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
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
    
    if sub_turn == 0:
        update_start_of_turn(ally_status, turn_num)
    skill_list = reduce_cooldown(skill_list, sub_turn)
    avail_skills = find_avail_skills(skill_list)
    if turn_num == 1 and sub_turn == 0:
        avail_skills = [skill_list[0]]
    elif turn_num == 3 and sub_turn == 1:
        avail_skills = [skill_list[0]]
    # elif turn_num == 1 and sub_turn == 1:
        # avail_skills = [None]
    # elif turn_num == 2 and sub_turn == 0:
        # avail_skills = [skill_list[2]]
        
    for skill in avail_skills:
        act_again = False
        new_enemies_status = enemy_generator.update_enemies(enemies_status, turn_num, sub_turn)
        new_ally_status = copy.deepcopy(ally_status)
        target_status = new_enemies_status['boss']
        kill_mob = len(new_enemies_status['mobs']) > 0
        kill_mob = False
        if kill_mob:
            target_status = new_enemies_status['mobs'][-1]
            if match_support_class(ally_status):
                activate_master_class_effect(ally_status, target_status, skill_list)
        
        if turn_num == 1:
           use_support_skill(new_ally_status, target_status, turn_num)
           
        # if turn_num == 4 and sub_turn == 0:
            # add_buff(new_ally_status, 'atk_buffs', [0.22, 2, 'Support/A'], 0)
        # if turn_num == 5 and sub_turn == 0:
            # add_buff(new_ally_status, 'atk_buffs', [0.25, 2, 'Support/A'], 0)
        # if turn_num >= 2:
            # add_buff(new_ally_status, 'crit_rate_buffs', [0.1, 99, 'azur sword'])
            # add_buff(new_ally_status, 'crit_dmg_buffs', [0.1, 99, 'azur sword'])
            # add_buff(new_ally_status, 'skill_dmg_dealt_buffs', [0.2, 99, 'sol'])
        
        add_buff(new_ally_status, 'battle_atk_buffs', [0.2, 99, 'one summer memory'])
        add_buff(new_ally_status, 'def_buffs', [0.25, 99, 'one summer memory'])
        add_buff(new_ally_status, 'res_buffs', [0.25, 99, 'one summer memory'])
        
        talent_stack_cnt = min(sum_buffs(new_ally_status, 'summer romance'), 3)
        add_buff(new_ally_status, 'crit_rate_buffs', [0.08 * talent_stack_cnt, 99, 'one summer memory'], turn_num)
        for _skill in skill_list:
            if 'id' in _skill:
                if _skill['id'] == 2:
                    add_buff(new_ally_status, 'crit_rate_buffs', [0.15, 99, "mind's eye"])
                elif _skill['id'] == 3:
                    add_buff(new_ally_status, 'dmg_dealt_buffs', [0.15, 99, 'summer-only saint'])
                    if talent_stack_cnt >= 1:
                        add_buff(new_ally_status, 'battle_dmg_res_buffs', [0.1, 99, 'summer-only saint'], turn_num)
                    if talent_stack_cnt >= 2:
                        add_buff(new_ally_status, 'atk_buffs', [0.1, 99, 'summer-only saint'], turn_num)
                        add_buff(new_ally_status, 'mag_buffs', [0.1, 99, 'summer-only saint'], turn_num)
                    if talent_stack_cnt >= 3:
                        add_buff(new_ally_status, 'crit_dmg_buffs', [0.1, 99, 'summer-only saint'], turn_num)
        if skill == None:
            pass
        else:                
            if skill['id'] == 0:
                pass
            elif skill['id'] == 1:
                pass
            elif skill['id'] == 4:
                new_ally_status = add_teamwise_buffs(['symbol skill'], new_ally_status)
                if turn_num >= 3:
                    add_buff(new_ally_status, 'battle_dmg_dealt_buffs', [0.2, 4, 'blessing of zenith', 'hp <=80%'], turn_num)
            elif skill['id'] == 5:
                add_buff(target_status, 'atk_buffs', [-0.2, 1, 'Main/A'], turn_num)
                add_buff(target_status, 'def_buffs', [-0.2, 1, 'Main/A'], turn_num)
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'attack'}, _skill)
        dmg = dmg[dmg_type] if dmg != None else 0
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
        if skill is None or 'dmg_modifier' in skill:
                add_buff(new_ally_status, 'summer romance', [1, 4], turn_num)
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
        total_dmg = max(total_dmg, dmg + recur_sjeanne(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg

sjeanne_stats = {
                    'class': 'soldier',
                    'master_class_lv': 3,
                    'atk': 573,
                    'tec': 336,
                    # 'enchant_atk_percent_n_2set': [0.15, 0.05, 0.05, 0.09],
                    # 'enchant_flat_atk': [31, 11, 11, 21*0+15],
                    # 'crit_rate_buffs': [0.1*0],
                }
sjeanne_status = load_equipments(['crimson lotus sword', "thymos surcoat", "warrior princess's helm", "orichalcon ring"], sjeanne_stats)
sjeanne_status = load_enchantments(['strike'], sjeanne_status)
sjeanne_status = load_enchantment_random_stats('max_atk_percent', sjeanne_status)
sjeanne_status = link_support('smichael', sjeanne_status)
#sjeanne_status = add_teamwise_buffs(['symbol skill'], sjeanne_status)
sjeanne_skills = [
                    {'id': 0, 'type': 'active', 'ct': 1, 'dmg_modifier': 1.3},
                    {'id': 1, 'type': 'active', 'ct': 2, 'dmg_modifier': 1.5},
                    {'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'passive'},
                    {'id': 4, 'type': 'active', 'ct': 3},
                    {'id': 5, 'type': 'active', 'ct': 4, 'dmg_modifier': 1.8},
                 ]
sjeanne_dmg = 0
sjeanne_skill_sets = get_all_skill_sets(sjeanne_skills, must_include_skill_ids=[4, 3])
for skill_set in sjeanne_skill_sets:
    sjeanne_dmg = max(sjeanne_dmg,
        recur_sjeanne(
            1,
            sjeanne_status,
            {
                'boss': {
                    #'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print sjeanne_dmg
print [skill['id'] for skill in best_skill_set if 'id' in skill]
print best_action_list
sjeanne_dmg_enemy_turn = 0
for action in best_action_list:
    if len(action) > 3:
        sjeanne_dmg_enemy_turn += action[3]
print sjeanne_dmg_enemy_turn
