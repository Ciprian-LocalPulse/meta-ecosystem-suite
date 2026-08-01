"""Lightweight text/regex compliance checker.

This module intentionally avoids heavy NLP dependencies so the
linter can run in CI without downloading models. It performs
case-insensitive pattern matching and simple heuristics; it is
designed to be swapped for a transformer-based classifier later
without changing the public API (`NLPChecker.scan`).
"""

import re
from dataclasses import dataclass


@dataclass
class Match:
    pattern: str
    span: tuple[int, int]
    snippet: str


class NLPChecker:
    """Scans free text against a list of regex patterns and phrases."""

    def __init__(self, patterns: list[str], phrases: list[str] | None = None):
        self._compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
        self._phrases = [p.lower() for p in (phrases or [])]

    def scan_patterns(self, text: str) -> list[Match]:
        matches: list[Match] = []
        for pattern in self._compiled:
            for m in pattern.finditer(text):
                start, end = max(0, m.start() - 10), min(len(text), m.end() + 10)
                matches.append(Match(pattern=pattern.pattern, span=m.span(), snippet=text[start:end].strip()))
        return matches

    def scan_phrases(self, text: str) -> list[str]:
        lowered = text.lower()
        return [phrase for phrase in self._phrases if phrase in lowered]

    @staticmethod
    def readability_flag(text: str, max_avg_word_len: float = 8.0) -> bool:
        """Cheap heuristic: flags text with unusually long average word
        length, which often indicates jargon-heavy or evasive copy."""
        words = [w for w in re.findall(r"[A-Za-z']+", text)]
        if not words:
            return False
        avg_len = sum(len(w) for w in words) / len(words)
        return avg_len > max_avg_word_len
