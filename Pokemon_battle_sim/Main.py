import neural_network
from Battle_Sim import battle
from pokemon import Pokemon, Move
Earthquake = Move("Earthquake", "Ground", 100)
Flamethrower = Move("Flamethrower", "Fire", 90)
Air_slash = Move("Air Slash", "Flying", 75)
Flare_Blitz = Move("Flare Blitz", "Fire", 120)
Thunderbolt = Move("Thunderbolt", "Electric", 90)
Surf = Move("Surf", "Water", 90)
Volt_tackle = Move("Volt Tackle", "Electric", 120)
Giga_Drain = Move("Giga Drain", "Grass", 75)
Sludge_Bomb = Move("Sludge Bomb", "Poison", 90)
Solar_Beam = Move("Solar Beam", "Grass", 100)
Ice_Beam = Move("Ice Beam", "Ice", 90)
Dragon_Pulse = Move("Dragon Pulse", "Dragon", 90)
Play_Rough = Move("Play Rough", "Fairy", 85)


Charizard = Pokemon("Charizard", ["Fire","Flying"], 78, 109, 85, 100, [Earthquake, Flamethrower, Air_slash, Flare_Blitz])
Blastoise = Pokemon("Blastoise", ["Water"], 79, 85, 105, 78, [Earthquake,Surf, Ice_Beam, Dragon_Pulse])
Pikachu = Pokemon("Pikachu", ["Electric"], 70, 100, 55, 90, [Volt_tackle, Surf, Thunderbolt, Play_Rough])
Venusaur = Pokemon("Venusaur", ["Grass", "Poison"], 80, 100, 100, 80, [Sludge_Bomb, Solar_Beam, Giga_Drain, Earthquake])
team1 = [Charizard, Venusaur]
team2 = [Blastoise, Pikachu]
nn1 = neural_network.simpleNN(6, 8, 4)
nn2 = neural_network.simpleNN(6, 8, 4)

for i in range(1000):
    nn1 = neural_network.simpleNN(6, 8, 5)
    nn2 = neural_network.simpleNN(6, 8, 5)
    for p in team1 + team2:
        p.reset()

    winner, s1, a1, r1, s2, a2, r2 = battle(team1, team2, nn1, nn2)

    for state, action, reward in zip(s1, a1, r1):
        nn1.train_step(state, action, reward)

    for state, action, reward in zip(s2, a2, r2):
        nn2.train_step(state, action, reward)

    print("Battle", i, "Winner:", winner)