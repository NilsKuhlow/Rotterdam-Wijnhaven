# -*- coding: utf-8 -*-
"""Den Seminarbereich in die Seite setzen.

Die Website ist oeffentlich, das Material dahinter nicht. Entscheidend
ist darum, was hier NICHT steht: kein Titel, keine Bildunterschrift,
kein Urhebername des geschuetzten Materials. Alles das liegt
verschluesselt in privat/inhalt.bin. Stuende es hier, verriete das
Schloss, was dahinter liegt, und waere die halbe Arbeit umsonst.

Aufgeschlossen wird mit WebCrypto: PBKDF2 ueber das Passwort, dann
AES-256-GCM. Der abgeleitete Schluessel bleibt im Browser, das Passwort
selbst wird nirgends abgelegt. Entschluesselte Bilder werden zu
Blob-URLs und gehen durch denselben Bildaufbau wie alles andere.

Das Passwort steht hinter der Raute im Link. Was dort steht, schickt
der Browser nie an einen Server und auch nicht im Referer mit; es taucht
also in keinem Protokoll auf. Direkt nach dem Aufschliessen wird die
Adresszeile gekuerzt, sonst stuende es im Verlauf und auf jedem
Bildschirmfoto.
"""
import io
import json
import os
import sys

REPO = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
        r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
        r"\Rotterdam-Wijnhaven")
P = os.path.join(REPO, 'index.html')

# ── 1. CSS ──────────────────────────────────────────────────────────────
CSS_ANKER = "#map-svg-wrap { touch-action:pan-y; user-select:none; -webkit-user-select:none; }"
CSS_NEU = CSS_ANKER + """

/* Das Tor zum Seminarbereich. Liegt ueber allem, weil es vom Link
   geoeffnet wird und nicht davon abhaengt, wie weit geblaettert ist.
   Form wie der Rest: weiss, Haarlinie, keine Rundung, kein Schatten. */
#seminar-tor {
  position:fixed; inset:0; z-index:210;
  display:flex; align-items:center; justify-content:center;
  padding:1.5rem;
  background:rgba(10,10,10,.55);
  -webkit-tap-highlight-color:transparent;
}
#seminar-tor[hidden] { display:none; }
#seminar-form {
  width:min(26rem, 100%); background:var(--paper-0);
  border:1px solid var(--ink-1); padding:1.6rem 1.5rem 1.4rem;
  display:flex; flex-direction:column; gap:.9rem;
}
.sem-marke {
  font-family:var(--font-mono); font-size:.55rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-3); margin:0;
}
.sem-wort {
  font-family:var(--font-sans); font-size:1.02rem; font-weight:600;
  line-height:1.25; color:var(--ink-1); margin:0;
}
#seminar-wort {
  font-family:var(--font-mono); font-size:.9rem; letter-spacing:.04em;
  padding:.6rem .7rem; border:1px solid var(--ink-1); border-radius:0;
  background:var(--paper-0); color:var(--ink-1); width:100%;
}
#seminar-wort:focus-visible { outline:2px solid var(--accent); outline-offset:-3px; }
#seminar-fehler {
  font-family:var(--font-mono); font-size:.58rem; letter-spacing:.06em;
  color:var(--here); margin:0; line-height:1.5;
}
#seminar-fehler[hidden] { display:none; }
/* Der Feldname steht nur fuer Hilfsmittel da; sichtbar traegt die Zeile
   darueber die Frage. Nicht display:none, das naehme ihn auch der
   Sprachausgabe. */
.sem-feldname {
  position:absolute; width:1px; height:1px; margin:-1px; padding:0;
  overflow:hidden; clip:rect(0 0 0 0); clip-path:inset(50%); white-space:nowrap;
}
.sem-knoepfe { display:flex; gap:.5rem; flex-wrap:wrap; }
.sem-knopf {
  font-family:var(--font-mono); font-size:.56rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; border-radius:0; padding:.5rem .9rem; cursor:pointer;
  border:1px solid var(--ink-1); background:var(--paper-0); color:var(--ink-1);
  -webkit-tap-highlight-color:transparent; touch-action:manipulation;
}
.sem-knopf[type="submit"] { background:var(--accent); font-weight:600; }
.sem-knopf:hover, .sem-knopf:focus-visible { background:var(--accent); outline:none; }
.sem-knopf[disabled] { opacity:.4; cursor:default; }
/* Der Knopf, der den Bereich wieder zusperrt. Steht im Kapitel selbst,
   weil er dort hingehoert und nicht in die Kartenleiste. */
.sem-sperren {
  font-family:var(--font-mono); font-size:.55rem; letter-spacing:var(--tr-label);
  text-transform:uppercase; color:var(--ink-1); background:none; cursor:pointer;
  border:none; border-bottom:1px solid var(--ink-1); padding:0 0 .15rem;
}
.sem-sperren:hover, .sem-sperren:focus-visible { background:var(--accent); outline:none; }"""

