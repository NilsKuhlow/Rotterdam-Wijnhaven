# -*- coding: utf-8 -*-
"""Die Grundrisse in das Verzeichnis des Seminarbereichs eintragen.

Gefunden habe ich sie bei ArchDaily, das die Zeichnungen der Bueros
veroeffentlicht. Eine Lizenz steht dort nirgends; die Rechte liegen bei
den Urhebern. Also gehoeren sie hinter das Schloss, und genau dafuer
ist es da.

Ausgewaehlt ist, was erklaert, und nicht alles, was da war. Von den
sechs fast gleichen Wohnungsgeschossen der Markthal etwa steht hier
eines; wer alle braucht, findet sie im Ordner.

Drei der sieben Bauten sind damit abgedeckt. Fuer das Witte Huis, Red
Apple, EY Netherlands und das Wijnhaveneiland habe ich nichts
Brauchbares gefunden; das steht so im Bericht und wird nicht
beschoenigt.

'ziel' ist hier der Slug der Station. Die Zeichnungen erscheinen dann
im Eintrag des Baus selbst und nicht in einem eigenen Kapitel, denn
dort sucht man sie.
"""
import io
import os

QUELLEN = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
           r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Input\Privat"
           r"\quellen.py")

URHEBER = {
 'kubuswoningen': ('Piet Blom. Zeichnung aus dem Werkarchiv, veröffentlicht bei '
                   'ArchDaily. Rechte beim Urheber, keine Lizenz erteilt.',
                   'https://www.archdaily.com/482339/ad-classics-kubuswoningen-piet-blom'),
 'markthal':      ('MVRDV, Rotterdam. Veröffentlicht bei ArchDaily. Rechte beim '
                   'Büro, keine Lizenz erteilt.',
                   'https://www.archdaily.com/553933/markthal-rotterdam-mvrdv'),
 'casanova':      ('Barcode Architects, Rotterdam. Veröffentlicht bei ArchDaily. '
                   'Rechte beim Büro, keine Lizenz erteilt.',
                   'https://www.archdaily.com/1006805/casanova-building-barcode-architects'),
}

