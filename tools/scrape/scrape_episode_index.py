#!/usr/bin/env python3
"""
Scrape episode titles+slugs from podscripts.co for two shows, save CSVs,
and print the title intersection (matched films).
Usage: python podscripts_scrape.py
Requires: pip install requests beautifulsoup4
"""
import csv, re, time, sys
import requests
from bs4 import BeautifulSoup

SHOWS = {
    "kill-james-bond": "kjb.csv",
    "the-bechdel-cast": "bechdel.csv",
}
BASE = "https://podscripts.co/podcasts/{show}/?page={page}"
HEADERS = {"User-Agent": "Mozilla/5.0 (research; episode-index)"}

def scrape_show(show):
    rows, page, seen = [], 1, set()
    while True:
        url = BASE.format(show=show, page=page)
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except Exception as e:
            print(f"  ! {show} p{page} error: {e}", file=sys.stderr); break
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        # episode links look like /podcasts/<show>/<slug>
        links = soup.select(f'a[href*="/podcasts/{show}/"]')
        new = 0
        for a in links:
            href = a.get("href", "")
            m = re.search(rf"/podcasts/{re.escape(show)}/([^/?#]+)", href)
            if not m:
                continue
            slug = m.group(1)
            if slug in ("", show) or slug in seen:
                continue
            title = a.get_text(strip=True)
            if not title:        # skip empty/nav links
                continue
            seen.add(slug)
            rows.append((title, slug))
            new += 1
        print(f"  {show} page {page}: +{new} (total {len(rows)})")
        if new == 0:             # no new episodes => past the last page
            break
        page += 1
        time.sleep(1.0)          # be polite
    return rows

def norm(title):
    """Normalise a title to a film key for matching."""
    t = title.lower()
    t = re.sub(r"^s?\d+e\d+(\.\d+)?[:\-\s]*", "", t)      # strip SxEx / episode numbers
    t = re.sub(r"\bwith\b.*$", "", t)                      # strip "with <guest>"
    t = re.sub(r"\(\d{4}\)", "", t)                        # strip year
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    t = re.sub(r"\b(the|a|an|live|preview|part|episode|qa)\b", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def main():
    catalogs = {}
    for show, fname in SHOWS.items():
        print(f"Scraping {show} ...")
        rows = scrape_show(show)
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["title", "slug", "film_key"])
            for title, slug in rows:
                w.writerow([title, slug, norm(title)])
        catalogs[show] = {norm(t): t for t, s in rows}
        print(f"  -> wrote {fname} ({len(rows)} eps)\n")

    a, b = list(SHOWS)
    shared = sorted(set(catalogs[a]) & set(catalogs[b]))
    print(f"\n=== {len(shared)} matched film keys ===")
    for k in shared:
        if k:
            print(f"  {k!r}\n     {a}: {catalogs[a][k]}\n     {b}: {catalogs[b][k]}")

if __name__ == "__main__":
    main()