#!/usr/bin/env python3
"""Within-pool lexicon counts for the third-pole mini-corpus (Q16).

Reuses the frozen lexicons from tagging/lexicons.json. WITHIN-POOL ONLY:
these are written prose, not speech — never compare these rates against
the podcast counts in tagging/counts.json (prose and speech have different
hedging/profanity norms). See third_pole/atomic_blonde/README.md.

Usage: python3 third_pole/third_pole_counts.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEX = json.loads((ROOT / "tagging" / "lexicons.json").read_text())
POOL = sorted((ROOT / "third_pole" / "atomic_blonde").glob("*.txt"))


def count_metric(text, tokens):
    total = 0
    hits = {}
    for tok in tokens:
        pat = r"\b" + re.escape(tok).replace(r"\ ", r"\s+") + r"\b"
        n = len(re.findall(pat, text, flags=re.IGNORECASE))
        if n:
            hits[tok] = n
            total += n
    return total, hits


def main():
    metrics = [m for m in LEX["metrics"] if m not in ("ingroup_kjb",)]
    out = {}
    for f in POOL:
        text = f.read_text()
        words = len(re.findall(r"[A-Za-z']+", text))
        row = {"words": words}
        for m in metrics:
            total, hits = count_metric(text, LEX["metrics"][m]["tokens"])
            row[m] = {"raw": total, "per_1k": round(total * 1000 / words, 2), "hits": hits}
        out[f.stem] = row
    dest = ROOT / "third_pole" / "third_pole_counts.json"
    dest.write_text(json.dumps(out, indent=2))
    for name, row in out.items():
        print(f"\n{name} ({row['words']} words)")
        for m in metrics:
            r = row[m]
            print(f"  {m:24s} raw {r['raw']:3d}  /1k {r['per_1k']:6.2f}")


if __name__ == "__main__":
    main()
