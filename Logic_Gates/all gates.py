from OR_gate import OR_GATE
from NOR_gate import NOR_GATE
from AND_gate import AND_GATE, predict
from NAND_gate import NAND_GATE
from XOR_gate import XOR_GATE, prediction_XOR_XNOR
from XNOR_gate import XNOR_GATE
from visualize_gate import plot_gate
import tkinter as tk
import threading

# ── palette ───────────────────────────────────────────────────────────────────
BG        = "#0a0a0a"
PANEL     = "#111111"
BORDER    = "#2a2a2a"
BORDER_HI = "#3a3a3a"
NEON_BLUE = "#00e5ff"
NEON_PINK = "#ff2d78"
NEON_GRN  = "#00e676"
NEON_YLW  = "#ffe600"
NEON_ORG  = "#ff9100"
DIM       = "#444444"
WHITE     = "#e0e0e0"

# ── global state ──────────────────────────────────────────────────────────────
weights, biases, current_gate = None, None, None
current_gate_name = None
x1_val, x2_val = 0, 0
adder_op = None

# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET FACTORIES  (sharp, flat, custom-bordered)
# ─────────────────────────────────────────────────────────────────────────────
def sharp_btn(parent, text, color, command, width=7, font_size=9):
    """Flat button with a 1-px coloured border drawn via a surrounding Frame."""
    outer = tk.Frame(parent, bg=color, padx=1, pady=1)
    btn = tk.Button(
        outer, text=text, command=command,
        font=("Courier", font_size, "bold"),
        fg=color, bg=PANEL,
        activebackground=color, activeforeground=BG,
        relief="flat", bd=0, cursor="hand2",
        width=width, padx=0, pady=3,
    )
    btn.pack()
    # store border frame ref on btn so callers can reach it
    btn._outer = outer
    return outer, btn


def sharp_entry(parent, color, width=5):
    """Entry with a 1-px coloured border."""
    outer = tk.Frame(parent, bg=color, padx=1, pady=1)
    e = tk.Entry(
        outer, width=width,
        font=("Courier", 18, "bold"),
        fg=color, bg=PANEL,
        insertbackground=color,
        justify="center", relief="flat", bd=3,
    )
    e.pack()
    return outer, e


def section_label(parent, text, color=DIM):
    tk.Label(parent, text=text, font=("Courier", 8),
             fg=color, bg=BG).pack(anchor="w", padx=0, pady=(6, 1))


def divider(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=4)


# ─────────────────────────────────────────────────────────────────────────────
#  ANIMATION HELPERS  (unchanged logic, same API)
# ─────────────────────────────────────────────────────────────────────────────
def fade_label(label, text, color, steps=8, delay=16):
    grays = ["#111","#222","#333","#444","#555","#777","#999", color]
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


def pulse_btn_border(outer, color, restore):
    outer.config(bg=color)
    outer.after(130, lambda: outer.config(bg=restore))


def slide_frame(frame_out, frame_in, direction=1, steps=10, delay=14):
    w = frame_out.winfo_width() or 480
    frame_in.place(x=direction * w, y=0, relwidth=1, relheight=1)
    frame_in.lift()
    def _step(i=0):
        frac = i / steps
        ease = frac * frac * (3 - 2 * frac)
        frame_out.place(x=int(-direction * w * ease),      y=0, relwidth=1, relheight=1)
        frame_in.place( x=int( direction * w * (1-ease)),  y=0, relwidth=1, relheight=1)
        if i < steps:
            frame_out.after(delay, lambda: _step(i + 1))
        else:
            frame_out.place_forget()
            frame_in.place(x=0, y=0, relwidth=1, relheight=1)
    _step()


