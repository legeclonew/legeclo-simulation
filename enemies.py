from simulate_battle import update_duration_enemy, add_buff

class EnemyGenerator(object):
    def __init__(self):
        self.num_new_mobs_per_turn = 0
        self.default_def = 100
        self.default_res = 100
        self.is_silenced = False

    def update_enemies(self, enemies_status, turn_num, sub_turn):
        new_enemies_status = {}
        new_enemies_status['boss'] = update_duration_enemy(enemies_status['boss'], sub_turn)
        
        new_enemies_status['mobs'] = []
        for mob in enemies_status['mobs']:
            new_enemies_status['mobs'].append(mob)
            
        return new_enemies_status
        
class BossGenerator(EnemyGenerator):
    def update_enemies(self, enemies_status, turn_num, sub_turn):
        new_enemies_status = super(BossGenerator, self).update_enemies(enemies_status, turn_num, sub_turn)
        new_enemies_status['boss']['def'] = self.default_def
        new_enemies_status['boss']['res'] = self.default_res
        
        return new_enemies_status
        
class NormalEnemyGenerator(EnemyGenerator):
    def update_enemies(self, enemies_status, turn_num, sub_turn):
        new_enemies_status = super(NormalEnemyGenerator, self).update_enemies(enemies_status, turn_num, sub_turn)
        new_enemies_status['boss']['def'] = self.default_def
        new_enemies_status['boss']['res'] = self.default_res
        if sub_turn == 0:
            for _ in range(self.num_new_mobs_per_turn):
                new_enemies_status['mobs'].append({
                    'def': self.default_def,
                    'res': self.default_res,
                })
        
        return new_enemies_status
        
class Gex1EnemyGenerator(EnemyGenerator):
    def update_enemies(self, enemies_status, turn_num, sub_turn):
        new_enemies_status = super(Gex1EnemyGenerator, self).update_enemies(enemies_status, turn_num, sub_turn)
        new_enemies_status['boss']['def'] = 100
        new_enemies_status['boss']['res'] = 100
        add_buff(new_enemies_status['boss'], 'def_buffs', [turn_num - 1, 99, 'Boss/T'])
        add_buff(new_enemies_status['boss'], 'res_buffs', [turn_num - 1, 99, 'Boss/T'])
        if turn_num >= 2 and sub_turn == 0:
            for _ in range(self.num_new_mobs_per_turn):
                new_enemies_status['mobs'].append({
                    'def': 100 * turn_num,
                    'res': 100 * turn_num,
                })
        
        return new_enemies_status
    
class Gex3EnemyGenerator(EnemyGenerator):
    def update_enemies(self, enemies_status, turn_num, sub_turn):
        new_enemies_status = super(Gex3EnemyGenerator, self).update_enemies(enemies_status, turn_num, sub_turn)
        new_enemies_status['boss']['def'] = 100
        new_enemies_status['boss']['res'] = 100
        if not self.is_silenced:
            add_buff(new_enemies_status['boss'], 'def_buffs', [0.2, 1, 'Main/A'], turn_num)
            add_buff(new_enemies_status['boss'], 'res_buffs', [0.2, 1, 'Main/A'], turn_num)
        if turn_num >= 2 and sub_turn == 0:
            for _ in range(self.num_new_mobs_per_turn):
                new_enemies_status['mobs'].append({
                    'def': 60 * turn_num,
                    'res': 60 * turn_num,
                })
        
        return new_enemies_status

def get_generator(battle_name):
    if battle_name == 'boss':
        return BossGenerator()
    elif battle_name == 'normal':
        return NormalEnemyGenerator()
    elif battle_name == 'gex1':
        return Gex1EnemyGenerator()
    elif battle_name == 'gex3':
        return Gex3EnemyGenerator()