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

def recur_toshizou(turn_num, ally_status, enemies_status, skill_list, action_list, dmg_type, sub_turn=0):
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
    
    skill_list = reduce_cooldown(skill_list, sub_turn)
    avail_skills = find_avail_skills(skill_list)
    # if (turn_num == 1) and sub_turn == 1:
        # avail_skills = [None]
    
    for skill in avail_skills:
        act_again = False
        new_enemies_status = enemy_generator.update_enemies(enemies_status, turn_num, sub_turn)
        new_ally_status = copy.deepcopy(ally_status)
        target_status = new_enemies_status['boss']
        kill_mob = len(new_enemies_status['mobs']) > 0
        kill_mob = kill_mob and ((turn_num == 1 and sub_turn == 0) or (turn_num == 4 and sub_turn == 0))
        #kill_mob = kill_mob and ((turn_num == 1 and sub_turn == 1) or (turn_num == 4 and sub_turn == 0))
        #kill_mob = False
        if kill_mob:
            target_status = new_enemies_status['mobs'][-1]
            if match_support_class(ally_status):
                activate_master_class_effect(ally_status, target_status, skill_list)
        
        if turn_num == 1:
           use_support_skill(new_ally_status, target_status, turn_num)
           
        # Team buffs
        if sub_turn == 0:
            # From MC
            add_buff(new_ally_status, 'atk_buffs', [0.1, 99, 'attack blessing'])
            add_buff(new_ally_status, 'battle_dmg_dealt_buffs', [0.15, 4, 'blessing of nadia'], 0)
            # From rider
            add_buff_including_minions(new_ally_status, 'crit_rate_buffs', [0.1, 2, 'azur sword'], 0)
            add_buff_including_minions(new_ally_status, 'crit_dmg_buffs', [0.1, 2, 'azur sword'], 0)
        
            #add_buff(new_ally_status, 'atk_buffs', [0.3, 99, 'Support/A'])
        
        
        talent_stack_cnt = min(sum_buffs(new_ally_status, 'pride of sincerity'), 3)
        add_buff(new_ally_status, 'atk_buffs', [0.12 * talent_stack_cnt, 99, 'toshizou/T'])
        add_buff(new_ally_status, 'crit_rate_buffs', [0.12 * talent_stack_cnt, 99, 'toshizou/T'])
        add_buff(new_ally_status, 'def_buffs', [-0.12 * talent_stack_cnt, 99, 'toshizou/T'])
        add_buff(new_ally_status, 'crit_dmg_buffs', [0.1 * talent_stack_cnt, -1, 'toshizou/T'], turn_num)
        if talent_stack_cnt <= 1:
            add_buff(target_status, 'atk_dmg_res_buffs', [0, -1, 'toshizou/T'], turn_num)
        elif talent_stack_cnt == 2:
            add_buff(target_status, 'atk_dmg_res_buffs', [-0.1, -1, 'toshizou/T'], turn_num)
        elif talent_stack_cnt == 3:
            add_buff(target_status, 'atk_dmg_res_buffs', [-0.15, -1, 'toshizou/T'], turn_num)
            
        # Sacrifice one minion
        if turn_num == 5 and sub_turn == 0 and "minions" in new_ally_status:
            new_ally_status["minions"].pop()
            add_buff(new_ally_status, 'dmg_dealt_buffs', [0.25, 1, 'bushido'], turn_num)
            add_buff(new_ally_status, 'dmg_res_buffs', [0.25, 1, 'bushido'], turn_num)
            
        for _skill in skill_list:
            if _skill['id'] == 0:
                add_buff(new_ally_status, 'atk_buffs', [0.1, 99, 'blade for victory'])
                add_buff(target_status, 'def_buffs', [-0.1, 1, 'blade for victory'], turn_num)
                add_buff(target_status, 'res_buffs', [-0.1, 1, 'blade for victory'], turn_num)
            elif _skill['id'] == 2:
                remove_buff(target_status)
                add_buff(target_status, 'atk_buffs', [-0.1, 1, 'grim face'], turn_num)
                add_buff(target_status, 'def_buffs', [-0.1, 1, 'grim face'], turn_num)
            elif _skill['id'] == 3:
                add_buff_including_minions(new_ally_status, 'dmg_dealt_buffs', [0.12, 99, 'mental support'])
                add_buff_including_minions(new_ally_status, 'dmg_res_buffs', [-0.12, 99, 'mental support'])
            elif _skill['id'] == 4:
                add_buff(new_ally_status, 'battle_atk_buffs', [0.15, 99, 'overflow'])
                add_buff(new_ally_status, 'tec_buffs', [0.15, 99, 'overflow'])
                add_buff(new_ally_status, 'def_buffs', [-0.1, 99, 'overflow'])
                add_buff(new_ally_status, 'res_buffs', [-0.1, 99, 'overflow'])
            elif _skill['id'] == 5:
                add_buff(new_ally_status, 'mov_buffs', [2, 99, 'indomitable lieutenant'])
                add_buff(new_ally_status, 'atk_dmg_dealt_buffs', [0.1, 99, 'indomitable lieutenant'])
                if talent_stack_cnt >= 3:
                    pass
                
        if skill == None:
            pass
        else:
            if skill['id'] == 1:
                if talent_stack_cnt < 3:
                    minion_status = {
                        'name': 'shinsengumi soldier',
                        'class': 'soldier',
                        'atk': 818,
                        'tec': 400,
                    }
                else:
                    minion_status = {
                        'name': 'mysterious shinsengumi soldier',
                        'class': 'soldier',
                        'atk': 1198,
                        'tec': 404,
                    }
                minion_status["summon_turn"] = turn_num
                add_buff(minion_status, 'dmg_dealt_buffs', [0.2, 99, 'bushido'])
                add_buff(minion_status, 'mov_buffs', [2, 99, 'bushido'])
                add_buff(minion_status, 'battle_atk_buffs', [0.2, 99, 'bushido'])
                add_buff(minion_status, 'def_buffs', [0.2, 99, 'bushido'])
                add_buff(minion_status, 'battle_atk_buffs', [0.15, 99, 'overflow'])
                add_buff(minion_status, 'tec_buffs', [0.15, 99, 'overflow'])
                add_buff(minion_status, 'def_buffs', [-0.1, 99, 'overflow'])
                add_buff(minion_status, 'res_buffs', [-0.1, 99, 'overflow'])
                summon(new_ally_status, minion_status)
            
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
            add_buff(new_ally_status, 'pride of sincerity', [1, 4], turn_num)
            for _skill in new_skill_list:
                if _skill['id'] == 5 and _skill['cd'] == 0 and kill_mob:
                    _skill['cd'] = _skill['ct']
                    act_again = True
        activate_after_action_effects(new_ally_status, target_status, new_skill_list, skill, turn_num, kill_enemy=kill_mob)
        
        if kill_mob:
            new_enemies_status['mobs'].pop()
            
        dmg_enemy_turn = 0
        minions_dmg = 0
        # Last sub-turn
        if not act_again:
            if "minions" in new_ally_status:
                for minion_status in new_ally_status["minions"]:
                    minion_skill = None
                    if minion_status["name"].startswith("mysterious"):
                        if (turn_num - minion_status["summon_turn"]) % 2 == 0:
                            minion_skill = {'type': 'active', 'ct': 1, 'dmg_modifier': 1.4}
                            add_buff(minion_status, 'crit_rate_buffs', [0.2, -1, 'Main/A'], turn_num)
                    else:
                        if (turn_num - minion_status["summon_turn"]) % 2 == 0:
                            minion_skill = {'type': 'active', 'ct': 1, 'dmg_modifier': 1.4}
                            add_buff(minion_status, 'crit_rate_buffs', [0.2, -1, 'Main/A'], turn_num)
                        elif (turn_num - minion_status["summon_turn"]) == 1:
                            minion_skill = {'type': 'active', 'ct': 3, 'dmg_modifier': 1.3}
                            add_buff(target_status, 'dmg_res_buffs', [-0.1, -1, 'Main/A'], turn_num)
                    minion_dmg = calc_damage(minion_status, target_status, {'type': 'attack'}, minion_skill, use_base_stat=True)[dmg_type]
                    minions_dmg += minion_dmg
                action_list[-1][2] += minions_dmg
                dmg += minions_dmg
                    
            #dmg_enemy_turn = calc_damage(new_ally_status, new_enemies_status['boss'], {'type': 'magic', on_enemy_turn=True}, None)[dmg_type]
            for mob in new_enemies_status['mobs']:
                dmg_enemy_turn += calc_damage(new_ally_status, mob, {'type': 'attack'}, None, dmg_penalty=True, on_enemy_turn=True)[dmg_type]
            new_enemies_status['mobs'][:] = []
        action_list[-1].append(dmg_enemy_turn)
        action_list[-1].append(minions_dmg)
        
        new_sub_turn = 0 if not act_again else sub_turn + 1
        new_ally_status = update_duration(new_ally_status, turn_num)
        total_dmg = max(total_dmg, dmg + recur_toshizou(turn_num + int(not act_again), new_ally_status, new_enemies_status, new_skill_list, action_list, dmg_type, new_sub_turn))
        
        action_list.pop()
    return total_dmg
    
