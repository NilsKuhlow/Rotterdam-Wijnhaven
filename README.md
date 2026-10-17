# Wijnhaven Rotterdam

Interaktiver Stadtrundgang durch das **Wijnhaven-Quartier in Rotterdam**: wie aus der
arbeitenden Hafenkante ein Wohnquartier wurde,
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

Zugrunde liegt der eigene **Schwarzplan**, Stand Oktober 2026. Die Fassung davor zeigte
1307 × 1996 m und endete an der Maas. Auf den Wunsch, mehr von der Umgebung zu sehen,
zeigt die aktuelle **3.928 × 2.837 m**, also rund das Neunfache der Fläche: die ganze
Innenstadt, den Fluss und die Kop van Zuid.

Seit Oktober 2026 liegt sie als **Vektorzeichnung** vor, `img/schwarzplan.svg`,
und nicht mehr als Bild. Davor war sie ein Rasterbild mit 4578 × 3307 px auf
3.928 × 2.837 m, also **0,86 m je Bildpunkt**. Beim Hineinzoomen auf eine Station
zeigte die Karte deshalb Treppen statt Kanten. Die gelieferte Quelle
(`Input/neue Karte.pdf`) half dagegen nicht: Sie enthält genau ein Objekt, ein PNG
mit 4960 × 3507 px, erzeugt in ALLPLAN. Der Vektor ging also schon vor dem Einbau
verloren, und auf der Website lagen bereits 93 % der Quellauflösung.

**Eingemessen, nicht angenommen.** Die neue Zeichnung kommt als CAD-Export mit
172.525 Polygonen in flachen Lagen. Ihre Wasserfläche wurde gegen die des bisherigen
Rasterplans kreuzkorreliert, über einen Maßstabsfächer von ±3 %. Das Maximum sitzt bei
**Maßstab 1,0000 und Versatz 0/0 Bildpunkten**, der **Jaccard der Wasserflächen bei
0,947**, der der Baukörper bei **0,912**. Der Ausschnitt ist also derselbe, und die
Abbildung ist dieselbe, die `preserveAspectRatio="none"` dem Rasterbild angetan hat:

    Rahmen 4375,84..5456,87 / 4524,04..5304,74   →   0..3010 / 0..2175

Gegenprobe an den sieben Bauten, und die zählt: **fünf liegen im Gebäude**, die beiden
anderen 12 m und 5 m daneben (Kubuswoningen, wo zwischen den Würfeln Lücken sind). Das
ist dieselbe Lagegenauigkeit wie zuvor, mit denselben beiden Ausreißern.

**Aus 516.864 Punkten wurden 167.458.** Der Export zerlegt jede gefüllte Fläche in
Dreiecke, allein 172.288 Stück für die Baukörper. Gezeichnet sieht man davon nichts,
weil Füllung und Strich dieselbe Farbe haben, die Datei trägt es aber mit: 6,0 MB. Der
erste Versuch, die Dreiecke über ihre gemeinsamen Kanten zusammenzusetzen, ist
gescheitert, denn 60 % der Kanten liegen am Rand, das Netz ist also keine saubere
Triangulierung; die Flächenprobe kam nur auf 0,92. Die ehrliche Variante, eine echte
Vereinigung der Flächen mit GEOS, braucht 8 Sekunden und schafft es exakt. Mit
relativen Wegstücken und 0,1 Einheiten Rundung (13 cm) sind es **2,1 MB, über die
Leitung gzip-komprimiert rund 640 KB**, praktisch dasselbe wie die 612 KB des
WebP-Bildes davor, bei beliebiger Schärfe.

**Angezeigt wird sie zweistufig.** Zuerst als verwiesenes Bild, damit die Karte ohne
Umweg da ist; danach holt `planVektorInline()` im Leerlauf dieselbe Datei und schreibt
sie in das Karten-SVG, das Bild fällt weg. Grund: Ob ein Browser ein verwiesenes SVG
beim Zoomen neu rastert, ist nicht garantiert. Chrome tut es, an einer Zoomprobe
gemessen; inline gilt es überall. Schlägt der Abruf fehl, bleibt das Bild stehen.

**Was der Wechsel sonst noch bringt:** Die Karte lässt sich wieder über CSS umfärben,
Wasser- und Bauwerksfarbe stecken nicht mehr in einem Bild.

