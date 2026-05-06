import tkinter as tk
from tkinter import font as tkfont
import numpy as np
from pokemon import Pokemon, Move
from Battle_Sim import get_state
import copy
from PIL import Image, ImageTk
import os
import random

# ─────────────────────────────────────────────
#  BASE DIR — find sprites relative to this file
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
#  MOVES
# ─────────────────────────────────────────────
Earthquake   = Move("Earthquake",   "Ground",  100, 100)
Flamethrower = Move("Flamethrower", "Fire",     90, 100)
Air_slash    = Move("Air Slash",    "Flying",   75,  95)
Flare_Blitz  = Move("Flare Blitz",  "Fire",    120, 100)
Surf         = Move("Surf",         "Water",    90, 100)
Ice_Beam     = Move("Ice Beam",     "Ice",      90, 100)
Dragon_Pulse = Move("Dragon Pulse", "Dragon",   90, 100)
Thunderbolt  = Move("Thunderbolt",  "Electric", 90, 100)
Volt_tackle  = Move("Volt Tackle",  "Electric",120, 100)
Play_Rough   = Move("Play Rough",   "Fairy",    90,  90)
Sludge_Bomb  = Move("Sludge Bomb",  "Poison",   90, 100)
Solar_Beam   = Move("Solar Beam",   "Grass",   120, 100)
Giga_Drain   = Move("Giga Drain",   "Grass",    75, 100)
Double_Edge  = Move("Double Edge",  "Normal",  120, 100)
Ice_Punch    = Move("Ice Punch",    "Ice",      75, 100)
Crunch       = Move("Crunch",       "Dark",     80, 100)
Iron_Head    = Move("Iron Head",    "Steel",    80, 100)
X_Scissor    = Move("X-Scissor",   "Bug",       80, 100)
Close_Combat = Move("Close Combat", "Fighting", 120, 100)

# ─────────────────────────────────────────────
#  POKÉMON
# ─────────────────────────────────────────────
Charizard = Pokemon("Charizard", ["Fire","Flying"], 78,109, 85,100,
                    [Earthquake, Flamethrower, Air_slash, Flare_Blitz])
Blastoise = Pokemon("Blastoise", ["Water"],         79, 85,105, 78,
                    [Earthquake, Surf, Ice_Beam, Dragon_Pulse])
Pikachu   = Pokemon("Pikachu",   ["Electric"],      70,100, 55, 90,
                    [Volt_tackle, Thunderbolt, Surf, Play_Rough])
Venusaur  = Pokemon("Venusaur",  ["Grass","Poison"],80,100,100, 80,
                    [Sludge_Bomb, Solar_Beam, Giga_Drain, Earthquake])
Snorlax   = Pokemon("Snorlax",   ["Normal"],       160,110,110, 30,
                    [Earthquake, Double_Edge, Crunch, Ice_Punch])
Scizor    = Pokemon("Scizor",    ["Bug","Steel"],   70,130,100, 65,
                    [Iron_Head, X_Scissor, Close_Combat, Ice_Punch])

all_pokemon = [Charizard, Blastoise, Pikachu, Venusaur, Snorlax, Scizor]

# ─────────────────────────────────────────────
#  TYPE CHART (for colouring move buttons)
# ─────────────────────────────────────────────
from pokemon import type_chart as TYPE_CHART

# ─────────────────────────────────────────────
#  NEURAL NETWORK  — loads weights saved by Main.py
#  Looks in BASE_DIR first, then one level up, so it works
#  whether App.py lives alongside the .npy files or in a subfolder.
# ─────────────────────────────────────────────
import neural_network

def _find_npy(filename):
    """Search BASE_DIR then parent dir for a .npy file."""
    for folder in [BASE_DIR, os.path.dirname(BASE_DIR)]:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"Could not find '{filename}' in '{BASE_DIR}' or its parent folder."
    )

nn = neural_network.simpleNN(7, 8, 5)
nn.W1 = np.load(_find_npy("W1.npy"))
nn.W2 = np.load(_find_npy("W2.npy"))
try:
    nn.b1 = np.load(_find_npy("b1.npy"))
