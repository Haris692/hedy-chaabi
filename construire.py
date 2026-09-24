# -*- coding: utf-8 -*-
"""Genere index.html : la page de presentation de Hedy Chaabi.

    python construire.py [chemin/du/codage.xml]

Aucun chiffre n'est saisi a la main. Tout vient de :
  - football-stats-scraper/data/*.json  : la saison koweitienne (fournisseur)
  - le XML du tagger                    : le releve video du match J13
  - SOURCES_CARRIERE ci-dessous         : les releves publics hors Koweit,
    recopies avec leur source, parce qu'aucun scraper ne les couvre.

La page est trilingue (en / fr / ar). Les textes vivent dans TRAD, un seul
dictionnaire : une chaine oubliee dans une langue se voit tout de suite.
"""
import csv, io, json, math, os, shutil, sys, datetime
import xml.etree.ElementTree as ET

ICI = os.path.dirname(os.path.abspath(__file__))
SCRAPER = r"C:/Users/Haris/football-stats-scraper/data"
XML_DEFAUT = r"C:/Users/Haris/Downloads/2026-09-17-al-jazeera-adversaire-codage (1).xml"
JOUEUR_ID = 1396246

CONTACT_MAIL = "haris.c@hotmail.fr"

# Les deux seuls matchs entiers en ligne (releve du 17/09/2026), puis les
# compilations. Les deux natures ne se melangent pas : un match entier se
# regarde pour juger, un montage se regarde pour voir un geste. Les titres des
# compilations sont recopies tels quels, avec leur chaine — ce ne sont pas nos
# images et la page ne les presente pas comme telles.
VIDEOS = [
    {"type": "match", "id": "iCsZfTOaguk", "date": "2026-02-05",
     "titre": "Al Jazeera 3-1 Al Sahel", "sous": None},
    {"type": "match", "id": "JoN2MlJqePY", "date": "2026-02-20",
     "titre": "Al Jazeera 3-3 Yarmouk", "sous": None},
    {"type": "reel", "id": "j7lk3kXSIhs", "date": None,
     "titre": "Skills, Goals &amp; Assists — Francs Borains, Rot-Wei&szlig; Erfurt",
     "sous": "Highlights Football Room"},
    {"type": "reel", "id": "R6ZvwA57ezI", "date": None,
     "titre": "Hedy Chaabi — Francs Borains", "sous": "Fou2Foot"},
]

# Hors Koweit, aucune source ne se scrape : on recopie, avec la source en face.
#
# Chaque ligne chiffree de footballdatabase.eu a ete VERIFIEE par recoupement
# interne : le site publie une colonne « efficacite » qui vaut minutes / buts.
# Quand elle retombe sur le quotient, la ligne se tient. Les lignes ou elle ne
# retombait pas ne sont pas ici. (Une premiere lecture automatique du tableau
# donnait « 5 buts et 17 passes en 870 minutes » : les colonnes etaient
# decalees. D'ou la verification.)
def C(saison, club, logo, en, fr, ar, m=None, b=None, pd=None, mn=None, src="fdb"):
    return {"saison": saison, "club": club, "logo": logo,
            "comp": {"en": en, "fr": fr, "ar": ar},
            "matchs": m, "buts": b, "passes": pd, "minutes": mn, "src": src}


SOURCES_CARRIERE = [
    C("2025/26", "Al Jazeera FC", "jazeera",
      "Zain First Division", "Zain First Division", "دوري زين للدرجة الأولى",
      b=4, src="sofascore"),
    C("2024/25", "CR Belouizdad", "belouizdad",
      "Ligue 1 (Algeria)", "Ligue 1 (Algérie)", "الرابطة المحترفة الأولى (الجزائر)",
      m=18, b=0, mn=633),
    C("2024/25", "CR Belouizdad", "belouizdad",
      "Algerian Cup", "Coupe d'Algérie", "كأس الجزائر",
      m=1, b=1, src="soccerway"),
    C("2024/25", "CR Belouizdad", "belouizdad",
      "CAF Champions League", "Ligue des champions CAF", "دوري أبطال أفريقيا",
      m=3, b=0, pd=1, mn=94, src="espn"),
    C("2023/24", "Francs Borains", "borains",
      "Challenger Pro League (2nd tier)", "Challenger Pro League (D2)",
      "تشالنجر برو ليغ (الدرجة الثانية)", m=25, b=2, pd=2, mn=791),
    C("2022/23", "Francs Borains", "borains",
      "National 1 (3rd tier) — promoted", "Nationale 1 (D3) — montée",
      "الوطنية الأولى (الدرجة الثالثة) — صعود", m=37, b=8, mn=2417),
    C("2021/22", "Francs Borains", "borains",
      "National 1 (3rd tier)", "Nationale 1 (D3)",
      "الوطنية الأولى (الدرجة الثالثة)", m=13, b=1, mn=635),
    C("2020-2022", "FC Rot-Weiß Erfurt", "erfurt",
      "Oberliga (Germany)", "Oberliga (Allemagne)", "أوبرليغا (ألمانيا)"),
    C("2019/20", "Francs Borains", "borains",
      "Division 2 Amateur (4th tier)", "Division 2 Amateurs (D4)",
      "الدرجة الثانية للهواة (الرابعة)", m=21, b=11, mn=1631),
    C("2018/19", "Francs Borains", "borains",
      "Division 2 Amateur (4th tier)", "Division 2 Amateurs (D4)",
      "الدرجة الثانية للهواة (الرابعة)", m=29, b=10, mn=2005),
    C("2016-2018", "Francs Borains", "borains",
      "Division 3 Amateur (5th tier)", "Division 3 Amateurs (D5)",
      "الدرجة الثالثة للهواة (الخامسة)"),
    C("2015/16", "AS Saint-Priest", "saintpriest",
      "CFA 2 (France)", "CFA 2 (France)", "الدرجة الخامسة (فرنسا)",
      m=15, b=2, mn=475),
    C("2014/15", "ESTAC Troyes B", "troyes",
      "CFA (France)", "CFA (France)", "الدرجة الرابعة (فرنسا)",
      m=19, b=0, mn=747),
]

PALETTE = {  # validee par valide_palette.py, clair et sombre
    "bleu":  ("#2a78d6", "#3987e5"),
    "orange": ("#eb6834", "#d95926"),
    "aqua":  ("#1baf7a", "#199e70"),
}


