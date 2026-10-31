"""LaTeX tables for the manuscript, generated from results/summaries/ (no typed numbers).

    python paper/make_paper_tables.py

Writes paper/tables/tab_*.tex (booktabs). Same sources as statistics/make_tables.py, in a
compact form that fits the journal page.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "results" / "summaries"
OUT = Path(__file__).resolve().parent / "tables"
DOMAINS = ("pharma", "energy")
CONF = ("fidelity", "evidence_support", "manipulation")
NAME = {"fidelity": "Fidelity $F$", "evidence_support": "Evidence support $E$",
        "manipulation": "Manipulation $M$", "collective_accuracy": "Collective accuracy",
        "manipulation_success": "Manipulation success", "consistency": "Consistency"}


def load(name):
    return json.loads((S / f"{name}.json").read_text())


def p(x):
    return "$<0.0001$" if x < 0.0001 else f"{x:.4f}"


def pct(x):
    return f"{100 * x:+.1f}\\%"


def ms(d):
    return f"{d['mean']:.3f} $\\pm$ {d['sd']:.3f}"


def ci(c):
    return f"{c['mean_difference']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]"


def table(label, caption, colspec, header, rows, note=None, wide=False):
    env = "table*" if wide else "table"
    lines = [f"\\begin{{{env}}}[t]", f"\\caption{{{caption}}}\\label{{{label}}}",
             "\\footnotesize", f"\\begin{{tabular}}{{{colspec}}}", "\\toprule",
             header + " \\\\", "\\midrule"]
    for r in rows:
        lines.append("\\midrule" if r == "MID" else " & ".join(r) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    if note:
        lines.append(f"\\footnotetext{{{note}}}")
    lines.append(f"\\end{{{env}}}")
    return "\n".join(lines) + "\n"


def tab_datasets():
    ph = json.loads((ROOT / "data/processed/pharma/scenarios_meta.json").read_text())
    en = json.loads((ROOT / "data/processed/energy/scenarios_meta.json").read_text())
    sp, se = ph["split_counts"], en["split_counts"]
    b = en["constructed_reference"]["simulated_battery_parameters"]
    rows = [
        ["Source", "USAID/PEPFAR SCMS delivery history \\citep{scmsdata2015}",
         "OptiREC energy community \\citep{optirecdata2025}"],
        ["Scenario", "one purchase order, three candidate sites", "one hour of the community"],
        ["Scenarios", f"{ph['n_scenarios']:,} ({ph['n_products']} products, {ph['n_sites']} sites)",
         f"{sum(se.values()):,}"],
        ["Train / val / test", f"{sp['train']} / {sp['val']} / {sp['test']} (by order date)",
         f"{se['train']:,} / {se['val']:,} / {se['test']:,} (week blocks)"],
        ["Agents", "cost, reliability, lead time, logistics, continuity",
         "producer, consumer, market, grid, storage"],
        ["Reference decision", "equal-weight multi-criteria score (constructed)",
         "daily perfect-foresight LP (constructed)"],
        ["Simulated inputs", "candidate set", f"battery: C-rate {b['c_rate']}, "
                                              f"efficiency {b['round_trip_efficiency']}"],
        ["Derived variables", f"{len(ph['derived_columns'])}", f"{len(en['derived_columns'])}"],
    ]
    return table("tab:data", "Case studies, scenarios and preprocessing", "@{}lp{5.2cm}p{5.2cm}@{}",
                 " & Pharmaceutical & Energy", rows, wide=True)


def tab_main():
    rows = []
    for d in DOMAINS:
        m = load(f"{d}_main")
        for k in CONF + ("collective_accuracy", "manipulation_success"):
            c = m["comparisons"]["proposed_vs_baseline"][k]
            conf = k in CONF
            rows.append([d if k == "fidelity" else "", NAME[k],
                         ms(m["descriptive"][k]["baseline"]), ms(m["descriptive"][k]["proposed"]),
                         ci(c), pct(c["relative_improvement"]),
                         p(c["p_holm"] if conf else c["p_value"]) + ("" if conf else "$^{a}$"),
                         c.get("verdict") or "--"])
        if d == "pharma":
            rows.append("MID")
    return table("tab:main", "Baseline vs proposed, classical agents ($n=10$ paired seeds; mean "
                 "$\\pm$ SD). Verdicts: pre-registered rule (Holm $p<0.05$ in the hypothesised "
                 "direction and $|\\mathrm{rel.}|\\geq 5\\%$)",
                 "@{}llllllll@{}",
                 "Domain & Metric & Baseline & Proposed & $\\Delta$ [95\\% CI] & Rel. & $p$ (Holm) & Verdict",
                 rows, note="$^{a}$Secondary outcome, unadjusted $p$, no verdict.", wide=True)


def tab_ablation():
    rows = []
    for d in DOMAINS:
        m = load(f"{d}_main")
        for k in CONF:
            a = m["comparisons"]["ablation_vs_baseline"][k]
            de = m["descriptive"][k]
            rows.append([d if k == "fidelity" else "", NAME[k], pct(a["relative_improvement"]),
                         p(a["p_holm"]), a["verdict"],
                         f"{de['proposed']['mean'] - de['ablation']['mean']:+.3f}"])
    return table("tab:ablation", "Incentive ablation (incentive without reputation) vs baseline, "
                 "and the descriptive increment of reputation (proposed $-$ ablation)",
                 "@{}llllll@{}", "Domain & Metric & Rel. & $p$ (Holm) & Verdict & Reputation increment",
                 rows)


def tab_robust():
    fin = load("final_statistics")["H4"]["classical"]
    rows = []
    for d in DOMAINS:
        h = fin[d]
        adv = load(f"{d}_adversarial")
        col = adv["collusion"]
        rows.append([d, f"{h['mean_difference']:+.3f} [{h['ci_low']:+.3f}, {h['ci_high']:+.3f}]",
                     p(h["p_value"]), h["verdict"],
                     f"{col['baseline']['manipulation_success']['mean_difference']:+.3f} / "
                     f"{col['proposed']['manipulation_success']['mean_difference']:+.3f}",
                     f"{col['proposed']['colluders_reward']['mean_difference']:+.3f}"])
    return table("tab:robust", "Robustness. H4: mean accuracy degradation over 10--40\\% malicious "
                 "agents, proposed $-$ baseline (negative = proposed degrades less; paired $t$-test). "
                 "Collusion: change in manipulation success (baseline / proposed) and in the "
                 "colluders' reward under the proposed system when two agents collude (unadjusted)",
                 "@{}llllll@{}",
                 "Domain & H4 $\\Delta$ [95\\% CI] & $p$ & Verdict & Collusion: manip. success & Colluders' reward",
                 rows, wide=True)


def tab_provenance():
    pr = load("provenance")
    v = pr["verification"]
    rows = []
    for g in ("decision", "explanation", "evidence", "reward", "reputation"):
        rows.append([g, f"{v[g]['TAMPERED']} / {sum(v[g].values())}", "detected"])
    for g, label in (("control_untouched", "untouched controls"),
                     ("control_reserialised", "re-serialised controls"),
                     ("all_untouched", "all other records")):
        rows.append([label, f"{v[g]['TAMPERED']} / {sum(v[g].values()):,}", "false positives"])
    rows.append(["below $10^{-6}$ resolution", f"{v['below_resolution']['TAMPERED']} / "
                 f"{sum(v['below_resolution'].values())}", "not detectable by design"])
    o = pr["overhead"]["100"]
    note = (f"Local node, {pr['records']:,} records. Batches of 100: "
            f"{o['gas_per_record']:,.0f} gas per record, "
            f"{1000 * o['verify_seconds_per_record']:.1f} ms verification per record; "
            f"{pr['onchain_storage_bytes_per_record']} bytes on-chain per record.")
    return table("tab:provenance", "Tamper detection on the provenance layer (H5)", "@{}lll@{}",
                 "Group & Flagged TAMPERED & Meaning", rows, note=note)


def tab_hardened():
    hr = load("provenance_hardened")
    h, rw, f = hr["honest"], hr["rewrite_hardened"], hr["forgery"]
    names = {"content_changed_after_signing": "content changed after signing",
             "other_agents_key": "signed with another agent's key",
             "unregistered_key": "signed with an unregistered key",
             "replay_other_record_id": "replayed under another record id",
             "replay_other_deployment": "replayed from another deployment",
             "model_substituted": "substituted model",
             "non_owner_sender": "sent by a non-owner account"}
    rows = [["\\multicolumn{2}{@{}l}{\\emph{Forged or replayed writes (refused by the "
             "contract)}}"]]
    rows += [[label, f"{f[k]['accepted']} / {f[k]['attempts']} accepted"]
             for k, label in names.items()]
    rows.append(["correctly signed (control)", f"{f['valid_control']['accepted']} / "
                 f"{f['valid_control']['attempts']} accepted"])
    rows += ["MID", ["\\multicolumn{2}{@{}l}{\\emph{History rebuilt by the operator}}"],
             ["altered records, amendment-5 check",
              f"{hr['rewrite_amendment5']['TAMPERED']} / {rw['altered']} detected"],
             ["registrations against anchor", f"{rw['registrations_mismatched']} / "
              f"{rw['registrations']} differ"],
             ["altered records against anchor", f"{rw['altered_detected_by_anchor']} / "
              f"{rw['altered']} detected"],
             ["unaltered records against anchor", f"{rw['unaltered_flagged']} / "
              f"{rw['unaltered']:,} flagged"],
             "MID", ["\\multicolumn{2}{@{}l}{\\emph{Honest run}}"],
             ["records, registrations, anchors", f"{h['per_record']['TAMPERED']} tampered, "
              f"{h['registrations_mismatched']} + {h['anchors_mismatched']} mismatches"]]
    o, a = hr["overhead"]["batches"]["100"], hr["overhead"]["anchor"]
    note = (f"Local nodes, {hr['records']:,} records; the anchor chain is a second local node "
            f"standing in for an external chain. Batches of 100: {o['gas_per_record']:,.0f} gas "
            f"per record (amendment 5: {load('provenance')['overhead']['100']['gas_per_record']:,.0f}); "
            f"anchoring {a['anchor_gas'] / a['leaves']:,.0f} gas per record; inclusion proof "
            f"{a['proof_bytes_median']:.0f} bytes.")
    return table("tab:hardened", "Hardened provenance: agent signatures, model registration "
                 "and anchoring (amendment 9, descriptive)", "@{}ll@{}", "Check & Result", rows,
                 note=note)


def tab_cross():
    cr = load("cross_domain")["arms"]
    rob = load("sensitivity_robustness")["runs"]
    rows = []
    for arm, label in (("classical", "Classical"), ("llm", "LLM")):
        c = cr[arm]["comparisons"]["proposed_vs_baseline"]
        for k in CONF:
            o = c["outcomes"][k]
            rows.append([label if k == "fidelity" else "", NAME[k],
                         f"{pct(o['pharma']['relative_improvement'])} ({o['pharma']['verdict']})",
                         f"{pct(o['energy']['relative_improvement'])} ({o['energy']['verdict']})",
                         "yes" if c["h6"][k]["same_verdict"] else "no"])
    rows.append("MID")
    for d in DOMAINS:
        bad = ["$\\" + n.split("_")[-1] + "$: "
               + ", ".join(k.split("_")[0] for k in CONF if not r["robust"][k])
               for n, r in rob.items() if n.startswith(d) and not all(r["robust"].values())]
        rows.append([f"Sensitivity ({d})", "verdicts changed", "\\multicolumn{3}{l}{"
                     + ("; ".join(bad) if bad else "none (all values of $\\beta$, $\\rho$, $\\omega$)")
                     + "}"])
    return table("tab:cross", "Cross-domain comparison (H6: same verdict in both domains) and "
                 "robustness of the classical verdicts across $\\beta$, $\\rho$ and $\\omega$",
                 "@{}lllll@{}", "Agents & Outcome & Pharmaceutical & Energy & Same verdict",
                 rows, wide=True)


def tab_llm():
    rows = []
    for d in DOMAINS:
        f = load(f"{d}_llm_factorial")
        e = f["effects"]["mean_confidence"]
        for k in ("wording", "payoff", "interaction"):
            c = next(v for name, v in e.items() if name.startswith(k))
            rows.append([d if k == "wording" else "", k,
                         f"{c['mean_difference']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]",
                         p(c["p_holm"]), c["verdict"]])
    return table("tab:llm", "LLM agents: 2$\\times$2 wording $\\times$ payoff experiment on mean "
                 "stated confidence ($n=5$ seeds; Holm over the three effects; added after the "
                 "main analysis)", "@{}lllll@{}",
                 "Domain & Effect & $\\Delta$ [95\\% CI] & $p$ (Holm) & Verdict", rows)


def main():
    OUT.mkdir(exist_ok=True)
    for build in (tab_datasets, tab_main, tab_ablation, tab_robust, tab_provenance, tab_hardened,
                  tab_cross,
                  tab_llm):
        name = build.__name__
        (OUT / f"{name}.tex").write_text(build(), encoding="utf-8")
        print(f"wrote paper/tables/{name}.tex")


if __name__ == "__main__":
    main()
