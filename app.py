"""LinkedImmortals — le réseau professionnel des immortels.

API Flask au-dessus de la base graphe Kùzu construite par build_graph.py.
Chaque route accepte ?lang=fr|en : les libellés traduits sont stockés dans le graphe
(propriétés « _fr »), le contenu parodique dans content.py.

Lancement : .venv/bin/flask --app app run --port 5000
"""
import hashlib
import random
import re
import threading
from pathlib import Path

import kuzu
from flask import Flask, abort, jsonify, request, send_from_directory

from content import (CURATED_POSTS, DEFAULT_RESIDENCE, EMPLOYERS_BY_GENRE, FAMILY_MESSAGES, GENERIC_COMMENTS, GENRES,
                     JOBS, MESSAGES, MESSAGES_BY_CLAN, NOTIFICATIONS, PAIR_MESSAGES, PERIODS, POSITION_BY_CLAN,
                     POSITIONS, RECOMMENDATIONS, SKILLS, SKILLS_BY_CLAN, TIME_UNITS, B)

ROOT = Path(__file__).parent
DB_PATH = ROOT / "graph.kuzu"
PORTRAITS = ROOT / "DATAS" / "IMAGES_JC"

app = Flask(__name__, static_folder="static", static_url_path="/static")
_db = kuzu.Database(str(DB_PATH), read_only=True)
_conn = kuzu.Connection(_db)
_lock = threading.Lock()

LANGUAGES = {"Greek": B("grec", "Greek"), "Latin": B("latin", "Latin")}


def q(cypher, **params):
    """Exécute une requête Cypher et renvoie une liste de dicts."""
    with _lock:
        res = _conn.execute(cypher, params)
        cols = res.get_column_names()
        rows = []
        while res.has_next():
            rows.append(dict(zip(cols, res.get_next())))
    return rows


def rng_for(*parts):
    seed = int(hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)
    return random.Random(seed)


# --------------------------------------------------------------------------
# Langue
# --------------------------------------------------------------------------

def lang():
    value = request.args.get("lang", "fr")
    return value if value in ("fr", "en") else "fr"


def tr(text, **fmt):
    """Choisit la version fr/en d'un texte de content.py (et le formate)."""
    value = text[lang()] if isinstance(text, dict) and "fr" in text else text
    return value.format(**fmt) if fmt else value


def L(prop):
    """Nom de la propriété du graphe dans la langue courante (« w.title » -> « w.title_fr »)."""
    return f"{prop}_fr" if lang() == "fr" else prop


def period_label(period):
    for en, label, _ in PERIODS:
        if en == period:
            return tr(label)
    return period


# --------------------------------------------------------------------------
# Profils
# --------------------------------------------------------------------------

def position_of(p):
    return tr(POSITIONS.get(p["name"]) or POSITION_BY_CLAN.get(p["clan"], POSITION_BY_CLAN["Mortel"]))


def headline_of(p):
    desc = ((lang() == "fr" and p.get("desc_fr")) or p.get("description") or "").strip()
    if not desc:
        return position_of(p)
    desc = desc[0].upper() + desc[1:]
    return desc if len(desc) <= 110 else desc[:107].rsplit(" ", 1)[0] + "…"


def skills_of(p):
    base = tr(SKILLS.get(p["name"], B([], []))) + [d.capitalize() for d in (p.get("domains") or [])]
    domains = p.get("deity_domains_fr") if lang() == "fr" else p.get("deity_domains")
    base += [d[0].upper() + d[1:] for d in (domains or []) if d]
    base += tr(SKILLS_BY_CLAN.get(p["clan"], B([], [])))
    seen, out = set(), []
    for s in base:
        if s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out[:6]


def card(p, **extra):
    """Version compacte d'un profil pour les listes. « name » reste l'identifiant (anglais)."""
    d = {"name": p["name"], "label": (lang() == "fr" and p.get("name_fr")) or p["name"],
         "clan": p["clan"], "gender": p.get("gender"),
         "headline": headline_of(p), "position": position_of(p)}
    d.update(extra)
    return d


IMMORTAL_FIELDS = ("i.name AS name, i.name_fr AS name_fr, i.clan AS clan, i.gender AS gender, "
                   "i.description AS description, i.desc_fr AS desc_fr, i.domains AS domains, i.type AS type, "
                   "i.residence AS residence, i.aliases AS aliases, i.theoi_url AS theoi_url, i.qid AS qid, "
                   "i.image AS image, i.deity_domains AS deity_domains, i.deity_domains_fr AS deity_domains_fr")


def wiki_fields():
    return (f"i.name_el AS name_el, i.name_la AS name_la, i.frwiki AS frwiki, i.enwiki AS enwiki, "
            f"{L('i.same_as')} AS same_as, {L('i.symbols')} AS symbols, "
            f"{L('i.worshipped_by')} AS worshipped_by, {L('i.wd_works')} AS wd_works, i.kin_ext AS kin_ext")


