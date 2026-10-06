"""Turn kaggle/llm_pilot_kaggle.py ("# %%" cells) into the .ipynb Kaggle imports.

    python kaggle/make_notebook.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cells(source):
    for block in source.split("# %%")[1:]:
        header, _, body = block.partition("\n")
        body = body.strip("\n")
        if "[markdown]" in header:
            text = "\n".join(line[2:] if line.startswith("# ") else line.lstrip("#")
                             for line in body.split("\n"))
            yield {"cell_type": "markdown", "metadata": {}, "source": text}
        else:
            yield {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                   "source": body}


def main():
    source = (HERE / "llm_pilot_kaggle.py").read_text(encoding="utf-8")
    notebook = {"cells": list(cells(source)), "nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                            "name": "python3"},
                             "language_info": {"name": "python"}}}
    (HERE / "llm_pilot_kaggle.ipynb").write_text(json.dumps(notebook, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
