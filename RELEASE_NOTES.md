# Notes de version

Ce fichier liste les nouveautés de chaque publication sur GitHub. La section « Prochaine version »
regroupe tout ce qui a changé depuis le dernier push ; au moment de publier, on lui donne un numéro
et une date, puis on ouvre une nouvelle section vide au-dessus.

## Prochaine version (non publiée)

*Rien pour l'instant.*

## Version 0.3 — 23 octobre 2026

Modifications depuis le commit `48b4c79` (*Version 0.2*).

### Nouveautés

- **Captures d'écran dans le README** : page d'accueil, profil d'Athéna, carte du monde mythologique
  et page de la *Bibliothèque* d'Apollodore, affichées sous la présentation du projet
  (images dans [docs/screenshots/](docs/screenshots/)).
- **Carte : filtre par personnage.** Un champ de saisie avec liste déroulante propose, au fil de la
  frappe, les personnages présents sur la carte (sans tenir compte des accents, noms français ou
  anglais, nombre de lieux affiché). Le personnage choisi se combine avec les filtres Naissance,
  Décès, Résidence, Sépulture et Passage ; l'adresse devient `#/map/<nom>` (partageable) et vider le champ
  réaffiche tout le monde.
- **Carte : Athènes d'après la *Bibliothèque* d'Apollodore.** Les passages qui nomment Athènes ont été
  relevés dans la traduction : 22 liens ajoutés (Athènes passe de 1 à 23 personnages). Résidents et
  rois (Thésée, Cécrops, Érichthonios, Amphictyon, Ménesthée, Médée, Dédale, Céphale, Procris, Éthra,
  Démophon, Acamas, Athéna), naissance de Médos, sépulture d'Érichthonios, et un nouveau type de lien
  **« Passage »** pour ceux qui y viennent sans y vivre (Adraste suppliant, Oreste devant l'Aréopage,
  Minos qui l'assiège, Poséidon sur l'Acropole, Androgée aux Panathénées, Amphitryon, Nisos).
  Chaque lien garde sa référence (« Apollodore III, 190 »), affichée dans la bulle de la carte.
