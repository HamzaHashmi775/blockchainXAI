"""Statistical analysis helpers (protocol section 9). Unit of analysis: the seed."""
import numpy as np
from scipy import stats


def describe(values, confidence=0.95):
    x = np.asarray(values, dtype=float)
    n, mean = len(x), float(np.mean(x))
    sd = float(np.std(x, ddof=1)) if n > 1 else float("nan")
    half = float(stats.t.ppf(0.5 + confidence / 2, n - 1) * sd / np.sqrt(n)) if n > 1 else float("nan")
    return {"n": n, "mean": mean, "sd": sd, "ci_low": mean - half, "ci_high": mean + half}


def relative_improvement(proposed_mean, baseline_mean):
    if baseline_mean == 0:
        return float("nan")
    return float((proposed_mean - baseline_mean) / abs(baseline_mean))


def rank_biserial(differences):
    """Matched-pairs rank-biserial correlation (zero differences dropped)."""
    d = np.asarray(differences, dtype=float)
    d = d[d != 0]
    if len(d) == 0:
        return float("nan")
    ranks = stats.rankdata(np.abs(d))
    return float((ranks[d > 0].sum() - ranks[d < 0].sum()) / ranks.sum())


def paired_comparison(treatment, control, alpha=0.05, n_boot=10000, seed=0):
    """Paired test of treatment vs control over seeds.

    Shapiro-Wilk on the differences decides between a paired t-test (Cohen's d_z)
    and a Wilcoxon signed-rank test (rank-biserial r). Two-sided.
    """
    a, b = np.asarray(treatment, dtype=float), np.asarray(control, dtype=float)
    if a.shape != b.shape:
        raise ValueError("paired samples must have the same length")
    d = a - b
    out = {"n": len(d), "mean_treatment": float(a.mean()), "mean_control": float(b.mean()),
           "mean_difference": float(d.mean()),
           "relative_improvement": relative_improvement(a.mean(), b.mean())}
    if np.allclose(d, d[0]):
        # constant differences: neither test is defined (zero variance)
        out.update(test="none (constant paired differences)", statistic=float("nan"),
                   p_value=float("nan") if d[0] != 0 else 1.0, effect_size_name="none",
                   effect_size=float("nan"), shapiro_p=float("nan"),
                   ci_low=float(d[0]), ci_high=float(d[0]), ci_method="degenerate")
        return out
    shapiro_p = float(stats.shapiro(d).pvalue)
    out["shapiro_p"] = shapiro_p
    if shapiro_p > alpha:
        res = stats.ttest_rel(a, b)
        half = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
        out.update(test="paired t-test", statistic=float(res.statistic), p_value=float(res.pvalue),
                   effect_size_name="cohen_dz", effect_size=float(d.mean() / d.std(ddof=1)),
                   ci_low=float(d.mean() - half), ci_high=float(d.mean() + half),
                   ci_method="t-interval")
    else:
        res = stats.wilcoxon(a, b)
        rng = np.random.default_rng(seed)
        boots = rng.choice(d, size=(n_boot, len(d)), replace=True).mean(axis=1)
        out.update(test="Wilcoxon signed-rank", statistic=float(res.statistic),
                   p_value=float(res.pvalue), effect_size_name="rank_biserial",
                   effect_size=rank_biserial(d), ci_low=float(np.quantile(boots, 0.025)),
                   ci_high=float(np.quantile(boots, 0.975)), ci_method="percentile bootstrap")
    return out


def holm(p_values):
    """Holm step-down adjusted p-values (NaN entries are left as NaN)."""
    p = np.asarray(p_values, dtype=float)
    adjusted = np.full(p.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(p))
    order = valid[np.argsort(p[valid], kind="stable")]
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (len(order) - rank) * p[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted


def friedman(groups):
    """Friedman test across repeated conditions; `groups` = list of per-seed arrays."""
    arrays = [np.asarray(g, dtype=float) for g in groups]
    if all(np.allclose(a, arrays[0]) for a in arrays[1:]):
        return {"test": "Friedman", "statistic": float("nan"), "p_value": 1.0,
                "note": "all conditions identical"}
    res = stats.friedmanchisquare(*arrays)
    return {"test": "Friedman", "statistic": float(res.statistic), "p_value": float(res.pvalue)}


def checkpoint_verdict(comparison, adjusted_p, higher_is_better, alpha=0.05, min_relative=0.05):
    """Pre-declared decision rule: 'improved', 'negligible' or 'worse'."""
    diff = comparison["mean_difference"]
    direction_ok = diff > 0 if higher_is_better else diff < 0
    significant = not np.isnan(adjusted_p) and adjusted_p < alpha
    rel = comparison["relative_improvement"]
    large = np.isnan(rel) or abs(rel) >= min_relative
    if significant and direction_ok and large:
        return "improved"
    if significant and not direction_ok and diff != 0:
        return "worse"
    return "negligible"
