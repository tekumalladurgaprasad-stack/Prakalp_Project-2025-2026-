import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ── colour palette (matches the tkinter UI) ───────────────────────────────────
BG       = "#0a0a0a"
PANEL    = "#111111"
NEON_BLUE = "#00e5ff"
NEON_PINK = "#ff2d78"
NEON_GRN  = "#00e676"
NEON_YLW  = "#ffe600"
DIM      = "#444444"

# custom 0→1 colormap: pink → dark → cyan
CMAP = LinearSegmentedColormap.from_list(
    "gate_cmap", [NEON_PINK, "#1a0010", "#001a1a", NEON_BLUE]
)

POINT_COLORS = {0: NEON_PINK, 1: NEON_GRN}
TRUTH_TABLE  = {
    "AND":  [0, 0, 0, 1],
    "OR":   [0, 1, 1, 1],
    "NAND": [1, 1, 1, 0],
    "NOR":  [1, 0, 0, 0],
    "XOR":  [0, 1, 1, 0],
    "XNOR": [1, 0, 0, 1],
}
INPUTS = [(0, 0), (0, 1), (1, 0), (1, 1)]


# ── prediction helpers ─────────────────────────────────────────────────────────
def _predict_basic(x1, x2, weights, biases):
    z = x1 * weights[0] + x2 * weights[1] + biases
    return 1 if z >= 0 else 0


def _predict_nn(x1, x2, weights, biases):
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    inp = np.array([x1, x2])
    a1  = sigmoid(inp @ weights[0] + biases[0])
    a2  = sigmoid(a1  @ weights[1] + biases[1])
    return 1 if float(a2.flat[0]) >= 0.5 else 0


def _score_nn(x1, x2, weights, biases):
    """Return raw probability (float) for the heatmap."""
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    inp = np.array([x1, x2])
    a1  = sigmoid(inp @ weights[0] + biases[0])
    a2  = sigmoid(a1  @ weights[1] + biases[1])
    return float(a2.flat[0])


# ── shared figure styling ──────────────────────────────────────────────────────
def _style_axes(ax, title):
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=NEON_BLUE, fontfamily="monospace",
                 fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("x1", color=DIM, fontfamily="monospace")
    ax.set_ylabel("x2", color=DIM, fontfamily="monospace")
    ax.tick_params(colors=DIM)
    for spine in ax.spines.values():
        spine.set_edgecolor(DIM)
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-0.3, 1.3)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])


def _plot_truth_points(ax, gate_name):
    labels = TRUTH_TABLE[gate_name]
    for (x1, x2), lbl in zip(INPUTS, labels):
        ax.scatter(x1, x2,
                   color=POINT_COLORS[lbl],
                   s=220, zorder=5,
                   edgecolors="white", linewidths=0.8)
        ax.text(x1 + 0.07, x2 + 0.07, str(lbl),
                color="white", fontfamily="monospace",
                fontsize=11, fontweight="bold", zorder=6)


# ─────────────────────────────────────────────────────────────────────────────
#  PERCEPTRON PLOT  (AND / OR / NAND / NOR)
#  Shows decision boundary line + colour-coded truth-table dots
# ─────────────────────────────────────────────────────────────────────────────
def plot_perceptron(gate_name, weights, biases):
    """
    weights : 1-D array-like of length 2  [w0, w1]
    biases  : scalar
    """
    w0, w1 = float(weights[0]), float(weights[1])
    b      = float(biases)

    fig, ax = plt.subplots(figsize=(5, 4.5))
    fig.patch.set_facecolor(BG)
    _style_axes(ax, f"{gate_name}  —  decision boundary")

    # ── background shading ────────────────────────────────────────────────────
    xs = np.linspace(-0.3, 1.3, 300)
    ys = np.linspace(-0.3, 1.3, 300)
    xx, yy = np.meshgrid(xs, ys)
    zz = w0 * xx + w1 * yy + b          # raw activation
    ax.contourf(xx, yy, zz, levels=[-1e9, 0, 1e9],
                colors=[NEON_PINK + "40", NEON_BLUE + "40"], zorder=0)

    # ── decision boundary ─────────────────────────────────────────────────────
    if abs(w1) > 1e-9:                  # x2 = -(w0*x1 + b) / w1
        x_line = np.array([-0.3, 1.3])
        y_line = -(w0 * x_line + b) / w1
        ax.plot(x_line, y_line, color=NEON_YLW, linewidth=2,
                linestyle="--", label="boundary", zorder=3)
    else:                               # vertical line
        xv = -b / (w0 + 1e-12)
        ax.axvline(xv, color=NEON_YLW, linewidth=2, linestyle="--", label="boundary")

    # ── truth-table dots + weight annotation ──────────────────────────────────
    _plot_truth_points(ax, gate_name)
    ax.legend(fontsize=8, labelcolor="white",
              facecolor=PANEL, edgecolor=DIM, loc="upper left")

    # weight text
    fig.text(0.13, 0.01,
             f"w₀={w0:.3f}   w₁={w1:.3f}   b={b:.3f}",
             color=DIM, fontfamily="monospace", fontsize=7)

    plt.tight_layout()
    plt.show(block=False)


