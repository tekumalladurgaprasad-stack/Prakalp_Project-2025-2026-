from OR_gate import OR_GATE
from NOR_gate import NOR_GATE
from AND_gate import AND_GATE, predict
from NAND_gate import NAND_GATE
from XOR_gate import XOR_GATE, prediction_XOR_XNOR
from XNOR_gate import XNOR_GATE
import tkinter as tk
from tkinter import ttk
import threading

# ── colours ──────────────────────────────────────────────────────────────────
BG        = "#0f0f0f"
DARK_GRAY = "#1a1a1a"
MID_GRAY  = "#2a2a2a"
NEON_BLUE = "#00fff0"
NEON_PINK = "#ff00ff"
NEON_GRN  = "#00ff00"
NEON_YLW  = "#ffff00"
NEON_ORG  = "#ff9900"
DIM       = "#555555"
WHITE     = "#ffffff"

# ── global state ─────────────────────────────────────────────────────────────
weights, biases, current_gate = None, None, None
x1_val, x2_val = 0, 0
adder_op = None                    # initialised after tk.Tk()

# ─────────────────────────────────────────────────────────────────────────────
#  ANIMATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fade_label(label, text, color, steps=8, delay=18):
    """Fade a label out, swap text, fade back in."""
    grays = ["#111111","#222222","#333333","#444444",
             "#555555","#777777","#999999", color]
    def _out(i=0):
        if i < steps:
            label.config(fg=grays[steps - 1 - i])
            label.after(delay, lambda: _out(i + 1))
        else:
            label.config(text=text)
            _in()
    def _in(i=0):
        if i < steps:
            label.config(fg=grays[i])
            label.after(delay, lambda: _in(i + 1))
    _out()

def pulse_button(btn, base_bg, highlight):
    """Flash a button background briefly."""
    btn.config(bg=highlight)
    btn.after(120, lambda: btn.config(bg=base_bg))

def slide_frame(frame_out, frame_in, direction=1, steps=10, delay=15):
    """Slide one frame out and another in (left/right)."""
    w = frame_out.winfo_width() or 480
    frame_in.place(x=direction * w, y=0, relwidth=1, relheight=1)
    frame_in.lift()
    def _step(i=0):
        frac = i / steps
        ease = frac * frac * (3 - 2 * frac)          # smoothstep
        ox = int(-direction * w * ease)
        ix = int(direction * w * (1 - ease))
        frame_out.place(x=ox, y=0, relwidth=1, relheight=1)
        frame_in.place(x=ix, y=0, relwidth=1, relheight=1)
        if i < steps:
            frame_out.after(delay, lambda: _step(i + 1))
        else:
            frame_out.place_forget()
            frame_in.place(x=0, y=0, relwidth=1, relheight=1)
    _step()

# ─────────────────────────────────────────────────────────────────────────────
#  GATE LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def select_gate(name, btn):
    global weights, biases, current_gate
    gate_status_label.config(text=f"Training {name}…", fg=NEON_YLW)
    window.update()
    pulse_button(btn, DARK_GRAY, MID_GRAY)

    def _train():
        global weights, biases, current_gate
        dispatch = {
            "AND":  (AND_GATE,  "basic"),
            "OR":   (OR_GATE,   "basic"),
            "NOR":  (NOR_GATE,  "basic"),
            "NAND": (NAND_GATE, "basic"),
            "XOR":  (XOR_GATE,  "nn"),
            "XNOR": (XNOR_GATE, "nn"),
        }
        fn, kind = dispatch[name]
        weights, biases = fn()
        current_gate = kind
        window.after(0, lambda: gate_status_label.config(
            text=f"✓ {name} ready", fg=NEON_GRN))

    threading.Thread(target=_train, daemon=True).start()


def predict_output():
    if current_gate is None:
        fade_label(result_label, "⚠  Select a gate first!", NEON_ORG)
        return

    fade_label(result_label, "Computing…", NEON_YLW)
    window.update()

    def _run():
        if current_gate == "basic":
            res = predict(x1_val, x2_val, weights, biases)
        else:
            res = prediction_XOR_XNOR(x1_val, x2_val, weights, biases)
        color = NEON_GRN if res == 1 else NEON_PINK
        window.after(0, lambda: fade_label(result_label, f"Output:  {res}", color))

    threading.Thread(target=_run, daemon=True).start()

# ─────────────────────────────────────────────────────────────────────────────
#  BINARY ADDER / SUBTRACTOR  (uses your gate functions)
# ─────────────────────────────────────────────────────────────────────────────
def half_adder(a, b, w_xor, b_xor, w_and, b_and):
    s = prediction_XOR_XNOR(a, b, w_xor, b_xor)
    c = predict(a, b, w_and, b_and)
    return s, c