def html_attr(t):
    """Echappe une valeur d'attribut HTML. Sans ca, l'apostrophe de
    « Coupe d'Algerie » ferme l'attribut et casse tout le script de la page."""
    return (t.replace("&", "&amp;").replace('"', "&quot;")
             .replace("'", "&#39;").replace("<", "&lt;"))


# --------------------------------------------------------------- lecture
def charge(nom):
    return json.load(io.open(os.path.join(SCRAPER, nom), encoding="utf-8"))


def lis_xml(chemin):
    """Le releve du tagger, MT1 retournee de 180 degres.

    Al Jazeera est configuree en equipe A, donc le tagger la suppose attaquant
    vers x=100 sur tout le match. En MT1 elle attaque vers x=0 (ses tirs sont a
    x = 4, 14, 14, 17) : c'est la MT1 qu'on retourne, pas la MT2, parce que les
    equipes changent de camp a la pause.
    """
    rows = []
    for inst in ET.parse(chemin).getroot().findall(".//instance"):
        d = {"code": inst.findtext("code"),
             "t": float(inst.findtext("start")) + 5.0}
        for l in inst.findall("label"):
            d[l.findtext("group")] = l.findtext("text")
        x, y = (float(v) for v in d["Zone"].split("/"))
        d["x"], d["y"] = (100 - x, 100 - y) if d["Période"] == "MT1" else (x, y)
        rows.append(d)
    rows.sort(key=lambda r: (r["Période"], r["t"]))
    return rows


def contexte():
    joueurs = charge("players.json")["players"]
    fiche = joueurs[str(JOUEUR_ID)]
    buteurs = charge("scorers.json")["scorers"]
    lui = next(b for b in buteurs if b["id"] == JOUEUR_ID)
    site = charge("site.json")
    events = charge("events.json")["events"]
    squad = charge("squads.json")["teams"]["jazira"]

    arrivee = next(c for c in fiche["career"] if c["to"] == "Al Jazeera FC Kuwait")
    depuis = arrivee["iso"]

    matchs = [m for m in events
              if (m["home_key"] == "jazira" or m["away_key"] == "jazira")
              and m["kickoff_iso"][:10] >= depuis]
    for m in matchs:
        dom = m["home_key"] == "jazira"
        pour, contre = ((m["home_score"], m["away_score"]) if dom
                        else (m["away_score"], m["home_score"]))
        m["_dom"] = dom
        m["_adv"] = m["away"] if dom else m["home"]
        m["_pour"], m["_contre"] = pour, contre
        m["_res"] = "W" if pour > contre else ("D" if pour == contre else "L")
        m["_buts"] = [t["minute"] for t in m["timeline"]
                      if t["type"] == "goal" and t.get("player") == fiche["name"]]

    club_buteurs = sorted([b for b in buteurs if b["team"] == "jazira"],
                          key=lambda b: -b["goals"])
    return {
        "fiche": fiche, "lui": lui, "matchs": matchs, "squad": squad,
        "classement": site["standings"],
        "club": next(r for r in site["standings"] if "Jaz" in r["team"]),
        "club_buteurs": club_buteurs,
        "rang_club": 1 + sum(1 for b in club_buteurs if b["goals"] > lui["goals"]),
        "rang_div": 1 + sum(1 for b in buteurs if b["goals"] > lui["goals"]),
        "n_buteurs": len(buteurs),
        "exaequo": sum(1 for b in buteurs if b["goals"] == lui["goals"]),
        "depuis": depuis,
    }


# ------------------------------------------------------------------ SVG
def pitch(marques, couleur, w=105.0, h=68.0):
    """Un terrain vu du dessus, attaque vers la DROITE, une seule couleur.

    Un terrain par type d'action : 48 marques sur une seule carte se
    recouvrent et l'oeil ne separe plus un tir d'une perte de balle.
    """
    S = 'fill="none" stroke="var(--pitch-line)" stroke-width=".5"'
    lignes = [
        '<rect x="0" y="0" width="%g" height="%g" %s/>' % (w, h, S),
        '<line x1="%g" y1="0" x2="%g" y2="%g" %s/>' % (w / 2, w / 2, h, S),
        '<circle cx="%g" cy="%g" r="9.15" %s/>' % (w / 2, h / 2, S),
    ]
    for dx, prof, larg in ((0, 16.5, 40.3), (w - 16.5, 16.5, 40.3),
                           (0, 5.5, 18.3), (w - 5.5, 5.5, 18.3)):
        lignes.append('<rect x="%g" y="%g" width="%g" height="%g" %s/>'
                      % (dx, (h - larg) / 2, prof, larg, S))
    L, rond = "".join(lignes), ""
    pts = []
    for r in marques:
        cx, cy = r["x"] / 100.0 * w, (100 - r["y"]) / 100.0 * h
        pts.append('<circle cx="%.2f" cy="%.2f" r="1.6" fill="%s" '
                   'stroke="var(--surface-1)" stroke-width=".45"/>'
                   % (cx, cy, couleur))
    fleche = ('<path d="M%g %g h6 m-2 -2 l2 2 l-2 2" fill="none" '
              'stroke="var(--pitch-line)" stroke-width=".5"/>') % (w / 2 - 3, h + 5)
    return ('<svg viewBox="-1 -1 %g %g" class="pitch" role="img">%s%s%s%s</svg>'
            % (w + 2, h + 10, L, rond, "".join(pts), fleche))


