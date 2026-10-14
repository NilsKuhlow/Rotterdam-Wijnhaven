# -*- coding: utf-8 -*-
"""Die beiden Kapitel in den Leseabschnitt aufnehmen.

Bisher waren sie nur ueber die zwei Knoepfe unter der Karte zu erreichen.
Damit standen sie neben dem Rundgang statt in ihm, und fuer einen Crawler
ohne JavaScript gab es sie gar nicht: Der Leseabschnitt ist der einzige
Ort, an dem Inhalt ungefiltert in der Quelle steht.

Sie erscheinen jetzt in derselben Form wie die sieben Stationen, aber
erkennbar als etwas anderes: roemische Ziffern statt 01 bis 07 und ein
weisses Feld statt einer Stationsfarbe. Beides sind keine Orte auf dem
Weg, sondern die Zeit davor und daneben.

Zur Datei: index.html haelt CRLF. Gelesen wird mit den ueblichen
Zeilenumbruechen, gearbeitet wird mit \\n, geschrieben wird wieder mit
CRLF. Alles andere hat hier schon einmal Markup hinter </html> gehaengt.
"""
import io
import sys

P = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
     r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
     r"\Rotterdam-Wijnhaven\index.html")

CSS_ANKER = """.rr-foot {
  font-family:var(--font-mono); font-size:.55rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-3);
  margin:3rem 0 0; max-width:52ch; line-height:1.9;
}"""

CSS_NEU = """/* Die beiden Kapitel stehen nach den sieben Stationen, in derselben Form.
   Stationen sind sie nicht: darum roemische Ziffern und ein weisses Feld
   statt einer Stationsfarbe. Die Zwischenueberschrift bleibt eine Marke,
   keine zweite Hauptzeile. */
.rr-kapitel-titel {
  font-family:var(--font-mono); font-weight:500; font-size:.55rem;
  letter-spacing:var(--tr-label); text-transform:uppercase; color:var(--ink-3);
  margin:3.2rem 0 1.4rem;
}
.rr-kapitel .rr-num { background:var(--paper-0); }
.rr-foot {
  font-family:var(--font-mono); font-size:.55rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-3);
  margin:3rem 0 0; max-width:52ch; line-height:1.9;
}"""

BLOECKE = {
 'de': {
  'marke': 'Zwei Kapitel zum Städtebau',
  'mehr': 'Kapitel öffnen',
  'eins': ('Die historische Stadt', 'Rotterdam am Wasser · 1609 bis 2007',
    'Das Viertel ist kein gewachsenes Ufer, sondern eine Konstruktion: 1609 der '
    'Leuvehaven, 1613 Wijnhaven und Scheepmakershaven, gegrabene Becken für den '
    'Umschlag. Das Kapitel verfolgt den Bogen von dort über den 14. Mai 1940 bis '
    'zur Stadsvisie 2030, die das Büroquartier 2007 zum Wohngebiet erklärte.',
    'historie'),
  'zwei': ('Der Basisplan von Van Traa', 'Cornelis van Traa · angenommen 28. Mai 1946',
    'Nach der Zerstörung stand nicht die Form zur Entscheidung, sondern die Methode. '
    'Van Traa legte Funktionen, Achsen und Baufelder fest und ließ die Bebauung offen. '
    'Für das Wijnhavengebiet hieß das Büros: Anfang der 1960er Jahre stand dort keine '
    'einzige Wohnung.',
    'basisplan'),
 },
 'nl': {
  'marke': 'Twee hoofdstukken over stedenbouw',
  'mehr': 'Hoofdstuk openen',
  'eins': ('De historische stad', 'Rotterdam aan het water · 1609 tot 2007',
    'De wijk is geen gegroeide oever maar een constructie: in 1609 de Leuvehaven, in '
    '1613 Wijnhaven en Scheepmakershaven, gegraven bekkens voor de overslag. Het '
    'hoofdstuk volgt de boog daarvandaan over 14 mei 1940 tot de Stadsvisie 2030, die '
    'het kantoorkwartier in 2007 tot woongebied verklaarde.',
    'historie'),
  'zwei': ('Het Basisplan van Van Traa', 'Cornelis van Traa · aangenomen 28 mei 1946',
    'Na de verwoesting ging het niet om de vorm maar om de methode. Van Traa legde '
    'functies, assen en bouwvelden vast en liet de bebouwing open. Voor het '
    'Wijnhavengebied betekende dat kantoren: begin jaren zestig stond er geen enkele '
    'woning meer.',
    'basisplan'),
 },
 'en': {
  'marke': 'Two chapters on urban design',
  'mehr': 'Open chapter',
  'eins': ('The historical city', 'Rotterdam on the water · 1609 to 2007',
    'The quarter is not a grown riverbank but a construction: the Leuvehaven in 1609, '
    'Wijnhaven and Scheepmakershaven in 1613, rectangular basins dug for cargo. The '
    'chapter follows the arc from there through 14 May 1940 to the Stadsvisie 2030, '
    'which in 2007 redefined the office district as a housing area.',
    'historie'),
  'zwei': ("Van Traa's Basisplan", 'Cornelis van Traa · adopted 28 May 1946',
    'After the destruction the decision was not about form but about method. Van Traa '
    'fixed functions, axes and building plots and left the buildings open. For the '
    'Wijnhaven area that meant offices: by the early 1960s not a single dwelling was '
    'left.',
    'basisplan'),
 },
}


def stueck(b):
    z = ['  <h3 class="rr-kapitel-titel">%s</h3>' % b['marke'],
         '  <ol class="rr-list rr-kapitel">']
    for ziffer, schluessel in (('I', 'eins'), ('II', 'zwei')):
        name, meta, text, anker = b[schluessel]
        z += ['    <li class="rr-item">',
              '      <h4 class="rr-name"><span class="rr-num">%s</span> %s</h4>'
              % (ziffer, name),
              '      <p class="rr-meta">%s</p>' % meta,
              '      <p>%s</p>' % text,
              '      <a class="rr-more" href="#%s">%s</a>' % (anker, b['mehr']),
              '    </li>']
    z.append('  </ol>')
    return '\n'.join(z) + '\n'


def main():
    s = io.open(P, encoding='utf-8').read()

    if s.count(CSS_ANKER) != 1:
        sys.exit('FEHLER: CSS-Anker %d mal gefunden' % s.count(CSS_ANKER))
    s = s.replace(CSS_ANKER, CSS_NEU)
    print('OK  CSS fuer die Kapitelliste')

    # Die drei Sprachbloecke des Leseabschnitts enden gleich. Nicht der
    # Reihe nach ersetzen: Der eingesetzte Text endet selbst wieder auf
    # dieses Muster, der zweite Durchgang landete sonst noch einmal im
    # deutschen Block. Darum einmal trennen und wieder zusammensetzen.
    alt = '  </ol>\n  <p class="rr-foot">'
    teile = s.split(alt)
    if len(teile) != 4:
        sys.exit('FEHLER: %d statt 3 Listenenden gefunden' % (len(teile) - 1))
    s = teile[0]
    for sprache, rest in zip(('de', 'nl', 'en'), teile[1:]):
        s += ('  </ol>\n' + stueck(BLOECKE[sprache])
              + '  <p class="rr-foot">' + rest)
        print('OK  Kapitelliste %s' % sprache)

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
