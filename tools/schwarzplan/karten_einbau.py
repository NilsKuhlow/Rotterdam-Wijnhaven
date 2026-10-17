# -*- coding: utf-8 -*-
"""Die beiden gemeinfreien Karten in die offenen Kapitel setzen.

Der Auftrag war, Planunterlagen herauszusuchen. Das Ergebnis faellt
besser aus als geplant: Die beiden wichtigsten Blaetter sind gemeinfrei
und gehoeren deshalb nicht hinter das Schloss, sondern offen in die
Seite. Das Schloss bleibt fuer das, was wirklich geschuetzt ist.

  Historie   Gemeente Rotterdam en omgeving, 1:10.000, 1940
             Die Vorkriegsstadt mit Strassennamen, Ausschnitt Innenstadt.
             Damit hat das Projekt zum ersten Mal einen Plan des
             Zustands, den der 14. Mai 1940 beendete. Bisher stand
             darueber nur Prosa, und einmal eine erfundene
             Platzhalterzeichnung, die wieder entfernt wurde.

  Basisplan  Oud en nieuw Rotterdam, 1:5.000, 18. Mai 1955
             Der Vorkriegsgrundriss, darueber der Plan des neuen
             Stadtkerns und der Stand des Wiederaufbaus, dazu die
             Brandgrenze in Gelb. Ein Blatt, das genau die Frage des
             Kapitels beantwortet: was vom Plan wurde gebaut.

Beide Bildunterschriften nennen Blattitel, Massstab, Herausgeber und
Rechtelage. Die Schutzfrist des Blattes von 1955 lief siebzig Jahre nach
Veroeffentlichung ab, also 2025; das steht ausdruecklich dabei, damit
niemand es spaeter nachrechnen muss.
"""
import io
import os
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')

# ── Texte, dreisprachig ────────────────────────────────────────────────
T1940 = {
 'de': ('Gemeente Rotterdam en omgeving, Maßstab 1:10.000, herausgegeben vom '
        'Gemeentelijke Technische Dienst, 1940. Ausschnitt der Innenstadt: die '
        'feinkörnige Parzellierung, die der 14. Mai 1940 beendete. Wijnhaven, '
        'Scheepmakershaven und Leuvehaven liegen noch inmitten geschlossener '
        'Blockränder.',
        'Stadtplan von Rotterdam 1940, Ausschnitt der Innenstadt mit Wijnhaven, '
        'Leuvehaven und Oude Haven'),
 'nl': ('Gemeente Rotterdam en omgeving, schaal 1:10.000, uitgegeven door den '
        'Gemeentelijken Technischen Dienst, 1940. Uitsnede van de binnenstad: de '
        'fijnkorrelige parcellering waaraan 14 mei 1940 een einde maakte. '
        'Wijnhaven, Scheepmakershaven en Leuvehaven liggen nog te midden van '
        'gesloten bouwblokken.',
        'Plattegrond van Rotterdam 1940, uitsnede binnenstad met Wijnhaven, '
        'Leuvehaven en Oude Haven'),
 'en': ('Gemeente Rotterdam en omgeving, scale 1:10,000, published by the municipal '
        'technical service, 1940. A detail of the inner city: the fine-grained '
        'parcelling that 14 May 1940 brought to an end. Wijnhaven, Scheepmakershaven '
        'and Leuvehaven still lie among closed perimeter blocks.',
        'City plan of Rotterdam 1940, detail of the inner city with Wijnhaven, '
        'Leuvehaven and Oude Haven'),
}
Q1940 = {
 'de': 'Stadsarchief Rotterdam, von dort ausdrücklich als gemeinfrei freigegeben. '
       'Über Wikimedia Commons.',
 'nl': 'Stadsarchief Rotterdam, door het archief uitdrukkelijk vrijgegeven als '
       'publiek domein. Via Wikimedia Commons.',
 'en': 'Stadsarchief Rotterdam, expressly released by the archive into the public '
       'domain. Via Wikimedia Commons.',
}
U1940 = 'https://commons.wikimedia.org/wiki/File:Plattegrond_van_Rotterdam_in_1940.jpg'

