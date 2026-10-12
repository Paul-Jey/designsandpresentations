"""Fill the static contents / tables / figures lists with real page numbers.

Builds the report, renders it to PDF with LibreOffice, finds the page of every heading and
caption, writes pagemap.json and rebuilds, repeating until the page numbers stop changing.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "_render"
OUT.mkdir(exist_ok=True)
ROMAN = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv", "xvi"]
norm = lambda s: re.sub(r"\s+", " ", s).strip()


def build():
    subprocess.run([sys.executable, str(HERE / "build_report.py")], check=True, capture_output=True)


def render():
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(OUT), str(ROOT / "Final_Report.docx")],
                   check=True, capture_output=True)
    pdf = OUT / "Final_Report.pdf"
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    pages = [subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), str(pdf), "-"],
                            capture_output=True, text=True).stdout for i in range(1, n + 1)]
    return pages


def pagemap(pages):
    ent = json.load(open(HERE / "toc_entries.json"))
    body0 = next(i for i, p in enumerate(pages) if re.search(r"^\s*CHAPTER 1\s*$", p, re.M))
    label = lambda i: str(i - body0 + 1) if i >= body0 else ROMAN[i + 1]
    flat = [norm(p) for p in pages]
    pm, missing = {}, []

    def find(text, start, end):
        t = norm(text)[:60]
        for i in range(start, end):
            if t in flat[i]:
                return i
        return None

    for kind, chap, title, key in ent["toc"]:
        if kind == "front":
            i = next((j for j in range(body0) if [l.strip() for l in pages[j].splitlines() if l.strip()][:2].count(title)), None)
        elif kind == "chap" and chap:
            i = next((j for j in range(body0, len(pages)) if re.search(rf"^\s*CHAPTER {chap}\s*$", pages[j], re.M)), None)
        else:
            i = find(key.split(":", 1)[1], body0, len(pages))
        (pm.__setitem__(key, label(i)) if i is not None else missing.append(key))
    for kind in ("tab", "fig"):
        for num, cap, key in ent[kind]:
            i = find(key.split(":", 1)[1], body0, len(pages))
            (pm.__setitem__(key, label(i)) if i is not None else missing.append(key))
    return pm, missing, body0, len(pages)


prev = None
for it in range(4):
    build()
    pages = render()
    pm, missing, body0, n = pagemap(pages)
    json.dump(pm, open(HERE / "pagemap.json", "w"), indent=1)
    print(f"pass {it + 1}: {n} pages, Chapter 1 on PDF page {body0 + 1}, mapped {len(pm)}, missing {missing}")
    if pm == prev:
        break
    prev = pm
build()
print("final build done")
