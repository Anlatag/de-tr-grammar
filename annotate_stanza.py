#!/usr/bin/env python3
"""Annotate German-Turkish sentence pairs with Stanza and write CoNLL-U files.

Input: a tab-separated file with one sentence pair per line (German<TAB>Turkish).
Usage:
    python annotate_stanza.py pairs.tsv --max-pairs 2000
Creates de.conllu and tr.conllu in the current folder.
"""
import argparse
import csv

import stanza
from stanza.utils.conll import CoNLL

PROCESSORS = {
    "de": "tokenize,mwt,pos,lemma,depparse",
    "tr": "tokenize,pos,lemma,depparse",
}


def annotate(lang, sentences, out_path):
    stanza.download(lang)
    nlp = stanza.Pipeline(lang, processors=PROCESSORS[lang], tokenize_no_ssplit=True)
    doc = nlp("\n\n".join(sentences))  # blank line = sentence boundary
    CoNLL.write_doc2conll(doc, out_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pairs")
    ap.add_argument("--de-col", type=int, default=0)
    ap.add_argument("--tr-col", type=int, default=1)
    ap.add_argument("--max-pairs", type=int, default=2000)
    args = ap.parse_args()

    de, tr = [], []
    with open(args.pairs, encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) > max(args.de_col, args.tr_col) and row[args.de_col].strip() and row[args.tr_col].strip():
                de.append(row[args.de_col].strip())
                tr.append(row[args.tr_col].strip())
            if len(de) >= args.max_pairs:
                break
    annotate("de", de, "de.conllu")
    annotate("tr", tr, "tr.conllu")
    print(f"Annotated {len(de)} sentence pairs.")


if __name__ == "__main__":
    main()
