"""Checks on the manuscript: word counts, citations vs bibliography, figures and tables used.

    python paper/check_manuscript.py
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def words(text):
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\begin\{(figure\*?|table\*?|equation)\}.*?\\end\{\1\}", " ", text, flags=re.S)
    text = re.sub(r"\\(input|label|ref|cite[pt]?|includegraphics)(\[[^]]*\])?\{[^}]*\}", " x ", text)
    text = re.sub(r"\$[^$]*\$", " x ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    return len(re.findall(r"[A-Za-z0-9][\w'.,%-]*", text))


def main():
    s = (HERE / "main.tex").read_text(encoding="utf-8")
    body = s[s.index(r"\section{Introduction}"):s.index(r"\backmatter")]
    abstract = s[s.index(r"\abstract{") + len(r"\abstract{"):s.index(r"\keywords")]
    keywords = s[s.index(r"\keywords{") + len(r"\keywords{"):]
    keywords = keywords[:keywords.index("}")]
    print(f"abstract: {words(abstract)} words (journal: 150-250)")
    print(f"keywords: {len([k for k in keywords.split(',') if k.strip()])} (journal: 4-6)")
    print(f"main text: {words(body)} words (journal guidance: about 6000)")
    cites = {k.strip() for m in re.findall(r"\\cite[pt]?\{([^}]*)\}", s) for k in m.split(",")}
    bib = set(re.findall(r"@\w+\{([a-z0-9]+),", (HERE / "references.bib").read_text(encoding="utf-8")))
    print("cited but missing from bib:", sorted(cites - bib) or "none")
    print("in bib but not cited:", sorted(bib - cites) or "none")
    for fig in re.findall(r"figures/(\w+)\.pdf", s):
        assert (ROOT / "figures" / f"{fig}.pdf").exists(), fig
    for tab in re.findall(r"\\input\{tables/(\w+)\}", s):
        assert (HERE / "tables" / f"{tab}.tex").exists(), tab
    print("all figures and tables exist")
    for pattern in ("Hashmi", "github", "HamzaHashmi"):
        if pattern.lower() in s.lower():
            print(f"WARNING: identifying string '{pattern}' in the blinded manuscript")


if __name__ == "__main__":
    main()
