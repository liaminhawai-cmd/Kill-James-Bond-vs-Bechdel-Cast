#!/usr/bin/env python3
"""
Transcript scraper v4 - corrected slugs verified from podscripts index pages.
Uses requests (not Playwright) since podscripts serves content statically.
Run: py download_transcripts_v4.py
"""
import os, re, time, requests
from bs4 import BeautifulSoup

# Verified slugs from podscripts index pages
# Format: (show-slug, episode-slug, output-filename)
MATCHES = [
    # KJB - verified from index
    ("kill-james-bond", "s4e22-point-break",                          "kjb_point_break"),
    ("kill-james-bond", "s4e24-casino-royale-2006",                   "kjb_casino_royale"),
    ("kill-james-bond", "s4e23-austin-powers",                        "kjb_austin_powers"),
    ("kill-james-bond", "s4e30-the-fast-and-the-furious",             "kjb_fast_furious"),
    # These need verification - will try likely slugs:
    ("kill-james-bond", "s3e10-atomic-blonde",                        "kjb_atomic_blonde"),
    ("kill-james-bond", "s3e03-the-birdcage",                         "kjb_the_birdcage"),
    ("kill-james-bond", "s2e19-die-hard",                             "kjb_die_hard"),
    ("kill-james-bond", "s3e09-oceans-eleven",                        "kjb_oceans_eleven"),
    ("kill-james-bond", "s3e13-romy-and-michele",                     "kjb_romy_michele"),
    ("kill-james-bond", "s4e25-spice-world-preview",                  "kjb_spice_world"),
    ("kill-james-bond", "s3e19-what-women-want",                      "kjb_what_women_want"),
    ("kill-james-bond", "s3e08-the-rock",                             "kjb_the_rock"),
    ("kill-james-bond", "s4e305-sex-and-the-city",                    "kjb_satc"),
    # BC - these worked before
    ("the-bechdel-cast", "point-break-with-anita-sarkeesian",         "bc_point_break"),
    ("the-bechdel-cast", "casino-royale-with-kenice-mobley",          "bc_casino_royale"),
    ("the-bechdel-cast", "austin-powers-with-atsuko-okatsuka",        "bc_austin_powers"),
    ("the-bechdel-cast", "atomic-blonde-with-jenny-slate",            "bc_atomic_blonde"),
    ("the-bechdel-cast", "the-birdcage",                              "bc_the_birdcage"),
    ("the-bechdel-cast", "die-hard",                                  "bc_die_hard"),
    ("the-bechdel-cast", "fast-and-furious",                          "bc_fast_furious"),
    ("the-bechdel-cast", "oceans-eleven",                             "bc_oceans_eleven"),
    ("the-bechdel-cast", "romy-and-michele-with-carmen-maria-machado","bc_romy_michele"),
    ("the-bechdel-cast", "spice-world-with-amanda-meadows",           "bc_spice_world"),
    ("the-bechdel-cast", "what-women-want",                           "bc_what_women_want"),
    ("the-bechdel-cast", "the-rock",                                  "bc_the_rock"),
    ("the-bechdel-cast", "sex-and-the-city-with-caitlin-durant",      "bc_satc"),
]

BASE    = "https://podscripts.co/podcasts"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
OUTDIR  = "transcripts"
os.makedirs(OUTDIR, exist_ok=True)

def fetch(show, slug, name):
    path = os.path.join(OUTDIR, f"{name}.txt")
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        print(f"  ✓ {name} — already have it")
        return True

    url = f"{BASE}/{show}/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"  ✗ {name} — {e}")
        return False

    soup = BeautifulSoup(r.text, "html.parser")

    # Check for "Episode Not Found" modal
    if "Episode Not Found" in r.text or "episode-not-found" in r.text.lower():
        print(f"  ✗ {name} — Episode Not Found (bad slug)")
        return False

    # Extract transcript: look for the longest text block
    # podscripts puts transcript in <p> tags with timestamps
    paras = soup.find_all("p")
    text_blocks = [p.get_text(" ", strip=True) for p in paras if len(p.get_text(strip=True)) > 50]
    
    if not text_blocks:
        # Fallback: try article or main
        for tag in ["article", "main"]:
            el = soup.find(tag)
            if el:
                t = el.get_text("\n", strip=True)
                if len(t) > 5000:
                    text_blocks = [t]
                    break

    text = "\n\n".join(text_blocks)
    text = re.sub(r"\n\n\n+", "\n\n", text).strip()

    # Sanity check: must contain "Starting point" or real dialogue
    if len(text) < 5000 or ("Starting point" not in text and len(text) < 20000):
        print(f"  ? {name} — {len(text):,} chars (may be homepage/stub, saving anyway)")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  ✓ {name} — {len(text):,} chars")
    time.sleep(2.5)
    return True

def main():
    print(f"Downloading {len(MATCHES)} transcripts to ./{OUTDIR}/\n")
    ok, fail = 0, 0
    for show, slug, name in MATCHES:
        if fetch(show, slug, name):
            ok += 1
        else:
            fail += 1
    print(f"\n=== {ok} ok, {fail} failed ===")
    print(f"\nCheck ./{OUTDIR}/ — files marked '?' may need slug correction.")

if __name__ == "__main__":
    main()
