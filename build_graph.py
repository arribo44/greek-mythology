"""Charge les CSV de DATAS/ dans une base graphe Kùzu (Cypher, embarquée).

Schéma :
    (:Immortal)-[:CONNECTED {mentions, weight, works}]-(:Immortal)   co-apparitions
    (:Immortal)-[:APPEARS_IN {mentions}]->(:Work)                     œuvres
    (:Immortal)-[:FEATURED_IN {mentions}]->(:Episode)                 mythes / chants
    (:Episode)-[:PART_OF]->(:Work)
    (:Immortal)-[:PARENT_OF {role, source}]->(:Immortal)              famille
    (:Immortal)-[:SPOUSE_OF {kind, source}]-(:Immortal)
    (:Immortal)-[:SIBLING_OF {source}]-(:Immortal)
    (:Immortal)-[:SAID]->(:Quote)-[:ADDRESSED_TO]->(:Immortal)        citations Wikiquote
    (:Quote)-[:ABOUT]->(:Immortal)
    (:Quote)-[:MENTIONS]->(:Immortal)                                 autres personnages nommés
    (:Immortal)-[:BORN_IN|DIED_IN|LIVED_IN|BURIED_IN|VISITED {source}]->(:Place)
                                                                      lieux Wikidata + textes antiques

Chaque libellé affiché existe en anglais (propriété « name », « title »…) et en
français (suffixe « _fr ») : Wikidata / Wikipédia pour les personnages (corrections dans
DATAS/names_fr.csv), DATAS/works_fr.csv et
DATAS/episodes_fr.csv pour les œuvres et les mythes.

Les présentations des œuvres viennent de DATAS/works_wiki.json (fetch_works.py, Wikipédia).

Les lieux viennent de DATAS/places.json (fetch_places.py, SPARQL) complété par
DATAS/places_manual.csv (coordonnées manquantes ou erronées) et DATAS/places_fr.csv
(noms français des tombeaux et lieux sans libellé français dans Wikidata).
DATAS/places_textes.csv ajoute des liens tirés des textes antiques (Bibliothèque d'Apollodore),
avec leur référence, dont les passages (« visit ») absents de Wikidata.

Les citations viennent de DATAS/quotes.csv (créé par fetch_wikiquote.py, à relire).

Les liens familiaux viennent de Wikidata (cache DATAS/wikidata.json, créé par
fetch_wikidata.py) et des descriptions du CSV (« son of X », « wife of Y »…).

Usage : .venv/bin/python build_graph.py
"""
import ast
import json
import unicodedata
import re
import shutil
import urllib.parse
from pathlib import Path

import kuzu
import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "DATAS"
DB_PATH = ROOT / "graph.kuzu"
PORTRAITS = ROOT / "static" / "portraits"   # vignettes personnalisées : « Nom_xxxx.png » (nom français ou anglais)
PORTRAIT_PRIORITY = [".png", ".webp", ".jpg", ".jpeg", ".svg"]   # plusieurs vignettes : la première de la liste gagne
WIKIDATA = DATA / "wikidata.json"
COMMONS = "https://commons.wikimedia.org/wiki/Special:FilePath/{}?width=320"

# Regroupement des types Wikidata en "clans" (utilisés pour avatars / couleurs)
CLAN_BY_TYPE = {
    "Olympian god": "Olympien",
    "titan": "Titan",
    "Greek primordial deity": "Primordial",
    "Giants": "Géant",
    "cyclops": "Monstre",
    "Hecatoncheires": "Monstre",
    "centaur": "Monstre",
    "satyr": "Monstre",
    "daemon": "Daïmon",
    "allegorical Greek deity": "Allégorie",
    "Anemoi": "Vent",
    "demigod of Greek mythology": "Demi-dieu",
    "sibyl": "Oracle",
}
CLAN_BY_LEVEL3 = {
    "Greek nymph": "Nymphe",
    "Greek water deities": "Aquatique",
    "titan": "Titan",
    "Greek primordial deity": "Primordial",
    "Giants": "Géant",
    "Olympian god": "Olympien",
    "allegorical Greek deity": "Allégorie",
    "daemon": "Daïmon",
    "Anemoi": "Vent",
    "demigod of Greek mythology": "Demi-dieu",
    "chthonic deities": "Chthonien",
}