except FileNotFoundError:
    pass
try:
    nn.b2 = np.load(_find_npy("b2.npy"))
except FileNotFoundError:
    pass

# ─────────────────────────────────────────────
#  TYPE → COLOUR
# ─────────────────────────────────────────────
TYPE_COLORS = {
    "Fire":     ("#d62828", "#fff"),
    "Water":    ("#3a86ff", "#fff"),
    "Grass":    ("#38b000", "#fff"),
    "Electric": ("#f9c74f", "#000"),
    "Ice":      ("#90e0ef", "#000"),
    "Ground":   ("#8B6914", "#fff"),
    "Flying":   ("#7b2d8b", "#fff"),
    "Dragon":   ("#560bad", "#fff"),
    "Fairy":    ("#e07a9e", "#000"),
    "Poison":   ("#7b2d8b", "#fff"),
    "Fighting": ("#c1121f", "#fff"),
    "Bug":      ("#55a630", "#fff"),
    "Steel":    ("#adb5bd", "#000"),
    "Dark":     ("#1b1b2f", "#fff"),
    "Normal":   ("#6c757d", "#fff"),
    "Psychic":  ("#d62828", "#fff"),
    "Ghost":    ("#4a0e8f", "#fff"),
    "Rock":     ("#7c6f57", "#fff"),
}

# ─────────────────────────────────────────────
#  GBA PALETTE
# ─────────────────────────────────────────────
BG_DARK   = "#0a0a14"
BG_PANEL  = "#12122a"
BG_FIELD  = "#0e1428"
BORDER    = "#e8c84a"
BORDER2   = "#7a6420"
TEXT_W    = "#f0f0f0"
TEXT_Y    = "#f5c518"
TEXT_G    = "#7a8899"
HP_GREEN  = "#30c030"
HP_YELLOW = "#e8c800"
HP_RED    = "#e83030"
SHADOW    = "#000000"

# ─────────────────────────────────────────────
#  ROOT
# ─────────────────────────────────────────────
root = tk.Tk()
root.geometry("800x580")
root.title("Pokémon Battle")
root.configure(bg=BG_DARK)
root.resizable(False, False)

FONT_TITLE = ("Courier", 28, "bold")
FONT_SUB   = ("Courier", 13, "bold")
FONT_BODY  = ("Courier",  9, "bold")
FONT_BTN   = ("Courier",  8, "bold")
FONT_LOG   = ("Courier",  8)
FONT_HP    = ("Courier",  7, "bold")
FONT_SMALL = ("Courier",  7)

# ─────────────────────────────────────────────
#  SPRITE CACHE
# ─────────────────────────────────────────────
_sprite_cache: dict = {}

def load_sprite(name: str, back: bool = False, size: int = 120) -> ImageTk.PhotoImage:
    key = (name.lower(), back, size)
    if key in _sprite_cache:
        return _sprite_cache[key]
    side = "back" if back else "front"
    path = os.path.join(BASE_DIR, "sprites", f"{name.lower()}_{side}.png")
    if os.path.exists(path):
        img = Image.open(path).convert("RGBA")
        img = img.resize((size, size), Image.NEAREST)
    else:
        img = Image.new("RGBA", (size, size), (80, 80, 130, 180))
    photo = ImageTk.PhotoImage(img)
    _sprite_cache[key] = photo
    return photo

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def type_text(p):
    return "/".join(p.types)

def stop_game():
    global _after_id, _game_running
    _game_running = False
    if _after_id:
        try:
            root.after_cancel(_after_id)
        except Exception:
            pass
        _after_id = None

def clear_screen():
    global _blink_after_id
    stop_game()
    if _blink_after_id:
        try:
            root.after_cancel(_blink_after_id)
        except Exception:
            pass
        _blink_after_id = None
    for w in root.winfo_children():
        w.destroy()

def scanlines(canvas, w, h, step=4):
    for y in range(0, h, step):
        canvas.create_line(0, y, w, y, fill="#111122")

