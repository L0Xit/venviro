import gradio as gr
import json
from backend.plot_classes import BarChart, HorizontalBarChart, PieChart
import os
import time
from datetime import datetime, timedelta

def process_data(file):
    """
    Verarbeitet die hochgeladene JSON-Datei und extrahiert die Daten.
    
    Parameter:
    ----------
    file : FileObj
        Die hochgeladene Datei
        
    Returns:
    --------
    tuple
        (data, error_message) - Die geladenen Daten oder eine Fehlermeldung
    """
    if file is None:
        return None, "No file selected"
    with open(file.name, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data, None

def is_pie_chart_compatible(data):
    """
    Prüft, ob die Daten für ein Kreisdiagramm geeignet sind.
    
    Parameter:
    ----------
    data : dict
        Die zu prüfenden Daten aus der JSON-Datei
        
    Returns:
    --------
    bool
        True, wenn die Daten für ein Kreisdiagramm geeignet sind, sonst False
    """
    results = data['results']
    
    # Fall 1: results ist ein einfaches Array - OK für Pie Chart
    if isinstance(results, list):
        return True
        
    # Fall 2: results ist ein Dict mit genau einem 'results'-Schlüssel - OK für Pie Chart
    if isinstance(results, dict) and 'results' in results and isinstance(results['results'], list):
        return True
        
    # Fall 3: results ist ein Dict mit mehreren Arrays - NICHT geeignet für Pie Chart
    if isinstance(results, dict) and len(results) > 0:
        first_key = next(iter(results))
        if isinstance(results[first_key], list):
            return False
    
    # Im Zweifelsfall annehmen, dass es nicht kompatibel ist
    return False

def plot_data(data, plot_type, selected_categories=None, title_text=None, 
              x_label=None, y_label=None, color_scheme=None):
    """
    Erstellt ein Diagramm basierend auf den übergebenen Daten und Parametern.
    
    Parameter:
    ----------
    data : dict
        Die Diagrammdaten aus der JSON-Datei
    plot_type : str
        Der gewünschte Diagrammtyp ("Percented Bar Chart", "Horizontal Bar Chart", "Pie Chart")
    selected_categories : list, optional
        Die ausgewählten Kategorien für die Filterung
    title_text : str, optional
        Benutzerdefinierter Titel für das Diagramm
    x_label : str, optional
        Beschriftung für die X-Achse
    y_label : str, optional
        Beschriftung für die Y-Achse
    color_scheme : str, optional
        Ausgewähltes Farbschema ("Standard", "Blau", "Rot", "Grün", "Spektrum")
        
    Returns:
    --------
    tuple
        (fig, error_message) - Die erstellte Figure oder eine Fehlermeldung
    """
    # Basiswerte aus JSON
    original_title = data['title']
    category_names = data['category_names']
    results = data['results']
    filename = data.get('filename', 'plot.png')  # Standardwert, falls nicht vorhanden
    
    # Anpassen der Titel-Texte wenn angegeben
    title = title_text if title_text else original_title
    
    # Auswahl der Kategorien - verbesserte Methode für unterschiedliche Datenstrukturen
    if selected_categories and len(selected_categories) > 0:
        indices = [i for i, cat in enumerate(category_names) if cat in selected_categories]
        filtered_categories = [category_names[i] for i in indices]
        
        if isinstance(results, dict) and 'results' in results:
            # Fall 1: results = {'results': [...]}
            filtered_results = {'results': [results['results'][i] for i in indices]}
        elif isinstance(results, list):
            # Fall 2: results = [...]
            filtered_results = [results[i] for i in indices]
        elif isinstance(results, dict) and all(isinstance(results[key], list) for key in results):
            # Fall 3: results = {'key1': [...], 'key2': [...], ...}
            filtered_results = {}
            for key in results:
                if len(results[key]) == len(category_names):
                    filtered_results[key] = [results[key][i] for i in indices]
                else:
                    # Wenn die Längen nicht übereinstimmen, das Original behalten
                    filtered_results[key] = results[key]
        else:
            # Fallback wenn nichts anderes passt
            filtered_results = results
    else:
        filtered_categories = category_names
        filtered_results = results
    
    # Debug-Ausgabe
    # print(f"Filtered Categories: {filtered_categories}")
    # print(f"Filtered Results Type: {type(filtered_results)}")
    # print(f"Filtered Results: {filtered_results}")

    # Farbschema-Parameter festlegen
    color = None
    cmap = None
    if color_scheme and color_scheme != "Standard":
        if (color_scheme == "Blau"):
            color = '#1f77b4'
        elif (color_scheme == "Rot"):
            color = '#d62728'
        elif (color_scheme == "Grün"):
            color = '#2ca02c'
        elif (color_scheme == "Spektrum"):
            cmap = 'viridis'

    # # Debug-Ausgabe für Farbparameter
    # print(f"Using color: {color}")
    # print(f"Using cmap: {cmap}")

    # Spezielle Prüfung für Pie Chart
    if plot_type == "Pie Chart" and not is_pie_chart_compatible(data):
        return None, "Diese Daten sind nicht mit einem Pie Chart kompatibel. Bitte wählen Sie ein anderes Diagramm."

    # Standardisierung des Datenformats - stelle sicher, dass für BarChart ein Dictionary vorliegt
    if isinstance(filtered_results, list):
        # Wenn results eine Liste ist, in Dictionary konvertieren
        if plot_type == "Percented Bar Chart":
            filtered_results = {'Werte': filtered_results}  # Schlüssel 'Werte' als Dummy-Label

    try:
        if plot_type == "Percented Bar Chart":
            chart = BarChart(
                title=title,
                category_names=filtered_categories,
                results=filtered_results,
                filename=filename,
                color=color,
                cmap=cmap
            )
        elif plot_type == "Horizontal Bar Chart":
            # Umwandlung in das erwartete Format für HorizontalBarChart
            if isinstance(filtered_results, list):
                # Erstelle ein Dictionary mit den richtigen Schlüsseln für HorizontalBarChart
                formatted_results = {'results': filtered_results}
            else:
                formatted_results = filtered_results
                
            chart = HorizontalBarChart(
                title=title,
                category_names=filtered_categories,
                results=formatted_results,
                filename=filename,
                color=color,
                cmap=cmap
            )
        elif plot_type == "Pie Chart":
            try:
                if isinstance(filtered_results, dict) and 'results' in filtered_results:
                    chart = PieChart(
                        title=title,
                        labels=filtered_categories,
                        values=filtered_results['results'],
                        filename=filename,
                        color=color,
                        cmap=cmap
                    )
                else:
                    chart = PieChart(
                        title=title,
                        labels=filtered_categories,
                        values=filtered_results,
                        filename=filename,
                        color=color,
                        cmap=cmap
                    )
            except (KeyError, IndexError, TypeError) as e:
                return None, f"Pie Chart error: Daten nicht kompatibel. Bitte wählen Sie ein anderes Diagramm. Details: {str(e)}"
        else:
            return None, "Invalid plot type"

        fig, ax = chart.plot()
        
        # Achsenbeschriftungen setzen, wenn angegeben - mit stärkerer Formatierung
        if x_label:
            ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
            
        if y_label:
            # Zuerst eventuell vorhandene Y-Achsenbeschriftung entfernen
            ax.set_ylabel('')
            # Dann neue Beschriftung setzen
            ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        
    except Exception as e:
        # import traceback # ---> lazy import
        # traceback.print_exc()  # Druckt den vollständigen Stacktrace aus
        return None, f"Error beim Erstellen des Plots: {str(e)}"
    
    return fig, None

def save_plot_as_image(fig, format="png", dpi=300, custom_name=None):
    """
    Speichert den Plot als Bilddatei im gewünschten Format im exports-Ordner.
    
    Parameter:
    ----------
    fig : matplotlib.figure.Figure
        Das zu speichernde Diagramm
    format : str
        Das gewünschte Ausgabeformat (png, jpg, pdf, svg)
    dpi : int
        Die Auflösung in Dots Per Inch
    custom_name : str, optional
        Ein benutzerdefinierter Dateiname
        
    Returns:
    --------
    str or None
        Der Pfad zur gespeicherten Datei oder None bei Fehler
    """
    if fig is not None:
        # Verwende den benutzerdefinierten Namen oder den Standardnamen
        prefix = custom_name or "plot"
        filename = f"{prefix}.{format}"
        
        # Erstelle den Exportordner im Projekthauptverzeichnis (ein Verzeichnis höher als frontend)
        export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        # Speichere die Datei direkt im Exportordner mit absolutem Pfad
        export_path = os.path.abspath(os.path.join(export_dir, filename))
        fig.savefig(export_path, format=format, dpi=dpi, bbox_inches="tight")
        
        # Überprüfe, ob die Datei erstellt wurde
        if os.path.exists(export_path):
            # print(f"Plot erfolgreich gespeichert in: {export_path}")
            return export_path
        else:
            # print(f"FEHLER: Datei wurde nicht erstellt: {export_path}")
            return None
    return None

def clean_export_dir(max_age_days=7):
    """
    Löscht Dateien im export-Ordner, die älter als max_age_days sind.
    
    Parameter:
    ----------
    max_age_days : int
        Maximales Alter der Dateien in Tagen
        
    Returns:
    --------
    int
        Anzahl der gelöschten Dateien
    """
    # Exportordner im Projekthauptverzeichnis (ein Verzeichnis höher als frontend)
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
    if not os.path.exists(export_dir):
        return 0
    
    # Aktuelles Datum
    now = datetime.now()
    threshold_date = now - timedelta(days=max_age_days)
    deleted_count = 0
    
    # Durchsuche alle Dateien im exports-Ordner
    for filename in os.listdir(export_dir):
        file_path = os.path.join(export_dir, filename)
        if os.path.isfile(file_path):
            # Prüfe das Erstellungsdatum der Datei
            file_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if file_time < threshold_date:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    # print(f"Alte Datei gelöscht: {file_path}")
                except Exception as e:
                    # Debug, kommt nicht vor wenn Berechtigungen korrekt sind
                    print(f"Fehler beim Löschen von {file_path}: {str(e)}")
    
    return deleted_count

def delete_all_exports():
    """
    Löscht alle Dateien im exports-Ordner.
    
    Returns:
    --------
    int
        Anzahl der gelöschten Dateien
    """
    # Exportordner im Projekthauptverzeichnis (ein Verzeichnis höher als frontend)
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
    if not os.path.exists(export_dir):
        return 0
    
    deleted_count = 0
    for filename in os.listdir(export_dir):
        file_path = os.path.join(export_dir, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                # Debug, kommt nicht vor wenn Berechtigungen korrekt sind
                print(f"Fehler beim Löschen von {file_path}: {str(e)}")
    
    return deleted_count

with gr.Blocks(theme=gr.themes.Base()) as interface:
    gr.Markdown("# Erweiterte Datenvisualisierung mit Gradio --- Venviro Production ©")
    gr.Markdown("Laden Sie eine JSON-Datei hoch, wählen Sie die Visualisierungsoptionen und exportieren Sie die Ergebnisse. 📊🚀")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Datei-Upload und Diagrammtyp
            file_input = gr.File(label="JSON-Datei hochladen", type="filepath")
            plot_type = gr.Radio(
                choices=["Percented Bar Chart", "Horizontal Bar Chart", "Pie Chart"], 
                label="Diagrammtyp",
                value="Percented Bar Chart"  # Standardwert
            )
            
            # Kategorie-Auswahl (wird dynamisch befüllt)
            category_checklist = gr.CheckboxGroup(
                choices=[], 
                label="Kategorien auswählen (leer = alle)", 
                interactive=True
            )
            
            with gr.Accordion("Styling-Optionen", open=False):
                title_input = gr.Textbox(label="Titel (leer = Standard)")
                x_label = gr.Textbox(label="X-Achsenbeschriftung")
                y_label = gr.Textbox(label="Y-Achsenbeschriftung")
                color_scheme = gr.Radio(
                    choices=["Standard", "Blau", "Rot", "Grün", "Spektrum"],
                    label="Farbschema",
                    value="Standard"
                )
            
            with gr.Accordion("Export-Optionen", open=False):
                export_format = gr.Radio(
                    choices=["png", "jpg", "pdf", "svg"],
                    label="Dateiformat",
                    value="png"
                )
                export_dpi = gr.Slider(
                    minimum=72, maximum=600, value=300, step=1,
                    label="Auflösung (DPI)"
                )
                
                # Neues Feld für benutzerdefinierten Dateinamen
                output_filename = gr.Textbox(
                    label="Dateiname (ohne Erweiterung, leer = automatisch generieren)",
                    placeholder="z.B. mein_diagramm"
                )
                
                # Checkbox für Timestamp hinzufügen
                add_timestamp = gr.Checkbox(
                    label="Zeitstempel zum Dateinamen hinzufügen",
                    value=True
                )
                
                # Zwei Export-Buttons statt einem
                gr.Row([
                    export_button := gr.Button("In Ordner exportieren", variant="primary"),
                    download_button := gr.Button("Als Datei herunterladen", variant="secondary")
                ])
                
                export_info = gr.Markdown("""
                **Hinweis zum Export:**
                - "In Ordner exportieren" speichert die Datei lokal im 'exports' Ordner
                - "Als Datei herunterladen" ermöglicht den direkten Download im Browser
                """)
                
                # Füge Funktionen zur Reinigung des export-Ordners hinzu
                gr.Markdown("### Export-Ordner verwalten")
                
                with gr.Row():
                    cleanup_button = gr.Button("Alte Exports löschen (>7 Tage)", variant="secondary")
                    delete_all_button = gr.Button("Alle Exports löschen", variant="stop")
                
                cleanup_info = gr.Markdown(visible=False)
        
        with gr.Column(scale=2):
            # Ausgabe
            output_plot = gr.Plot(label="Visualisierung")
            message = gr.Markdown(visible=True)  # Immer sichtbar, um Platz zu reservieren
            
            # Entferne den problematischen Download-Button und ersetze ihn durch einen Hinweis
            export_success_info = gr.Markdown(visible=False)
            
            # Download-Output für direkten Download
            download_output = gr.File(label="⬇️ HIER KLICKEN ZUM HERUNTERLADEN", visible=False)

    def load_categories(file):
        """
        Lädt die Kategorien aus der JSON-Datei und aktualisiert die Auswahlbox.
        
        Parameter:
        ----------
        file : FileObj
            Die hochgeladene Datei
            
        Returns:
        --------
        gr.update
            Update-Objekt für die Kategorie-Auswahl mit den geladenen Optionen
        """
        if file is None:
            # Keine Datei vorhanden - zurücksetzen der Kategorien und unsichtbar machen
            return gr.update(choices=[], value=[], visible=False)
        
        try:
            data, error = process_data(file)
            if error:
                return gr.update(choices=[], value=[], visible=False)
            
            category_names = data['category_names']
            # Sofort den Plot mit allen Kategorien erstellen
            return gr.update(choices=category_names, value=[], visible=True)
        except Exception as e:
            # print(f"Fehler beim Laden der Kategorien: {str(e)}")
            return gr.update(choices=[], value=[], visible=False)
    
    def update_plot(file, plot_type, selected_categories, title_text, x_label, y_label, color_scheme):
        """
        Aktualisiert das Diagramm basierend auf den ausgewählten Parametern.
        
        Parameter:
        ----------
        file : FileObj
            Die hochgeladene Datei
        plot_type : str
            Der gewählte Diagrammtyp
        selected_categories : list
            Die ausgewählten Kategorien
        title_text : str
            Benutzerdefinierter Titel
        x_label : str
            X-Achsenbeschriftung
        y_label : str
            Y-Achsenbeschriftung
        color_scheme : str
            Ausgewähltes Farbschema
            
        Returns:
        --------
        tuple
            (fig, message_update, download_update) - Die Figur und UI-Updates
        """
        if file is None:
            # Wenn keine Datei ausgewählt ist, Plots und Downloads zurücksetzen
            return None, gr.update(value="**Info:** Bitte eine JSON-Datei hochladen", visible=True), None
        
        try:
            data, error_message = process_data(file)
            if error_message:
                return None, gr.update(value=f"**Error:** {error_message}", visible=True), None
            
            fig, error_message = plot_data(
                data, plot_type, selected_categories, title_text, x_label, y_label, color_scheme
            )
            
            if error_message:
                return None, gr.update(value=f"**Error:** {error_message}", visible=True), None
            
            return fig, gr.update(value="Plot erfolgreich generiert!", visible=True), None
        except Exception as e:
            return None, gr.update(value=f"**Error:** {str(e)}", visible=True), None
    
    def export_plot(file, plot_type, selected_categories, title_text, x_label, y_label, color_scheme, export_format, export_dpi, output_filename, add_timestamp):
        """
        Exportiert das Diagramm im gewünschten Format in den exports-Ordner.
        
        Parameter:
        ----------
        file : FileObj
            Die hochgeladene Datei
        plot_type : str
            Der gewählte Diagrammtyp
        selected_categories : list
            Die ausgewählten Kategorien
        title_text : str
            Benutzerdefinierter Titel
        x_label : str
            X-Achsenbeschriftung
        y_label : str
            Y-Achsenbeschriftung
        color_scheme : str
            Ausgewähltes Farbschema
        export_format : str
            Das gewünschte Dateiformat (png, jpg, pdf, svg)
        export_dpi : int
            Die Auflösung in DPI
        output_filename : str
            Der benutzerdefinierte Dateiname
        add_timestamp : bool
            Flag zum Hinzufügen eines Zeitstempels zum Dateinamen
            
        Returns:
        --------
        gr.update
            Update-Objekt für die Erfolgs-/Fehlermeldung
        """
        if file is None:
            return gr.update(value="**⚠️ Fehler:** Keine Datei ausgewählt", visible=True)
        
        try:
            data, error_message = process_data(file)
            if error_message:
                return gr.update(value=f"**⚠️ Fehler:** {error_message}", visible=True)
            
            fig, error_message = plot_data(
                data, plot_type, selected_categories, title_text, x_label, y_label, color_scheme
            )
            
            if error_message:
                return gr.update(value=f"**⚠️ Fehler:** {error_message}", visible=True)
            
            # Dateinamen für den Export bestimmen
            timestamp = time.strftime("%Y%m%d_%H%M%S") if add_timestamp else ""
            
            # Wenn kein benutzerdefinierter Name angegeben wird, verwende den Basisnamen aus dem Original
            if not output_filename:
                original_filename = data.get('filename', 'plot')
                base_name = os.path.splitext(original_filename)[0]
            else:
                base_name = output_filename
                
            # Timestamp hinzufügen, wenn aktiviert
            if timestamp:
                filename = f"{base_name}_{timestamp}.{export_format}"
            else:
                filename = f"{base_name}.{export_format}"
            
            # Erstelle den Export-Pfad
            export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, filename)
            
            # Speichere die Figur
            fig.savefig(export_path, format=export_format, dpi=export_dpi, bbox_inches="tight")
            
            if os.path.exists(export_path):
                return gr.update(
                    value=f"""
                    **✅ Export erfolgreich!**
                    
                    Die Datei wurde gespeichert als: 
                    **{filename}**
                    
                    Vollständiger Pfad:
                    `{export_path}`
                    
                    Sie finden alle exportierten Dateien im Ordner 'exports'.
                    """, 
                    visible=True
                )
            else:
                return gr.update(value="**⚠️ Fehler:** Export fehlgeschlagen", visible=True)
        except Exception as e:
            # import traceback # ---> lazy import
            # traceback.print_exc()
            return gr.update(value=f"**⚠️ Fehler:** {str(e)}", visible=True)
    
    def export_for_download(file, plot_type, selected_categories, title_text, x_label, y_label, color_scheme, export_format, export_dpi, output_filename, add_timestamp):
        """
        Exportiert das Diagramm für den direkten Download im Browser.
        
        Parameter:
        ----------
        file : FileObj
            Die hochgeladene Datei
        plot_type : str
            Der gewählte Diagrammtyp
        selected_categories : list
            Die ausgewählten Kategorien
        title_text : str
            Benutzerdefinierter Titel
        x_label : str
            X-Achsenbeschriftung
        y_label : str
            Y-Achsenbeschriftung
        color_scheme : str
            Ausgewähltes Farbschema
        export_format : str
            Das gewünschte Dateiformat (png, jpg, pdf, svg)
        export_dpi : int
            Die Auflösung in DPI
        output_filename : str
            Der benutzerdefinierte Dateiname
        add_timestamp : bool
            Flag zum Hinzufügen eines Zeitstempels zum Dateinamen
            
        Returns:
        --------
        tuple
            (download_update, message_update) - Update-Objekte für den Download und die Nachricht
        """
        if file is None:
            return None, gr.update(value="**⚠️ Fehler:** Keine Datei ausgewählt", visible=True)
        
        try:
            data, error_message = process_data(file)
            if error_message:
                return None, gr.update(value=f"**⚠️ Fehler:** {error_message}", visible=True)
            
            fig, error_message = plot_data(
                data, plot_type, selected_categories, title_text, x_label, y_label, color_scheme
            )
            
            if error_message:
                return None, gr.update(value=f"**⚠️ Fehler:** {error_message}", visible=True)
            
            # Dateinamen für den Export bestimmen
            timestamp = time.strftime("%Y%m%d_%H%M%S") if add_timestamp else ""
            
            # Wenn kein benutzerdefinierter Name angegeben wird, verwende den Basisnamen aus dem Original
            if not output_filename:
                original_filename = data.get('filename', 'plot')
                base_name = os.path.splitext(original_filename)[0]
            else:
                base_name = output_filename
                
            # Timestamp hinzufügen, wenn aktiviert
            if timestamp:
                filename = f"{base_name}_{timestamp}.{export_format}"
            else:
                filename = f"{base_name}.{export_format}"
            
            # Erstelle den Export-Pfad
            export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, filename)
            
            # Speichere die Figur
            fig.savefig(export_path, format=export_format, dpi=export_dpi, bbox_inches="tight")
            
            #! Wichtig: wir nehmen an, dass die Datei erfolgreich gespeichert wurde
            # print(f"Download-Datei erstellt in: {export_path}")
            
            # Rückgabe für Download
            return gr.update(value=export_path, visible=True), gr.update(
                value=f"""
                **✅ Download bereit!**
                
                Die Datei wurde als **{filename}** gespeichert und ist zum Download bereit.
                Sie finden die Datei auch direkt im 'exports'-Ordner.
                
                Klicken Sie auf den Dateinamen unten zum Herunterladen.
                """, 
                visible=True
            )
                
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            return None, gr.update(value=f"**⚠️ Fehler:** {str(e)}", visible=True)

    def cleanup_exports():
        """
        Löscht alte Export-Dateien, die älter als 7 Tage sind.
        
        Returns:
        --------
        gr.update
            Update-Objekt für die Statusmeldung mit Anzahl der gelöschten Dateien
        """
        deleted = clean_export_dir(max_age_days=7)
        if deleted > 0:
            return gr.update(value=f"**✅ Aufgeräumt!** {deleted} alte Dateien wurden gelöscht.", visible=True)
        else:
            return gr.update(value="**ℹ️ Info:** Es wurden keine alten Dateien gefunden.", visible=True)
    
    def clear_exports():
        """
        Löscht alle Dateien im Export-Ordner sofort.
        
        Returns:
        --------
        gr.update
            Update-Objekt für die Statusmeldung mit Anzahl der gelöschten Dateien
        """
        deleted = delete_all_exports()
        if deleted > 0:
            return gr.update(value=f"**✅ Erledigt!** Alle {deleted} Dateien wurden aus dem Export-Ordner gelöscht.", visible=True)
        else:
            return gr.update(value="**ℹ️ Info:** Der Export-Ordner ist bereits leer.", visible=True)

    # Event-Handler
    file_input.change(
        fn=load_categories,
        inputs=[file_input],
        outputs=[category_checklist]
    )
    
    # Entferne den automatischen Plot-Generator beim Datei-Upload
    # und ersetze ihn durch eine einfache Willkommensnachricht
    def show_welcome_message(file):
        """Zeigt eine Willkommensnachricht nach dem Datei-Upload an"""
        if file is None:
            return gr.update(value="**Info:** Bitte eine JSON-Datei hochladen", visible=True)
        return gr.update(
            value="**✅ Datei geladen!** Bitte wählen Sie einen Diagrammtyp oder passen Sie die Parameter an.", 
            visible=True
        )
    
    file_input.change(
        fn=show_welcome_message,
        inputs=[file_input],
        outputs=[message]
    )
    
    # Rest der Event-Handler bleibt unverändert
    # Plot aktualisieren bei Änderungen der Eingaben
    inputs = [file_input, plot_type, category_checklist, title_input, x_label, y_label, color_scheme]
    
    plot_type.change(
        fn=update_plot,
        inputs=inputs,
        outputs=[output_plot, message]
    )
    
    category_checklist.change(
        fn=update_plot,
        inputs=inputs,
        outputs=[output_plot, message]
    )
    
    # Weitere Änderungen (Titel, Labels, etc.)
    for component in [title_input, x_label, y_label, color_scheme]:
        component.change(
            fn=update_plot,
            inputs=inputs,
            outputs=[output_plot, message]
        )
    
    # Export-Button für lokales Speichern
    export_button.click(
        fn=export_plot,
        inputs=inputs + [export_format, export_dpi, output_filename, add_timestamp],
        outputs=[export_success_info]
    )
    
    # Neuer Download-Button für Direktdownload
    download_button.click(
        fn=export_for_download,
        inputs=inputs + [export_format, export_dpi, output_filename, add_timestamp],
        outputs=[download_output, message]
    )
    
    # Funktionen zum Aufräumen des Export-Ordners
    cleanup_button.click(fn=cleanup_exports, outputs=[cleanup_info])
    delete_all_button.click(fn=clear_exports, outputs=[cleanup_info])
    
    # Beim Starten der App automatisch aufräumen
    clean_export_dir(max_age_days=30)  # Lösche Dateien, die älter als 30 Tage sind

# launch()-Aufruf erfolgt in main.py
if __name__ == "__main__":
    interface.launch()

