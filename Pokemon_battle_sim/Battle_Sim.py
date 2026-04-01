import numpy as np
from pokemon import type_chart, type_advantage

def get_state(attacker, defender):
    state = []

    state.append(attacker.current_hp / attacker.hp)
    state.append(defender.current_hp / defender.hp)

    for move in attacker.moves:
        multiplier = 1
        for t in defender.types:
            if move.type in type_chart and t in type_chart[move.type]:
                multiplier *= type_chart[move.type][t]
        state.append(multiplier)

    state.append(type_advantage(attacker, defender))

    return state


def battle(team1, team2, nn1, nn2):

    active1 = 0
    active2 = 0

    states1, actions1, rewards1 = [], [], []
    states2, actions2, rewards2 = [], [], []

    while True:

        p1 = team1[active1]
        p2 = team2[active2]

        # auto switch if fainted
        if p1.current_hp <= 0:
            active1 = 1 - active1
            continue
        if p2.current_hp <= 0:
            active2 = 1 - active2
            continue

        # -------- PLAYER 1 --------
        state1 = np.array(get_state(p1, p2))
        out1 = nn1.forward(state1)

        action1 = np.random.randint(5) if np.random.rand() < 0.2 else np.argmax(out1)

        states1.append(state1)
        actions1.append(action1)

        reward1 = 0

        if action1 < 4:
            move = p1.moves[action1]
            dmg = p1.attack_target(p2, move)

            # FIX: handle "missed"
            if dmg == 'missed':
                dmg = 0
                reward1 -= 0.3

            if dmg == 0:
                reward1 -= 0.5
            else:
                reward1 += dmg / p2.hp

            # type awareness bonus
            mult = 1
            for t in p2.types:
                if move.type in type_chart and t in type_chart[move.type]:
                    mult *= type_chart[move.type][t]

            reward1 += (mult - 1) * 0.3

        else:
            active1 = 1 - active1
            new_p1 = team1[active1]
            reward1 += type_advantage(new_p1, p2) - 1

        # -------- PLAYER 2 --------
        state2 = np.array(get_state(p2, p1))
        out2 = nn2.forward(state2)

        action2 = np.random.randint(5) if np.random.rand() < 0.2 else np.argmax(out2)

        states2.append(state2)
        actions2.append(action2)

        reward2 = 0

        if action2 < 4:
            move = p2.moves[action2]
            dmg = p2.attack_target(p1, move)

            # FIX: handle "missed"
            if dmg == 'missed':
                dmg = 0
                reward2 -= 0.3

            if dmg == 0:
                reward2 -= 0.5
            else:
                reward2 += dmg / p1.hp

            mult = 1
            for t in p1.types:
                if move.type in type_chart and t in type_chart[move.type]:
                    mult *= type_chart[move.type][t]

            reward2 += (mult - 1) * 0.3

        else:
            active2 = 1 - active2
            new_p2 = team2[active2]
            reward2 += type_advantage(new_p2, p1) - 1

        rewards1.append(reward1)
        rewards2.append(reward2)

        # win check
        if all(p.current_hp <= 0 for p in team1):
            return 2, states1, actions1, rewards1, states2, actions2, rewards2

        if all(p.current_hp <= 0 for p in team2):
            return 1, states1, actions1, rewards1, states2, actions2, rewards2
