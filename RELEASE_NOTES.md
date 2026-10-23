# Notes de version

Ce fichier liste les nouveautés de chaque publication sur GitHub. La section « Prochaine version »
regroupe tout ce qui a changé depuis le dernier push ; au moment de publier, on lui donne un numéro
et une date, puis on ouvre une nouvelle section vide au-dessus.

## Prochaine version (non publiée)

*Rien pour l'instant.*

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
