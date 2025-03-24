# Venviro - Datenvisualisierungstool

Venviro ist eine interaktive Webanwendung zur Datenvisualisierung, die es ermöglicht, JSON-Datendateien hochzuladen und verschiedene Arten von Diagrammen zu erstellen, anzupassen und zu exportieren.

## Funktionen

- **Unterstützte Diagrammtypen**: 
  - Gestapeltes Prozent-Balkendiagramm 
  - Horizontales Balkendiagramm
  - Kreisdiagramm

- **Anpassungsoptionen**:
  - Titel und Achsenbeschriftungen
  - Farbschemata (Standard, Blau, Rot, Grün, Spektrum)
  - Kategoriefilterung

- **Export-Funktionen**:
  - Mehrere Dateiformate (PNG, JPG, PDF, SVG)
  - Anpassbare Auflösung
  - Dateiname und Zeitstempel-Optionen
  - Direkter Download oder lokaler Export

## Installation
1. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

## Verwendung

1. Starten Sie die Anwendung (mit aktiviertem venv):
   ```
   python main.py
   ```

2. Öffnen Sie einen Webbrowser und navigieren Sie zu:
   ```
   http://127.0.0.1:7860
   ```

3. Laden Sie eine JSON-Datei mit dem folgenden Format hoch oder verwenden Sie die Beispiele im 'test/'-Verzeichnis:
   ```json
   {
     "title": "Diagrammtitel",
     "category_names": ["Kategorie1", "Kategorie2", "Kategorie3"],
     "results": {
       "Gruppe1": [10, 20, 30],
       "Gruppe2": [15, 25, 35]
     },
     "filename": "export_name"
   }
   ```

## Projektstruktur

```
enviro/
├── backend/
│   ├── __init__.py
│   ├── plot_abs.py       # Abstrakte Basisklasse für Diagramme
│   └── plot_classes.py   # Implementierungen der verschiedenen Diagrammtypen
├── frontend/
│   ├── __init__.py
│   └── gui_enhanced.py   # Gradio-Benutzeroberfläche
├── exports/              # Speicherort für exportierte Diagramme
├── test/                 # Testdateien mit JSON-Beispieldaten
├── main.py               # Startpunkt der Anwendung
├── requirements.txt      # Abhängigkeitsliste
└── README.md             # Diese Datei
```

## Anforderungen

- Python 3.10.11
- siehe: requirements.txt

## Entwickler

Entwickelt von:
- Pepaj Artiol
- Simader Florian

## Lizenz

Copyright © 2025 Venviro
