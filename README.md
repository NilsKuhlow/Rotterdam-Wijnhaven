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
- 3D: `<model-viewer>`, `.glb` in `/models`
- PWA: `manifest.json` + `sw.js` (offline-fähig)
- Sprachen: DE / NL / EN

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