def get_immortal(name):
    rows = q(f"MATCH (i:Immortal {{name: $n}}) RETURN {IMMORTAL_FIELDS}", n=name)
    return rows[0] if rows else None


def resolve(text):
    """Retrouve l'identifiant d'un personnage à partir de son nom anglais ou français."""
    if not text:
        return None
    if get_immortal(text):
        return text
    rows = q("MATCH (i:Immortal) WHERE lower(i.name) = $t OR lower(i.name_fr) = $t RETURN i.name AS name LIMIT 1",
             t=text.strip().lower())
    return rows[0]["name"] if rows else None


def degree(name):
    return q("MATCH (i:Immortal {name: $n})-[:CONNECTED]-(b) RETURN count(b) AS c", n=name)[0]["c"]


def neighbors(name, limit=50):
    return q(f"""MATCH (me:Immortal {{name: $n}})-[r:CONNECTED]-(i:Immortal)
                 RETURN {IMMORTAL_FIELDS}, r.mentions AS mentions, r.works AS works
                 ORDER BY r.mentions DESC LIMIT $l""", n=name, l=limit)


def shortest_path(a, b):
    if a == b:
        return [a], []
    rows = q("""MATCH p = (a:Immortal {name: $a})-[:CONNECTED* SHORTEST 1..10]-(b:Immortal {name: $b})
                RETURN properties(nodes(p), 'name') AS names, properties(rels(p), 'mentions') AS mentions
                LIMIT 1""", a=a, b=b)
    return (rows[0]["names"], rows[0]["mentions"]) if rows else (None, None)


def work_fields(alias="w"):
    return (f"{alias}.key AS key, {L(alias + '.title')} AS title, {L(alias + '.author')} AS author, "
            f"{alias}.genre AS genre, {alias}.period AS period, {alias}.years AS years")


def localize_work(w):
    w["genre_label"] = tr(GENRES.get(w["genre"], w["genre"]))
    w["period_label"] = period_label(w["period"])
    if lang() == "fr" and w.get("years"):  # « 300 B.C. - 100 B.C. » -> « 300 av. J.-C. – 100 av. J.-C. »
        w["years"] = w["years"].replace("B.C.", "av. J.-C.").replace("A.D.", "ap. J.-C.").replace(" - ", " – ")
    return w


def bibliography(name):
    """Toutes les œuvres citant le personnage, avec les épisodes (mythes, chants) concernés."""
    books = q(f"""MATCH (i:Immortal {{name: $n}})-[a:APPEARS_IN]->(w:Work)
                  RETURN {work_fields()}, a.mentions AS mentions
                  ORDER BY a.mentions DESC""", n=name)
    episodes = q(f"""MATCH (i:Immortal {{name: $n}})-[f:FEATURED_IN]->(e:Episode)-[:PART_OF]->(w:Work)
                     RETURN w.key AS work, e.key AS key, {L('e.name')} AS name, f.mentions AS mentions
                     ORDER BY f.mentions DESC""", n=name)
    for b in books:
        b["episodes"] = [e for e in episodes if e["work"] == b["key"]][:8]
        localize_work(b)
    return books


def family_of(name, kin_ext=()):
    """Famille d'un personnage, lue dans le graphe (+ proches Wikidata hors jeu de données)."""
    parents = q(f"""MATCH (i:Immortal)-[r:PARENT_OF]->(me:Immortal {{name: $n}})
                    RETURN {IMMORTAL_FIELDS}, r.role AS role, r.source AS source""", n=name)
    children = q(f"""MATCH (me:Immortal {{name: $n}})-[r:PARENT_OF]->(i:Immortal)
                     OPTIONAL MATCH (i)-[c:CONNECTED]-()
                     RETURN {IMMORTAL_FIELDS}, r.source AS source, count(c) AS deg
                     ORDER BY deg DESC""", n=name)
    spouses = q(f"""MATCH (me:Immortal {{name: $n}})-[r:SPOUSE_OF]-(i:Immortal)
                    RETURN {IMMORTAL_FIELDS}, r.kind AS kind, r.source AS source""", n=name)
    declared = q(f"""MATCH (me:Immortal {{name: $n}})-[r:SIBLING_OF]-(i:Immortal)
                     RETURN {IMMORTAL_FIELDS}, r.source AS source""", n=name)
    # frères et sœurs déduits du graphe : enfants d'un même parent
    via_parent = q(f"""MATCH (me:Immortal {{name: $n}})<-[:PARENT_OF]-(p:Immortal)-[:PARENT_OF]->(i:Immortal)
                       WHERE i.name <> $n
                       RETURN {IMMORTAL_FIELDS}, collect(DISTINCT p.name) AS via""", n=name)
    grandparents = q("""MATCH (g:Immortal)-[:PARENT_OF]->(:Immortal)-[:PARENT_OF]->(me:Immortal {name: $n})
                        RETURN DISTINCT g.name AS name""", n=name)
    grandchildren = q("""MATCH (me:Immortal {name: $n})-[:PARENT_OF]->(:Immortal)-[:PARENT_OF]->(g:Immortal)
                         RETURN count(DISTINCT g) AS c""", n=name)[0]["c"]

    siblings = {x["name"]: card(x, source=x["source"], via=[]) for x in declared}
    for x in via_parent:
        sib = siblings.setdefault(x["name"], card(x, source="graphe", via=[]))
        sib["via"] = x["via"]
    nparents = len(parents)
    for sib in siblings.values():
        sib["half"] = nparents >= 2 and 0 < len(sib["via"]) < nparents

    external = {}
    for item in kin_ext or []:
        kind, label_fr, label_en, qid = item.split("|", 3)
        external.setdefault(kind, []).append({"label": label_fr if lang() == "fr" else label_en, "qid": qid})

    return {
        "parents": [card(x, role=x["role"], source=x["source"]) for x in parents],
        "spouses": [card(x, kind=x["kind"], source=x["source"]) for x in spouses],
        "siblings": sorted(siblings.values(), key=lambda x: (x["half"], x["label"])),
        "children": [card(x, source=x["source"]) for x in children],
        "grandparents": [g["name"] for g in grandparents], "grandchildren": grandchildren,
        "external": external,
    }


