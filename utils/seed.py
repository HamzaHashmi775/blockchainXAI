"""Global seeding utility (Golden Rule 10: determinism)."""
import os
import random

import numpy as np


def seed_everything(seed: int) -> np.random.Generator:
    """Seed `random` and numpy's legacy global RNG; return a seeded Generator.

    Model RNGs (scikit-learn estimators) are not global: pass `seed` to their
    `random_state` argument, or use `model_seed` to derive a per-model seed.
    """
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError(f"seed must be a non-negative int, got {seed!r}")
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)


def model_seed(seed: int, name: str) -> int:
    """Deterministic per-component seed derived from the run seed and a name."""
    import hashlib

    digest = hashlib.sha256(f"{seed}:{name}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)