# ── 2. Dritter Knopf in der Kartenleiste ───────────────────────────────
KNOPF_ANKER = """            onclick="openBasisplan()">Basisplan 1946</button>
  </div>"""
KNOPF_NEU = """            onclick="openBasisplan()">Basisplan 1946</button>
    <!-- Dritter Knopf, nur im aufgeschlossenen Zustand. Seine Beschriftung
         steht absichtlich nicht hier, sondern im verschluesselten
         Verzeichnis: Sonst verriete die Seite, was hinter dem Schloss liegt. -->
    <button class="eb-schalter eb-kapitel" type="button" id="eb-plaene"
            hidden onclick="openPlaene()"></button>
  </div>"""

# ── 3. Das Tor als Markup, hinter den Zoomstapel ───────────────────────
TOR_ANKER = """            onclick="kartenGanz()">GANZ</button>
  </div>"""
TOR_NEU = """            onclick="kartenGanz()">GANZ</button>
  </div>
  <!-- Tor zum Seminarbereich. Erscheint nur ueber #seminar, sonst nie. -->
  <div id="seminar-tor" hidden>
    <form id="seminar-form" onsubmit="return seminarAbsenden(event)">
      <p class="sem-marke" data-i18n="sem_marke">Seminarbereich</p>
      <p class="sem-wort" data-i18n="sem_frage">Passwort eingeben</p>
      <label class="sem-feldname" for="seminar-wort" data-i18n="sem_feld">Passwort</label>
      <input type="password" id="seminar-wort" autocomplete="off"
             autocapitalize="off" autocorrect="off" spellcheck="false">
      <p id="seminar-fehler" role="alert" hidden></p>
      <div class="sem-knoepfe">
        <button type="submit" class="sem-knopf" id="seminar-los"
                data-i18n="sem_auf">Aufschließen</button>
        <button type="button" class="sem-knopf" onclick="seminarTorZu()"
                data-i18n="sem_ab">Abbrechen</button>
      </div>
    </form>
  </div>"""

# ── 4. Das Schloss ──────────────────────────────────────────────────────
JS_ANKER = "function openHistorie(){ _historieFuellen(); openModal(-99, HISTORIE); }"

