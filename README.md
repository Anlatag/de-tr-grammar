# German vs. Turkish: tense, mood and voice

A small corpus-linguistic tool that compares how often German and Turkish use
different **tenses**, **moods** and **voices** (active/passive). It reads
[CoNLL-U](https://universaldependencies.org/format.html) files, so it works with
any Universal Dependencies (UD) treebank or with output from Stanza.

## Quick start

```bash
python compare_features.py sample_de.conllu sample_tr.conllu --out results.csv --plot plot.png
```

The sample files are tiny, hand-made illustrations (3 sentences each) and are
**not** taken from an official treebank. Use real data for any real analysis.

## With your own parallel sentences

```bash
pip install -r requirements.txt
python annotate_stanza.py pairs.tsv --max-pairs 2000   # German<TAB>Turkish per line
python compare_features.py de.conllu tr.conllu --out results.csv --plot plot.png
```

Parallel sentences can come from Tatoeba or OPUS (check each licence and cite it).
Alternatively, download UD treebanks for German and Turkish directly.

## Method notes

- Counts `Tense`, `Mood` and `Voice` on verbs (UPOS `VERB`, `AUX`).
- **Voice:** Turkish UD marks passives with `Voice=Pass`. German UD usually does not,
  so a German verb counts as passive when it has an `aux:pass` dependent.
  Verbs without either count as active.
- Output: counts, frequency per 1,000 tokens, and share within each feature.

## Limitations

- UD annotation conventions differ between languages and treebanks; the two
  languages are not tagged identically, so compare with care.
- Automatic parsing makes errors, especially on short or unusual sentences.
- Turkish tense/aspect/mood and German tense/mood do not map one-to-one
  (e.g. Turkish evidentiality); this tool counts tags, it does not translate categories.

## Author

Tülin Aker Gökgöz, M.A. German Studies (Linguistics). Code written with AI assistance and reviewed by the author.
