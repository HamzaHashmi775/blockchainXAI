"""SHAP attributions for the agents' tree models (protocol sections 4-6)."""
import numpy as np
import shap


def shap_values(model, X):
    """Exact TreeSHAP for a multiclass forest.

    Returns (values, base) with values of shape (n_samples, n_features, n_classes)
    and base of shape (n_classes,), such that
    base + values.sum(axis=1) == model.predict_proba(X).
    """
    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(np.asarray(X), check_additivity=False)
    if isinstance(values, list):                 # older shap: one array per class
        values = np.stack(values, axis=-1)
    values = np.asarray(values)
    base = np.atleast_1d(np.asarray(explainer.expected_value, dtype=float))
    return values, base


def top_k_features(phi, k):
    """Indices of the k largest |phi|, most important first (stable on ties)."""
    order = np.argsort(-np.abs(phi), kind="stable")
    return order[:k]


def bottom_k_features(phi, k):
    """Indices of the k smallest |phi|, least important first (stable on ties)."""
    order = np.argsort(np.abs(phi), kind="stable")
    return order[:k]
