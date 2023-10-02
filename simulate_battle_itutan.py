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

enemy_generator = get_generator('gex3')
enemy_generator.default_res = 100
enemy_generator.is_silenced = True
enemy_generator.num_new_mobs_per_turn = 2
best_action_list = []
best_skill_set = None
                    
def recur_itutan(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
    if match_support_class(ally_status) and turn_num == 1 and sub_turn == 0:
        activate_master_class_effect(ally_status, enemies_status['boss'], skill_list)
    
    if turn_num > 5:
        global best_action_list
        global best_skill_set
        if sum_dmg(action_list) > sum_dmg(best_action_list):
            best_action_list = copy.deepcopy(action_list)
            best_skill_set = skill_list
            print "Crit rate: %f" % get_crit_rate(ally_status, enemies_status['boss'])
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
        #kill_mob = kill_mob and skill != None and 'dmg_modifier' in skill
        kill_mob = kill_mob and skill != None and skill['id'] == 3
        #kill_mob = False
        if kill_mob:
            target_status = new_enemies_status['mobs'][-1]
            if match_support_class(ally_status):
                activate_master_class_effect(ally_status, target_status, skill_list)
        
        if turn_num == 2:
           use_support_skill(new_ally_status, target_status, turn_num)
        
        add_buff(new_ally_status, 'skill_dmg_dealt_buffs', [0.25, 99, "because i'm an idol!"])
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                pass
            elif skill['id'] == 1:
                add_buff(new_ally_status, 'dmg_dealt_buffs', [0.1, 1, 'Main/A'], turn_num)
            elif skill['id'] == 3:  # Need to kill an enemy
                pass
            elif skill['id'] == 4:
                new_ally_status = add_teamwise_buffs(['symbol skill'], new_ally_status)
            elif skill['id'] == 5:
                add_buff(target_status, 'mag_dmg_res_buffs', [-0.2, 1, 'Main/A'], turn_num)
        talent_stack_cnt = min(sum_buffs(new_ally_status, 'sparkly ale'), 3)
        if talent_stack_cnt > 0:
            add_buff(new_ally_status, 'atk_buffs', [0.05 * talent_stack_cnt, 4, "because i'm an idol!"], turn_num)
            add_buff(new_ally_status, 'mag_buffs', [0.05 * talent_stack_cnt, 4, "because i'm an idol!"], turn_num)
            add_buff(new_ally_status, 'tec_buffs', [0.05 * talent_stack_cnt, 4, "because i'm an idol!"], turn_num)
            add_buff(new_ally_status, 'def_buffs', [0.05 * talent_stack_cnt, 4, "because i'm an idol!"], turn_num)
            add_buff(new_ally_status, 'res_buffs', [0.05 * talent_stack_cnt, 4, "because i'm an idol!"], turn_num)
        if talent_stack_cnt >= 2 and (skill is None or skill['id'] != 1):
            add_buff(target_status, 'battle_dmg_res_buffs', [-0.1, 4, "because i'm an idol!"], turn_num)
            add_buff(target_status, 'battle_dmg_dealt_buffs', [-0.1, 4, "because i'm an idol!"], turn_num)
        if talent_stack_cnt >= 3:
            add_buff(new_ally_status, 'battle_dmg_dealt_buffs', [0.15, 4, "because i'm an idol!"], turn_num)
            add_buff(new_ally_status, 'battle_dmg_res_buffs', [0.15, 4, "because i'm an idol!"], turn_num)
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'magic'}, _skill)
        dmg = dmg[dmg_type] if dmg != None else 0
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
                    
            if 'dmg_modifier' in skill:
                add_buff(new_ally_status, 'sparkly ale', [1, 4], turn_num)
            
            if skill['id'] == 1:
                act_again = True
            elif skill['id'] == 3 and kill_mob:
                act_again = True
        activate_after_action_effects(new_ally_status, target_status, new_skill_list, skill, turn_num, kill_enemy=kill_mob)
        
        if kill_mob:
            new_enemies_status['mobs'].pop()
        if not act_again:
            dmg_enemy_turn = 0
            #dmg_enemy_turn = calc_damage(new_ally_status, new_enemies_status['boss'], {'type': 'magic', on_enemy_turn=True}, None)[2]
            for mob in new_enemies_status['mobs']:
                dmg_enemy_turn += calc_damage(new_ally_status, mob, {'type': 'magic'}, None, dmg_penalty=False, on_enemy_turn=True)[2]
            new_enemies_status['mobs'][:] = []
            action_list[-1].append(dmg_enemy_turn)
        
        new_sub_turn = 0 if not act_again else sub_turn + 1
        new_ally_status = update_duration(new_ally_status, turn_num)
        total_dmg = max(total_dmg, dmg + recur_itutan(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
itutan_stats = {
                    'class': 'saint',
                    'master_class_lv': 3,
                    'mag': 568,
                    'tec': 101,
                    'res': 212,
                }
itutan_status = add_teamwise_buffs(['mc', 'azur sword'], itutan_stats)
itutan_skills = [
                    {'id': 0, 'type': 'active', 'ct': 1, 'dmg_modifier': 1.5},
                    {'id': 1, 'type': 'active', 'ct': 3},
                    {'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'active', 'ct': 4, 'dmg_modifier': 1.5},
                    {'id': 4, 'type': 'active', 'ct': 3},
                    {'id': 5, 'type': 'active', 'ct': 4, 'dmg_modifier': 1.6},
                 ]
itutan_skill_sets = get_all_skill_sets(itutan_skills, must_include_skill_ids=[1])

itutan_status = load_equipments(['zion jabana', 'everlasting darkness ceremonial dress', "leo's heavenly crown", 'necklace of everlasting darkness'], itutan_status)
itutan_status = load_enchantments(['strike'], itutan_status)
itutan_status = load_enchantment_random_stats('max_mag_percent', itutan_status)
itutan_status = link_support('sol', itutan_status)
itutan_dmg = 0
for skill_set in itutan_skill_sets:
    itutan_dmg = max(itutan_dmg,
        recur_itutan(
            1,
            itutan_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            DAMAGE_MODE))
print "Total damage (player phase): %f" % itutan_dmg
log_skill_set(best_skill_set)
log_action_list(best_action_list)