def full_adder(a, b, cin, w_xor, b_xor, w_and, b_and, w_or, b_or):
    s1 = prediction_XOR_XNOR(a, b, w_xor, b_xor)
    c1 = predict(a, b, w_and, b_and)
    s  = prediction_XOR_XNOR(s1, cin, w_xor, b_xor)
    c2 = predict(s1, cin, w_and, b_and)
    cout = predict(c1, c2, w_or, b_or)
    return s, cout

_adder_weights = {}          # cached so we don't retrain every click

def get_adder_weights():
    if not _adder_weights:
        adder_status.config(text="Training gates…", fg=NEON_YLW)
        window.update()
        _adder_weights["xor_w"], _adder_weights["xor_b"] = XOR_GATE()
        _adder_weights["and_w"], _adder_weights["and_b"] = AND_GATE()
        _adder_weights["or_w"],  _adder_weights["or_b"]  = OR_GATE()
        adder_status.config(text="Gates ready ✓", fg=NEON_GRN)
    return _adder_weights

def run_adder():
    def _compute():
        try:
            A = int(numA_entry.get())
            B = int(numB_entry.get())
        except ValueError:
            window.after(0, lambda: fade_label(adder_result, "Invalid input!", NEON_ORG))
            return

        A = max(0, min(15, A))
        B = max(0, min(15, B))
        op = adder_op.get()
        aw = get_adder_weights()

        # two's complement subtraction
        effective_B = ((~B) & 0xF) + 1 if op == "sub" else B

        a_bits = [(A >> i) & 1 for i in range(4)]
        b_bits = [(effective_B >> i) & 1 for i in range(4)]

        carry = 0
        sum_bits = []
        trace_lines = []

        for i in range(4):
            a, b = a_bits[i], b_bits[i]
            if i == 0 and op == "add":
                s, carry = half_adder(a, b,
                    aw["xor_w"], aw["xor_b"],
                    aw["and_w"], aw["and_b"])
                trace_lines.append(
                    f"  bit{i}  HA({a},{b})  → sum={s}  carry={carry}")
            else:
                s, carry = full_adder(a, b, carry,
                    aw["xor_w"], aw["xor_b"],
                    aw["and_w"], aw["and_b"],
                    aw["or_w"],  aw["or_b"])
                trace_lines.append(
                    f"  bit{i}  FA({a},{b},cin={carry if i>0 else 0})  → sum={s}  carry={carry}")
            sum_bits.append(s)

        raw = sum(b << i for i, b in enumerate(sum_bits))
        bin_str = "".join(str(sum_bits[i]) for i in range(3, -1, -1))
        overflow = (carry == 1 and op == "add")

        if op == "sub":
            display_val = A - B
            equation = f"{A} − {B} = {display_val}"
        else:
            display_val = raw + (carry << 4)
            equation = f"{A} + {B} = {display_val}" + (" (overflow!)" if overflow else "")

        trace_text = "\n".join(trace_lines)
        color = NEON_ORG if overflow else NEON_GRN

        window.after(0, lambda: _update_adder(equation, bin_str, trace_text, color))

    threading.Thread(target=_compute, daemon=True).start()

def _update_adder(equation, bin_str, trace, color):
    fade_label(adder_result, equation, color)
    adder_binary.config(text=f"Binary: {bin_str}")
    trace_box.config(state="normal")
    trace_box.delete("1.0", tk.END)
    trace_box.insert(tk.END, trace)
    trace_box.config(state="disabled")

# ─────────────────────────────────────────────────────────────────────────────
#  BIT TOGGLE HELPER
# ─────────────────────────────────────────────────────────────────────────────
def set_bit(which, val, btn0, btn1):
    global x1_val, x2_val
    if which == "x1":
        x1_val = val
    else:
        x2_val = val
    active, inactive = (btn1, btn0) if val == 1 else (btn0, btn1)
    active.config(fg="#0f0f0f",
                  bg=NEON_BLUE if which == "x1" else NEON_PINK,
                  relief="sunken")
    inactive.config(fg=NEON_BLUE if which == "x1" else NEON_PINK,
                    bg=DARK_GRAY, relief="raised")

# ─────────────────────────────────────────────────────────────────────────────
#  BUILD WINDOW
# ─────────────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.title("Gate Predictor Pro")
window.geometry("520x560")
window.configure(bg=BG)
window.resizable(False, False)
adder_op = tk.StringVar(value="add")

# ── header ───────────────────────────────────────────────────────────────────
tk.Label(window, text="GATE PREDICTOR PRO",
         font=("Helvetica", 18, "bold"), fg=NEON_BLUE, bg=BG).pack(pady=(12, 0))
tk.Label(window, text="perceptron & neural network edition",
         font=("Helvetica", 9), fg=DIM, bg=BG).pack()

