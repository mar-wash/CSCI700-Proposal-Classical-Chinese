# Classical Chinese UPOS pilot annotations

This repository contains a 40-document pilot of automatic tokenization, part-of-speech tagging, and dependency parsing for texts from the 佛藏, 医藏, 道藏, and 儒藏 sections of the Daizhige corpus.

## Contents

- `佛藏/`, `医藏/`, `道藏/`, and `儒藏/`: CoNLL-U files arranged in the same subfolder structure as the source corpus.
- `scripts/tag_classical_chinese.py`: script used to generate the annotations and to process additional source documents.
- `requirements-upos.txt`: Python dependency list (`esupar`).

The pilot contains the first 10 Markdown files, in sorted path order, from each of the four sections: 40 files total. The `.conllu` files contain predicted annotations; they have not been manually reviewed.

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

Use Python 3. The first run downloads the model from Hugging Face and requires network access. From this repository's directory, with the original corpus available at `../daizhigev20`, install the dependency and process the pilot-sized sample:

```bash
python3 -m pip install -r requirements-upos.txt
HF_HUB_DISABLE_IMPLICIT_TOKEN=1 python3 scripts/tag_classical_chinese.py \
  --corpus ../daizhigev20 --limit 10 --output ./pilot-output
```

To process the full four sections, omit `--limit 10` and set `--output .` to place results in this repository. Existing `.conllu` files are skipped by default, so the pilot files will be retained and the run can be resumed. Add `--overwrite` to regenerate existing annotations.

The Hugging Face model is public and does not require an access token. `HF_HUB_DISABLE_IMPLICIT_TOKEN=1` prevents sending a locally saved token with public model requests.

To process a different selection, pass section names after `--sections`, for example:

```bash
HF_HUB_DISABLE_IMPLICIT_TOKEN=1 python3 scripts/tag_classical_chinese.py \
  --corpus ../daizhigev20 --sections 道藏 --limit 10 --output ./pilot-output
```
