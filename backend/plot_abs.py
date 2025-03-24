from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import numpy as np


class AbstractPlot(ABC):
    """
    Abstrakte Basisklasse für verschiedene Diagrammtypen.
    Definiert die grundlegende Struktur und benötigten Methoden für alle Diagrammarten.
    """
    def __init__(self, results, category_names, title, filename, color=None, cmap=None):
        """
        Initialisiert die gemeinsamen Eigenschaften aller Diagrammtypen.
        
        Parameter:
        ----------
        results : dict oder list
            Die darzustellenden Datenwerte
        category_names : list
            Die Namen der Kategorien/Beschriftungen
        title : str
            Der Titel des Diagramms
        filename : str
            Der Dateiname zum Speichern des Diagramms
        color : str, optional
            Eine einzelne Farbe für das Diagramm
        cmap : str, optional
            Name einer Farbpalette für das Diagramm
        """
        self.results = results
        self.category_names = category_names
        self.title = title
        self.filename = filename
        self.color = color  # Farbparameter für einzelne Farbe
        self.cmap = cmap    # Farbparameter für Farbpalette

    @abstractmethod
    def plot(self):
        """
        Abstrakte Methode zum Erstellen des Diagramms.
        Muss von allen abgeleiteten Klassen implementiert werden.
        
        Returns:
        --------
        tuple
            (fig, ax) Matplotlib-Figur und Achsenobjekt
        """
        pass
