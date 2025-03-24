import matplotlib.pyplot as plt
import numpy as np
from backend.plot_abs import AbstractPlot


class BarChart(AbstractPlot):
    """
    Implementierung eines gestapelten Prozent-Balkendiagramms.
    Zeigt die prozentuale Verteilung der Kategorien pro Gruppe.
    """
    def __init__(self, title, category_names, results, filename, color=None, cmap=None):
        """
        Initialisiert das Balkendiagramm mit den übergebenen Parametern.
        
        Parameter:
        ----------
        title : str
            Titel des Diagramms
        category_names : list
            Namen der Kategorien/Segmente
        results : dict
            Dictionary mit den Datenreihen als Listen
        filename : str
            Name der Ausgabedatei
        color : str, optional
            Einzelne Farbe für das Diagramm
        cmap : str, optional
            Name einer Matplotlib-Farbpalette
        """
        super().__init__(results, category_names, title, filename, color, cmap)

    def plot(self):
        """
        Erstellt ein gestapeltes Prozent-Balkendiagramm.
        
        Returns:
        --------
        tuple
            (fig, ax) Matplotlib-Figur und Achsenobjekt
        """
        labels = list(self.results.keys())
        data = np.array(list(self.results.values()))

        # Berechne Prozentanteile und kumulative Summen für Stapelung
        data_percent = data / data.sum(axis=1, keepdims=True) * 100
        data_cum = data_percent.cumsum(axis=1)
        
        # Bestimme die Anzahl der Kategorien direkt
        num_categories = len(self.category_names)
        
        # Verwende die übergebene Farbe oder Farbpalette, wenn angegeben
        if self.cmap:
            category_colors = plt.colormaps[self.cmap](
                np.linspace(0.15, 0.85, num_categories))
        elif self.color:
            # Für Balkendiagramme brauchen wir verschiedene Abstufungen einer Farbe
            import matplotlib.colors as mcolors
            base_color = mcolors.to_rgb(self.color)
            # Erzeuge Farbtöne von hell (links) nach dunkel (rechts)
            category_colors = [mcolors.to_rgba(mcolors.rgb2hex([
                min(1.0, c * (0.5 + 1.0 * i/num_categories)) for c in base_color
            ])) for i in range(num_categories)]
        else:
            # Standardfarbschema wenn nichts angegeben
            category_colors = plt.colormaps['RdYlGn_r'](
                np.linspace(0.15, 0.85, num_categories))

        fig, ax = plt.subplots(figsize=(9.4, 5))
        ax.set_title(self.title, pad=30)
        ax.invert_yaxis()
        
        # X-Achse sichtbar machen, aber keine Tick-Labels anzeigen
        ax.xaxis.set_visible(True)
        ax.set_xticklabels([])  # Keine Tick-Labels
        ax.set_xlim(0, 100)

        # Zeichne die Balken für jede Kategorie
        for i, (colname, color) in enumerate(zip(self.category_names, category_colors)):
            widths = data_percent[:, i]
            starts = data_cum[:, i] - widths
            rects = ax.barh(labels, widths, left=starts, height=0.7, 
                           label=colname, color=color)

            # Farbe des Texts bestimmen - Bei dunklen Hintergründen weißen Text verwenden
            if isinstance(color, str):
                text_color = 'black'  # Standard für benannte Farben
            else:
                r, g, b, _ = color
                text_color = 'white' if (r * 0.299 + g * 0.587 + b * 0.114) < 0.5 else 'black'
                
            # Beschriftung der Balken mit Wert und Prozentsatz
            ax.bar_label(rects, label_type='center', color=text_color,
                         labels=[f'{y} \n{x:.0f}%' for x, y in zip(widths, data[:, i])])

        # Legende über dem Diagramm positionieren
        ax.legend(ncols=len(self.category_names), 
                 bbox_to_anchor=(0, 1.005), 
                 loc='lower left', 
                 fontsize='small')
        
        # Y-Achse-Beschriftung default
        # ax.set_ylabel("Kategorien")
        
        return fig, ax


