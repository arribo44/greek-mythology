"""Lieux des personnages (naissance, décès, résidence, inhumation) via le service SPARQL de Wikidata.

Une requête par lot de 300 personnages : libellés fr/en et coordonnées sont obtenus dans la
même réponse. Un lieu sans coordonnées (ville mythique, région…) prend celles de son lieu
englobant (P131 division administrative, P706 relief, P276 localisation), sur deux niveaux.
Résultat : DATAS/places.json, lu par build_graph.py.

Usage : .venv/bin/python fetch_places.py
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
OUT = ROOT / "DATAS" / "places.json"
ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "LinkedImmortals/0.4 (projet personnel, mythologie grecque)"
BATCH = 300
KINDS = {"P19": "birth", "P20": "death", "P551": "residence", "P119": "burial"}

QUERY = """
SELECT ?item ?kind ?place ?fr ?en ?coord ?parentCoord WHERE {{
  VALUES ?item {{ {items} }}
  VALUES (?p ?kind) {{ {kinds} }}
  ?item ?p ?place .
  OPTIONAL {{ ?place rdfs:label ?fr . FILTER(lang(?fr) = "fr") }}
  OPTIONAL {{ ?place rdfs:label ?en . FILTER(lang(?en) = "en") }}
  OPTIONAL {{ ?place wdt:P625 ?coord }}
  OPTIONAL {{
    FILTER NOT EXISTS {{ ?place wdt:P625 [] }}
    ?place (wdt:P131|wdt:P706|wdt:P276)/((wdt:P131|wdt:P706|wdt:P276)?) ?parent .
    ?parent wdt:P625 ?parentCoord .
  }}
}}"""


def sparql(query, retries=6):
    data = urllib.parse.urlencode({"query": query}).encode()
    req = urllib.request.Request(ENDPOINT, data=data, headers={
        "User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.load(resp)["results"]["bindings"]
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 30 * (attempt + 1)
            print(f"  SPARQL indisponible ({exc.code}), nouvel essai dans {wait}s")
            time.sleep(wait)


def qid(uri):
    return uri.rsplit("/", 1)[-1]


def point(wkt):
    """« Point(23.72 37.97) » -> (lat, lon) ; None si autre globe (Mars, Lune…)."""
    if not wkt.startswith("Point("):
        return None
    lon, lat = map(float, re.findall(r"-?[\d.]+(?:E-?\d+)?", wkt)[:2])
    return round(lat, 4), round(lon, 4)


def main():
    chars = pd.read_csv(ROOT / "DATAS" / "characters.csv")
    qids = sorted(set(chars["id"]))
    kinds = " ".join(f'(wdt:{p} "{k}")' for p, k in KINDS.items())
    places, links = {}, set()

    for i in range(0, len(qids), BATCH):
        chunk = qids[i:i + BATCH]
        print(f"lot {i // BATCH + 1}/{(len(qids) - 1) // BATCH + 1}")
        rows = sparql(QUERY.format(items=" ".join(f"wd:{q}" for q in chunk), kinds=kinds))
        for r in rows:
            place = qid(r["place"]["value"])
            if not place.startswith("Q"):          # valeur « inconnue » ou anonyme
                continue
            links.add((qid(r["item"]["value"]), r["kind"]["value"], place))
            p = places.setdefault(place, {"fr": None, "en": None})
            p["fr"] = p["fr"] or r.get("fr", {}).get("value")
            p["en"] = p["en"] or r.get("en", {}).get("value")
            if "lat" not in p:
                own = point(r["coord"]["value"]) if "coord" in r else None
                parent = point(r["parentCoord"]["value"]) if "parentCoord" in r else None
                if own or parent:
                    p["lat"], p["lon"] = own or parent
                    p["approx"] = own is None   # coordonnées du lieu englobant
        time.sleep(2)

    for q, p in places.items():
        p["en"] = p["en"] or p["fr"] or q
        p["fr"] = p["fr"] or p["en"]
    out = {"places": places, "links": [{"character": c, "kind": k, "place": p} for c, k, p in sorted(links)]}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))

    located = sum(1 for p in places.values() if "lat" in p)
    print(f"{len(places)} lieux ({located} avec coordonnées, dont "
          f"{sum(1 for p in places.values() if p.get('approx'))} approchées) -> {OUT}")
    for kind in KINDS.values():
        people = {c for c, k, _ in links if k == kind}
        print(f"  {kind} : {len(people)} personnages")
    print(f"  au moins un lieu : {len({c for c, _, _ in links})} personnages")


if __name__ == "__main__":
    main()
