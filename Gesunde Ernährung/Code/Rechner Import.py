
import pandas as pd
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import re
try:
    import ttkbootstrap as tb
except ImportError:
    print("Das Modul 'ttkbootstrap' ist nicht installiert. Bitte installieren Sie es mit 'pip install ttkbootstrap'.")
    sys.exit(1)

# Dark mode support
def get_theme():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dark', action='store_true')
    args, _ = parser.parse_known_args()
    return "darkly" if args.dark else "flatly"

# Globale Variablen für die geladene Tabelle und die Eingabefelder
df_global = None           # Hier wird das aktuell geladene DataFrame gespeichert
eintrag_widgets = []       # Liste für alle Eingabefelder (Entry-Widgets)

def lade_und_zeige_tabelle(dateipfad):
    """
    Lädt die Excel-Tabelle und zeigt sie im Fenster an.
    """
    global df_global
    try:
        df_global = pd.read_excel(dateipfad)  # Excel-Datei laden
        zeige_tabelle()                       # Tabelle im GUI anzeigen
    except Exception as e:
        messagebox.showerror("Fehler", f"Die Datei konnte nicht geladen werden:\n{e}")

def zeige_tabelle():
    """
    Zeigt die Tabelle in drei nebeneinanderliegenden Teilen an,
    jeweils mit Eingabefeldern für eigene Werte.
    """
    global eintrag_widgets
    # Vorherige Inhalte löschen
    for widget in frame_tabellen.winfo_children():
        widget.destroy()
    eintrag_widgets.clear()
    if df_global is None:
        return

    n = len(df_global)
    drittel = (n + 2) // 3  # Tabelle in 3 etwa gleich große Teile aufteilen

    # Tabelle in drei Teile aufteilen
    teile = [
        df_global.iloc[0:drittel],
        df_global.iloc[drittel:2*drittel],
        df_global.iloc[2*drittel:]
    ]

    frames = []
    # Drei Frames nebeneinander für die drei Teile
    for i in range(3):
        f = tk.Frame(frame_tabellen, borderwidth=2, relief="groove")
        f.grid(row=0, column=i, padx=5, pady=5, sticky="n")
        frames.append(f)

    # Jeden Teil in einem eigenen Frame anzeigen
    import math
    for teil_idx, teil in enumerate(teile):
        # Spaltenüberschriften
        for i, col in enumerate(teil.columns):
            tk.Label(frames[teil_idx], text=col, relief="ridge", bg="#e0e0e0").grid(row=0, column=i, sticky="nsew")
        tk.Label(frames[teil_idx], text="Dein Wert", relief="ridge", bg="#e0e0e0").grid(row=0, column=len(teil.columns), sticky="nsew")
        # Zeilen mit Daten und Eingabefeld
        for row_idx, row in enumerate(teil.itertuples(index=False), 1):
            for col_idx, value in enumerate(row):
                # Wenn Wert NaN ist, nichts anzeigen
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    label_text = ""
                else:
                    label_text = str(value)
                tk.Label(frames[teil_idx], text=label_text, relief="ridge").grid(row=row_idx, column=col_idx, sticky="nsew")
            # Eingabefeld für eigenen Wert
            eintrag = tk.Entry(frames[teil_idx], width=10)
            eintrag.grid(row=row_idx, column=len(teil.columns), sticky="nsew")
            eintrag_widgets.append(eintrag)

def tabelle_ausgewaehlt(event):
    """
    Wird aufgerufen, wenn eine Tabelle aus der Combobox ausgewählt wurde.
    """
    auswahl = combo_tabellen.get()
    if auswahl:
        dateipfad = filter_ordner / auswahl
        lade_und_zeige_tabelle(dateipfad)

