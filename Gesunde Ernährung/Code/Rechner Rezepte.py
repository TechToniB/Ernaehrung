import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os
import json
import ttkbootstrap as tb

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


# Einstellungen laden (Dark Mode, Vollbild)
settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
dark_mode = False
fullscreen = False
if os.path.exists(settings_path):
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            dark_mode = settings.get('dark_mode', False)
            fullscreen = settings.get('fullscreen', False)
    except Exception:
        pass

themename = "darkly" if dark_mode else "flatly"
try:
    root = tb.Window(themename=themename)
except Exception:
    root = tk.Tk()
root.title('Rezept-Zutaten-Anzeige')
if fullscreen:
    root.attributes('-fullscreen', True)

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

# Frame für Zutatenliste
frame_zutaten = tk.Frame(root)
frame_zutaten.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

zutaten_widgets = []

# Funktion zum Anzeigen der Zutaten
def zeige_zutaten(event=None):
    for widget in frame_zutaten.winfo_children():
        widget.destroy()
    zutaten_widgets.clear()
    rezept = combo_rezepte.get()
    if not rezept or df_rezepte is None:
        return
    df_zutaten = df_rezepte[df_rezepte['Rezeptname'] == rezept]
    # Spaltenüberschriften
    for i, col in enumerate(['Zutat', 'Menge']):
        tk.Label(frame_zutaten, text=col, relief="ridge", bg="#e0e0e0").grid(row=0, column=i, sticky="nsew")
    # Zutaten und Mengen anzeigen
    for idx, row in enumerate(df_zutaten.itertuples(index=False), 1):
        tk.Label(frame_zutaten, text=getattr(row, 'Zutat', ''), relief="ridge").grid(row=idx, column=0, sticky="nsew")
        tk.Label(frame_zutaten, text=getattr(row, 'Menge', ''), relief="ridge").grid(row=idx, column=1, sticky="nsew")
        zutaten_widgets.append((getattr(row, 'Zutat', ''), getattr(row, 'Menge', '')))

combo_rezepte.bind("<<ComboboxSelected>>", zeige_zutaten)

# Speichern unter Funktion

def speichern_unter():
    rezept = combo_rezepte.get()
    if not rezept or not zutaten_widgets:
        messagebox.showerror("Fehler", "Kein Rezept ausgewählt oder keine Zutaten vorhanden.")
        return
    df_save = pd.DataFrame(zutaten_widgets, columns=['Zutat', 'Menge'])
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel-Dateien", "*.xlsx")],
        title="Speichern unter"
    )
    if file_path:
        try:
            df_save.to_excel(file_path, index=False)
            messagebox.showinfo("Erfolg", f"Datei gespeichert unter:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")

# Speichern unter Button
btn_speichern = tk.Button(root, text="Speichern unter", command=speichern_unter)
btn_speichern.grid(row=2, column=0, padx=10, pady=5, sticky="w")

# Verlassen Button unten rechts in eigenem Frame
GRID_LAST_ROW = 100
GRID_LAST_COL = 2
root.grid_rowconfigure(GRID_LAST_ROW, weight=1)
root.grid_columnconfigure(GRID_LAST_COL, weight=1)
frame_verlassen = tk.Frame(root)
frame_verlassen.grid(row=GRID_LAST_ROW, column=GRID_LAST_COL, sticky="se", padx=10, pady=10)
btn_verlassen = tk.Button(frame_verlassen, text="Verlassen", command=root.destroy)
btn_verlassen.pack(anchor='e', side='right')

root.mainloop()
