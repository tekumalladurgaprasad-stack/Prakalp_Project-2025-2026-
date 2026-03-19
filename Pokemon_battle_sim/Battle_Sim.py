import neural_network
import numpy as np
from pokemon import Pokemon, type_chart, Move
def battle(p1,p2, nn1, nn2):
        turn = 0
        states1 = []
        actions1 = []
        states2 = []
        actions2 = []
        rewards1 = []
        rewards2 = []
        while p1.current_hp > 0 and p2.current_hp > 0:
            if p1.speed > p2.speed:
                state = np.array(get_state(p1,p2))
                outputs = nn1.forward(state)
                if np.random.rand() < 0.3:  
                    move_index = np.random.randint(len(p1.moves))
                else:
                    move_index = np.argmax(outputs)
                states1.append(state)
                actions1.append(move_index)
                move = p1.moves[move_index]
                reward = p1.attack_target(p2, move)
                rewards1.append(reward/50-0.2)

                if p2.current_hp > 0:
                    state = np.array(get_state(p2,p1))
                    outputs = nn2.forward(state)
                    if np.random.rand() < 0.3:  
                        move_index = np.random.randint(len(p2.moves))
                    else:
                        move_index = np.argmax(outputs)
                    states2.append(state)
                    actions2.append(move_index)
                    move = p2.moves[move_index]
                    reward = p2.attack_target(p1,move)
                    rewards2.append(reward/50 - 0.2)
            else:
                state = np.array(get_state(p2,p1))
                outputs = nn2.forward(state)
                if np.random.rand() < 0.3:  # 10% random
                    move_index = np.random.randint(len(p2.moves))
                else:
                    move_index = np.argmax(outputs)
                states2.append(state)
                actions2.append(move_index)
                move = p2.moves[move_index]
                reward = p2.attack_target(p1,move)
                rewards2.append(reward/50-0.2)

                if p1.current_hp > 0:
                    state = np.array(get_state(p1,p2))
                    outputs = nn1.forward(state)
                    if np.random.rand() < 0.3:  
                        move_index = np.random.randint(len(p1.moves))
                    else:
                        move_index = np.argmax(outputs)
                    states1.append(state)
                    actions1.append(move_index)
                    move = p1.moves[move_index] 
                    reward = p1.attack_target(p2,move)
                    rewards1.append(reward/50-0.2)
            turn += 1
        if p1.current_hp <= 0:
            winner = 2        
        else:
            winner = 1
        return winner, states1, actions1, rewards1, states2, actions2, rewards2
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