Eine SVG-Einheit bleibt **1,3048 m** wie in allen Fassungen davor. Nur so gelten
Punktgrößen, Strichstärken, Beschriftungen und der 50-m-Radius unverändert weiter.
Ursprung (`gpsToSvg`) und Planmaße (`MAP_VW` 3010, `MAP_VH` 2175) sind dieselben
wie bei der Rasterfassung, deshalb hat sich keine Stationsnadel bewegt.

**Vergrößern und verkleinern.** Drei Knöpfe rechts unten in der Karte: näher, weiter,
zurück auf die Gesamtansicht. Dazu Gesten, aber nur solche, die dem Blättern nicht in
die Quere kommen: **zwei Finger** auf der Karte für Größe und Lage zugleich, am Rechner
das **Rad mit Strg oder Befehlstaste** (das ist auch die Geste, die ein Trackpad beim
Zusammenziehen schickt), **Ziehen mit der Maus** und **Doppelklick**. Der eine Finger
bleibt dem Scrollen vorbehalten: Die Karte füllt das ganze Fenster, wer ihr den einen
Finger nimmt, sperrt die Seite ein. Deshalb `touch-action: pan-y` statt `none`.

Die engste Stufe ist `KARTE_MIN_VB` = 60 Einheiten, also **78 m Bildbreite**. Die
weiteste ergibt sich aus dem Plan selbst: mehr als 3010 × 2175 gibt es nicht, und weil
das SVG mit `slice` arbeitet, ist auf einem hochformatigen Telefon bei rund 1005
Einheiten Breite Schluss, dann steht die volle Planhöhe im Bild.

**Dabei kam ein alter Fehler ans Licht.** Die Gestenebene des Smart-Track rechnete noch
mit `CANVAS_W` 1000 und `CANVAS_H` 750, den Maßen der engen Karte von vor dem Wechsel
auf den weiten Ausschnitt. Das Schieben war dadurch auf das linke obere Neuntel des
Plans eingesperrt, und `MAX_VB_W` von 900 ließ ein Herauszoomen auf die ganze Karte gar
nicht zu. Beide Klemmungen laufen jetzt über dieselbe Funktion, `kartenVBSetzen()`.

**Marken wachsen nicht mit.** Punkte, Ringe und Beschriftungen liegen im Koordinatenraum
des Plans; bei fünffacher Vergrößerung deckte „05 Red Apple" das halbe Bild zu.
`_markenMass()` rechnet die Größen gegen, angestoßen von einem `MutationObserver` auf der
viewBox. Der fasst alle Wege zusammen, auf denen sie gesetzt wird: Knopf, Geste, Schwung,
Sprung zur Station und die weichen Überblendungen. Strichstärken brauchen das nicht,
für sie genügt `vector-effect: non-scaling-stroke`; das hält sie in Bildpunkten fest und
lässt die Zustände für Zeiger und aktive Station in Ruhe. Gemessen: Punkt 5,68 → 5,66
Bildpunkte, Beschriftung 6,94 → 6,96, über fünf Zoomstufen.

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

## Die Eintragstexte

Jeder der sieben Einträge trägt **fünf Absätze**, rund 2.100 Zeichen, in DE, NL und EN.
Die ersten drei sind Beobachtung vor Ort, im Ton des Feldjournals. Die beiden letzten
stellen den Bau in den Städtebau und stammen aus der Begleitarbeit in `thesis/`
(Kapitel 04 Rotterdam, 05 Bauten, 06 Synthese):

* **Absatz 4** sagt, woher der Ort kommt und in welcher Etappe der Bau steht: die
  gegrabenen Becken von 1609 und 1613, der Basisplan von Van Traa vom 28. Mai 1946,
  die drei Wellen der Hinwendung zum Wasser (Waterstad 1985, Kop van Zuid 1991,
  Stadsvisie 2030 vom 29. November 2007), das Regelwerk von KCAP ab 1992/93.
* **Absatz 5** sagt, was der Bau für den Stadtraum bedeutet, und läuft immer bis ins
  Erdgeschoss hinunter. Dort liegt die Leitfrage: Die Sockelzone macht rund ein Zehntel
  eines Gebäudes aus und entscheidet über etwa neun Zehntel dessen, was man auf der
  Straße erlebt. Rotterdams eigene **Hoogbouwvisie (2019)** hat das amtlich übernommen,
  samt Verabschiedung des freistehenden Turms. Ob die Wijnhaven das einlöst, lässt die
  Seite offen; entschieden wird es beim Gehen.

