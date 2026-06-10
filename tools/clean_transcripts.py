#!/usr/bin/env python3
"""Clean podscripts.co scrapes into the corpus files defined in ANALYTIC_BRIEF.md §3.

Method (as documented in the brief): raw pages contain the transcript repeated
~16x plus navigation junk. Each copy begins at a "Starting point is 00:00:0x"
marker. We split on those markers, keep the longest copy, and trim the
comments/footer block. Already-clean files pass through unchanged.
"""
import re
import sys
from pathlib import Path

SRC = Path("transcripts")
OUT = Path("transcripts_clean")

# source filename -> brief-convention target ({film}_{SHOW}.txt, _preview flag)
MAPPING = {
    # Tier 1
    "kill-james-bond_s4e22-point-break.txt": "point_break_KJB.txt",
    "bc_point_break_with_anita_sarkeesian.txt": "point_break_BC.txt",
    "kill-james-bond_episode-24-casino-royale-2006.txt": "casino_royale_KJB.txt",
    "bc_casino_royale_with_kenice_mobley.txt": "casino_royale_BC.txt",
    "kill-james-bond_s2e23-austin-powers-live.txt": "austin_powers_KJB.txt",
    "bc_austin_powers_with_atsuko_okatsuka.txt": "austin_powers_BC.txt",
    "kill-james-bond_s2e22-atomic-blonde.txt": "atomic_blonde_KJB.txt",
    "the-bechdel-cast_atomic-blonde-with-vanessa-guerrero.txt": "atomic_blonde_BC.txt",
    "kill-james-bond_kjb-holiday-special-die-hard.txt": "die_hard_KJB.txt",
    "the-bechdel-cast_die-hard-with-debra-digiovanni.txt": "die_hard_BC.txt",
    "kill-james-bond_s4e30-the-fast-and-the-furious.txt": "fast_furious_KJB.txt",
    "bc_the_fast_and_the_furious.txt": "fast_furious_BC.txt",
    "Kill-james-bond-ocean's-eleven.txt": "oceans_eleven_KJB.txt",
    "the-bechdel-cast_oceans-eleven-with-edgar-momplaisir.txt": "oceans_eleven_BC.txt",
    "kill-james-bond_episode-22-the-rock.txt": "the_rock_KJB.txt",
    "the-bechdel-cast_the-rock-with-miles-gray.txt": "the_rock_BC.txt",
    # Tier 2 (KJB Patreon previews + BC full)
    "kill-james-bond_s3e215-the-birdcage-preview.txt": "birdcage_KJB_preview.txt",
    "the-bechdel-cast_the-birdcage-with-manuel-betancourt.txt": "birdcage_BC.txt",
    "kill-james-bond_s3e175-romy-and-micheles-high-school-reunion-preview.txt": "romy_michele_KJB_preview.txt",
    "the-bechdel-cast_romy-and-micheles-high-school-reunion-with-danielle-perez.txt": "romy_michele_BC.txt",
    "kill-james-bond_s4e25-spice-world-preview.txt": "spice_world_KJB_preview.txt",
    "the-bechdel-cast_spice-world-with-amanda-meadows.txt": "spice_world_BC.txt",
    "kill-james-bond_s3e245-what-women-want-preview.txt": "what_women_want_KJB_preview.txt",
    "the-bechdel-cast_what-women-want-with-laci-mosley.txt": "what_women_want_BC.txt",
    "kill-james-bond_s4e305-sex-and-the-city.txt": "satc_KJB_preview.txt",
    "the-bechdel-cast_sex-and-the-city-the-movie-with-megan-gailey.txt": "satc_BC.txt",
    # Off-corpus extras (no BC counterpart): kept under extras/
    "kill-james-bond_s2e24-austin-powers-the-spy-who-shagged-me-live.txt": "extras/austin_powers_2_KJB.txt",
    "kill-james-bond_s2e25-austin-powers-goldmember-live.txt": "extras/austin_powers_3_KJB.txt",
}

COPY_MARKER = re.compile(r"(?=Starting point is 00:00:0\d)")
FOOTER = re.compile(
    r"(There aren't comments yet for this episode.*|© PodScripts\.co.*)$",
    re.S,
)


def clean(text: str) -> str:
    copies = [c for c in COPY_MARKER.split(text) if "Starting point is" in c]
    body = max(copies, key=len) if copies else text
    body = FOOTER.sub("", body)
    return body.strip() + "\n"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "extras").mkdir(exist_ok=True)
    rows = []
    for src_name, dst_name in MAPPING.items():
        src = SRC / src_name
        text = src.read_text(encoding="utf-8", errors="replace")
        n_copies = len(COPY_MARKER.split(text)) - 1
        cleaned = clean(text)
        (OUT / dst_name).write_text(cleaned, encoding="utf-8")
        rows.append((dst_name, len(text), max(n_copies, 1), len(cleaned)))
    rows.sort()
    print(f"{'target':42} {'raw':>9} {'copies':>6} {'clean':>9}")
    for name, raw, copies, cleaned in rows:
        print(f"{name:42} {raw:>9} {copies:>6} {cleaned:>9}")


if __name__ == "__main__":
    main()
