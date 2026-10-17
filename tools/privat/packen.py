# -*- coding: utf-8 -*-
"""Den Seminarbereich packen.

Die Website ist oeffentlich. Material, dessen Rechte bei Dritten liegen,
kann deshalb nicht einfach darauf liegen. Ein Passwort in JavaScript
aendert daran nichts: Die Dateien stuenden weiter unter oeffentlichen
Adressen, und wer die Adresse kennt, laedt sie. Also wird nicht
abgefragt, sondern verschluesselt. Veroeffentlicht wird nur Geheimtext.
Ohne Passwort ist das kein Bild, sondern Rauschen.

Dieses Skript verraet nichts und darf darum im Repo liegen. Was es
verarbeitet, liegt ausserhalb:

    Input\\Privat\\quellen.py     Titel, Bildunterschriften, Urheber
    Input\\Privat\\passwort.txt   das Passwort, eine Zeile
    Input\\Privat\\*.jpg|png|pdf  die Vorlagen

Keine dieser Dateien gehoert ins Repo. Die Tabelle nicht, weil sie sonst
verriete, was hinter dem Schloss liegt; das Passwort nicht aus dem
offensichtlichen Grund.

Erzeugt wird:

    privat/schluessel.json   Salz, Rundenzahl, ein Pruefblock
    privat/inhalt.bin        das verschluesselte Verzeichnis
    privat/<8 Byte hex>.bin  je Abbildung ein Geheimtext

Die Namen sind aus Passwort und Dateiname abgeleitet, nicht geraten:
Ein zweiter Lauf schreibt dieselben Namen, der Cache des Service Workers
laeuft also nicht voll. Zu erkennen ist an ihnen nichts.
"""
import argparse
import hashlib
import hmac
import io
import json
import os
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import krypto                                              # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..'))
ZIEL = os.path.join(REPO, 'privat')
VORGABE_QUELLE = os.path.abspath(os.path.join(REPO, '..', '..', 'Input', 'Privat'))

LANGE_KANTE = 2000          # Bildpunkte; Plaene will man vergroessern koennen
GUETE = 82                  # WebP, verlustbehaftet: Karten sind keine Flaechengrafik.
                            # Gemessen an der Revisiekarte: q78 326 KB, q82 373 KB,
                            # q88 465 KB. Ab q82 sind die Strassennamen lesbar.
WOERTER = ('hafen', 'wijnhaven', 'basisplan', 'kade', 'maas', 'wederopbouw',
           'schwarzplan', 'kubus', 'markthal', 'boompjes', 'leuvehaven',
           'coolsingel', 'blaak', 'oude', 'nieuwe', 'brug')


def passwort_holen(quelle):
    """Passwort aus der Datei daneben, sonst eines erzeugen und ablegen."""
    p = os.path.join(quelle, 'passwort.txt')
    if os.path.exists(p):
        wort = io.open(p, encoding='utf-8').read().strip()
        if wort:
            return wort, False
    # Vier verschiedene Woerter, nicht viermal gewuerfelt: "basisplan-kubus-
    # basisplan-hafen" sieht nach Fehler aus und ist ausserdem schwaecher.
    rest = list(WOERTER)
    gewaehlt = []
    for _ in range(4):
        gewaehlt.append(rest.pop(secrets.randbelow(len(rest))))
    wort = '-'.join(gewaehlt)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(wort + '\n')
    return wort, True


def tabelle_laden(quelle):
    """quellen.py aus dem Quellordner laden, ohne sie zu importieren."""
    p = os.path.join(quelle, 'quellen.py')
    if not os.path.exists(p):
        sys.exit('FEHLER: %s fehlt' % p)
    raum = {}
    exec(compile(io.open(p, encoding='utf-8').read(), p, 'exec'), raum)
    return raum['KAPITEL'], raum['STUECKE']