def gold_border(canvas, x1, y1, x2, y2):
    canvas.create_rectangle(x1+2, y1+2, x2+2, y2+2, outline=SHADOW,  width=3)
    canvas.create_rectangle(x1,   y1,   x2,   y2,   outline=BORDER,  width=3)
    canvas.create_rectangle(x1+4, y1+4, x2-4, y2-4, outline=BORDER2, width=1)

def pixel_button(parent, text, cmd, bg="#1a2040", fg=TEXT_W, w=18):
    outer = tk.Frame(parent, bg=BORDER, padx=2, pady=2)
    tk.Button(
        outer, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=TEXT_Y, activeforeground=SHADOW,
        font=FONT_BTN, relief="flat", cursor="hand2",
        width=w, pady=5
    ).pack()
    return outer

def draw_hp_bar(canvas, bx, by, bw, bh, cur, maxhp):
    ratio = max(0.0, cur / maxhp)
    if   ratio > 0.5: col = HP_GREEN;  hi = "#aaffaa"
    elif ratio > 0.2: col = HP_YELLOW; hi = "#ffff88"
    else:             col = HP_RED;    hi = "#ffaaaa"
    canvas.create_rectangle(bx, by, bx+bw, by+bh, fill="#1a1a1a", outline="#555")
    canvas.create_rectangle(bx, by, bx+int(bw*ratio), by+bh, fill=col)
    canvas.create_rectangle(bx, by, bx+int(bw*ratio), by+int(bh*0.4), fill=hi, outline="")
    canvas.create_text(bx+bw+4, by+bh//2, anchor="w",
                       text=f"{int(cur)}/{maxhp}", font=FONT_SMALL, fill=TEXT_G)

# ─────────────────────────────────────────────
#  STATE
# ─────────────────────────────────────────────
_after_id       = None
_game_running   = False
_blink_after_id = None

# ─────────────────────────────────────────────
#  DAMAGE / SWITCH HELPERS  (mirrors JS logic)
# ─────────────────────────────────────────────
def calc_move_damages(attacker, defender):
    damages = []
    for move in attacker.moves:
        mult = 1.0
        for t in defender.types:
            if move.type in TYPE_CHART and t in TYPE_CHART[move.type]:
                mult *= TYPE_CHART[move.type][t]
        if mult == 0:
            damages.append(-999)
        else:
            damages.append((attacker.attack / defender.defence) * move.bp * mult)
    return damages

def best_move_idx(attacker, defender):
    dmgs = calc_move_damages(attacker, defender)
    return dmgs.index(max(dmgs))

def ai_should_switch(cur_a, bench_a, cur_p):
    if bench_a is None or bench_a.current_hp <= 0:
        return False
    bench_score = 1.0
    atk_score   = 1.0
    for d_type in cur_p.types:
        for a_type in bench_a.types:
            if a_type in TYPE_CHART and d_type in TYPE_CHART[a_type]:
                bench_score *= TYPE_CHART[a_type][d_type]
        for a_type in cur_a.types:
            if a_type in TYPE_CHART and d_type in TYPE_CHART[a_type]:
                atk_score *= TYPE_CHART[a_type][d_type]
    return bench_score > 1.0 and bench_score > atk_score

# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
def main_menu():
    clear_screen()

    bg = tk.Canvas(root, width=800, height=580, bg=BG_DARK, highlightthickness=0)
    bg.place(x=0, y=0)
    scanlines(bg, 800, 580)
    gold_border(bg, 8, 8, 792, 572)

    cx, cy = 400, 290
    bg.create_oval(cx-160, cy-160, cx+160, cy+160, fill="#111122", outline=BORDER2, width=2)
    bg.create_rectangle(cx-160, cy-4, cx+160, cy+4, fill="#222240")
    bg.create_oval(cx-24, cy-24, cx+24, cy+24, fill="#222240", outline=BORDER2, width=2)

    for dx, dy in [(3,3),(2,2)]:
        bg.create_text(400+dx, 130+dy, text="POKÉMON",      font=FONT_TITLE, fill=SHADOW)
        bg.create_text(400+dx, 188+dy, text="BATTLE ARENA", font=FONT_SUB,   fill=SHADOW)
    bg.create_text(400, 130, text="POKÉMON",      font=FONT_TITLE, fill=TEXT_Y)
    bg.create_text(400, 188, text="BATTLE ARENA", font=FONT_SUB,   fill=TEXT_W)

    blink = tk.Label(root, text="▶  PRESS START  ◀", font=FONT_BODY,
                     fg=TEXT_Y, bg=BG_DARK)
    blink.place(x=400, y=340, anchor="center")

    _state = [True]
    def do_blink():
        global _blink_after_id
        if not blink.winfo_exists():
            return
        _state[0] = not _state[0]
        blink.config(fg=TEXT_Y if _state[0] else BG_DARK)
        _blink_after_id = root.after(550, do_blink)
    do_blink()

    btn = pixel_button(root, "NEW GAME", selection_screen, bg="#1a2a4a", w=20)
    btn.place(x=400, y=420, anchor="center")

# ─────────────────────────────────────────────
#  SELECTION SCREEN
# ─────────────────────────────────────────────
def selection_screen():
    clear_screen()

    bg = tk.Canvas(root, width=800, height=580, bg=BG_PANEL, highlightthickness=0)
    bg.place(x=0, y=0)
    scanlines(bg, 800, 580)
    gold_border(bg, 8, 8, 792, 572)
    bg.create_text(402, 42, text="CHOOSE YOUR TEAM", font=FONT_SUB, fill=SHADOW)
    bg.create_text(400, 40, text="CHOOSE YOUR TEAM", font=FONT_SUB, fill=TEXT_Y)
    bg.create_text(400, 68, text="Pick 2 Pokémon to battle with", font=FONT_SMALL, fill=TEXT_G)

    chosen = []
    count_var = tk.StringVar(value="Selected: 0 / 2")
    count_lbl = tk.Label(root, textvariable=count_var, font=FONT_BODY,
                         fg=TEXT_W, bg=BG_PANEL)
    count_lbl.place(x=400, y=520, anchor="center")

    COLS, start_x, start_y, cw, rh = 3, 80, 100, 216, 88

    for idx, p in enumerate(all_pokemon):
        col, row = idx % COLS, idx // COLS
        x = start_x + col * cw
        y = start_y + row * rh
        tc = TYPE_COLORS.get(p.types[0], ("#333","#fff"))

        outer = tk.Frame(root, bg=BORDER, padx=2, pady=2, cursor="hand2")
        outer.place(x=x, y=y, width=200, height=72)
        inner = tk.Frame(outer, bg=tc[0])
        inner.pack(fill="both", expand=True)

        n = tk.Label(inner, text=p.name.upper(),  font=FONT_BTN,   fg=tc[1], bg=tc[0])
        n.pack(pady=(8,0))
        t = tk.Label(inner, text=type_text(p),    font=FONT_SMALL, fg=tc[1], bg=tc[0])
        t.pack()
        s = tk.Label(inner, text=f"ATK {p.attack}  DEF {p.defence}  SPD {p.speed}",
                     font=FONT_SMALL, fg=tc[1], bg=tc[0])
        s.pack(pady=(0,4))

        def make_pick(pokemon=p, frame=outer, bg_col=tc[0]):
            def pick():
                if pokemon in chosen:
                    return
                chosen.append(pokemon)
                for widget in frame.winfo_children():
                    _recolor(widget, "#2a2a2a", TEXT_G)
                frame.configure(bg="#2a2a2a")
                count_var.set(f"Selected: {len(chosen)} / 2")
                if len(chosen) == 2:
                    root.after(250, lambda: start_battle(chosen))
            return pick

        fn = make_pick()
        for w in [outer, inner, n, t, s]:
            w.bind("<Button-1>", lambda e, f=fn: f())

def _recolor(widget, bg, fg=TEXT_G):
    try: widget.config(bg=bg)
    except Exception: pass
    try: widget.config(fg=fg)
    except Exception: pass
    for c in widget.winfo_children():
        _recolor(c, bg, fg)

