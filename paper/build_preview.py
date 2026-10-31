"""Preview PDF of the manuscript without a LaTeX installation.

    python paper/build_preview.py

Converts paper/main.tex (only the LaTeX subset it uses) to paper/build/manuscript_preview.html,
with author-year citations resolved from references.bib, the generated tables and the PNG
figures, then prints it to paper/build/manuscript_preview.pdf with Microsoft Edge (headless).
This is a reading copy: the submission is compiled with the official Springer Nature
template (see paper/README.md).
"""
import html
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "build"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "lambda": "λ", "rho": "ρ",
         "omega": "ω", "phi": "φ", "varepsilon": "ε", "Delta": "Δ", "pi": "π"}
SYMBOLS = {"pm": "±", "geq": "≥", "leq": "≤", "neq": "≠", "times": "×", "leftarrow": "←",
           "in": "∈", "sum": "Σ", "ast": "*", "dots": "…", "cdot": "·", "max": "max",
           "min": "min", "arg": "arg", "quad": "&emsp;", "qquad": "&emsp;&emsp;"}


# --- bibliography ----------------------------------------------------------------------

def braced(text, start):
    """Return (content, end) of the brace group opening at text[start] == '{'."""
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError("unbalanced braces")


def parse_bib(path):
    text = path.read_text(encoding="utf-8")
    entries = {}
    for m in re.finditer(r"@(\w+)\{([a-z0-9]+),", text):
        body, _ = braced(text, m.end() - len(m.group(2)) - 2)
        fields = {}
        for f in re.finditer(r"(\w+)\s*=\s*(\{|\")", body):
            if f.group(2) == "{":
                value, _ = braced(body, f.end() - 1)
            else:
                value = body[f.end():body.index('"', f.end())]
            fields.setdefault(f.group(1).lower(), re.sub(r"\s+", " ", value).strip())
        for f in re.finditer(r"(\w+)\s*=\s*(\d+)\s*[,}]", body):
            fields.setdefault(f.group(1).lower(), f.group(2))
        entries[m.group(2)] = fields
    return entries


def clean(s):
    s = re.sub(r"\\url\{([^}]*)\}", r"\1", s)
    s = s.replace("{", "").replace("}", "").replace("\\&", "&").replace("--", "–")
    return s


def surnames(fields):
    authors = [a.strip() for a in clean(fields.get("author", "Anonymous")).split(" and ")]
    out = []
    for a in authors:
        out.append(a.split(",")[0].strip() if "," in a else a.split()[-1])
    return out


def cite_label(fields):
    names = surnames(fields)
    who = names[0] if len(names) == 1 else (f"{names[0]} and {names[1]}" if len(names) == 2
                                              else f"{names[0]} et al.")
    return who, fields.get("year", "n.d.")


def reference_html(fields):
    authors = [a.strip() for a in clean(fields.get("author", "")).split(" and ") if a.strip()]
    def short(a):
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
        else:
            parts = a.split()
            last, first = parts[-1], " ".join(parts[:-1])
        initials = "".join(w[0] for w in re.split(r"[\s.-]+", first) if w)
        return f"{last} {initials}".strip()
    names = [short(a) for a in authors]
    who = ", ".join(names[:6]) + (", et al." if len(names) > 6 else "")
    parts = [f"{html.escape(who)} ({fields.get('year', 'n.d.')})",
             html.escape(clean(fields.get("title", ""))) + "."]
    venue = clean(fields.get("journal") or fields.get("booktitle") or fields.get("publisher")
                  or fields.get("howpublished") or "")
    vol = fields.get("volume", "")
    pages = clean(fields.get("pages", ""))
    if venue:
        parts.append(f"<i>{html.escape(venue)}</i>" + (f" {vol}" if vol else "")
                     + (f":{pages}" if pages else ""))
    if fields.get("eprint"):
        parts.append(f"arXiv:{fields['eprint']}")
    if fields.get("doi"):
        parts.append(f"https://doi.org/{fields['doi'].lower()}")
    if fields.get("note"):
        parts.append(html.escape(clean(fields["note"])))
    return " ".join(parts)


