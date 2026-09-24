# Wijnhaven Rotterdam

Interaktiver Stadtrundgang durch das **Wijnhaven-Quartier in Rotterdam**: sieben Bauten am Wasser,
vom Witte Huis (1898) bis CasaNova. Mobile-first Progressive Web App mit scroll-geführter Karte,
GPS-Tracker und einem Tagebuch-Layout (eigene Einträge, Stimmen vom Ort, interaktive 3D-Modelle).

Wahlpflichtmodul „Stadt + Raum“, Hochschule Wismar, WiSe 2026/27, Thema *Waterfront in Motion*.
Gruppe 4. Nils Kuhlow & Kai-Lars Ehrich.

## Stationen (Route, ca. 3 h)

1. Witte Huis · Willem Molenbroek, 1898
2. Kubuswoningen · Piet Blom, 1978–84
3. Markthal · MVRDV, 2014
4. Red Apple · KCAP / Jan des Bouvrie, 2009
5. Wijnhaven-Türme · Masterplan KCAP & Barcode Architecten
6. EY Netherlands · Bürohaus am Wijnhaven
7. CasaNova · Pavillon am Wasser

## Technik

- Single-File `index.html` (HTML + CSS + Vanilla-JS), keine Build-Pipeline
- 2D-Karte: inline SVG-Figure-Ground (OSM), **statisch und antippbar** wie eine normale Karte;
  GPS Smart-Track bewegt sie weiterhin
