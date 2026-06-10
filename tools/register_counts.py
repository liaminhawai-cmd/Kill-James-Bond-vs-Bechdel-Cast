#!/usr/bin/env python3
"""Quantitative register pass per ANALYTIC_BRIEF.md §7, run per transcript.

Usage: python3 tools/register_counts.py transcripts/the_rock_KJB.txt transcripts/the_rock_BC.txt

Counts are crude regex passes over ASR text — treat as directional, hand-check
specimens before citing. BC iHeart ad blocks are stripped via marker phrases
(dynamically-inserted ads; they reflect scrape date, not air date).
"""
import re
import sys
from pathlib import Path

AD_MARKER = re.compile(
    r"[^.]*?(?:iHeartRadio app, Apple Podcasts?|Apple Podcasts, or wherever you (?:get|stream))[^.]*\.",
)
AD_SHOWS = re.compile(
    r"(Daphne Caruana Galizia|Las Culturistas|Let's Talk Offline|Lucha Libre Behind the Mask)[^!]*?(wherever you (?:get|stream) (?:your )?podcasts\.)",
    re.S,
)
TIMESTAMP = re.compile(r"Starting point is [0-9:]+")

METRICS = {
    "hedges (I think/feel like/guess/dunno/kinda/sorta/maybe)": re.compile(
        r"\b(I think|I feel like|I guess|I don't know|I dunno|kind of|sort of|maybe)\b", re.I),
    "profanity (fuck/shit/ass*/bitch/damn)": re.compile(
        r"\b(fuck\w*|shit\w*|asshole|ass-?hole|bitch\w*|goddamn|damn)\b", re.I),
    "apology tokens (sorry/apologize/my bad)": re.compile(
        r"\b(sorry|apologi[sz]e\w*|my bad)\b", re.I),
    "first person singular (I/me/my)": re.compile(r"\b(I|me|my|mine)\b"),
    "first person plural (we/us/our)": re.compile(r"\b(we|us|our|ours)\b", re.I),
    "disgust lexicon (gross/hate/disgust/ew/infuriat/tired)": re.compile(
        r"\b(gross\w*|hate\w*|disgust\w*|ew+|ick\w*|infuriat\w*|i'm (?:so )?tired)\b", re.I),
    "anger lexicon (piece of shit/get fucked/prick/idiot/loser)": re.compile(
        r"\b(piece of shit|get fucked|prick|idiot\w*|loser\w*|moron\w*)\b", re.I),
}


def analyze(path: Path) -> None:
    text = TIMESTAMP.sub(" ", path.read_text(encoding="utf-8"))
    stripped = AD_SHOWS.sub(" ", text)
    words = len(stripped.split())
    print(f"\n=== {path.name} — {words:,} words (ads stripped: {len(text.split()) - words:,}) ===")
    for label, rx in METRICS.items():
        n = len(rx.findall(stripped))
        print(f"  {label:62} {n:>4}  ({1000 * n / words:5.1f}/1k)")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        analyze(Path(arg))
