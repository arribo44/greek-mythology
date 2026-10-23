# LinkedImmortals 🏛️

Parodie de LinkedIn pour les immortels de la mythologie grecque, construite sur les données de `DATAS/*.csv`
et enrichie avec Wikidata.

## Lancer

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python fetch_wikidata.py   # (optionnel, ~2 min) Wikidata -> DATAS/wikidata.json (cache)
.venv/bin/python fetch_places.py     # (optionnel, ~15 s) lieux via SPARQL Wikidata -> DATAS/places.json
.venv/bin/python fetch_works.py      # (optionnel) présentations Wikipédia des œuvres -> DATAS/works_wiki.json
.venv/bin/python fetch_wikiquote.py Odysseus Achilles fr:Iliade   # (optionnel) citations Wikiquote -> DATAS/quotes.csv
.venv/bin/python build_graph.py      # CSV + caches -> base graphe Kùzu (graph.kuzu)
.venv/bin/flask --app app run --port 5000
```

## Langues (bouton FR / EN)

- **Données** : chaque libellé existe en anglais et en français dans le graphe (propriétés `name` / `name_fr`,
  `title` / `title_fr`, `same_as` / `same_as_fr`…). Sources du français : Wikidata pour les personnages,
  [DATAS/works_fr.csv](DATAS/works_fr.csv) pour les 54 œuvres et [DATAS/episodes_fr.csv](DATAS/episodes_fr.csv)
  pour les 823 noms de mythes (colonne `statut` = « à relire »). Les noms français des personnages viennent du
  libellé Wikidata, sinon du titre Wikipédia fr ; [DATAS/names_fr.csv](DATAS/names_fr.csv) les corrige à la main. Après correction d'un de ces fichiers,
  relancer `build_graph.py`.
- **Interface** : [static/i18n.js](static/i18n.js) (menus, boutons, phrases du fil).
- **Contenu parodique** (postes, posts, offres…) : [content.py](content.py).
- L'API prend `?lang=fr|en` ; le nom anglais (`name`) reste l'identifiant dans les URL.

## Base graphe (Kùzu, requêtes Cypher)

```
(:Immortal)-[:CONNECTED {mentions, weight, works}]-(:Immortal)   # co-apparitions dans les textes
(:Immortal)-[:APPEARS_IN {mentions}]->(:Work)                     # bibliographie / « Expérience »
(:Immortal)-[:FEATURED_IN {mentions}]->(:Episode)                 # mythes et chants / « Projets »
(:Episode)-[:PART_OF]->(:Work)
(:Immortal)-[:PARENT_OF {role, source}]->(:Immortal)              # famille (Wikidata + descriptions)
(:Immortal)-[:SPOUSE_OF {kind, source}]-(:Immortal)               # mariage / liaison
(:Immortal)-[:SIBLING_OF {source}]-(:Immortal)
(:Immortal)-[:SAID]->(:Quote)-[:ADDRESSED_TO]->(:Immortal)        # citations Wikiquote
(:Quote)-[:ABOUT]->(:Immortal)
(:Immortal)-[:BORN_IN|DIED_IN|LIVED_IN|BURIED_IN]->(:Place)      # lieux Wikidata (P19, P20, P551, P119)
```

Les **lieux** sont récupérés en quelques requêtes SPARQL (`fetch_places.py`) avec leurs coordonnées (P625) ;
un lieu sans coordonnées prend celles de son lieu englobant (position « approchée »).
`DATAS/places_manual.csv` complète ou corrige les coordonnées, `DATAS/places_fr.csv` traduit les noms
(tombeaux de Pausanias…). La page **Carte** les affiche avec Leaflet / OpenStreetMap.

Les **recommandations** d'un profil sont des citations Wikiquote : « reçues » (dites à propos du personnage
ou à lui) et « données » (dites par lui). `fetch_wikiquote.py` trouve les pages fr/en via Wikidata, devine
le locuteur et le destinataire (« Ulysse, à Calypso »), et écrit `DATAS/quotes.csv` (corrections durables dans `DATAS/quotes_corrections.csv`) ; les pages téléchargées
sont gardées dans `DATAS/wikiquote_cache/`. Sans citation, un profil affiche des recommandations génériques.

Les liens familiaux viennent de Wikidata (P22 père, P25 mère, P26 conjoint, P451 partenaire, P40 enfant,
P3373 fratrie) via la colonne `id` de `characters.csv`, et des descriptions du CSV (« son of X and Y »,
« wife of Z »). Les frères et sœurs sont aussi déduits du graphe (parents communs).

## Pages

Accueil (fil d'actualité), profil (infos Wikidata, famille, bibliographie, activité par époque),
arbre généalogique, Mythspace (réseau + degrés de séparation), page mythe (casting, duos, liens familiaux),
page œuvre (« page entreprise »), bibliothèque, offres, messagerie, notifications.

## Vignettes personnalisées

Les images de `DATAS/IMAGES_JC/` (SVG, PNG, JPG ou WebP) remplacent l'emoji du médaillon. Le début du nom
de fichier, avant le premier `_`, désigne le personnage, en français ou en anglais, sans accents
(`Hephaistos_xxx.svg` -> Héphaïstos). Pour en ajouter une : déposer le fichier puis relancer
`build_graph.py` ; les fichiers sans personnage correspondant sont signalés.

## Présentations des œuvres

`fetch_works.py` prend, pour chaque œuvre, l'article Wikipédia (fr et en) choisi dans sa liste `CANDIDATES`
(pages d'homonymie écartées ; le dernier choix est souvent l'article sur l'auteur, signalé comme « repli »).
La présentation = introduction de l'article + sa section « Résumé / Argument / Plot… », coupée à 500 mots.
Les articles téléchargés sont gardés dans `DATAS/wikipedia_cache/` ; texte sous licence CC BY-SA 4.0,
la source est affichée sous chaque présentation.

## Remerciements

Ce site repose sur le jeu de données Kaggle
[**Greek Mythology Network Data**](https://www.kaggle.com/datasets/zaylaatsi/greek-mythology-network-data/data)
publié par **zaylaatsi** (personnages, descriptions et co-apparitions dans 54 œuvres antiques) : merci !
Sources complémentaires : Wikidata (CC0), Wikipédia et Wikiquote (CC BY-SA 4.0), Wikimedia Commons,
Theoi Project, OpenStreetMap (ODbL). La page **Crédits** du site (`#/about`) les détaille.