# ── tab bar ──────────────────────────────────────────────────────────────────
tab_frame = tk.Frame(window, bg=MID_GRAY, height=2)
tab_frame.pack(fill="x", padx=16, pady=(10, 0))

btn_gate_tab = None
btn_adder_tab = None

container = tk.Frame(window, bg=BG, width=488, height=440)
container.pack(fill="both", expand=True, padx=16, pady=8)
container.pack_propagate(False)

gate_frame  = tk.Frame(container, bg=BG)
adder_frame = tk.Frame(container, bg=BG)
gate_frame.place(x=0, y=0, relwidth=1, relheight=1)

def show_gate_tab():
    slide_frame(adder_frame, gate_frame, direction=-1)
    btn_gate_tab.config(fg=NEON_BLUE, bg=MID_GRAY)
    btn_adder_tab.config(fg=DIM, bg=DARK_GRAY)

def show_adder_tab():
    slide_frame(gate_frame, adder_frame, direction=1)
    btn_adder_tab.config(fg=NEON_GRN, bg=MID_GRAY)
    btn_gate_tab.config(fg=DIM, bg=DARK_GRAY)

btn_gate_tab = tk.Button(tab_frame, text="Logic Gate", font=("Helvetica", 10, "bold"),
    fg=NEON_BLUE, bg=MID_GRAY, bd=0, padx=14, pady=6,
    activebackground=MID_GRAY, activeforeground=NEON_BLUE,
    command=show_gate_tab)
btn_gate_tab.pack(side="left")

btn_adder_tab = tk.Button(tab_frame, text="Adder / Subtractor", font=("Helvetica", 10, "bold"),
    fg=DIM, bg=DARK_GRAY, bd=0, padx=14, pady=6,
    activebackground=MID_GRAY, activeforeground=NEON_GRN,
    command=show_adder_tab)
btn_adder_tab.pack(side="left")

# ═════════════════════════════════════════════════════════════════════════════
#  GATE FRAME
# ═════════════════════════════════════════════════════════════════════════════
tk.Label(gate_frame, text="Select Gate", font=("Helvetica", 10),
         fg=DIM, bg=BG).pack(anchor="w", padx=4, pady=(8, 4))

gate_status_label = tk.Label(gate_frame, text="No gate selected",
    font=("Helvetica", 9), fg=DIM, bg=BG)
gate_status_label.pack(anchor="w", padx=4)

g_btn_frame = tk.Frame(gate_frame, bg=BG)
g_btn_frame.pack(pady=6)

gate_buttons_info = [
    ("AND",  NEON_PINK), ("OR",   NEON_BLUE),
    ("NAND", NEON_YLW),  ("NOR",  NEON_GRN),
    ("XOR",  NEON_PINK), ("XNOR", NEON_BLUE),
]

for idx, (name, color) in enumerate(gate_buttons_info):
    r, c = divmod(idx, 4)
    btn = tk.Button(g_btn_frame, text=name, width=7,
                    fg=color, bg=DARK_GRAY,
                    activebackground=color, activeforeground=BG,
                    font=("Helvetica", 10, "bold"), relief="raised")
    btn.config(command=lambda n=name, b=btn: select_gate(n, b))
    btn.grid(row=r, column=c, padx=5, pady=5)

# ── inputs ───────────────────────────────────────────────────────────────────
tk.Label(gate_frame, text="Inputs", font=("Helvetica", 10),
         fg=DIM, bg=BG).pack(anchor="w", padx=4, pady=(10, 4))

inp_frame = tk.Frame(gate_frame, bg=BG)
inp_frame.pack()

# x1 row
tk.Label(inp_frame, text="x1:", fg=NEON_YLW, bg=BG,
         font=("Helvetica", 12)).grid(row=0, column=0, padx=8)
x1b0 = tk.Button(inp_frame, text="0", width=4, fg="#0f0f0f", bg=NEON_BLUE,
                  relief="sunken", font=("Helvetica", 10, "bold"),
                  activebackground=NEON_BLUE)
x1b1 = tk.Button(inp_frame, text="1", width=4, fg=NEON_BLUE, bg=DARK_GRAY,
                  relief="raised", font=("Helvetica", 10, "bold"),
                  activebackground=NEON_BLUE)
x1b0.config(command=lambda: set_bit("x1", 0, x1b0, x1b1))
x1b1.config(command=lambda: set_bit("x1", 1, x1b0, x1b1))
x1b0.grid(row=0, column=1, padx=3, pady=5)
x1b1.grid(row=0, column=2, padx=3, pady=5)

# x2 row
tk.Label(inp_frame, text="x2:", fg=NEON_YLW, bg=BG,
         font=("Helvetica", 12)).grid(row=1, column=0, padx=8)
x2b0 = tk.Button(inp_frame, text="0", width=4, fg="#0f0f0f", bg=NEON_PINK,
                  relief="sunken", font=("Helvetica", 10, "bold"),
                  activebackground=NEON_PINK)