- 3D-Gesamtmodell (Button „3D" oben links): `<model-viewer>`-Drehteller, Draco-Mesh + WebP-Texturen
- PWA: `manifest.json` + `sw.js` (offline-fähig)
- Sprachen: NL (Start) / DE / EN, umschaltbar oben rechts
- Akkuschonend: Animationen + GPS pausieren im Hintergrund, ~30fps-Scroll-Cap, kein Idle-Rendering

## 2D-Karte: lesen und antippen

Die 2D-Karte ist eine **normale Karte**: Sie zeigt durchgehend die ganze Route, bewegt sich
nicht mit dem Scrollen, und man öffnet ein Bauwerk, indem man seinen Punkt antippt. Die
frühere Scroll-Strecke (sieben Bildschirme, die die Kamera von Ort zu Ort zogen) und die
Schublade darunter sind entfallen; der Schwerpunkt liegt auf dem 3D-Gesamtmodell.

Die sieben Punkte tragen **dieselben Farben wie die Marker im 3D-Modell**. Einzige Quelle
ist `STOP_COLORS` in `index.html`, zugeordnet über den Slug und nicht über die Nummer: Die
Nummer kommt aus der Route und kann sich ändern, die Identität des Bauwerks nicht. Auch die
3D-Marker und ihre Legende lesen die Nummer über `_pinNum()` aus der Route, damit beide
Karten nie auseinanderlaufen.

Der eigene Standort trägt dasselbe Signalrot (`--here`) wie der Marker im 3D-Modell:
roter Kern, weißer Ring, dunkle Haarlinie, damit er auf hellem Grund ebenso steht wie
auf schwarzem Baukörper. Er ist mit 16 px etwas größer als ein Stopp-Punkt (14 px),
denn es gibt nur einen davon. Der Genauigkeitskreis ist eine Haarlinie und keine
Fläche, sonst läge ein weicher Schleier über dem harten Schwarzplan.

Die Karte steht auch im **Smart-Track**. Sie zeigt durchgehend die ganze Route, der
Punkt wandert darin; gezoomt oder mitgeführt wird nicht. Beides nähme den Überblick,
den man beim Gehen braucht, und nötig ist es nicht: Der Punkt ist ohnehin im Bild.
Kommt man einem Bauwerk auf 50 m nahe, wird sein Punkt hervorgehoben und die
Info-Karte erscheint. Beim Beenden wird die Hervorhebung gelöscht.

Bewegt wird die Karte nur von Hand, mit Wischen und Pinch. Dann erscheint der Knopf
**Übersicht** (`resetMapView()`), der sie wieder in die Gesamtansicht legt. Ein Sprung
zum eigenen Standort, den der Knopf früher machte, ergibt keinen Sinn mehr, solange die
Karte steht.

### Die Grundkarte

Zugrunde liegt der eigene **Schwarzplan**, Stand September 2026. Er kam zuletzt als
**Rasterbild** (3094 × 4724 px, 300 dpi) und liegt deshalb als `img/schwarzplan.webp`
unter dem SVG, nicht mehr als Pfade darin. **Verlustfrei sind das 253 KB** — bei einer
Strichzeichnung aus vier flachen Farben komprimiert verlustfrei besser als
verlustbehaftet: dieselbe Datei mit q=90 wäre 1,4 MB, also fünfmal so groß.

**Georeferenziert ist er gemessen, nicht geschätzt.** Das Bild trägt keine Georeferenz.
Seine Wasserfläche wurde deshalb gegen die des alten OSM-Plans kreuzkorreliert, dessen
Projektion bekannt war, mit mittelwertfreier und örtlich normierter Korrelation auf
einer Kreisscheibe um die Wijnhaven. Das Maximum saß bei **0 Grad Drehung** und
**1:4989**, also glatt **1:5000**, mit einer Korrelation von **0,93**. Die Seite deckt
1307 × 1996 m.

Gegenprobe an den sieben Bauten: **fünf liegen im Gebäude**, die beiden anderen 4 m und
11 m daneben (Kubuswoningen, wo zwischen den Würfeln Lücken sind). Das ist feiner als
GPS vor Ort.

Eine SVG-Einheit bleibt **1,3048 m** wie in allen Fassungen davor. Nur so gelten
Punktgrößen, Strichstärken, Beschriftungen und der 50-m-Radius unverändert weiter;
geändert haben sich allein der Ursprung (`gpsToSvg`) und die Planmaße (`MAP_VW` 1002,
`MAP_VH` 1530).

**Was Raster statt Vektor kostet:** Bei stärkstem Zoom (`MIN_VB_W` 80 Einheiten, also
104 m Bildbreite) wird das Bild weich, weil es 2,37 px je Meter trägt. Im normalen
Zuschnitt der Karte ist es scharf. Außerdem lässt sich die Karte nicht mehr über CSS
umfärben; Wasser- und Bauwerksfarbe stecken im Bild. Kommt wieder ein Vektor-Export,
ist der Weg zurück offen: `tools/schwarzplan/schwarzplan.py` erzeugt daraus die drei
Pfade.

**Was die Rasterfassung dafür bringt:** Sie zeichnet Innenstrukturen, die der
Vektorplan als massive Flächen zeigte — die Markthal mit ihren Ständen, der Bahnhof
Blaak. Verglichen wurden beide Fassungen Ebene für Ebene: Baukörper decken sich zu
85 %, Wasser zu 90 %, der Rest ist Rasterversatz an den Kanten und der engere
Ausschnitt.

Die Werkzeuge liegen in `tools/schwarzplan/` samt Kontrollbildern.

Den Zuschnitt rechnet `_computeStaticVB()` aus den Wegpunkten. Wichtig: Das SVG nutzt
`preserveAspectRatio="slice"`, eine viewBox mit falschem Seitenverhältnis würde also
beschnitten und Stationen am Rand verschwinden. `_vbFit()` zieht die viewBox deshalb
immer auf das Seitenverhältnis des Kartenfensters und rechnet bei Drehung des Geräts neu.

Die beiden Pausen (APARTT., FLOATS) sind aus der Route entfernt; die Route zählt wieder
01 bis 07. Die generische Pausen-Unterstützung in `buildRoute()` bleibt bestehen, ein
`{type:'break',…}` in `ROUTES` genügt, um sie zurückzuholen.

Einzelne Häuser haben **kein** eigenes 3D-Modell mehr (Qualität nicht ausreichend). Der
Renderer dafür steht weiterhin bereit: ein `model:{src,poster}` an einem Eintrag genügt,
so wie `voices` auf die Interviews wartet.

## 3D-Gesamtmodell: eigenes Modell bauen

Die 3D-Ansicht zeigt die Gesamtkarte `models/wijnhaven.glb` (Konstante `TOUR_MODEL_URL`
in `index.html`) als Drehteller. Für antippbare Objekte gilt die **Namenskonvention**. Beim eigenen Modell
(Blender o.ä.) einfach die Objekte/Meshes so benennen:

- `building_<N>` → Antippen öffnet Eintrag N (0 = Witte Huis … 6 = CasaNova). Beispiel: `building_2` = Markthal.
- `person_<id>` → Antippen zeigt das Zitat/Interview aus `TOUR_PEOPLE[id]` (in `index.html`).
  Beispiel: `person_kai`. Neue Personen einfach in `TOUR_PEOPLE` mit `de/nl/en`-Eintrag ergänzen.
- `ground`, `scenery_*` → reine Kulisse, nicht antippbar.

Als `.glb` nach `/models/wijnhaven.glb` exportieren (Y nach oben, reale Maßstäbe sind ok)
und `TOUR_MODEL_URL` ggf. anpassen. Große Exporte vorher komprimieren:

```
gltf-transform optimize in.glb out.glb --compress draco --texture-compress webp --texture-size 1024 --simplify false
```

Draco statt Meshopt, weil `<model-viewer>` Meshopt hier nicht lädt. `--simplify false` ist wichtig:
sonst zerlegt die Vereinfachung die Photogrammetrie-Geometrie.

### Marker der sieben Bauten

In der 3D-Ansicht sitzt über jedem der sieben Bauten ein farbiger Marker mit der
Stopp-Nummer. Antippen öffnet den Eintrag, die Legende unten links benennt die
Farben und öffnet dieselben Einträge.

Die Marker sind **`<model-viewer>`-Hotspots**, also HTML-Buttons an einer
Modellkoordinate, und bewusst **keine Geometrie im glb**. Drei Gründe:

- `gltf-transform optimize` führt `flatten` und `join` aus. Das Modell besteht
  danach aus einem einzigen Mesh (`Mesh_0`, 415 Primitives). Benannte
  Marker-Objekte aus Blender wären nicht mehr auffindbar.
- HTML-Marker bleiben in jeder Zoomstufe scharf, sind echte Buttons (Tastatur,
  Screenreader) und übersetzbar.
- Farbe, Text und Reihenfolge ändert man in `TOUR_PINS` in `index.html`, ohne das
  199-MB-Modell neu zu exportieren und zu optimieren.

Farben nach **Okabe-Ito** (farbfehlsichtigkeitssicher); jeder Chip hat eine
near-black Kontur, damit auch die hellen Töne auf Weiß stehen. Gelb sitzt auf den
Kubuswoningen, die real gelb sind.

#### Woher die Koordinaten kommen

`data-position` ist eine Modellkoordinate in Metern. Der Blender-Umweg hat die
Georeferenz aus dem Google-3D-Tiles-Export entfernt, sie wurde deshalb
zurückgerechnet: aus dem Modell ein Höhenraster (DSM, 2 m) bilden, daraus per
Blockminimum die Gebäudehöhen ableiten, und diese Maske gegen die OSM-Grundrisse
der Website (`gpsToSvg`) kreuzkorrelieren. Das Maximum lag 11 Sigma über dem
Mittel, ohne Drehung und im Maßstab 1 Einheit = 1 m:

```
X = (lon - 4.486400) * 68671.61405
Z = (51.916868 - lat) * 110540
```

Y liegt 18 m über der aus dem Modell gemessenen Dachhöhe.

Gegenprobe über die gemessenen Höhen: Red Apple 127,8 m (real 124 m), CasaNova
115,0 m (rund 110 m), Witte Huis 46,9 m (rund 43 m), Markthal 44,7 m (rund 40 m).

Die Skripte liegen in `tools/marker-kalibrierung/` (`extract_dsm.py`,
`register.py`, `hotspots.py`) samt Kontrollbild. Sie sind nur nötig, wenn das
Modell **neu exportiert** wird und dabei der Ausschnitt wandert.

Hinweis: Die Koordinate der Kubuswoningen in `COORDS` (51.9199 / 4.4902) liegt
rund 45 m südwestlich des tatsächlichen Schwerpunkts; in OSM heißt der Komplex
**Blaakse Bos** und liegt bei 51.92029 / 4.49047. Der Marker nutzt den korrigierten
Wert, `COORDS` ist unverändert, weil davon Karte und GPS-Tracker abhängen. Vor Ort
prüfen und dann gemeinsam nachziehen.

### Eigener Standort im Modell

Läuft **Smart-Track**, während die 3D-Ansicht offen ist, zeigt ein roter Marker, wo
man steht. Er ist bewusst anders gebaut als die eckigen, nummerierten
Bauwerksmarker: rund statt eckig, rot statt Bauwerksfarbe, ohne Nummer.

Er besteht aus drei Teilen. Der **Fußring** sitzt auf dem Punkt, auf dem man steht;
aus ihm laufen zwei Ringe aus, damit man ihn im Gewimmel findet
(`prefers-reduced-motion` friert sie ein). Darauf steht senkrecht eine **Nadel**, und
auf der sitzt der **Kopf**, der die Fernwirkung trägt.

Der Ankerpunkt liegt auf Augenhöhe über dem Boden, also dort, wo man wirklich steht,
und `<model-viewer>` zentriert das Element darauf. Deshalb ist der Standring das
Element selbst. Nadel und Kopf sind in Pixeln versetzt, nicht in Metern: Ein Versatz
in Metern würde beim Kippen der Kamera perspektivisch mitwandern und am Ende neben
den Standort zeigen.

Der Marker steht in jeder Ansicht **aufrecht** und sieht aus jedem Blickwinkel gleich
aus. Eine frühere Fassung ließ den Fußring der Kameraneigung folgen, damit er in der
Bodenebene liegt; beim Kippen las sich das aber, als lege sich der ganze Marker mit um.
Geprüft an sechs Kamerawinkeln: Ring 39×39, Nadel 2×39 senkrecht, Kopf mittig darüber,
überall identisch.

Rot (`--here`) ist die einzige Farbe außerhalb der Palette. Sie ist dem Standort
vorbehalten, kein Bauwerk trägt sie, deshalb ist sie an dieser Stelle eindeutig.

Beim Herauszoomen bleibt der Marker größer als die Bauwerksmarker
(`scale(max(.85, var(--pin-k)))`): Es gibt nur einen davon, und er muss auch in der
Gesamtansicht auffindbar sein.

`gpsToModel()` nutzt dieselbe Registrierung wie die Bauwerksmarker, nur umgekehrt
gelesen. Gegenprobe: Die Koordinate der Markthal aus `STOP_COORDS` landet auf
`32.3 / -358.4` und trifft damit ihren Marker auf den Zehntelmeter.

Der Marker entsteht mit dem ersten Fix, wird beim Öffnen der 3D-Ansicht nachgezogen,
falls schon geortet wird, und verschwindet beim Beenden des Trackers.

Eine Fallgrube: `mv.updateHotspot()` bewegt den Punkt zwar in der Szene, schreibt
aber `data-position` nicht zurück. `_t3dMeUpdate()` setzt deshalb immer beides.

### Volldetail-Modell und App (geplant)

Der frühere Umschalter **Abstrakt / Realistisch** gehörte zum Three.js-Walkthrough und ist mit
dem Umbau auf den Drehteller entfallen; seine beiden Modelle (`map_v1.glb`,
`walkthrough_detailed.glb`) sind aus dem Repo entfernt.

Die Karte für die App-/Download-Wahl **Windows / Apple / Android** (`TOUR_APP_WINDOWS`,
`TOUR_APP_IOS`, `TOUR_APP_ANDROID` in `index.html`) liegt als Code bereit, ist aber derzeit
nicht verdrahtet. Vorgesehen: externe Links (Microsoft Store / App Store / Google Play) öffnen,
relative Dateien (`.exe`, `.msi`, `.apk` auf derselben Domain) laden direkt herunter, und die
Website erkennt das Betriebssystem und stellt den passenden Download nach vorne.

### Ego-Perspektive (Street View) + Vor-Ort-Sync

Oben gibt es einen Umschalter **Geführt / Frei**:
- **Geführt** (Standard, professionell): die Kamera gleitet zwischen festen Aussichtspunkten;
  mit **‹ / ›** (unten) Schritt vor/zurück, ziehen = am Punkt umsehen, antippen = öffnen. Die
  Punkte stehen in `TOUR_PATH` in `index.html` (je Punkt Standort + Blickziel, fürs echte Modell anpassen).
- **Frei**: First-Person-Walk, ziehen = umsehen, **Joystick** (unten links) bzw. **WASD/Pfeile**
  am Desktop = laufen, antippen = Gebäude/Person öffnen.

Der Schalter **Vor Ort** (unten rechts) synchronisiert die Kamera mit dem **echten Standort**:
`watchPosition` setzt die Position über `gpsToWorld(lat, lon)`, der Geräte-Kompass richtet die
Blickrichtung aus. So sieht man vor Ort dasselbe wie im Modell. Manuelle Steuerung ist im
Sync-Modus aus; aus Akkugründen läuft der Renderloop nur bei Eingabe/Bewegung.

**Kalibrieren** (wie `gpsToSvg` für den Schwarzplan, in `index.html`): `GPS_ORIGIN` (GPS-Punkt am
Modell-Ursprung), `GPS_KX`/`GPS_KZ` (Welt-Einheiten pro Grad Länge/Breite, an Modellmaßstab
anpassen, Norden = -z) und `GPS_HEADING` (Grad-Offset für die Blickrichtung). Die Vorgaben sind
Platzhalter und müssen am echten Modell vor Ort feinjustiert werden. iOS fragt beim ersten Mal
nach Erlaubnis für Bewegungssensoren; ohne Kompass folgt nur die Position, Umsehen bleibt manuell.

## Kein Verzeichnis mehr

Neben **3D** stand bis September 2026 ein Knopf **Orte**, der ein Blatt von unten
hereinschob: die sieben Stationen in der Reihenfolge des Gehens, darunter eine zweite
Liste mit 24 weiteren Häusern des Hafengebiets. Beides ist heraus.

Der Grund ist die Karte selbst. Sie zeigt dieselben sieben Stationen schon, mit
Nummer, Farbe, Namen und Lage, und man tippt sie dort an. Ein Verzeichnis daneben
war dieselbe Liste ein zweites Mal, nur ohne Ort.

Mit dem Knopf fielen das Blatt, sein CSS, `renderPlacesList()`, `openPlaces()`,
`closePlaces()`, `openExtraPlace()`, das Wischen zum Schließen, der Escape-Zweig,
`EXTRA_PLACES` samt Übersetzungspflege und zehn Beschriftungen in DE/NL/EN. Geblieben
ist `openBuilding()`: Daran hängen die Marker im 3D-Modell.

Die 24 Bauwerke außerhalb der Route stehen weiter in `NEWBUILDINGS`, mit
Übersetzungen und Bildern, und ein Link auf `#slug` öffnet sie nach wie vor. Von der
Oberfläche aus führt kein Weg mehr dorthin.

**3D** und **Smart-Track** erscheinen gemeinsam, sobald die Karte einsetzt. Die
Schwelle dafür ist `MAP_EIN` (70 % der Introhöhe) und gilt für beide: Vorher hing der
Smart-Track-Schalter an einer eigenen Marke dicht vor der Kartenbühne und kam spürbar
später als der Rest.

### Der Knopf zum Modell

Er war eine schwarze Pille von 56 × 26 px mit der Aufschrift „3D“, kleiner als der
Smart-Track-Schalter daneben, und damit das leiseste Element auf der Karte, obwohl er
das Beste öffnet, was die Seite hat. Jetzt misst er 135 × 37 px, heißt **3D-Modell**
(NL `3D-model`, EN `3D model`, über `data-i18n="tour3dBtn"`) und trägt als einziges
Bedienelement auf der Karte das Hausgelb.

Das ist keine Ausnahme von der Regel, sondern die Regel: Gelb markiert im ganzen
Dokument die eine Handlung — der Absenden-Knopf unter den Stimmen, die angesprungene
Stimme, die geöffnete Sprechblase. Auf der Karte ist das Modell diese Handlung.
Schwarze Schrift und schwarze Haarlinie halten ihn gezeichnet; er leuchtet nicht, er
liegt vorn. Platz ist da: Auch auf 360 px bleiben 96 px Lücke zum Smart-Track.

## Sprache

Die Seite startet auf **Deutsch** (`START_LANG` in `index.html`), wie das statische
HTML. `_startLang()` schaltet dann nichts um, die Seite steht sofort richtig da.
Niederländisch und Englisch wählt man über die Knöpfe oben rechts. Ein anderer Wert
in `START_LANG` genügt, um die Startsprache zu wechseln; stand sie auf `nl`, schaltete
`_startLang()` noch während des Ladeschirms um, damit kein Wechsel aufblitzt.

Umgeschaltet werden drei Dinge: die Texte über `data-i18n`, die drei Sprachblöcke
(Lese-Abschnitt und Datenschutz) über `data-lang-block`, und die Meldungen des
Trackers über `trkT()`.

**Offen bleibt:** NL und EN haben keine eigenen URLs. Google indexiert deshalb nur die
deutsche Fassung; niederländische Suchen finden den niederländischen Text nicht. Mit
Deutsch als Startsprache decken sich immerhin gerenderte Seite und indexierter Text,
was vorher nicht der Fall war. Sauber lösen ließe sich der Rest nur mit eigenen URLs
je Sprache plus `hreflang`.

## Stimmen und Kommentare

Fünf Gespräche aus dem Viertel stehen im Abschnitt **Stimmen** am Fuß der Seite und
als kleine Sprechblasen im 3D-Modell. Beides kommt aus einem einzigen Array `STIMMEN`
in `index.html`: Wer eine Stimme ergänzt, trägt sie dort ein, und Blase, Abschnitt und
Beschriftung entstehen daraus. Jede Stimme führt Text und Kontext in allen drei
Sprachen.

**Die Position der Blasen ist frei gewählt.** Nur zwei Gespräche nennen überhaupt einen
Ort: Sirano die Markthal, die Dreiergruppe den Blaak; deren Blasen stehen in der Nähe
des jeweiligen Baus. Die übrigen vier gelten dem Quartier als Ganzem und sind über das
Modell verteilt. Die Oberfläche behauptet deshalb nirgends, dort sei gesprochen worden,
und der Hinweis unter dem Abschnitt sagt es ausdrücklich.

Gestalterisch sind die Blasen bewusst leiser als alles andere im Modell: 18 × 13 px,
weiß, eine Haarlinie, 60 % Deckkraft, und ihr Maßstab ist bei 1 gedeckelt, während die
Bauwerksmarker bis 1,15 wachsen. Antippen öffnet das Zitat in einem Feld über dem
Modell; man kann weiterdrehen, während es steht. Die offene Blase färbt sich gelb.
`Alle Stimmen` schließt das Modell und springt auf den Anker der Stimme, die dann über
`:target` kurz hervorgehoben wird. Der Hash-Router lässt unbekannte Anker in Ruhe, das
ist in `openFromHash()` geprüft.

### Kommentarfeld

Unter den Stimmen kann man selbst einen Kommentar hinterlassen. Er geht über
**Web3Forms** als E-Mail an uns und erscheint **nicht** von selbst auf der Seite;
eingepflegt wird er von Hand in `STIMMEN`.

Kein Skript des Anbieters liegt auf der Seite. Es gibt genau einen `POST` an
`api.web3forms.com`, und zwar erst, nachdem jemand Absenden gedrückt hat. Der Service
Worker fasst das nicht an, er behandelt nur `GET`. Ein Köderfeld `botcheck` fängt
einfache Roboter ab.

Der Schlüssel steht in `index.html` im Feld `access_key`; Kommentare gehen an
**nils.kuhlow@gmail.com**. **Bei Web3Forms hängt die Zieladresse am Schlüssel, nicht am
Formular** — es gibt kein Feld `to`. Für eine andere Adresse braucht es also einen neuen
Schlüssel. Der Schlüssel ist öffentlich und gehört in den Quelltext. Antworten gehen an
den Besucher, weil Web3Forms `replyto` aus dem Feld `email` setzt.

**Zwei Stolperstellen, beide schon gelöst:**

`FormData` geht **direkt und ohne eigene Header** raus. Ein
`Content-Type: application/json` ist nicht CORS-sicher und löst eine OPTIONS-Vorabfrage
aus; die beantwortet die API von Web3Forms grundsätzlich mit `403 This method is not
allowed`, auch von beliebigen anderen Herkünften. Die Dokumentation sagt es ebenso:
*Don't add headers or content-type*.

Ein Test mit **headless Chrome** schlägt fehl, auch wenn alles richtig ist: Der
Bot-Schutz weist die Kennung `HeadlessChrome` ab, und die Fehlerantwort trägt dann
keinen CORS-Header. Wer den Versand prüft, muss die User-Agent-Kennung überschreiben
(`Network.setUserAgentOverride`). Steht so in `test_versand_live.mjs`.

Die Datenschutzerklärung hat dafür einen eigenen Abschnitt in allen drei Sprachen
(Anbieter, übertragene Daten, Rechtsgrundlage Einwilligung, Freiwilligkeit von Name und
E-Mail, keine automatische Veröffentlichung). Der frühere Satz „keine Formulare“ stimmte
damit nicht mehr und ist ersetzt.

## Kein Notizbuch

Die Eintragstexte trugen aus der Vorbereitung Sätze mit sich, die ankündigten, was vor
Ort noch zu prüfen sei: die Materialfrage beim Witte Huis, Höhe und Wohnungsschlüssel
beim Red Apple, der belebte oder unbelebte Straßenraum am Wijnhaveneiland. Auf der
Seite lasen sie sich wie ein fremdes Notizbuch. Sie sind heraus, nach einer festen
Linie:

* Ein Satz, der nur ankündigt, was vor Ort geprüft wird, fällt weg.
* Ein Satz, der eine Feststellung im Notizton trägt („Wir notieren die städtebauliche
  Pointe: …“), behält die Feststellung und verliert den Ton.
* Nichts Neues wird behauptet. Wo ein Absatz nur aus Vorhaben bestand — Markthal,
  dritter Absatz — bleibt allein der Satz, den die Verfasser selbst als Befund
  geschrieben hatten.

Jeder deutsche Satz steht zweimal im Dokument, in den Einträgen und im Sprachblock;
Niederländisch und Englisch je einmal. Wer hier etwas ändert, ändert es viermal.

## Offline

Ein Service Worker legt Seite, Bilder und Symbole beim ersten Besuch ab. Das 3D-Modell
(23,5 MB) wird bewusst **nicht** vorgeladen, sondern erst beim ersten Öffnen der
3D-Ansicht gecacht.

Wichtig: `www.gstatic.com` steht in `CACHEABLE_HOSTS`, denn von dort kommt der
Draco-Decoder (59 KB Wrapper + 286 KB WebAssembly). Ohne ihn läge zwar das Modell im
Cache, ließe sich offline aber nicht auspacken, die 3D-Ansicht blieb leer.

**Vor der Reise einmal über WLAN die 3D-Ansicht öffnen.** Erst dann liegen Modell und
Decoder im Cache. Geprüft mit gekappter Verbindung: Seite lädt, Modell lädt, alle
sieben Marker stehen.

## Datenschutz

Die Erklärung steht aufklappbar im Colophon, dreisprachig über `[data-lang-block]`,
das `setLang()` mitschaltet. Sie beschreibt, was die Seite technisch tut: Hosting bei
GitHub Pages, cookiefreie Zählung mit GoatCounter, Ortung ausschließlich auf dem Gerät,
Schriften von Google Fonts, 3D-Bausteine von unpkg und gstatic, keine Cookies, keine
Formulare.

Der Text ist eine sachliche Beschreibung, **keine juristische Prüfung**. Ob er für eure
Abgabe genügt, klärt ihr mit der Hochschule.

## SEO

Der Kern des Problems war nicht Technik, sondern Inhalt: Die Eintragstexte entstehen erst
beim Antippen eines Punktes, das gerenderte Dokument enthielt deshalb nur **77 Wörter**.
Der statische Abschnitt `#route-read` (Kurzfassung der sieben Bauten, keine Kopie der
Einträge) bringt das auf **439 gerenderte Wörter** mit sauberer Hierarchie H1 zu H2 zu
sieben H3 und sieben internen Links auf die Deep-Link-Anker.

Der Abschnitt liegt **dreisprachig** im Dokument und wird über `data-lang-block`
umgeschaltet, genau wie die Datenschutzerklärung. Im Quelltext stehen damit alle drei
Fassungen (1346 Wörter), gerendert ist immer nur die gewählte. Die drei Blöcke tragen
je ein eigenes `lang`; die frühere `id="rr-title"` musste weichen, weil drei
Überschriften nicht dieselbe id tragen können.

Weiter: `<title>` und Beschreibungen auf *Wijnhaven Rotterdam* und *Stadtführung*
ausgerichtet, strukturierte Daten als `TouristTrip` mit allen sieben Stationen samt
Koordinaten (JSON-LD im `<head>`), `lastmod` in der Sitemap. `robots.txt`, `sitemap.xml`,
Canonical und Open Graph waren bereits vorhanden.

**Realistisch einordnen:** Für *Wijnhaven* allein ist der Wettbewerb hart, der Begriff
gehört auch dem Universitätsgebäude Wijnhaven in Den Haag und der gleichnamigen Straße.
Erreichbar sind Suchen wie *Wijnhaven Rotterdam*, *Wijnhaven Architektur*, *Stadtführung
Wijnhaven* oder *Wijnhaveneiland*. Die Domain wijnhaven.com hilft bei Suchen, die die
Seite ohnehin meinen.

**Offen:** NL und EN werden clientseitig umgeschaltet, ohne eigene URLs. Google indexiert
deshalb nur die deutsche Fassung; niederländische Suchen finden den niederländischen Text
nicht. Das zu lösen hieße eigene URLs je Sprache plus `hreflang`.

**Nicht automatisierbar:** Die Sitemap muss in der Google Search Console eingereicht
werden, das ist der wirksamste einzelne Schritt und braucht euren Zugang.

## Besucherzahlen

**GoatCounter** ist eingebaut und aktiv: `GOATCOUNTER_CODE = 'nilsklw'` in `index.html`.
Auswertung unter <https://nilsklw.goatcounter.com>. Cookiefrei und quelloffen, deshalb
ohne Einwilligungsbanner üblich.

Drei Dinge sind bewusst geregelt:

- Auf `localhost` und `127.0.0.1` wird **nicht** gezählt, eigene Tests verfälschen die
  Zahlen also nicht.
- Bei gesetztem `doNotTrack` wird das Skript gar nicht erst geladen.
- Ist `GOATCOUNTER_CODE` leer, passiert nichts. Ein Fehlkonfigurieren kann nichts kaputt
  machen.

Zusätzlich meldet `countEntry()` aus `openModal()`, **welcher Eintrag** geöffnet wurde,
als Pfad `eintrag/<slug>`. Damit sieht man, welches Bauwerk gelesen wird. Übertragen wird
nur der Slug.

Grenze: Der Service Worker liefert die Seite offline aus dem Cache, der Zähl-Aufruf geht
aber ans Netz. Ohne Empfang vor Ort zählt nichts mit, die Zahlen der Exkursionswoche
liegen also unter der tatsächlichen Nutzung.

## Google Search Console

Zeigt, mit welchen Suchbegriffen die Seite gefunden wird, wie oft sie erscheint und auf
welcher Position.

Eingerichtet als **Domain-Property**, bestätigt über einen DNS-TXT-Eintrag beim
Domainanbieter (`google-site-verification=EdSquVP6…`). Diese Variante deckt alle
Subdomains und beide Protokolle ab. Im `<head>` ist deshalb **kein** Meta-Tag nötig.

Offen bleibt ein Schritt, der einen Google-Login braucht: In der Search Console unter
**Sitemaps** einmal `sitemap.xml` einreichen. Ohne das dauert die Indexierung deutlich
länger.

## Lokal starten

```
python -m http.server 8097
# http://localhost:8097
```

## Testmodus (`?debug`)

`index.html?debug` blendet ein kleines Bedienfeld ein, das einen GPS-Verlauf
vortäuscht. Nützlich am Schreibtisch, wo der Browser mitten in Wismar steht.
Ohne `?debug` ist der Testmodus vollständig inaktiv.

Die Route entsteht aus den echten `STOP_COORDS`: `_simPfad(6)` legt zwischen je zwei
Stationen sechs Zwischenschritte, man läuft die Tour also der Reihe nach ab. Damit
prüft ein Durchlauf Kartenführung, 50-m-Näherung, Info-Karte und den Standortpunkt
im 3D-Modell in einem Rutsch.


## Abbildungen

Die sieben Einträge tragen seit September 2026 die **58 eigenen Aufnahmen** der
Exkursion: Kubuswoningen 21, Markthal 14, Witte Huis 7, CasaNova 6, Wijnhaveneiland 4,
Red Apple 3, EY 3. Sie liegen als WebP mit 1500 px an der längeren Kante,
zusammen 8,1 MB. Sieben Aufnahmen sind auf Wunsch wieder herausgenommen; die
Dateien sind fortlaufend nummeriert, die dahinterliegenden rücken deshalb auf. An erster Stelle steht je Bauwerk die beste Übersicht, dahinter
nähere Aufnahmen und Details.

Drei Dinge waren dafür an der Galerie nötig, sonst hätte ein Eintrag mit 21 Bildern
mehrere Megabyte auf einmal geholt:

* **Verzögertes Laden.** Die Adresse steht in `data-bg`, geladen wird nur die gezeigte
  Folie samt ihren beiden Nachbarn (`_galLaden()`). Beim Öffnen sind das **drei** Bilder
  statt 21; nachgeladen wird beim Blättern. Eine Fallgrube dabei: Die Funktion muss
  *alle* Folien greifen, nicht nur die noch ungeladenen. Sonst schrumpft die Liste beim
  Laden und der Index zeigt auf die falschen Nachbarn.
* **Kein automatisches Weiterblättern** ab sieben Aufnahmen (`GAL_AUTO_MAX`). Sonst
  liefe die Galerie bei 21 Bildern minutenlang weiter, man käme mit dem Lesen nicht
  nach, und nach einer Runde wären doch alle Bilder geholt.
* **Keine Punktleiste** ab zwölf Aufnahmen; 21 Punkte passen nicht nebeneinander. Die
  Zählung oben rechts übernimmt. Sie stand bisher hinter dem Schließen-Knopf und sitzt
  jetzt daneben.

Vorgeladen wird nur die erste Aufnahme je Bauwerk, damit die Seite auch ohne Empfang
etwas zeigt. Die übrigen holt der Worker beim ersten Ansehen.

Mit den eigenen Fotos entfallen das Kennzeichen `tmp` (der Hinweis „Foto folgt") und die
Lizenzangaben. **Historisch bleiben** das Luftbild von 1940 und der Vergleich
Damals/Heute beim Witte Huis: dessen beide Hälften sind aufeinander eingemessen, ein
anders stehendes Foto würde den Regler entwerten.

Die 24 Bauwerke außerhalb der Route sind nicht mehr im Verzeichnis aufgeführt, siehe
**Das Verzeichnis**. Ihre Daten stehen noch in `NEWBUILDINGS`.

## Vorläufig draußen

Die **Arbeitsfassung (PDF)** ist aus dem Impressum genommen und die Datei aus
`downloads/` entfernt, bis die Fassung als fertig gilt. Der Verweis steht
auskommentiert an seiner Stelle in `index.html`, die Schlüssel `imp_thesis` und
`imp_thesis_link` bleiben in allen drei Sprachen stehen. Zurückholen: Zeile wieder
einkommentieren und die Datei aus der Git-Geschichte wiederherstellen.

Ebenso wartet die **ladungsfähige Anschrift** im Impressum auf Freigabe.

## Status & nächste Schritte

Phase A (Gerüst) steht: Identität, Karte, Tracker, 7 Einträge, 3D-Demos, Trilingualität, Deploy.
Inhalte sind teils Platzhalter.

- **Phase B (vor Ort, 24.10.–01.11.2026):** Interviews je Bauwerk (`voices`), echte GPS-Pins
  (`STOP_COORDS`), Photogrammetrie/Modelle (`/models`), Routenreihenfolge bestätigen.
- **Phase C (nach der Reise):** Reportage-Texte + Steckbriefe füllen, handgezeichneten Schwarzplan
  einsetzen und Karte neu kalibrieren (`gpsToSvg`, `VB`), Print-Handout (A4) erzeugen.


**Bekannt und offen:** Sobald die Karte einsetzt, legt sich der Smart-Track-Schalter
genau über den Sprachschalter (DE · NL · EN). Gemessen auf 360, 390 und 430 px:
`elementFromPoint()` in der Mitte des Sprachschalters trifft jedes Mal den Tracker,
die Sprache lässt sich auf der Karte also nicht mehr wechseln. Das ist eine
Überdeckung, keine Absicht — zu entscheiden bleibt, wohin der Sprachschalter dort
gehört.

Deploy: GitHub Pages aus `main`, Domain `wijnhaven.com` via `CNAME`.
