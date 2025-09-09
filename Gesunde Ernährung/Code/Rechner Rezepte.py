import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

import os
import json
import ttkbootstrap as tb
import webbrowser
import sys
try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

# Excel-Datei Pfad (angepasst)
REZEPTE_DATEI = Path(__file__).parent.parent / 'Quellen' / 'Scraper' / 'rezepte_gefiltert.xlsx'

# Daten laden
try:
    df_rezepte = pd.read_excel(REZEPTE_DATEI)
except Exception as e:
    df_rezepte = None
    print(f"Fehler beim Laden der Datei: {e}")

# Rezeptnamen extrahieren
if df_rezepte is not None:
    rezeptnamen = df_rezepte['Rezeptname'].dropna().unique().tolist()
else:
    rezeptnamen = []



# --- Einstellungen und Theme-Auswahl wie im Hauptmenü ---
settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
dark_mode = False
fullscreen = False
themename = "flatly"
available_themes = [
    "flatly", "darkly", "cyborg", "journal", "solar", "vapor", "morph", "superhero"
]
if os.path.exists(settings_path):
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            dark_mode = settings.get('dark_mode', False)
            fullscreen = settings.get('fullscreen', False)
            themename = settings.get('themename', "darkly" if dark_mode else "flatly")
            if themename not in available_themes:
                themename = "darkly" if dark_mode else "flatly"
    except Exception:
        pass


try:
    root = tb.Window(themename=themename)
except Exception:
    root = tk.Tk()
root.title('Rezept-Zutaten-Anzeige')
if fullscreen:
    root.attributes('-fullscreen', True)

# Make window and grid scale dynamically
root.grid_rowconfigure(1, weight=1)  # Zutatenliste row
root.grid_rowconfigure(2, weight=0)  # Button row
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=0)

# Dropdown für Rezepte mit eigener Such-/Filterfunktion
label_rezept = tk.Label(root, text="Rezept auswählen:")
label_rezept.grid(row=0, column=0, padx=10, pady=10, sticky="w")

entry_var = tk.StringVar()
combo_rezepte = ttk.Combobox(root, textvariable=entry_var, values=rezeptnamen, state="normal")
combo_rezepte.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

def filter_rezepte(event=None):
    eingabe = entry_var.get().lower()
    filtered = [r for r in rezeptnamen if eingabe in r.lower()]
    combo_rezepte['values'] = filtered
    # Optional: Dropdown öffnen, wenn gefiltert wird
    if filtered:
        combo_rezepte.event_generate('<Down>')
    # Fokus und Cursor ans Ende setzen, damit man weiterschreiben kann
    combo_rezepte.focus_set()
    combo_rezepte.icursor(tk.END)

entry_var.trace_add('write', lambda *args: filter_rezepte())


# Zutatenliste mit Scrollbar
zutaten_canvas = tk.Canvas(root)
zutaten_canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
scrollbar_zutaten = tk.Scrollbar(root, orient="vertical", command=zutaten_canvas.yview)
scrollbar_zutaten.grid(row=1, column=3, sticky="ns")
zutaten_canvas.configure(yscrollcommand=scrollbar_zutaten.set)
frame_zutaten = tk.Frame(zutaten_canvas)
zutaten_canvas.create_window((0,0), window=frame_zutaten, anchor="nw")
def on_frame_configure(event):
    zutaten_canvas.configure(scrollregion=zutaten_canvas.bbox("all"))
    zutaten_canvas.itemconfig("zutaten_frame", width=zutaten_canvas.winfo_width())
frame_zutaten.bind("<Configure>", on_frame_configure)
def on_canvas_resize(event):
    zutaten_canvas.itemconfig("zutaten_frame", width=event.width)
zutaten_canvas.bind("<Configure>", on_canvas_resize)
zutaten_canvas.create_window((0,0), window=frame_zutaten, anchor="nw", tags="zutaten_frame")
zutaten_widgets = []
ergebnis_labels = []  # NEU: Für Ergebnis-Spalte


# Eingabefeld und Button für verwendete Portionen in einem Frame nebeneinander
frame_verwendete = tk.Frame(root)
frame_verwendete.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="w")
label_verwendete = tk.Label(frame_verwendete, text="Verwendete Portionen:")
label_verwendete.pack(side="left")
entry_verwendete = tk.Entry(frame_verwendete, width=5)
entry_verwendete.pack(side="left", padx=(5, 5))
entry_verwendete.insert(0, "1")  # Standardwert

