"""
Haupteinstiegspunkt für die Datenvisualisierungsanwendung.
Startet die Gradio-Weboberfläche.
"""

from frontend.gui import interface

if __name__ == "__main__":
    # Starte die Weboberfläche
    interface.launch()