def parse_list(value):
    if not isinstance(value, str) or not value.startswith("["):
        return []
    try:
        return [str(v) for v in ast.literal_eval(value)]
    except (ValueError, SyntaxError):
        return []


def clan_of(row):
    if row["type"] in CLAN_BY_TYPE:
        return CLAN_BY_TYPE[row["type"]]
    if row["level3"] in CLAN_BY_LEVEL3:
        return CLAN_BY_LEVEL3[row["level3"]]
    if row["level2"] == "Greek deity":
        return "Divinité"
    return "Mortel"


# « son of X and Y », « wife of X »… -> (relation, noms)
KIN_PATTERN = re.compile(
    r"\b(son|daughter|child|children|offspring|wife|husband|consort|spouse|mother|father|"
    r"sister|brother|twin|lover)s? of ([A-Z][\w'-]+(?:(?:,| and| &) [A-Z][\w'-]+)*)")
KIN_KIND = {
    "son": "child_of", "daughter": "child_of", "child": "child_of", "children": "child_of",
    "offspring": "child_of", "mother": "parent_of", "father": "parent_of",
    "wife": "spouse", "husband": "spouse", "consort": "spouse", "spouse": "spouse",
    "lover": "partner", "sister": "sibling", "brother": "sibling", "twin": "sibling",
}


def wikidata_cache():
    if not WIKIDATA.exists():
        print("(pas de DATAS/wikidata.json : lancez fetch_wikidata.py pour enrichir les profils)")
        return {}
    return json.loads(WIKIDATA.read_text())


def family_links(chars, wd):
    """Renvoie une liste de liens (kind, a, b, role, source) entre personnages du jeu de données.

    kind = parent (a parent de b), spouse, partner ou sibling.
    """
    by_qid = dict(zip(chars["id"], chars["name"]))
    gender = dict(zip(chars["name"], chars["gender"].fillna("")))
    links = []

    for q, entry in wd.items():
        me = by_qid.get(q)
        claims = entry.get("claims", {})
        for prop, kind in [("father", "parent"), ("mother", "parent"), ("child", "child"),
                           ("spouse", "spouse"), ("partner", "partner"), ("sibling", "sibling")]:
            for v in claims.get(prop, []):
                other = by_qid.get(v["qid"])
                if not other or other == me:
                    continue
                if kind == "parent":
                    links.append(("parent", other, me, prop, "wikidata"))
                elif kind == "child":
                    links.append(("parent", me, other, None, "wikidata"))
                else:
                    links.append((kind, me, other, None, "wikidata"))

    # index des noms et alias (on ignore les alias ambigus)
    index, seen = {}, {}
    for name, aliases in zip(chars["name"], chars["aliases"].map(parse_list)):
        for key in [name] + aliases:
            seen[key] = seen.get(key, 0) + (1 if key != name else 100)
            if key == name or key not in index:
                index[key] = name
    index = {k: v for k, v in index.items() if seen[k] == 1 or seen[k] >= 100}

    for me, desc in zip(chars["name"], chars["description"].fillna("")):
        for word, names in KIN_PATTERN.findall(desc):
            kind = KIN_KIND[word]
            for raw in re.split(r",| and | & ", names):
                other = index.get(raw.strip())
                if not other or other == me:
                    continue
                if kind == "child_of":
                    links.append(("parent", other, me, None, "description"))
                elif kind == "parent_of":
                    links.append(("parent", me, other, word, "description"))
                else:
                    links.append((kind, me, other, None, "description"))

    # fusion : un lien par paire (ordonnée pour parent, non ordonnée sinon)
    merged = {}
    for kind, a, b, role, source in links:
        key = (kind, a, b) if kind == "parent" else (kind, *sorted((a, b)))
        m = merged.setdefault(key, {"role": None, "sources": set()})
        m["sources"].add(source)
        m["role"] = m["role"] or role
    # un couple marié n'est pas aussi listé comme « partenaire »
    merged = {k: v for k, v in merged.items()
              if not (k[0] == "partner" and ("spouse", k[1], k[2]) in merged)}

    rows = []
    for (kind, a, b), m in merged.items():
        role = m["role"]
        if kind == "parent" and role is None:
            g = gender.get(a, "")
            role = "mother" if g.startswith("female") else "father" if g.startswith("male") else "parent"
        rows.append({"kind": kind, "a": a, "b": b, "role": role or kind,
                     "source": "+".join(sorted(m["sources"]))})
    return pd.DataFrame(rows)