Die Zahlen aus dem Regelwerk stehen so, wie die Begleitarbeit sie belegt: 22 m³ je m²
Grund, höchstens 580 m² Turmgeschossfläche, ein Turm je 2.000 m² erworbener Fläche,
FSI 3,9 und im Hochbau bis 6,2. Wo die Quellen auseinandergehen, steht das im Text
(KCAP nennt an anderer Stelle eine höhere Dichte).

Jeder deutsche Absatz steht zweimal im Dokument, in `SEED7` und im Sprachblock
`stopParas`; Niederländisch und Englisch je einmal. Wer hier etwas ändert, ändert es
viermal. `_weaveBody()` verteilt die Abbildungen gleichmäßig auf die Absätze, längere
Texte brauchen also keine Anpassung des Layouts.

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

**Sieben Aufnahmen standen schief** und werden beim Aufbereiten geradegerückt
(`gerade.py`, Winkel zwischen 0,5 und 3,2 Grad). Die Originale in `Fotos Export`
bleiben unberührt, gedreht wird erst auf dem Weg zur Website: Winkel aus der Tabelle
streichen, Bilder neu erzeugen, und der Eingriff ist weg.

Gemessen wurde mit zwei unabhängigen Zeugen, der Richtung der fast senkrechten und
der der fast waagerechten Kanten. Eine echte Kameradrehung verdreht beide um denselben
Betrag, Perspektive und Dachschrägen nicht. Nur wo beide innerhalb von 1,2 Grad
übereinstimmten, galt der Wert; jede Korrektur wurde danach mit einem Gitter im Bild
gegengeprüft. Nach dem Drehen wird auf den größten zentrierten Ausschnitt gleichen
Seitenverhältnisses beschnitten, damit keine leeren Ecken bleiben und die Maße in
`index.html` weiter stimmen.

**Warum nicht alle:** Die Kubuswoningen bestehen aus um 45 Grad gekippten Würfeln, und
die meisten Aufnahmen blicken nach oben. Dort gibt es keine Senkrechte, an der sich
eine Messung festhalten könnte. Eine erste Messung über alle Kanten meldete dort acht
Grad Schieflage, obwohl die Aufnahme gerade ist. Was dort schief aussieht, ist die
Sache selbst.

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

### Zwei historische Karten, gemeinfrei

Im Oktober 2026 dazugekommen, und bewusst **offen** statt hinter dem Schloss: Was frei
ist, gehört nach vorn.

**`img/plan-1940.webp`** — *Gemeente Rotterdam en omgeving*, 1:10.000, herausgegeben vom
Gemeentelijke Technische Dienst, 1940. Ausschnitt der Innenstadt aus einem Blatt von
9894 × 7900 px; zugeschnitten statt verkleinert, sonst wäre der Wijnhaven ein Fleck von
zwanzig Bildpunkten. Vom Stadsarchief Rotterdam ausdrücklich als gemeinfrei freigegeben.
Damit hat das Projekt **zum ersten Mal einen Plan der Vorkriegsstadt**: die feinkörnige
Parzellierung, über die es bisher nur Prosa gab. Für die entfernte Platzhalterzeichnung
`vorkrieg.webp` ist das der späte Ersatz, diesmal ein echtes Blatt.

**`img/oud-en-nieuw-1955.webp`** — *Oud en nieuw Rotterdam*, 1:5.000, Gemeentewerken
Rotterdam, Abteilung Kartografie, **18. Mai 1955**. Das Blatt legt dreierlei übereinander:
den Grundriss vor Mai 1940, den Plan des neuen Stadtkerns und den Stand des Wiederaufbaus
an jenem Tag, dazu die **Brandgrenze in Gelb**. Es beantwortet in einem Bild genau die
Frage des Basisplan-Kapitels: was vorgesehen war und was davon nach neun Jahren stand.
Anonymes Werk, Schutzfrist siebzig Jahre nach Veröffentlichung, **2025 abgelaufen**.

Beide über Wikimedia Commons. Die Rechtelage steht in der Bildunterschrift auf der Seite,
nicht nur hier.

## Der Seminarbereich

Ein Teil des Planmaterials gehört uns nicht. Es liegt deshalb hinter einem Schloss,
erreichbar nur über einen Link, den der Kurs bekommt.