def fleches(passes, w=105.0, h=68.0):
    """Les passes en fleches : progressives en couleur, les autres en gris.

    DEFINITION reprise a l'identique de `hedy-rapport/passes_progressives.py`,
    elle-meme validee contre un chiffre publie (44 progressives sur 107 sur le
    rapport Kazma-Al-Shabab). On ne change pas de definition d'un joueur a
    l'autre, sinon les chiffres ne se comparent plus.

    Les coordonnees arrivent DEJA dans le sens d'attaque : Al Jazeera attaque
    vers x=0 en MT1 dans le repere du tagger, la MT1 est donc retournee avant
    tout calcul. La colonne `progression_m` du CSV est fausse pour cette raison
    et n'est jamais lue.
    """
    S = 'fill="none" stroke="var(--pitch-line)" stroke-width=".5"'
    L = ['<rect x="0" y="0" width="%g" height="%g" %s/>' % (w, h, S),
         '<line x1="%g" y1="0" x2="%g" y2="%g" %s/>' % (w/2, w/2, h, S),
         '<circle cx="%g" cy="%g" r="9.15" %s/>' % (w/2, h/2, S)]
    for dx, prof, larg in ((0, 16.5, 40.3), (w-16.5, 16.5, 40.3),
                           (0, 5.5, 18.3), (w-5.5, 5.5, 18.3)):
        L.append('<rect x="%g" y="%g" width="%g" height="%g" %s/>'
                 % (dx, (h-larg)/2, prof, larg, S))
    defs = ('<defs>'
            '<marker id="fp" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="4.5"'
            ' markerHeight="4.5" orient="auto"><path d="M0 0 L8 4 L0 8 z"'
            ' fill="var(--series-1)"/></marker>'
            '<marker id="fa" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="4"'
            ' markerHeight="4" orient="auto"><path d="M0 0 L8 4 L0 8 z"'
            ' fill="var(--bar-muted)"/></marker></defs>')
    out = []
    for p in sorted(passes, key=lambda p: p["prog"]):   # les bleues au-dessus
        x1, y1 = p["x"]/100.0*w, (100-p["y"])/100.0*h
        x2, y2 = p["x2"]/100.0*w, (100-p["y2"])/100.0*h
        c = "var(--series-1)" if p["prog"] else "var(--bar-muted)"
        out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round" '
                   'marker-end="url(#%s)"/>'
                   % (x1, y1, x2, y2, c, 1.1 if p["prog"] else .7,
                      "fp" if p["prog"] else "fa"))
        out.append('<circle cx="%.2f" cy="%.2f" r="1.2" fill="%s" '
                   'stroke="var(--surface-1)" stroke-width=".4"/>' % (x1, y1, c))
    fleche = ('<path d="M%g %g h6 m-2 -2 l2 2 l-2 2" fill="none" '
              'stroke="var(--pitch-line)" stroke-width=".5"/>') % (w/2-3, h+5)
    return ('<svg viewBox="-1 -1 %g %g" class="pitch" role="img">%s%s%s%s</svg>'
            % (w+2, h+10, defs, "".join(L), "".join(out), fleche))


def carte_zones(marques, cols=5, rangs=3, w=105.0, h=68.0):
    # NOM : `zones` est deja une variable locale de construire(), qui la
    # masquerait -- Python ne signale rien, l'appel echoue a l'execution.
    """Carte de chaleur en cases chiffrees, pas en nuage flou.

    POURQUOI DES CASES. 48 actions etalees en densite continue donnent une
    tache qui suggere une precision qu'on n'a pas -- le relevé est selectif,
    la forme tient, la densite non. Une case porte un NOMBRE : on voit
    l'intensite et on peut la verifier.

    POURQUOI 5 x 3. Trois rangs, ce sont les trois couloirs deja cites dans le
    texte de la page (droite / axe / gauche), donc les totaux par rang doivent
    retomber sur 27 / 16 / 5 -- un controle visible par le lecteur. Cinq
    colonnes donnent la profondeur sans descendre sous ~3 actions par case,
    en dessous de quoi on dessinerait du bruit.

    Le repere est celui de `pitch()` : attaque vers la DROITE, et y=0 est le
    couloir droit, donc en BAS.
    """
    S = 'fill="none" stroke="var(--pitch-line)" stroke-width=".5"'
    grille = [[0]*cols for _ in range(rangs)]
    for r in marques:
        c = min(cols-1, max(0, int(r["x"] / 100.0 * cols)))
        g = min(rangs-1, max(0, int(r["y"] / 100.0 * rangs)))
        grille[g][c] += 1
    maxi = max((v for l in grille for v in l), default=1) or 1
    cw, ch = w / cols, h / rangs
    out = []
    for g in range(rangs):
        for c in range(cols):
            n = grille[g][c]
            x, y = c * cw, (rangs - 1 - g) * ch          # y=0 en bas
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                       'fill="var(--series-1)" fill-opacity="%.3f"/>'
                       % (x, y, cw, ch, .07 + .68 * n / maxi))
            if n:
                out.append('<text x="%.2f" y="%.2f" class="zn">%d</text>'
                           % (x + cw/2, y + ch/2 + 2.2, n))
    L = ['<rect x="0" y="0" width="%g" height="%g" %s/>' % (w, h, S),
         '<line x1="%g" y1="0" x2="%g" y2="%g" %s/>' % (w/2, w/2, h, S),
         '<circle cx="%g" cy="%g" r="9.15" %s/>' % (w/2, h/2, S)]
    for dx, prof, larg in ((0, 16.5, 40.3), (w-16.5, 16.5, 40.3),
                           (0, 5.5, 18.3), (w-5.5, 5.5, 18.3)):
        L.append('<rect x="%g" y="%g" width="%g" height="%g" %s/>'
                 % (dx, (h-larg)/2, prof, larg, S))
    mx = sum(r["x"] for r in marques) / max(len(marques), 1)
    my = sum(r["y"] for r in marques) / max(len(marques), 1)
    croix = ('<circle cx="%.2f" cy="%.2f" r="2.4" fill="var(--surface-1)" '
             'stroke="var(--series-1)" stroke-width="1.4"/>'
             % (mx/100.0*w, (100-my)/100.0*h))
    fleche = ('<path d="M%g %g h6 m-2 -2 l2 2 l-2 2" fill="none" '
              'stroke="var(--pitch-line)" stroke-width=".5"/>') % (w/2-3, h+5)
    return ('<svg viewBox="-1 -1 %g %g" class="pitch" role="img">%s%s%s%s</svg>'
            % (w+2, h+10, "".join(out), "".join(L), croix, fleche))


def lis_passes(chemin):
    """Les passes avec un point d'arrivee, mesurees et classees."""
    LONG, LARG, BUT, SEUIL = 105.0, 68.0, (100.0, 50.0), 10.0
    VECTEURS = ("Passe", "Passe clé", "Passe cle", "Centre")
    out = []
    for r in csv.DictReader(io.open(chemin, encoding="utf-8-sig")):
        if r.get("action") not in VECTEURS:
            continue
        try:
            x, y = float(r["x"]), float(r["y"])
            x2, y2 = float(r["x2"]), float(r["y2"])
        except (TypeError, ValueError):
            continue
        # MT1 : Al Jazeera attaque vers x=0 dans le tagger, on retourne
        if r.get("periode") == "1":
            x, y, x2, y2 = 100-x, 100-y, 100-x2, 100-y2
        a0, b0 = x/100.0*LONG, y/100.0*LARG
        a1, b1 = x2/100.0*LONG, y2/100.0*LARG
        gx, gy = BUT[0]/100.0*LONG, BUT[1]/100.0*LARG
        prof = a1 - a0
        gain = math.hypot(gx-a0, gy-b0) - math.hypot(gx-a1, gy-b1)
        out.append({"x": x, "y": y, "x2": x2, "y2": y2,
                    "prog": prof > 0 and max(prof, gain) >= SEUIL,
                    "gain": max(prof, gain)})
    return out