class HorizontalBarChart(AbstractPlot):
    """
    Implementierung eines horizontalen Balkendiagramms.
    Zeigt absolute Werte pro Kategorie.
    """
    def __init__(self, title, category_names, results, filename, color=None, cmap=None):
        """
        Initialisiert das horizontale Balkendiagramm mit den übergebenen Parametern.
        
        Parameter entsprechen denen der Basisklasse AbstractPlot.
        """
        super().__init__(results, category_names, title, filename, color, cmap)

    def plot(self):
        """
        Erstellt ein horizontales Balkendiagramm.
        
        Returns:
        --------
        tuple
            (fig, ax) Matplotlib-Figur und Achsenobjekt
        """
        data = np.array(list(self.results.values()))
        
        # Sichere Bestimmung der Anzahl der Kategorien
        num_categories = len(self.category_names)
        
        # Farbkonfiguration
        if self.cmap:
            category_colors = plt.colormaps[self.cmap](
                np.linspace(0.15, 0.85, num_categories))[::-1]
        elif self.color:
            category_colors = [self.color] * num_categories
        else:
            category_colors = plt.colormaps['RdYlGn_r'](
                np.linspace(0.15, 0.85, num_categories))[::-1]

        # Gesamt-Datensumme für Prozentberechnung
        total = np.sum(data)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title(self.title, pad=30)

        # Parameter für die Balken
        bar_height = 0.5
        y_pos = np.arange(len(self.category_names))
        
        # Verwende die erste (oder einzige) Farbe aus category_colors
        bar_color = category_colors[0] if isinstance(category_colors, list) else category_colors
        
        # Stelle sicher, dass data[0] ein Array ist, wenn data flach ist
        if data.ndim == 1:
            bars = ax.barh(y_pos, data, height=bar_height, label='Results', color=bar_color)
            # Für die Textanzeige brauchen wir Einzelwerte
            values = data
        else:
            bars = ax.barh(y_pos, data[0], height=bar_height, label='Results', color=bar_color)
            # Für die Textanzeige brauchen wir Einzelwerte
            values = data[0]

        # Default-Achsenbeschriftungen
        ax.set_xlabel('Anzahl')
        ax.set_ylabel('Kategorien')
        
        # Y-Achsen-Beschriftung mit Kategorienamen
        ax.set_yticks(y_pos)
        ax.set_yticklabels(self.category_names)
        # Dynamische X-Achsen-Ticks berechnen
        ax.set_xticks(np.linspace(0, max(values) * 1.1, 6).astype(int))

        # Beschriftung der Balken mit Wert und Prozent
        for i, bar in enumerate(bars):
            absolute_value = bar.get_width()
            percentage = (absolute_value / total) * 100 if total > 0 else 0

            # Positioniere Text innerhalb oder neben dem Balken
            x_position = absolute_value * 0.05 if absolute_value > 0 else 0.1
            ha_value = 'left'

            ax.text(x_position, bar.get_y() + bar.get_height() / 2,
                    f'{absolute_value} \n{percentage:.0f}%', 
                    va='center', ha=ha_value, fontsize=10, color='black')

        return fig, ax