def wd_list(entry, prop, lang):
    key = "label_en" if lang == "en" else "label"
    labels = [v.get(key) or v["label"] for v in entry.get("claims", {}).get(prop, [])]
    return [x for x in labels if not re.fullmatch(r"Q\d+", x)]   # entité Wikidata sans libellé


def external_kin(entry, known_qids):
    """Proches cités par Wikidata mais absents du jeu de données : « relation|libellé fr|libellé en|qid »."""
    out = []
    for prop in ("father", "mother", "spouse", "partner", "sibling", "child"):
        for v in entry.get("claims", {}).get(prop, []):
            if v["qid"] not in known_qids:
                out.append(f"{prop}|{v['label']}|{v.get('label_en') or v['label']}|{v['qid']}")
    return out


def load_translations(filename, keys):
    """Lit un fichier DATAS/*_fr.csv -> {clé anglaise: ligne}."""
    path = DATA / filename
    if not path.exists():
        print(f"(pas de DATAS/{filename} : libellés laissés en anglais)")
        return {}
    df = pd.read_csv(path, keep_default_na=False)
    return {tuple(row[k] for k in keys) if len(keys) > 1 else row[keys[0]]: row
            for row in df.to_dict("records")}


def episode_names(row, myths_fr):
    """(nom anglais, nom français) d'un épisode."""
    if row["kind"] == "MYTH":
        m = re.fullmatch(r"Book\s*(\d+)", str(row["myth"]))
        if m:
            return f"Book {m.group(1)}", f"Livre {m.group(1)}"
        fr = myths_fr.get(row["myth"], {}).get("name_fr") or row["myth"]
        return row["myth"], fr
    chapter = int(row["chapter"]) if pd.notna(row["chapter"]) else "?"
    return f"Book {chapter}", f"{'Chant' if row['genre'] == 'Epic' else 'Livre'} {chapter}"


PLACE_RELS = {"birth": "BORN_IN", "death": "DIED_IN", "residence": "LIVED_IN", "burial": "BURIED_IN",
              "visit": "VISITED"}   # visit : passage ou séjour attesté par un texte (DATAS/places_textes.csv)


def place_frames(chars):
    """Lieux (nœuds Place) et liens personnage -> lieu, un tableau par type de lien."""
    path = DATA / "places.json"
    data = json.loads(path.read_text()) if path.exists() else {"places": {}, "links": []}
    places = data["places"]
    manual = DATA / "places_manual.csv"
    if manual.exists():
        for row in pd.read_csv(manual, keep_default_na=False).to_dict("records"):
            places.setdefault(row["qid"], {}).update(
                fr=row["name_fr"], en=row["name_en"], lat=float(row["lat"]), lon=float(row["lon"]),
                approx=bool(int(row["approx"])), manual=True)
    names_fr = {q: row["name_fr"] for q, row in load_translations("places_fr.csv", ["qid"]).items()}
    for q, name in names_fr.items():
        if q in places and not places[q].get("manual"):
            places[q]["fr"] = name
    df = pd.DataFrame([{"qid": q, "name": p.get("en") or q, "name_fr": p.get("fr") or p.get("en") or q,
                        "lat": p.get("lat"), "lon": p.get("lon"), "approx": bool(p.get("approx", False)),
                        "source": "manuel" if p.get("manual") else "wikidata"}
                       for q, p in places.items()],
                      columns=["qid", "name", "name_fr", "lat", "lon", "approx", "source"])
    by_qid = dict(zip(chars["id"], chars["name"]))
    links = pd.DataFrame(data["links"], columns=["character", "kind", "place"])
    links["name"] = links["character"].map(by_qid)
    links = links.dropna(subset=["name"]).assign(source="Wikidata")[["name", "kind", "place", "source"]]
    # liens tirés des textes antiques (Bibliothèque d'Apollodore…), avec leur référence
    texts = DATA / "places_textes.csv"
    if texts.exists():
        extra = pd.read_csv(texts, keep_default_na=False).rename(columns={"ref": "source"})
        for col, known, what in (("name", set(chars["name"]), "personnages"), ("place", set(places), "lieux"),
                                 ("kind", set(PLACE_RELS), "types de lien")):
            unknown = set(extra[col]) - known
            assert not unknown, f"places_textes.csv : {what} inconnus {unknown}"
        links = pd.concat([links, extra[["name", "kind", "place", "source"]]], ignore_index=True)
    # un même lien donné par plusieurs sources : une seule arête, sources jointes (« Wikidata ; Apollodore III, 190 »)
    links = links.groupby(["name", "kind", "place"], as_index=False)["source"].agg(lambda s: " ; ".join(dict.fromkeys(s)))
    return df, [(rel, links[links["kind"] == kind][["name", "place", "source"]])
                for kind, rel in PLACE_RELS.items()]


