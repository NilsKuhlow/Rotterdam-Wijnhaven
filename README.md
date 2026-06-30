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
- 3D-Walkthrough (Button „3D" oben links): Three.js, lazy vom CDN, On-Demand-Rendering
- PWA: `manifest.json` + `sw.js` (offline-fähig)
- Sprachen: DE / NL / EN
- Akkuschonend: Animationen + GPS pausieren im Hintergrund, ~30fps-Scroll-Cap, kein Idle-Rendering

## 3D-Walkthrough: eigenes Modell bauen

Der Walkthrough lädt `models/walkthrough.glb`. Das mitgelieferte Beispielmodell zeigt die
**Namenskonvention** für antippbare Objekte. Beim eigenen Modell (Blender o.ä.) einfach die
Objekte/Meshes so benennen:

- `building_<N>` → Antippen öffnet Eintrag N (0 = Witte Huis … 6 = CasaNova). Beispiel: `building_2` = Markthal.
- `person_<id>` → Antippen zeigt das Zitat/Interview aus `TOUR_PEOPLE[id]` (in `index.html`).
  Beispiel: `person_kai`. Neue Personen einfach in `TOUR_PEOPLE` mit `de/nl/en`-Eintrag ergänzen.
- `ground`, `scenery_*` → reine Kulisse, nicht antippbar.

Als `.glb` nach `/models/walkthrough.glb` exportieren (Y nach oben, reale Maßstäbe sind ok).
Das Generator-Skript des Beispiels liegt unter `tools/make_walkthrough.py`.

### Abstrakt / Realistisch umschalten

In der 3D-Ansicht gibt es oben einen Umschalter **Abstrakt / Realistisch**.

- **Abstrakt** ist Standard und lädt `models/walkthrough.glb` (weiß, leicht).
- **Realistisch** lädt `models/walkthrough_detailed.glb` erst auf Knopfdruck, mit
  Größen-Hinweis (per HTTP-HEAD ermittelt) und Fortschrittsbalken. Beide Dateien müssen
  **dieselben Knotennamen** haben (`building_<N>`, `person_<id>`), dann funktioniert das
  Antippen für beide ohne Codeänderung. Web-Budget anpeilen: möglichst unter ~25 MB,
  Licht in Lightmaps backen, Texturen als KTX2, Mesh per Draco/Meshopt (`gltf-transform optimize`).
- Gibt es keine Detaildatei, zeigt der Umschalter stattdessen eine **App-/Download-Karte**
  mit Plattformwahl **Windows / Apple / Android** (`TOUR_APP_WINDOWS`, `TOUR_APP_IOS`,
  `TOUR_APP_ANDROID` in `index.html`). Die Website **erkennt das Betriebssystem** und stellt
  den passenden Download nach vorne und hervorgehoben dar. Externe Links (Microsoft Store /
  App Store / Google Play) öffnen, relative Dateien (z. B. `.exe`/`.msi`/`.apk` auf derselben
  Domain) laden direkt herunter. Die echten App-Builds baust du selbst und trägst dann nur
  die Links/Dateien ein.

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
