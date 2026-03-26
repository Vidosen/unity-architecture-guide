#!/usr/bin/env python3
"""
Rank relevant architecture guidance sections for a free-form Unity query.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REFERENCE_DIR = Path(__file__).resolve().parent.parent / "references"
TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9+#.-]{1,}")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "when",
    "what",
    "where",
    "which",
    "как",
    "для",
    "или",
    "это",
    "если",
    "надо",
    "нужно",
    "unity",
}


@dataclass
class Section:
    file_name: str
    heading: str
    body: str


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if len(token) > 2 and token.lower() not in STOP_WORDS
    ]


def iter_sections(path: Path) -> Iterable[Section]:
    heading = path.stem.replace("-", " ").title()
    body_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        heading_match = HEADING_RE.match(line)
        if heading_match and heading_match.group(1) in {"##", "###"}:
            if body_lines:
                yield Section(path.name, heading, "\n".join(body_lines).strip())
            heading = heading_match.group(2).strip()
            body_lines = []
            continue
        body_lines.append(line)
    if body_lines:
        yield Section(path.name, heading, "\n".join(body_lines).strip())


def score_section(section: Section, query_tokens: list[str]) -> int:
    haystack = f"{section.heading}\n{section.body}".lower()
    heading_tokens = set(tokenize(section.heading))
    score = 0
    for token in query_tokens:
        if token in heading_tokens:
            score += 6
        elif token in haystack:
            score += 2
    if any(word in section.file_name for word in ("reference", "practice")):
        score += 0
    return score


def summarize(text: str, limit: int = 180) -> str:
    single_line = re.sub(r"\s+", " ", text).strip()
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 3].rstrip() + "..."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="Query text to rank against the references")
    parser.add_argument("--top", type=int, default=5, help="Number of sections to show")
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    query_tokens = tokenize(query)
    if not query_tokens:
        print("No searchable tokens in query.")
        return 1

    ranked: list[tuple[int, Section]] = []
    for ref_path in sorted(REFERENCE_DIR.glob("*.md")):
        for section in iter_sections(ref_path):
            score = score_section(section, query_tokens)
            if score > 0:
                ranked.append((score, section))

    ranked.sort(key=lambda item: (-item[0], item[1].file_name, item[1].heading))

    if not ranked:
        print("No matching sections found.")
        return 1

    print(f'Query: "{query}"')
    print()
    for index, (score, section) in enumerate(ranked[: args.top], start=1):
        print(f"{index}. [{section.file_name}] {section.heading} (score={score})")
        print(f"   {summarize(section.body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
