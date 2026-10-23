"""Interroge Wikidata pour chaque personnage de DATAS/characters.csv (colonne id).

Récupère les liens familiaux et des informations complémentaires via l'API
wbgetentities (50 entités par appel), puis les enregistre dans
DATAS/wikidata.json (cache utilisé par build_graph.py). Les lieux sont récupérés
à part, en SPARQL, par fetch_places.py.

Usage : .venv/bin/python fetch_wikidata.py
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
OUT = ROOT / "DATAS" / "wikidata.json"
API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "LinkedImmortals/0.2 (projet personnel, mythologie grecque)"
BATCH = 50

# propriétés dont la valeur est une autre entité
ENTITY_PROPS = {
    "P22": "father",
    "P25": "mother",
    "P26": "spouse",
    "P451": "partner",
    "P40": "child",
    "P3373": "sibling",
    "P1038": "relative",
    "P1441": "present_in_work",
    "P460": "same_as",
    "P2925": "deity_domain",
    "P4185": "symbol",
    "P1049": "worshipped_by",
    "P361": "part_of",
}


def wbgetentities(ids, props, retries=8):
    params = {"action": "wbgetentities", "ids": "|".join(ids), "props": props,
              "languages": "fr|en|el|la", "languagefallback": "1",
              "sitefilter": "frwiki|enwiki", "format": "json", "maxlag": "5"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
            if "error" in data:
                raise RuntimeError(data["error"].get("info"))
            return data["entities"]
        except Exception as exc:  # noqa: BLE001 — réseau, 429, maxlag…
            retry_after = getattr(exc, "headers", None) and exc.headers.get("Retry-After")
            wait = int(retry_after) if retry_after and retry_after.isdigit() else 15 * (attempt + 1)
            print(f"  erreur ({exc}), nouvel essai dans {wait}s")
            time.sleep(wait)
    raise RuntimeError("Wikidata ne répond pas")


def batches(seq):
    for i in range(0, len(seq), BATCH):
        yield seq[i:i + BATCH]
        time.sleep(0.5)


def label(entity, lang):
    """Libellé dans la langue demandée, en ignorant les valeurs de repli (autre langue) de languagefallback."""
    value = entity.get("labels", {}).get(lang, {})
    return value.get("value") if value.get("language") == lang else None


def main():
    chars = pd.read_csv(ROOT / "DATAS" / "characters.csv")
    qids = sorted(set(chars["id"].dropna()))
    data, referenced = {}, set()

    for n, chunk in enumerate(batches(qids), 1):
        print(f"personnages : lot {n}/{(len(qids) - 1) // BATCH + 1}")
        for q, ent in wbgetentities(chunk, "labels|descriptions|claims|sitelinks").items():
            claims = {}
            for prop, name in ENTITY_PROPS.items():
                for c in ent.get("claims", {}).get(prop, []):
                    v = c["mainsnak"].get("datavalue", {}).get("value")
                    if isinstance(v, dict) and "id" in v:
                        claims.setdefault(name, []).append({"qid": v["id"]})
                        referenced.add(v["id"])
            image = [c["mainsnak"].get("datavalue", {}).get("value")
                     for c in ent.get("claims", {}).get("P18", [])]
            sitelinks = ent.get("sitelinks", {})
            info = {
                "fr": label(ent, "fr"),
                "frDesc": label({"labels": ent.get("descriptions", {})}, "fr"),
                "el": label(ent, "el"),
                "la": label(ent, "la"),
                "image": image[0] if image and image[0] else None,
                "frwiki": sitelinks.get("frwiki", {}).get("title"),
                "enwiki": sitelinks.get("enwiki", {}).get("title"),
            }
            data[q] = {"info": {k: v for k, v in info.items() if v}, "claims": claims}

    # libellés français et anglais des entités référencées
    labels = {}
    refs = sorted(referenced)
    for n, chunk in enumerate(batches(refs), 1):
        print(f"libellés : lot {n}/{(len(refs) - 1) // BATCH + 1}")
        for q, ent in wbgetentities(chunk, "labels").items():
            en = label(ent, "en") or label(ent, "fr") or q
            labels[q] = (label(ent, "fr") or en, en)
    for d in data.values():
        for values in d["claims"].values():
            for v in values:
                v["label"], v["label_en"] = labels.get(v["qid"], (v["qid"], v["qid"]))

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    n_family = sum(len(d["claims"].get(k, [])) for d in data.values()
                   for k in ("father", "mother", "spouse", "partner", "child", "sibling"))
    print(f"{len(data)} entités, {n_family} liens familiaux -> {OUT}")


if __name__ == "__main__":
    main()
