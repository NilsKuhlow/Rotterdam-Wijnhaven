// ============================================================================
//  Bachelor-Thesis (Arbeitsfassung) - Wijnhaven Waterfront, Rotterdam
//  Hochschule Wismar, Fakultaet Gestaltung, Studiengang Architektur (B.A.)
//  Verfasser: Nils Kuhlow
//  Layout: saubere akademische Standardsetzung. Die HS Wismar schreibt fuer
//  Architektur KEINE verbindliche Typografie vor (PSO/Modulhandbuch ohne
//  Formatvorgaben); Schrift/Abstand/Raender hier als begruendete Konvention.
// ============================================================================

#set document(title: "Transformation der Kante. Die Wijnhaven-Waterfront in Rotterdam", author: "Nils Kuhlow")
#set text(font: "New Computer Modern", size: 11pt, lang: "de", region: "de")
#set par(justify: true, leading: 0.9em, spacing: 1.1em)
#show heading: set block(above: 1.4em, below: 0.8em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => [
  #set text(size: 15pt, weight: "bold")
  #block(it)
]
#show heading.where(level: 2): set text(size: 12.5pt, weight: "bold")
#show heading.where(level: 3): set text(size: 11.5pt, weight: "bold")

// Kurzbeleg im Text: #q[Meyer 1999] -> (Meyer 1999)
#let q(s) = text(style: "normal")[(#s)]

// ---------------------------------------------------------------------------
//  TITELBLATT
// ---------------------------------------------------------------------------
#set page(numbering: none)
#align(center)[
  #v(1.2cm)
  #text(size: 11pt)[Hochschule Wismar \ University of Applied Sciences: Technology, Business and Design \ Fakultät Gestaltung · Studiengang Architektur (B.A.)]
  #v(2.4cm)
  #text(size: 11pt, fill: rgb("#555"))[Bachelor-Thesis (Arbeitsfassung)]
  #v(0.6cm)
  #line(length: 38%, stroke: 0.5pt)
  #v(0.8cm)
  #text(size: 22pt, weight: "bold")[Transformation der Kante]
  #v(0.5cm)
  #text(size: 13pt)[Die Wijnhaven-Waterfront in Rotterdam \ vom Arbeitshafen zum Wohnquartier (1898 bis 2023)]
  #v(0.8cm)
  #line(length: 38%, stroke: 0.5pt)
  #v(2.4cm)
  #text(size: 11pt)[
    vorgelegt von \
    *Nils Kuhlow* \
    Matrikelnummer: _\[einsetzen\]_
  ]
  #v(1.6cm)
  #text(size: 11pt)[
    Erstgutachter: _\[einsetzen\]_ \
    Zweitgutachter: _\[einsetzen\]_
  ]
  #v(1.6cm)
  #text(size: 10.5pt, fill: rgb("#555"))[
    Entstanden im Kontext des Wahlpflichtmoduls „Stadt + Raum“ \
    Thema „Waterfront in Motion“, Exkursion Rotterdam, Gruppe 4 (Wijnhaven)
  ]
  #v(1.0cm)
  #text(size: 11pt)[Wismar, _\[Abgabedatum\]_]
]
#pagebreak()

// ---------------------------------------------------------------------------
//  EIGENSTAENDIGKEITSERKLAERUNG  (RPO HS Wismar, Paragraf 15 Abs. 6)
// ---------------------------------------------------------------------------
#heading(numbering: none, outlined: false)[Eigenständigkeitserklärung]
Ich versichere, dass ich die vorliegende Arbeit selbstständig und ohne
unzulässige fremde Hilfe angefertigt und keine anderen als die angegebenen
Quellen und Hilfsmittel benutzt habe. Alle Stellen, die wörtlich oder
sinngemäß aus veröffentlichten oder nicht veröffentlichten Schriften entnommen
wurden, sind als solche kenntlich gemacht. Die Arbeit hat in gleicher oder
ähnlicher Form noch keiner Prüfungsbehörde vorgelegen.

Bei der elektronischen Fassung versichere ich die Übereinstimmung mit der
schriftlichen Fassung und stimme einer Überprüfung mittels einer
Plagiatssoftware zu.

#v(1.6cm)
#grid(columns: (1fr, 1fr), gutter: 1cm,
  [#line(length: 90%, stroke: 0.5pt) \ Ort, Datum],
  [#line(length: 90%, stroke: 0.5pt) \ Nils Kuhlow]
)
#pagebreak()

// ---------------------------------------------------------------------------
//  KURZFASSUNG
// ---------------------------------------------------------------------------
#heading(numbering: none, outlined: false)[Kurzfassung]
Die Arbeit liest die Wasserkante des Wijnhaven-Quartiers in Rotterdam als
bauliche Schichtung von sieben Bauten zwischen 1898 und 2023 und fragt, was
diese Schichtung über Rotterdams Umgang mit seiner Waterfront erzählt. Vom
Witte Huis (1898) als frühem Hochbau am Arbeitshafen über die Kubuswoningen
(1982 bis 1984) und die Wederopbouw-Kante der Boompjes bis zu den schlanken
Wohntürmen Red Apple (2009) und CasaNova (2022/2023) sowie der hybriden
Markthal (2014) wird die Kante als ein über mehr als ein Jahrhundert
ausgehandelter Übergang zwischen großmaßstäblicher Infrastruktur und Stadt
untersucht. Methodisch verbindet die Arbeit das Port-City-Interface-Modell und
Han Meyers Lesart der Hafenstadt mit einer morphologisch-typologischen
Fallstudie. Der Befund: Rotterdam behandelt seine Waterfront weniger als
fertige Form denn als regelgesteuerten, schrittweisen Übergang, dessen
jüngste, regelbasierte Phase (Wijnhaveneiland-Masterplan) eine dichte, schlanke
Wohn-Silhouette erzeugt, deren Aktivierung des Erdgeschosses und der
Wasserkante offen bleibt und vor Ort zu prüfen ist.

#v(0.6cm)
#text(size: 9.5pt, fill: rgb("#666"))[
  Hinweis zur Fassung: Dies ist eine wissenschaftliche Arbeitsfassung. Die
  Bachelor-Thesis im Studiengang Architektur (B.A.) der HS Wismar ist
  regelhaft eine Entwurfs-/Projektarbeit (Modul PM 20); eine überwiegend
  textbasierte Abhandlung ist mit dem Erstbetreuer und ggf. dem
  Prüfungsausschuss abzustimmen. Einige Zahlen (u. a. Höhe Witte Huis und
  EY-Turm, Wohnungszahl Red Apple, Fertigstellungsjahr CasaNova, Volumenregel
  des Masterplans) sind in den Quellen uneinheitlich und werden im Text
  transparent gemacht; sie sind an den Primärquellen abschließend zu prüfen.
]
#pagebreak()

// ---------------------------------------------------------------------------
//  INHALTSVERZEICHNIS
// ---------------------------------------------------------------------------
#outline(title: "Inhaltsverzeichnis", indent: auto, depth: 3)
#pagebreak()

// ===========================================================================
//  HAUPTTEIL
// ===========================================================================
#set page(numbering: "1")
#counter(page).update(1)

#include "kapitel/01_einleitung.typ"
#include "kapitel/02_theorie.typ"
#include "kapitel/03_methodik.typ"
#include "kapitel/04_rotterdam.typ"
#include "kapitel/05_bauten.typ"
#include "kapitel/06_synthese.typ"
#include "kapitel/07_fazit.typ"

#include "kapitel/99_literatur.typ"