def quote_frames(known):
    """Citations Wikiquote : nœuds Quote et liens vers le locuteur, le destinataire, le sujet et les mentions."""
    cols = ["id", "lang", "speaker_label", "text", "original", "original_lang", "context", "work", "section", "url"]
    path = DATA / "quotes.csv"
    df = pd.read_csv(path, keep_default_na=False) if path.exists() else pd.DataFrame(
        columns=cols + ["subject", "speaker", "addressee", "mentions"])
    if "mentions" not in df:
        df["mentions"] = ""
    mentions = df[["id", "mentions"]].assign(mentions=df["mentions"].str.split("|")).explode("mentions")
    mentions = mentions[mentions["mentions"] != ""].drop_duplicates()
    for col, values in (("subject", df["subject"]), ("speaker", df["speaker"]), ("addressee", df["addressee"]),
                        ("mentions", mentions["mentions"])):
        unknown = set(values) - known - {""}
        assert not unknown, f"quotes.csv, colonne {col} : personnages inconnus {unknown}"
    said = df[df["speaker"] != ""][["speaker", "id"]]
    addressed = df[df["addressee"] != ""][["id", "addressee"]]
    about = df[df["subject"] != ""][["id", "subject"]]   # narration pure : aucun personnage concerné
    return df[cols], said, addressed, about, mentions


