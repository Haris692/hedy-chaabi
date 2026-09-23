# -*- coding: utf-8 -*-
"""Recupere les ecussons des clubs et les ecrit dans logos.json.

    python logos.py

A lancer une seule fois : `construire.py` lit ensuite le JSON, sans reseau.
Les ecussons sont stockes en `data:` URI, comme dans football-stats-scraper :
la page reste un fichier unique, sans requete vers un serveur tiers au
chargement (et sans lien qui casse le jour ou la source bouge).

Sources :
  - Al Jazeera FC : football-stats-scraper/data/crests.json (deja telecharge)
  - les autres    : la vignette servie par l'API de Wikipedia
"""
import base64, io, json, os, urllib.parse, urllib.request
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
CRESTS = r"C:/Users/Haris/football-stats-scraper/data/crests.json"
UA = {"User-Agent": "hedy-chaabi-page/1.0 (https://github.com/Haris692/hedy-chaabi)"}

# slug -> (wiki, titre de l'article)
CLUBS = {
    "belouizdad": ("en", "CR Belouizdad"),
    "borains":    ("en", "Royal Francs Borains"),
    "erfurt":     ("en", "FC Rot-Weiss Erfurt"),
    "saintpriest": ("fr", "AS Saint-Priest"),
    "troyes":     ("fr", "ES Troyes AC"),
}


def vignette(wiki, titre, px=120):
    url = ("https://%s.wikipedia.org/w/api.php?action=query&prop=pageimages"
           "&titles=%s&pithumbsize=%d&format=json&redirects=1"
           % (wiki, urllib.parse.quote(titre), px))
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        pages = json.load(r)["query"]["pages"]
    src = next(iter(pages.values())).get("thumbnail", {}).get("source")
    if not src:
        return None
    src = src.split("?")[0]          # les parametres utm ne servent a rien
    with urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=30) as r:
        return encode(r.read())


def encode(brut, haut=72):
    """Ramene l'ecusson a une hauteur commune avant de l'encoder.

    Les sources font de 11 a 48 ko chacune, pour un rendu a 26 px : sans ca on
    embarque 150 ko de base64 dans la page pour six vignettes."""
    im = Image.open(io.BytesIO(brut)).convert("RGBA")
    im.thumbnail((haut * 3, haut), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def main():
    out = {}
    crests = json.load(io.open(CRESTS, encoding="utf-8"))
    out["jazeera"] = encode(base64.b64decode(crests["jazira"].split(",", 1)[1]))
    print("jazeera     <- crests.json (%d ko)" % (len(out["jazeera"]) // 1024))
    for slug, (wiki, titre) in CLUBS.items():
        try:
            d = vignette(wiki, titre)
        except Exception as e:
            d = None
            print("%-11s ECHEC : %s" % (slug, e))
        if d:
            out[slug] = d
            print("%-11s <- %s.wikipedia (%d ko)" % (slug, wiki, len(d) // 1024))
    json.dump(out, io.open(os.path.join(ICI, "logos.json"), "w", encoding="utf-8"))
    print("\nlogos.json : %d ecussons" % len(out))


if __name__ == "__main__":
    main()
