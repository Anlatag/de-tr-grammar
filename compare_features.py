#!/usr/bin/env python3
"""Compare tense, mood and voice in German and Turkish CoNLL-U data.

Usage:
    python compare_features.py de.conllu tr.conllu --out results.csv --plot plot.png
"""
import argparse
import csv
from collections import Counter

FEATURES = ("Tense", "Mood", "Voice")
VERBAL = {"VERB", "AUX"}


def parse_feats(s):
    if s in ("_", ""):
        return {}
    return dict(p.split("=", 1) for p in s.split("|") if "=" in p)


def read_conllu(path):
    """Yield sentences as lists of token dicts (multiword and empty tokens skipped)."""
    sent = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if sent:
                    yield sent
                    sent = []
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) != 10 or "-" in cols[0] or "." in cols[0]:
                continue
            sent.append({
                "id": int(cols[0]),
                "upos": cols[3],
                "feats": parse_feats(cols[5]),
                "head": int(cols[6]) if cols[6].isdigit() else 0,
                "deprel": cols[7],
            })
    if sent:
        yield sent


def analyze(path):
    counts = {f: Counter() for f in FEATURES}
    n_tokens = 0
    for sent in read_conllu(path):
        # German passive is marked by an aux:pass dependent, not by a Voice feature
        passive_heads = {t["head"] for t in sent if t["deprel"].startswith("aux:pass")}
        for t in sent:
            if t["upos"] == "PUNCT":
                continue
            n_tokens += 1
            if t["upos"] not in VERBAL:
                continue
            for feat in ("Tense", "Mood"):
                if feat in t["feats"]:
                    counts[feat][t["feats"][feat]] += 1
            # Count voice on lexical verbs, or on auxiliaries that carry Voice themselves
            if t["upos"] == "VERB" or "Voice" in t["feats"]:
                voice = t["feats"].get("Voice") or ("Pass" if t["id"] in passive_heads else "Act")
                counts["Voice"][voice] += 1
    return counts, n_tokens


def rows(lang, counts, n_tokens):
    for feat in FEATURES:
        total = sum(counts[feat].values())
        for value, c in sorted(counts[feat].items()):
            yield [lang, feat, value, c,
                   round(c / n_tokens * 1000, 2) if n_tokens else 0,
                   round(c / total * 100, 1) if total else 0]


def plot(results, path):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping plot")
        return
    fig, axes = plt.subplots(1, len(FEATURES), figsize=(12, 4))
    for ax, feat in zip(axes, FEATURES):
        values = sorted({r[2] for r in results if r[1] == feat})
        for i, lang in enumerate(("German", "Turkish")):
            shares = {r[2]: r[5] for r in results if r[0] == lang and r[1] == feat}
            ax.bar([k + i * 0.4 for k in range(len(values))],
                   [shares.get(v, 0) for v in values], width=0.4, label=lang)
        ax.set_xticks([k + 0.2 for k in range(len(values))])
        ax.set_xticklabels(values)
        ax.set_title(feat)
        ax.set_ylabel("share within feature (%)")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("german")
    ap.add_argument("turkish")
    ap.add_argument("--out", default="results.csv")
    ap.add_argument("--plot")
    args = ap.parse_args()

    results = []
    for lang, path in (("German", args.german), ("Turkish", args.turkish)):
        counts, n_tokens = analyze(path)
        results.extend(rows(lang, counts, n_tokens))

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["language", "feature", "value", "count", "per_1000_tokens", "share_in_feature_percent"])
        w.writerows(results)
    for r in results:
        print("{:8} {:6} {:5} count={:<4} per1000={:<8} share={}%".format(*r))
    if args.plot:
        plot(results, args.plot)


if __name__ == "__main__":
    main()