**Ein Passwort in JavaScript wäre dafür wertlos.** Auf einer statischen Seite stünden die
Dateien weiter unter öffentlichen Adressen; wer die Adresse kennt, lädt sie, und
rechtlich ist das Werk damit weiterhin öffentlich zugänglich gemacht. Also wird nicht
abgefragt, sondern **verschlüsselt**. Veröffentlicht wird nur Geheimtext: ohne Passwort
kein Bild, sondern Rauschen. Gemessen an `privat/inhalt.bin`: **7,939 Bit Entropie je
Byte**, von Zufall nicht zu unterscheiden.

| | |
|---|---|
| Schlüssel | `PBKDF2-SHA256`, 310.000 Runden (OWASP-Empfehlung), 256 Bit |
| Verfahren | `AES-256-GCM`, je Datei ein zufälliger 12-Byte-IV, vorangestellt |
| Bibliothek | keine. WebCrypto bringt beides mit |

GCM authentifiziert mit: Ein falsches Passwort und jede Veränderung am Paket fallen auf,
statt halb entschlüsselten Unsinn durchzulassen.

### Der Link

```
https://wijnhaven.com/#seminar=<passwort>
```

Was hinter der Raute steht, **schickt der Browser nie an einen Server** und auch nicht im
Referer mit. Es taucht also in keinem Protokoll von GitHub Pages auf. Direkt nach dem
Aufschließen kürzt `_semHashKuerzen()` die Adresszeile auf `#seminar`; sonst stünde das
Passwort im Verlauf, in der Zurück-Liste und auf jedem Bildschirmfoto. Unter `#seminar`
allein erscheint ein Eingabefeld, der gekürzte Link bleibt also brauchbar.

Der abgeleitete Schlüssel liegt danach in `localStorage` (`wij-seminar-v1`), **das
Passwort nie**. Ein Knopf im Kapitel wirft ihn wieder weg.

### Was bewusst nicht in `index.html` steht

Kein Titel, keine Bildunterschrift, kein Urhebername des geschützten Materials. Das alles
liegt im verschlüsselten Verzeichnis `privat/inhalt.bin`. Stünde es im Quelltext,
verriete das Schloss, was es verschließt. Aus demselben Grund liegt die Tabelle
`quellen.py` **außerhalb des Repos**, in `Input/Privat/`, zusammen mit dem Passwort und
den Vorlagen. Im Repo steht nur die Maschine, `tools/privat/packen.py`, die nichts verrät.

Die Dateinamen in `privat/` sind aus Passwort und Dateiname abgeleitete Hex-Namen ohne
Endung: bei jedem Lauf dieselben, damit der Cache nicht vollläuft, und ohne jeden Hinweis
auf den Inhalt.

### Nachfüllen

Datei nach `Input/Privat/` legen, in `Input/Privat/quellen.py` eintragen,
`python tools/privat/packen.py` laufen lassen. PDFs werden Seite für Seite zu Abbildungen.
`ziel` sagt, wo sie erscheint: `plaene` im eigenen Kapitel, `basisplan` oder `historie`
zusätzlich in einem der beiden vorhandenen. Entschlüsselte Bilder werden zu Blob-URLs und
gehen durch denselben `_figureHtml()`-Aufbau wie jede andere Abbildung.

### Die Kartenebene mit Regler

Im aufgeschlossenen Zustand liegt über der Karte eine zuschaltbare Schicht: die vom
Basisplan **tatsächlich ausgeführten Bauten**, aus der Revisiekaart gelöst, alles andere
durchsichtig. Ein **Regler statt eines Schalters**, Startwert 0 Prozent, weil man zwei
Schichten im Übergang vergleicht und nicht im Entweder-oder.

Die Lage stammt aus der Einmessung vom 13. Oktober und wurde damals mit drei Verfahren
geprüft: **2,27 m je Bildpunkt**, nordgerichtet, `translate(442,3 −93,8) scale(1,73952)`.
Der verbleibende Rest von rund **10 m** ist die Auflösung der Vorlage, 1600 Bildpunkte
auf 3,6 km, und kein Fehler der Einpassung.

Zugesperrt gibt es beides nicht, und zwar wirklich nicht: kein Bild, keine Lage, kein
Regler, und im Quelltext steht an keiner Stelle, was die Schicht zeigt. Beschriftung und
Geometrie kommen aus dem verschlüsselten Verzeichnis.

### Die Karte als Palimpsest

Drei Schichten übereinander, zwei Regler:

