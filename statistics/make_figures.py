"""Paper figures 1-8 (CLAUDE.md step 35), generated from saved results only.

    python statistics/make_figures.py

Figures 1-2 are diagrams of the method (no data). Figures 3-8 read results/summaries/*.json;
error bars are the 95 % CIs stored there. Writes figures/fig{1..8}_*.png (200 dpi) and .pdf.

Colour follows the system in every figure: proposed blue, baseline orange, ablation aqua
(slots 1-3 of the reference palette, validated for all pairs on a light surface). Text is
never in a series colour.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SUMMARIES = ROOT / "results" / "summaries"
FIGURES = ROOT / "figures"
DOMAINS = ("pharma", "energy")
COLOR = {"proposed": "#2a78d6", "baseline": "#eb6834", "ablation": "#1baf7a"}
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#ffffff"
BOX, BOX_EDGE, ACCENT_FILL = "#f4f3f0", "#c9c8c2", "#e3eefb"
LABEL = {"fidelity": "Fidelity F", "evidence_support": "Evidence support E",
         "manipulation": "Manipulation M", "collective_accuracy": "Collective accuracy"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10,
    "axes.labelsize": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "axes.linewidth": 0.8, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "legend.frameon": False,
    "text.color": INK, "savefig.facecolor": SURFACE})


def load(name):
    return json.loads((SUMMARIES / f"{name}.json").read_text())


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote figures/{name}.png/.pdf")


def err(d):
    return [[d["mean"] - d["ci_low"]], [d["ci_high"] - d["mean"]]]


# --- diagrams ------------------------------------------------------------------------

def box(ax, x, y, w, h, text, accent=False, size=8.5):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=ACCENT_FILL if accent else BOX,
                                ec=COLOR["proposed"] if accent else BOX_EDGE, lw=1.0))
    ax.text(x, y, text, ha="center", va="center", fontsize=size, color=INK, wrap=True)


def arrow(ax, a, b, text=None, rad=0.0, offset=(0, 0.12)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, lw=1.0,
                                 color=INK2, connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=2, shrinkB=2))
    if text:
        ax.text((a[0] + b[0]) / 2 + offset[0], (a[1] + b[1]) / 2 + offset[1], text,
                ha="center", va="center", fontsize=7.5, color=INK2)


def blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")


def fig1_architecture():
    fig, ax = plt.subplots(figsize=(10.6, 3.6))
    blank(ax, (0, 10.6), (0, 3.6))
    top = [("Real dataset\n(SCMS / OptiREC)", False), ("Deterministic\npreprocessing", False),
           ("Scenarios\n(constructed\nreference)", False), ("5 specialised\nagents (RF / LLM)", False),
           ("Game: strategy\nchoice and vote", False)]
    bottom = [("Collective\ndecision", False), ("SHAP\nexplanations", False),
              ("Fidelity, evidence,\nconsistency", False),
              ("Explanation-aware\nutility → reward", True), ("Reputation\n(vote weight)", True)]
    xs = [1.0 + 2.0 * i for i in range(5)]
    for x, (t, acc) in zip(xs, top):
        box(ax, x, 2.8, 1.7, 0.8, t, acc)
    for x, (t, acc) in zip(xs, bottom):
        box(ax, x, 1.45, 1.7, 0.8, t, acc)
    for a, b in zip(xs, xs[1:]):
        arrow(ax, (a + 0.85, 2.8), (b - 0.85, 2.8))
        arrow(ax, (a + 0.85, 1.45), (b - 0.85, 1.45))
    arrow(ax, (xs[-1] - 0.5, 2.4), (xs[0] + 0.2, 1.85), "votes", offset=(0, 0.13))
    arrow(ax, (xs[-1], 1.85), (xs[-1], 2.4), "weights next\nround's votes", offset=(0.75, 0))
    box(ax, 5.0, 0.35, 8.6, 0.5,
        "Provenance: SHA-256 of decision, explanation, evidence + reward, reputation on a "
        "local chain → VALID / TAMPERED", accent=False, size=8)
    for x in xs[2:]:
        arrow(ax, (x, 1.05), (x, 0.62))
    ax.text(0.0, 3.5, "Shaded blue: components only the proposed system has (ablation: utility "
            "only). Blockchain records integrity, not truth.", fontsize=7.5, color=INK2)
    save(fig, "fig1_architecture")


def fig2_mechanism():
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    blank(ax, (0, 9.6), (0, 4.2))
    comps = [("D  decision quality", "α 0.30"), ("F  explanation fidelity", "β 0.25"),
             ("E  evidence support", "γ 0.15"), ("C  cooperation", "δ 0.10"),
             ("M  manipulation", "−λ 0.20")]
    for i, (t, w) in enumerate(comps):
        y = 3.7 - 0.62 * i
        box(ax, 1.25, y, 2.2, 0.48, t, size=8)
        arrow(ax, (2.35, y), (3.55, 2.46))
        ax.text(2.42, y + 0.14, w, fontsize=7.5, color=INK2, ha="left", va="center")
    box(ax, 4.3, 2.46, 1.5, 0.75, "U = αD + βF + γE\n+ δC − λM", accent=True, size=8)
    box(ax, 6.3, 3.35, 1.7, 0.7, "R = (U − U_min) /\n(U_max − U_min)", accent=True, size=8)
    box(ax, 8.0, 2.46, 1.6, 0.75, "Rep ← ρ·Rep\n+ (1 − ρ)·R", accent=True, size=8)
    box(ax, 6.3, 1.0, 2.6, 0.7, "payoff = ω · private utility\n+ (1 − ω) · R", size=8)
    box(ax, 3.0, 0.45, 2.4, 0.6, "agent learns a strategy\n(ε-greedy bandit)", size=8)
    arrow(ax, (5.05, 2.65), (5.45, 3.2))
    arrow(ax, (7.15, 3.2), (7.6, 2.85))
    arrow(ax, (6.3, 3.0), (6.3, 1.35), "relative\nreward", offset=(0.42, 0))
    arrow(ax, (5.0, 0.85), (4.2, 0.55))
    arrow(ax, (8.0, 2.08), (7.6, 1.35), "vote weight → decision\n→ private utility", offset=(0.95, 0.05))
    ax.text(0.15, 0.02, "Weights frozen in the protocol (§7); R = 0.5 when all U are equal; "
            "ρ 0.8; ω 0.5. Baseline: U = 0.75·D + 0.25·C, no reputation.",
            fontsize=7.5, color=INK2)
    save(fig, "fig2_mechanism")


# --- data figures --------------------------------------------------------------------

def dodge_points(ax, groups, series, get, xlabels):
    width = 0.22
    for j, s in enumerate(series):
        for i, g in enumerate(groups):
            d = get(g, s)
            x = i + (j - (len(series) - 1) / 2) * width
            ax.errorbar(x, d["mean"], yerr=err(d), fmt="o", ms=5, color=COLOR[s],
                        ecolor=COLOR[s], elinewidth=1.4, capsize=0,
                        label=s if i == 0 else None)
    ax.set_xticks(range(len(groups)), xlabels)
    ax.grid(axis="x", visible=False)


def fig3_explanation_quality():
    systems = ("baseline", "ablation", "proposed")
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.6), sharey="col")
    for r, (arm, name) in enumerate((("classical", "main"), ("llm", "llm"))):
        data = {d: (load(f"{d}_main") if arm == "classical" else load(f"{d}_llm")["main"])
                ["descriptive"] for d in DOMAINS}
        for c, m in enumerate(("fidelity", "evidence_support", "manipulation")):
            ax = axes[r, c]
            dodge_points(ax, DOMAINS, systems, lambda g, s: data[g][m][s], DOMAINS)
            ax.set_ylim(0, 1)
            if r == 0:
                ax.set_title(LABEL[m] + ("  (lower is better)" if m == "manipulation" else ""),
                             loc="left")
            if c == 0:
                ax.set_ylabel(f"{'Classical (n = 10)' if arm == 'classical' else 'LLM (n = 5)'}"
                              "\nmean, 95% CI")
    axes[0, 0].legend(loc="lower left", fontsize=8)
    fig.suptitle("Explanation quality by system and domain", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    save(fig, "fig3_explanation_quality")


def share_lines(ax, adv, metric):
    """Mean line with 95 % CI band per system; returns the line ends for label_ends()."""
    fr = adv["fractions"]
    xs = [100 * float(f) for f in fr]
    ends = []
    for s in adv["systems"]:
        d = adv["descriptive"][metric][s]
        mean = [d[f]["mean"] for f in fr]
        ax.fill_between(xs, [d[f]["ci_low"] for f in fr], [d[f]["ci_high"] for f in fr],
                        color=COLOR[s], alpha=0.12, lw=0)
        ax.plot(xs, mean, color=COLOR[s], lw=1.6, marker="o", ms=4.5,
                markeredgecolor=SURFACE, markeredgewidth=1.0, label=s)
        ends.append((s, xs[-1], mean[-1]))
    ax.set_xticks(xs, [f"{x:.0f}%" for x in xs])
    ax.set_xlim(-2, 48)
    return ends


def label_ends(ax, ends, min_gap_px=11):
    """Direct labels at the line ends, pushed apart vertically so they never overlap.
    Call after the axis limits and layout are final."""
    to_px = ax.transData.transform
    placed = sorted(((to_px((x, y))[1], s, x, y) for s, x, y in ends))
    ys = [p[0] for p in placed]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + min_gap_px)
    for (py, s, x, y), ny in zip(placed, ys):
        ax.annotate(s, (x, y), xytext=(6, ny - py), textcoords="offset points",
                    va="center", fontsize=8, color=INK2)


def fig4_quality_vs_malicious():
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex=True, sharey=True)
    ends = {}
    for r, d in enumerate(DOMAINS):
        adv = load(f"{d}_adversarial")
        for c, m in enumerate(("fidelity", "evidence_support")):
            ax = axes[r, c]
            ends[(r, c)] = share_lines(ax, adv, m)
            ax.set_ylim(0, 1)
            ax.set_title(f"{d} — {LABEL[m]}", loc="left")
            if c == 0:
                ax.set_ylabel("mean, 95% CI band")
    for ax in axes[1]:
        ax.set_xlabel("share of malicious agents")
    fig.suptitle("Explanation quality as the malicious-agent share rises (classical, n = 10)",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    for (r, c), e in ends.items():
        label_ends(axes[r, c], e)
    save(fig, "fig4_quality_vs_malicious")


def fig5_decision_vs_malicious():
    final = load("final_statistics")["H4"]["classical"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharex=True)
    ends = []
    for ax, d in zip(axes, DOMAINS):
        adv = load(f"{d}_adversarial")
        ends.append((ax, share_lines(ax, adv, "collective_accuracy")))
        h4 = final[d]
        ax.set_title(f"{d}: H4 {h4['verdict']} (Δ degradation {h4['mean_difference']:+.3f}, "
                     f"p {h4['p_value']:.2f})", loc="left", fontsize=9)
        ax.set_xlabel("share of malicious agents")
    axes[0].set_ylabel("collective accuracy\n(vs constructed reference)")
    fig.suptitle("Decision performance as the malicious-agent share rises (classical, n = 10)",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    for ax, e in ends:
        label_ends(ax, e)
    save(fig, "fig5_decision_vs_malicious")


def fig6_ablation():
    outcomes = ("fidelity", "evidence_support", "manipulation")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
    for ax, d in zip(axes, DOMAINS):
        comps = load(f"{d}_main")["comparisons"]
        for j, (key, s) in enumerate((("ablation_vs_baseline", "ablation"),
                                      ("proposed_vs_baseline", "proposed"))):
            for i, m in enumerate(outcomes):
                c = comps[key][m]
                y = i + (0.15 if j == 0 else -0.15)
                ax.errorbar(c["mean_difference"], y,
                            xerr=[[c["mean_difference"] - c["ci_low"]],
                                  [c["ci_high"] - c["mean_difference"]]],
                            fmt="o", ms=5, color=COLOR[s], elinewidth=1.4, capsize=0,
                            label=f"{s} − baseline" if i == 0 else None)
                ax.annotate(c["verdict"], (c["ci_high"], y), xytext=(4, 0),
                            textcoords="offset points", va="center", fontsize=7.5, color=INK2)
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_yticks(range(3), [LABEL[m] for m in outcomes])
        ax.grid(axis="y", visible=False)
        ax.set_title(d, loc="left")
        ax.set_xlabel("difference from baseline, 95% CI")
        ax.margins(x=0.25)
    axes[0].invert_yaxis()  # shared y: invert once
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, fontsize=8,
               bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Incentive ablation: the incentive alone vs incentive + reputation "
                 "(classical, n = 10)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    save(fig, "fig6_ablation")


def fig7_tampering():
    prov = load("provenance")
    ver = {k: v for k, v in prov["verification"].items() if isinstance(v, dict)}
    tampered = [g for g in prov["detection_rate"]]
    controls = [g for g in ver if g not in tampered]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    rows = tampered + controls
    for i, g in enumerate(rows):
        v = ver[g]
        n = sum(v.values())
        flagged = v["TAMPERED"] / n
        tampered_group = g in tampered
        ax.barh(i, flagged, height=0.6, color=COLOR["proposed"] if tampered_group else MUTED)
        what = ("detected" if tampered_group else
                "change < 10⁻⁶, undetectable by design" if g == "below_resolution"
                else "false positives")
        ax.annotate(f"{v['TAMPERED']:,} / {n:,} flagged ({what})", (max(flagged, 0), i),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=7.5,
                    color=INK2)
    ax.set_yticks(range(len(rows)), [r.replace("_", " ") for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 1.45)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("share of records flagged TAMPERED")
    ax.set_title(f"Tamper detection on {prov['records']:,} chain records (blue: tampered "
                 "targets; gray: unchanged controls). Below-resolution changes (< 10⁻⁶) are "
                 "invisible by design.", loc="left", fontsize=8.5, wrap=True)
    fig.tight_layout()
    save(fig, "fig7_tampering")


def fig8_cross_domain():
    cross = load("cross_domain")
    outcomes = ("fidelity", "evidence_support", "manipulation")
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), sharex=True)
    for ax, (arm, title) in zip(axes, (("classical", "Classical (n = 10)"),
                                       ("llm", "LLM (n = 5)"))):
        c = cross["arms"][arm]["comparisons"]["proposed_vs_baseline"]["outcomes"]
        labels, y = [], 0
        ax.axvspan(-5, 5, color=GRID, alpha=0.6, lw=0)
        for m in outcomes:
            for d in DOMAINS:
                row = c[m][d]
                sign = -1 if m == "manipulation" else 1
                val = 100 * sign * row["relative_improvement"]
                ax.barh(y, val, height=0.62, color=COLOR["proposed"])
                ax.annotate(row["verdict"], (max(val, 0), y), xytext=(4, 0),
                            textcoords="offset points", va="center", fontsize=7.5, color=INK2)
                labels.append(f"{LABEL[m].split(' ')[-1]} · {d}")
                y += 1
            y += 0.4
        ticks = [i + 0.4 * (i // 2) for i in range(6)]
        ax.set_yticks(ticks, labels)
        ax.invert_yaxis()
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.grid(axis="y", visible=False)
        ax.set_title(title, loc="left")
        ax.set_xlabel("improvement over baseline (%)")
    axes[1].set_xlim(right=max(axes[0].get_xlim()[1], 100))
    fig.suptitle("Cross-domain comparison (H6): relative improvement, proposed vs baseline. "
                 "M plotted as reduction; gray band = ±5 % threshold", x=0.01, ha="left",
                 fontsize=10)
    fig.tight_layout()
    save(fig, "fig8_cross_domain")


BUILDERS = (fig1_architecture, fig2_mechanism, fig3_explanation_quality,
            fig4_quality_vs_malicious, fig5_decision_vs_malicious, fig6_ablation,
            fig7_tampering, fig8_cross_domain)


def main():
    FIGURES.mkdir(exist_ok=True)
    for build in BUILDERS:
        build()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
