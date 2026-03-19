import neural_network
import numpy as np
from pokemon import Pokemon, type_chart, Move
def type_advantage(attacker, defender):
        multiplier = 1
        for t in defender.types:
            if attacker.types[0] in type_chart and t in type_chart[attacker.types[0]]:
                multiplier *= type_chart[attacker.types[0]][t]
        return multiplier
def battle(team1, team2, nn1, nn2):
    active1 = 0
    active2 = 0

    states1, actions1, rewards1 = [], [], []
    states2, actions2, rewards2 = [], [], []

    while True:
        p1 = team1[active1]
        p2 = team2[active2]

        if p1.current_hp <= 0:
            active1 = 1 - active1
            continue
        if p2.current_hp <= 0:
            active2 = 1 - active2
            continue

        
        state1 = np.array(get_state(p1, p2))
        outputs1 = nn1.forward(state1)

        if np.random.rand() < 0.3:
            action1 = np.random.randint(5)
        else:
            action1 = np.argmax(outputs1)

        states1.append(state1)
        actions1.append(action1)

        
        state2 = np.array(get_state(p2, p1))
        outputs2 = nn2.forward(state2)

        if np.random.rand() < 0.3:
            action2 = np.random.randint(5)
        else:
            action2 = np.argmax(outputs2)

        states2.append(state2)
        actions2.append(action2)

        
        reward1 = 0
        reward2 = 0

        
        if action1 < 4:
            dmg = p1.attack_target(p2, p1.moves[action1])
            reward1 += dmg / 50
        else:
            active1 = 1 - active1
            new_p1 = team1[active1]
            adv = type_advantage(new_p1, p2)
            reward1 += adv - 1   

        
        if action2 < 4:
            dmg = p2.attack_target(p1, p2.moves[action2])
            reward2 += dmg / 50
        else:
            active2 = 1 - active2
            new_p2 = team2[active2]
            adv = type_advantage(new_p2, p1)
            reward2 += adv - 1

        rewards1.append(reward1)
        rewards2.append(reward2)

        
        if all(p.current_hp <= 0 for p in team1):
            return 2, states1, actions1, rewards1, states2, actions2, rewards2

        if all(p.current_hp <= 0 for p in team2):
            return 1, states1, actions1, rewards1, states2, actions2, rewards2
def get_state(attacker,defender):
    state = []

    state.append(attacker.current_hp / attacker.hp)
    state.append(defender.current_hp / defender.hp)    

    for move in attacker.moves:
        multiplier = 1
        for t in defender.types:
            if move.type in type_chart and t in type_chart[move.type]:
                multiplier *= type_chart[move.type][t]
        stab = 1.5 if move.type in attacker.types else 1
        state.append(multiplier * stab)
        
    return state

