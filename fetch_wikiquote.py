"""Récupère les citations Wikiquote (fr et en) d'un ou plusieurs personnages.

Les pages Wikiquote sont trouvées via les liens de la fiche Wikidata (colonne id de
characters.csv). Pour chaque citation, on devine qui parle et à qui à partir des
« précisions » (fr) ou de la ligne de source (en), puis on écrit DATAS/quotes.csv,
à relire avant de lancer build_graph.py.

Deux modes, combinables :
  - un personnage (nom anglais) : ses pages Wikiquote fr/en, trouvées via Wikidata ;
  - une page d'œuvre « langue:Titre » (ex. fr:Iliade) : les répliques entre personnages,
    rattachées au locuteur, au destinataire et à la personne dont on parle (« au sujet de »).
Une citation déjà présente (même texte, venue d'une autre page) n'est pas ajoutée deux fois.

Usage : .venv/bin/python fetch_wikiquote.py Odysseus Achilles fr:Iliade
"""
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA = ROOT / "DATAS"
OUT = DATA / "quotes.csv"
# corrections manuelles (id, champ, valeur), réappliquées à chaque extraction
CORRECTIONS = DATA / "quotes_corrections.csv"
CACHE = DATA / "wikiquote_cache"
USER_AGENT = "LinkedImmortals/0.3 (projet personnel, mythologie grecque)"
# subject = personnage dont parle la citation (lien ABOUT) ; page = page Wikiquote d'origine
COLUMNS = ["id", "page", "subject", "lang", "speaker", "speaker_label", "addressee", "text", "original",
           "original_lang", "context", "work", "section", "url", "statut"]

# « sa mère », « son fils »… -> relation Wikidata du locuteur
KIN_WORDS_FR = {"mère": "mother", "père": "father", "fils": "child", "fille": "child",
                "femme": "spouse", "épouse": "spouse", "mari": "spouse", "époux": "spouse"}


def get_json(url, retries=5):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == retries - 1:
                raise
            wait = 10 * (attempt + 1)
            print(f"  Wikiquote limite les requêtes, nouvel essai dans {wait}s")
            time.sleep(wait)


def wikiquote_titles(qid):
    url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks&format=json"
           f"&sitefilter=frwikiquote|enwikiquote&ids={qid}")
    links = get_json(url)["entities"][qid].get("sitelinks", {})
    return {lang: links[f"{lang}wikiquote"]["title"] for lang in ("fr", "en") if f"{lang}wikiquote" in links}


def wikitext(lang, title):
    """Wikitexte d'une page, mis en cache dans DATAS/wikiquote_cache (supprimer le fichier pour le rafraîchir)."""
    cache = CACHE / f"{lang}_{re.sub(r'[^\w-]', '_', title)}.wiki"
    if cache.exists():
        return cache.read_text()
    url = (f"https://{lang}.wikiquote.org/w/api.php?action=parse&prop=wikitext&format=json&formatversion=2"
           f"&page={urllib.parse.quote(title)}")
    text = get_json(url)["parse"]["wikitext"]
    CACHE.mkdir(exist_ok=True)
    cache.write_text(text)
    return text


# ---------------------------------------------------------------- nettoyage du wikitexte