# ─────────────────────────────────────────────────────────────────────────────
#  NEURAL-NETWORK PLOT  (XOR / XNOR)
#  Shows a smooth probability heatmap over [0,1]² + truth-table dots
# ─────────────────────────────────────────────────────────────────────────────
def plot_nn(gate_name, weights, biases):
    """
    weights : list  [w1 (2×2), w2 (2×1)]
    biases  : list  [b1 (1×2), b2 (1×1)]
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.patch.set_facecolor(BG)

    # ── left: probability heatmap ─────────────────────────────────────────────
    ax = axes[0]
    _style_axes(ax, f"{gate_name}  —  output heatmap")

    res = 200
    xs  = np.linspace(0, 1, res)
    ys  = np.linspace(0, 1, res)
    xx, yy = np.meshgrid(xs, ys)
    zz = np.vectorize(lambda a, b: _score_nn(a, b, weights, biases))(xx, yy)

    im = ax.imshow(zz, extent=[0, 1, 0, 1], origin="lower",
                   cmap=CMAP, vmin=0, vmax=1, aspect="auto", zorder=1)
    ax.contour(xx, yy, zz, levels=[0.5], colors=[NEON_YLW],
               linewidths=2, linestyles="--", zorder=2)
    _plot_truth_points(ax, gate_name)

    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.yaxis.set_tick_params(color=DIM)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color=DIM,
             fontfamily="monospace", fontsize=7)
    cb.set_label("P(output = 1)", color=DIM,
                 fontfamily="monospace", fontsize=8)

    # ── right: discrete prediction grid ───────────────────────────────────────
    ax2 = axes[1]
    _style_axes(ax2, f"{gate_name}  —  predicted output")

    res2 = 60
    xs2  = np.linspace(0, 1, res2)
    ys2  = np.linspace(0, 1, res2)
    xx2, yy2 = np.meshgrid(xs2, ys2)
    zz2 = np.vectorize(lambda a, b: _predict_nn(a, b, weights, biases))(xx2, yy2)

    ax2.contourf(xx2, yy2, zz2, levels=[-0.5, 0.5, 1.5],
                 colors=[NEON_PINK + "50", NEON_BLUE + "50"], zorder=0)
    ax2.contour(xx2, yy2, zz2, levels=[0.5], colors=[NEON_YLW],
                linewidths=2, linestyles="--", zorder=2)
    _plot_truth_points(ax2, gate_name)

    # legend patches
    from matplotlib.patches import Patch
    legend_els = [Patch(facecolor=NEON_PINK + "80", label="output = 0"),
                  Patch(facecolor=NEON_BLUE + "80", label="output = 1")]
    ax2.legend(handles=legend_els, fontsize=8, labelcolor="white",
               facecolor=PANEL, edgecolor=DIM, loc="upper left")

    plt.tight_layout()
    plt.show(block=False)


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC ENTRY POINT  – called from all_gates.py
# ─────────────────────────────────────────────────────────────────────────────
def plot_gate(gate_name, weights, biases, gate_kind):
    """
    gate_name  : str   e.g. "AND", "XOR"
    weights    : returned by the gate training function
    biases     : returned by the gate training function
    gate_kind  : "basic"  →  perceptron plot
                 "nn"     →  neural-network heatmap
    """
    if gate_kind == "basic":
        plot_perceptron(gate_name, weights, biases)
    else:
        plot_nn(gate_name, weights, biases)