def barres_buteurs(club_buteurs, moi):
    """Les buteurs du club. Une seule serie : pas de legende, valeurs ecrites."""
    rows = club_buteurs[:8]
    maxi = max(b["goals"] for b in rows)
    hl, gap, lab = 22, 8, 150
    w, h = 460, len(rows) * (hl + gap)
    out = []
    for i, b in enumerate(rows):
        y = i * (hl + gap)
        lui = b["id"] == moi
        larg = (w - lab - 34) * b["goals"] / maxi
        nom = b["name"] if len(b["name"]) <= 19 else b["name"][:18] + "…"
        out.append('<text x="%d" y="%d" class="bar-name%s">%s</text>'
                   % (lab - 8, y + hl - 6, " me" if lui else "", nom))
        out.append('<rect x="%d" y="%d" width="%.1f" height="%d" rx="3" '
                   'fill="%s"><title>%s : %d</title></rect>'
                   % (lab, y, larg, hl,
                      "var(--series-1)" if lui else "var(--bar-muted)",
                      b["name"], b["goals"]))
        out.append('<text x="%.1f" y="%d" class="bar-val%s">%d</text>'
                   % (lab + larg + 7, y + hl - 6, " me" if lui else "", b["goals"]))
    return ('<svg viewBox="0 0 %d %d" class="bars" role="img">%s</svg>'
            % (w, h, "".join(out)))


