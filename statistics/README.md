# statistics/

Statistical-analysis scripts (CLAUDE.md section 7).

This folder is deliberately **not** a Python package (no `__init__.py`): a package named
`statistics` at the project root would shadow the standard-library `statistics` module.
Run scripts here by path (`python statistics/<script>.py`); shared, importable code goes
in `evaluation/`.