JS_NEU = JS_ANKER + """

/* ═══════════════════════════════════════════════════════════════
   SEMINARBEREICH

   Die Seite ist oeffentlich, ein Teil des Planmaterials ist es nicht.
   Ein Passwort in JavaScript haette daran nichts geaendert: Die Dateien
   stuenden weiter unter oeffentlichen Adressen. Also wird nicht
   abgefragt, sondern entschluesselt. Auf dem Server liegt nur
   Geheimtext; ohne Passwort ist das kein Bild, sondern Rauschen.

   PBKDF2 ueber das Passwort, daraus AES-256-GCM, beides aus WebCrypto,
   nichts nachgeladen. Der abgeleitete Schluessel bleibt im Browser,
   damit nicht bei jedem Aufruf 310.000 Runden neu gerechnet werden; das
   Passwort selbst wird nirgends abgelegt.

   Was hier bewusst fehlt: jeder Titel, jede Bildunterschrift, jeder
   Urhebername des geschuetzten Materials. Das steht im verschluesselten
   Verzeichnis. Stuende es hier, verriete das Schloss, was es verschliesst.
   ═══════════════════════════════════════════════════════════════ */
var SEMINAR = { auf:false, schluessel:null, inhalt:null, blobs:[] };
var SEMINAR_LAGER = 'wij-seminar-v1';

function _semB64(s){
  var roh = atob(s), a = new Uint8Array(roh.length);
  for (var i = 0; i < roh.length; i++) a[i] = roh.charCodeAt(i);
  return a;
}
function _semB64aus(a){
  var s = '';
  for (var i = 0; i < a.length; i++) s += String.fromCharCode(a[i]);
  return btoa(s);
}

/* Zwoelf Byte Vorlauf, dann Geheimtext samt Pruefwert. Stimmt das
   Passwort nicht, wirft decrypt; es gibt also keinen Zustand, in dem
   halb entschluesselter Unsinn durchrutscht. */
function _semAuf(k, puffer){
  var b = new Uint8Array(puffer);
  return crypto.subtle.decrypt({ name:'AES-GCM', iv:b.slice(0, 12) }, k, b.slice(12))
    .then(function(r){ return new Uint8Array(r); });
}

function _semKopf(){
  return fetch('privat/schluessel.json', { cache:'no-cache' })
    .then(function(r){ if (!r.ok) throw new Error('weg'); return r.json(); });
}

function _semSchluessel(passwort, kopf){
  return crypto.subtle.importKey('raw', new TextEncoder().encode(passwort),
                                 'PBKDF2', false, ['deriveKey'])
    .then(function(roh){
      return crypto.subtle.deriveKey(
        { name:'PBKDF2', salt:_semB64(kopf.salz), iterations:kopf.runden, hash:'SHA-256' },
        roh, { name:'AES-GCM', length:256 }, true, ['decrypt']);
    });
}

/* Das Verzeichnis holen und alle Abbildungen entschluesseln. Sie werden
   zu Blob-URLs und gehen danach durch denselben Bildaufbau wie jede
   andere Abbildung der Seite. */
function _semLaden(k){
  return fetch('privat/inhalt.bin').then(function(r){
    if (!r.ok) throw new Error('weg');
    return r.arrayBuffer();
  }).then(function(b){
    return _semAuf(k, b);
  }).then(function(klar){
    var v = JSON.parse(new TextDecoder().decode(klar));
    return Promise.all((v.bilder || []).map(function(bi){
      return fetch('privat/' + bi.datei)
        .then(function(r){ if (!r.ok) throw new Error('weg'); return r.arrayBuffer(); })
        .then(function(p){ return _semAuf(k, p); })
        .then(function(d){
          var u = URL.createObjectURL(new Blob([d], { type:'image/webp' }));
          SEMINAR.blobs.push(u);
          bi.url = u;
          return bi;
        });
    })).then(function(bilder){
      v.bilder = bilder;
      SEMINAR.auf = true; SEMINAR.schluessel = k; SEMINAR.inhalt = v;
      _semKnopf();
      return v;
    });
  });
}

/* Die Abbildungen einer Stelle, in der Form, die _figureHtml erwartet. */
function _semFiguren(ziel){
  if (!SEMINAR.auf || !SEMINAR.inhalt) return [];
  var lang = currentLang;
  return (SEMINAR.inhalt.bilder || []).filter(function(b){
    return b.ziel === ziel;
  }).map(function(b){
    var t = b[lang] || b.de || {};
    return { src:b.url, w:b.w, h:b.h, alt:t.alt || '', cap:t.cap || '',
             credit:b.credit || '', creditUrl:b.creditUrl || '' };
  });
}

function _semKapitelText(){
  var kap = (SEMINAR.inhalt || {}).kapitel || {};
  return kap[currentLang] || kap.de || { name:'', sub:'', paras:[] };
}

function _semKnopf(){
  var b = document.getElementById('eb-plaene');
  if (!b) return;
  if (SEMINAR.auf){
    b.textContent = _semKapitelText().name || '';
    b.hidden = false;
  } else {
    b.textContent = '';
    b.hidden = true;
  }
}

/* ── Das Kapitel mit den Planunterlagen ── */
var PLAENE = { slug:'plaene' };
function _plaeneFuellen(){
  var t = _semKapitelText();
  PLAENE.name = t.name;
  PLAENE.sub = t.sub;
  PLAENE.paras = (t.paras || []).concat([
    '<button type="button" class="sem-sperren" onclick="seminarSperren()">'
    + uiT('sem_sperren') + '</button>'
  ]);
  PLAENE.slides = [];
  PLAENE.figures = _semFiguren('plaene');
  PLAENE.facts = [];
  PLAENE.sources = [];
}
function openPlaene(){
  if (!SEMINAR.auf) return;
  _plaeneFuellen();
  openModal(-99, PLAENE);
}

/* ── Tor auf, Tor zu ── */
function seminarTor(passwort){
  var tor = document.getElementById('seminar-tor');
  if (!tor) return;
  if (passwort){
    _semOeffnen(passwort);
    return;
  }
  tor.hidden = false;
  var feld = document.getElementById('seminar-wort');
  if (feld){ feld.value = ''; setTimeout(function(){ feld.focus(); }, 60); }
}

function seminarTorZu(){
  var tor = document.getElementById('seminar-tor');
  if (tor) tor.hidden = true;
  var f = document.getElementById('seminar-fehler');
  if (f) f.hidden = true;
  _semHashKuerzen(true);
}

function seminarAbsenden(e){
  e.preventDefault();
  var feld = document.getElementById('seminar-wort');
  _semOeffnen(feld ? feld.value : '');
  return false;
}

function _semMeldung(text){
  var f = document.getElementById('seminar-fehler');
  if (!f) return;
  f.textContent = text || '';
  f.hidden = !text;
}

function _semOeffnen(passwort){
  var los = document.getElementById('seminar-los');
  if (los) los.disabled = true;
  _semMeldung(uiT('sem_laedt'));
  var kopf;
  return _semKopf().then(function(kp){
    kopf = kp;
    return _semSchluessel(passwort, kopf);
  }).then(function(k){
    /* Erst den kleinen Pruefblock, dann erst grosse Dateien laden. */
    return _semAuf(k, _semB64(kopf.probe).buffer).then(function(){ return k; });
  }).then(function(k){
    return crypto.subtle.exportKey('raw', k).then(function(roh){
      try { localStorage.setItem(SEMINAR_LAGER, _semB64aus(new Uint8Array(roh))); }
      catch (_){ /* privates Fenster: dann eben nur fuer diese Sitzung */ }
      return _semLaden(k);
    });
  }).then(function(){
    _semMeldung('');
    var tor = document.getElementById('seminar-tor');
    if (tor) tor.hidden = true;
    _semHashKuerzen(false);
    if (los) los.disabled = false;
    showToast(uiT('sem_offen'), 3200);
  }).catch(function(err){
    if (los) los.disabled = false;
    var tor = document.getElementById('seminar-tor');
    if (tor) tor.hidden = false;
    _semMeldung(uiT(String(err && err.message) === 'weg' ? 'sem_weg' : 'sem_falsch'));
    var feld = document.getElementById('seminar-wort');
    if (feld){ feld.value = ''; feld.focus(); }
  });
}

/* Das Passwort darf nicht in der Adresszeile stehenbleiben: Es landete
   sonst im Verlauf, in der Zurueck-Liste und auf jedem Bildschirmfoto.
   replaceState statt pushState, damit der Zurueck-Knopf nicht wieder
   darauf zeigt. */
function _semHashKuerzen(ganz){
  try {
    var ziel = location.pathname + location.search + (ganz ? '' : '#seminar');
    history.replaceState(null, '', ziel);
  } catch (_){ }
}

function seminarSperren(){
  try { localStorage.removeItem(SEMINAR_LAGER); } catch (_){ }
  SEMINAR.blobs.forEach(function(u){ try { URL.revokeObjectURL(u); } catch (_){ } });
  SEMINAR = { auf:false, schluessel:null, inhalt:null, blobs:[] };
  _semKnopf();
  if (typeof closeModal === 'function') closeModal();
  showToast(uiT('sem_zu'), 2600);
}

/* Beim Laden: War schon einmal aufgeschlossen, dann still wieder
   aufschliessen. Der Schluessel liegt im Browser, das Passwort nicht. */
function _semWiederaufnehmen(){
  var roh;
  try { roh = localStorage.getItem(SEMINAR_LAGER); } catch (_){ return; }
  if (!roh) return;
  crypto.subtle.importKey('raw', _semB64(roh), { name:'AES-GCM' }, true, ['decrypt'])
    .then(function(k){ return _semLaden(k); })
    .catch(function(){ try { localStorage.removeItem(SEMINAR_LAGER); } catch (_){ } });
}
window.addEventListener('load', function(){
  (window.requestIdleCallback || function(f){ setTimeout(f, 600); })(_semWiederaufnehmen);
});"""

