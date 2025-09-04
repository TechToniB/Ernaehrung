
# Ernährungsrechner Dokumentation


- [Übersicht](#übersicht)
- [1. Hauptmenü](#1-hauptmenü-hauptmenüpy)
	- Die Einstellungen werden persistent gespeichert und beim nächsten Start automatisch übernommen.
- [3. Rechner Nahrungsmittel in Nährstoffe](#3-rechner-nahrungsmittel-in-nährstoffe-rechner-nahrungsmittel-in-nährstoffepy)
- [4. Gerichte / Rezepte](#4-gerichte--rezepte-rechner-rezeptepy)
	- Die Oberfläche ist responsiv und passt sich der Fenstergröße an.
- [6. Weitere Dateien und Ordner](#6-weitere-dateien-und-ordner)
- [7. Technische Hinweise](#7-technische-hinweise)
- [8. Installation und Voraussetzungen](#8-installation-und-voraussetzungen)

## Übersicht

Dieses Projekt besteht aus mehreren Python-Programmen, die verschiedene Funktionen rund um das Thema gesunde Ernährung, Nährstoffberechnung, Rezepte und Saisonkalender bieten. Die Programme sind über ein zentrales Hauptmenü mit moderner grafischer Oberfläche (Tkinter + ttkbootstrap) miteinander verbunden. Im Folgenden werden die wichtigsten Programme und deren Funktionsweise ausführlich beschrieben.

---

### Technische Besonderheiten

- Die Prozesse werden über `subprocess.Popen` gestartet, was eine unabhängige Ausführung der Teilprogramme ermöglicht.
- Die Fenstersteuerung (in den Vordergrund holen) funktioniert nur unter Windows und mit installiertem `pywin32`.
- Die Einstellungen werden als JSON-Datei gespeichert und sind leicht anpassbar.


## 1. Hauptmenü (`Hauptmenü.py`)


### Hauptfunktionen und Ablauf
	- Die Tabellen können beliebig erweitert werden, solange das Format (Spaltennamen) erhalten bleibt.
- **Start und Einstellungen:**
	- Beim Start liest das Programm die Datei `settings.json` ein, um Theme (hell/dunkel, verschiedene Farbschemata) und Vollbildmodus zu setzen. Die Einstellungen können jederzeit über das Einstellungsmenü angepasst werden.
	- Im Vollbildmodus wird die Fensterleiste ausgeblendet, um ein ablenkungsfreies Arbeiten zu ermöglichen.

- **Bedienoberfläche:**
	- Das Hauptmenü zeigt eine Liste von Buttons, die jeweils ein Teilprogramm starten. Die Buttons sind groß und klar beschriftet, sodass die Navigation auch auf Touchscreens oder für ältere Nutzer einfach ist.
	- Die Buttons passen sich dem gewählten Theme an und sind im Vollbildmodus besonders groß und übersichtlich angeordnet.

- **Starten von Teilprogrammen:**
	- Die Kommunikation zwischen den Fenstern erfolgt über die Bibliothek `pywin32` (sofern installiert), um Fenster gezielt zu aktivieren.
- **Buttons im Überblick:**

### Technische Besonderheiten

- Die Tabellenanzeige ist dynamisch und passt sich der Größe der geladenen Tabelle an.
- Die Prüfung der Werte erfolgt automatisiert und berücksichtigt verschiedene Kategorien und Toleranzen.
- Die Speicherung erfolgt im Excel-Format, sodass die Ergebnisse weiterverarbeitet werden können.

	- *Rechner Nahrungsmittel in Nährstoffe*: Startet den Nährstoffrechner für beliebige Lebensmittel.
	- *Gerichte*: Startet das Rezepte-Programm zur Anzeige und Berechnung von Rezepten.
	- *Saisonkalender*: Öffnet die Saisonkalender-Übersicht für Obst und Gemüse.
	- *Beenden*: Schließt das Hauptmenü und damit die zentrale Steuerung.

---
---

## 2. Rechner Import (`Rechner Import.py`)
Dieses Programm ist speziell für den Vergleich eigener Nährstoffaufnahmen mit offiziellen Referenzwerten (z.B. DGE-Empfehlungen) konzipiert. Es eignet sich besonders für Ernährungsberater, Studierende oder Privatpersonen, die ihre Ernährung gezielt überprüfen möchten.
### Funktionsweise und Ablauf

- **Excel-Tabellen laden:**

### Technische Besonderheiten

- Die Lebensmittel- und Nährstoffdatenbank ist als Excel-Datei organisiert und kann leicht erweitert werden.
- Die dynamische Generierung der Auswahlfelder ermöglicht eine flexible Nutzung.
- Die Summenfunktion erkennt automatisch gleichnamige Nährstoffe und addiert diese korrekt.

	- Nach Auswahl einer Tabelle werden die Daten geladen und in drei gleich große Spalten aufgeteilt, um die Übersichtlichkeit zu erhöhen.

- **Tabellenanzeige und Eingabe:**
	- Für jede Zeile gibt es ein eigenes Eingabefeld, in das der Nutzer seinen eigenen Wert eintragen kann (z.B. die eigene Tageszufuhr).
- **Prüfen der Werte:**
	- Nach Eingabe der Werte kann per Button eine automatische Prüfung erfolgen. Das Programm vergleicht die eigenen Werte mit den Referenzwerten.
		- *Richtwert*: ±10%
		- *Empfohlene Zufuhr*: Wert sollte mindestens erreicht werden
	- Fehlerhafte oder fehlende Eingaben werden erkannt und entsprechend markiert.
- **Speichern der Ergebnisse:**

### Technische Besonderheiten

- Die Rezepte werden aus einer Excel-Datei geladen, die beliebig erweitert werden kann.
- Die Suchfunktion ist performant und filtert auch bei sehr vielen Rezepten schnell.
- Die Speicherung erfolgt im Excel-Format, sodass die Rezepte weitergegeben oder archiviert werden können.


- **Rückkehr zum Hauptmenü:**
	- Über einen Button kann das Hauptmenü wieder in den Vordergrund geholt werden, ohne das Programm komplett zu schließen.
---
---


## 3. Rechner Nahrungsmittel in Nährstoffe (`Rechner Nahrungsmittel in Nährstoffe.py`)
Dieses Programm ist ein flexibler Nährstoffrechner, mit dem die Nährstoffgehalte beliebiger Lebensmittel individuell berechnet und verglichen werden können. Es eignet sich für Ernährungsplanung, Diätberatung und wissenschaftliche Auswertungen.
### Funktionsweise und Ablauf

### Technische Besonderheiten

- Die Kalenderdaten werden aus Python-Dateien geladen, die jeweils Listen mit Monatswerten enthalten.
- Die Tabellenanzeige ist dynamisch und kann beliebig viele Einträge verarbeiten.
- Die Exportfunktion nutzt `pandas` und `openpyxl` für maximale Kompatibilität.

- **Lebensmittelauswahl:**
	- Über ein oder mehrere Dropdown-Menüs können beliebig viele Lebensmittel aus einer umfangreichen Datenbank ausgewählt werden. Die Suchfunktion erleichtert das schnelle Finden des gewünschten Lebensmittels.
	- Für jedes Lebensmittel kann die gewünschte Menge in Gramm angegeben werden (Standard: 100g).
	- Es können dynamisch weitere Auswahlfelder hinzugefügt oder entfernt werden, um mehrere Lebensmittel gleichzeitig zu berechnen.

- **Nährstoffberechnung:**
	- Nach Auswahl und Mengeneingabe werden die Nährstoffwerte (z.B. Eiweiß, Fett, Vitamine, Mineralstoffe) für das jeweilige Lebensmittel berechnet und übersichtlich im Ausgabefeld angezeigt.
	- Die Berechnung erfolgt auf Basis der hinterlegten Excel-Datenbank (`Gefilterte_Kategorien_zusammengefuegt.xlsx`).

- **Summenfunktion:**
	- Mit einem eigenen Button können die Summen aller Nährstoffe über alle ausgewählten Lebensmittel berechnet werden. Dies ist besonders nützlich für die Planung kompletter Mahlzeiten oder Tagesrationen.

- **Ergebnisse speichern:**
	- Die berechneten Werte können als Textdatei gespeichert werden. Der Dateiname enthält automatisch die Namen der ausgewählten Lebensmittel.

- **Weitere Funktionen:**
	- Das Ausgabefeld kann per Button geleert werden.
	- Im Nicht-Vollbildmodus steht eine Menüleiste mit Datei- und Hilfefunktionen zur Verfügung (z.B. Öffnen, Speichern, Hilfe).
	- Über einen Button kann das Hauptmenü wieder in den Vordergrund geholt werden.

---

---


## 4. Gerichte / Rezepte (`Rechner Rezepte.py`)

Dieses Programm dient der Anzeige, Anpassung und Speicherung von Rezepten. Es ist besonders hilfreich für die Planung von Mahlzeiten, das Nachkochen und die Nährwertberechnung von Gerichten.

### Funktionsweise und Ablauf

- **Rezeptauswahl:**
	- Die Rezepte sind in einer Excel-Datei (`rezepte_gefiltert.xlsx`) gespeichert. Über ein Dropdown mit Suchfunktion kann ein Rezept schnell gefunden und ausgewählt werden.

- **Zutatenanzeige:**
	- Nach Auswahl eines Rezepts werden alle Zutaten, Mengen und Einheiten tabellarisch angezeigt. Die Tabelle ist übersichtlich gestaltet und zeigt auch die Anzahl der Portionen an.
	- Die Zutatenliste ist dynamisch: Sie passt sich an das gewählte Rezept an und zeigt alle relevanten Informationen (z.B. Menge, Einheit, ggf. Link zum Originalrezept).

- **Berechnung für Portionen:**
	- Die Mengen der Zutaten können für eine beliebige Anzahl verwendeter Portionen umgerechnet werden. Der Nutzer gibt die gewünschte Portionszahl ein, und die Mengen werden automatisch angepasst.

- **Link zum Originalrezept:**
	- Falls in der Excel-Datei ein Link zum Originalrezept hinterlegt ist, wird dieser angezeigt und kann direkt im Browser geöffnet werden.

- **Speichern:**
	- Die angezeigten Zutaten und Mengen (inklusive der umgerechneten Werte) können als Excel-Datei gespeichert werden. So kann der Nutzer die Rezepte weitergeben oder archivieren.

- **Weitere Funktionen:**
	- Über einen Button kann das Hauptmenü wieder in den Vordergrund geholt werden.

---

---


## 5. Saisonkalender (`Zusammenführung der Saisonkalender.py`)

Dieses Programm bietet eine übersichtliche Darstellung der Saisonzeiten für Obst und Gemüse aus verschiedenen Quellen (REWE, EDEKA). Es unterstützt eine nachhaltige und saisonale Ernährung.

### Funktionsweise und Ablauf

- **Kalenderauswahl:**
	- Der Nutzer kann zwischen den Kalendern von REWE, EDEKA oder einer kombinierten Ansicht wählen. Die Auswahl erfolgt über Radiobuttons.

- **Tabellenanzeige:**
	- Die verfügbaren Obst- und Gemüsesorten werden in einer Tabelle angezeigt, zusammen mit den Monaten, in denen sie Saison haben.
	- In der kombinierten Ansicht wird zusätzlich angezeigt, aus welchem Kalender die Information stammt.
	- Die Tabelle ist dynamisch und passt sich der Auswahl an.

- **Export:**
	- Die angezeigte Tabelle kann als Excel-Datei gespeichert werden. So kann der Nutzer die Saisonzeiten ausdrucken oder weiterverarbeiten.

- **Weitere Funktionen:**
	- Über einen Button kann das Hauptmenü wieder in den Vordergrund geholt werden.

---

---

## 6. Weitere Dateien und Ordner

- **settings.json:** Speichert die Einstellungen für Theme und Vollbildmodus.
- **Filter/**: Enthält die Excel-Tabellen für den Import-Vergleich.
- **Quellen/**: Enthält Quellenangaben, Rohdaten und weitere Excel-Dateien.
- **Saisonklaender/**: Enthält die Python-Dateien mit den Saisonkalenderdaten.
- **legacy/**: Alte Versionen von Programmen, die nicht mehr aktiv genutzt werden.

---

## 7. Technische Hinweise

- Die Programme sind modular aufgebaut und können unabhängig voneinander gestartet werden.
- Die Kommunikation zwischen den Fenstern erfolgt über Fenster-Titel und die Bibliothek `pywin32` (sofern installiert), um Fenster gezielt in den Vordergrund zu bringen.
- Für die grafische Oberfläche wird `ttkbootstrap` verwendet, das moderne Themes für Tkinter bereitstellt.
- Die Datenverarbeitung erfolgt überwiegend mit `pandas` und `openpyxl` (für Excel).

---


## 8. Installation und Voraussetzungen

- **Python-Version:** Python 3.10 oder neuer empfohlen
- **Benötigte Pakete:** `tkinter`, `ttkbootstrap`, `pandas`, `openpyxl`, `pywin32` (optional)

### Speicherorte der Excel-Listen und Daten

Damit die Programme korrekt funktionieren, müssen die Excel-Dateien an den folgenden Speicherorten liegen:

- **Für Rechner Import:**
	- Die Excel-Tabellen für den Vergleich liegen im Ordner:
		- `Gesunde Ernährung/Filter/`
		- Beispiel: `Gesunde Ernährung/Filter/Antonia_Filter.xlsx`

- **Für Rechner Nahrungsmittel in Nährstoffe:**
	- Die zentrale Nährstoffdatenbank muss liegen unter:
		- `Gesunde Ernährung/Quellen/Nährstoffe in X/lebensmittel-naehrstoffe.de/Gefilterte_Kategorien_zusammengefuegt.xlsx`

- **Für Gerichte / Rezepte:**
	- Die Rezepte-Datei muss liegen unter:
		- `Gesunde Ernährung/Quellen/Scraper/rezepte_gefiltert.xlsx`

- **Für Saisonkalender:**
	- Die Python-Dateien mit den Saisonkalenderdaten müssen liegen unter:
		- `Gesunde Ernährung/Code/Saisonklaender/`
		- Beispiel: `Gesunde Ernährung/Code/Saisonklaender/REWE_Saison_Kalender.py`

Bitte stelle sicher, dass die Verzeichnisse und Dateinamen exakt so vorhanden sind, da die Programme sonst die Daten nicht finden können.

---

## 9. Kontakt & Support

Bei Fragen oder Problemen wenden Sie sich bitte an den Entwickler oder konsultieren Sie die README/Quellen im Projektordner.