| | |
|---|---|
| unten | der Schwarzplan von heute, als Vektorzeichnung |
| darüber | **die Stadt vor dem 14. Mai 1940**, öffentlich |
| darüber | **die vom Basisplan ausgeführten Bauten**, hinter dem Schloss |

Die Reihenfolge ist die eines Palimpsests: **die älteste Karte zuunterst.** Was darüber
liegt, blendet man weg, um sie freizulegen. Die Wiederaufbauschicht bleibt oben, weil sie
bis auf die roten Bauten durchsichtig ist und gegen heute gelesen wird, nicht gegen das
Papier.

Jede Schicht hat **einen Schalter und einen Regler**. Der Schalter merkt sich den Wert:
Ausschalten und wieder einschalten macht dort weiter, wo man aufgehört hat. Der Regler
auf 0 gezogen heißt aus, das ist dieselbe Aussage und soll nicht zwei Zustände ergeben.

Der Regler läuft in **Schritten von 20 Prozent**. Stufenlos zog er bei jedem Zwischenwert
eine mehrere Megabyte große Ebene neu durch den Compositor, was auf dem Telefon ruckelte.
Sechs Stufen reichen, und die Bedienung wird dadurch sicherer statt ärmer.

Das Blatt von 1940 ist gemeinfrei und braucht kein Schloss; die Revisiekaart schon. Eine
Quellenzeile nennt, was gerade zu sehen ist, und verschwindet wieder. Das Bild der 1940er
Ebene (861 KB) wird **erst beim ersten Aufdrehen** geladen: Wer die Ebene nie anfasst,
soll sie auch nicht bezahlen.

### Was der Erstaufruf kostet

Gemessen gegen die Live-Seite: **9,68 MB in 67 Dateien**, alles innerhalb von sechs
Sekunden. Der Schwarzplan sind 680 KB davon, der Löwenanteil sind die **58 Galeriefotos**,
die `preloadAll()` im Leerlauf vorholt, damit die Seite vor Ort offline funktioniert.

Im WLAN ist das richtig. Im Zug nach Rotterdam über Mobilfunk ist es der teuerste Posten
der ganzen Seite, in Datenvolumen wie in Energie, und zwar bevor jemand überhaupt einen
Eintrag geöffnet hat. Seit dem 17. Oktober 2026 **fragt die Seite deshalb nach der
Leitung**: `_darfVorladen()` prüft `navigator.connection.saveData` und `effectiveType`.
Wer Datensparen eingeschaltet hat oder in einem 2G- oder 3G-Netz steckt, bekommt die
Bilder erst beim Öffnen eines Eintrags.

| | Dateien | übertragen |
|---|---|---|
| normal | 65 | 11,53 MB |
| Datensparen | 7 | **3,02 MB** |

(lokal gemessen, ohne gzip auf dem SVG, deshalb mehr als die 9,68 MB live)

Browser ohne `navigator.connection`, also Safari, laden vor wie bisher: Schweigen ist kein
Nein. Der Precache des Service Workers bleibt unangetastet, 20 Dateien als Offline-Hülle.
Das ist das Versprechen, dass die Karte in Rotterdam auch ohne Netz steht, und dafür lohnt
es sich.

### Was die Seite im Leerlauf kostet

Gemessen über `Performance.getMetrics`, acht Sekunden Ruhe auf der Kartenbühne:

| | vorher | nachher |
|---|---|---|
| Stilberechnung | 4,4 ms/s | **0,0 ms/s** |
| Layout | 0,0 ms/s | 0,0 ms/s |
| gesamt | 2,2 % einer CPU | **1,2 %** |

Die Ursache war der **Scroll-Hinweis im Intro**: `cueSlide` lief endlos weiter, auch wenn
das Intro längst durchgescrollt war, und erzwang dauerhaft Stilberechnung, ohne irgendetwas
zu zeigen. `document.getAnimations()` im Leerlauf meldet jetzt eine leere Liste. Dazu
respektiert er `prefers-reduced-motion`.

Zwei Schichten gleichzeitig kosten im Leerlauf nichts zusätzlich (1,65 % statt 1,22 %,
der Rest ist Messaufwand): Die Ebenen sind statische Bilder, der Compositor arbeitet nur,
wenn sich etwas ändert.

