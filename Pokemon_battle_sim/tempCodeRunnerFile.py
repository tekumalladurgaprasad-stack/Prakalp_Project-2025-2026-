import tkinter as tk
import numpy as np
import neural_network
from pokemon import Pokemon, Move, type_chart
from Battle_Sim import get_state
import copy

# ---------------- MOVES ----------------
Earthquake = Move("Earthquake", "Ground", 100, 100)
Flamethrower = Move("Flamethrower", "Fire", 90, 100)
Air_slash = Move("Air Slash", "Flying", 75, 95)
Flare_Blitz = Move("Flare Blitz", "Fire", 120, 100)

Surf = Move("Surf", "Water", 90, 100)
Ice_Beam = Move("Ice Beam", "Ice", 90, 100)
Dragon_Pulse = Move("Dragon Pulse", "Dragon", 90, 100)

Thunderbolt = Move("Thunderbolt", "Electric", 90, 100)
Volt_tackle = Move("Volt Tackle", "Electric", 120, 100)
Play_Rough = Move("Play Rough", "Fairy", 90, 90)

Sludge_Bomb = Move("Sludge Bomb", "Poison", 90, 100)
Solar_Beam = Move("Solar Beam", "Grass", 120, 100)
Giga_Drain = Move("Giga Drain", "Grass", 75, 100)

Double_Edge = Move("Double Edge", "Normal", 120, 100)
Ice_Punch = Move("Ice Punch", "Ice", 75, 100)
Crunch = Move("Crunch", "Dark", 80, 100)

Iron_Head = Move("Iron Head", "Steel", 80, 100)
X_Scissor = Move("X-Scissor", "Bug", 80, 100)
Close_Combat = Move("Close Combat", "Fighting", 120, 100)

# ---------------- POKEMON ----------------
Charizard = Pokemon("Charizard", ["Fire","Flying"], 78, 109, 85, 100,
                    [Earthquake, Flamethrower, Air_slash, Flare_Blitz])

Blastoise = Pokemon("Blastoise", ["Water"], 79, 85, 105, 78,
                    [Earthquake, Surf, Ice_Beam, Dragon_Pulse])

Pikachu = Pokemon("Pikachu", ["Electric"], 70, 100, 55, 90,
                  [Volt_tackle, Thunderbolt, Surf, Play_Rough])

Venusaur = Pokemon("Venusaur", ["Grass","Poison"], 80, 100, 100, 80,
                   [Sludge_Bomb, Solar_Beam, Giga_Drain, Earthquake])

Snorlax = Pokemon("Snorlax",["Normal"],160,110,110,30,
                  [Earthquake, Double_Edge, Crunch, Ice_Punch])

Scizor = Pokemon("Scizor", ["Bug", "Steel"],70,130,100,65,
                 [Iron_Head, X_Scissor, Close_Combat, Ice_Punch])

all_pokemon = [Charizard, Blastoise, Pikachu, Venusaur, Snorlax, Scizor]

# ---------------- LOAD MODEL ----------------
nn = neural_network.simpleNN(7, 8, 5)
nn.W1 = np.load("W1.npy")
nn.W2 = np.load("W2.npy")

# ---------------- UI ----------------
root = tk.Tk()
root.title("Pokemon AI Battle")
root.configure(bg="#cc0000")

top_frame = tk.Frame(root, bg="#cc0000")
top_frame.pack(fill="both", expand=True)

divider = tk.Frame(root, height=5, bg="black")
divider.pack(fill="x")

bottom_frame = tk.Frame(root, bg="white")
bottom_frame.pack(fill="both", expand=True)

log = tk.Text(top_frame, height=15, width=60,
              bg="#330000", fg="white",
              font=("Consolas", 10))
log.pack(pady=10)

frame = tk.Frame(bottom_frame, bg="white")
frame.pack(pady=10)

def write(msg):
    log.insert(tk.END, msg + "\n")
    log.see(tk.END)

def clear_buttons():
    for w in frame.winfo_children():
        w.destroy()

# ---------------- AI (NO SWITCH) ----------------
def get_ai_choice(attacker, defender):
    state = np.array(get_state(attacker, defender))
    out = nn.forward(state)

    scores = out.copy()

    for i, move in enumerate(attacker.moves):
        mult = 1
        for t in defender.types:
            if move.type in type_chart and t in type_chart[move.type]:
                mult *= type_chart[move.type][t]


        if mult == 0:
            scores[i] = -9999


        scores[i] += (mult - 1) * 2


    return np.argmax(scores[:4])

