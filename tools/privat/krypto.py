# -*- coding: utf-8 -*-
"""Das Schloss. Dieselben Bausteine, die der Browser mitbringt.

Verschluesselt wird mit AES-256-GCM, der Schluessel kommt aus dem Passwort
ueber PBKDF2-HMAC-SHA256. Beides kann WebCrypto von Haus aus, es muss also
nichts nachgeladen werden und die Gegenseite rechnet mit genau denselben
Verfahren.

Dateiform, bewusst schlicht: zwoelf Byte Zufall voran, dann der Geheimtext
mit angehaengtem Pruefwert. GCM erkennt jede Veraenderung und jedes falsche
Passwort von selbst; ein eigener Pruefmechanismus waere nur eine zweite
Stelle, an der man es falsch machen kann.

310.000 Runden sind die Empfehlung des OWASP fuer PBKDF2-SHA256. Auf einem
Telefon kostet das knapp eine Sekunde, einmalig beim Aufschliessen.
"""
import base64
import json
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

RUNDEN = 310000
PROBE_TEXT = b'wijnhaven'          # Klartext des Pruefblocks, absichtlich nichtssagend


def schluessel(passwort, salz):
    """Aus Passwort und Salz die 32 Byte fuer AES-256."""
    k = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salz,
                   iterations=RUNDEN)
    return k.derive(passwort.encode('utf-8'))


def zu(k, klartext):
    """Verschluesseln: IV voran, dann Geheimtext samt Pruefwert."""
    iv = os.urandom(12)
    return iv + AESGCM(k).encrypt(iv, klartext, None)


def auf(k, blob):
    """Entschluesseln. Wirft, wenn das Passwort nicht stimmt."""
    return AESGCM(k).decrypt(blob[:12], blob[12:], None)


def b64(b):
    return base64.b64encode(b).decode('ascii')


def schluesseldatei(passwort, salz=None):
    """Was oeffentlich liegen darf: Salz, Rundenzahl, ein Pruefblock.

    Der Pruefblock verraet nichts ueber den Inhalt, erlaubt aber die
    Meldung "Passwort stimmt nicht", bevor irgendeine grosse Datei
    geladen wird.
    """
    salz = salz or os.urandom(16)
    k = schluessel(passwort, salz)
    return {
        'verfahren': 'PBKDF2-SHA256 + AES-256-GCM',
        'salz': b64(salz),
        'runden': RUNDEN,
        'probe': b64(zu(k, PROBE_TEXT)),
    }, k


if __name__ == '__main__':
    import sys
    pw = sys.argv[1] if len(sys.argv) > 1 else 'probe'
    kopf, k = schluesseldatei(pw)
    print(json.dumps(kopf, indent=2, ensure_ascii=False))
