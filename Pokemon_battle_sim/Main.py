import neural_network
from Battle_Sim import battle
from pokemon import Pokemon, Move
import numpy as np
import itertools
import random

# ---------------- MOVES ----------------
Earthquake = Move("Earthquake", "Ground", 100)
Flamethrower = Move("Flamethrower", "Fire", 90)
Air_slash = Move("Air Slash", "Flying", 75)
Flare_Blitz = Move("Flare Blitz", "Fire", 120)

Surf = Move("Surf", "Water", 90)
Ice_Beam = Move("Ice Beam", "Ice", 90)
Dragon_Pulse = Move("Dragon Pulse", "Dragon", 90)

Thunderbolt = Move("Thunderbolt", "Electric", 90)
Volt_tackle = Move("Volt Tackle", "Electric", 120)
Play_Rough = Move("Play Rough", "Fairy", 85)

Sludge_Bomb = Move("Sludge Bomb", "Poison", 90)
Solar_Beam = Move("Solar Beam", "Grass", 100)
Giga_Drain = Move("Giga Drain", "Grass", 75)

# ---------------- POKEMON ----------------
Charizard = Pokemon("Charizard", ["Fire","Flying"], 78, 109, 85, 100,
                    [Earthquake, Flamethrower, Air_slash, Flare_Blitz])

Blastoise = Pokemon("Blastoise", ["Water"], 79, 85, 105, 78,
                    [Earthquake, Surf, Ice_Beam, Dragon_Pulse])

Pikachu = Pokemon("Pikachu", ["Electric"], 70, 100, 55, 90,
                  [Volt_tackle, Thunderbolt, Surf, Play_Rough])

Venusaur = Pokemon("Venusaur", ["Grass","Poison"], 80, 100, 100, 80,
                   [Sludge_Bomb, Solar_Beam, Giga_Drain, Earthquake])

all_pokemon = [Charizard, Blastoise, Pikachu, Venusaur]

# ---------------- TEAM GENERATION ----------------
teams = list(itertools.combinations(all_pokemon, 2))

# ---------------- NN ----------------
nn1 = neural_network.simpleNN(7, 8, 5)
nn2 = neural_network.simpleNN(7, 8, 5)

# ---------------- TRAINING ----------------
for epoch in range(1000):

    random.shuffle(teams)  # makes training better

    for t1 in teams:
        for t2 in teams:

            if t1 == t2:
                continue

            team1 = list(t1)
            team2 = list(t2)

            # reset HP
            for p in team1 + team2:
                p.reset()

            # battle
            winner, s1, a1, r1, s2, a2, r2 = battle(team1, team2, nn1, nn2)

            # train NN1
            for s, a, r in zip(s1, a1, r1):
                nn1.train_step(s, a, r)

            # train NN2
            for s, a, r in zip(s2, a2, r2):
                nn2.train_step(s, a, r)

    if epoch % 50 == 0:
        print(f"Epoch {epoch} done")

# ---------------- SAVE MODEL ----------------
np.save("W1.npy",nn1.W1)
np.save("W2.npy", nn2.W2)
print("Model saved!")