def berechne_erg():
    rezept = combo_rezepte.get()
    if not rezept or df_rezepte is None:
        return
    df_zutaten = df_rezepte[df_rezepte['Rezeptname'] == rezept]
    if df_zutaten.empty or 'Portionen' not in df_zutaten.columns:
        return
    try:
        verwendete = float(entry_verwendete.get())
    except Exception:
        verwendete = 1
    try:
        portionen = float(df_zutaten.iloc[0]['Portionen'])
    except Exception:
        portionen = 1
    for idx, row in enumerate(df_zutaten.itertuples(index=False)):
        menge_zahl = getattr(row, 'Menge_Zahl', '')
        try:
            menge_zahl = float(menge_zahl)
            erg = menge_zahl / portionen * verwendete
            ergebnis_labels[idx]['text'] = f"{erg:.2f}"
        except Exception:
            ergebnis_labels[idx]['text'] = "-"


# Reset function for textbox and result labels
def reset_entry_and_results():
    entry_verwendete.delete(0, tk.END)
    entry_verwendete.insert(0, "1")
    for lbl in ergebnis_labels:
        lbl['text'] = "-"

btn_berechnen = tk.Button(frame_verwendete, text="Berechnen", command=berechne_erg)
btn_berechnen.pack(side="left", padx=(5, 0))
btn_reset = tk.Button(frame_verwendete, text="Reset", command=reset_entry_and_results)
btn_reset.pack(side="left", padx=(5, 0))

# Funktion zum Anzeigen der Zutaten
def zeige_zutaten(event=None):
    for widget in frame_zutaten.winfo_children():
        widget.destroy()
    zutaten_widgets.clear()
    ergebnis_labels.clear()
    rezept = combo_rezepte.get()
    if not rezept or df_rezepte is None:
        return
    df_zutaten = df_rezepte[df_rezepte['Rezeptname'] == rezept]
    # Rezeptname als große Überschrift
    tk.Label(frame_zutaten, text=rezept, font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))
    # Portionen als kleinere Überschrift (letzte Spalte, falls vorhanden)
    portionen = None
    if not df_zutaten.empty and 'Portionen' in df_zutaten.columns:
        portionen = df_zutaten.iloc[0]['Portionen']
    if portionen is not None:
        tk.Label(frame_zutaten, text=f"Portionen: {portionen}", font=("Arial", 12, "bold")).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 5))
        start_row = 2
    else:
        start_row = 1
    # Spaltenüberschriften (jetzt mit Ergebnis)
    columns = ['Zutat', 'Menge_Zahl', 'Menge_Einheit', 'Ergebnis']
    for i, col in enumerate(columns):
        tk.Label(frame_zutaten, text=col, relief="ridge", bg="#e0e0e0").grid(row=start_row, column=i, sticky="nsew")
    # Zutaten und Mengen anzeigen
    max_lens = [len(col) for col in columns]
    for idx, row in enumerate(df_zutaten.itertuples(index=False), 1):
        zutat = str(getattr(row, 'Zutat', ''))
        menge_zahl = str(getattr(row, 'Menge_Zahl', ''))
        menge_einheit = str(getattr(row, 'Menge_Einheit', ''))
        tk.Label(frame_zutaten, text=zutat, relief="ridge").grid(row=start_row + idx, column=0, sticky="nsew")
        tk.Label(frame_zutaten, text=menge_zahl, relief="ridge").grid(row=start_row + idx, column=1, sticky="nsew")
        tk.Label(frame_zutaten, text=menge_einheit, relief="ridge").grid(row=start_row + idx, column=2, sticky="nsew")
        lbl_erg = tk.Label(frame_zutaten, text="-", relief="ridge")
        lbl_erg.grid(row=start_row + idx, column=3, sticky="nsew")
        ergebnis_labels.append(lbl_erg)
        zutaten_widgets.append((zutat, menge_zahl, menge_einheit))
        # Für Spaltenbreite
        max_lens[0] = max(max_lens[0], len(zutat))
        max_lens[1] = max(max_lens[1], len(menge_zahl))
        max_lens[2] = max(max_lens[2], len(menge_einheit))
    # Spaltenbreite anpassen
    for i, maxlen in enumerate(max_lens):
        frame_zutaten.grid_columnconfigure(i, minsize=(maxlen+2)*8)  # 8 Pixel pro Zeichen, +2 für Puffer
    # Link anzeigen, falls vorhanden
    link = df_zutaten['Link'].iloc[0] if 'Link' in df_zutaten.columns and not df_zutaten['Link'].isnull().all() else None
    if link:
        def open_link(event):
            webbrowser.open(link)
        link_label = tk.Label(frame_zutaten, text="Zum Rezept", fg="blue", cursor="hand2", underline=True)
        link_label.grid(row=start_row + idx + 1, column=0, columnspan=4, sticky="w", pady=(10,0))
        link_label.bind("<Button-1>", open_link)