def simplify(text):
    """« Héphaïstos » -> « hephaistos » : minuscules, sans accents ni ponctuation."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def portrait_files(immortals):
    """Nom du personnage -> fichier de static/portraits dont le nom commence par ce personnage.

    DATAS/portraits_manuels.csv impose une vignette quand le nom de fichier ne suffit pas
    (une même image pour plusieurs personnages, nom mal orthographié dans les données).
    """
    if not PORTRAITS.exists():
        return {}
    index = {}
    for name, fr, aliases in zip(immortals["name"], immortals["name_fr"], immortals["aliases"]):
        for label in [name, fr, *aliases]:
            index.setdefault(simplify(label), name)
    manual = DATA / "portraits_manuels.csv"
    manual = dict(pd.read_csv(manual)[["name", "file"]].values) if manual.exists() else {}
    files = sorted((f for f in PORTRAITS.iterdir() if f.suffix.lower() in PORTRAIT_PRIORITY),
                   key=lambda f: PORTRAIT_PRIORITY.index(f.suffix.lower()))
    found, unknown = {}, []
    for f in files:
        name = index.get(simplify(f.stem.split("_")[0]))
        if name:
            found.setdefault(name, f.name)
        elif f.name not in manual.values():
            unknown.append(f.name)
    for name, file in manual.items():
        assert (PORTRAITS / file).exists(), f"portraits_manuels.csv : fichier absent {file}"
        found[name] = file
    if unknown:
        print(f"(vignettes sans personnage correspondant : {', '.join(unknown)})")
    return found


def french_name(name, info):
    """Nom français : libellé Wikidata, sinon titre de l'article Wikipédia fr, sinon nom anglais.

    Renvoie (nom, source). Le titre Wikipédia est aussi préféré quand le libellé Wikidata
    n'est que le nom anglais recopié (« Panopea » -> « Panope »).
    """
    label = info.get("fr")
    article = re.sub(r"\s*\(.*\)$", "", info.get("frwiki", "")).strip()
    article = article[:1].upper() + article[1:]
    if re.search(r"\s[a-zàâäéèêëîïôöùûüç]", article) or re.search(r"\sd'", article):
        article = ""   # « Actor fils de Déion », « Apis d'Argos » : précision d'homonymie, pas un nom
    if label and (label != name or not article or article == name):
        return label[:1].upper() + label[1:], "wikidata"
    if article:
        return article, "wikipedia"
    return name, "anglais"


def text_additions(chars, edges):
    """Compléments tirés des textes antiques (Bibliothèque d'Apollodore), sans toucher aux fichiers Kaggle.

    - DATAS/characters_textes.csv : personnages absents du jeu de données (Taureau de Crète…) ;
    - DATAS/edges_corrections.csv : dans une scène, un homonyme remplacé par le bon personnage
      (Diomède de Thrace et non le fils de Tydée, dans les travaux d'Héraclès) ;
    - DATAS/edges_textes.csv : co-apparitions manquées par le jeu de données (noms communs :
      « la biche », « le sanglier »…), ajoutées à une scène existante dont elles reprennent l'œuvre.
    """
    extra = DATA / "characters_textes.csv"
    if extra.exists():
        chars = pd.concat([chars, pd.read_csv(extra)[list(chars.columns)]], ignore_index=True)
    fixes = DATA / "edges_corrections.csv"
    if fixes.exists():
        for fix in pd.read_csv(fixes).to_dict("records"):
            in_group = edges["group_key"] == fix["group_key"]
            assert in_group.any(), f"edges_corrections.csv : scène inconnue {fix['group_key']}"
            for col in ("source", "target"):
                edges.loc[in_group & (edges[col] == fix["ancien"]), col] = fix["nouveau"]
    added = DATA / "edges_textes.csv"
    if added.exists():
        rows = []
        for link in pd.read_csv(added).to_dict("records"):
            group = edges[edges["group_key"] == link["group_key"]]
            assert len(group), f"edges_textes.csv : scène inconnue {link['group_key']}"
            row = group.iloc[0].copy()
            row["source"], row["target"] = link["source"], link["target"]
            row["normalized_weight"] = group["normalized_weight"].median()
            rows.append(row)
        edges = pd.concat([edges, pd.DataFrame(rows)], ignore_index=True)
    # le jeu de données range chaque paire par ordre alphabétique : un seul lien par paire
    swap = edges["source"] > edges["target"]
    edges.loc[swap, ["source", "target"]] = edges.loc[swap, ["target", "source"]].values
    return chars, edges


def load_frames():
    chars = pd.read_csv(DATA / "characters.csv")
    edges = pd.read_csv(DATA / "edges.csv", low_memory=False)
    chars, edges = text_additions(chars, edges)
    edges["author"] = edges["author"].fillna("Lyric Poets (anthology)")  # Lyra Graeca
    wd = wikidata_cache()
    known_qids = set(chars["id"])
    info = {q: wd.get(q, {}).get("info", {}) for q in chars["id"]}
    entry = {q: wd.get(q, {}) for q in chars["id"]}

    def from_info(field):
        return chars["id"].map(lambda q: info[q].get(field, ""))

    # noms français : corrections manuelles (DATAS/names_fr.csv) en priorité, sinon Wikidata / Wikipédia
    manual = {k: row["name_fr"] for k, row in load_translations("names_fr.csv", ["name_en"]).items()}
    names_fr = [(manual[n], "manuel") if n in manual else french_name(n, info[q])
                for n, q in zip(chars["name"], chars["id"])]

    immortals = pd.DataFrame({
        "name": chars["name"],
        "qid": chars["id"],
        "description": chars["description"].fillna(""),
        "type": chars["type"].fillna(""),
        "clan": chars.apply(clan_of, axis=1),
        "gender": chars["gender"].fillna("inconnu"),
        "domains": chars["domain"].map(parse_list),
        "aliases": chars["aliases"].map(parse_list),
        "residence": chars["residence"].fillna(""),
        "theoi_url": chars["theoi_url"].fillna(""),
        "name_fr": [n for n, _ in names_fr],
        "name_fr_source": [src for _, src in names_fr],
        "desc_fr": from_info("frDesc"),
        "name_el": from_info("el"),
        "name_la": from_info("la"),
        "image": from_info("image").map(lambda f: COMMONS.format(urllib.parse.quote(f)) if f else ""),
        "frwiki": from_info("frwiki"),
        "enwiki": from_info("enwiki"),
        "kin_ext": chars["id"].map(lambda q: external_kin(entry[q], known_qids)),
    })
    for col, prop in [("same_as", "same_as"), ("deity_domains", "deity_domain"), ("symbols", "symbol"),
                      ("worshipped_by", "worshipped_by"), ("wd_works", "present_in_work")]:
        for lang, suffix in [("en", ""), ("fr", "_fr")]:
            immortals[col + suffix] = chars["id"].map(lambda q, p=prop, l=lang: wd_list(entry[q], p, l))
    # texte de recherche : nom, alias et nom français, en minuscules
    immortals["search"] = (immortals["name"] + "|" + immortals["name_fr"] + "|"
                           + immortals["aliases"].map("|".join)).str.lower()
    immortals = immortals.drop_duplicates("name")
    portraits = portrait_files(immortals)
    immortals["portrait"] = immortals["name"].map(lambda n: portraits.get(n, ""))

    edges["work"] = edges["author"] + " — " + edges["title"]
    edges["kind"] = edges["group_key"].str.split("::").str[0]

    connected = (
        edges.groupby(["source", "target"])
        .agg(mentions=("group_key", "count"),
             weight=("normalized_weight", "sum"),
             works=("work", "nunique"))
        .reset_index()
    )

    works = (
        edges.groupby("work")
        .agg(author=("author", "first"), title=("title", "first"),
             genre=("genre", "first"), period=("period", "first"),
             years=("years", "first"), language=("language", "first"))
        .reset_index().rename(columns={"work": "key"})
    )
    works_fr = load_translations("works_fr.csv", ["author_en", "title_en"])
    works["author_fr"] = [works_fr.get((a, t), {}).get("author_fr") or a for a, t in zip(works.author, works.title)]
    works["title_fr"] = [works_fr.get((a, t), {}).get("title_fr") or t for a, t in zip(works.author, works.title)]
    # présentations Wikipédia (fetch_works.py) : texte, article source et repli éventuel sur l'auteur
    wiki_path = DATA / "works_wiki.json"
    wiki = json.loads(wiki_path.read_text()) if wiki_path.exists() else {}
    for lang in ("fr", "en"):
        entry = [wiki.get(k, {}).get(lang, {}) for k in works["key"]]
        works[f"summary_{lang}"] = [e.get("summary", "") for e in entry]
        works[f"wiki_{lang}_title"] = [e.get("title", "") for e in entry]
        works[f"wiki_{lang}_url"] = [e.get("url", "") for e in entry]
        works[f"wiki_{lang}_fallback"] = [bool(e.get("fallback", False)) for e in entry]

    # épisodes = mythes (groupes MYTH) et chants/livres (groupes CHAPTER)
    ep_rows = edges[edges["kind"].isin(["MYTH", "CHAPTER"])]
    episodes = ep_rows.drop_duplicates("group_key").copy()
    myths_fr = load_translations("episodes_fr.csv", ["name_en"])
    names = episodes.apply(lambda r: episode_names(r, myths_fr), axis=1)
    episodes["name"] = names.str[0]
    episodes["name_fr"] = names.str[1]
    episodes["chapter"] = episodes["chapter"].map(lambda c: str(int(c)) if pd.notna(c) else "")
    episodes = episodes.rename(columns={"group_key": "key"})[["key", "name", "name_fr", "kind", "chapter", "work"]]
    part_of = episodes[["key", "work"]].rename(columns={"key": "from", "work": "to"})

    both = pd.concat([
        edges[["source", "work", "group_key", "kind"]].rename(columns={"source": "name"}),
        edges[["target", "work", "group_key", "kind"]].rename(columns={"target": "name"}),
    ])
    appears = both.groupby(["name", "work"]).size().reset_index(name="mentions")
    featured = (both[both["kind"].isin(["MYTH", "CHAPTER"])]
                .groupby(["name", "group_key"]).size().reset_index(name="mentions"))

    known = set(immortals["name"])
    missing = (set(connected["source"]) | set(connected["target"])) - known
    assert not missing, f"Personnages absents de characters.csv : {missing}"

    family = family_links(chars, wd)
    parent_of = family[family["kind"] == "parent"][["a", "b", "role", "source"]]
    spouse_of = family[family["kind"].isin(["spouse", "partner"])][["a", "b", "kind", "source"]]
    sibling_of = family[family["kind"] == "sibling"][["a", "b", "source"]]

    quotes, said, addressed, about, mentions = quote_frames(known)
    places, place_links = place_frames(chars)

    return [
        ("Immortal", immortals), ("Work", works), ("Episode", episodes.drop(columns="work")),
        ("CONNECTED", connected), ("APPEARS_IN", appears), ("FEATURED_IN", featured),
        ("PART_OF", part_of), ("PARENT_OF", parent_of), ("SPOUSE_OF", spouse_of),
        ("SIBLING_OF", sibling_of), ("Quote", quotes), ("SAID", said),
        ("ADDRESSED_TO", addressed), ("ABOUT", about), ("MENTIONS", mentions), ("Place", places),
        *place_links,
    ]


def build():
    tables = load_frames()

    if DB_PATH.exists():
        shutil.rmtree(DB_PATH) if DB_PATH.is_dir() else DB_PATH.unlink()
    db = kuzu.Database(str(DB_PATH))
    conn = kuzu.Connection(db)

    conn.execute("""CREATE NODE TABLE Immortal(
        name STRING, qid STRING, description STRING, type STRING, clan STRING,
        gender STRING, domains STRING[], aliases STRING[], residence STRING,
        theoi_url STRING, name_fr STRING, name_fr_source STRING, desc_fr STRING, name_el STRING, name_la STRING,
        image STRING, frwiki STRING, enwiki STRING, kin_ext STRING[],
        same_as STRING[], same_as_fr STRING[], deity_domains STRING[], deity_domains_fr STRING[],
        symbols STRING[], symbols_fr STRING[], worshipped_by STRING[], worshipped_by_fr STRING[],
        wd_works STRING[], wd_works_fr STRING[], search STRING, portrait STRING, PRIMARY KEY(name))""")
    conn.execute("""CREATE NODE TABLE Work(
        key STRING, author STRING, title STRING, genre STRING, period STRING,
        years STRING, language STRING, author_fr STRING, title_fr STRING,
        summary_fr STRING, wiki_fr_title STRING, wiki_fr_url STRING, wiki_fr_fallback BOOLEAN,
        summary_en STRING, wiki_en_title STRING, wiki_en_url STRING, wiki_en_fallback BOOLEAN,
        PRIMARY KEY(key))""")
    conn.execute("""CREATE NODE TABLE Episode(
        key STRING, name STRING, name_fr STRING, kind STRING, chapter STRING, PRIMARY KEY(key))""")
    conn.execute("CREATE REL TABLE CONNECTED(FROM Immortal TO Immortal, mentions INT64, weight DOUBLE, works INT64)")
    conn.execute("CREATE REL TABLE APPEARS_IN(FROM Immortal TO Work, mentions INT64)")
    conn.execute("CREATE REL TABLE FEATURED_IN(FROM Immortal TO Episode, mentions INT64)")
    conn.execute("CREATE REL TABLE PART_OF(FROM Episode TO Work)")
    conn.execute("CREATE REL TABLE PARENT_OF(FROM Immortal TO Immortal, role STRING, source STRING)")
    conn.execute("CREATE REL TABLE SPOUSE_OF(FROM Immortal TO Immortal, kind STRING, source STRING)")
    conn.execute("CREATE REL TABLE SIBLING_OF(FROM Immortal TO Immortal, source STRING)")
    conn.execute("""CREATE NODE TABLE Quote(
        id STRING, lang STRING, speaker_label STRING, text STRING, original STRING, original_lang STRING,
        context STRING,
        work STRING, section STRING, url STRING, PRIMARY KEY(id))""")
    conn.execute("CREATE REL TABLE SAID(FROM Immortal TO Quote)")
    conn.execute("CREATE REL TABLE ADDRESSED_TO(FROM Quote TO Immortal)")
    conn.execute("CREATE REL TABLE ABOUT(FROM Quote TO Immortal)")
    conn.execute("CREATE REL TABLE MENTIONS(FROM Quote TO Immortal)")
    conn.execute("""CREATE NODE TABLE Place(
        qid STRING, name STRING, name_fr STRING, lat DOUBLE, lon DOUBLE, approx BOOLEAN, source STRING,
        PRIMARY KEY(qid))""")
    for rel in PLACE_RELS.values():
        conn.execute(f"CREATE REL TABLE {rel}(FROM Immortal TO Place, source STRING)")

    for table, df in tables:
        conn.execute(f"COPY {table} FROM df")
        print(f"{table:12s} {len(df):>6d} lignes")

    print(f"Base graphe créée dans {DB_PATH}")


if __name__ == "__main__":
    build()
