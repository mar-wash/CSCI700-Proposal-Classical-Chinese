# Classical Chinese corpus analysis

This repository contains CoNLL-U annotations for Classical Chinese texts from four Daizhige collections, a script for generating more annotations, and a feasibility notebook that explores contextual uses of 仁, 道, and 天.

## Contents

- `upos-tags/`: 240 CoNLL-U files arranged in the source corpus folder structure: 60 each from 佛藏, 医藏, 道藏, and 儒藏. These are automatic model predictions and have not been manually corrected.
- `scripts/tag_classical_chinese.py`: script used to generate the annotations and to process additional source documents.
- `requirements-upos.txt`: Python dependency list (`esupar`).
- `Classical_Chinese_Feasibility.ipynb`: exploratory analysis of standalone occurrences of 仁, 道, and 天. It uses the CoNLL-U files to locate target tokens, creates contextual embeddings with `ethanyt/guwenbert-base`, and clusters those embeddings separately for each target word.
- `pilot_outputs/`: saved outputs from the feasibility notebook, including occurrence samples, embeddings, cluster assignments, review files, and plots.

The current annotation set contains 60 files per collection. The tagging script selects files in sorted path order independently within each requested section. The committed set can be regenerated from the source corpus with `--offset 10 --limit 50` per section.

## Model and method

The script uses the `lzh` pipeline in [esupar](https://github.com/KoichiYasuoka/esupar), which loads [KoichiYasuoka/roberta-classical-chinese-base-upos](https://huggingface.co/KoichiYasuoka/roberta-classical-chinese-base-upos). The model predicts Universal Dependencies part-of-speech tags (UPOS), grammatical features, and dependency relations.

The script removes YAML front matter from each Markdown file, retains the text, then splits it at punctuation and line breaks. Each model input is capped at 450 tokenizer tokens (below the model's 512-token limit). It writes one `.conllu` output per source document and leaves the source Markdown unchanged. Dependency links are local to each split chunk, so they do not connect words across chunk boundaries.

The model is published under the Apache-2.0 license. This does not determine the rights or license of the source texts or this collection of annotations; check the source corpus terms before redistribution.

## CoNLL-U file format

Each non-comment row represents a token and has ten tab-separated columns:

| Column | Meaning |
| --- | --- |
| ID | Token number within the sentence/chunk |
| FORM | Token text |
| LEMMA | Lemma, when supplied by the pipeline |
| UPOS | Universal part-of-speech tag, such as `NOUN`, `VERB`, or `PART` |
| XPOS | Language-specific part-of-speech tag (often `_` here) |
| FEATS | Grammatical features, such as `Polarity=Neg` |
| HEAD | Head token ID for the dependency parse (`0` marks the root) |
| DEPREL | Dependency relation to the head, such as `nsubj` or `conj` |
| DEPS | Enhanced dependency relations (often `_`) |
| MISC | Other information, including `SpaceAfter=No` |

An underscore (`_`) means the field has no value. Blank lines separate parsed sentences/chunks.

## Run the script

Use Python 3. The first run downloads the model from Hugging Face and requires network access. From this repository's directory, with the original corpus available at `../daizhigev20`, install the dependency and process the currently represented files:

```bash
python3 -m pip install -r requirements-upos.txt
for section in 佛藏 医藏 道藏 儒藏; do
  HF_HUB_DISABLE_IMPLICIT_TOKEN=1 python3 scripts/tag_classical_chinese.py \
    --corpus ../daizhigev20 --sections "$section" --offset 10 --limit 50 \
    --output ./upos-tags
done
```

To process all Markdown files in the four sections, omit `--offset` and `--limit`. Existing `.conllu` files are skipped by default, so a run can be resumed. Add `--overwrite` to regenerate existing annotations. The script creates the corresponding output directories and mirrors the source paths under `--output`.

The Hugging Face model is public and does not require an access token. `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` prevents sending a locally saved token with public model requests.

To process a different selection, pass section names after `--sections`, for example:

```bash
HF_HUB_DISABLE_IMPLICIT_TOKEN=1 python3 scripts/tag_classical_chinese.py \
  --corpus ../daizhigev20 --sections 道藏 --offset 10 --limit 50 --output ./upos-tags
```

## Feasibility notebook notes

The notebook uses the CoNLL-U tokenization to count target characters only when they are represented as standalone tokens. It then embeds a context window around each occurrence with GuwenBERT and applies KMeans (`k=3`) separately to each target word. UPOS tags are not clustering features; annotation quality can still affect which occurrences enter the analysis. The clusters are exploratory and may reflect topic, genre, author, or grammatical role as well as meaning. Review the exported contexts before interpreting clusters as semantic categories.
