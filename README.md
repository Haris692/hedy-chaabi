# Hedy Chaabi — page de présentation

Page publique pour présenter **Hedy Chaabi** aux clubs, en trois langues
(anglais, français, arabe) : <https://haris692.github.io/hedy-chaabi/>

Un lien peut ouvrir la page directement dans la langue du destinataire :

```
https://haris692.github.io/hedy-chaabi/?lang=ar
https://haris692.github.io/hedy-chaabi/?lang=fr
```

## Regénérer la page

```bash
python construire.py [chemin/du/codage.xml]
```

`index.html` est **produit**, jamais édité à la main. Le contenu vient de :

| Source | Ce qu'elle donne |
|---|---|
| `football-stats-scraper/data/*.json` | saison koweïtienne : matchs, buteurs, classement, fiche joueur, photo |
| le XML du tagger (`kazma-tagger`) | le relevé vidéo du match J13 : 48 actions |
| `SOURCES_CARRIERE` dans `construire.py` | la carrière hors Koweït, chaque ligne avec sa source |

`gabarit.html` est le squelette (mise en page, styles, script) ; `construire.py`
y injecte les données et les textes des trois langues.

## Les trois pièges déjà traités

1. **La MT1 est retournée de 180°.** Al Jazeera est configurée en équipe A dans
   le tagger, qui la suppose donc attaquant vers `x=100` tout le match. En
   première période elle attaque vers `x=0`. Sans la rotation, ses tirs
   apparaissent dans son propre camp.
2. **Les scores sont isolés en `direction:ltr`.** En arabe, l'algorithme bidi
   retourne « 3–1 » en « 1–3 » — le tiret est un caractère neutre entre deux
   nombres. Le score affiché devenait faux, et seul un lecteur arabophone
   pouvait s'en apercevoir.
3. **Les valeurs d'attributs sont échappées** (`html_attr`). L'apostrophe de
   « Coupe d'Algérie » fermait l'attribut `data-tj` et cassait tout le script de
   la page : plus aucun chiffre ne s'affichait.

## Ce que la page n'affirme pas

Le relevé vidéo ne porte que sur **un seul match**, codé à la main et de façon
sélective. La page le dit explicitement : les pourcentages y sont hauts et les
volumes bas, seuls les comptes d'actions rares et saillantes tiennent. Le
classement des buteurs de la division est un **rang partagé** (six joueurs à
quatre buts) et la page l'écrit. L'écart entre les quatre buts du classement
officiel et les trois datés par les chronologies publiques est affiché, pas lissé.