# ─────────────────────────────────────────────
#  BATTLE SCREEN
# ─────────────────────────────────────────────
def start_battle(chosen):
    global _after_id, _game_running
    clear_screen()
    _game_running = True

    W, H, FH = 800, 580, 220

    # ── field canvas ──────────────────────────────────────────────────────────
    field = tk.Canvas(root, width=W, height=FH, bg=BG_FIELD, highlightthickness=0)
    field.place(x=0, y=0)

    # sky bands
    SKY_COLS = ["#09091e","#0c0c26","#10102e","#131338","#161640"]
    band_h = FH // len(SKY_COLS)
    for i, c in enumerate(SKY_COLS):
        field.create_rectangle(0, i*band_h, W, (i+1)*band_h, fill=c, outline="")

    # platforms
    field.create_oval(540, 108, 740, 140, fill="#0f3010", outline="#1a5520", width=2)
    field.create_oval( 60, 188, 260, 220, fill="#0f3010", outline="#1a5520", width=2)

    # ── HUD strip ─────────────────────────────────────────────────────────────
    HUD_H = 58
    hud_strip = tk.Canvas(root, width=W, height=HUD_H, bg="#0d0d20", highlightthickness=0)
    hud_strip.place(x=0, y=FH)
    hud_strip.create_line(0, 0, W, 0, fill=BORDER, width=2)
    hud_strip.create_line(0, HUD_H-1, W, HUD_H-1, fill=BORDER, width=2)
    hud_strip.create_line(W//2, 0, W//2, HUD_H, fill="#3a3010", width=1)

    # player left
    hud_strip.create_text(14, 12, anchor="w", text="---", font=FONT_BODY, fill=TEXT_W, tags="p-name")
    hud_strip.create_text(14, 27, anchor="w", text="",    font=FONT_SMALL, fill=TEXT_G, tags="p-types")
    hud_strip.create_text(14, 42, anchor="w", text="HP",  font=FONT_HP,   fill=TEXT_Y)
    # enemy right
    hud_strip.create_text(W//2+14, 12, anchor="w", text="---", font=FONT_BODY, fill=TEXT_W, tags="e-name")
    hud_strip.create_text(W//2+14, 27, anchor="w", text="",    font=FONT_SMALL, fill=TEXT_G, tags="e-types")
    hud_strip.create_text(W//2+14, 42, anchor="w", text="HP",  font=FONT_HP,   fill=TEXT_Y)

    HUD_BAR_X  = 40
    HUD_BAR_W  = 340
    HUD_BAR_Y  = 38
    HUD_BAR_H  = 10

    # ── bottom panel ──────────────────────────────────────────────────────────
    BOTTOM_Y = FH + HUD_H
    BOTTOM_H = H - BOTTOM_Y

    btm = tk.Frame(root, bg=BG_DARK, width=W, height=BOTTOM_H)
    btm.place(x=0, y=BOTTOM_Y)
    btm.pack_propagate(False)

    move_frame = tk.Frame(btm, bg=BG_DARK)
    move_frame.place(x=0, y=0, width=396, height=BOTTOM_H)

    # divider
    tk.Frame(btm, bg=BORDER, width=4, height=BOTTOM_H).place(x=396, y=0)

    log_border = tk.Frame(btm, bg=BORDER, padx=2, pady=2)
    log_border.place(x=400, y=6, width=392, height=BOTTOM_H-12)
    log_inner = tk.Frame(log_border, bg="#08080f")
    log_inner.pack(fill="both", expand=True)
    log = tk.Text(log_inner, bg="#08080f", fg=TEXT_W, font=FONT_LOG,
                  relief="flat", wrap="word", state="disabled", cursor="arrow",
                  padx=6, pady=4)
    log.pack(fill="both", expand=True)
    log.tag_config("damage", foreground="#ff6666")
    log.tag_config("info",   foreground=TEXT_Y)

    # ── teams ─────────────────────────────────────────────────────────────────
    team_p = [copy.deepcopy(x) for x in chosen]
    team_a = [copy.deepcopy(x) for x in random.sample(all_pokemon, 2)]
    for p in team_p + team_a:
        p.reset()

    idx_p = [0]
    idx_a = [0]
    def cur_p(): return team_p[idx_p[0]]
    def cur_a(): return team_a[idx_a[0]]

    # ── write to log ──────────────────────────────────────────────────────────
    def write(msg: str, tag: str = ""):
        log.config(state="normal")
        log.insert(tk.END, "▶ " + msg + "\n", tag if tag else ())
        log.see(tk.END)
        log.config(state="disabled")

    # ── HUD update ────────────────────────────────────────────────────────────
    def update_hud():
        # player
        p1 = cur_p()
        hud_strip.delete("p-name"); hud_strip.delete("p-types"); hud_strip.delete("p-hp-bar")
        hud_strip.create_text(14, 12, anchor="w", text=p1.name.upper(),
                              font=FONT_BODY, fill=TEXT_W, tags="p-name")
        hud_strip.create_text(14, 27, anchor="w", text=type_text(p1),
                              font=FONT_SMALL, fill=TEXT_G, tags="p-types")
        _draw_hud_bar(hud_strip, HUD_BAR_X, HUD_BAR_Y, HUD_BAR_W, HUD_BAR_H,
                      p1.current_hp, p1.hp, "p-hp-bar")

        # enemy
        p2 = cur_a()
        hud_strip.delete("e-name"); hud_strip.delete("e-types"); hud_strip.delete("e-hp-bar")
        ex = W//2 + 14
        hud_strip.create_text(ex, 12, anchor="w", text=p2.name.upper(),
                              font=FONT_BODY, fill=TEXT_W, tags="e-name")
        hud_strip.create_text(ex, 27, anchor="w", text=type_text(p2),
                              font=FONT_SMALL, fill=TEXT_G, tags="e-types")
        _draw_hud_bar(hud_strip, W//2+HUD_BAR_X, HUD_BAR_Y, HUD_BAR_W, HUD_BAR_H,
                      p2.current_hp, p2.hp, "e-hp-bar")

    def _draw_hud_bar(canvas, bx, by, bw, bh, cur, maxhp, tag):
        ratio = max(0.0, cur / maxhp)
        if   ratio > 0.5: col = HP_GREEN;  hi = "#aaffaa"
        elif ratio > 0.2: col = HP_YELLOW; hi = "#ffff88"
        else:             col = HP_RED;    hi = "#ffaaaa"
        canvas.create_rectangle(bx, by, bx+bw, by+bh, fill="#1a1a1a", outline="#555", tags=tag)
        canvas.create_rectangle(bx, by, bx+int(bw*ratio), by+bh, fill=col, tags=tag)
        canvas.create_rectangle(bx, by, bx+int(bw*ratio), by+int(bh*0.4),
                                 fill=hi, outline="", tags=tag)
        canvas.create_text(bx+bw+44, by+bh//2, anchor="w",
                           text=f"{int(cur)}/{maxhp}", font=FONT_SMALL, fill=TEXT_G, tags=tag)

    # ── sprites ───────────────────────────────────────────────────────────────
    _spr_refs = {}   # keep references so GC doesn't kill PhotoImages

    def update_sprites(slide_p=False, slide_e=False):
        field.delete("spr")
        spr_e = load_sprite(cur_a().name, back=False, size=120)
        spr_p = load_sprite(cur_p().name, back=True,  size=120)
        _spr_refs["e"] = spr_e
        _spr_refs["p"] = spr_p
        field.create_image(630, 10,  image=spr_e, anchor="n", tags="spr")
        field.create_image(150, FH,  image=spr_p, anchor="s", tags="spr")

    # ── move buttons ──────────────────────────────────────────────────────────
    def render_moves(locked=False):
        for w in move_frame.winfo_children():
            w.destroy()

        tk.Label(move_frame, text="WHAT WILL",  font=FONT_SMALL,
                 fg=TEXT_G, bg=BG_DARK).place(x=14, y=6)
        tk.Label(move_frame, text=f"{cur_p().name.upper()} DO?",
                 font=FONT_BODY, fg=TEXT_W, bg=BG_DARK).place(x=14, y=22)

        for k, m in enumerate(cur_p().moves):
            tc  = TYPE_COLORS.get(m.type, ("#2a2a2a","#fff"))
            col = k % 2
            row = k // 2
            bx  = 12  + col * 190
            by  = 52  + row * 58

            outer_f = tk.Frame(move_frame, bg=BORDER, padx=2, pady=2)
            outer_f.place(x=bx, y=by, width=182, height=52)

            bg_c = "#2a2a2a" if locked else tc[0]
            inner_f = tk.Frame(outer_f, bg=bg_c,
                               cursor="" if locked else "hand2")
            inner_f.pack(fill="both", expand=True)

            nl = tk.Label(inner_f, text=m.name.upper(), font=FONT_BTN,
                          fg=tc[1] if not locked else TEXT_G, bg=bg_c)
            nl.pack(pady=(5,0))
            il = tk.Label(inner_f,
                          text=f"{m.type}  PWR:{m.bp}  ACC:{m.acc}",
                          font=FONT_SMALL,
                          fg=tc[1] if not locked else TEXT_G, bg=bg_c)
            il.pack()

            if not locked:
                def on_move_click(idx=k):
                    render_moves(locked=True)
                    player_turn(move_idx=idx, switching=False)
                for ww in [outer_f, inner_f, nl, il]:
                    ww.bind("<Button-1>", lambda e, fn=on_move_click: fn())

        # switch button
        bench_alive = any(
            p.current_hp > 0 for i, p in enumerate(team_p) if i != idx_p[0]
        )
        bench_name = next(
            (p.name for i, p in enumerate(team_p)
             if i != idx_p[0] and p.current_hp > 0), ""
        )
        sw_bg  = "#1a3a1a" if (bench_alive and not locked) else "#1e1e1e"
        sw_fg  = "#66ff66" if (bench_alive and not locked) else TEXT_G
        sw_bdr = BORDER    if (bench_alive and not locked) else "#333"
        sw_text = f"SWITCH  →  {bench_name.upper()}" if bench_name else "SWITCH"
        if not bench_alive:
            sw_text += "  (fainted)"

        sw_outer = tk.Frame(move_frame, bg=sw_bdr, padx=2, pady=2)
        sw_outer.place(x=12, y=175, width=370, height=40)
        sw_inner = tk.Frame(sw_outer, bg=sw_bg,
                            cursor="hand2" if (bench_alive and not locked) else "")
        sw_inner.pack(fill="both", expand=True)
        sw_lbl = tk.Label(sw_inner, text=sw_text, font=FONT_BTN,
                          fg=sw_fg, bg=sw_bg)
        sw_lbl.pack(expand=True)

        if bench_alive and not locked:
            def on_switch():
                render_moves(locked=True)
                player_turn(move_idx=None, switching=True)
            for ww in [sw_outer, sw_inner, sw_lbl]:
                ww.bind("<Button-1>", lambda e, fn=on_switch: fn())

    # ── player turn ───────────────────────────────────────────────────────────
    def player_turn(move_idx, switching: bool):
        global _after_id
        p, e = cur_p(), cur_a()

        if switching:
            for ni, bp in enumerate(team_p):
                if ni != idx_p[0] and bp.current_hp > 0:
                    write(f"Come back, {p.name}!", "info")
                    idx_p[0] = ni
                    write(f"Go, {cur_p().name}!", "info")
                    update_sprites(slide_p=True)
                    break
        else:
            move = p.moves[move_idx]
            write(f"{p.name} used {move.name}!")
            result = p.attack_target(e, move)
            if result == 'missed':
                write("  ...missed!")
            else:
                write(f"  {e.name} took {int(result)} dmg!", "damage")
                if e.current_hp <= 0:
                    write(f"  {e.name} fainted!", "info")

        update_hud()
        update_sprites()
        _after_id = root.after(500, ai_turn)

    # ── AI turn ───────────────────────────────────────────────────────────────
    def ai_turn():
        global _after_id
        if not _game_running:
            return

        e, p = cur_a(), cur_p()

        # handle fainted active
        if e.current_hp <= 0:
            ni = next((i for i, x in enumerate(team_a)
                       if i != idx_a[0] and x.current_hp > 0), None)
            if ni is not None:
                idx_a[0] = ni
                write(f"Enemy sent {cur_a().name}!", "info")
                update_sprites(slide_e=True)
                update_hud()
            _after_id = root.after(400, game_loop)
            return

        # rule-based switch
        bench_idx = 1 - idx_a[0]
        bench_a   = team_a[bench_idx] if 0 <= bench_idx < len(team_a) else None
        if ai_should_switch(cur_a(), bench_a, cur_p()):
            write(f"Enemy withdrew {cur_a().name}!", "info")
            idx_a[0] = bench_idx
            write(f"Enemy sent {cur_a().name}!", "info")
            update_sprites(slide_e=True)
            update_hud()
            _after_id = root.after(500, game_loop)
            return

        # neural-net move selection (with 15% random noise)
        state  = np.array(get_state(cur_a(), cur_p()))
        scores = nn.forward(state)
        if np.random.rand() < 0.15:
            dmgs   = calc_move_damages(cur_a(), cur_p())
            viable = [i for i, d in enumerate(dmgs) if d > 0]
            ai_idx = random.choice(viable) if viable else int(np.argmax(scores))
        else:
            ai_idx = int(np.argmax(scores))
            if ai_idx >= 4:
                # NN chose switch but we handle that above — fall back to best move
                ai_idx = best_move_idx(cur_a(), cur_p())
            ai_idx = min(ai_idx, len(cur_a().moves) - 1)

        move = cur_a().moves[ai_idx]
        write(f"Enemy {cur_a().name} used {move.name}!")
        result = cur_a().attack_target(cur_p(), move)
        if result == 'missed':
            write("  ...missed!")
        else:
            write(f"  {cur_p().name} took {int(result)} dmg!", "damage")
            if cur_p().current_hp <= 0:
                write(f"  {cur_p().name} fainted!", "info")

        update_hud()
        _after_id = root.after(350, game_loop)

    # ── game loop ─────────────────────────────────────────────────────────────
    def game_loop():
        global _after_id
        if not _game_running:
            return

        p_alive = [p for p in team_p if p.current_hp > 0]
        a_alive = [a for a in team_a if a.current_hp > 0]

        if not p_alive:
            write("══════════════════", "info")
            write("  YOU LOST...",      "info")
            write("══════════════════", "info")
            _end_screen()
            stop_game()
            return

        if not a_alive:
            write("══════════════════", "info")
            write("  YOU WON! 🏆",      "info")
            write("══════════════════", "info")
            _end_screen()
            stop_game()
            return

        # auto-swap fainted mons
        if cur_p().current_hp <= 0:
            for ni, p in enumerate(team_p):
                if p.current_hp > 0:
                    idx_p[0] = ni
                    write(f"Go, {cur_p().name}!", "info")
                    break

        if cur_a().current_hp <= 0:
            for ni, a in enumerate(team_a):
                if a.current_hp > 0:
                    idx_a[0] = ni
                    write(f"Enemy sent {cur_a().name}!", "info")
                    break

        update_sprites()
        update_hud()
        render_moves()

    def _end_screen():
        for w in move_frame.winfo_children():
            w.destroy()
        pixel_button(move_frame, "PLAY AGAIN", selection_screen,
                     bg="#1a2a4a", fg=TEXT_W, w=20).place(x=60,  y=60)
        pixel_button(move_frame, "MAIN MENU",  main_menu,
                     bg="#2a1a1a", fg="#ff8888", w=20).place(x=60, y=116)

    # ── kick off ──────────────────────────────────────────────────────────────
    write(f"A wild {cur_a().name} appeared!", "info")
    write(f"Go, {cur_p().name}!", "info")
    update_sprites()
    update_hud()
    root.after(600, game_loop)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
main_menu()
root.mainloop()