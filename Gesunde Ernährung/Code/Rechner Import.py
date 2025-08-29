import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import re

df_global = None
eintrag_widgets = []

def lade_und_zeige_tabelle(dateipfad):
    global df_global
    try:
        df_global = pd.read_excel(dateipfad)
        zeige_tabelle()
    except Exception as e:
        messagebox.showerror("Fehler", f"Die Datei konnte nicht geladen werden:\n{e}")

def zeige_tabelle():
    global eintrag_widgets
    for widget in frame_tabellen.winfo_children():
        widget.destroy()
    eintrag_widgets.clear()
    if df_global is None:
        return

    n = len(df_global)
    drittel = (n + 2) // 3  # Aufrunden, damit alles abgedeckt ist

    teile = [
        df_global.iloc[0:drittel],
        df_global.iloc[drittel:2*drittel],
        df_global.iloc[2*drittel:]
    ]

    frames = []
    for i in range(3):
        f = tk.Frame(frame_tabellen, borderwidth=2, relief="groove")
        f.grid(row=0, column=i, padx=5, pady=5, sticky="n")
        frames.append(f)

    for teil_idx, teil in enumerate(teile):
        # Spaltenüberschriften
        for i, col in enumerate(teil.columns):
            tk.Label(frames[teil_idx], text=col, relief="ridge", bg="#e0e0e0").grid(row=0, column=i, sticky="nsew")
        tk.Label(frames[teil_idx], text="Dein Wert", relief="ridge", bg="#e0e0e0").grid(row=0, column=len(teil.columns), sticky="nsew")
        # Zeilen
        for row_idx, row in enumerate(teil.itertuples(index=False), 1):
            for col_idx, value in enumerate(row):
                tk.Label(frames[teil_idx], text=str(value), relief="ridge").grid(row=row_idx, column=col_idx, sticky="nsew")
            eintrag = tk.Entry(frames[teil_idx], width=10)
            eintrag.grid(row=row_idx, column=len(teil.columns), sticky="nsew")
            eintrag_widgets.append(eintrag)

def tabelle_ausgewaehlt(event):
    auswahl = combo_tabellen.get()
    if auswahl:
        dateipfad = filter_ordner / auswahl
        lade_und_zeige_tabelle(dateipfad)

def pruefe_werte():
    if df_global is None:
        return
    ergebnisse = []
    for idx, (i, row) in enumerate(df_global.iterrows()):
        try:
            ref_str = str(row['Referenzwert'])
            match = re.search(r"[-+]?\d*\.?\d+", ref_str)
            if not match:
                ergebnisse.append("Kein Referenzwert")
                continue
            referenz = float(match.group())
            eintrag = eintrag_widgets[idx].get()
            if eintrag.strip() == "":
                ergebnisse.append("Kein Wert")
                continue
            wert = float(eintrag)
            kategorie = str(row.get('Kategorie', '')).strip().lower()
            naehrstoff = str(row.get('Nährstoff', '')).strip().lower()
            if kategorie == "richtwert":
                tol = 0.01
                if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                    ergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    ergebnisse.append("Zu niedrig")
                else:
                    ergebnisse.append("Zu hoch")
            elif kategorie == "schätzwert":
                tol = 0.05
                if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                    ergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    ergebnisse.append("Zu niedrig")
                else:
                    ergebnisse.append("Zu hoch")
            elif kategorie == "empfohlene zufuhr":
                if "gesättigte fettsäuren" in naehrstoff:
                    if wert <= referenz:
                        ergebnisse.append("Im Rahmen")
                    else:
                        ergebnisse.append("Zu hoch")
                else:
                    tol = 0.10
                    if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                        ergebnisse.append("Im Rahmen")
                    elif wert < referenz * (1 - tol):
                        ergebnisse.append("Zu niedrig")
                    else:
                        ergebnisse.append("Zu hoch")
            else:
                tol = 0.05
                if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                    ergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    ergebnisse.append("Zu niedrig")
                else:
                    ergebnisse.append("Zu hoch")
        except Exception:
            ergebnisse.append("Ungültig")
    # Ergebnisse anzeigen
    idx = 0
    n = len(df_global)
    drittel = (n + 2) // 3
    for teil_idx in range(3):
        frame = frame_tabellen.grid_slaves(row=0, column=teil_idx)[0]
        rows = len(df_global.iloc[teil_idx*drittel : min((teil_idx+1)*drittel, n)])
        for row in range(1, rows+1):
            tk.Label(frame, text=ergebnisse[idx], relief="ridge", bg="#f0f0f0").grid(row=row, column=len(df_global.columns)+1, sticky="nsew")
            idx += 1

# Filter-Ordner festlegen
filter_ordner = Path.home() / "Dokumente" / "Ernaehrung" / "Gesunde Ernährung" / "Filter"
tabellen = [f.name for f in filter_ordner.glob("*.xlsx")]

# Fenster erstellen
root = tk.Tk()
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
