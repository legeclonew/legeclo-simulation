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

def recur_alexander(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
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
    if (turn_num == 1) and sub_turn == 0:
        avail_skills = [skill_list[0]]
        
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
                if _skill['id'] == 4:
                    add_buff(new_ally_status, 'atk_buffs', [0.12, 99, "conqueror's command"])
                    add_buff(new_ally_status, 'mag_buffs', [0.12, 99, "conqueror's command"])
        #add_buff(new_ally_status, 'atk_buffs', [0.3, 99, 'support'])
        add_buff(new_ally_status, 'atk_buffs', [0.25, 99, 'alexander/T'])
        add_buff(new_ally_status, 'def_buffs', [0.25, 99, 'alexander/T'])
        add_buff(new_ally_status, 'battle_dmg_dealt_buffs', [0.25, 99, 'alexander/T'])
        add_buff(new_ally_status, 'battle_dmg_res_buffs', [0.25, 99, 'alexander/T'])
        if skill == None:
            pass
        else:
            if skill['id'] == 0:
                add_buff(new_ally_status, 'atk_buffs', [0.1])
                add_buff(new_ally_status, 'mag_buffs', [0.1])
                add_buff(new_ally_status, 'def_buffs', [0.1])
                add_buff(new_ally_status, 'res_buffs', [0.1])
                add_buff(new_ally_status, 'tec_buffs', [0.1])
            elif skill['id'] == 1:
                pass
            elif skill['id'] == 3:
                add_buff(target_status, 'def_buffs', [-0.15, 2, 'Main/A'], turn_num)
                add_buff(target_status, 'res_buffs', [-0.15, 2, 'Main/A'], turn_num)
            elif skill['id'] == 5:
                add_buff(target_status, 'atk_buffs', [-0.2, 2, 'Main/A'], turn_num)
                add_buff(target_status, 'mag_buffs', [-0.2, 2, 'Main/A'], turn_num)
            
        new_skill_list = copy.deepcopy(skill_list)
        _skill = skill if skill is None else copy.deepcopy(skill)
        activate_before_attack_effects(new_ally_status, target_status, _skill, turn_num)
        dmg = calc_damage(new_ally_status, target_status, {'type': 'attack'}, _skill)
        dmg = dmg[dmg_type] if dmg != None else 0
        action_list.append([turn_num, _skill if _skill is None else _skill['id'], dmg])
        if skill != None:
            put_skill_on_cooldown(new_skill_list, skill['id'])
            if _skill['id'] == 0:
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
        total_dmg = max(total_dmg, dmg + recur_alexander(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
alexander_stats = {
                    'class': 'rider',
                    'master_class_lv': 3,
                    'atk': 593,
                    'tec': 273,
                    'def': 231,
                }
alexander_status = alexander_stats
alexander_status = add_teamwise_buffs(['symbol skill'], alexander_stats)
alexander_skills = [
                    {'id': 0, 'type': 'active', 'ct': 5},
                    {'id': 1, 'type': 'active', 'ct': 2, 'dmg_modifier': 1.5},
                    #{'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'active', 'ct': 2, 'dmg_modifier': 1.6},
                    {'id': 4, 'type': 'passive'},
                    {'id': 5, 'type': 'active', 'ct': 3, 'dmg_modifier': 1.7},
                 ]
alexander_skill_sets = get_all_skill_sets(alexander_skills, must_include_skill_ids=[0, 4])

alexander_status = load_equipments(['azure sword', "assassin's vest", "tracking headband", "rakshasa's earrings"], alexander_status)
alexander_status = load_enchantments(['strike'], alexander_status)
alexander_status = load_enchantment_random_stats('max_atk_percent', alexander_status)
alexander_status = link_support('odin', alexander_status)
alexander_dmg = 0
for skill_set in alexander_skill_sets:
    alexander_dmg = max(alexander_dmg,
        recur_alexander(
            1,
            alexander_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            2))
print alexander_dmg
print [skill['id'] for skill in best_skill_set if 'id' in skill]
print best_action_list
alexander_dmg_enemy_turn = 0
for action in best_action_list:
    if len(action) > 3:
        alexander_dmg_enemy_turn += action[3]
print alexander_dmg_enemy_turn