# datei, Station, (de, nl, en)
PLAENE = [
 ('kubuswoningen-lageplan.jpg', 'kubuswoningen', (
  'Lageplan. Das Ensemble überbaut die Blaak; der Zug der Verkehrsachse ist unter '
  'den Würfeln als Trasse zu lesen.',
  'Situatietekening. Het ensemble overbouwt de Blaak; het tracé van de '
  'verkeersas is onder de kubussen te lezen.',
  'Site plan. The ensemble bridges the Blaak; the line of the traffic axis reads '
  'beneath the cubes.')),
 ('kubuswoningen-plan-strasse.jpg', 'kubuswoningen', (
  'Grundriss Straßenebene. Unten läuft die mehrspurige Blaak samt Metrotunnel '
  'durch, die Pfeiler stehen dazwischen.',
  'Plattegrond straatniveau. Onderlangs loopt de Blaak met de metrotunnel, de '
  'pijlers staan ertussen.',
  'Plan at street level. The multi-lane Blaak and the metro tunnel run through '
  'below; the piers stand between them.')),
 ('kubuswoningen-plan-promenade.jpg', 'kubuswoningen', (
  'Grundriss Fußgängerebene. Die Ebene, die Altstadt und Oude Haven verbindet, '
  'und zugleich das Dach der Verkehrsachse.',
  'Plattegrond voetgangersniveau. Het vlak dat de oude stad met de Oude Haven '
  'verbindt en tegelijk het dak van de verkeersas is.',
  'Plan at promenade level. The deck that links the old town with the Oude Haven '
  'and at once roofs the traffic axis.')),
 ('kubuswoningen-plan-wohnen.jpg', 'kubuswoningen', (
  'Grundriss Wohnebene. Die 38 gekippten Würfel im Raster der Sechsecke; hier '
  'wird das Bild vom Wald aus Wohnungen zur Zeichnung.',
  'Plattegrond woonniveau. De 38 gekantelde kubussen in het zeshoekige raster; '
  'hier wordt het beeld van het woonbos een tekening.',
  'Plan at living level. The 38 tilted cubes on the hexagonal grid; here the '
  'image of a forest of dwellings becomes a drawing.')),
 ('kubuswoningen-schnitt.jpg', 'kubuswoningen', (
  'Längsschnitt. Pfeiler, Fußgängerebene, Würfel und der Superkubus der Akademie '
  'in einer Zeichnung, koloriert von Blom selbst.',
  'Langsdoorsnede. Pijlers, voetgangersdek, kubussen en de superkubus van de '
  'academie in één tekening, door Blom zelf ingekleurd.',
  'Long section. Piers, pedestrian deck, cubes and the academy superstructure in '
  'one drawing, coloured by Blom himself.')),

 ('markthal-plan-1.jpg', 'markthal', (
  'Grundriss Markthalle. Die Stände in zwei Reihen unter dem Bogen, 96 an der '
  'Zahl, dazwischen der stützenfreie Raum.',
  'Plattegrond markthal. De kramen in twee rijen onder de boog, 96 in getal, '
  'daartussen de kolomvrije ruimte.',
  'Plan of the market hall. The stalls in two rows beneath the arch, 96 of them, '
  'with the column-free space between.')),
 ('markthal-plan-3.jpg', 'markthal', (
  'Grundriss eines Wohngeschosses. Die Wohnungen liegen beidseitig im Bogen; '
  'ihre Fenster schauen nach außen und in die Halle.',
  'Plattegrond van een woonlaag. De woningen liggen aan weerszijden in de boog; '
  'hun ramen kijken naar buiten en de hal in.',
  'Plan of a residential floor. The apartments sit on both flanks of the arch; '
  'their windows look outward and into the hall.')),
 ('markthal-plan-5.jpg', 'markthal', (
  'Grundriss im Scheitel. Oben wird der Bogen flach, die Wohnungen rücken '
  'zusammen und der Luftraum verengt sich.',
  'Plattegrond in de top. Boven wordt de boog vlak, de woningen schuiven samen '
  'en de luchtruimte versmalt.',
  'Plan at the crown. At the top the arch flattens, the apartments draw together '
  'and the void narrows.')),
 ('markthal-plan-6.jpg', 'markthal', (
  'Grundriss mit Umgebung. Der Bau sitzt zwischen Binnenrotte und Blaak; die '
  'Stirnseiten sind Glasnetze ohne tragende Rahmen.',
  'Plattegrond met omgeving. Het gebouw zit tussen Binnenrotte en Blaak; de '
  'kopgevels zijn glasnetten zonder dragend raamwerk.',
  'Plan with its surroundings. The building sits between Binnenrotte and Blaak; '
  'the end walls are glass nets without a load-bearing frame.')),
 ('markthal-schnitt.jpg', 'markthal', (
  'Querschnitt. Rund 40 Meter Scheitelhöhe, darunter 1.200 Stellplätze und der '
  'Supermarkt; der Bogen trägt 228 Wohnungen.',
  'Dwarsdoorsnede. Ruim 40 meter tophoogte, daaronder 1.200 parkeerplaatsen en '
  'de supermarkt; de boog draagt 228 woningen.',
  'Cross section. About 40 metres to the crown, with 1,200 parking spaces and the '
  'supermarket below; the arch carries 228 apartments.')),

 ('casanova-lageplan.jpg', 'casanova', (
  'Lageplan. Der Turm steht an der Spitze der Wijnhaven, auf drei Seiten von '
  'Wasser umgeben, und teilt den Sockel mit dem Nachbarn The Muse.',
  'Situatietekening. De toren staat op de punt van de Wijnhaven, aan drie zijden '
  'door water omgeven, en deelt de plint met buurman The Muse.',
  'Site plan. The tower stands at the tip of the Wijnhaven, water on three sides, '
  'sharing its plinth with its neighbour The Muse.')),
 ('casanova-plan-eg.jpg', 'casanova', (
  'Grundriss Erdgeschoss. Hier entscheidet sich, was der Bau zur Straße hin '
  'macht; genau die Frage, die der Rundgang an das Quartier stellt.',
  'Plattegrond begane grond. Hier valt de beslissing wat het gebouw aan de '
  'straat doet; precies de vraag die de rondgang aan de wijk stelt.',
  'Ground floor plan. This is where it is decided what the building does towards '
  'the street, the very question the walk puts to the quarter.')),
 ('casanova-plan-05.jpg', 'casanova', (
  'Grundriss im Sockel. Dachgarten und Gemeinschaftsräume liegen auf der '
  'Sockelplatte, nicht ebenerdig.',
  'Plattegrond in de plint. Daktuin en gemeenschappelijke ruimten liggen op het '
  'plintdak, niet op maaiveld.',
  'Plan within the plinth. Roof garden and shared rooms sit on the plinth roof, '
  'not at ground level.')),
 ('casanova-plan-14.jpg', 'casanova', (
  'Regelgeschoss des Turms. Der dreieckige Grundriss mit abgestumpften Ecken; '
  'daher die schlanke Wirkung der 35 Etagen.',
  'Standaardverdieping van de toren. De driehoekige plattegrond met afgestompte '
  'hoeken; vandaar de slanke werking van de 35 lagen.',
  'Typical tower floor. The triangular plan with truncated corners, which is why '
  'the 35 storeys read as slender.')),
 ('casanova-axonometrie.jpg', 'casanova', (
  'Axonometrie. CasaNova rot, der Nachbar The Muse grau; die unteren Geschosse '
  'ziehen sich ein, der Turm scheint auf einer Spitze zu stehen.',
  'Axonometrie. CasaNova in rood, buurman The Muse in grijs; de onderste lagen '
  'trekken zich terug, de toren lijkt op een punt te staan.',
  'Axonometric. CasaNova in red, its neighbour The Muse in grey; the lower floors '
  'draw in, so the tower appears to balance on a point.')),
]


def main():
    s = io.open(QUELLEN, encoding='utf-8').read()
    marke = 'STUECKE = [\n'
    assert s.count(marke) == 1
    teile = []
    for datei, ziel, (de, nl, en) in PLAENE:
        cred, url = URHEBER[ziel]
        art = {'kubuswoningen': 'Zeichnung', 'markthal': 'Zeichnung',
               'casanova': 'Zeichnung'}[ziel]
        teile.append(
            "    {\n"
            "        'datei': 'grundrisse/%s',\n"
            "        'ziel': '%s',\n"
            "        'credit': %r,\n"
            "        'creditUrl': '%s',\n"
            "        'de': {'cap': %r, 'alt': %r},\n"
            "        'nl': {'cap': %r, 'alt': %r},\n"
            "        'en': {'cap': %r, 'alt': %r},\n"
            "    },\n" % (datei, ziel, cred, url,
                          de, de.split('.')[0], nl, nl.split('.')[0],
                          en, en.split('.')[0]))
    s = s.replace(marke, marke + ''.join(teile), 1)
    io.open(QUELLEN, 'w', encoding='utf-8', newline='\n').write(s)
    print('%d Grundrisse eingetragen' % len(PLAENE))
    for z in ('kubuswoningen', 'markthal', 'casanova'):
        print('   %-14s %d Zeichnungen' % (z, sum(1 for p in PLAENE if p[1] == z)))


if __name__ == '__main__':
    main()