# ---------------- GAME ----------------
def player_vs_ai():

    log.delete(1.0, tk.END)
    clear_buttons()

    selected = []

    write("Select 2 Pokémon:")

    def select_pokemon(p):
        if p not in selected:
            selected.append(p)
            write(f"Selected: {p.name}")

        if len(selected) == 2:
            start_game()

    for p in all_pokemon:
        tk.Button(frame, text=p.name, width=15,
                  bg="#ff6666", fg="white",
                  font=("Arial", 10, "bold"),
                  command=lambda x=p: select_pokemon(x)).pack(pady=3)

    def start_game():
        clear_buttons()

        team_player = [copy.deepcopy(p) for p in selected]
        team_ai = [copy.deepcopy(p) for p in np.random.choice(all_pokemon, 2, replace=False)]

        for p in team_player + team_ai:
            p.reset()

        write("\nAI Team:")
        for p in team_ai:
            write(p.name)

        active_player = 0
        active_ai = 0

        def game_loop():
            nonlocal active_player, active_ai

            p1 = team_player[active_player]
            p2 = team_ai[active_ai]

            if p1.current_hp <= 0:
                if all(p.current_hp <= 0 for p in team_player):
                    write("\nYou lost!")
                    return
                active_player = 1 - active_player
                write(f"Switched to {team_player[active_player].name}")
                root.after(500, game_loop)
                return

            if p2.current_hp <= 0:
                if all(p.current_hp <= 0 for p in team_ai):
                    write("\nYou win!")
                    return
                active_ai = 1 - active_ai
                write(f"AI switched!")
                root.after(500, game_loop)
                return

            write(f"\n{p1.name} ({p1.current_hp:.1f}) vs {p2.name} ({p2.current_hp:.1f})")

            if p1.speed >= p2.speed:
                player_turn()
            else:
                ai_first()

        def ai_first():
            p = team_ai[active_ai]
            e = team_player[active_player]

            ai_choice = get_ai_choice(p, e)

            move = p.moves[ai_choice]
            dmg = p.attack_target(e, move)

            write(f"AI used {move.name}")
            write(f"AI did {round(dmg,1)} damage!")

            root.after(500, player_turn)

        def player_turn():
            clear_buttons()

            p = team_player[active_player]
            write(f"\nYour turn ({p.name})")

            for i, move in enumerate(p.moves):
                tk.Button(frame, text=move.name, width=20,
                          bg="#ff4d4d", fg="white",
                          font=("Arial", 10, "bold"),
                          command=lambda x=i: choose_move(x)).pack(pady=3)

            tk.Button(frame, text="Switch", width=20,
                      bg="#333333", fg="white",
                      font=("Arial", 10, "bold"),
                      command=lambda: choose_move(4)).pack(pady=5)

        def choose_move(choice):
            nonlocal active_player, active_ai

            clear_buttons()

            p = team_player[active_player]
            e = team_ai[active_ai]

            player_choice = choice
            ai_choice = get_ai_choice(e, p)

            player_first = p.speed >= e.speed

            def do_player():
                nonlocal active_player
                if player_choice == 4:
                    active_player = 1 - active_player
                    write(f"You switched to {team_player[active_player].name}")
                else:
                    move = p.moves[player_choice]
                    dmg = p.attack_target(team_ai[active_ai], move)

                    write(f"You used {move.name}")
                    if dmg == 'missed':
                        write(f"{move.name} missed!")
                    else:
                        write(f"You did {round(dmg,1)} damage!")

            def do_ai():
                ai_p = team_ai[active_ai]
                target = team_player[active_player]

                move = ai_p.moves[ai_choice]
                dmg = ai_p.attack_target(target, move)
                write(f"AI used {move.name}")
                if dmg == 'missed':
                    write(f"{move.name} missed!")
                else:
                    write(f"AI did {round(dmg,1)} damage!")

            if player_first:
                do_player()
                if team_ai[active_ai].current_hp > 0:
                    do_ai()
            else:
                do_ai()
                if team_player[active_player].current_hp > 0:
                    do_player()

            root.after(500, game_loop)

        game_loop()

tk.Button(root, text="Start Battle",
          bg="#ff1a1a", fg="white",
          font=("Arial", 12, "bold"),
          command=player_vs_ai).pack(pady=10)

root.mainloop()
