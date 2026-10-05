"""Experiment registry: maps the `experiment` key of a YAML config to a runner.

A runner has signature `run(config: dict, seed: int) -> dict` and returns the
metrics for one seed. Nothing is registered until the corresponding phase is
implemented; `run_experiment.py` refuses to produce results for an unregistered
experiment rather than emitting placeholders.
"""
REGISTRY = {}


def register(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn

    return deco