PLACE_KINDS = {"BORN_IN": "birth", "DIED_IN": "death", "LIVED_IN": "residence", "BURIED_IN": "burial"}


def places_of(name):
    """Lieux d'un personnage (naissance, décès, résidence, inhumation)."""
    rows = q(f"""MATCH (i:Immortal {{name: $n}})-[r:BORN_IN|DIED_IN|LIVED_IN|BURIED_IN]->(p:Place)
                 RETURN label(r) AS rel, p.qid AS qid, {L('p.name')} AS name, p.lat AS lat, p.lon AS lon,
                        p.approx AS approx""", n=name)
    order = list(PLACE_KINDS)
    rows.sort(key=lambda r: order.index(r["rel"]))
    return [{**{k: r[k] for k in ("qid", "name", "lat", "lon", "approx")}, "kind": PLACE_KINDS[r["rel"]]}
            for r in rows]


QUOTE_FIELDS = ("q.id AS id, q.lang AS lang, q.speaker_label AS speaker_label, q.text AS text, "
                "q.original AS original, q.original_lang AS original_lang, q.context AS context, q.work AS work, q.section AS section, q.url AS url")


def quotes_of(name):
    """Citations Wikiquote d'un personnage : reçues (dites à son sujet, à lui ou le nommant) et données (dites par lui).

    Les citations dans la langue courante passent en premier.
    """
    received = q(f"""MATCH (q:Quote)-[:ABOUT|ADDRESSED_TO|MENTIONS]->(me:Immortal {{name: $n}})
                     OPTIONAL MATCH (i:Immortal)-[:SAID]->(q)
                     WITH DISTINCT q, i WHERE i IS NULL OR i.name <> $n
                     RETURN {QUOTE_FIELDS}, i.name AS name, {IMMORTAL_FIELDS.replace("i.name AS name, ", "")}""",
             n=name)
    given = q(f"""MATCH (me:Immortal {{name: $n}})-[:SAID]->(q:Quote)
                  OPTIONAL MATCH (q)-[:ADDRESSED_TO]->(i:Immortal)
                  RETURN {QUOTE_FIELDS}, i.name AS name, {IMMORTAL_FIELDS.replace("i.name AS name, ", "")}""",
          n=name)

    def pack(rows, who):
        out = []
        for row in rows:
            quote = {k: row[k] for k in QUOTE_FIELDS_KEYS}
            quote[who] = card(row) if row["name"] else None
            out.append(quote)
        return sorted(out, key=lambda x: (x["lang"] != lang(), x["id"]))

    return pack(received, "author"), pack(given, "target")


QUOTE_FIELDS_KEYS = ("id", "lang", "speaker_label", "text", "original", "original_lang", "context", "work",
                     "section", "url")


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/portraits/<path:filename>")
def portrait(filename):
    """Vignettes personnalisées (DATAS/IMAGES_JC)."""
    return send_from_directory(PORTRAITS, filename, max_age=86400)


@app.route("/api/portraits")
def api_portraits():
    """Nom du personnage -> URL de sa vignette personnalisée."""
    rows = q("MATCH (i:Immortal) WHERE i.portrait <> '' RETURN i.name AS name, i.portrait AS file")
    return jsonify({r["name"]: f"/portraits/{r['file']}" for r in rows})


@app.route("/api/labels")
def api_labels():
    """Noms français de tous les personnages (le front s'en sert pour afficher les noms seuls)."""
    rows = q("MATCH (i:Immortal) RETURN i.name AS name, i.name_fr AS name_fr")
    return jsonify({r["name"]: r["name_fr"] for r in rows if r["name_fr"]})


@app.route("/api/me/<name>")
def api_me(name):
    p = get_immortal(name) or abort(404)
    r = rng_for("views", name)
    return jsonify(card(p, connections=degree(name), views=r.randint(40, 4000),
                        impressions=r.randint(1000, 90000)))


