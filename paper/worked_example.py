"""Worked example for the manuscript: one real round of the pharma proposed run (seed 0).

    python paper/worked_example.py

Replays `pharma_proposed` seed 0 (deterministic), checks that the replay reproduces the saved
metrics, and picks, by a fixed rule, the first evaluation round in which a learning agent
played *manipulative* while its preferred site differed from both its model's vote and the
reference (a conflict of interest, the case the mechanism targets). For that agent it scores
two reports in the same round, everything else held fixed: the honest report and the
manipulative one, each paid by the proposed and by the baseline utility. Because one round is
an illustration, the same honest-versus-manipulative comparison is also made for every agent
in every evaluation round (others' reports as played), as a representative summary. Writes
results/summaries/worked_example.json and paper/tables/tab_example.tex. No number is typed.
"""
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import collective_decision, contributions, observed_level  # noqa: E402
from experiments.core import simulate, summarise  # noqa: E402
from experiments.pharma import prepare  # noqa: E402
from game.strategies import STRATEGIES, build_report_content, choose_report  # noqa: E402
from incentives.mechanism import (  # noqa: E402
    ATTACKS, manipulation_components, manipulation_score, reward, utility, validate_weights)

LABEL = {"exp_unit_price": "expected unit price", "price_rel": "price relative to candidates",
         "last_price_rel": "last price (relative)", "price_cv": "price variability",
         "log_order_units": "order size", "ontime_rate": "on-time rate",
         "ontime_rel": "on-time rate (relative)", "mean_late_days": "mean days late",
         "log_n_lines": "past deliveries", "late_last5": "late in last five",
         "median_lead_days": "median lead time", "lead_rel": "lead time (relative)",
         "lead_iqr": "lead-time spread", "log_n_lead": "lead-time records",
         "requested_lead_days": "requested lead time", "freight_per_kg": "freight per kg",
         "freight_rel": "freight (relative)", "share_air": "share by air",
         "share_freight_included": "share freight included",
         "log_n_country_lines": "deliveries to country",
         "log_n_product_lines": "deliveries of product", "product_share": "product share",
         "days_since_last": "days since last delivery", "n_countries": "countries served",
         "log_units_supplied": "units supplied"}


def report(prep, t, i, strategy):
    """(vote, confidence, explanation, claims, style) of agent i in round t."""
    game, audit = prep["game"], prep["audit"][i]
    vote, conf, style = choose_report(strategy, prep["proba"][t, i], prep["preferred"][t, i],
                                      prep["utilities"][t, i], game["deviation_threshold"],
                                      game["inflation"])
    explanation, claims = build_report_content(style, audit["phi"][t, vote], audit["X"][t, vote],
                                               audit["thresholds"], game["top_k"])
    return vote, conf, explanation, claims, style


def score_round(prep, t, strategies, weights, vote_weights):
    """The per-round computation of `experiments.core.simulate`, for given strategies."""
    n = len(strategies)
    proba = prep["proba"][t]
    votes, conf, F, E = np.zeros(n, dtype=int), np.zeros(n), np.zeros(n), np.zeros(n)
    for i, s in enumerate(strategies):
        vote, c, _, _, style = report(prep, t, i, s)
        votes[i], conf[i] = vote, c
        F[i] = prep["quality"][style]["F"][t, i, vote]
        E[i] = prep["quality"][style]["E"][t, i, vote]
    n_actions = proba.shape[1]
    decision = collective_decision(votes, conf, vote_weights, n_actions)
    ref = prep["reference"][t]
    D = (votes == ref).astype(float)
    C = contributions(votes, conf, vote_weights, n_actions, ref)
    comp = manipulation_components(F, E, conf, proba[np.arange(n), votes], votes,
                                   proba.argmax(axis=1))
    M = manipulation_score(comp)
    U = utility(D, F, E, C, M, weights)
    R = reward(U, 0.5)
    private = prep["utilities"][t][np.arange(n), decision]
    return {"votes": votes, "conf": conf, "F": F, "E": E, "D": D, "C": C, "M": M,
            "components": comp, "U": U, "R": R, "decision": int(decision), "private": private}