- **Carte : sept autres cités d'après Apollodore** (même méthode qu'Athènes, formes Ilion, Lacédémone
  et Pytho comprises) : 150 liens ajoutés. Nombre de personnages par lieu : Troie 37, Thèbes 32,
  Sparte 27, Argos 25, Mycènes 22, Delphes 17, Corinthe 10 (contre 1 à 10 auparavant, Sparte mise à part).
  Exemples : rois et devins (Cadmos, Œdipe, Tirésias à Thèbes ; Acrisios, Adraste à Argos ; Atrée,
  Agamemnon, Égisthe à Mycènes ; Tyndare, Ménélas à Sparte), morts (Agamemnon, Cassandre,
  Clytemnestre et Égisthe à Mycènes, Jocaste à Thèbes, Pâris et Ajax à Troie, Néoptolème à Delphes),
  et passages (les Sept contre Thèbes, les héros de la guerre de Troie, les consultants de l'oracle de Delphes).
- **Statistiques des lieux de la *Bibliothèque* d'Apollodore** : [DATAS/stat_places_fr.json](DATAS/stat_places_fr.json)
  donne, par ordre décroissant, la fréquence de 167 lieux cités dans la traduction (874 mentions) :
  Thèbes (42), Troie (38), Athènes (29), Argos (27), Mycènes (22), Péloponnèse (20), Crète (19)…
  avec leur type (ville, région, île, fleuve…) et, pour les 21 déjà présents, leur identifiant sur la carte.
  Les noms qui désignent aussi un personnage (Argos, Europe, Libye, dieux-fleuves…) ne sont comptés
  qu'en emploi de lieu. Le fichier ne contient que des comptages, pas le texte de la traduction.

- **Nouvelles vignettes de personnages** : 42 images PNG attribuées à 44 personnages : dieux (Zeus,
  Poséidon, Hadès, Déméter, Perséphone, Apollon, Aphrodite, Artémis, Dionysos, Éole, Callisto, Éros, Pan, Ouranos, Thémis, Céto),
  héros (Héraclès, Thésée, Persée, Bellérophon, Agamemnon, Pâris et sa pomme d'or, Icare, Pénélope à son métier à tisser), Titans (Atlas,
  Prométhée), créatures (Polyphème, Charybde, les trois Cyclopes d'Hésiode, Chiron, Charon, la Chimère, Typhon,
  le Minotaure, l'Hydre de Lerne, les Harpies, le Lion de Némée, la Biche de Cérynie, le Sanglier
  d'Érymanthe)… Ulysse (attaché au mât face aux Sirènes) et Pénélope (à son métier à tisser) ont des
  emblèmes noir et blanc, présentés sur un disque blanc ; Ulysse n'affiche plus l'emoji du cheval de Troie.
  61 personnages ont une vignette (22 auparavant). Toutes les images livrées sur fond gris opaque
  ont été détourées (fond transparent, contour adouci) pour s'intégrer aux médaillons.

- **Fil d'actualité : de 30 à 152 posts parodiques** écrits à la main, tirés de l'Iliade, de l'Odyssée
  et d'Apollodore (Poséidon rappelle le partage du monde en trois, Calypso ne comprend pas les avis
  mitigés de son dernier client, Procuste lance son lit taille unique, Œdipe aurait dû poser plus de
  questions…), dont 99 avec un commentaire attitré d'un personnage lié (« Sac à vin. » signé Achille
  sous le post d'Agamemnon). Commentaires génériques : de 9 à 40. Chaque fil affiche en priorité des
  posts d'auteurs de l'entourage du profil, jamais deux posts du même auteur ; sur les 150 profils les
  plus connectés, 123 auteurs différents apparaissent.

- **Les douze travaux d'Héraclès au complet dans le graphe.** Héraclès n'était relié qu'à sept de ses
  douze adversaires. Ajouts d'après Apollodore (II, 74-126) : liens avec la Biche de Cérynie, le Sanglier
  d'Érymanthe et Orthos, le chien de Géryon (que le jeu de données manquait, Apollodore écrivant « la
  biche », « le sanglier », « le chien ») ; quatre nouveaux personnages : le **Taureau de Crète**, les
  **Juments de Diomède**, les **Oiseaux du lac Stymphale** et **Diomède de Thrace**, reliés à Héraclès,
  Eurysthée, Minos, Athéna, Abdère, Thésée (le taureau de Marathon)… Tous rattachés à l'épisode
  « Les douze travaux d'Héraclès ».

- **Carte : l'Odyssée d'Ulysse.** Ulysse n'était relié qu'à Troie. D'après l'Épitomé d'Apollodore
  (chapitre 7), il passe désormais par Ismaros des Cicones, le pays des Lotophages, la terre des Cyclopes,
  l'Éolie, Télépyle des Lestrygons, l'île de Circé, les Enfers, les îles des Sirènes, le détroit de
  Scylla et Charybde, Thrinacie, Ogygie et Schérie, puis réside à Ithaque (où il meurt) et en Thesprotie.
  Dix lieux légendaires ajoutés à leur localisation traditionnelle, en « position approchée » (Djerba,
  Lipari, Formia, Li Galli, Gozo, Corfou…), et 32 liens, dont les habitants de chaque étape (Maron,
  Polyphème, Éole, Antiphatès, Circé, Tirésias, Scylla, Charybde, Hélios, Calypso, Alcinoos, Nausicaa,
  Pénélope, Télémaque, Eumée, Mélanthée, Télégonos).