@app.route("/api/profile/<name>")
def api_profile(name):
    p = get_immortal(name) or abort(404)
    viewer = request.args.get("me")
    neigh = neighbors(name, 60)
    r = rng_for("profile", name)

    wiki = q(f"MATCH (i:Immortal {{name: $n}}) RETURN {wiki_fields()}", n=name)[0]
    books = bibliography(name)
    experience = [{**b, "employer": tr(EMPLOYERS_BY_GENRE.get(b["genre"], EMPLOYERS_BY_GENRE["Other"]), a=b["author"])}
                  for b in books[:8]]
    by_period = {}
    for b in books:
        by_period[b["period"]] = by_period.get(b["period"], 0) + b["mentions"]
    activity = [{"period": tr(label), "dates": tr(dates), "mentions": by_period.get(en, 0)}
                for en, label, dates in PERIODS]

    projects = q(f"""MATCH (i:Immortal {{name: $n}})-[f:FEATURED_IN]->(e:Episode)-[:PART_OF]->(w:Work)
                     WHERE e.kind = 'MYTH'
                     RETURN e.key AS key, {L('e.name')} AS name, {L('w.title')} AS title,
                            {L('w.author')} AS author, f.mentions AS mentions
                     ORDER BY f.mentions DESC LIMIT 10""", n=name)

    endorsers = [card(x) for x in neigh[:12]]
    skills = []
    for i, s in enumerate(skills_of(p)):
        who = r.sample(endorsers, k=min(3, len(endorsers))) if endorsers else []
        skills.append({"name": s, "count": max(1, len(neigh) // (i + 1) + r.randint(0, 9)), "by": who})

    received, given = quotes_of(name)
    if not received and not given:
        # pas encore de citation Wikiquote pour ce personnage : recommandations génériques
        label = card(p)["label"]
        received = [{"author": card(n), "text": r.choice(tr(RECOMMENDATIONS)).format(
            name=label, works=n["works"], mentions=n["mentions"]), "generated": True} for n in neigh[:2]]

    mutual, path = [], None
    if viewer and viewer != name:
        mutual = q("""MATCH (a:Immortal {name: $a})-[:CONNECTED]-(m:Immortal)-[:CONNECTED]-(b:Immortal {name: $b})
                      RETURN m.name AS name, m.clan AS clan LIMIT 200""", a=viewer, b=name)
        names, _ = shortest_path(viewer, name)
        path = [card(get_immortal(n)) for n in names] if names else None

    return jsonify({
        **card(p), "name_fr": p["name_fr"], "description": p["description"], "desc_fr": p["desc_fr"],
        "type": p["type"], "residence": p["residence"] or tr(DEFAULT_RESIDENCE), "aliases": p["aliases"],
        "domains": p["domains"], "theoi_url": p["theoi_url"], "qid": p["qid"], "image": p["image"],
        "deity_domains": p["deity_domains_fr"] if lang() == "fr" else p["deity_domains"],
        "connections": degree(name),
        "followers": r.randint(100, 50000) * (1 + len(neigh) // 10),
        "top_connections": [card(n, mentions=n["mentions"]) for n in neigh[:9]],
        "experience": experience, "projects": projects, "skills": skills,
        "books": books, "activity": activity, "family": family_of(name, wiki["kin_ext"]),
        **{k: wiki[k] for k in ("name_el", "name_la", "frwiki", "enwiki", "same_as",
                                "symbols", "worshipped_by", "wd_works")},
        "recommendations": {"received": received, "given": given},
        "places": places_of(name),
        "mutual": mutual[:8], "mutual_count": len(mutual), "path": path,
        "open_to_work": name in ("Heracles", "Prometheus") or p["clan"] == "Géant",
    })


@app.route("/api/feed/<name>")
def api_feed(name):
    page = int(request.args.get("page", 0))
    r = rng_for("feed", name, page)
    neigh = neighbors(name, 40)
    if not neigh:
        neigh = neighbors("Zeus", 40)
    profiles = {}

    def prof(n):
        if n not in profiles:
            profiles[n] = get_immortal(n)
        return profiles[n]

    posts = []

    # 1. Posts "humoristiques" écrits à la main (si l'auteur existe dans le graphe)
    curated = [c for c in CURATED_POSTS if prof(c[0])]
    r.shuffle(curated)
    for author, action, text, comment in curated[:3]:
        a = prof(author)
        com = None
        if comment and prof(comment[0]):
            com = {"author": card(prof(comment[0])), "text": tr(comment[1])}
        else:
            cn = neighbors(author, 10)
            if cn:
                com = {"author": card(r.choice(cn)), "text": r.choice(tr(GENERIC_COMMENTS))}
        posts.append({"kind": "post", "author": card(a), "action": tr(action), "text": tr(text),
                      "likes": degree(author) * r.randint(3, 12), "comment": com})

    # 2. Posts générés à partir du graphe (réseau de l'utilisateur)
    for _ in range(5):
        kind = r.choice(["connect", "endorse", "press", "anniversary", "job", "family", "family"])
        a = r.choice(neigh)
        if kind == "anniversary" and (a["clan"] == "Mortel" or "·" not in position_of(a)):
            kind = "job"  # 3000 ans de carrière, c'est réservé aux immortels qui ont une entreprise
        if kind == "connect":
            friends = [f for f in neighbors(a["name"], 25) if f["name"] != name]
            if not friends:
                continue
            b = r.choice(friends)
            posts.append({"kind": "connect", "author": card(a), "target": card(b),
                          "mentions": b["mentions"], "works": b["works"]})
        elif kind == "endorse":
            friends = neighbors(a["name"], 15)
            if not friends:
                continue
            b = r.choice(friends)
            posts.append({"kind": "endorse", "author": card(a), "target": card(b), "skill": r.choice(skills_of(b))})
        elif kind == "press":
            works = q(f"""MATCH (i:Immortal {{name: $n}})-[x:APPEARS_IN]->(w:Work)
                          RETURN {work_fields()}, x.mentions AS m""", n=a["name"])
            if not works:
                continue
            w = localize_work(r.choice(works))
            posts.append({"kind": "press", "author": card(a), "work": w, "likes": w["m"] * r.randint(2, 9)})
        elif kind == "anniversary":
            posts.append({"kind": "anniversary", "author": card(a),
                          "years": r.choice([500, 1000, 2000, 2500, 3000, 4000]),
                          "company": position_of(a).split("·")[-1].strip()})
        elif kind == "family":
            fam = family_of(a["name"])
            options = ([("birth", c) for c in fam["children"]]
                       + [("wedding", sp) for sp in fam["spouses"] if sp["kind"] == "spouse"]
                       + [("reunion", sb) for sb in fam["siblings"]])
            if not options:
                continue
            event, other = r.choice(options)
            posts.append({"kind": "family", "event": event, "author": card(a), "target": other,
                          "source": other.get("source"), "likes": r.randint(20, 3000)})
        else:
            posts.append({"kind": "job", "author": card(a), "position": position_of(a)})

    r.shuffle(posts)
    return jsonify(posts)


@app.route("/api/suggestions/<name>")
def api_suggestions(name):
    """Amis d'amis non connectés, classés par nombre de relations communes."""
    limit = int(request.args.get("limit", 5))
    rows = q(f"""MATCH (me:Immortal {{name: $n}})-[:CONNECTED]-(f:Immortal)-[:CONNECTED]-(i:Immortal)
                 WHERE i.name <> $n AND NOT EXISTS {{ MATCH (me)-[:CONNECTED]-(i) }}
                 RETURN {IMMORTAL_FIELDS}, count(DISTINCT f) AS mutual
                 ORDER BY mutual DESC LIMIT $l""", n=name, l=limit)
    return jsonify([card(x, mutual=x["mutual"]) for x in rows])


@app.route("/api/sidebar/<name>")
def api_sidebar(name):
    events = q(f"""MATCH (i:Immortal {{name: $n}})-[f:FEATURED_IN]->(e:Episode)
                   WHERE e.kind = 'MYTH'
                   RETURN e.key AS key, {L('e.name')} AS name, f.mentions AS mentions
                   ORDER BY f.mentions DESC LIMIT 3""", n=name)
    r = rng_for("events", name)
    for e in events:
        e["when"] = tr(TIME_UNITS["d"], n=r.randint(1, 30))
    trending = q(f"""MATCH (i:Immortal)-[f:FEATURED_IN]->(e:Episode)
                     WHERE e.kind = 'MYTH' AND NOT e.name STARTS WITH 'Book' AND e.name <> 'Preface'
                     RETURN e.key AS key, {L('e.name')} AS name, count(i) AS people
                     ORDER BY people DESC LIMIT 5""")
    return jsonify({"events": events, "trending": trending})


@app.route("/api/search")
def api_search():
    term = request.args.get("q", "").strip().lower()
    if len(term) < 2:
        return jsonify([])
    rows = q(f"""MATCH (i:Immortal)
                 WHERE i.search CONTAINS $t
                 OPTIONAL MATCH (i)-[c:CONNECTED]-()
                 RETURN {IMMORTAL_FIELDS}, count(c) AS deg
                 ORDER BY deg DESC LIMIT 12""", t=term)
    return jsonify([card(x, connections=x["deg"]) for x in rows])


@app.route("/api/network/<name>")
def api_network(name):
    size = min(int(request.args.get("size", 25)), 80)
    center = get_immortal(name) or abort(404)
    neigh = neighbors(name, size)
    names = [name] + [n["name"] for n in neigh]
    edges = q("""MATCH (a:Immortal)-[r:CONNECTED]->(b:Immortal)
                 WHERE a.name IN $names AND b.name IN $names
                 RETURN a.name AS source, b.name AS target, r.mentions AS mentions""", names=names)
    nodes = [card(center, mentions=None)] + [card(n, mentions=n["mentions"]) for n in neigh]
    return jsonify({"nodes": nodes, "edges": edges})


@app.route("/api/path")
def api_path():
    a, b = resolve(request.args.get("a")), resolve(request.args.get("b"))
    if not (a and b):
        abort(404)
    names, mentions = shortest_path(a, b)
    if names is None:
        return jsonify({"found": False})
    people = [card(get_immortal(n)) for n in names]
    return jsonify({"found": True, "people": people, "mentions": mentions, "degrees": len(names) - 1})


JOBS_SHOWN = 8


@app.route("/api/jobs/<name>")
def api_jobs(name):
    """Offres du moment : d'abord celles qui visent le clan du profil, puis les autres, tirées au sort par profil."""
    me = get_immortal(name)
    r = rng_for("jobs", name)
    pool = [j for j in JOBS if j["boss"] != name]
    r.shuffle(pool)
    pool.sort(key=lambda j: not (me and me["clan"] in j["clans"]))
    out = []
    for job in pool:
        if len(out) == JOBS_SHOWN:
            break
        boss = get_immortal(job["boss"])
        if not boss:
            continue
        cands = q(f"""MATCH (b:Immortal {{name: $boss}})-[r:CONNECTED]-(i:Immortal)
                      WHERE i.clan IN $clans
                      RETURN {IMMORTAL_FIELDS}, r.mentions AS mentions
                      ORDER BY r.mentions DESC LIMIT 4""", boss=job["boss"], clans=job["clans"])
        link, _ = shortest_path(name, job["boss"])
        out.append({**{k: tr(job[k]) for k in ("title", "company", "location", "desc")},
                    "boss": card(boss), "candidates": [card(c) for c in cands],
                    "degrees": len(link) - 1 if link else None,
                    "applicants": rng_for("job", job["boss"]).randint(3, 900)})
    return jsonify(out)


@app.route("/api/notifications/<name>")
def api_notifications(name):
    r = rng_for("notif", name)
    neigh = neighbors(name, 30)
    notes = []
    for n in r.sample(neigh, k=min(4, len(neigh))):
        notes.append({"who": card(n), "text": tr(NOTIFICATIONS["viewed"]),
                      "when": tr(TIME_UNITS["h"], n=r.randint(1, 23))})
    works = q(f"""MATCH (i:Immortal {{name: $n}})-[x:APPEARS_IN]->(w:Work)
                  RETURN {work_fields()} ORDER BY x.mentions DESC LIMIT 3""", n=name)
    for w in works:
        if neigh:
            notes.append({"who": card(r.choice(neigh)),
                          "text": tr(NOTIFICATIONS["mentioned"], title=w["title"], author=w["author"]),
                          "when": tr(TIME_UNITS["d"], n=r.randint(1, 9))})
    notes.append({"who": None, "text": tr(NOTIFICATIONS["searches"], n=r.randint(5, 900)),
                  "when": tr(TIME_UNITS["w"])})
    r.shuffle(notes)
    return jsonify(notes)


CONVERSATIONS = 8
PAIR_CONVERSATIONS = 5  # au plus, pour laisser de la place aux relations proches


def kinship(name):
    """Lien familial de chaque proche, vu depuis ce proche (« parent » : il est le parent de name)."""
    kin = {}
    for rel, query in (
            ("sibling", "MATCH (me:Immortal {name: $n})-[:SIBLING_OF]-(i:Immortal) RETURN i.name AS name"),
            ("sibling", """MATCH (me:Immortal {name: $n})<-[:PARENT_OF]-(:Immortal)-[:PARENT_OF]->(i:Immortal)
                           WHERE i.name <> $n RETURN DISTINCT i.name AS name"""),
            ("spouse", "MATCH (me:Immortal {name: $n})-[:SPOUSE_OF]-(i:Immortal) RETURN i.name AS name"),
            ("child", "MATCH (me:Immortal {name: $n})-[:PARENT_OF]->(i:Immortal) RETURN i.name AS name"),
            ("parent", "MATCH (i:Immortal)-[:PARENT_OF]->(me:Immortal {name: $n}) RETURN i.name AS name")):
        for row in q(query, n=name):
            kin[row["name"]] = rel   # parent et enfant passent en dernier : ils l'emportent
    return kin


def ago(minutes):
    if minutes < 60:
        return tr(TIME_UNITS["min"], n=minutes)
    if minutes < 24 * 60:
        return tr(TIME_UNITS["h"], n=minutes // 60)
    return tr(TIME_UNITS["d"], n=minutes // (24 * 60))


@app.route("/api/messages/<name>")
def api_messages(name):
    """Messagerie : répliques écrites pour le couple (Iliade, Odyssée, Apollodore), sinon selon le lien familial,
    sinon une phrase du clan de l'expéditeur ou générique ; jamais deux fois le même texte dans la boîte."""
    r = rng_for("msg", name)
    senders = [p for p in (get_immortal(a) for a, b in PAIR_MESSAGES if b == name) if p]
    r.shuffle(senders)
    senders = senders[:PAIR_CONVERSATIONS]
    taken = {p["name"] for p in senders}
    senders += [n for n in neighbors(name, 3 * CONVERSATIONS) if n["name"] not in taken][:CONVERSATIONS - len(senders)]
    kin = kinship(name)
    used, out = set(), []
    for p in senders:
        # les phrases du clan sont mêlées aux génériques : sinon les mortels, très nombreux, se répètent
        pools = (PAIR_MESSAGES.get((p["name"], name), []), FAMILY_MESSAGES.get(kin.get(p["name"]), []),
                 MESSAGES_BY_CLAN.get(p["clan"], []) + MESSAGES)
        text = next((m for pool in pools for m in r.sample(pool, len(pool)) if m["fr"] not in used), r.choice(MESSAGES))
        used.add(text["fr"])
        out.append({"who": card(p), "last": tr(text)})
    for conv, minutes in zip(out, sorted(r.randint(1, 3 * 24 * 60) for _ in out)):
        conv["when"] = ago(minutes)
    return jsonify(out)


@app.route("/api/family-tree/<name>")
def api_family_tree(name):
    """Arbre généalogique : grands-parents -> petits-enfants, pour vis-network (layout hiérarchique)."""
    get_immortal(name) or abort(404)
    # nombre max de personnes par catégorie (les plus connues d'abord) pour garder un arbre lisible
    caps = {"grandparents": 8, "parents": 8, "spouses": 10, "siblings": 10, "children": 24, "grandchildren": 16}
    levels, edges, truncated = {name: 0}, [], []
    queries = [
        ("grandparents", -2, "(g:Immortal)-[:PARENT_OF]->(:Immortal)-[:PARENT_OF]->(:Immortal {name: $n})"),
        ("parents", -1, "(g:Immortal)-[:PARENT_OF]->(:Immortal {name: $n})"),
        ("spouses", 0, "(:Immortal {name: $n})-[:SPOUSE_OF]-(g:Immortal)"),
        ("siblings", 0, "(:Immortal {name: $n})<-[:PARENT_OF]-(:Immortal)-[:PARENT_OF]->(g:Immortal)"),
        ("children", 1, "(:Immortal {name: $n})-[:PARENT_OF]->(g:Immortal)"),
        ("grandchildren", 2, "(:Immortal {name: $n})-[:PARENT_OF]->(:Immortal)-[:PARENT_OF]->(g:Immortal)"),
    ]
    for label, level, pattern in queries:
        rows = q(f"""MATCH {pattern} WHERE g.name <> $n
                     WITH DISTINCT g
                     OPTIONAL MATCH (g)-[x:CONNECTED]-()
                     RETURN g.name AS name, count(x) AS d ORDER BY d DESC""", n=name)
        if len(rows) > caps[label]:
            truncated.append({"what": label, "shown": caps[label], "total": len(rows)})
        for x in rows[:caps[label]]:
            levels.setdefault(x["name"], level)

    names = list(levels)
    nodes = q(f"MATCH (i:Immortal) WHERE i.name IN $names RETURN {IMMORTAL_FIELDS}", names=names)
    for e in q("""MATCH (a:Immortal)-[r:PARENT_OF]->(b:Immortal)
                  WHERE a.name IN $names AND b.name IN $names
                  RETURN a.name AS source, b.name AS target, r.source AS src""", names=names):
        edges.append({**e, "kind": "parent"})
    for e in q("""MATCH (a:Immortal)-[r:SPOUSE_OF]->(b:Immortal)
                  WHERE a.name IN $names AND b.name IN $names
                  RETURN a.name AS source, b.name AS target, r.kind AS kind, r.source AS src""", names=names):
        edges.append(e)
    return jsonify({"nodes": [card(n, level=levels[n["name"]]) for n in nodes], "edges": edges,
                    "truncated": truncated})


@app.route("/api/episode")
def api_episode():
    key = request.args.get("key", "")
    ep = q(f"""MATCH (e:Episode {{key: $k}})-[:PART_OF]->(w:Work)
               RETURN {L('e.name')} AS name, e.kind AS kind, e.chapter AS chapter, w.key AS work_key,
                      {L('w.title')} AS title, {L('w.author')} AS author, w.period AS period,
                      w.years AS years, w.genre AS genre""", k=key)
    if not ep:
        abort(404)
    cast = q(f"""MATCH (i:Immortal)-[f:FEATURED_IN]->(e:Episode {{key: $k}})
                 RETURN {IMMORTAL_FIELDS}, f.mentions AS mentions ORDER BY f.mentions DESC""", k=key)
    names = [c["name"] for c in cast]
    kin = q("""MATCH (a:Immortal)-[r:PARENT_OF]->(b:Immortal)
               WHERE a.name IN $names AND b.name IN $names
               RETURN a.name AS a, b.name AS b, r.role AS role""", names=names)
    kin += q("""MATCH (a:Immortal)-[r:SPOUSE_OF]->(b:Immortal)
                WHERE a.name IN $names AND b.name IN $names
                RETURN a.name AS a, b.name AS b, r.kind AS role""", names=names)
    duos = q("""MATCH (a:Immortal)-[r:CONNECTED]->(b:Immortal)
                WHERE a.name IN $names AND b.name IN $names
                RETURN a.name AS a, b.name AS b, r.mentions AS mentions
                ORDER BY r.mentions DESC LIMIT 6""", names=names)
    others = q(f"""MATCH (e:Episode {{key: $k}})-[:PART_OF]->(w:Work)<-[:PART_OF]-(o:Episode)<-[f:FEATURED_IN]-(i:Immortal)
                   WHERE o.key <> $k
                   RETURN o.key AS key, {L('o.name')} AS name, count(i) AS people
                   ORDER BY people DESC LIMIT 12""", k=key)
    return jsonify({**localize_work(ep[0]), "key": key,
                    "cast": [card(c, mentions=c["mentions"]) for c in cast],
                    "kin": kin, "duos": duos, "other_episodes": others})


@app.route("/api/work")
def api_work():
    key = request.args.get("key", "")
    w = q(f"MATCH (w:Work {{key: $k}}) RETURN {work_fields()}, w.language AS language", k=key)
    if not w:
        abort(404)
    w = localize_work(w[0])
    w["language"] = tr(LANGUAGES.get(w["language"], w["language"]))
    # présentation Wikipédia dans la langue courante, sinon dans l'autre
    wiki = q("""MATCH (w:Work {key: $k}) RETURN w.summary_fr AS fr, w.wiki_fr_title AS fr_title,
                w.wiki_fr_url AS fr_url, w.wiki_fr_fallback AS fr_fallback, w.summary_en AS en,
                w.wiki_en_title AS en_title, w.wiki_en_url AS en_url, w.wiki_en_fallback AS en_fallback""", k=key)[0]
    for src in (lang(), "en" if lang() == "fr" else "fr"):
        if wiki[src]:
            w["summary"] = {"text": wiki[src], "lang": src, "title": wiki[f"{src}_title"],
                            "url": wiki[f"{src}_url"], "fallback": wiki[f"{src}_fallback"]}
            break
    cast = q(f"""MATCH (i:Immortal)-[a:APPEARS_IN]->(w:Work {{key: $k}})
                 RETURN {IMMORTAL_FIELDS}, a.mentions AS mentions ORDER BY a.mentions DESC""", k=key)
    clans = {}
    for c in cast:
        clans[c["clan"]] = clans.get(c["clan"], 0) + 1
    episodes = q(f"""MATCH (e:Episode)-[:PART_OF]->(w:Work {{key: $k}})
                     OPTIONAL MATCH (i:Immortal)-[:FEATURED_IN]->(e)
                     RETURN e.key AS key, {L('e.name')} AS name, e.chapter AS chapter, count(i) AS people""", k=key)
    episodes.sort(key=lambda e: (int(e["chapter"]) if e["chapter"].isdigit() else 10**6, e["name"]))
    return jsonify({**w, "headcount": len(cast), "cast": [card(c, mentions=c["mentions"]) for c in cast[:36]],
                    "clans": sorted(clans.items(), key=lambda x: -x[1]), "episodes": episodes})


@app.route("/api/map")
def api_map():
    """Tous les lieux liés à des personnages, avec les personnages regroupés par lieu."""
    rows = q(f"""MATCH (i:Immortal)-[r:BORN_IN|DIED_IN|LIVED_IN|BURIED_IN]->(p:Place)
                 RETURN label(r) AS rel, p.qid AS place_qid, {L('p.name')} AS place, p.lat AS lat,
                        p.lon AS lon, p.approx AS approx, {IMMORTAL_FIELDS}""")
    places = {}
    for r in rows:
        p = places.setdefault(r["place_qid"], {"qid": r["place_qid"], "name": r["place"], "lat": r["lat"], "lon": r["lon"],
                                         "approx": r["approx"], "people": []})
        p["people"].append({**card(r), "kind": PLACE_KINDS[r["rel"]]})
    return jsonify(sorted(places.values(), key=lambda p: -len(p["people"])))


@app.route("/api/works")
def api_works():
    rows = q(f"""MATCH (i:Immortal)-[a:APPEARS_IN]->(w:Work)
                 RETURN {work_fields()}, count(i) AS people, sum(a.mentions) AS mentions,
                        w.summary_{lang()} AS summary""")
    order = {en: k for k, (en, _, _) in enumerate(PERIODS)}
    rows.sort(key=lambda r: (order.get(r["period"], 99), r["author"], r["title"]))
    for r in rows:   # aperçu pour les cartes de la bibliothèque : la première phrase
        first = re.split(r"(?<=[.!?])\s", r.pop("summary") or "", maxsplit=1)[0]
        r["excerpt"] = first if len(first) <= 180 else first[:177].rsplit(" ", 1)[0] + "…"
    return jsonify([localize_work(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=False, port=5000)