def bilder_aus(pfad, durchsichtig=False):
    """Eine Vorlage in eine oder mehrere WebP-Abbildungen verwandeln.

    PDF-Seiten werden einzeln gerendert, damit auch ein mehrseitiges
    Planwerk als Folge von Abbildungen erscheint und der vorhandene
    Bildaufbau der Seite unveraendert bleibt.

    Eine Kartenschicht wird durchsichtig gehalten und verlustfrei
    gespeichert: Sie besteht aus einer einzigen flachen Farbe auf Nichts,
    da kostet verlustfrei fast gar nichts und verlustbehaftet erzeugte
    Zwischentoene wuerden als Schleier ueber der Karte liegen.
    """
    from PIL import Image
    if durchsichtig:
        im = Image.open(pfad).convert('RGBA')
        if max(im.size) > LANGE_KANTE:
            k = LANGE_KANTE / max(im.size)
            im = im.resize((round(im.width * k), round(im.height * k)),
                           Image.LANCZOS)
        puffer = io.BytesIO()
        im.save(puffer, 'WEBP', lossless=True, quality=100, method=6)
        return [(puffer.getvalue(), im.width, im.height)]
    raus = []
    if pfad.lower().endswith('.pdf'):
        import pymupdf as fitz
        d = fitz.open(pfad)
        for seite in d:
            k = min(3.0, LANGE_KANTE / max(seite.rect.width, seite.rect.height))
            pm = seite.get_pixmap(matrix=fitz.Matrix(k, k))
            im = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
            raus.append(im)
    else:
        im = Image.open(pfad)
        im = im.convert('RGB') if im.mode not in ('RGB', 'L') else im
        raus.append(im)

    fertig = []
    for im in raus:
        if max(im.size) > LANGE_KANTE:
            k = LANGE_KANTE / max(im.size)
            im = im.resize((round(im.width * k), round(im.height * k)),
                           Image.LANCZOS)
        puffer = io.BytesIO()
        im.save(puffer, 'WEBP', quality=GUETE, method=6)
        fertig.append((puffer.getvalue(), im.width, im.height))
    return fertig


def name_fuer(k, datei, nr):
    """Ein Name, der nichts verraet und bei jedem Lauf derselbe ist."""
    roh = hmac.new(k, ('%s#%d' % (datei, nr)).encode('utf-8'),
                   hashlib.sha256).digest()
    return roh[:8].hex() + '.bin'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quelle', default=VORGABE_QUELLE)
    a = ap.parse_args()
    quelle = os.path.abspath(a.quelle)
    if not os.path.isdir(quelle):
        sys.exit('FEHLER: Quellordner fehlt: %s' % quelle)

    wort, neu = passwort_holen(quelle)
    kapitel, stuecke = tabelle_laden(quelle)
    kopf, k = krypto.schluesseldatei(wort)

    os.makedirs(ZIEL, exist_ok=True)
    for f in os.listdir(ZIEL):
        if f.endswith('.bin') or f == 'schluessel.json':
            os.remove(os.path.join(ZIEL, f))

    verzeichnis = {'fassung': 1, 'kapitel': kapitel, 'bilder': []}
    gesamt = 0
    for s in stuecke:
        p = os.path.join(quelle, s['datei'])
        if not os.path.exists(p):
            sys.exit('FEHLER: Vorlage fehlt: %s' % p)
        ebene = s.get('ziel') == 'ebene'
        seiten = bilder_aus(p, durchsichtig=ebene)
        for nr, (daten, w, h) in enumerate(seiten):
            datei = name_fuer(k, s['datei'], nr)
            paket = krypto.zu(k, daten)
            open(os.path.join(ZIEL, datei), 'wb').write(paket)
            gesamt += len(paket)
            eintrag = {'datei': datei, 'w': w, 'h': h,
                       'ziel': s.get('ziel', 'plaene'),
                       'credit': s.get('credit', ''),
                       'creditUrl': s.get('creditUrl', '')}
            if ebene:
                eintrag['lage'] = s['lage']
            for sprache in ('de', 'nl', 'en'):
                t = dict(s.get(sprache, {}))
                if len(seiten) > 1:
                    zusatz = {'de': ' (Blatt %d von %d)', 'nl': ' (blad %d van %d)',
                              'en': ' (sheet %d of %d)'}[sprache]
                    t['cap'] = (t.get('cap', '')
                                + zusatz % (nr + 1, len(seiten)))
                eintrag[sprache] = t
            verzeichnis['bilder'].append(eintrag)
            print('  %-34s %4d x %4d  %6.0f KB'
                  % (s['datei'] + ('' if len(seiten) == 1 else ' #%d' % (nr + 1)),
                     w, h, len(paket) / 1024))

    inhalt = krypto.zu(k, json.dumps(verzeichnis, ensure_ascii=False)
                       .encode('utf-8'))
    open(os.path.join(ZIEL, 'inhalt.bin'), 'wb').write(inhalt)
    io.open(os.path.join(ZIEL, 'schluessel.json'), 'w', encoding='utf-8',
            newline='\n').write(json.dumps(kopf, indent=2, ensure_ascii=False))

    print('\n%d Abbildungen, %.1f MB Geheimtext, Verzeichnis %d Byte'
          % (len(verzeichnis['bilder']), gesamt / 1e6, len(inhalt)))
    if neu:
        print('Passwort erzeugt und abgelegt in %s'
              % os.path.join(quelle, 'passwort.txt'))
    print('\nDer Link fuer den Kurs:\n  https://wijnhaven.com/#seminar=%s\n' % wort)


if __name__ == '__main__':
    main()