class PieChart(AbstractPlot):
    """
    Implementierung eines Kreisdiagramms (Donut-Stil).
    Zeigt die proportionale Verteilung der Kategorien.
    """
    def __init__(self, title, labels, values, filename, color=None, cmap=None):
        """
        Initialisiert das Kreisdiagramm mit den übergebenen Parametern.
        
        Parameter:
        ----------
        title : str
            Titel des Diagramms
        labels : list
            Liste der Kategorienamen
        values : list
            Liste der zugehörigen Werte
        filename : str
            Name der Ausgabedatei
        color : str, optional
            Einzelne Farbe für das Diagramm
        cmap : str, optional
            Name einer Matplotlib-Farbpalette
        """
        super().__init__(results={'values': values}, category_names=labels, 
                        title=title, filename=filename, color=color, cmap=cmap)
        self.labels = labels
        self.values = values

    def plot(self):
        """
        Erstellt ein Kreisdiagramm im Donut-Stil.
        
        Returns:
        --------
        tuple
            (fig, ax) Matplotlib-Figur und Achsenobjekt
        """
        # Summe der Werte für Prozentberechnung
        val_sum = sum(self.values)
        
        # Sichere Bestimmung der Anzahl der Labels
        num_labels = len(self.labels)
        
        # Farbkonfiguration
        if self.cmap:
            colors = plt.colormaps[self.cmap](
                np.linspace(0.15, 0.85, num_labels))[::-1]
        elif self.color:
            # Für Kreisdiagramme - Verwende die gleiche Farbabstufung wie beim BarChart
            import matplotlib.colors as mcolors
            base_color = mcolors.to_rgb(self.color)
            # Erzeuge Farbtöne mit der gleichen Formel wie beim BarChart
            colors = [mcolors.to_rgba(mcolors.rgb2hex([
                min(1.0, c * (0.5 + 1.0 * i/num_labels)) for c in base_color
            ])) for i in range(num_labels)]
            colors = np.array(colors)  # Konvertiere zu numpy Array für Konsistenz
        else:
            colors = plt.colormaps['RdYlGn_r'](
                np.linspace(0.15, 0.85, num_labels))[::-1]

        fig = plt.figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(1, 1, 1)

        # Etiketten und Werte kopieren, da wir sie verändern werden
        pie_labels = self.labels.copy()
        pie_values = self.values.copy()
        
        # Leeres Zentrum hinzufügen für Donut-Stil
        pie_labels.append("")
        pie_values.append(sum(pie_values))
        
        # Füge eine weiße Farbe für das Zentrum hinzu
        if len(colors.shape) > 1:
            # Wenn colors bereits ein 2D-Array ist (RGBA-Werte)
            colors_with_white = np.vstack([colors, [1, 1, 1, 1]])
        else:
            # Wenn colors eine Liste von benannten Farben ist
            colors_with_white = list(colors) + ['white']

        # Diagramm erstellen
        wedges, texts, autotexts = ax.pie(
            pie_values, labels=None, colors=colors_with_white,
            wedgeprops={'width': 0.3, 'edgecolor': 'white'},
            autopct='%1.0f%%', startangle=0, pctdistance=0.85
        )

        # Beschriftung der Segmente anpassen
        for id, text in enumerate(autotexts):
            if text.get_text() == '50.0%':
                # Mittleres weißes Segment nicht beschriften
                text.set_text('')
            else:
                # Wert und Prozentsatz anzeigen
                text.set_text(f"{pie_values[id]} \n{int(round(pie_values[id] / val_sum * 100, 0))}%")
                text.set_color('black')

        # Weißer Kreis in der Mitte für Donut-Effekt
        ax.add_artist(plt.Circle((0, 0), 0.6, color='white'))
        ax.set_aspect('equal')
        ax.set_ylim(0, 1)
        ax.set_title(self.title, pad=20)
        
        # Labels entfernen, da sie bei Kreisdiagrammen nicht sinnvoll sind
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Legende hinzufügen, aber ohne das leere Zentrum
        if len(wedges) > 1:
            ax.legend(
                wedges[:len(wedges)-1], 
                pie_labels[:len(pie_labels)-1], 
                loc="center"
            )
        
        return fig, ax


if __name__ == "__main__":
    # Test-Ausführung der Diagrammklassen
    
    # Test BarChart
    bar_chart = BarChart(
        title="Digitalisierung Unterrichtsmaterialien in Fach 1",
        category_names=['Vollständig digital', 'Überwiegend digital', 
                       'Überwiegend analog', 'Vollständig analog'],
        results={
            'derzeitiger Stand': [4, 7, 9, 2],
            'zukünftiger Stand': [7, 7, 6, 2],
        },
        filename="bar_chart.png"
    )
    bar_chart.plot()

    # Test HorizontalBarChart
    horizontal_bar_chart = HorizontalBarChart(
        title="Softwarenutzung in Fach 1",
        category_names=['CAD Software', 'Chat GPT', 'Citrix', 'MathCAD', 
                       'Moodle (E-Learning)', 'MS-Office Produkte', 
                       'MS-Teams', 'Sonstige Software'][::-1],
        results={"results": [5, 4, 1, 23, 9, 3, 2, 2][::-1]},
        filename="horizontal_bar_chart.png"
    )
    horizontal_bar_chart.plot()

    # Test PieChart
    pie_chart = PieChart(
        title="Digitale Tools in Fach 1",
        labels=["Ja", "Nein"][::-1],
        values=[21, 9][::-1],
        filename="pie_chart.png"
    )
    pie_chart.plot()