def main():
    config = yaml.safe_load((ROOT / "configs" / "pharma_proposed.yaml").read_text())
    baseline = yaml.safe_load((ROOT / "configs" / "pharma_baseline.yaml").read_text())
    seed = 0
    prep = prepare(config, seed)
    log = simulate(prep, config, seed)
    saved = json.loads((ROOT / "results" / "raw" / "pharma_proposed" / "seed_0.json")
                       .read_text())["metrics"]
    replay = summarise(prep, log)
    for key in ("fidelity", "evidence_support", "manipulation", "collective_accuracy"):
        assert abs(replay[key] - saved[key]) < 1e-12, key

    T, game = len(prep["reference"]), prep["game"]
    manip = STRATEGIES.index("manipulative")
    pick = None
    for t in range(T - game["eval_last"], T):
        for i in range(len(prep["agents"])):
            if (log["strategy"][t, i] == manip and not log["malicious"][t, i]
                    and prep["preferred"][t, i] != prep["proba"][t, i].argmax()
                    and prep["preferred"][t, i] != prep["reference"][t]):
                pick = (t, i)
                break
        if pick:
            break
    t, i = pick
    played = [STRATEGIES[int(s)] for s in log["strategy"][t]]
    rep = log["reputation"][t]
    w_prop = validate_weights(config["incentive_weights"])
    w_base = validate_weights(baseline["incentive_weights"])

    # the replayed round must equal the logged round
    check = score_round(prep, t, played, w_prop, rep)
    assert np.allclose(check["U"], log["U"][t]) and np.allclose(check["R"], log["R"][t])

    audit = prep["audit"][i]
    feats = audit["features"]
    out = {"run": "pharma_proposed", "seed": seed, "round": int(t),
           "scenario_id": str(prep["scenario_ids"][t]), "agent": prep["agents"][i],
           "omega": game["omega"], "strategies_played": played,
           "reference": int(prep["reference"][t]), "model_vote": int(prep["proba"][t, i].argmax()),
           "preferred": int(prep["preferred"][t, i]),
           "private_utility": prep["utilities"][t, i].tolist(),
           "model_proba": prep["proba"][t, i].tolist(), "reputation": rep.tolist(),
           "reports": {}}
    for strategy in ("honest", "manipulative"):
        strategies = list(played)
        strategies[i] = strategy
        vote, conf, expl, claims, _ = report(prep, t, i, strategy)
        phi = audit["phi"][t, vote]
        x = audit["X"][t, vote]
        th = audit["thresholds"]
        entry = {"vote": int(vote), "confidence": conf,
                 "explanation": [{"feature": feats[f], "sign": int(s),
                                  "true_sign": int(np.sign(phi[f])),
                                  "abs_shap": float(abs(phi[f]))} for f, s in expl],
                 "true_top": [{"feature": feats[f], "sign": int(np.sign(phi[f])),
                               "abs_shap": float(abs(phi[f]))}
                              for f in np.argsort(-np.abs(phi))[:game["top_k"]]],
                 "claims": [{"feature": feats[f], "claimed": lv,
                             "observed": observed_level(x[f], th[0, f], th[1, f])}
                            for f, lv in claims]}
        for name, weights, votes_w in (("proposed", w_prop, rep),
                                       ("baseline", w_base, np.ones(len(rep)))):
            s = score_round(prep, t, strategies, weights, votes_w)
            entry[name] = {"F": float(s["F"][i]), "E": float(s["E"][i]), "D": float(s["D"][i]),
                           "C": float(s["C"][i]), "M": float(s["M"][i]),
                           "components": {a: float(s["components"][a][i]) for a in ATTACKS},
                           "U": float(s["U"][i]), "R": float(s["R"][i]),
                           "decision": s["decision"], "private": float(s["private"][i]),
                           "payoff": float(game["omega"] * s["private"][i]
                                           + (1 - game["omega"]) * s["R"][i]),
                           "reputation_next": float(config["reputation"]["rho"] * rep[i]
                                                    + (1 - config["reputation"]["rho"])
                                                    * s["R"][i])}
        out["reports"][strategy] = entry
    out["all_rounds"] = all_rounds(prep, log, config, w_prop, w_base)
    path = ROOT / "results" / "summaries" / "worked_example.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    (ROOT / "paper" / "tables" / "tab_example.tex").write_text(to_latex(out), encoding="utf-8")
    print(json.dumps(out, indent=1))


