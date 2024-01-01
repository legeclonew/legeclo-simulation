import copy
import json
from damage_calculator import calc_damage, get_crit_rate
from simulate_battle import *
from equipments import load_equipments
from enchantments import *
from supports import link_support
from enemies import get_generator

'''
    0 = all non-crit/min damage
    1 = all crit/max damage
    2 = expected value/average damage
'''
DAMAGE_MODE = 2

enemy_generator = get_generator('normal')
enemy_generator.default_def = 100
enemy_generator.is_silenced = True
enemy_generator.num_new_mobs_per_turn = 2
best_action_list = []
best_skill_set = None

def recur_nyokita(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
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
        
    for skill in avail_skills:
        act_again = False
        new_enemies_status = enemy_generator.update_enemies(enemies_status, turn_num, sub_turn)
        new_ally_status = copy.deepcopy(ally_status)
        target_status = new_enemies_status['boss']
        kill_mob = len(new_enemies_status['mobs']) > 0
        kill_mob = kill_mob and (skill is not None and skill['id'] == 5)
        #kill_mob = False
        if kill_mob:
            target_status = new_enemies_status['mobs'][-1]
            if match_support_class(ally_status):
                activate_master_class_effect(ally_status, target_status, skill_list)
        
        if turn_num == 1:
           use_support_skill(new_ally_status, target_status, turn_num)
        
        for _skill in skill_list:
            if 'id' in _skill:
                if _skill['id'] == 2:
                    remove_buff(target_status)
                    add_buff(target_status, 'def_buffs', [-0.2, 1, "duel aura"])
                elif _skill['id'] == 3:
                    add_buff(new_ally_status, 'skill_dmg_dealt_buffs', [0.2, 99, "rabbit god worship"])
                    add_buff(new_ally_status, 'dmg_res_buffs', [0.1, 99, "rabbit god worship"])
                    add_buff(new_ally_status, 'battle_atk_buffs', [0.1, 99, "rabbit god worship"])
                elif _skill['id'] == 4:
                    add_buff(new_ally_status, 'battle_atk_buffs', [0.15, 99, 'overflow'])
                    add_buff(new_ally_status, 'tec_buffs', [0.15, 99, 'overflow'])
                    add_buff(new_ally_status, 'def_buffs', [-0.1, 99, 'overflow'])
                    add_buff(new_ally_status, 'res_buffs', [-0.1, 99, 'overflow'])
        add_buff(new_ally_status, 'atk_buffs', [0.25, 99, 'rabbit maiden dance'])
        add_buff(new_ally_status, 'def_buffs', [0.25, 99, 'rabbit maiden dance'])
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                add_buff(target_status, 'atk_dmg_res_buffs', [-0.2, 1, 'Main/A'], turn_num)
            elif skill['id'] == 1:
                add_buff(target_status, 'dmg_res_buffs', [-0.1, -1, 'Main/A'], turn_num)
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'attack'}, _skill)[dmg_type]
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
            
            if 'dmg_modifier' in skill:
                add_buff(new_ally_status, 'talent_buffs', [1, 3], turn_num)
                talent_stack_cnt = min(sum_buffs(new_ally_status, 'talent_buffs'), 2)
                add_buff(new_ally_status, 'dmg_dealt_buffs', [0.15 * talent_stack_cnt, 3, 'rabbit maiden dance'], turn_num)
                if kill_mob:
                    reduce_skill_cooldown(new_skill_list, skill['id'])
                    if skill['id'] == 5:
                        add_buff(new_ally_status, 'skill_dmg_dealt_buffs', [0.2, 2, "Main/A"], turn_num)
        if kill_mob:
            for _skill in new_skill_list:
                if _skill['id'] == 3 and _skill['cd'] == 0:
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
        total_dmg = max(total_dmg, dmg + recur_nyokita(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
nyokita_stats = {
                    'class': 'rider',
                    'master_class_lv': 3,
                    'atk': 614,
                    'tec': 279,
                    'def': 242,
                }
nyokita_status = nyokita_stats
nyokita_status = add_teamwise_buffs(['symbol skill', 'azur sword'], nyokita_stats)
nyokita_skills = [
                    {'id': 0, 'type': 'active', 'ct': 1, 'dmg_modifier': 1.5},
                    {'id': 1, 'type': 'active', 'ct': 3, 'dmg_modifier': 1.3},
                    #{'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'passive', 'ct': 2},
                    {'id': 4, 'type': 'passive'},
                    {'id': 5, 'type': 'active', 'ct': 3, 'dmg_modifier': 2},
                 ]
nyokita_skill_sets = get_all_skill_sets(nyokita_skills, must_include_skill_ids=[0, 3])

nyokita_status = load_equipments(['moon-splitting cleaver', "golden conscious", "tracking headband", "ring of life"], nyokita_status)
nyokita_status = load_enchantments(['strike'], nyokita_status)
nyokita_status = load_enchantment_random_stats('max_atk_percent', nyokita_status)
nyokita_status = link_support('amaterasu_newyear', nyokita_status)
nyokita_dmg = 0
for skill_set in nyokita_skill_sets:
    nyokita_dmg = max(nyokita_dmg,
        recur_nyokita(
            1,
            nyokita_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            DAMAGE_MODE))
print "Total damage (player phase): %f" % nyokita_dmg
log_skill_set(best_skill_set)
log_action_list(best_action_list)