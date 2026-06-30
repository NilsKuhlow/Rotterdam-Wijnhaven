# downloads/

Direkt von der Website herunterladbare Dateien (Volldetail-Modell bzw. App).

- `wijnhaven-volldetail-demo.glb` ist nur eine **Testdatei** (Kopie des Beispiel-
  Walkthroughs), damit der Download-Knopf in der 3D-Ansicht geprueft werden kann.
- Spaeter durch das echte Volldetail-Modell ersetzen (gleicher Dateiname, dann muss
  am Code nichts geaendert werden) **oder** einen neuen Namen vergeben und in
  `index.html` bei `TOUR_FULLDETAIL_URL` eintragen.

Direkter Download funktioniert, weil die Datei auf **derselben Domain** liegt und der
Link das `download`-Attribut hat.

Groessen-Hinweis: eine Datei direkt im Git-Repo darf max. 100 MB sein. Fuer ein sehr
grosses Modell besser einen GitHub-Release (bis 2 GB pro Datei) oder externen Speicher
nutzen und `TOUR_FULLDETAIL_URL` auf diese URL setzen (externe Links oeffnen statt
direkt herunterzuladen).