# ─────────────────────────────────────────────────────────────────────────────
#  GATE LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def select_gate(name, outer):
    global weights, biases, current_gate
    gate_status_label.config(text=f"training {name}…", fg=NEON_YLW)
    window.update()
    pulse_btn_border(outer, NEON_YLW, BORDER)

    def _train():
        global weights, biases, current_gate, current_gate_name
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
        current_gate_name = name
        window.after(0, lambda: gate_status_label.config(
            text=f"✓  {name} ready", fg=NEON_GRN))
        window.after(0, lambda: pulse_btn_border(outer, NEON_GRN, BORDER))

    threading.Thread(target=_train, daemon=True).start()


def plot_current_gate():
    if current_gate is None or weights is None:
        fade_label(result_label, "⚠  train a gate first", NEON_ORG)
        return
    gate_status_label.config(text="opening plot…", fg=NEON_YLW)
    # matplotlib MUST run on the main thread — use after() instead of a Thread
    window.after(0, lambda: plot_gate(current_gate_name, weights, biases, current_gate))


def predict_output():
    if current_gate is None:
        fade_label(result_label, "⚠  select a gate first", NEON_ORG)
        return
    fade_label(result_label, "computing…", NEON_YLW)
    window.update()

    def _run():
        if current_gate == "basic":
            res = predict(x1_val, x2_val, weights, biases)
        else:
            res = prediction_XOR_XNOR(x1_val, x2_val, weights, biases)
        color = NEON_GRN if res == 1 else NEON_PINK
        window.after(0, lambda: fade_label(result_label, f"output  →  {res}", color))

    threading.Thread(target=_run, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
#  BINARY ADDER / SUBTRACTOR
# ─────────────────────────────────────────────────────────────────────────────
def half_adder(a, b, w_xor, b_xor, w_and, b_and):
    return prediction_XOR_XNOR(a, b, w_xor, b_xor), predict(a, b, w_and, b_and)

def full_adder(a, b, cin, w_xor, b_xor, w_and, b_and, w_or, b_or):
    s1 = prediction_XOR_XNOR(a, b, w_xor, b_xor)
    c1 = predict(a, b, w_and, b_and)
    s  = prediction_XOR_XNOR(s1, cin, w_xor, b_xor)
    c2 = predict(s1, cin, w_and, b_and)
    return s, predict(c1, c2, w_or, b_or)

_adder_weights = {}

def get_adder_weights():
    if not _adder_weights:
        adder_status.config(text="training gates…", fg=NEON_YLW)
        window.update()
        _adder_weights["xor_w"], _adder_weights["xor_b"] = XOR_GATE()
        _adder_weights["and_w"], _adder_weights["and_b"] = AND_GATE()
        _adder_weights["or_w"],  _adder_weights["or_b"]  = OR_GATE()
        adder_status.config(text="gates ready ✓", fg=NEON_GRN)
    return _adder_weights

def run_adder():
    def _compute():
        try:
            A = int(numA_entry.get())
            B = int(numB_entry.get())
            if A < 0 or B < 0:
                raise ValueError
        except ValueError:
            window.after(0, lambda: fade_label(adder_result, "positive integers only", NEON_ORG))
            return

        op = adder_op.get()
        aw = get_adder_weights()

        # figure out how many bits we need
        if op == "sub":
            num_bits = max(A.bit_length(), B.bit_length(), 1)
            mask = (1 << num_bits) - 1
            effective_B = ((~B) & mask) + 1
        else:
            effective_B = B
            num_bits = max(A.bit_length(), effective_B.bit_length(), 1) + 1  # +1 for carry

        a_bits = [(A >> i) & 1 for i in range(num_bits)]
        b_bits = [(effective_B >> i) & 1 for i in range(num_bits)]

        carry, sum_bits, trace_lines = 0, [], []
        for i in range(num_bits):
            a, b = a_bits[i], b_bits[i]
            if i == 0 and op == "add":
                s, carry = half_adder(a, b, aw["xor_w"], aw["xor_b"],
                                             aw["and_w"], aw["and_b"])
                trace_lines.append(f"  bit{i}  HA({a},{b})  -> s={s}  c={carry}")
            else:
                prev_carry = carry
                s, carry = full_adder(a, b, carry,
                    aw["xor_w"], aw["xor_b"],
                    aw["and_w"], aw["and_b"],
                    aw["or_w"],  aw["or_b"])
                trace_lines.append(f"  bit{i}  FA({a},{b},cin={prev_carry})  -> s={s}  c={carry}")
            sum_bits.append(s)

        raw     = sum(bit << i for i, bit in enumerate(sum_bits))
        bin_str = "".join(str(sum_bits[i]) for i in range(len(sum_bits)-1, -1, -1))

        if op == "sub":
            result  = A - B
            equation = f"{A} - {B} = {result}"
        else:
            total    = raw + (carry << num_bits)
            equation = f"{A} + {B} = {total}"

        color = NEON_GRN
        window.after(0, lambda: _update_adder(equation, bin_str, "\n".join(trace_lines), color))

    threading.Thread(target=_compute, daemon=True).start()

def _update_adder(equation, bin_str, trace, color):
    fade_label(adder_result, equation, color)
    adder_binary.config(text=f"binary:  {bin_str}")
    num_lines = trace.count("\n") + 1
    trace_box.config(state="normal", height=max(4, num_lines))
    trace_box.delete("1.0", tk.END)
    trace_box.insert(tk.END, trace)
    trace_box.config(state="disabled")
    window.update_idletasks()
    window.geometry("")


# ─────────────────────────────────────────────────────────────────────────────
#  BIT TOGGLE
# ─────────────────────────────────────────────────────────────────────────────
def set_bit(which, val, btn0, btn1, color):
    global x1_val, x2_val
    if which == "x1":
        x1_val = val
    else:
        x2_val = val
    active, inactive = (btn1, btn0) if val == 1 else (btn0, btn1)
    active.config(fg=BG, bg=color)
    inactive.config(fg=color, bg=PANEL)
    # update border frame colours
    active._outer.config(bg=color)
    inactive._outer.config(bg=BORDER)


# ─────────────────────────────────────────────────────────────────────────────
#  WINDOW
# ─────────────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.title("Gate Predictor")
window.configure(bg=BG)
window.resizable(False, False)
adder_op = tk.StringVar(value="add")

# ── header ────────────────────────────────────────────────────────────────────
hdr = tk.Frame(window, bg=BG)
hdr.pack(fill="x", padx=14, pady=(10, 0))
tk.Label(hdr, text="GATE PREDICTOR",
         font=("Courier", 15, "bold"), fg=NEON_BLUE, bg=BG).pack(side="left")
tk.Label(hdr, text="perceptron + nn",
         font=("Courier", 8), fg=DIM, bg=BG).pack(side="left", padx=(8, 0), pady=(4, 0))

tk.Frame(window, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(6, 0))

# ── tab bar ───────────────────────────────────────────────────────────────────
tab_frame = tk.Frame(window, bg=BG)
tab_frame.pack(fill="x", padx=14, pady=(4, 0))

container = tk.Frame(window, bg=BG)
container.pack(fill="x", padx=14, pady=(4, 10))

gate_frame  = tk.Frame(container, bg=BG)
adder_frame = tk.Frame(container, bg=BG)
gate_frame.pack(fill="both", expand=True)

TAB_ACTIVE_BG   = PANEL
TAB_INACTIVE_BG = BG

def show_gate_tab():
    adder_frame.pack_forget()
    gate_frame.pack(fill="both", expand=True)
    btn_gate_tab.config(fg=NEON_BLUE, bg=TAB_ACTIVE_BG)
    btn_adder_tab.config(fg=DIM,      bg=TAB_INACTIVE_BG)

def show_adder_tab():
    gate_frame.pack_forget()
    adder_frame.pack(fill="both", expand=True)
    btn_adder_tab.config(fg=NEON_GRN, bg=TAB_ACTIVE_BG)
    btn_gate_tab.config(fg=DIM,       bg=TAB_INACTIVE_BG)

btn_gate_tab = tk.Button(tab_frame, text="Logic Gate",
    font=("Courier", 9, "bold"), fg=NEON_BLUE, bg=TAB_ACTIVE_BG,
    bd=0, padx=10, pady=4, relief="flat",
    activebackground=PANEL, activeforeground=NEON_BLUE,
    command=show_gate_tab)
btn_gate_tab.pack(side="left")

btn_adder_tab = tk.Button(tab_frame, text="Adder / Sub",
    font=("Courier", 9, "bold"), fg=DIM, bg=TAB_INACTIVE_BG,
    bd=0, padx=10, pady=4, relief="flat",
    activebackground=PANEL, activeforeground=NEON_GRN,
    command=show_adder_tab)
btn_adder_tab.pack(side="left")

tk.Frame(window, bg=BORDER, height=1).pack(fill="x", padx=14)

# ═════════════════════════════════════════════════════════════════════════════
#  GATE FRAME
# ═════════════════════════════════════════════════════════════════════════════
section_label(gate_frame, "SELECT GATE")

gate_status_label = tk.Label(gate_frame, text="no gate selected",
    font=("Courier", 8), fg=DIM, bg=BG)
gate_status_label.pack(anchor="w", pady=(0, 4))

g_btn_frame = tk.Frame(gate_frame, bg=BG)
g_btn_frame.pack(anchor="w")

GATE_BUTTONS_INFO = [
    ("AND",  NEON_PINK), ("OR",   NEON_BLUE),
    ("NAND", NEON_YLW),  ("NOR",  NEON_GRN),
    ("XOR",  NEON_PINK), ("XNOR", NEON_BLUE),
]

for idx, (name, color) in enumerate(GATE_BUTTONS_INFO):
    r, c = divmod(idx, 3)
    outer, btn = sharp_btn(g_btn_frame, name, color, None, width=6, font_size=9)
    btn.config(command=lambda n=name, o=outer: select_gate(n, o))
    outer.grid(row=r, column=c, padx=3, pady=3)

divider(gate_frame)
section_label(gate_frame, "INPUTS")

inp_frame = tk.Frame(gate_frame, bg=BG)
inp_frame.pack(anchor="w", pady=(0, 4))

def bit_row(parent, label, which, color, row):
    tk.Label(parent, text=label, fg=NEON_YLW, bg=BG,
             font=("Courier", 10, "bold"), width=3).grid(row=row, column=0, padx=(0,6))
    o0, b0 = sharp_btn(parent, "0", color, None, width=3, font_size=9)
    o1, b1 = sharp_btn(parent, "1", color, None, width=3, font_size=9)
    # initial state: 0 is active
    b0.config(fg=BG, bg=color)
    o0.config(bg=color)
    b1.config(fg=color, bg=PANEL)
    o1.config(bg=BORDER)
    b0.config(command=lambda: set_bit(which, 0, b0, b1, color))
    b1.config(command=lambda: set_bit(which, 1, b0, b1, color))
    o0.grid(row=row, column=1, padx=3, pady=2)
    o1.grid(row=row, column=2, padx=3, pady=2)

bit_row(inp_frame, "x1", "x1", NEON_BLUE, 0)
bit_row(inp_frame, "x2", "x2", NEON_PINK, 1)

divider(gate_frame)

pred_outer, pred_btn = sharp_btn(gate_frame, "▶  PREDICT", NEON_GRN,
                                  predict_output, width=14, font_size=10)
pred_outer.pack(pady=(2, 3))

plot_outer, plot_btn = sharp_btn(gate_frame, "◈  PLOT", NEON_BLUE,
                                  plot_current_gate, width=14, font_size=10)
plot_outer.pack(pady=(0, 6))

result_label = tk.Label(gate_frame, text="output  →  —",
    font=("Courier", 16, "bold"), fg=NEON_BLUE, bg=BG)
result_label.pack(pady=(0, 4))


# ═════════════════════════════════════════════════════════════════════════════
#  ADDER FRAME
# ═════════════════════════════════════════════════════════════════════════════
section_label(adder_frame, "4-BIT ADDER / SUBTRACTOR")

adder_status = tk.Label(adder_frame, text="",
    font=("Courier", 8), fg=DIM, bg=BG)
adder_status.pack(anchor="w", pady=(0, 4))

num_row = tk.Frame(adder_frame, bg=BG)
num_row.pack(anchor="w")

def num_entry_widget(parent, label_text, color):
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=label_text, fg=DIM, bg=BG,
             font=("Courier", 8)).pack(anchor="w")
    outer, e = sharp_entry(f, color, width=4)
    outer.pack()
    return f, e