def clean(text):
    text = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", text, flags=re.S)
    text = re.sub(r"</?poem>|<br\s*/?>", "\n", text)
    text = re.sub(r"\{\{(?:w|lang\|[^|}]+)\|([^}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)                      # autres modèles
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", text)   # [[cible|texte]] -> texte
    text = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", text)
    text = text.replace("'''", "").replace("''", "")
    text = re.sub(r"^[ \t]*:+[ \t]*", "", text, flags=re.M)          # indentation wiki « : »
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", text)).strip()


def templates(text, name):
    """Liste (début, fin, paramètres) des modèles {{name …}}, en respectant les imbrications."""
    out = []
    for m in re.finditer(r"\{\{\s*" + name + r"\s*\|", text, flags=re.I):
        depth, i = 0, m.start()
        while i < len(text):
            if text.startswith("{{", i) or text.startswith("[[", i):
                depth += 1
                i += 2
            elif text.startswith("}}", i) or text.startswith("]]", i):
                depth -= 1
                i += 2
                if depth == 0:
                    break
            else:
                i += 1
        body = text[m.end():i - 2]
        params, cur, d = [], "", 0
        for j, ch in enumerate(body):
            pair = body[j:j + 2]
            if pair in ("{{", "[["):
                d += 1
            elif pair in ("}}", "]]"):
                d -= 1
            if ch == "|" and d == 0:
                params.append(cur)
                cur = ""
            else:
                cur += ch
        params.append(cur)
        named, positional = {}, []
        for p in params:
            k, sep, v = p.partition("=")
            if sep and re.fullmatch(r"[\wéè' -]+", k.strip()):
                named[k.strip().lower()] = v
            else:
                positional.append(p)
        out.append((m.start(), i, named, positional))
    return out


# ---------------------------------------------------------------- personnages

def name_index():
    """Nom (anglais, français, alias) -> identifiant, des plus longs aux plus courts."""
    chars = pd.read_csv(DATA / "characters.csv")
    wd = json.loads((DATA / "wikidata.json").read_text()) if (DATA / "wikidata.json").exists() else {}
    index = {}
    for qid, name, aliases in zip(chars["id"], chars["name"], chars["aliases"].fillna("[]")):
        entry = wd.get(qid, {})
        labels = [name, entry.get("info", {}).get("fr")]
        labels += re.findall(r"'([^']+)'", aliases)
        # équivalents romains (Hercule, Jupiter…) : utiles pour les citations modernes
        labels += [v.get(k) for v in entry.get("claims", {}).get("same_as", []) for k in ("label", "label_en")]
        for label in filter(None, labels):
            index.setdefault(label, name)
    return dict(sorted(index.items(), key=lambda kv: -len(kv[0]))), chars, wd


def find_names(text, index):
    """Personnages cités dans un texte, dans l'ordre d'apparition."""
    found, taken = [], []
    for label, name in index.items():
        for m in re.finditer(r"(?<![\w-])" + re.escape(label) + r"(?![\w-])", text):
            if any(a <= m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            found.append((m.start(), name))
    return [name for _, name in sorted(found)]


def leading_name(text, index):
    text = re.sub(r"^(?:L'ombre|Le fantôme|L'âme) (?:de |d')", "", text)   # « L'ombre d'Achille… »
    # « Conseils de Nestor à son fils… », « Paroles d'Hector… »
    text = re.sub(r"^(?:Conseils?|Paroles?|Discours|Prière|Plainte|Reproches?|Réponse) (?:de |d')", "", text)
    # « La déesse Dioné », « Le guerrier troyen Glaucos » : article + un ou deux mots en minuscules
    for candidate in (text, re.sub(r"^(?:Le|La|Les|L')\s?(?:[a-zàâäéèêëîïôöùûüç'-]+ ){1,2}", "", text)):
        for label, name in index.items():
            if candidate.startswith(label) and not candidate[len(label):len(label) + 1].isalnum():
                return name
    return ""


def kin_of(name, relation, chars, wd):
    qid = chars.loc[chars["name"] == name, "id"].iloc[0]
    by_qid = dict(zip(chars["id"], chars["name"]))
    for v in wd.get(qid, {}).get("claims", {}).get(relation, []):
        if v["qid"] in by_qid:
            return by_qid[v["qid"]]
    return ""


# ---------------------------------------------------------------- extraction

def parse_fr(subject, text, url, index, chars, wd):
    """subject = personnage de la page ; None pour une page d'œuvre (Iliade…)."""
    rows = []
    # on s'arrête avant les sections de commentaires (« Sur l'Iliade » : Aristote, Romilly…)
    end_of_quotes = re.search(r"^==\s*Sur\b", text, re.M)
    text = text[:end_of_quotes.start()] if end_of_quotes else text
    chapters = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^===\s*([^=\n]+?)\s*===", text, re.M)]
    refs = templates(text, r"Réf [^|}]+")      # Réf Livre, Réf Film, Réf Article…
    for start, end, named, pos in templates(text, "citation"):
        quote = clean(named.get("citation") or (pos[0] if pos else ""))
        if not quote:
            continue
        context = clean(named.get("précisions", ""))
        ref = next((r for r in refs if r[0] >= end and r[0] - end < 40), None)
        work = clean(ref[2].get("titre", "")) if ref else ""
        author = clean(ref[2].get("auteur", "")) if ref else ""
        section = clean(ref[2].get("section") or ref[2].get("date", "")) if ref else ""
        if not section:
            section = next((title for pos_, title in reversed(chapters) if pos_ < start), "")

        speaker, label, addressee = "", "", ""
        # « au sujet de X » : la personne dont on parle, pas le destinataire
        about_clause = re.search(r"\b[Aa]u sujet (?:de la |du |des |de |d')(.*)", context)
        about = (find_names(about_clause.group(1), index) or [""])[0] if about_clause else ""
        context_for_target = context[:about_clause.start()] if about_clause else context
        lead = leading_name(context, index)   # « Ulysse, à Calypso » : le locuteur ouvre les précisions
        if not lead and re.search(r"\bpar (?:lui|elle)-même\b", context):
            lead = subject                     # « présentation du héros par lui-même »
        if lead:
            speaker = lead
            # destinataire : un nom après « à / au / aux », sinon un lien de parenté (« sa mère »)
            # « à Calypso », « au Cyclope Polyphème » : le nom doit suivre de près la préposition
            tail = re.search(r"\b(?:à|au|aux) ((?:\S+ ){0,2}\S+)", context_for_target)
            after = [n for n in find_names(tail.group(1), index) if n != speaker] if tail else []
            kin = re.search(r"\b(?:sa|son) (" + "|".join(KIN_WORDS_FR) + r")\b(.*)", context_for_target)
            if after:
                addressee = after[0]
            elif kin:
                # « son fils Télémaque » : le nom qui suit ; « sa mère défunte » : la mère dans Wikidata
                kin_name = leading_name(kin.group(2).strip(), index)
                addressee = kin_name or kin_of(speaker, KIN_WORDS_FR[kin.group(1)], chars, wd)
        else:
            label = author          # narration ou auteur cité (Homère, du Bellay…)
            if subject is None and not about:
                about = (find_names(context, index) or [""])[0]   # narration : le premier personnage cité
        rows.append({"subject": subject if subject is not None else about, "lang": "fr", "speaker": speaker, "speaker_label": label,
                     "addressee": addressee, "text": quote, "original": clean(named.get("original", "")),
                     "original_lang": named.get("langue", "").strip() if named.get("original") else "",
                     "context": context, "work": work, "section": section, "url": url})
    return rows


def parse_en(subject, text, url, index):
    rows = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^\*[^*]", line):
            continue
        quote = clean(line[1:])
        source_raw = lines[i + 1][2:] if i + 1 < len(lines) and lines[i + 1].startswith("**") else ""
        source = clean(source_raw)
        linked = [clean(f"[[{m}]]") for m in re.findall(r"\[\[([^\]]+)\]\]", source_raw)]
        speakers = [n for n in find_names(" | ".join(linked), index) if n != subject]
        speaker = speakers[0] if speakers else ""
        label = ""
        if not speaker:
            # auteur extérieur : premier lien après « In … », sinon le texte avant la première virgule
            label = linked[0] if source.startswith("In ") and linked else source.split(",")[0]
        rows.append({"subject": subject, "lang": "en", "speaker": speaker, "speaker_label": label.strip(),
                     "addressee": "", "text": quote, "original": "", "original_lang": "", "context": "",
                     "work": "", "section": source, "url": url})
    return rows


def norm(text):
    """Forme normalisée d'une citation pour repérer les doublons entre pages."""
    return re.sub(r"\W+", " ", text.lower()).strip()[:80]


def main(targets):
    index, chars, wd = name_index()
    existing = pd.read_csv(OUT, keep_default_na=False) if OUT.exists() else pd.DataFrame(columns=COLUMNS)
    if "page" not in existing:
        existing.insert(1, "page", existing["subject"])           # ancien format : page = personnage
    existing = existing[~existing["page"].isin(targets)]          # on remplace les pages relancées
    known = {norm(t) for t in existing["text"]}
    rows = []
    for target in targets:
        if re.match(r"^(fr|en):", target):                      # page d'œuvre : « fr:Iliade »
            lang, title = target.split(":", 1)
            pages, subject = {lang: title}, None
            print(f"page {target}")
        else:
            qid = chars.loc[chars["name"] == target, "id"].iloc[0]
            pages, subject = wikiquote_titles(qid), target
            print(f"{target} ({qid}) : pages Wikiquote {pages or 'aucune'}")
        for lang, title in pages.items():
            url = f"https://{lang}.wikiquote.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            text = wikitext(lang, title)
            found = parse_fr(subject, text, url, index, chars, wd) if lang == "fr" else parse_en(subject, text, url, index)
            new = [r for r in found if norm(r["text"]) not in known]
            known.update(norm(r["text"]) for r in new)
            print(f"  {lang} : {len(found)} citations, dont {len(found) - len(new)} déjà présentes")
            for r in new:
                r["page"] = target
            rows += new
            time.sleep(0.5)
    counters = {}
    for row in rows:
        key = (re.sub(r"^(fr|en):", "", row["page"]), row["lang"])
        counters[key] = counters.get(key, 0) + 1
        row["id"] = f"{key[0]}-{key[1]}-{counters[key]:03d}"
        row["statut"] = "à relire"
    out = pd.concat([existing, pd.DataFrame(rows, columns=COLUMNS)], ignore_index=True)[COLUMNS]
    if CORRECTIONS.exists():
        for c in pd.read_csv(CORRECTIONS, keep_default_na=False).to_dict("records"):
            hit = out["id"] == c["id"]
            if hit.any():
                out.loc[hit, c["champ"]] = c["valeur"]
            else:
                print(f"  correction ignorée, citation introuvable : {c['id']}")
    out.to_csv(OUT, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"{len(rows)} nouvelles citations -> {OUT} ({len(out)} au total)")


if __name__ == "__main__":
    main(sys.argv[1:] or ["Odysseus"])