def all_rounds(prep, log, config, w_prop, w_base):
    """Honest versus manipulative report of each agent in each evaluation round, the other
    agents' reports as played: how often does manipulating pay more, under each payoff?"""
    T, game = len(prep["reference"]), prep["game"]
    omega, n = game["omega"], len(prep["agents"])
    out = {}
    for name, weights, use_rep in (("proposed", w_prop, True), ("baseline", w_base, False)):
        diffs, conflict_diffs = [], []
        for t in range(T - game["eval_last"], T):
            played = [STRATEGIES[int(s)] for s in log["strategy"][t]]
            votes_w = log["reputation"][t] if use_rep else np.ones(n)
            for i in range(n):
                pay = {}
                for strategy in ("honest", "manipulative"):
                    strategies = list(played)
                    strategies[i] = strategy
                    s = score_round(prep, t, strategies, weights, votes_w)
                    pay[strategy] = omega * s["private"][i] + (1 - omega) * s["R"][i]
                d = pay["manipulative"] - pay["honest"]
                diffs.append(d)
                pref = prep["preferred"][t, i]
                if pref != prep["proba"][t, i].argmax() and pref != prep["reference"][t]:
                    conflict_diffs.append(d)
        diffs, conflict_diffs = np.array(diffs), np.array(conflict_diffs)
        out[name] = {"agent_rounds": int(len(diffs)),
                     "manipulation_pays_share": float((diffs > 0).mean()),
                     "mean_payoff_difference": float(diffs.mean()),
                     "conflict_agent_rounds": int(len(conflict_diffs)),
                     "conflict_manipulation_pays_share": float((conflict_diffs > 0).mean()),
                     "conflict_mean_payoff_difference": float(conflict_diffs.mean())}
    return out


def to_latex(ex):
    site = lambda a: f"site {a + 1}"  # noqa: E731
    h, m = ex["reports"]["honest"], ex["reports"]["manipulative"]

    def expl(r):
        return "; ".join(f"{LABEL.get(e['feature'], e['feature'])} "
                         f"{'raises' if e['sign'] > 0 else 'lowers'}" for e in r["explanation"])

    def claims(r):
        return "; ".join(f"{LABEL.get(c['feature'], c['feature'])} {c['claimed']}"
                         f" (observed {c['observed']})" for c in r["claims"])

    rows = [("Vote, confidence", f"{site(h['vote'])}, {h['confidence']:.2f}",
             f"{site(m['vote'])}, {m['confidence']:.2f}"),
            ("Explanation", expl(h), expl(m)),
            ("Evidence claims", claims(h), claims(m))]
    for key, name in (("F", "Fidelity $F$"), ("E", "Evidence $E$"), ("M", "Manipulation $M$"),
                      ("D", "Decision $D$")):
        rows.append((name, f"{h['proposed'][key]:.2f}", f"{m['proposed'][key]:.2f}"))
    for system in ("proposed", "baseline"):
        rows.append((f"Contribution $C$ ({system})", f"{h[system]['C']:.2f}",
                     f"{m[system]['C']:.2f}"))
        rows.append((f"Utility $U$ ({system})", f"${h[system]['U']:+.3f}$",
                     f"${m[system]['U']:+.3f}$"))
        rows.append((f"Reward $R$ ({system})", f"{h[system]['R']:.3f}", f"{m[system]['R']:.3f}"))
        rows.append((f"Collective decision ({system})", site(h[system]["decision"]),
                     site(m[system]["decision"])))
        rows.append((f"Payoff $\\pi$ ({system})", f"{h[system]['payoff']:.3f}",
                     f"{m[system]['payoff']:.3f}"))
    body = "\n".join(" & ".join(r) + " \\\\" for r in rows)
    agent = ex["agent"].replace("_", "-")
    return (
        "\\begin{table*}[t]\n"
        f"\\caption{{Worked example: the {agent} agent in one round of the pharmaceutical "
        f"proposed run (seed {ex['seed']}, round {ex['round']}). The same round is scored with "
        "the agent's honest and manipulative report, the other agents' reports fixed}"
        "\\label{tab:example}\n\\footnotesize\n"
        "\\begin{tabular}{@{}p{0.24\\textwidth}p{0.36\\textwidth}p{0.36\\textwidth}@{}}\n"
        "\\toprule\n & Honest report & Manipulative report \\\\\n\\midrule\n"
        f"{body}\n\\bottomrule\n\\end{{tabular}}\n"
        f"\\footnotetext{{Model vote {site(ex['model_vote'])} (probabilities "
        + ", ".join(f"{p:.2f}" for p in ex["model_proba"])
        + f"); privately preferred {site(ex['preferred'])} (normalised private utility "
        + ", ".join(f"{u:.2f}" for u in ex["private_utility"])
        + f"); reference {site(ex['reference'])}; reputation {ex['reputation'][ex_index(ex)]:.3f}. "
        f"Payoff $\\pi=\\omega\\tilde u_i(a^\\ast)+(1-\\omega)R$ with $\\omega={ex['omega']}$. "
        "Baseline rows: the same reports paid by the decision-only utility with equal votes.}\n"
        "\\end{table*}\n")


def ex_index(ex):
    from agents.pharma_agents import AGENTS
    return list(AGENTS).index(ex["agent"])


if __name__ == "__main__":
    main()