# ── 5. Die Abbildungen in die beiden vorhandenen Kapitel ───────────────
HIST_ALT = """  HISTORIE.figures = [{ src: "img/plan-1913.webp", w: 1233, h: 1403,
                        alt: t.bildunter, cap: t.bildunter }];"""
HIST_NEU = """  HISTORIE.figures = [{ src: "img/plan-1913.webp", w: 1233, h: 1403,
                        alt: t.bildunter, cap: t.bildunter }]
                      .concat(_semFiguren('historie'));"""

BP_ALT = "  BASISPLAN.figures = [];"
BP_NEU = """  /* Leer, solange zugesperrt. Was aus dem Seminarbereich hierher
     gehoert, kommt erst dazu, wenn der Schluessel da ist. */
  BASISPLAN.figures = _semFiguren('basisplan');"""

# ── 6. Knopfbeschriftung bei Sprachwechsel ─────────────────────────────
TEXTE_ALT = """  var b = document.getElementById('eb-kapitel');
  if (b) b.textContent = KAPITEL_KNOPF.bp[currentLang] || KAPITEL_KNOPF.bp.de;"""
TEXTE_NEU = """  var b = document.getElementById('eb-kapitel');
  if (b) b.textContent = KAPITEL_KNOPF.bp[currentLang] || KAPITEL_KNOPF.bp.de;
  if (typeof _semKnopf === 'function') _semKnopf();"""