**Die Einpassung von 1940 hat sieben Anläufe gekostet, und der Fehler lag bei mir.** Ich
hatte 300 dpi angenommen, weil die Metadaten bei Wikimedia das an einer Stelle behaupten.
Das Blatt entspricht aber **200 dpi**, bei 1:10.000 also **1,270 m je Bildpunkt** statt
0,847. Alle Suchen lagen damit um den Faktor 1,5 im Maßstab daneben, und deshalb ist nie
etwas eingerastet; die Korrelation rutschte stattdessen der Maas entlang und landete
einmal sogar auf der Waalhaven.

Mit dem richtigen Wert rastet es sofort ein: **Jaccard der Wasserflächen 0,692**, mit
sauberem Anstieg und Abfall zu beiden Seiten, Drehung +0,4 Grad. Was übrig bleibt, ist
kein Fehler, sondern Geschichte: die seither zugeschütteten Singels und die nach dem
Krieg veränderten Kaikanten.

**Ein zweiter Fehler fiel dabei auf.** Meine Wassermaske hatte die Becken der Innenstadt
verschluckt. Sie sind 40 bis 80 m breit, also 50 bis 95 Bildpunkte im Blatt und nach dem
Verkleinern ein Dutzend; im Papierton des Rasterdrucks verschwinden sie dabei. An der
Wijnhaven fand die Maske **null Wasser**. Übrig blieb die Maas, und an einem Fluss allein
rutscht jede Korrelation entlang. Jetzt wird in voller Auflösung geschwellt und erst
danach zusammengefasst (`tools/schwarzplan/hist_neu.py`).

### Grundrisse in den Einträgen

Seit dem 17. Oktober 2026 liegen **15 Zeichnungen** im Seminarbereich, die nicht in einem
eigenen Kapitel stehen, sondern **im Eintrag des Baus selbst**: `ziel` ist dort der Slug
der Station, und `openModal()` hängt sie an die Abbildungen des Eintrags an. Zugesperrt
gibt `_semFiguren()` eine leere Liste zurück und der Eintrag sieht aus wie immer.

| Bau | Zeichnungen | Urheber |
|---|---|---|
| Kubuswoningen | Lageplan, drei Grundrisse (Straße, Promenade, Wohnen), Längsschnitt | Piet Blom |
| Markthal | Markthalle, zwei Wohngeschosse, Umgebung, Querschnitt | MVRDV |
| CasaNova | Lageplan, Erdgeschoss, Sockel, Regelgeschoss, Axonometrie | Barcode Architects |

Gefunden bei ArchDaily, das die Zeichnungen der Büros veröffentlicht. **Eine Lizenz steht
dort nirgends**, die Rechte liegen bei den Urhebern, und genau deshalb liegen sie hinter
dem Schloss. Jede Zeichnung trägt diesen Vermerk in ihrer Bildunterschrift.

Ausgewählt ist, was erklärt, nicht alles, was da war: Von den sechs fast gleichen
Wohnungsgeschossen der Markthal steht hier eines. Die übrigen liegen in
`Input/Privat/grundrisse/` und sind mit einer Zeile in `quellen.py` nachzutragen.

**Vier der sieben Bauten haben keine.** Für das **Witte Huis**, **Red Apple**,
**EY Netherlands** und das **Wijnhaveneiland** habe ich nichts Brauchbares gefunden. Beim
Witte Huis wäre es die Mühe wert: Molenbroek starb 1922, seine Zeichnungen sind damit
gemeinfrei und könnten offen stehen. Das Stadsarchief Rotterdam führt Bauakten zum
Gebäude, online auffindbar war nichts. KCAP und die Seite zu Boompjes 258 liefern ihre
Projektseiten als JavaScript-Anwendung aus, da kam der Abruf nicht durch.

### Die Rechtelage, ungeschönt

Der Bereich senkt das Risiko, er macht die Nutzung nicht von selbst rechtmäßig. Der
Rahmen, der hier trägt, ist **§ 60a UrhG**: Veranschaulichung des Unterrichts für einen
**bestimmt abgegrenzten Kreis** von Teilnehmern. Genau diesen Kreis stellt das Schloss
her, und deshalb ist die Verschlüsselung kein Beiwerk, sondern die Bedingung. Jede
Abbildung trägt ihren tatsächlichen Rechtevermerk. **Keine Genehmigung behaupten, die es
nicht gibt.** Das ist in diesem Projekt schon einmal passiert und wurde zurückgenommen.

Offen und nachzuhalten: eine Anfrage an den Urheber der Revisiekarte
(`info@3develop.nl`, er verkauft Drucke davon) und eine Rückfrage beim Lehrstuhl.

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