- **Carte : itinéraire d'Ulysse.** Filtrée sur Ulysse, la carte trace les 17 étapes de son voyage dans
  l'ordre de l'Épitomé : segments en pointillé, flèches de direction, étapes numérotées (« 7 · 9 » pour
  les deux séjours chez Circé), et la liste des étapes avec leurs références sous la carte (les Enfers,
  hors carte, y figurent). Les itinéraires sont décrits dans `DATAS/itineraires.csv`, prêt pour d'autres
  voyages (Argonautes, Héraclès…).

### Corrections

- **Homonyme corrigé : Diomède.** Dans les travaux d'Héraclès (Apollodore, Diodore), le jeu de données
  attribuait au héros de l'Iliade, fils de Tydée, les mentions du roi de Thrace aux juments mangeuses
  d'hommes. Elles passent désormais à Diomède de Thrace.
- **Carte : plus de lieux cachés sous un autre point.** Les lieux très proches (l'Achilléion et le
  tumulus d'Achille, à 500 m l'un de l'autre) se superposaient : on voyait 2 points pour 3 lieux.
  Les points qui se chevaucheraient à l'écran sont désormais regroupés en un seul marqueur dont la
  bulle liste tous les lieux, et les regroupements sont recalculés à chaque zoom (en zoomant, les
  lieux se séparent). S'applique aussi à la mini-carte des profils.

### Changements techniques

- Nouveau fichier `DATAS/places_textes.csv` (personnage, lieu Wikidata, type de lien, référence, extrait) :
  liens tirés des textes antiques, à compléter pour d'autres villes.
- Graphe : nouveau lien `VISITED` et propriété `source` sur tous les liens vers un lieu
  (« Wikidata », « Apollodore III, 190 » ou les deux) ; `build_graph.py` vérifie personnages, lieux et types.
- `app.py` et `static/app.js` : type de lien « visit » (couleur violette), source affichée dans les bulles.
- Vignettes : répertoire de référence `static/portraits/` (servi directement par Flask, la route
  `/portraits/` disparaît) ; un PNG l'emporte sur un SVG pour le même personnage ;
  `DATAS/portraits_manuels.csv` impose une image quand le nom de fichier ne suffit pas.
  `static/images/` garde les illustrations sans personnage dans les données (mont Olympe, nymphe,
  phénix, Sirènes, Moires, Sphinx, ancien cheval de Troie d'Ulysse) ;
  `DATAS/IMAGES_JC/` conserve les originaux.
- Nouveaux fichiers `DATAS/characters_textes.csv`, `DATAS/edges_textes.csv` et `DATAS/edges_corrections.csv`
  (compléments et corrections du jeu de données Kaggle, avec références) ; `fetch_wikidata.py --manquants`
  ne récupère que les fiches absentes du cache.
- Relancer `build_graph.py` après la mise à jour.

## Version 0.2 — 23 octobre 2026

Modifications depuis le commit `b3c7725` (*Initial commit*).

### Nouveautés

- **Offres d'emploi parodiques : de 7 à 53 offres** ([content.py](content.py), liste `JOBS`).
  Nouvelles offres tirées de l'Iliade, de l'Odyssée et de la *Bibliothèque* d'Apollodore :
  gardien·ne de labyrinthe (Minos), ingénieur·e en ailes de cire (Dédale), hôte·sse d'accueil
  chez Procuste, coiffeur·se pour Méduse, rameur·se chez Argo Ventures (Jason), berger·ère chez
  Polyphème (« candidatures signées *Personne* refusées »), tisserand·e de nuit chez Pénélope, etc.
  Chaque profil voit 8 offres : d'abord celles qui visent son clan, puis un tirage propre au profil.
  Sur les 150 profils les plus connectés, toutes les listes affichées sont différentes.
- **Messagerie enrichie** ([content.py](content.py), [app.py](app.py)). Pour chaque conversation,
  le message est choisi dans cet ordre :
  1. une réplique écrite pour ce couple de personnages (199 couples : Achille et Agamemnon,
     Hector et Andromaque, Ulysse et Polyphème, Calypso, Circé, Pénélope, Orphée et Eurydice,
     Dédale et Icare, Thésée et Procuste, Œdipe et Jocaste…), inspirée des passages Wikiquote
     de l'Iliade et de l'Odyssée et de la *Bibliothèque* d'Apollodore ;
  2. sinon une phrase selon le lien familial (parent, enfant, conjoint, frère ou sœur), lu dans le graphe ;
  3. sinon une phrase du clan de l'expéditeur (Titan, Nymphe, Monstre, Oracle, Mortel…) ou une phrase générique.

  Les messages sont traduits en anglais. Une boîte de réception affiche 8 conversations, dont au plus 5
  répliques écrites pour le couple, et jamais deux fois le même texte. Les dates des messages
  vont maintenant de quelques minutes à plusieurs jours.
- **Recommandations : les personnages nommés dans une citation la reçoivent aussi.**
  Nouvelle colonne `mentions` dans [DATAS/quotes.csv](DATAS/quotes.csv) et nouveau lien
  `(:Quote)-[:MENTIONS]->(:Immortal)` dans le graphe. Un passage de l'Iliade où Achille nomme
  Chiron apparaît désormais dans les recommandations de Chiron (35 liens au total).
  Bellérophon, Chiron, Stentor, Hypnos, Thanatos ou Hélios ont ainsi de vraies citations
  au lieu de recommandations générées.
- **Périphrases homériques reconnues** ([fetch_wikiquote.py](fetch_wikiquote.py), table `PERIPHRASES_FR`) :
  « le fils de Cronos » = Zeus, « le Péléide » = Achille, « fils de Télamon » = Ajax,
  « Laërtiade » = Ulysse, « Tydéide » = Diomède, « l'Ébranleur du sol » = Poséidon,
  « Aïdoneus » = Hadès, « Sommeil » / « Trépas » = Hypnos / Thanatos, « le Soleil » = Hélios…
  Le père nommé dans « fils de X » n'est plus compté comme mentionné. Les périphrases ambiguës
  (« l'Atride » : Agamemnon ou Ménélas) sont tranchées citation par citation dans
  [DATAS/quotes_corrections.csv](DATAS/quotes_corrections.csv).
- **Script de lancement [run.sh](run.sh)** : crée l'environnement virtuel et installe les dépendances
  si besoin, construit `graph.kuzu` s'il manque (cas d'un clone tout neuf), puis lance l'application
  (`./run.sh` ou `./run.sh 8080` pour un autre port).
- **Bibliothèque d'Apollodore en Markdown (usage local, non publiée)** : conversion du PDF à partir
  de la page 27 du livre (livres I à III, Épitomé, notes, bibliographie), qui a servi de source pour
  les nouvelles offres et répliques. La traduction étant protégée par le droit d'auteur, le dossier
  `DATAS/DOCS/` est exclu du dépôt (`.gitignore`).

### Changements techniques

- `fetch_wikiquote.py` recalcule la colonne `mentions` de toutes les citations à chaque extraction
  (avant d'appliquer les corrections manuelles).
- `build_graph.py` crée la table de liens `MENTIONS` et vérifie que les personnages mentionnés existent.
- `app.py` :
  - les recommandations reçues incluent les citations qui nomment le personnage ;
  - nouvelle fonction `kinship()` pour le lien familial avec chaque correspondant ;
  - sélection des offres par clan et par profil.
- `content.py` : `MESSAGES` devient une liste de textes bilingues `B(fr, en)` ; nouvelles listes
  `MESSAGES_BY_CLAN`, `FAMILY_MESSAGES` et `PAIR_MESSAGES`.
- `.gitignore` : ajout de `DATAS/DOCS/` (documents de travail sous droits).
- Après une mise à jour, relancer `build_graph.py` (ou supprimer `graph.kuzu` et lancer `./run.sh`).