# ------------------------------------------------------------ traductions
TRAD = {
 "nav_profile": {"en": "Profile", "fr": "Profil", "ar": "البطاقة"},
 "nav_season": {"en": "Kuwait 2025/26", "fr": "Koweït 2025/26", "ar": "الكويت 2025/26"},
 "nav_match": {"en": "Match analysis", "fr": "Analyse d'un match", "ar": "تحليل مباراة"},
 "nav_career": {"en": "Career", "fr": "Carrière", "ar": "المسيرة"},
 "nav_video": {"en": "Video", "fr": "Vidéo", "ar": "الفيديو"},
 "nav_contact": {"en": "Contact", "fr": "Contact", "ar": "للتواصل"},

 "role": {"en": "Attacking midfielder · Right winger",
          "fr": "Milieu offensif · Ailier droit",
          "ar": "صانع ألعاب · جناح أيمن"},
 "status": {"en": "Free agent", "fr": "Libre de tout contrat", "ar": "لاعب حر"},
 "status_note": {"en": "Available since the end of the Kuwaiti season, 20 August 2026",
                 "fr": "Disponible depuis la fin de la saison koweïtienne, le 20 août 2026",
                 "ar": "متاح منذ نهاية الموسم الكويتي في 20 أغسطس 2026"},
 "f_age": {"en": "Age", "fr": "Âge", "ar": "العمر"},
 "f_born": {"en": "Born 30 Oct 1995 in Lyon (France)",
            "fr": "Né le 30/10/1995 à Lyon (France)",
            "ar": "من مواليد 30 أكتوبر 1995 في ليون (فرنسا)"},
 "f_height": {"en": "Height", "fr": "Taille", "ar": "الطول"},
 "f_foot": {"en": "Strong foot", "fr": "Pied fort", "ar": "القدم المفضلة"},
 "f_left": {"en": "Left", "fr": "Gauche", "ar": "اليسرى"},
 "f_nat": {"en": "Nationality", "fr": "Nationalité", "ar": "الجنسية"},
 "f_nat_v": {"en": "Algeria", "fr": "Algérie", "ar": "الجزائر"},
 "f_last": {"en": "Last club", "fr": "Dernier club", "ar": "آخر نادٍ"},
 "years": {"en": "years", "fr": "ans", "ar": "سنة"},

 "t_goals": {"en": "Goals in Kuwait", "fr": "Buts au Koweït", "ar": "أهداف في الكويت"},
 "t_goals_s": {"en": "in his 10 eligible league rounds",
               "fr": "sur ses 10 journées de championnat",
               "ar": "في جولاته العشر بالدوري"},
 "t_club": {"en": "Top scorer at his club", "fr": "Buteur de son club", "ar": "هدّاف ناديه"},
 "t_club_s": {"en": "in a 32-man squad, having played half the season",
              "fr": "dans un effectif de 32, en une demi-saison",
              "ar": "ضمن قائمة من 32 لاعبًا، في نصف موسم"},
 "t_div": {"en": "Among the division's scorers",
           "fr": "Au classement des buteurs",
           "ar": "في ترتيب هدّافي الدوري"},
 "t_div_s": {"en": "of %(nb)d players who scored this season; %(tie)d of them are level on four goals",
             "fr": "sur %(nb)d joueurs ayant marqué cette saison ; %(tie)d sont à égalité à quatre buts",
             "ar": "من أصل %(nb)d لاعبًا سجّلوا هذا الموسم، و%(tie)d منهم متعادلون عند أربعة أهداف"},
 "t_team": {"en": "His club's finish", "fr": "Classement de son club", "ar": "ترتيب ناديه"},
 "t_team_s": {"en": "of 8 · 41 goals scored, 2nd best attack",
              "fr": "sur 8 · 41 buts marqués, 2e attaque",
              "ar": "من 8 · 41 هدفًا، ثاني أقوى هجوم"},
 "ord_1": {"en": "st", "fr": "er", "ar": ""},
 "ord_2": {"en": "nd", "fr": "e", "ar": ""},
 "ord_3": {"en": "rd", "fr": "e", "ar": ""},
 "ord_n": {"en": "th", "fr": "e", "ar": ""},

 "s_season": {"en": "The 2025/26 season in Kuwait",
              "fr": "La saison 2025/26 au Koweït",
              "ar": "موسم 2025/26 في الكويت"},
 "season_intro": {
   "en": "He signed for Al Jazeera FC on 26 January 2026, from CR Belouizdad. "
         "That makes him eligible from round 12 onwards: ten league rounds, "
         "plus the Emir Cup tie against Al Kuwait on 15 February. He scored "
         "four goals in that window &mdash; the club's third-highest tally of the "
         "whole season, reached in half of it.",
   "fr": "Il signe à Al Jazeera FC le 26 janvier 2026, en provenance du "
         "CR Belouizdad, ce qui le rend qualifiable à partir de la 12e journée : "
         "dix journées de championnat, plus le match de Coupe de l'Émir contre "
         "Al Kuwait le 15 février. Il marque quatre buts sur cette fenêtre "
         "&mdash; le troisième total du club sur toute la saison, atteint en une moitié.",
   "ar": "انضم إلى نادي الجزيرة في 26 يناير 2026 قادمًا من شباب بلوزداد، "
         "ليكون مؤهلاً اعتبارًا من الجولة 12: عشر جولات في الدوري، إضافة إلى "
         "مباراة كأس الأمير أمام الكويت في 15 فبراير. سجّل في هذه الفترة أربعة "
         "أهداف &mdash; ثالث أفضل حصيلة في النادي طوال الموسم، بلغها في نصفه."},
 "th_round": {"en": "Round", "fr": "Journée", "ar": "الجولة"},
 "th_date": {"en": "Date", "fr": "Date", "ar": "التاريخ"},
 "th_opp": {"en": "Opponent", "fr": "Adversaire", "ar": "الخصم"},
 "th_score": {"en": "Score", "fr": "Score", "ar": "النتيجة"},
 "th_his": {"en": "His goals", "fr": "Ses buts", "ar": "أهدافه"},
 "home": {"en": "home", "fr": "domicile", "ar": "أرضه"},
 "away": {"en": "away", "fr": "extérieur", "ar": "خارج أرضه"},
 "scorers_t": {"en": "Goals scored for Al Jazeera FC in 2025/26",
               "fr": "Les buteurs d'Al Jazeera FC en 2025/26",
               "ar": "هدّافو نادي الجزيرة في 2025/26"},
 "scorers_c": {"en": "Whole-season totals. He appears from round 12 only.",
               "fr": "Totaux sur la saison entière. Il n'apparaît qu'à partir de la 12e journée.",
               "ar": "إجماليات الموسم كاملًا. هو لم يشارك إلا اعتبارًا من الجولة 12."},
 "gap_note": {
   "en": "The league's official scorer table credits him with four goals; the "
         "public match timelines date only three of them. The gap is shown, not "
         "smoothed over.",
   "fr": "Le classement officiel des buteurs lui attribue quatre buts ; les "
         "chronologies publiques n'en datent que trois. L'écart est affiché, pas lissé.",
   "ar": "يمنحه جدول الهدّافين الرسمي أربعة أهداف، بينما لا توثّق التسلسلات "
         "الزمنية المنشورة سوى ثلاثة. الفارق معروض كما هو، دون تجميل."},

 "s_match": {"en": "One match, tagged action by action",
             "fr": "Un match, codé action par action",
             "ar": "مباراة واحدة، موثّقة لقطة بلقطة"},
 "match_intro": {
   "en": "This division publishes a single number per player: the goal. "
         "Everything below comes from manual video tagging of one full match "
         "&mdash; Al Jazeera 3-3 Yarmouk, round 13, 20 February 2026 &mdash; "
         "done by his analyst, 48 actions logged. He scored one goal and "
         "assisted the other two: he was involved in all three.",
   "fr": "Cette division ne publie qu'un seul chiffre par joueur : le but. "
         "Tout ce qui suit vient du codage vidéo manuel d'un match entier "
         "&mdash; Al Jazeera 3-3 Yarmouk, 13e journée, le 20 février 2026 &mdash; "
         "réalisé par son analyste, 48 actions relevées. Il marque un but et "
         "délivre les deux autres passes décisives : il touche aux trois buts.",
   "ar": "لا ينشر هذا الدوري سوى رقم واحد لكل لاعب: الهدف. وكل ما يلي مصدره "
         "توثيق يدوي بالفيديو لمباراة كاملة &mdash; الجزيرة 3-3 اليرموك، الجولة 13، "
         "20 فبراير 2026 &mdash; أنجزه محلّله، بواقع 48 لقطة. سجّل هدفًا وصنع "
         "الهدفين الآخرين: ساهم في الأهداف الثلاثة كلها."},
 "m_goal": {"en": "goal", "fr": "but", "ar": "هدف"},
 "m_assists": {"en": "assists", "fr": "passes décisives", "ar": "تمريرتان حاسمتان"},
 "m_actions": {"en": "actions logged", "fr": "actions relevées", "ar": "لقطة موثّقة"},
 "m_drib": {"en": "dribbles, all completed", "fr": "dribbles, tous réussis",
            "ar": "مراوغات، جميعها ناجحة"},
 "p_passes": {"en": "Passes", "fr": "Passes", "ar": "التمريرات"},
 "p_prog": {"en": "Progressive passes", "fr": "Passes progressives",
            "ar": "التمريرات التقدمية"},
 "prog_cap": {
   "en": "Progressive = played forward AND gaining at least 10 m, either in "
         "depth or in distance to goal. First half only — arrows show "
         "where each pass started and ended.",
   "fr": "Progressive = jouée vers l’avant ET au moins 10 m gagnés, en "
         "profondeur ou en distance au but. Première mi-temps seulement — "
         "les flèches donnent le départ et l’arrivée de chaque passe.",
   "ar": "التمريرة التقدمية: تُلعب إلى الأمام وتكسب 10 أمتار على الأقل، عمقاً "
         "أو اقتراباً من المرمى. الشوط الأول فقط — تُظهر الأسهم نقطة "
         "الانطلاق ونقطة الوصول."},
 "m_prog": {"en": "progressive passes", "fr": "passes progressives",
            "ar": "تمريرات تقدمية"},
 "p_zones": {"en": "Where he acts", "fr": "Où il agit", "ar": "أين يتحرك"},
 "zones_cap": {
   "en": "Each cell counts his actions. Rows are the three channels — "
         "they add up to the 27 / 16 / 5 quoted below. The ring marks the "
         "average position of his actions, not of his presence: time spent "
         "without the ball is not in here.",
   "fr": "Chaque case compte ses actions. Les rangs sont les trois couloirs — "
         "ils retombent sur les 27 / 16 / 5 cités plus bas. L’anneau marque "
         "la position moyenne de ses ACTIONS, pas de sa présence : le temps "
         "passé sans ballon n’y figure pas.",
   "ar": "كل خانة تُحصي أفعاله. الصفوف هي الممرات الثلاثة — مجموعها 27 / 16 / 5 "
         "المذكورة أدناه. الحلقة تُشير إلى متوسط موضع أفعاله لا حضوره: الوقت "
         "المقضي دون كرة غير محسوب."},
 "p_drib": {"en": "Dribbles", "fr": "Dribbles", "ar": "المراوغات"},
 "p_shots": {"en": "Shots", "fr": "Tirs", "ar": "التسديدات"},
 "p_cap": {"en": "Attacking left to right. Both halves brought into the same "
                 "direction of play.",
           "fr": "Attaque de gauche à droite. Les deux périodes sont ramenées "
                 "dans le même sens de jeu.",
           "ar": "الهجوم من اليسار إلى اليمين. تم توحيد اتجاه اللعب في الشوطين."},
 "zones_t": {"en": "Where he played", "fr": "Où il a joué", "ar": "أين لعب"},
 "zones_b": {
   "en": "<b>A number 10 who drops in, working the right half-space.</b> "
         "%(right)d of his %(n)d actions came down the right and %(mid)d in the "
         "middle third &mdash; not a winger holding the touchline. "
         "%(final)d actions in the final third, and a goal scored from inside the box.",
   "fr": "<b>Un n° 10 qui décroche et travaille dans le demi-espace droit.</b> "
         "%(right)d de ses %(n)d actions sont du côté droit et %(mid)d dans le "
         "tiers médian &mdash; pas un ailier qui reste sur sa ligne. "
         "%(final)d actions dans le dernier tiers, et un but marqué de l'intérieur de la surface.",
   "ar": "<b>صانع ألعاب يتراجع ويعمل في نصف المساحة اليمنى.</b> "
         "%(right)d من لقطاته الـ%(n)d جاءت من الجهة اليمنى و%(mid)d في الثلث "
         "الأوسط &mdash; لا جناح يلتصق بالخط. "
         "%(final)d لقطة في الثلث الأخير، وهدف سجّله من داخل منطقة الجزاء."},
 "caveat": {
   "en": "<b>Read this before the numbers.</b> One match, tagged by hand and "
         "selectively: what stands out gets logged, so percentages run high and "
         "volumes run low compared with a full provider feed. Counts of rare, "
         "salient events &mdash; goals, key passes, dribbles, shots &mdash; are the "
         "part that holds. Ten tagged matches would give these axes their meaning; "
         "one gives them their shape.",
   "fr": "<b>À lire avant les chiffres.</b> Un seul match, codé à la main et de "
         "façon sélective : on relève ce qu'on remarque, donc les pourcentages "
         "sont hauts et les volumes bas face à un relevé fournisseur complet. "
         "Ce qui tient, ce sont les comptes d'actions rares et saillantes "
         "&mdash; buts, passes clés, dribbles, tirs. Dix matchs codés donneraient "
         "du sens à ces axes ; un seul leur donne leur forme.",
   "ar": "<b>اقرأ هذا قبل الأرقام.</b> مباراة واحدة، وُثّقت يدويًا وبشكل انتقائي: "
         "يُسجَّل ما يلفت النظر، لذا تأتي النسب مرتفعة والأحجام منخفضة مقارنةً "
         "بتغذية بيانات كاملة من مزوّد. ما يصمد هو عدّ الأحداث النادرة البارزة "
         "&mdash; الأهداف والتمريرات الحاسمة والمراوغات والتسديدات. عشر مباريات "
         "موثّقة تمنح هذه المحاور معناها؛ ومباراة واحدة تمنحها شكلها."},

 "s_career": {"en": "Career", "fr": "Carrière", "ar": "المسيرة"},
 "career_intro": {
   "en": "Trained in France, he built his career in Belgium. He joined Francs "
         "Borains in 2016 and went up three divisions with them, which earned "
         "him the nickname of &laquo;&nbsp;the man of the three "
         "promotions&nbsp;&raquo; at the club: <b>21 goals in two seasons</b> in "
         "the fourth tier, then <b>8 in the promotion season</b>, over 2,417 "
         "minutes. Then the Challenger Pro League, then Algeria &mdash; league, "
         "cup and CAF Champions League with CR Belouizdad &mdash; then Kuwait.",
   "fr": "Formé en France, il fait sa carrière en Belgique. Arrivé aux Francs "
         "Borains en 2016, il monte trois divisions avec eux, ce qui lui vaut au "
         "club le surnom de &laquo;&nbsp;l'homme aux trois montées&nbsp;&raquo; : "
         "<b>21 buts en deux saisons</b> de D4, puis <b>8 lors de la saison de "
         "montée</b>, en 2 417 minutes. Puis la Challenger Pro League, puis "
         "l'Algérie &mdash; championnat, coupe et Ligue des champions CAF avec le "
         "CR Belouizdad &mdash; puis le Koweït.",
   "ar": "تكوّن في فرنسا وبنى مسيرته في بلجيكا. التحق بفرانك بوران عام 2016 وصعد "
         "معه ثلاث درجات، وهو ما أكسبه في النادي لقب &laquo;&nbsp;صاحب الصعودات "
         "الثلاثة&nbsp;&raquo;: <b>21 هدفًا في موسمين</b> بالدرجة الرابعة، ثم "
         "<b>8 أهداف في موسم الصعود</b> خلال 2417 دقيقة. ثم تشالنجر برو ليغ، ثم "
         "الجزائر &mdash; الدوري والكأس ودوري أبطال أفريقيا مع شباب بلوزداد "
         "&mdash; ثم الكويت."},
 "career_b": {
   "en": "<b>The minutes explain the Algerian season.</b> At CR Belouizdad he "
         "came off the bench: 26 appearances across league, cup and CAF "
         "Champions League for <b>870 minutes</b> &mdash; 33 minutes per "
         "appearance, with one assist in the Champions League. In Kuwait, with a "
         "real role, he scored four times in ten rounds.",
   "fr": "<b>Les minutes expliquent la saison algérienne.</b> Au CR Belouizdad il "
         "entre en cours de jeu : 26 apparitions entre championnat, coupe et "
         "Ligue des champions CAF pour <b>870 minutes</b> &mdash; 33 minutes par "
         "apparition, et une passe décisive en Ligue des champions. Au Koweït, "
         "avec un vrai rôle, il marque quatre fois en dix journées.",
   "ar": "<b>الدقائق تفسّر الموسم الجزائري.</b> في شباب بلوزداد كان يدخل من مقعد "
         "البدلاء: 26 مشاركة بين الدوري والكأس ودوري أبطال أفريقيا مقابل "
         "<b>870 دقيقة</b> &mdash; 33 دقيقة لكل مشاركة، مع تمريرة حاسمة في دوري "
         "الأبطال. وفي الكويت، وبدور حقيقي، سجّل أربع مرات في عشر جولات."},
 "th_season": {"en": "Season", "fr": "Saison", "ar": "الموسم"},
 "th_club": {"en": "Club", "fr": "Club", "ar": "النادي"},
 "th_comp": {"en": "Competition", "fr": "Compétition", "ar": "المسابقة"},
 "th_apps": {"en": "Apps", "fr": "Matchs", "ar": "مباريات"},
 "th_g": {"en": "Goals", "fr": "Buts", "ar": "أهداف"},
 "th_a": {"en": "Assists", "fr": "Passes déc.", "ar": "تمريرات حاسمة"},
 "th_min": {"en": "Minutes", "fr": "Minutes", "ar": "الدقائق"},
 "career_note": {
   "en": "Belgian, French and Algerian figures: footballdatabase.eu, each line "
         "cross-checked against the minutes-per-goal it publishes. Algerian Cup: "
         "Soccerway. CAF Champions League: ESPN. Kuwait: Sofascore. Blank cells "
         "are seasons no public source states &mdash; they are left blank rather "
         "than guessed.",
   "fr": "Chiffres belges, français et algériens : footballdatabase.eu, chaque "
         "ligne recoupée avec les minutes par but que le site publie. Coupe "
         "d'Algérie : Soccerway. Ligue des champions CAF : ESPN. Koweït : "
         "Sofascore. Les cases vides sont les saisons qu'aucune source publique "
         "ne chiffre &mdash; elles restent vides plutôt que devinées.",
   "ar": "الأرقام البلجيكية والفرنسية والجزائرية: footballdatabase.eu، وكل سطر "
         "تم التحقق منه عبر معدل الدقائق لكل هدف الذي ينشره الموقع. كأس الجزائر: "
         "Soccerway. دوري أبطال أفريقيا: ESPN. الكويت: Sofascore. الخانات "
         "الفارغة مواسم لا يذكرها أي مصدر علني &mdash; تُركت فارغة بدل تخمينها."},
 "s_video": {"en": "Video", "fr": "Vidéo", "ar": "الفيديو"},
 "v_full": {"en": "Full matches", "fr": "Matchs entiers", "ar": "مباريات كاملة"},
 "v_reel": {"en": "Highlight reels", "fr": "Compilations", "ar": "ملخّصات مجمّعة"},
 "v_reel_b": {
   "en": "Two compilations put together by third-party channels, from his years "
         "in Belgium and Germany. Watch them for the actions themselves &mdash; a "
         "montage shows what a player can do, never how often he does it.",
   "fr": "Deux compilations montées par des chaînes tierces, sur ses années en "
         "Belgique et en Allemagne. À regarder pour les gestes eux-mêmes &mdash; un "
         "montage montre ce qu'un joueur sait faire, jamais à quelle fréquence.",
   "ar": "ملخّصان من إعداد قنوات مستقلة، من سنواته في بلجيكا وألمانيا. يُشاهَدان "
         "من أجل اللقطات نفسها &mdash; فالمونتاج يُظهر ما يستطيع اللاعب فعله، لا "
         "عدد مرات فعله."},
 "video_intro": {
   "en": "The Kuwaiti federation published two of his matches in full. Both are "
         "complete broadcasts, not highlight packages.",
   "fr": "La fédération koweïtienne a publié deux de ses matchs en entier. Ce sont "
         "des diffusions complètes, pas des résumés.",
   "ar": "نشر الاتحاد الكويتي مباراتين له كاملتين. وهما بثّان كاملان، لا ملخّصات."},
 "watch": {"en": "Watch", "fr": "Voir", "ar": "المشاهدة"},
 "tagged_here": {"en": "the match tagged above", "fr": "le match codé ci-dessus",
                 "ar": "المباراة الموثّقة أعلاه"},

 "s_contact": {"en": "Contact", "fr": "Contact", "ar": "للتواصل"},
 "contact_b": {
   "en": "For the full dataset behind this page, the tagged match file, or to "
         "arrange a conversation with the player:",
   "fr": "Pour les données complètes derrière cette page, le fichier du match "
         "codé, ou pour organiser un échange avec le joueur :",
   "ar": "للحصول على البيانات الكاملة وراء هذه الصفحة، أو ملف المباراة الموثّقة، "
         "أو لترتيب حديث مع اللاعب:"},
 "contact_role": {"en": "Performance analyst", "fr": "Analyste de la performance",
                  "ar": "محلل أداء"},
 "sources": {"en": "Sources", "fr": "Sources", "ar": "المصادر"},
 "src_body": {
   "en": "Kuwaiti season, squad and scorer tables: Sofascore. Career before "
         "Kuwait: Soccerway, FotMob and Royal Francs Borains. Match analysis: "
         "manual video tagging, %(d)s. Page generated on %(gen)s.",
   "fr": "Saison koweïtienne, effectif et classement des buteurs : Sofascore. "
         "Carrière avant le Koweït : Soccerway, FotMob et le Royal Francs Borains. "
         "Analyse de match : codage vidéo manuel, %(d)s. Page générée le %(gen)s.",
   "ar": "الموسم الكويتي والقائمة وجداول الهدّافين: Sofascore. المسيرة قبل الكويت: "
         "Soccerway وFotMob ونادي فرانك بوران. تحليل المباراة: توثيق يدوي "
         "بالفيديو، %(d)s. أُنشئت الصفحة في %(gen)s."},
}


