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
TOKEN_RE = re.compile(r"[^\W_]\w*(?:[+.-]\w+)*#?", re.UNICODE)
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

TOKEN_ALIASES: dict[str, tuple[str, ...]] = {
    "architecture": ("architectural",),
    "architectural": ("architecture",),
    "authority": ("authoritative",),
    "authoritative": ("authority",),
    "di": ("dependency", "injection", "composition"),
    "network": ("networked",),
    "networked": ("network",),
    "архитектура": ("architecture", "architectural"),
    "архитектуры": ("architecture", "architectural"),
    "асинхронность": ("async", "cancellation"),
    "авторитет": ("authority", "authoritative"),
    "авторитета": ("authority", "authoritative"),
    "граница": ("boundary", "boundaries"),
    "границы": ("boundary", "boundaries"),
    "зависимости": ("dependency", "dependencies", "di"),
    "игровой": ("gameplay",),
    "интерфейс": ("interface", "contract"),
    "интерфейсы": ("interface", "contracts"),
    "отмена": ("cancel", "cancellation"),
    "полномочия": ("authority", "authoritative"),
    "реактивность": ("reactive", "rx", "r3"),
    "сеть": ("network", "networked"),
    "сетевой": ("network", "networked"),
    "сетевого": ("network", "networked"),
    "сетевые": ("network", "networked"),
    "событие": ("event", "events"),
    "события": ("event", "events"),
    "состояние": ("state",),
    "состояния": ("state",),
    "слой": ("layer", "layers"),
    "слои": ("layer", "layers"),
    "тест": ("test", "testing"),
    "тесты": ("test", "testing"),
    "физика": ("physics",),
}


@dataclass
class Section:
    file_name: str
    heading: str
    body: str


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for match in TOKEN_RE.findall(text):
        token = match.casefold()
        if len(token) < 2 or token in STOP_WORDS:
            continue
        tokens.append(token)
        tokens.extend(TOKEN_ALIASES.get(token, ()))
    return list(dict.fromkeys(tokens))


def iter_sections(path: Path) -> Iterable[Section]:
    current_heading = path.stem.replace("-", " ").title()
    parent_h2: str | None = None
    body_lines: list[str] = []

    def build_section() -> Section | None:
        body = "\n".join(body_lines).strip()
        if not body:
            return None
        return Section(path.name, current_heading, body)

    for line in path.read_text(encoding="utf-8").splitlines():
        heading_match = HEADING_RE.match(line)
        if heading_match and len(heading_match.group(1)) in {2, 3}:
            section = build_section()
            if section is not None:
                yield section

            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if level == 2:
                parent_h2 = heading_text
                current_heading = heading_text
            else:
                current_heading = (
                    f"{parent_h2} > {heading_text}" if parent_h2 else heading_text
                )
            body_lines = []
            continue
        body_lines.append(line)

    section = build_section()
    if section is not None:
        yield section


def score_section(section: Section, query_tokens: list[str]) -> int:
    heading_token_list = tokenize(section.heading)
    heading_tokens = set(heading_token_list)
    body_tokens = set(tokenize(section.body))
    file_tokens = set(tokenize(section.file_name.replace("-", " ")))
    score = 0
    for token in query_tokens:
        if token in heading_tokens:
            score += 8
        elif token in body_tokens:
            score += 3
        elif token in file_tokens:
            score += 1
    if heading_token_list and heading_token_list[0] in query_tokens:
        score += 2
    return score


def summarize(text: str, limit: int = 180) -> str:
    single_line = re.sub(r"\s+", " ", text).strip()
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 3].rstrip() + "..."


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="Query text to rank against the references")
    parser.add_argument(
        "--top",
        type=positive_int,
        default=5,
        help="Number of sections to show",
    )
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
