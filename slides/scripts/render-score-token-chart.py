# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.9,<4"]
# ///
"""Render the evaluation overview and its Summary thumbnail.

Run: uv run slides/scripts/render-score-token-chart.py
Source: docs/FINAL_REPORT.md, section 5.3 (whole-system input + output,
including cache-read). Ranges are accounting bounds, not confidence intervals.
The static assets are checked in; building the deck does not require Python.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides/public/assets"
SETUPS = [
    {"id": "gemini", "name": "Direct Gemini", "tokens": 8_564_976, "score": 0.6045803, "color": "#5d7fbd", "detail": "8.565M · 0.6045803"},
    {"id": "luna", "name": "Direct GPT Luna", "tokens": 28_069_574, "score": 0.6046, "color": "#e98238", "detail": "28.070M · ≈0.6046 · provisional"},
    {"id": "heterogeneous", "name": "Heterogeneous", "tokens": 39_607_277, "score": 0.6047, "color": "#df7328", "detail": "39.607M · ≈0.6047"},
    {"id": "antigravity", "name": "SciOdyssey + Antigravity", "tokens": (45_043_916 + 51_173_911) / 2, "score": 0.6052, "color": "#a66cff", "detail": "45.044–51.174M · 0.6052"},
    {"id": "submission", "name": "SciOdyssey submission", "tokens": 48_240_128, "score": 0.6059363, "color": "#16803b", "detail": "48.240M · 0.6059363 · verified"},
]
TOKEN_RANGE = (45_043_916 / 1e6, 51_173_911 / 1e6)
REFERENCE_SCORE = 0.6016

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "text.color": "#424b58",
    "axes.labelcolor": "#747f8d",
    "xtick.color": "#8a929d",
    "ytick.color": "#8a929d",
    "svg.fonttype": "path",
    "svg.hashsalt": "sciodyssey-score-token-overview",
})


def draw_points(ax, thumbnail=False):
    ax.hlines(0.6052, *TOKEN_RANGE, color="#a66cff", linewidth=2.1, zorder=3)
    ax.vlines(TOKEN_RANGE, 0.6052 - 0.00006, 0.6052 + 0.00006, color="#a66cff", linewidth=1.3, zorder=3)
    for setup in SETUPS:
        x, y = setup["tokens"] / 1e6, setup["score"]
        retained = setup["id"] == "submission"
        if retained:
            ax.scatter(x, y, s=460 if not thumbnail else 190, color=setup["color"], alpha=0.08, linewidths=0, zorder=3)
        ax.scatter(x, y, s=(155 if retained else 80) if not thumbnail else (70 if retained else 38), color=setup["color"], edgecolor="white", linewidth=1.7, zorder=4)


fig, ax = plt.subplots(figsize=(12.5, 4.85), dpi=160)
fig.subplots_adjust(left=0.079, right=0.978, top=0.93, bottom=0.155)
fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax.set_xlim(0, 55)
ax.set_ylim(0.6014, 0.6067)
ax.set_xticks([0, 10, 20, 30, 40, 50, 55])
ax.set_yticks([0.602, 0.603, 0.604, 0.605, 0.606])
ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
ax.grid(color="#e9edf1", linewidth=0.7, alpha=0.8)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis="both", length=0, pad=9, labelsize=9.5)
ax.set_xlabel("Total LLM tokens (millions)", fontsize=10, labelpad=13)
ax.text(0, 1.035, "Public-validation Primary ↑", transform=ax.transAxes, color="#747f8d", fontsize=9.5, va="bottom")
ax.axhline(REFERENCE_SCORE, color="#bfc7cf", linewidth=1.0, linestyle=(0, (5, 5)), zorder=2)
ax.annotate("Official reference · 0.6016", (1.2, REFERENCE_SCORE), xytext=(0, 6), textcoords="offset points", color="#8a929d", fontsize=9, va="bottom")
draw_points(ax)

# Label positions are offset in display points to retain legible spacing.
placements = {
    "gemini": (10, 23, "left"),
    "luna": (10, 23, "left"),
    "heterogeneous": (-10, -25, "right"),
    "antigravity": (-11, 23, "right"),
    "submission": (-11, 23, "right"),
}
for setup in SETUPS:
    dx, dy, align = placements[setup["id"]]
    xy = (setup["tokens"] / 1e6, setup["score"])
    color = setup["color"] if setup["id"] == "submission" else "#424b58"
    ax.annotate(setup["name"], xy, xytext=(dx, dy), textcoords="offset points", ha=align, va="bottom", fontsize=11, color=color, zorder=5)
    ax.annotate(setup["detail"], xy, xytext=(dx, dy - 13), textcoords="offset points", ha=align, va="bottom", fontsize=8.7, color="#738092", zorder=5)

ASSETS.mkdir(parents=True, exist_ok=True)
fig.savefig(ASSETS / "score-token-comparison.svg", transparent=True, metadata={
    "Title": "Scores and token usage",
    "Description": "Public-validation Primary versus whole-system input and output tokens including cache-read. Five distinct configurations, not an equal-budget comparison. Purple interval: 45.044–51.174M token accounting bounds. Source: docs/FINAL_REPORT.md section 5.3.",
    "Date": None,
})
fig.savefig(ASSETS / "score-token-comparison.png", transparent=True, dpi=180)
plt.close(fig)

# Compact view of the same five points for the existing Summary card.
fig, ax = plt.subplots(figsize=(6.5, 1.2), dpi=180)
fig.subplots_adjust(left=0.025, right=0.975, top=0.88, bottom=0.12)
ax.set_xlim(0, 55)
ax.set_ylim(0.60415, 0.60625)
ax.axis("off")
draw_points(ax, thumbnail=True)
(ASSETS / "summary").mkdir(exist_ok=True)
fig.savefig(ASSETS / "summary/scores-tokens.png", facecolor="white", dpi=180)
plt.close(fig)
print("Rendered score-token-comparison.svg, score-token-comparison.png and summary/scores-tokens.png")