fA, numA_entry = num_entry_widget(num_row, "A", NEON_BLUE)
fA.pack(side="left", padx=(0, 10))

op_col = tk.Frame(num_row, bg=BG)
op_col.pack(side="left", padx=(0, 10))
tk.Label(op_col, text="op", fg=DIM, bg=BG, font=("Courier", 8)).pack()

o_add, btn_add = sharp_btn(op_col, "+", NEON_GRN, None, width=2, font_size=12)
o_sub, btn_sub = sharp_btn(op_col, "−", NEON_ORG, None, width=2, font_size=12)
# initial: add is active
btn_add.config(fg=BG, bg=NEON_GRN); o_add.config(bg=NEON_GRN)
btn_sub.config(fg=NEON_ORG, bg=PANEL); o_sub.config(bg=BORDER)

def set_op(op):
    adder_op.set(op)
    if op == "add":
        btn_add.config(fg=BG, bg=NEON_GRN);  o_add.config(bg=NEON_GRN)
        btn_sub.config(fg=NEON_ORG, bg=PANEL); o_sub.config(bg=BORDER)
    else:
        btn_sub.config(fg=BG, bg=NEON_ORG);  o_sub.config(bg=NEON_ORG)
        btn_add.config(fg=NEON_GRN, bg=PANEL); o_add.config(bg=BORDER)

