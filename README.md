# Wijnhaven, Feldjournal

Interaktives Feldjournal durch das **Wijnhaven-Quartier in Rotterdam**: sieben Bauten am Wasser,
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
- Karte: inline SVG-Figure-Ground (Platzhalter), scroll-getriebene Kamerafahrt, GPS Smart-Track
- 3D je Eintrag: `<model-viewer>`, `.glb` in `/models`
- 3D-Gesamtmodell (Button „3D" oben links): `<model-viewer>`-Drehteller, Draco-Mesh + WebP-Texturen
- PWA: `manifest.json` + `sw.js` (offline-fähig)
- Sprachen: DE / NL / EN
- Akkuschonend: Animationen + GPS pausieren im Hintergrund, ~30fps-Scroll-Cap, kein Idle-Rendering

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

## Lokal starten

```
python -m http.server 8097
# http://localhost:8097
```

## Status & nächste Schritte

Phase A (Gerüst) steht: Identität, Karte, Tracker, 7 Einträge, 3D-Demos, Trilingualität, Deploy.
Inhalte sind teils Platzhalter.

- **Phase B (vor Ort, 24.10.–01.11.2026):** eigene Fotos, Interviews (`voices`), echte GPS-Pins
  (`STOP_COORDS`), Photogrammetrie/Modelle (`/models`), Routenreihenfolge bestätigen.
- **Phase C (nach der Reise):** Reportage-Texte + Steckbriefe füllen, handgezeichneten Schwarzplan
  einsetzen und Karte neu kalibrieren (`gpsToSvg`, `VB`), Print-Handout (A4) erzeugen.

Deploy: GitHub Pages aus `main`, Domain `wijnhaven.com` via `CNAME`.
