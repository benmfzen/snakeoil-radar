"""Evidence — ground fact-check verdicts in REAL, retrievable literature.

Uses NCBI PubMed E-utilities (free, no API key, ~3 req/s polite limit).
The hard rule this module enforces: a verdict may only cite what this module
actually returned. If no evidence comes back, the claim is UNVERIFIED — never
invent a citation. (Same fail-closed pattern as the Warhammer verify.py gate.)
"""
import json, time, subprocess, urllib.parse

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = "snakeoil-radar/0.1 (research tool)"


def _get(url: str, timeout: int = 30) -> bytes:
    # curl instead of urllib: sidesteps macOS python.org-build cert issues
    p = subprocess.run(
        ["curl", "-s", "--max-time", str(timeout), "-A", UA, url],
        capture_output=True, timeout=timeout + 10,
    )
    if p.returncode != 0 or not p.stdout:
        raise RuntimeError(f"fetch failed rc={p.returncode} for {url[:80]}")
    return p.stdout


def search(query: str, n: int = 5, prefer_reviews: bool = True) -> list:
    """PubMed search -> [{pmid,title,journal,year,pubtypes,abstract,url}].

    prefer_reviews: try meta-analyses/systematic reviews first (highest evidence
    tier), fall back to any article type if none found.
    """
    def _esearch(q):
        u = f"{BASE}/esearch.fcgi?db=pubmed&retmode=json&retmax={n}&sort=relevance&term=" + urllib.parse.quote(q)
        return json.loads(_get(u))["esearchresult"].get("idlist", [])

    ids = []
    if prefer_reviews:
        ids = _esearch(f"({query}) AND (meta-analysis[pt] OR systematic review[pt] OR review[pt])")
    if not ids:
        ids = _esearch(query)
    if not ids:
        return []
    time.sleep(0.4)  # polite spacing
    u = f"{BASE}/efetch.fcgi?db=pubmed&retmode=xml&id=" + ",".join(ids)
    xml = _get(u).decode("utf-8", errors="replace")
    return _parse_efetch(xml)


def _parse_efetch(xml: str) -> list:
    """Minimal, dependency-free XML pull of the fields we cite."""
    import re
    out = []
    for art in re.split(r"</PubmedArticle>", xml)[:-1]:
        def grab(pat, flags=re.S):
            m = re.search(pat, art, flags)
            return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None
        pmid = grab(r"<PMID[^>]*>(\d+)</PMID>")
        if not pmid:
            continue
        abstract = " ".join(
            re.sub(r"<[^>]+>", "", t).strip()
            for t in re.findall(r"<AbstractText[^>]*>(.+?)</AbstractText>", art, re.S)
        ) or None
        out.append({
            "pmid": pmid,
            "title": grab(r"<ArticleTitle>(.+?)</ArticleTitle>"),
            "journal": grab(r"<Title>(.+?)</Title>"),
            "year": grab(r"<PubDate>.*?<Year>(\d{4})</Year>"),
            "pubtypes": re.findall(r"<PublicationType[^>]*>([^<]+)</PublicationType>", art),
            "abstract": abstract,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })
    return out


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "artificial sweeteners weight management randomized"
    for r in search(q, n=3):
        print(f"- [{r['year']}] {r['title']}  ({r['journal']})")
        print(f"  {r['url']}  · types: {', '.join(r['pubtypes'][:3])}")
        if r["abstract"]:
            print(f"  {r['abstract'][:220]}…")
        print()