def pruefe_werte():
    """
    Prüft die eingetragenen Werte gegen die Referenzwerte und zeigt das Ergebnis an.
    Die Toleranz hängt von der Kategorie ab.
    """
    if df_global is None:
        return
    ergebnisse = []
    # Farben für die Einfärbung
    COLOR_OK = "#067a06"   # Dunkelgrün
    COLOR_FAIL = "#d81212" # Dunkelrot
    # Alle Zeilen der Tabelle durchgehen
    for idx, (_, row) in enumerate(df_global.iterrows()):
        try:
            ref_str = str(row['Referenzwert'])
            match = re.search(r"[-+]?\d*\.?\d+", ref_str)
            if not match:
                ergebnisse.append("Kein Referenzwert")
                eintrag_widgets[idx].config(bg=COLOR_FAIL)
                continue
            referenz = float(match.group())
            eintrag = eintrag_widgets[idx].get()
            if eintrag.strip() == "":
                ergebnisse.append("Kein Wert")
                eintrag_widgets[idx].config(bg=COLOR_FAIL)
                continue
            wert = float(eintrag)
            kategorie = str(row.get('Kategorie', '')).strip().lower()
            naehrstoff = str(row.get('Nährstoff', '')).strip().lower()
            im_rahmen = False
            if kategorie == "richtwert":
                tol = 0.01
                im_rahmen = referenz * (1 - tol) <= wert <= referenz * (1 + tol)
                if im_rahmen:
                    ergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    ergebnisse.append("Zu niedrig")
                else:
                    ergebnisse.append("Zu hoch")
            elif kategorie == "schätzwert":
                tol = 0.05
                im_rahmen = referenz * (1 - tol) <= wert <= referenz * (1 + tol)
                if im_rahmen:
                    ergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    ergebnisse.append("Zu niedrig")
                else:
                    ergebnisse.append("Zu hoch")
            elif kategorie == "empfohlene zufuhr":
                if "gesättigte fettsäuren" in naehrstoff:
                    im_rahmen = wert <= referenz
                    if im_rahmen:
                        ergebnisse.append("Im Rahmen")
                    else:
                        ergebnisse.append("Zu hoch")
                else:
                    tol = 0.10
                    im_rahmen = referenz * (1 - tol) <= wert <= referenz * (1 + tol)
                    if im_rahmen:
                        ergebnisse.append("Im Rahmen")
                    elif wert < referenz * (1 - tol):
                        ergebnisse.append("Zu niedrig")
                    else:
                        ergebnisse.append("Zu hoch")
            else:
                tol = 0.01
                im_rahmen = referenz * (1 - tol) <= wert <= referenz * (1 + tol)
                if im_rahmen:
                    ergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    ergebnisse.append("Zu niedrig")
                else:
                    ergebnisse.append("Zu hoch")
            # Zelle einfärben
            if im_rahmen:
                eintrag_widgets[idx].config(bg=COLOR_OK)
            else:
                eintrag_widgets[idx].config(bg=COLOR_FAIL)
        except Exception as e:
            print(f"Fehler beim Prüfen der Werte in Zeile {idx}: {e}")
            ergebnisse.append("Ungültig")
            eintrag_widgets[idx].config(bg=COLOR_FAIL)
    # Ergebnisse in den jeweiligen Frames anzeigen
    idx = 0
    n = len(df_global)
    drittel = (n + 2) // 3
    for teil_idx in range(3):
        frames = frame_tabellen.grid_slaves(row=0, column=teil_idx)
        if not frames:
            continue
        frame = frames[0]
        rows = len(df_global.iloc[teil_idx*drittel : min((teil_idx+1)*drittel, n)])
        for row in range(1, rows+1):
            tk.Label(frame, text=ergebnisse[idx], relief="ridge", bg="#f0f0f0").grid(row=row, column=len(df_global.columns)+1, sticky="nsew")
            idx += 1


# Filter-Ordner festlegen (hier werden die Excel-Dateien gesucht)
filter_ordner = Path.home() / "Dokumente" / "Ernaehrung" / "Gesunde Ernährung" / "Filter"
tabellen = [f.name for f in filter_ordner.glob("*.xlsx")]


# Fenster erstellen
root = tb.Window(themename=get_theme())
root.title("Tabellen-Auswahl")

# Auswahlfeld für Tabellen
combo_tabellen = ttk.Combobox(root, values=tabellen, state="readonly")
combo_tabellen.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
combo_tabellen.bind("<<ComboboxSelected>>", tabelle_ausgewaehlt)

# Frame für Tabellenausgabe
frame_tabellen = tk.Frame(root)
frame_tabellen.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Prüfen-Button
btn_pruefen = tk.Button(root, text="Prüfen", command=pruefe_werte)
btn_pruefen.grid(row=2, column=0, sticky="e", padx=10, pady=5)

root.mainloop()
