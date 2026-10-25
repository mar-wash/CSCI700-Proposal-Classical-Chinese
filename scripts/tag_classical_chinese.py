#!/usr/bin/env python3
"""Generate CoNLL-U UPOS/dependency annotations for the Daizhige Markdown corpus.

Outputs are written to a separate directory, mirroring the corpus paths, with
one .conllu file per Markdown document. Existing outputs are skipped so a run
can be resumed.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import esupar


DEFAULT_CORPUS = Path(__file__).resolve().parents[1] / "daizhigev20"
DEFAULT_SECTIONS = ("佛藏", "医藏", "道藏", "儒藏")


def markdown_body(text: str) -> str:
    """Remove YAML front matter; leave the text and headings intact."""
    if text.startswith("---\n") or text.startswith("---\r\n"):
        lines = text.splitlines(keepends=True)
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "".join(lines[index + 1 :]).strip()
    return text.strip()


def split_for_model(text: str, tokenizer, max_tokens: int) -> list[str]:
    """Split into sentence-like inputs the tagger and dependency parser can handle."""
    # esupar treats each call as one sentence. Sentence boundaries also keep
    # dependency parsing from receiving an entire book as one giant sentence.
    pieces = [part for part in re.split(r"(?<=[。！？；.!?;])|(?<=\n)", text) if part]
    chunks: list[str] = []
    current = ""

    def token_count(value: str) -> int:
        return len(tokenizer(value, add_special_tokens=True, truncation=False)["input_ids"])

    def append_long(value: str) -> None:
        """Break a sentence with no usable boundary into tokenizer-safe spans."""
        nonlocal current
        start = 0
        while start < len(value):
            low, high = start + 1, len(value)
            while low < high:
                middle = (low + high + 1) // 2
                if token_count(value[start:middle]) <= max_tokens:
                    low = middle
                else:
                    high = middle - 1
            end = low
            if end <= start:
                raise ValueError(f"Cannot fit a character within the {max_tokens}-token limit")
            # Prefer ending at punctuation or whitespace near the hard limit.
            if end < len(value):
                floor = max(start + 1, end - 100)
                boundary = max(value.rfind(mark, floor, end) for mark in "，。！？；、 \t\n")
                if boundary >= floor:
                    end = boundary + 1
            span = value[start:end]
            if current:
                chunks.append(current)
                current = ""
            chunks.append(span)
            start = end

    for piece in pieces:
        if token_count(piece) > max_tokens:
            if current:
                chunks.append(current)
                current = ""
            append_long(piece)
        elif current and token_count(current + piece) > max_tokens:
            chunks.append(current)
            current = piece
        else:
            current += piece
    if current:
        chunks.append(current)
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--output", type=Path, default=DEFAULT_CORPUS.parent / "upos-tags")
    parser.add_argument("--sections", nargs="+", default=DEFAULT_SECTIONS)
    parser.add_argument("--limit", type=int, help="Process only the first N files (for a pilot).")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=450,
        help="Maximum tokenizer tokens per sentence passed to esupar (default: 450; model limit: 512).",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace existing output files.")
    args = parser.parse_args()

    sources = sorted(
        path
        for section in args.sections
        for path in (args.corpus / section).rglob("*.md")
    )
    if args.limit is not None:
        sources = sources[: args.limit]

    # esupar maps `lzh` to KoichiYasuoka/roberta-classical-chinese-base-upos.
    nlp = esupar.load("lzh")
    successes = skipped = failures = 0
    for index, source in enumerate(sources, start=1):
        relative = source.relative_to(args.corpus)
        destination = (args.output / relative).with_suffix(".conllu")
        if destination.exists() and not args.overwrite:
            skipped += 1
            continue
        try:
            body = markdown_body(source.read_text(encoding="utf-8"))
            if not body:
                raise ValueError("document body is empty")
            chunks = split_for_model(body, nlp.tokenizer, args.max_tokens)
            tagged = "\n\n".join(str(nlp(chunk)).strip() for chunk in chunks if chunk.strip())
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(tagged.rstrip() + "\n", encoding="utf-8")
            successes += 1
            print(f"[{index}/{len(sources)}] tagged {relative}", flush=True)
        except Exception as error:  # keep processing the rest of the corpus
            failures += 1
            print(f"[{index}/{len(sources)}] ERROR {relative}: {error}", flush=True)

    print(f"Done: {successes} tagged, {skipped} skipped, {failures} failed.")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