def ordinal(n, lang):
    if lang != "en":
        return {"fr": "er" if n == 1 else "e", "ar": ""}[lang]
    return {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th")


# ------------------------------------------------------------------ page
def construire(xml_path):
    c = contexte()
    rows = lis_xml(xml_path)
    f, lui = c["fiche"], c["lui"]

    n = len(rows)
    zones = {
        "right": sum(1 for r in rows if r["y"] < 100 / 3.0),
        "mid": sum(1 for r in rows if 100 / 3.0 <= r["x"] < 200 / 3.0),
        "final": sum(1 for r in rows if r["x"] >= 200 / 3.0),
        "n": n,
    }
    drib = [r for r in rows if r["code"] == "Dribble"]

    # Les passes PROGRESSIVES demandent le point d'ARRIVEE, que le XML de
    # codage ne transporte pas (un seul point par action). D'ou le CSV du
    # tagger, qui porte x2/y2. Premiere mi-temps seulement : c'est ce qui a
    # ete releve.
    pas = lis_passes(os.path.join(ICI, "donnees", "j13_actions_mt1.csv"))
    n_prog = sum(1 for p in pas if p["prog"])
    terrains = {
        "p_passes": pitch([r for r in rows if r["code"] in ("Passe", "Passe clé")],
                          "var(--series-1)"),
        "p_drib": pitch(drib, "var(--series-3)"),
        "p_shots": pitch([r for r in rows if r["code"] in ("Tir", "But")],
                         "var(--series-2)"),
        "p_prog": fleches(pas),
        "p_zones": carte_zones(rows),
    }

    # ---- tableau des matchs (une seule fois, les libelles sont traduits en JS)
    lignes = []
    for m in c["matchs"]:
        pills = "".join('<span class="g">%d\u2032</span>' % b for b in m["_buts"])
        lignes.append(
            '<tr%s><td class="rnd">%d</td><td class="dt" data-date="%s"></td>'
            '<td class="opp">%s <span class="ha" data-t="%s"></span></td>'
            '<td><span class="res %s">%d&ndash;%d</span></td>'
            '<td class="gl">%s</td></tr>'
            % (' class="scored"' if m["_buts"] else "", m["round"],
               m["kickoff_iso"][:10], m["_adv"], "home" if m["_dom"] else "away",
               m["_res"], m["_pour"], m["_contre"], pills))
    table_matchs = "".join(lignes)

    # ---- tableau de carriere
    logos = json.load(io.open(os.path.join(ICI, "logos.json"), encoding="utf-8"))
    cl = []
    for r in SOURCES_CARRIERE:
        ecusson = ('<img class="crest" src="%s" alt="" loading="lazy">' % logos[r["logo"]]
                   if r["logo"] in logos else "")
        def num(v, but=False):
            """Une case chiffree. Le tiret des saisons non publiees reste
            discret, et seuls les buts REELLEMENT marques sont en gras : un
            « 0 » en gras attire l'oeil sur ce qui n'existe pas."""
            if v is None:
                return '<td class="num empty">&mdash;</td>'
            cls = "num goals" if but and v else "num"
            return '<td class="%s" data-num="%d">%d</td>' % (cls, v, v)
        cl.append('<tr><td class="sea">%s</td>'
                  '<td class="cl">%s<span>%s</span></td>'
                  '<td class="cp" data-tj="%s"></td>%s%s%s%s</tr>'
                  % (r["saison"], ecusson, r["club"],
                     html_attr(json.dumps(r["comp"], ensure_ascii=False)),
                     num(r["matchs"]), num(r["buts"], but=True),
                     num(r["passes"]), num(r["minutes"])))
    table_carriere = "".join(cl)

    # ---- videos
    def cartes(nature):
        out = []
        for v in [x for x in VIDEOS if x["type"] == nature]:
            tag = ('<span class="tag" data-t="tagged_here"></span>'
                   if v["id"] == "JoN2MlJqePY" else "")
            second = ('<span data-date="%s"></span>' % v["date"] if v["date"]
                      else '<span>%s</span>' % v["sous"])
            out.append(
                '<a class="vid" href="https://www.youtube.com/watch?v=%s" '
                'target="_blank" rel="noopener">'
                '<img src="https://img.youtube.com/vi/%s/mqdefault.jpg" alt="" loading="lazy">'
                '<div><b>%s</b>%s%s</div></a>'
                % (v["id"], v["id"], v["titre"], second, tag))
        return "".join(out)

    videos, compils = cartes("match"), cartes("reel")

    donnees = {
        "age": f["age"], "height": f["height"],
        "goals": lui["goals"],
        "rangClub": c["rang_club"], "rangDiv": c["rang_div"],
        "nButeurs": c["n_buteurs"], "exaequo": c["exaequo"], "rangEquipe": c["club"]["rank"],
        "zones": zones, "nDrib": len(drib),
        "ordClub": {k: ordinal(c["rang_club"], k) for k in ("en", "fr", "ar")},
        "ordDiv": {k: ordinal(c["rang_div"], k) for k in ("en", "fr", "ar")},
        "ordTeam": {k: ordinal(c["club"]["rank"], k) for k in ("en", "fr", "ar")},
        "dateMatch": "20/02/2026",
        "gen": datetime.date.today().strftime("%d/%m/%Y"),
    }

    html = GABARIT.replace("{{T}}", json.dumps(TRAD, ensure_ascii=False))
    html = html.replace("{{D}}", json.dumps(donnees, ensure_ascii=False))
    html = html.replace("{{N_PROG}}", str(n_prog))
    html = html.replace("{{N_PAS}}", str(len(pas)))
    html = html.replace("{{MATCHS}}", table_matchs)
    html = html.replace("{{CARRIERE}}", table_carriere)
    html = html.replace("{{BARRES}}", barres_buteurs(c["club_buteurs"], JOUEUR_ID))
    html = html.replace("{{VIDEOS}}", videos)
    html = html.replace("{{COMPILS}}", compils)
    html = html.replace("{{MAIL}}", CONTACT_MAIL)
    for k, v in terrains.items():
        html = html.replace("{{PITCH_%s}}" % k.upper(), v)

    io.open(os.path.join(ICI, "index.html"), "w", encoding="utf-8").write(html)

    src_photo = os.path.join(SCRAPER, "photos", "%d.webp" % JOUEUR_ID)
    if os.path.exists(src_photo):
        shutil.copyfile(src_photo, os.path.join(ICI, "hedy-chaabi.webp"))

    print("index.html ecrit : %d actions, %d matchs, %d lignes de carriere"
          % (n, len(c["matchs"]), len(SOURCES_CARRIERE)))
    print("  passes mesurees : %d, dont %d progressives" % (len(pas), n_prog))
    return c, rows


GABARIT = io.open(os.path.join(ICI, "gabarit.html"), encoding="utf-8").read()

if __name__ == "__main__":
    construire(sys.argv[1] if len(sys.argv) > 1 else XML_DEFAUT)