# ── 7. Hash-Routing ────────────────────────────────────────────────────
HASH_ALT = """  function openFromHash(){
    var h = (location.hash || '').replace(/^#/, '').toLowerCase();
    if (!h) return false;
    var idx = -1;"""
HASH_NEU = """  function openFromHash(){
    var h = (location.hash || '').replace(/^#/, '').toLowerCase();
    if (!h) return false;
    /* Der Seminarbereich. Das Passwort steht hinter dem Gleichheitszeichen
       und wird am ungebeugten Hash gelesen, nicht am kleingeschriebenen:
       ein Passwort darf Grossbuchstaben haben. */
    var roh = (location.hash || '').replace(/^#/, '');
    if (/^seminar(=|$)/i.test(roh)){
      var g = roh.indexOf('=');
      seminarTor(g > 0 ? decodeURIComponent(roh.slice(g + 1)) : '');
      return true;
    }
    var idx = -1;"""

HASHCHANGE_ALT = """  window.addEventListener('hashchange', function(){
    var h = (location.hash || '').replace(/^#/, '').toLowerCase();
    if (h === 'basisplan' || h === 'historie' || (typeof BYSLUG!=='undefined' && BYSLUG[h])) openFromHash();
    else if (document.getElementById('modal').classList.contains('open')) closeModal();  /* Zurueck-Taste schliesst */
  });"""
