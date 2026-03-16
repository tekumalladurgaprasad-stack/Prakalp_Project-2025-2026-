import random
type_chart = {
    "Normal": {"Ghost" : 0, "Rock" : 0.5, "Steel" : 0.5},
    "Bug": {"Fire" : 0.5, "Steel" : 0.5, "Fairy" : 0.5, "Fighting" : 0.5, "Poison" : 0.5, "Flying" : 0.5, "Ghost" : 0.5, "Dark" : 2, "Psychic" : 2, "Grass" : 2},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Rock": 0.5, "Dragon": 0.5, "Bug": 2, "Steel": 2, "Ice": 2, "Grass": 2},
    "Water": {"Water": 0.5, "Grass": 0.5, "Dragon": 0.5, "Fire": 2, "Rock": 2, "Ground": 2},
    "Grass": {"Grass": 0.5, "Fire": 0.5, "Bug": 0.5, "Flying": 0.5, "Poison": 0.5, "Dragon": 0.5, "Water": 2, "Rock": 2, "Ground": 2},
    "Steel": {"Steel": 0.5, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Rock": 2, "Ice": 2, "Fairy": 2},
    "Fighting": {"Ghost": 0, "Bug": 0.5, "Flying": 0.5, "Poison": 0.5, "Psychic": 0.5, "Fairy": 0.5, "Steel": 2, "Rock": 2, "Ice": 2, "Dark": 2, "Normal": 2},
    "Electric": {"Ground": 0, "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5, "Water": 2, "Flying": 2},
    "Poison": {"Steel": 0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Grass": 2, "Fairy": 2},
    "Ground": {"Flying": 0, "Grass": 0.5, "Bug": 0.5, "Fire": 2, "Steel": 2, "Rock": 2, "Poison": 2, "Electric": 2},
    "Ice": {"Ice": 0.5, "Water": 0.5, "Steel": 0.5, "Fire": 0.5, "Flying": 2, "Grass": 2, "Ground": 2, "Dragon": 2},
    "Flying": {"Rock": 0.5, "Steel": 0.5, "Electric": 0.5, "Bug": 2, "Grass": 2, "Fighting": 2},
    "Psychic": {"Dark": 0, "Psychic": 0.5, "Steel": 0.5, "Fighting": 2, "Poison": 2},
    "Rock": {"Ground": 0.5, "Fighting": 0.5, "Steel": 0.5, "Flying": 2, "Fire": 2, "Ice": 2, "Bug": 2},
    "Ghost": {"Normal": 0, "Dark": 0.5, "Psychic": 2, "Ghost": 2},
    "Dragon": {"Fairy": 0, "Steel": 0.5, "Dragon": 2},
    "Dark": {"Dark": 0.5, "Fighting": 0.5, "Fairy": 0.5, "Ghost": 2, "Psychic": 2},
    "Fairy": {"Steel": 0.5, "Fire": 0.5, "Poison": 0.5, "Dark": 2, "Fighting": 2, "Dragon": 2}
}
def calc_hp(base_hp):
    return 2 * base_hp + 204
def calc_stat(base_stat):
    return 2 * base_stat + 99
def battle(p1,p2):
        turn = 0

        while p1.current_hp > 0 and p2.current_hp > 0:
            if p1.speed > p2.speed:
                move = random.choice(p1.moves)
                p1.attack_target(p2, move)

                if p2.current_hp > 0:
                    move = random.choice(p2.moves)
                    p2.attack_target(p1,move)

            else:
                move = random.choice(p2.moves)
                p2.attack_target(p1, move)

                if p1.current_hp > 0:
                    move = random.choice(p1.moves) 
                    p1.attack_target(p2,move)
            turn += 1
        if p1.current_hp <= 0:
            return p2.name
        else:
            return p1.name
def get_state(attacker,defender):
    state = []

    state.append(attacker.current_hp / attacker.hp)
    state.append(defender.current_hp / defender.hp)    

    for move in attacker.moves:
        multiplier = 1
        for t in defender.types:
            if move.type in type_chart and t in type_chart[move.type]:
                multiplier *= type_chart[move.type][t]
        state.append(multiplier)
        
    return state
class Pokemon:

    def __init__(self, name, types, hp, attack, defence, speed, moves):
        self.name = name
        self.types = types
        self.hp = calc_hp(hp)
        self.attack = calc_stat(attack)
        self.defence = calc_stat(defence)
        self.speed = calc_stat(speed)
        self.current_hp = self.hp
        self.moves = moves

    def attack_target(self, defender, move):

        multiplier = 1
        
        for t in defender.types:
            if move.type in type_chart:
                if t in type_chart[move.type]:
                    multiplier *= type_chart[move.type][t]
        multiplier *= 1.5 if move.type in self.types else 1
        damage = int((self.attack/ defender.defence) * move.bp   * multiplier * random.uniform(0.85, 1))
        defender.current_hp -= damage
    

        print(f"{self.name} used {move.name} and dealt {damage} damage!")

    def reset(self):
        self.current_hp = self.hp
    

class Move:
    def __init__(self, name, type, bp):
        self.name = name
        self.type = type
        self.bp = bp
