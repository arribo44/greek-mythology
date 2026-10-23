"""Présentation de chaque œuvre (Bibliothèque) d'après Wikipédia, en français et en anglais.

Pour chaque œuvre, on essaie une liste de titres d'articles choisis à la main (le premier
qui existe gagne ; le dernier est souvent l'article sur l'auteur). La présentation est
l'introduction de l'article, complétée par sa section de résumé (« Résumé », « Argument »,
« Plot », « Synopsis »…) quand elle existe, coupée à 500 mots en fin de phrase.
Les articles téléchargés (texte brut, API « extracts ») sont gardés dans DATAS/wikipedia_cache.
Résultat : DATAS/works_wiki.json, lu par build_graph.py (texte sous licence CC BY-SA,
l'URL de l'article est conservée pour l'attribution).

Usage : .venv/bin/python fetch_works.py
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "DATAS" / "works_wiki.json"
CACHE = ROOT / "DATAS" / "wikipedia_cache"
USER_AGENT = "LinkedImmortals/0.4 (projet personnel, mythologie grecque)"
MAX_WORDS = 500

# clé de l'œuvre -> (titres fr candidats, titres en candidats)
CANDIDATES = {
    "Aeschylus — Agamemnon": (["Agamemnon (Eschyle)"], ["Agamemnon (play)"]),
    "Aeschylus — Eumenides": (["Les Euménides", "Orestie"], ["The Eumenides", "Eumenides (play)", "Oresteia"]),
    "Aeschylus — Fragments": (["Eschyle"], ["Aeschylus"]),
    "Aeschylus — Libation Bearers": (["Les Choéphores"], ["The Libation Bearers"]),
    "Aeschylus — Prometheus Bound": (["Prométhée enchaîné"], ["Prometheus Bound"]),
    "Aeschylus — Seven Against Thebes": (["Les Sept contre Thèbes"], ["Seven Against Thebes"]),
    "Aeschylus — Suppliant Women": (["Les Suppliantes (Eschyle)"], ["The Suppliants (Aeschylus)"]),
    "Apollodorus — The Library": (["Bibliothèque (Pseudo-Apollodore)", "Bibliothèque (Apollodore)"],
                                  ["Bibliotheca (Pseudo-Apollodorus)"]),
    "Apollonius Rhodius — Argonautica": (["Argonautiques (Apollonios de Rhodes)", "Les Argonautiques",
                                          "Apollonios de Rhodes"], ["Argonautica"]),
    "Aratus — Phaenomena": (["Phénomènes (Aratos)", "Aratos de Soles"], ["Phaenomena (Aratus)", "Aratus"]),
    "Callimachus — Hymns": (["Hymnes (Callimaque)", "Callimaque de Cyrène"], ["Hymns (Callimachus)", "Callimachus"]),
    "Claudian — Gigantomachy & Other Poems": (["Claudien"], ["Claudian"]),
    "Claudian — Rape Of Proserpine": (["Le Rapt de Proserpine (Claudien)", "De raptu Proserpinae", "Claudien"],
                                      ["De raptu Proserpinae", "Claudian"]),
    "Dictys Cretensis — Journal Of The Trojan War": (["Dictys de Crète"], ["Dictys Cretensis"]),
    "Diodorus Siculus — Library Of History Bks 4 - 6": (["Bibliothèque historique"], ["Bibliotheca historica"]),
    "Epic Cycle — Fragments": (["Cycle troyen", "Cycle épique"], ["Epic Cycle"]),
    "Fulgentius — The Mythologies": (["Fulgence le Mythographe"], ["Fabius Planciades Fulgentius"]),
    "Hesiod — Miscellany Fragments": (["Hésiode"], ["Hesiod"]),
    "Hesiod — Theogony": (["Théogonie (Hésiode)", "Hésiode"], ["Theogony"]),
    "Hesiod — Works And Days": (["Les Travaux et les Jours"], ["Works and Days"]),
    "Homer — Homeric Hymns": (["Hymnes homériques"], ["Homeric Hymns"]),
    "Homer — Iliad": (["Iliade"], ["Iliad"]),
    "Homer — Odyssey": (["Odyssée"], ["Odyssey"]),
    "Hyginus — Fabulae": (["Fables (Hygin)", "Hygin (mythographe)", "Caius Julius Hyginus"], ["Fabulae", "Hyginus"]),
    "Lucian — Dialogues Of The Dead": (["Dialogues des morts (Lucien)", "Lucien de Samosate"],
                                       ["Dialogues of the Dead (Lucian)", "Dialogues of the Dead", "Lucian"]),
    "Lucian — Dialogues Of The Gods": (["Dialogues des dieux (Lucien)", "Dialogues des dieux", "Lucien de Samosate"],
                                       ["Dialogues of the Gods", "Lucian"]),
    "Lucian — Dialogues Of The Sea Gods": (["Dialogues marins", "Lucien de Samosate"],
                                           ["Dialogues of the Sea Gods", "Lucian"]),
    "Lyric Poets (anthology) — Lyra Graeca 1": (["Poésie lyrique grecque archaïque", "Poésie lyrique"],
                                                ["Greek lyric"]),
    "Lyric Poets (anthology) — Orphic Hymns": (["Hymnes orphiques", "Orphisme"], ["Orphic Hymns"]),
    "Lyric Poets (anthology) — Pattern Poems": (["Technopaegnia", "Calligramme"], ["Technopaegnia", "Calligram"]),
    "Nonnus — Dionysiaca Bks 1 - 14": (["Dionysiaques"], ["Dionysiaca"]),
    "Ovid — Fasti": (["Fastes (Ovide)", "Les Fastes", "Ovide"], ["Fasti (poem)"]),
    "Ovid — Heroides": (["Héroïdes"], ["Heroides"]),
    "Ovid — Metamorphoses": (["Les Métamorphoses (Ovide)", "Les Métamorphoses"], ["Metamorphoses"]),
    "Parthenius — Love Romances": (["Parthénios de Nicée"], ["Parthenius of Nicaea"]),
    "Pausanias — Description Of Greece": (["Description de la Grèce"], ["Description of Greece"]),
    "Philostratus The Elder — Imagines": (["Philostrate de Lemnos"], ["Philostratus of Lemnos", "Imagines (work)"]),
    "Philostratus The Younger — Imagines": (["Philostrate le Jeune"], ["Philostratus the Younger"]),
    "Quintus Smyrnaeus — Fall Of Troy": (["Suite d'Homère", "Quintus de Smyrne"], ["Posthomerica"]),
    "Seneca — Agamemnon": (["Agamemnon (Sénèque)"], ["Agamemnon (Seneca)"]),
    "Seneca — Hercules Furens": (["Hercule furieux (Sénèque)", "Hercule furieux"],
                                 ["Hercules Furens (Seneca)", "Hercules (Seneca)", "Seneca the Younger"]),
    "Seneca — Hercules Oetaeus": (["Hercule sur l'Œta", "Hercule sur l'Œta (Sénèque)", "Sénèque"], ["Hercules Oetaeus"]),
    "Seneca — Medea": (["Médée (Sénèque)"], ["Medea (Seneca)"]),
    "Seneca — Oedipus": (["Œdipe (Sénèque)"], ["Oedipus (Seneca)"]),
    "Seneca — Phaedra": (["Phèdre (Sénèque)"], ["Phaedra (Seneca)"]),
    "Seneca — Phoenissae": (["Les Phéniciennes (Sénèque)"], ["Phoenissae (Seneca)"]),
    "Seneca — Thyestes": (["Thyeste (Sénèque)"], ["Thyestes (Seneca)"]),
    "Seneca — Troades": (["Les Troyennes (Sénèque)"], ["Troades (Seneca)"]),
    "Statius — Achilleid": (["Achilléide"], ["Achilleid"]),
    "Statius — Thebaid": (["Thébaïde (Stace)"], ["Thebaid (Latin poem)"]),
    "Theocritus — Idylls": (["Idylles (Théocrite)", "Théocrite"], ["Idylls (Theocritus)", "Theocritus"]),
    "Valerius Flaccus — Argonautica": (["Argonautiques (Valerius Flaccus)", "Valerius Flaccus"],
                                       ["Argonautica (Valerius Flaccus)", "Gaius Valerius Flaccus"]),
    "Virgil — Aeneid Bks 1 - 6": (["Énéide"], ["Aeneid"]),
    "Virgil — Eclogues": (["Bucoliques"], ["Eclogues"]),
}


def api(lang, params, retries=6):
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {**params, "format": "json", "formatversion": "2", "maxlag": "5"})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 503) or attempt == retries - 1:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 15 * (attempt + 1)
            print(f"  Wikipédia limite les requêtes, nouvel essai dans {wait}s")
            time.sleep(wait)


def resolve(lang, titles):
    """Titres qui existent (redirections suivies, pages d'homonymie écartées) : {titre demandé: article}."""
    out = {}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        data = api(lang, {"action": "query", "prop": "info|pageprops", "ppprop": "disambiguation",
                          "redirects": "1", "titles": "|".join(chunk)})["query"]
        alias = {r["from"]: r["to"] for r in data.get("normalized", []) + data.get("redirects", [])}
        existing = {p["title"] for p in data.get("pages", [])
                    if not p.get("missing") and not p.get("invalid") and "disambiguation" not in p.get("pageprops", {})}
        for t in chunk:
            target = alias.get(alias.get(t, t), alias.get(t, t))
            if target in existing:
                out[t] = target
        time.sleep(1)
    return out


def article(lang, title):
    """Texte brut d'un article, sections marquées « == Titre == » ; mis en cache."""
    cache = CACHE / f"{lang}_{re.sub(r'[^\w-]', '_', title)}.txt"
    if cache.exists():
        return cache.read_text()
    data = api(lang, {"action": "query", "prop": "extracts", "explaintext": "1", "exsectionformat": "wiki",
                      "redirects": "1", "titles": title})
    text = data["query"]["pages"][0].get("extract", "")
    CACHE.mkdir(exist_ok=True)
    cache.write_text(text)
    time.sleep(1)
    return text


PLOT_SECTIONS = r"(résumé|argument|intrigue|synopsis|contenu|sujet|structure|plot|summary|contents|synopsis|story)"


def presentation(text):
    """Introduction + première section de résumé (si elle existe), coupées à MAX_WORDS mots."""
    parts = re.split(r"^(==+)\s*(.+?)\s*==+\s*$", text, flags=re.M)
    intro = parts[0].strip()
    plot = ""
    for i in range(1, len(parts) - 2, 3):
        level, title, body = parts[i], parts[i + 1], parts[i + 2].strip()
        if len(level) == 2 and re.search(PLOT_SECTIONS, title, re.I) and body:
            plot = body
            break
    return trim("\n".join(x for x in (intro, plot) if x))


def trim(text, max_words=MAX_WORDS):
    """Coupe à max_words mots, en fin de phrase ; supprime les lignes vides en trop."""
    text = re.sub(r"\n{2,}", "\n", text).strip()
    words = text.split()
    if len(words) <= max_words:
        return text
    cut = " ".join(words[:max_words])
    end = max(cut.rfind(". "), cut.rfind(".\n"), cut.rfind(".»"))
    return (cut[:end + 1] if end > 0 else cut) + " […]"


def main():
    result = {key: {} for key in CANDIDATES}
    for li, lang in enumerate(("fr", "en")):
        all_titles = sorted({t for c in CANDIDATES.values() for t in c[li]})
        found = resolve(lang, all_titles)
        print(f"{lang} : {len(found)}/{len(all_titles)} titres candidats existent")
        for key, cands in CANDIDATES.items():
            rank = next((i for i, t in enumerate(cands[li]) if t in found), None)
            if rank is None:
                print(f"  {key} : aucun article {lang}")
                continue
            title = found[cands[li][rank]]
            summary = presentation(article(lang, title))
            result[key][lang] = {
                "title": title, "summary": summary, "words": len(summary.split()),
                # dernier choix de la liste : article plus général (souvent l'auteur), pas l'œuvre elle-même
                "fallback": len(cands[li]) > 1 and rank == len(cands[li]) - 1,
                "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    for lang in ("fr", "en"):
        ok = [r[lang] for r in result.values() if lang in r]
        print(f"{lang} : {len(ok)}/{len(result)} œuvres, {sum(r['words'] for r in ok) // max(len(ok), 1)} mots en moyenne")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