HASHCHANGE_NEU = """  window.addEventListener('hashchange', function(){
    var h = (location.hash || '').replace(/^#/, '').toLowerCase();
    /* Die sieben Stationen fehlten hier: Ein Sprung von #markthal auf
       #witte-huis schloss das Fenster, statt zu wechseln. SLUGS kennt sie. */
    if (/^seminar(=|$)/.test(h) || h === 'basisplan' || h === 'historie'
        || SLUGS[h] !== undefined
        || (typeof BYSLUG!=='undefined' && BYSLUG[h])) openFromHash();
    else if (document.getElementById('modal').classList.contains('open')) closeModal();  /* Zurueck-Taste schliesst */
  });"""

# ── 8. Oberflaechentexte ───────────────────────────────────────────────
UI_NEU = [
    {"key": "sem_marke", "de": "Seminarbereich", "nl": "Seminariegedeelte",
     "en": "Seminar area"},
    {"key": "sem_frage", "de": "Passwort eingeben", "nl": "Wachtwoord invoeren",
     "en": "Enter the password"},
    {"key": "sem_feld", "de": "Passwort", "nl": "Wachtwoord", "en": "Password"},
    {"key": "sem_auf", "de": "Aufschließen", "nl": "Openen", "en": "Unlock"},
    {"key": "sem_ab", "de": "Abbrechen", "nl": "Annuleren", "en": "Cancel"},
    {"key": "sem_laedt", "de": "Wird entschlüsselt …", "nl": "Wordt ontsleuteld …",
     "en": "Decrypting …"},
    {"key": "sem_falsch", "de": "Das Passwort stimmt nicht.",
     "nl": "Het wachtwoord klopt niet.", "en": "That password is not right."},
    {"key": "sem_weg", "de": "Der Bereich ist gerade nicht erreichbar.",
     "nl": "Het gedeelte is nu niet bereikbaar.",
     "en": "The area cannot be reached right now."},
    {"key": "sem_offen", "de": "Seminarbereich offen",
     "nl": "Seminariegedeelte open", "en": "Seminar area unlocked"},
    {"key": "sem_zu", "de": "Seminarbereich gesperrt",
     "nl": "Seminariegedeelte gesloten", "en": "Seminar area locked"},
    {"key": "sem_sperren", "de": "Bereich wieder sperren",
     "nl": "Gedeelte weer sluiten", "en": "Lock the area again"},
]


def main():
    s = io.open(P, encoding='utf-8').read()

    def tausch(alt, neu, was):
        nonlocal s
        if s.count(alt) != 1:
            sys.exit('FEHLER: %d Treffer: %r' % (s.count(alt), alt[:70]))
        s = s.replace(alt, neu)
        print('OK  ' + was)

    tausch(CSS_ANKER, CSS_NEU, 'CSS fuer Tor und Sperrknopf')
    tausch(KNOPF_ANKER, KNOPF_NEU, 'dritter Kapitelknopf')
    tausch(TOR_ANKER, TOR_NEU, 'das Tor')
    tausch(JS_ANKER, JS_NEU, 'das Schloss')
    tausch(HIST_ALT, HIST_NEU, 'Abbildungen im Historie-Kapitel')
    tausch(BP_ALT, BP_NEU, 'Abbildungen im Basisplan-Kapitel')
    tausch(TEXTE_ALT, TEXTE_NEU, 'Knopfbeschriftung bei Sprachwechsel')
    tausch(HASH_ALT, HASH_NEU, 'Anker #seminar')
    tausch(HASHCHANGE_ALT, HASHCHANGE_NEU, 'hashchange, dabei die Stationen gerichtet')

    marke = '"ui":['
    i = s.find(marke)
    if i < 0:
        sys.exit('FEHLER: I18N.ui nicht gefunden')
    zusatz = ''.join(json.dumps(u, ensure_ascii=False) + ',' for u in UI_NEU)
    s = s[:i + len(marke)] + zusatz + s[i + len(marke):]
    print('OK  %d Oberflaechentexte' % len(UI_NEU))

    io.open(P, 'w', encoding='utf-8', newline='\r\n').write(s)
    print('\nindex.html geschrieben')


if __name__ == '__main__':
    main()