T1955 = {
 'de': ('Oud en nieuw Rotterdam, Maßstab 1:5.000, Gemeentewerken Rotterdam, Abteilung '
        'Kartografie, 18. Mai 1955. Das Blatt legt dreierlei übereinander: den '
        'Grundriss vor Mai 1940, den Plan des neuen Stadtkerns und den Stand des '
        'Wiederaufbaus an jenem Tag. Gelb die Brandgrenze. Damit zeigt es in einem '
        'Bild, was der Basisplan vorsah und was davon nach neun Jahren stand.',
        'Karte Oud en nieuw Rotterdam von 1955, Vorkriegsgrundriss mit dem Plan des '
        'neuen Stadtkerns und der Brandgrenze'),
 'nl': ('Oud en nieuw Rotterdam, schaal 1:5.000, Gemeentewerken Rotterdam, afdeling '
        'kartografie, 18 mei 1955. Het blad legt drie dingen over elkaar: de '
        'plattegrond van vóór mei 1940, het plan van de nieuwe stadskern en de stand '
        'van de herbouw op die dag. In geel de brandgrens. Zo laat het in één beeld '
        'zien wat het Basisplan voorzag en wat er na negen jaar stond.',
        'Kaart Oud en nieuw Rotterdam uit 1955, vooroorlogse plattegrond met het plan '
        'van de nieuwe stadskern en de brandgrens'),
 'en': ('Oud en nieuw Rotterdam, scale 1:5,000, Rotterdam Public Works, cartography '
        'division, 18 May 1955. The sheet lays three things over one another: the '
        'street plan before May 1940, the plan of the new city core, and how far the '
        'rebuilding had got that day. The fire boundary is in yellow. In one image it '
        'shows what the Basisplan intended and what of it stood after nine years.',
        'Map Oud en nieuw Rotterdam from 1955, pre-war street plan with the plan of '
        'the new city core and the fire boundary'),
}
Q1955 = {
 'de': 'Gemeinfrei: anonymes Werk, Schutzfrist siebzig Jahre nach Veröffentlichung, '
       'abgelaufen 2025. Über Wikimedia Commons.',
 'nl': 'Publiek domein: anoniem werk, beschermingstermijn zeventig jaar na publicatie, '
       'verstreken in 2025. Via Wikimedia Commons.',
 'en': 'Public domain: anonymous work, seventy-year term from publication, expired in '
       '2025. Via Wikimedia Commons.',
}
U1955 = ('https://commons.wikimedia.org/wiki/File:Kaart_Rotterdam_'
         '(BF3747741ECA9E5D5CE94D17F6082CDA)_1945_%C3%A8n_1955.jpg')


def js(d):
    import json
    return json.dumps(d, ensure_ascii=False)


# ── Die Figuren in die beiden Kapitel ──────────────────────────────────
HIST_ALT = """  HISTORIE.figures = [{ src: "img/plan-1913.webp", w: 1233, h: 1403,
                        alt: t.bildunter, cap: t.bildunter }]
                      .concat(_semFiguren('historie'));"""
HIST_NEU = """  /* Zwei Blaetter: der Verkehrsplan von 1913 und, seit Oktober 2026, der
     Stadtplan von 1940. Erst mit dem zweiten hat das Kapitel ein Bild des
     Zustands, den der 14. Mai beendete; vorher stand darueber nur Prosa. */
  HISTORIE.figures = [{ src: "img/plan-1913.webp", w: 1233, h: 1403,
                        alt: t.bildunter, cap: t.bildunter },
                      { src: "img/plan-1940.webp", w: 2200, h: 1408,
                        alt: KARTE_1940.alt[currentLang] || KARTE_1940.alt.de,
                        cap: KARTE_1940.cap[currentLang] || KARTE_1940.cap.de,
                        credit: KARTE_1940.q[currentLang] || KARTE_1940.q.de,
                        creditUrl: KARTE_1940.u }]
                      .concat(_semFiguren('historie'));"""

BP_ALT = """  /* Leer, solange zugesperrt. Was aus dem Seminarbereich hierher
     gehoert, kommt erst dazu, wenn der Schluessel da ist. */
  BASISPLAN.figures = _semFiguren('basisplan');"""
BP_NEU = """  /* Das Blatt von 1955 steht offen: anonymes Werk, Schutzfrist 2025
     abgelaufen. Was aus dem Seminarbereich dazugehoert, kommt erst, wenn
     der Schluessel da ist. */
  BASISPLAN.figures = [{ src: "img/oud-en-nieuw-1955.webp", w: 2200, h: 1521,
                         alt: KARTE_1955.alt[currentLang] || KARTE_1955.alt.de,
                         cap: KARTE_1955.cap[currentLang] || KARTE_1955.cap.de,
                         credit: KARTE_1955.q[currentLang] || KARTE_1955.q.de,
                         creditUrl: KARTE_1955.u }]
                       .concat(_semFiguren('basisplan'));"""

DATEN_ANKER = "var HISTORIE = { slug: \"historie\" };"


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    daten = ("""/* Zwei gemeinfreie Blaetter, im Oktober 2026 dazugekommen. Sie stehen
   offen und nicht hinter dem Schloss: Was frei ist, gehoert nach vorn.
   Die Rechtelage steht in der Bildunterschrift, nicht nur hier. */
var KARTE_1940 = { cap: %s, alt: %s, q: %s, u: %s };
var KARTE_1955 = { cap: %s, alt: %s, q: %s, u: %s };

""" % (js({k: v[0] for k, v in T1940.items()}), js({k: v[1] for k, v in T1940.items()}),
       js(Q1940), js(U1940),
       js({k: v[0] for k, v in T1955.items()}), js({k: v[1] for k, v in T1955.items()}),
       js(Q1955), js(U1955))) + DATEN_ANKER

    tausch(DATEN_ANKER, daten, 'Texte der beiden Karten')
    tausch(HIST_ALT, HIST_NEU, 'Stadtplan 1940 in das Historie-Kapitel')
    tausch(BP_ALT, BP_NEU, 'Oud en nieuw 1955 in das Basisplan-Kapitel')

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
