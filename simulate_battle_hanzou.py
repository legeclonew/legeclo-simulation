import copy
import json
from damage_calculator import calc_damage, get_crit_rate
from simulate_battle import *
from equipments import load_equipments
from enchantments import *
from supports import link_support
from enemies import get_generator

enemy_generator = get_generator('gex3')
enemy_generator.num_new_mobs_per_turn = 0
best_action_list = []
best_skill_set = None

def recur_hanzou(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
    if match_support_class(ally_status) and turn_num == 1 and sub_turn == 0:
        activate_master_class_effect(ally_status, enemies_status['boss'], skill_list)

    if turn_num > 5:
        global best_action_list
        global best_skill_set
        if sum_dmg(action_list) > sum_dmg(best_action_list):
            best_action_list = copy.deepcopy(action_list)
            best_skill_set = skill_list
        return 0
                
    total_dmg = 0
    
    skill_list = reduce_cooldown(skill_list, sub_turn)
    avail_skills = find_avail_skills(skill_list)
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
        
        # if turn_num == 2:
           # use_support_skill(new_ally_status, target_status)
        
        add_buff(new_ally_status, 'atk_dmg_dealt_buffs', [0.2, 99, 'teachings of iga'])
        add_buff(new_ally_status, 'crit_rate_buffs', [0.2, 99, 'teachings of iga'])
        for _skill in skill_list:
            if _skill['id'] == 4:
                add_buff(new_ally_status, 'crit_dmg_buffs', [0.2, 99, 'critical armor'])
        talent_stack_cnt = min(sum_buffs(new_ally_status, 'shinobi secret art'), 3)
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                add_buff(target_status, 'atk_dmg_res_buffs', [-0.1, 1, 'Main/A'])
            elif skill['id'] == 1:
                add_buff(new_ally_status, 'crit_rate_buffs', [0.2, 1, 'Main/A'])
                add_buff(new_ally_status, 'crit_dmg_buffs', [0.2, 1, 'Main/A'])
                if talent_stack_cnt >= 3:
                    add_buff(new_ally_status, 'fixed_dmg_atk', [2, 1, 'Main/A'])
                #print get_crit_rate(new_ally_status, target_status, None, False)
            elif skill['id'] == 5:
                #add_buff(new_ally_status, 'weak_debuff_success_rate', [1, 2, 'Main/A'])
                #add_buff(new_ally_status, 'weak_debuff_success_rate', [1, 2, 'Main/A'])
                if talent_stack_cnt >= 3:
                    add_buff(target_status, 'def_buffs', [-0.2, -1, 'Main/A'])
        if talent_stack_cnt > 0:
            add_buff(new_ally_status, 'atk_buffs', [0.05 * talent_stack_cnt, 1, 'teachings of iga'])
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'attack'}, _skill)
        if skill is None or skill['id'] != 1:
            dmg = dmg[dmg_type]
        else:
            dmg = 0
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
                   
            if skill['id'] == 1:
                act_again = True
        if skill is None or 'dmg_modifier' in skill:
            add_buff(new_ally_status, 'shinobi secret art', 1)
        activate_after_action_effects(new_ally_status, target_status, new_skill_list, skill, turn_num, kill_enemy=kill_mob)
        
        if kill_mob:
            new_enemies_status['mobs'].pop()
        if not act_again:
            dmg_enemy_turn = 0
            #dmg_enemy_turn = calc_damage(new_ally_status, new_enemies_status['boss'], {'type': 'magic', on_enemy_turn=True}, None)[2]
            for mob in new_enemies_status['mobs']:
                dmg_enemy_turn += calc_damage(new_ally_status, mob, {'type': 'attack'}, None, dmg_penalty=True, on_enemy_turn=True)[2]
            new_enemies_status['mobs'][:] = []
            action_list[-1].append(dmg_enemy_turn)
        
        new_sub_turn = 0 if not act_again else sub_turn + 1
        new_ally_status = update_duration(new_ally_status, new_sub_turn)
        total_dmg = max(total_dmg, dmg + recur_hanzou(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
hanzou_stats = {
                    'class': 'assassin',
                    'master_class_lv': 2,
                    'atk': 538,
                    'tec': 425,
                }
hanzou_status = add_teamwise_buffs(['symbol skill', 'cleared quest effect'], hanzou_stats)
#print json.dumps(hanzou_status, indent=2)
hanzou_skills = [
                    {'id': 0, 'type': 'active', 'ct': 1, 'dmg_modifier': 1.3},
                    {'id': 1, 'type': 'active', 'ct': 3},
                    #{'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'active', 'ct': 2, 'dmg_modifier': 1.1},
                    {'id': 4, 'type': 'passive'},
                    {'id': 5, 'type': 'active', 'ct': 5, 'dmg_modifier': 1.7},
                 ]
hanzou_skill_sets = get_all_skill_sets(hanzou_skills, must_include_skill_ids=[])
hanzou_dmg = 0
for skill_set in hanzou_skill_sets:
    hanzou_dmg = max(hanzou_dmg,
        recur_hanzou(
            1,
            hanzou_status,
            {
                'boss': {
                    #'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print hanzou_dmg

hanzou_status = load_equipments(['atomical fire', "assassin's vest", 'tracking headband', 'origin amulet'], hanzou_status)
hanzou_status = load_enchantments(['strike'], hanzou_status)
hanzou_status = load_enchantment_random_stats('avg', hanzou_status)
hanzou_status = link_support('byakko', hanzou_status)
hanzou_dmg = 0
for skill_set in hanzou_skill_sets:
    hanzou_dmg = max(hanzou_dmg,
        recur_hanzou(
            1,
            hanzou_status,
            {
                'boss': {
                    #'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print hanzou_dmg
print [skill['id'] for skill in best_skill_set if 'id' in skill]
print best_action_list
hanzou_dmg_enemy_turn = 0
for action in best_action_list:
    if len(action) > 3:
        hanzou_dmg_enemy_turn += action[3]
print hanzou_dmg_enemy_turn