x2b1 = tk.Button(inp_frame, text="1", width=4, fg=NEON_PINK, bg=DARK_GRAY,
                  relief="raised", font=("Helvetica", 10, "bold"),
                  activebackground=NEON_PINK)
x2b0.config(command=lambda: set_bit("x2", 0, x2b0, x2b1))
x2b1.config(command=lambda: set_bit("x2", 1, x2b0, x2b1))
x2b0.grid(row=1, column=1, padx=3, pady=5)
x2b1.grid(row=1, column=2, padx=3, pady=5)

# ── predict button ────────────────────────────────────────────────────────────
tk.Button(gate_frame, text="▶  Predict", width=14, command=predict_output,
          fg=NEON_GRN, bg=DARK_GRAY,
          activebackground=NEON_GRN, activeforeground=BG,
          font=("Helvetica", 12, "bold")).pack(pady=10)

result_label = tk.Label(gate_frame, text="Output: —",
    font=("Courier", 18, "bold"), fg=NEON_BLUE, bg=BG)
result_label.pack(pady=4)

# ═════════════════════════════════════════════════════════════════════════════
#  ADDER FRAME
# ═════════════════════════════════════════════════════════════════════════════
tk.Label(adder_frame, text="4-bit Adder / Subtractor",
         font=("Helvetica", 11, "bold"), fg=NEON_GRN, bg=BG).pack(pady=(10, 2))
tk.Label(adder_frame, text="Using XOR, AND, OR gate models",
         font=("Helvetica", 8), fg=DIM, bg=BG).pack()

adder_status = tk.Label(adder_frame, text="", font=("Helvetica", 8), fg=DIM, bg=BG)
adder_status.pack()

num_row = tk.Frame(adder_frame, bg=BG)
num_row.pack(pady=10)

def num_entry(parent, label_text, color):
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=label_text, fg=color, bg=BG,
             font=("Helvetica", 10)).pack()
    e = tk.Entry(f, width=5, font=("Courier", 20, "bold"),
                 fg=color, bg=DARK_GRAY, insertbackground=color,
                 justify="center", relief="flat", bd=4)
    e.pack()
    return f, e

fA, numA_entry = num_entry(num_row, "Number A  (0–15)", NEON_BLUE)
fA.pack(side="left", padx=12)

op_col = tk.Frame(num_row, bg=BG)
op_col.pack(side="left", padx=8)
tk.Label(op_col, text="op", fg=DIM, bg=BG, font=("Helvetica", 8)).pack()
btn_add = tk.Button(op_col, text="+", width=3, font=("Helvetica", 14, "bold"),
    fg=BG, bg=NEON_GRN, activebackground=NEON_GRN, relief="flat")
btn_sub = tk.Button(op_col, text="−", width=3, font=("Helvetica", 14, "bold"),
    fg=NEON_ORG, bg=DARK_GRAY, activebackground=NEON_ORG, relief="flat")

def set_op(op):
    adder_op.set(op)
    if op == "add":
        btn_add.config(fg=BG, bg=NEON_GRN)
        btn_sub.config(fg=NEON_ORG, bg=DARK_GRAY)
    else:
        btn_sub.config(fg=BG, bg=NEON_ORG)
        btn_add.config(fg=NEON_GRN, bg=DARK_GRAY)

btn_add.config(command=lambda: set_op("add"))
btn_sub.config(command=lambda: set_op("sub"))
btn_add.pack(pady=2)
btn_sub.pack(pady=2)

fB, numB_entry = num_entry(num_row, "Number B  (0–15)", NEON_PINK)
fB.pack(side="left", padx=12)

numA_entry.insert(0, "5")
numB_entry.insert(0, "3")

tk.Button(adder_frame, text="▶  Compute", width=14, command=run_adder,
          fg=NEON_GRN, bg=DARK_GRAY,
          activebackground=NEON_GRN, activeforeground=BG,
          font=("Helvetica", 12, "bold")).pack(pady=6)

adder_result = tk.Label(adder_frame, text="—",
    font=("Courier", 16, "bold"), fg=NEON_GRN, bg=BG)
adder_result.pack()

adder_binary = tk.Label(adder_frame, text="",
    font=("Courier", 10), fg=DIM, bg=BG)
adder_binary.pack()

tk.Label(adder_frame, text="Gate trace", font=("Helvetica", 9),
         fg=DIM, bg=BG).pack(anchor="w", padx=16, pady=(8, 2))

trace_box = tk.Text(adder_frame, height=5, width=54,
    font=("Courier", 9), fg=NEON_BLUE, bg=DARK_GRAY,
    relief="flat", bd=4, state="disabled")
trace_box.pack(padx=16)

# ─────────────────────────────────────────────────────────────────────────────
window.mainloop()
