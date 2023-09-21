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
enemy_generator.is_silenced = False
enemy_generator.num_new_mobs_per_turn = 2
best_action_list = []
best_skill_set = None

def recur_saffie(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
    if match_support_class(ally_status) and turn_num == 1 and sub_turn == 0:
        activate_master_class_effect(ally_status, enemies_status['boss'], skill_list)
        
    if turn_num == 1 and sub_turn == 0:
        if len(skill_list) == 0 or 'id' in skill_list[-1]:
            skill_list.append({'type': 'passive', 'ct': 1, 'effect': 'act again'})

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
    avail_skills = find_avail_skills_and_use(skill_list)
    # if (turn_num == 1) and sub_turn == 0:
        # avail_skills = [skill_list[0]]
        
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
        
        for _skill in skill_list:
            if 'id' in _skill:
                if _skill['id'] == 1:
                    add_buff(new_ally_status, 'atk_buffs', [0.08, 99, 'saffie/P'])
                    add_buff(new_ally_status, 'mag_buffs', [0.08, 99, 'saffie/P'])
                    add_buff(new_ally_status, 'def_buffs', [0.08, 99, 'saffie/P'])
                    add_buff(new_ally_status, 'res_buffs', [0.08, 99, 'saffie/P'])
                elif _skill['id'] == 4:
                    add_buff(new_ally_status, 'battle_dmg_dealt_buffs', [0.15, 99, 'gospel'])
        add_buff(new_ally_status, 'mag_dmg_dealt_buffs', [0.25, 99, 'saffie/T'])
        if skill is None or 'dmg_modifier' in skill:
             add_buff(target_status, 'res_buffs', [-0.25, -1, 'saffie/T'], turn_num)
        add_buff(new_ally_status, 'atk_buffs', [0.1, 99, 'saffie/T'])
        add_buff(new_ally_status, 'mag_buffs', [0.1, 99, 'saffie/T'])
        add_buff(new_ally_status, 'def_buffs', [0.1, 99, 'saffie/T'])
        add_buff(new_ally_status, 'res_buffs', [0.1, 99, 'saffie/T'])
        add_buff(new_ally_status, 'tec_buffs', [0.1, 99, 'saffie/T'])
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                pass
            elif skill['id'] == 2:
                pass
            elif skill['id'] == 3:
                add_buff(new_ally_status, 'res_buffs', [0.2, 3, 'Main/A'], turn_num)
                add_buff(new_ally_status, 'dmg_res_buffs', [0.2, 3, 'Main/A'], turn_num)
            elif skill['id'] == 5:
                add_buff(target_status, 'dmg_res_buffs', [-0.2, 1, 'Main/A'], turn_num)
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'magic'}, _skill)
        dmg = dmg[dmg_type] if dmg != None else 0
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
            if _skill['id'] == 3:
                act_again = True
        if skill is None or 'dmg_modifier' in skill:
            for _skill in new_skill_list:
                if 'effect' in _skill and _skill['effect'].startswith('act again') and _skill['cd'] == 0 and not act_again:
                    _skill['cd'] = _skill['ct']
                    act_again = True
        activate_after_action_effects(new_ally_status, target_status, new_skill_list, skill, turn_num, kill_enemy=kill_mob)
        
        if kill_mob:
            new_enemies_status['mobs'].pop()
        if not act_again:
            dmg_enemy_turn = 0
            #dmg_enemy_turn = calc_damage(new_ally_status, new_enemies_status['boss'], {'type': 'attack', on_enemy_turn=True}, None)[dmg_type]
            for mob in new_enemies_status['mobs']:
                dmg_enemy_turn += calc_damage(new_ally_status, mob, {'type': 'magic'}, None, on_enemy_turn=True)[dmg_type]
            new_enemies_status['mobs'][:] = []
            action_list[-1].append(dmg_enemy_turn)
        
        new_sub_turn = 0 if not act_again else sub_turn + 1
        new_ally_status = update_duration(new_ally_status, turn_num)
        total_dmg = max(total_dmg, dmg + recur_saffie(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
saffie_stats = {
                    'class': 'saint',
                    'master_class_lv': 3,
                    'mag': 592,
                    'tec': 105,
                    'res': 242,
                }
saffie_status = saffie_stats
saffie_status = add_teamwise_buffs(['mc', 'azur sword'], saffie_stats)
saffie_skills = [
                    {'id': 0, 'type': 'active', 'ct': 1, 'dmg_modifier': 1.8},
                    {'id': 1, 'type': 'passive'},
                    #{'id': 2, 'type': 'active', 'ct': 1},
                    {'id': 3, 'type': 'active', 'ct': 3},
                    {'id': 4, 'type': 'passive'},
                    {'id': 5, 'type': 'active', 'ct': 3, 'dmg_modifier': 1.8},
                 ]
saffie_skill_sets = get_all_skill_sets(saffie_skills, must_include_skill_ids=[1])

saffie_status = load_equipments(['zion jabana', 'everlasting darkness ceremonial dress', "leo's heavenly crown", 'necklace of everlasting darkness'], saffie_status)
saffie_status = load_enchantments(['strike'], saffie_status)
saffie_status = load_enchantment_random_stats('max_mag_percent', saffie_status)
saffie_status = link_support('sol', saffie_status)
saffie_dmg = 0
for skill_set in saffie_skill_sets:
    saffie_dmg = max(saffie_dmg,
        recur_saffie(
            1,
            saffie_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            DAMAGE_MODE))
print "Total damage (player phase): %f" % saffie_dmg
log_skill_set(best_skill_set)
log_action_list(best_action_list)