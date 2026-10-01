"""Export GEDE into our format-classification input.

GEDE asks our question independently: `jobs.prompt_mode` grades how much of the essay the
student contributed, holding the writing model fixed. The mapping to our label rule follows
CONTENT origin, never surface:

  human          the student wrote it                       -> y=1   human ideas, human prose
  task           model given only the assignment prompt     -> y=0   model ideas, model prose
  task+summary   assignment plus a summary of the student's -> y=0   a summary carries the
  summary        model given a summary of the student's     -> y=0   GIST only; the model
                                                                     still invents the
                                                                     structure and every
                                                                     specific, which is rung
                                                                     2 on our ladder. This
                                                                     is also the boundary
                                                                     Gehring and Paassen
                                                                     themselves adopt.
  rewrite-human  model rewrites the student's essay         -> y=1   supplies only wording
  improve-human  model improves the student's essay         -> y=1
  dipper-*       DIPPER paraphrase attack on a generated    -> y=0   attack on model text
  rewrite-*      rewrite attack on a generated essay        -> y=0

The attack arms carry `attack` so the humanizer question can be asked separately; the ladder
arms carry `rung` so the graded contrast survives into scoring.
"""
import json, re, sqlite3
from pathlib import Path

W = Path("${WORK_DIR}")
DB = W / "gede/database.db"
OUT = W / "newevals/gede_format_input.jsonl"

# ladder position: 0 is the model supplying everything, 4 the student supplying all the ideas
RUNG = {"task": 0, "task+summary": 1, "summary": 2, "rewrite-human": 3, "improve-human": 4}
# Only a rewrite or an improvement leaves the student's substance intact. A SUMMARY
# carries the gist alone -- the model still invents the structure and every specific,
# which is rung 2 on our ladder -- so summary and task+summary are the model's ideas.
# This is also the boundary Gehring and Paassen adopt for every headline number.
HUMAN_IDEAS = {"rewrite-human", "improve-human"}


def main():
    if OUT.exists():
        raise SystemExit(f"{OUT} exists -- refusing to overwrite")
    c = sqlite3.connect(DB)
    rows, skipped = [], 0
    q = """SELECT a.id, a.answer, a.is_human, a.rewrite_of, j.prompt_mode, j.model,
                  d.name, q.question
           FROM answers a
           LEFT JOIN jobs j      ON a.job_id = j.id
           LEFT JOIN questions q ON a.question_id = q.id
           LEFT JOIN datasets d  ON q.dataset_id = d.id"""
    for aid, ans, is_h, rw, mode, model, dsname, _quest in c.execute(q):
        if not ans or not ans.strip():
            skipped += 1
            continue
        mode = mode or ""
        if is_h:
            arm, y, rung, attack = "human", 1, None, None
        elif mode in RUNG:
            arm, rung = mode, RUNG[mode]
            y = 1 if mode in HUMAN_IDEAS else 0
            attack = None
        elif mode.startswith("dipper-") or mode.startswith("rewrite-"):
            # an attack applied to already-generated text: the ideas are still the model's
            arm, y, rung = ("dipper" if mode.startswith("dipper-") else "rewrite_attack"), 0, None
            attack = mode.split("-", 1)[0]
        elif mode == "task+resource":
            arm, y, rung, attack = "task+resource", 0, None, None
        else:
            skipped += 1
            continue
        txt = re.sub(r"\s+", " ", ans).strip()
        rows.append({"id": f"gede_{aid}", "text": txt, "words": len(txt.split()),
                     "y": y, "arm": arm, "rung": rung, "attack": attack,
                     "generator": model, "corpus": dsname,
                     "pair_id": f"gede_src_{rw}" if rw else f"gede_own_{aid}"})
    with open(OUT, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    import collections
    print(f"wrote {OUT}\n  {len(rows):,} documents, {skipped:,} skipped")
    ca = collections.Counter((r["arm"], r["y"]) for r in rows)
    print(f"\n  {'arm':16s} {'y':>3s} {'n':>7s}   reading")
    lab = {1: "HUMAN ideas", 0: "MODEL ideas"}
    for (a, y), n in sorted(ca.items(), key=lambda x: (-x[1])):
        print(f"  {a:16s} {y:>3} {n:>7,}   {lab[y]}")
    w = [r["words"] for r in rows]
    w.sort()
    print(f"\n  words: median {w[len(w)//2]}, "
          f"under 500 {sum(1 for x in w if x < 500)/len(w)*100:.1f}%")
    print(f"  documents with a human source (pair_id): "
          f"{sum(1 for r in rows if r['pair_id'].startswith('gede_src_')):,}")
    print(f"\n  extraction at $15.07/1k = ${len(rows)/1000*15.07:,.0f}"
          f"   (paraphrase deferred, would be ${len(rows)/1000*24.89:,.0f})")


main()
