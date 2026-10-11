"""LLM-agent experiments (protocol amendments 3 and 4).

`<domain>_llm_main`: baseline, ablation and proposed on the same rounds of a seed.
`<domain>_llm_adversarial`: scripted malicious agents and scripted colluders among LLM
agents, on the first rounds of the same seed's main rounds.

A result file holds, per system, the metrics, the per-round outcome and every raw model
reply: concurrent inference is not bit-reproducible, so the replies are the record.
"""
import importlib
import platform

import numpy as np

from agents.llm_agent import OllamaClient
from experiments import register
from experiments.llm import simulate_llm, summarise_llm

ROUND_KEYS = ("votes", "confidence", "F", "E", "M", "R", "payoff", "deviates", "invalid",
              "reputation")


def make_client(llm):
    """Client for the configured model; refuses a model other than the frozen one."""
    client = OllamaClient(llm["model"], host=llm.get("host", "http://127.0.0.1:11434"),
                          temperature=llm["temperature"], num_predict=llm["num_predict"],
                          num_ctx=llm["num_ctx"])
    served = client.describe()
    if llm.get("digest") and served.get("digest") != llm["digest"]:
        raise RuntimeError(f"served model digest {served.get('digest')!r} is not the frozen "
                           f"{llm['digest']!r}; refusing to run")
    return client, served


def _style(config):
    """Prompt style of the run; amendment 3 configs have none and mean "disclosed"."""
    return config["llm"].get("prompt_style", "disclosed")


def environment():
    versions = {"python": platform.python_version()}
    for name in ("numpy", "pandas", "sklearn", "shap", "scipy"):
        versions[name] = importlib.import_module(name).__version__
    return versions


def _package(prep, log, records, window=None):
    T = len(log["collective"])
    return {"metrics": summarise_llm(prep, log, records, window),
            "rounds": {"reference": prep["reference"][:T].tolist(),
                       "collective": log["collective"].tolist(),
                       **{key: np.asarray(log[key]).tolist() for key in ROUND_KEYS}},
            "calls": [{k: v for k, v in r.items() if k != "prompt"} for r in records],
            "first_round_prompts": [r["prompt"] for r in records if "prompt" in r]}


def register_llm_domain(domain, client_factory=make_client):
    prepare = importlib.import_module(f"experiments.{domain}").prepare

    def run_main(config, seed):
        client, served = client_factory(config["llm"])
        prep = prepare(config, seed)
        out = {"seed": seed, "domain": domain, "model": served, "environment": environment(),
               "prompt_style": _style(config), "omega": config["game"]["omega"],
               "tool_val_accuracy": prep["val_accuracy"], "systems": {}}
        for name, system in config["systems"].items():
            log, records = simulate_llm(prep, system, seed, client, domain,
                                        workers=config["llm"]["workers"],
                                        prompt_style=_style(config))
            out["systems"][name] = _package(prep, log, records)
        return out

    def run_adversarial(config, seed):
        client, served = client_factory(config["llm"])
        prep = prepare(config, seed)
        n_agents = len(prep["agents"])
        rounds = config["adversarial"]["rounds"]
        order = np.random.default_rng([seed, 3]).permutation(n_agents)      # as experiments/core
        pair = tuple(int(i) for i in np.random.default_rng([seed, 4]).permutation(n_agents)[:2])
        out = {"seed": seed, "domain": domain, "model": served, "environment": environment(),
               "prompt_style": _style(config), "omega": config["game"]["omega"],
               "rounds_played": rounds, "colluders": [prep["agents"][i] for i in pair],
               "systems": {}}
        for name, system in config["systems"].items():
            by_fraction = {}
            for fraction in config["adversarial"]["malicious_fractions"]:
                count = int(round(n_agents * fraction))
                bad = [int(i) for i in order[:count]]
                log, records = simulate_llm(prep, system, seed, client, domain, n_rounds=rounds,
                                            workers=config["llm"]["workers"],
                                        prompt_style=_style(config), malicious=bad)
                by_fraction[str(fraction)] = {
                    "malicious_agents": [prep["agents"][i] for i in bad],
                    **_package(prep, log, records)}
            log, records = simulate_llm(prep, system, seed, client, domain, n_rounds=rounds,
                                        workers=config["llm"]["workers"],
                                        prompt_style=_style(config), colluders=pair)
            out["systems"][name] = {"malicious": by_fraction,
                                    "collusion": _package(prep, log, records)}
        return out

    register(f"{domain}_llm_main")(run_main)
    register(f"{domain}_llm_adversarial")(run_adversarial)


for _domain in ("pharma", "energy"):
    register_llm_domain(_domain)