combo_rezepte.bind("<<ComboboxSelected>>", zeige_zutaten)

# Speichern unter Funktion

def speichern_unter():
    rezept = combo_rezepte.get()
    if df_rezepte is None:
        messagebox.showerror("Fehler", "Die Rezepte-Datei konnte nicht geladen werden. Bitte prüfen Sie die Datei und starten Sie das Programm neu.")
        return
    if not rezept or not zutaten_widgets:
        messagebox.showerror("Fehler", "Kein Rezept ausgewählt oder keine Zutaten vorhanden.")
        return
    # Ergebniswerte aus Labels holen
    ergebnisse = [lbl['text'] for lbl in ergebnis_labels]
    # Portionen-Info holen
    df_zutaten = df_rezepte[df_rezepte['Rezeptname'] == rezept]
    portionen = None
    if not df_zutaten.empty and 'Portionen' in df_zutaten.columns:
        portionen = df_zutaten.iloc[0]['Portionen']
    # DataFrame mit Ergebnis-Spalte
    df_save = pd.DataFrame(
        [
            (zutat, menge_zahl, menge_einheit, ergebnis)
            for (zutat, menge_zahl, menge_einheit), ergebnis in zip(zutaten_widgets, ergebnisse)
        ],
        columns=['Zutat', 'Menge_Zahl', 'Menge_Einheit', 'Ergebnis']
    )
    # Optional: Portionen und Rezeptname als erste Zeilen einfügen
    extra_rows = []
    extra_rows.append(['Rezeptname', rezept, '', '', ''])
    if portionen is not None:
        extra_rows.append(['Portionen', portionen, '', '', ''])
    # Leere Zeile als Trenner
    extra_rows.append(['', '', '', '', ''])
    # DataFrame für Zusatzinfos
    df_extra = pd.DataFrame(extra_rows, columns=['Zutat', 'Menge_Zahl', 'Menge_Einheit', 'Ergebnis', ''])
    # DataFrames zusammenführen
    df_final = pd.concat([df_extra, df_save], ignore_index=True)
    # Datei speichern
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel-Dateien", "*.xlsx")],
        title="Speichern unter"
    )
    if file_path:
        try:
            df_final.to_excel(file_path, index=False)
            messagebox.showinfo("Erfolg", f"Datei gespeichert unter:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")

# Speichern unter Button
btn_speichern = tk.Button(root, text="Speichern unter", command=speichern_unter)
btn_speichern.grid(row=2, column=0, padx=10, pady=5, sticky="w")


# Funktion, um das Hauptmenü in den Vordergrund zu bringen und dann das Fenster zu schließen

# Cross-platform: bring main menu to front (Windows only)
def bring_hauptmenue_to_front(window_title='MeinErnaehrungsHauptmenue2025'):
    if sys.platform.startswith('win') and win32gui is not None and win32con is not None:
        def enumHandler(hwnd, lParam):
            if hasattr(win32gui, 'IsWindowVisible') and win32gui.IsWindowVisible(hwnd):
                if hasattr(win32gui, 'GetWindowText') and window_title in win32gui.GetWindowText(hwnd):
                    if hasattr(win32gui, 'ShowWindow') and hasattr(win32con, 'SW_RESTORE'):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    if hasattr(win32gui, 'SetForegroundWindow'):
                        win32gui.SetForegroundWindow(hwnd)
        if hasattr(win32gui, 'EnumWindows'):
            win32gui.EnumWindows(enumHandler, None)

def zurueck_zum_hauptmenue():
    if sys.platform.startswith('win') and win32gui is not None:
        bring_hauptmenue_to_front()
    # On Linux/macOS, just close the window
    root.destroy()



# Verlassen Button unten rechts in der Ecke
frame_verlassen = tk.Frame(root)
frame_verlassen.grid(row=3, column=3, sticky="se", padx=10, pady=10)
btn_verlassen = tk.Button(frame_verlassen, text="Verlassen", command=zurueck_zum_hauptmenue)
btn_verlassen.pack(anchor='e', side='right')

root.mainloop()