btn_add.config(command=lambda: set_op("add"))
btn_sub.config(command=lambda: set_op("sub"))
o_add.pack(pady=(0, 3))
o_sub.pack()

fB, numB_entry = num_entry_widget(num_row, "B", NEON_PINK)
fB.pack(side="left")

numA_entry.insert(0, "5")
numB_entry.insert(0, "3")

divider(adder_frame)

comp_outer, _ = sharp_btn(adder_frame, "▶  COMPUTE", NEON_GRN,
                            run_adder, width=14, font_size=10)
comp_outer.pack(pady=(2, 6))

adder_result = tk.Label(adder_frame, text="—",
    font=("Courier", 15, "bold"), fg=NEON_GRN, bg=BG)
adder_result.pack(anchor="w")

adder_binary = tk.Label(adder_frame, text="",
    font=("Courier", 9), fg=DIM, bg=BG)
adder_binary.pack(anchor="w")

divider(adder_frame)
section_label(adder_frame, "GATE TRACE")

# 1-px border around trace box
trace_outer = tk.Frame(adder_frame, bg=BORDER, padx=1, pady=1)
trace_outer.pack(fill="x", pady=(0, 4))
trace_box = tk.Text(trace_outer, height=5, width=54,
    font=("Courier", 8), fg=NEON_BLUE, bg=PANEL,
    relief="flat", bd=4, state="disabled")
trace_box.pack(fill="x")

# ── auto-size window to content ───────────────────────────────────────────────
window.update_idletasks()
w = window.winfo_reqwidth()
h = window.winfo_reqheight()
window.geometry(f"{w}x{h}")

window.mainloop()