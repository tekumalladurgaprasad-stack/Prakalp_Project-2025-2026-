from OR_gate import OR_GATE
from NOR_gate import NOR_GATE
from AND_gate import AND_GATE, predict
from NAND_gate import NAND_GATE
from XOR_gate import XOR_GATE, prediction_XOR_XNOR
from XNOR_gate import XNOR_GATE
import tkinter as tk


weights, biases, current_gate = None, None, None


def select_AND():
    global weights, biases, current_gate
    weights, biases = AND_GATE()
    current_gate = "basic"

def select_OR():
    global weights, biases, current_gate
    weights, biases = OR_GATE()
    current_gate = "basic"

def select_NOR():
    global weights, biases, current_gate
    weights, biases = NOR_GATE()
    current_gate = "basic"

def select_NAND():
    global weights, biases, current_gate
    weights, biases = NAND_GATE()
    current_gate = "basic"

def select_XOR():
    global weights, biases, current_gate
    weights, biases = XOR_GATE()
    current_gate = "nn"

def select_XNOR():
    global weights, biases, current_gate
    weights, biases = XNOR_GATE()
    current_gate = "nn"


def predict_output():
    if current_gate is None:
        result_label.config(text="Select a gate first!")
        return

    
    result_label.config(text="Analysing...")
    window.update()  

    if current_gate == "basic":
        result = predict(x1.get(), x2.get(), weights, biases)
    else:
        result = prediction_XOR_XNOR(x1.get(), x2.get(), weights, biases)

    result_label.config(text=f"Output: {result}")


window = tk.Tk()
window.title("Gate Predictor")
window.geometry("500x380")
window.configure(bg="#0f0f0f") 


NEON_BLUE = "#00fff0"
NEON_PINK = "#ff00ff"
NEON_GREEN = "#00ff00"
NEON_YELLOW = "#ffff00"
DARK_GRAY = "#1a1a1a"


tk.Label(window, text="GATE PREDICTOR", font=("Helvetica", 20, "bold"), fg=NEON_BLUE, bg="#0f0f0f").pack(pady=10)


tk.Label(window, text="Select Gate:", font=("Helvetica", 12), fg=NEON_GREEN, bg="#0f0f0f").pack()
frame_gates = tk.Frame(window, bg="#0f0f0f")
frame_gates.pack(pady=5)

buttons_info = [
    ("AND", select_AND, NEON_PINK),
    ("OR", select_OR, NEON_BLUE),
    ("NAND", select_NAND, NEON_YELLOW),
    ("NOR", select_NOR, NEON_GREEN),
    ("XOR", select_XOR, NEON_PINK),
    ("XNOR", select_XNOR, NEON_BLUE)
]

for idx, (text, cmd, color) in enumerate(buttons_info):
    row, col = divmod(idx, 4)
    tk.Button(frame_gates, text=text, width=6, command=cmd,
              fg=color, bg=DARK_GRAY, activebackground=color, activeforeground="#0f0f0f", font=("Helvetica", 10, "bold")).grid(row=row, column=col, padx=5, pady=5)


x1 = tk.IntVar()
x2 = tk.IntVar()
frame_inputs = tk.Frame(window, bg="#0f0f0f")
frame_inputs.pack(pady=15)


tk.Label(frame_inputs, text="x1:", fg=NEON_YELLOW, bg="#0f0f0f", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
tk.Button(frame_inputs, text="0", width=3, command=lambda: x1.set(0), fg=NEON_BLUE, bg=DARK_GRAY,
          activebackground=NEON_BLUE, activeforeground="#0f0f0f").grid(row=0, column=1, padx=3)
tk.Button(frame_inputs, text="1", width=3, command=lambda: x1.set(1), fg=NEON_BLUE, bg=DARK_GRAY,
          activebackground=NEON_BLUE, activeforeground="#0f0f0f").grid(row=0, column=2, padx=3)

tk.Label(frame_inputs, text="x2:", fg=NEON_YELLOW, bg="#0f0f0f", font=("Helvetica", 12)).grid(row=1, column=0, padx=5)
tk.Button(frame_inputs, text="0", width=3, command=lambda: x2.set(0), fg=NEON_PINK, bg=DARK_GRAY,
          activebackground=NEON_PINK, activeforeground="#0f0f0f").grid(row=1, column=1, padx=3)
tk.Button(frame_inputs, text="1", width=3, command=lambda: x2.set(1), fg=NEON_PINK, bg=DARK_GRAY,
          activebackground=NEON_PINK, activeforeground="#0f0f0f").grid(row=1, column=2, padx=3)


tk.Button(window, text="Predict", width=12, command=predict_output, fg=NEON_GREEN, bg=DARK_GRAY,
          activebackground=NEON_GREEN, activeforeground="#0f0f0f", font=("Helvetica", 12, "bold")).pack(pady=10)


result_label = tk.Label(window, text="Output: ", font=("Helvetica", 14, "bold"), fg=NEON_BLUE, bg="#0f0f0f")
result_label.pack(pady=5)

window.mainloop()