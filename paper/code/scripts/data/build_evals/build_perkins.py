"""Export Perkins et al. into our format-classification input.

A .docx is a zip with word/document.xml inside, so no dependency is needed: paragraphs are
<w:p> elements and the text is the <w:t> runs within them.

Arms follow CONTENT origin. Every adversarial variant is a SURFACE edit applied to an
already model-written sample, so all of them stay y=0 -- which is the point: our claim is
that surface edits should not move an idea-level verdict. The technique is kept so the six
can be read separately.

The human arm is 10 documents. That is far below the k>=25 floor for any threshold fitted on
this set, so Perkins can report detection rates against calibration cuts and nothing else.
No FPR is computable here and none should be quoted.
"""
import json, re, zipfile
from pathlib import Path

SRC = Path("${AUX_DIR}/data/"
           "Data files Simple Techniques to Bypass GenAI Text Detectors "
           "Implications for Inclusive Education")
OUT = Path("${WORK_DIR}/newevals/"
           "perkins_format_input.jsonl")
NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TECH = {"1": ("spelling_errors", "SE"), "2": ("non_native_style", "NNS"),
        "3": ("decrease_complexity", "DC"), "4": ("increase_complexity", "IC"),
        "5": ("increase_burstiness", "IB"), "6": ("paraphrase", "PR")}


def docx_text(p):
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(p) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paras = []
    for para in root.iter(f"{NS}p"):
        s = "".join(t.text or "" for t in para.iter(f"{NS}t"))
        if s.strip():
            paras.append(s.strip())
    return re.sub(r"\s+", " ", " ".join(paras)).strip()


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} exists -- refusing to overwrite")
    rows, bad = [], []
    for p in sorted(SRC.rglob("*.docx")):
        rel = p.relative_to(SRC)
        if len(rel.parts) < 3:
            continue                      # the prompts document at the root
        top, sub, name = rel.parts[0], rel.parts[1], rel.parts[-1]
        if top.startswith("Control"):
            arm, y, tech = ("human_faculty" if "Faculty" in sub else "human_student"), 1, None
        elif top.startswith("Original"):
            arm, y, tech = "ai_" + sub.split("(")[-1].rstrip(")").replace("ai_", ""), 0, None
        else:
            key = sub.split(".")[0].strip()
            if key not in TECH:
                bad.append(str(rel)); continue
            tech, _ = TECH[key]
            arm, y = f"adv_{tech}", 0
        try:
            txt = docx_text(p)
        except Exception as e:
            bad.append(f"{rel}: {e}"); continue
        if len(txt.split()) < 20:
            bad.append(f"{rel}: only {len(txt.split())} words"); continue
        rows.append({"id": "perkins_" + re.sub(r"[^A-Za-z0-9]+", "_",
                                               str(rel.with_suffix("")))[:120],
                     "text": txt, "words": len(txt.split()), "y": y, "arm": arm,
                     "technique": tech, "source_dir": sub})
    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    import collections, statistics as st
    print(f"wrote {OUT}\n  {len(rows)} documents, {len(bad)} skipped")
    for b in bad[:6]:
        print(f"    skipped: {b}")
    print(f"\n  {'arm':26s} {'y':>3s} {'n':>4s} {'median words':>13s}")
    for a in sorted({r['arm'] for r in rows}):
        g = [r for r in rows if r["arm"] == a]
        print(f"  {a:26s} {g[0]['y']:>3} {len(g):>4} "
              f"{int(st.median([x['words'] for x in g])):>13}")
    w = sorted(r["words"] for r in rows)
    print(f"\n  words overall: median {w[len(w)//2]}, min {w[0]}, max {w[-1]}, "
          f"under 500 {100*sum(1 for x in w if x < 500)/len(w):.0f}%")
    print(f"  human arm total: {sum(1 for r in rows if r['y'] == 1)} "
          f"-- too few for any threshold fitted here; use calibration cuts only")
    print(f"  pipeline cost: ${len(rows)/1000*39.96:,.2f} both stages")


main()