# --- LaTeX subset -> HTML --------------------------------------------------------------

def math(m):
    s = m
    s = re.sub(r"\\(text|mathrm|operatorname)\{([^}]*)\}", r"\2", s)
    s = re.sub(r"\\mathbb\{1\}", "𝟙", s)
    s = re.sub(r"\\mathcal\{E\}", "ℰ", s)
    s = re.sub(r"\\tilde\s*u", "ũ", s)
    s = re.sub(r"\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
               r"(\1) / (\2)", s)
    for k, v in {**GREEK, **SYMBOLS}.items():
        s = re.sub(r"\\" + k + r"(?![a-zA-Z])", v, s)
    s = s.replace("\\,", " ").replace("\\ ", " ").replace("\\{", "{").replace("\\}", "}")
    s = s.replace("\\%", "%").replace("\\left", "").replace("\\right", "")
    for _ in range(3):
        s = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", s)
        s = re.sub(r"\^\{([^{}]*)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"_(\w|\S)", r"<sub>\1</sub>", s)
    s = re.sub(r"\^(\w|\S)", r"<sup>\1</sup>", s)
    s = s.replace("{", "").replace("}", "")
    return f"<span class='m'>{s}</span>"


class Converter:
    def __init__(self, bib):
        self.bib = bib
        self.labels = {}
        self.cited = []

    def cite(self, keys, textual):
        out = []
        for k in [k.strip() for k in keys.split(",")]:
            if k not in self.cited:
                self.cited.append(k)
            who, year = cite_label(self.bib[k])
            out.append(f"{who} ({year})" if textual else f"{who} {year}")
        return "; ".join(out) if textual else "(" + "; ".join(out) + ")"

    def inline(self, s):
        s = re.sub(r"(?<!\\)%.*", "", s)
        s = re.sub(r"\$([^$]+)\$", lambda m: "\x00" + math(m.group(1)) + "\x01", s)
        s = re.sub(r"\\cite(p|t)\{([^}]*)\}", lambda m: self.cite(m.group(2), m.group(1) == "t"), s)
        s = re.sub(r"\\ref\{([^}]*)\}", lambda m: self.labels.get(m.group(1), "??"), s)
        s = re.sub(r"\\label\{[^}]*\}", "", s)
        s = re.sub(r"\\url\{([^}]*)\}", r"<a href='\1'>\1</a>", s)
        s = re.sub(r"\\multicolumn\{\d+\}\{\w\}\{(.*)\}", r"\1", s)
        for _ in range(2):
            s = re.sub(r"\\emph\{([^{}]*)\}", r"<em>\1</em>", s)
            s = re.sub(r"\\textbf\{([^{}]*)\}", r"<b>\1</b>", s)
        s = s.replace("\\%", "%").replace("\\&", "&amp;").replace("~", "&nbsp;")
        s = s.replace("---", "—").replace("--", "–").replace("{,}", ",")
        s = s.replace("\\\\", "")
        # text outside math: drop stray braces
        parts = re.split(r"(\x00.*?\x01)", s)
        parts = [p if p.startswith("\x00") else p.replace("{", "").replace("}", "")
                 for p in parts]
        return "".join(parts).replace("\x00", "").replace("\x01", "")

    def table(self, tex):
        cap = re.search(r"\\caption\{(.*)\}\\label\{([^}]*)\}", tex)
        label, caption = cap.group(2), cap.group(1)
        num = self.labels[label]
        body = tex[tex.index("\\toprule") + 8:tex.index("\\bottomrule")]
        rows = [r.strip() for r in body.split("\\\\")]
        out = [f"<div class='tab'><p class='cap'><b>Table {num}</b> {self.inline(caption)}</p>",
               "<table>"]
        first = True
        for r in rows:
            mid = "\\midrule" in r
            r = r.replace("\\midrule", "").strip()
            if not r:
                continue
            raw = [c.strip() for c in re.split(r"(?<!\\)&", r)]
            spans = [int(m.group(1)) if (m := re.match(r"\\multicolumn\{(\d+)\}", c)) else 1
                     for c in raw]
            cells = [self.inline(c) for c in raw]
            tag = "th" if first else "td"
            cls = " class='mid'" if mid and not first else ""
            out.append(f"<tr{cls}>" + "".join(
                f"<{tag}{f' colspan={n}' if n > 1 else ''}>{c}</{tag}>"
                for c, n in zip(cells, spans)) + "</tr>")
            first = False
        out.append("</table>")
        note = re.search(r"\\footnotetext\{(.*)\}", tex)
        if note:
            out.append(f"<p class='note'>{self.inline(note.group(1))}</p>")
        out.append("</div>")
        return "\n".join(out)

    def figure(self, tex):
        img = re.search(r"figures/(\w+)\.pdf", tex).group(1)
        cap = tex[tex.index("\\caption{") + 9:]
        cap, _ = braced("{" + cap, 0)
        label = re.search(r"\\label\{([^}]*)\}", tex).group(1)
        return (f"<figure><img src='../../figures/{img}.png'><figcaption><b>Fig. "
                f"{self.labels[label]}</b> {self.inline(cap)}</figcaption></figure>")


def number_labels(text, conv):
    sec = sub = fig = tab = eq = 0
    for m in re.finditer(r"\\(section|subsection)\{[^}]*\}\\label\{([^}]*)\}|"
                         r"\\begin\{(figure\*?|equation)\}|\\input\{tables/(\w+)\}|"
                         r"\\label\{([^}]*)\}", text):
        if m.group(1) == "section":
            sec, sub = sec + 1, 0
            conv.labels[m.group(2)] = str(sec)
        elif m.group(1) == "subsection":
            sub += 1
            conv.labels[m.group(2)] = f"{sec}.{sub}"
        elif m.group(3):
            kind = m.group(3)
            if kind.startswith("figure"):
                fig += 1
                lab = re.search(r"\\label\{([^}]*)\}", text[m.end():]).group(1)
                conv.labels[lab] = str(fig)
            else:
                eq += 1
                lab = re.search(r"\\label\{([^}]*)\}", text[m.end():]).group(1)
                conv.labels[lab] = f"({eq})"
        elif m.group(4):
            tab += 1
            t = (HERE / "tables" / f"{m.group(4)}.tex").read_text(encoding="utf-8")
            conv.labels[re.search(r"\\label\{([^}]*)\}", t).group(1)] = str(tab)


def convert(main_tex, conv):
    text = "\n".join(l for l in main_tex.splitlines() if not l.lstrip().startswith("%"))
    title = re.search(r"\\title\[[^]]*\]\{(.*?)\}\n\n", text, flags=re.S).group(1)
    abstract, _ = braced(text, text.index("\\abstract{") + 9)
    keywords, _ = braced(text, text.index("\\keywords{") + 9)
    body = text[text.index("\\section{Introduction}"):text.index("\\bibliography")]
    number_labels(body, conv)

    out = ["<p class='preview'>Reading copy generated from main.tex (blinded manuscript). "
           "Layout differs from the journal template; content is identical.</p>",
           f"<h1>{conv.inline(title)}</h1>",
           f"<div class='abs'><p><b>Abstract</b> {conv.inline(abstract)}</p>"
           f"<p><b>Keywords</b> {conv.inline(keywords)}</p></div>"]
    blocks = re.split(r"(\\begin\{(?:figure\*?|equation|enumerate)\}.*?\\end\{(?:figure\*?|equation|enumerate)\}"
                      r"|\\input\{tables/\w+\})", body, flags=re.S)
    sec = sub = 0
    for block in blocks:
        if block.startswith("\\begin{figure"):
            out.append(conv.figure(block))
        elif block.startswith("\\begin{equation}"):
            eq = block[len("\\begin{equation}"):block.index("\\end{equation}")]
            lab = re.search(r"\\label\{([^}]*)\}", eq)
            eq = re.sub(r"\\label\{[^}]*\}", "", eq)
            out.append(f"<div class='eq'>{math(eq.strip())}<span>"
                       f"{conv.labels.get(lab.group(1), '') if lab else ''}</span></div>")
        elif block.startswith("\\begin{enumerate}"):
            items = block.split("\\item")[1:]
            items[-1] = items[-1].replace("\\end{enumerate}", "")
            out.append("<ol>" + "".join(f"<li>{conv.inline(i.strip())}</li>" for i in items)
                       + "</ol>")
        elif block.startswith("\\input{tables/"):
            name = re.search(r"tables/(\w+)", block).group(1)
            out.append(conv.table((HERE / "tables" / f"{name}.tex").read_text(encoding="utf-8")))
        else:
            for para in re.split(r"\n\s*\n", block):
                para = para.strip()
                if not para or para in ("\\backmatter",):
                    continue
                m = re.match(r"\\section\*?\{([^}]*)\}(?:\\label\{[^}]*\})?", para)
                if m:
                    starred = para.startswith("\\section*")
                    if not starred:
                        sec, sub = sec + 1, 0
                    out.append(f"<h2>{'' if starred else str(sec) + ' '}{conv.inline(m.group(1))}</h2>")
                    para = para[m.end():].strip()
                    if not para:
                        continue
                m = re.match(r"\\subsection\{([^}]*)\}(?:\\label\{[^}]*\})?", para)
                if m:
                    sub += 1
                    out.append(f"<h3>{sec}.{sub} {conv.inline(m.group(1))}</h3>")
                    para = para[m.end():].strip()
                    if not para:
                        continue
                para = re.sub(r"\\(paragraph|bmhead)\{([^}]*?)\.?\}", r"<b>\2.</b>", para)
                out.append(f"<p>{conv.inline(para)}</p>")
    refs = sorted(conv.cited, key=lambda k: (cite_label(conv.bib[k])[0].lower(),
                                             cite_label(conv.bib[k])[1]))
    out.append("<h2>References</h2><div class='refs'>"
               + "".join(f"<p>{reference_html(conv.bib[k])}</p>" for k in refs) + "</div>")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 22mm 20mm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 10.5pt; line-height: 1.45;
       color: #111; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 12pt; }
h2 { font-size: 12.5pt; margin: 16pt 0 6pt; }
h3 { font-size: 11pt; margin: 12pt 0 4pt; font-style: italic; }
p { margin: 0 0 6pt; text-align: justify; }
.preview { font-family: Arial, sans-serif; font-size: 8pt; color: #666; text-align: left; }
.abs { border-top: 1px solid #999; border-bottom: 1px solid #999; padding: 6pt 0;
       margin-bottom: 10pt; }
.m { font-style: italic; white-space: nowrap; }
.eq { text-align: center; margin: 8pt 0; position: relative; }
.eq span { position: absolute; right: 0; }
figure { margin: 10pt 0; break-inside: avoid; }
figure img { width: 100%; }
figcaption, .cap { font-size: 9pt; text-align: left; }
.tab { margin: 10pt 0; break-inside: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 8pt; border-top: 1.2px solid #000;
        border-bottom: 1.2px solid #000; }
th { border-bottom: 0.8px solid #000; text-align: left; padding: 2pt 4pt; }
td { padding: 1.5pt 4pt; vertical-align: top; }
tr.mid td { border-top: 0.6px solid #000; }
.note { font-size: 8pt; }
.refs p { font-size: 9pt; text-align: left; padding-left: 1.5em; text-indent: -1.5em; }
ol li { margin-bottom: 4pt; text-align: justify; }
"""


def main():
    BUILD.mkdir(exist_ok=True)
    conv = Converter(parse_bib(HERE / "references.bib"))
    body = convert((HERE / "main.tex").read_text(encoding="utf-8"), conv)
    page = (f"<!doctype html><html><head><meta charset='utf-8'><title>Manuscript preview</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    html_path = BUILD / "manuscript_preview.html"
    html_path.write_text(page, encoding="utf-8")
    pdf_path = BUILD / "manuscript_preview.pdf"
    subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    unresolved = body.count("??")
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size:,} bytes); unresolved refs: {unresolved}")


if __name__ == "__main__":
    main()