toshizou_stats = {
                    'class': 'assassin',
                    'master_class_lv': 3,
                    'atk': 545,
                    'tec': 455,
                }
toshizou_status = add_teamwise_buffs(['symbol skill'], toshizou_stats)
toshizou_skills = [
                    {'id': 0, 'type': 'passive'},
                    {'id': 1, 'type': 'active', 'ct': 5},
                    {'id': 2, 'type': 'passive'},
                    {'id': 3, 'type': 'passive'},
                    {'id': 4, 'type': 'passive'},
                    {'id': 5, 'type': 'passive', 'ct': 3},
                 ]
toshizou_skill_sets = get_all_skill_sets(toshizou_skills, must_include_skill_ids=[3])

toshizou_status = load_equipments(['john dillinger', "leo's heavenly armor", 'tracking headband', 'ring of life'], toshizou_status)
toshizou_status = load_enchantments(['strike'], toshizou_status)
toshizou_status = load_enchantment_random_stats('max_atk_percent', toshizou_status)
toshizou_status = link_support('nuwa_yukata', toshizou_status)
toshizou_dmg = 0
for skill_set in toshizou_skill_sets:
    toshizou_dmg = max(toshizou_dmg,
        recur_toshizou(
            1,
            toshizou_status,
            {
                'boss': {
                    'dmg_res_buffs': [-0.35],
                },
                'mobs': [],
            },
            skill_set,
            [],
            DAMAGE_MODE))
print "Total damage (player phase): %f" % toshizou_dmg
log_skill_set(best_skill_set)
log_action_list(best_action_list)