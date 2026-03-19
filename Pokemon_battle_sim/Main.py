import neural_network
from Battle_Sim import battle
from pokemon import Pokemon, Move

# create moves
tackle = Move("Tackle", "Normal", 40)
ember = Move("Ember", "Fire", 40)
water_gun = Move("Water Gun", "Water", 40)
vine_whip = Move("Vine Whip", "Grass", 40)

# create pokemon
p1 = Pokemon("Charmander", ["Fire"], 39, 52, 43, 65, [tackle, ember, tackle, tackle])
p2 = Pokemon("Squirtle", ["Water"], 44, 48, 65, 43, [tackle, water_gun, tackle, tackle])

# create neural networks
nn1 = neural_network.simpleNN(6, 8, 4)
nn2 = neural_network.simpleNN(6, 8, 4)

# 🔁 TRAINING LOOP
for i in range(1000):
    p1.reset()
    p2.reset()

    winner, s1, a1, r1, s2, a2, r2 = battle(p1, p2, nn1, nn2)

    for state, action, reward in zip(s1, a1, r1):
        nn1.train_step(state, action, reward)

    for state, action, reward in zip(s2, a2, r2):
        nn2.train_step(state, action, reward)

    print(f"Battle {i} winner: Player {winner}")