import pandas as pd
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, filedialog  # <-- filedialog import added
from pathlib import Path
import re

import os
import json
try:
    import ttkbootstrap as tb
except ImportError:
    print("Das Modul 'ttkbootstrap' ist nicht installiert. Bitte installieren Sie es mit 'pip install ttkbootstrap'.")
    sys.exit(1)
import platform

import math
import tkinter.font as tkfont

def lade_settings():
    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    dark_mode = False
    fullscreen = False
    themename = "flatly"
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                dark_mode = settings.get('dark_mode', False)
                fullscreen = settings.get('fullscreen', False)
                themename = settings.get('themename', "darkly" if dark_mode else "flatly")
        except Exception:
            pass
    return dark_mode, fullscreen, themename

df_global = None
eintrag_widgets = []

tree = None
entry_dict = {}
table_font = None

def lade_und_zeige_tabelle(dateipfad):
    global df_global
    try:
        df_global = pd.read_excel(dateipfad)
    # Diagnose-Popup entfernt
        zeige_tabelle()
    except Exception as e:
        messagebox.showerror("Fehler", f"Die Datei konnte nicht geladen werden:\n{e}")

def zeige_tabelle():
    global tree, entry_dict, eintrag_widgets, table_font
    for widget in frame_tabellen.winfo_children():
        widget.destroy()
    eintrag_widgets.clear()
    entry_dict.clear()
    if df_global is None:
        return

    h = root.winfo_height() if root.winfo_height() > 1 else root.winfo_screenheight()
    base_font_size = max(10, int(h * 0.025))
    table_font = tkfont.Font(family="Arial", size=base_font_size)


    columns = list(df_global.columns) + ["Dein Wert"]
    echte_spalten = [col for col in df_global.columns if str(col).strip() != "" and col is not None]
    if (
        df_global is None
        or len(echte_spalten) == 0
        or df_global.shape[0] == 0
        or len(columns) < 2
    ):
        messagebox.showerror("Fehler", "Die Tabelle enthält keine gültigen Spaltennamen oder keine Zeilen.")
        return
    letzte_spalte = columns[-1] if len(columns) > 1 else None
    tree = ttk.Treeview(frame_tabellen, columns=columns, show="headings")
    frame_width = frame_tabellen.winfo_width() if frame_tabellen.winfo_width() > 1 else root.winfo_width()
    col_width = int(frame_width / len(columns)) if len(columns) > 0 else 120
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_width, anchor="center")
    tree.grid(row=0, column=0, sticky="nsew")

    vsb = ttk.Scrollbar(frame_tabellen, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame_tabellen, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame_tabellen.grid_rowconfigure(0, weight=1)
    frame_tabellen.grid_rowconfigure(1, weight=0)
    frame_tabellen.grid_columnconfigure(0, weight=1)
    frame_tabellen.grid_columnconfigure(1, weight=0)

    for idx, row in df_global.iterrows():
        values = [row[col] if pd.notna(row[col]) else "" for col in df_global.columns]
        values.append("")
        tree.insert("", "end", iid=str(idx), values=values)

    for idx in range(len(df_global)):
        entry = tk.Entry(tree, font=table_font)
        entry_dict[str(idx)] = entry
        eintrag_widgets.append(entry)
    def place_all_entries(event=None):
        if df_global is not None and tree is not None and letzte_spalte is not None:
            for idx in range(len(df_global)):
                entry = entry_dict.get(str(idx))
                if entry is not None:
                    try:
                        bbox = tree.bbox(str(idx), letzte_spalte)
                        if bbox is not None:
                            entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                        else:
                            entry.place_forget()
                    except IndexError:
                        entry.place_forget()
                        return
    tree.bind("<Configure>", place_all_entries)
    place_all_entries()

def on_resize(event):
    if tree is not None:
        total_width = tree.winfo_width()
        num_cols = len(tree["columns"])
        if num_cols > 0 and total_width > 0:
            col_width = int(total_width / num_cols)
            for col in tree["columns"]:
                tree.column(col, width=col_width)
        columns = tree["columns"]
        letzte_spalte = columns[-1] if len(columns) > 1 else None
        if df_global is not None and letzte_spalte is not None:
            for idx in range(len(df_global)):
                entry = entry_dict.get(str(idx))
                if entry is not None:
                    try:
                        bbox = tree.bbox(str(idx), letzte_spalte)
                        if bbox is not None:
                            entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                        else:
                            entry.place_forget()
                    except IndexError:
                        entry.place_forget()
                        return


def tabelle_ausgewaehlt(event):
    auswahl = combo_tabellen.get()
    if auswahl:
        dateipfad = filter_ordner / auswahl
        lade_und_zeige_tabelle(dateipfad)

def pruefe_werte():
    if df_global is None:
        return
    ergebnisse = []
    COLOR_OK = "#067a06"
    COLOR_FAIL = "#d81212"
    for idx, (_, row) in enumerate(df_global.iterrows()):
        try:
            ref_str = str(row['Referenzwert'])
            match = re.search(r"[-+]?\d*\.?\d+", ref_str)
            if not match:
                ergebnisse.append("Kein Referenzwert")
                continue
            referenz = float(match.group())
            entry = entry_dict.get(str(idx))
            if not entry or entry.get().strip() == "":
                ergebnisse.append("Kein Wert")
                continue
            try:
                wert = float(entry.get())
            except ValueError:
                ergebnisse.append("Ungültige Eingabe")
                continue
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
            if entry:
                entry.config(bg=COLOR_OK if im_rahmen else COLOR_FAIL)
        except Exception:
            ergebnisse.append("Fehler in Zeile")
            entry = entry_dict.get(str(idx))
            if entry:
                entry.config(bg=COLOR_FAIL)
    messagebox.showinfo("Prüfungsergebnisse", "\n".join(ergebnisse))

filter_ordner = Path.home() / "Dokumente" / "Ernaehrung" / "Gesunde Ernährung" / "Filter"
tabellen = [f.name for f in filter_ordner.glob("*.xlsx") if f.is_file()]

dark_mode, fullscreen, themename = lade_settings()
IMPORT_TITLE = 'RechnerImportFenster2025'
root = tb.Window(themename=themename)
root.title(IMPORT_TITLE)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
if fullscreen:
    root.attributes('-fullscreen', True)
else:
    w = int(screen_width * 0.9)
    h = int(screen_height * 0.9)
    root.geometry(f"{w}x{h}")

base_font_size = max(10, int(screen_height * 0.025))
table_font = tkfont.Font(family="Arial", size=base_font_size)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.bind("<Configure>", on_resize)

combo_tabellen = ttk.Combobox(root, values=tabellen, state="readonly")
combo_tabellen.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
combo_tabellen.bind("<<ComboboxSelected>>", tabelle_ausgewaehlt)


GRID_LAST_ROW = 2
GRID_LAST_COL = 2
# Tabelle nimmt den gesamten Platz bis zu den Buttons ein
frame_tabellen = tk.Frame(root)
frame_tabellen.grid(row=1, column=0, columnspan=3, padx=0, pady=0, sticky="nsew")
root.grid_rowconfigure(1, weight=1)  # Tabelle wächst
root.grid_rowconfigure(GRID_LAST_ROW, weight=0)  # Buttons fix unten
root.grid_columnconfigure(0, weight=1)
frame_tabellen.grid_rowconfigure(0, weight=1)
frame_tabellen.grid_columnconfigure(0, weight=1)

def bring_hauptmenue_to_front(window_title='MeinErnaehrungsHauptmenue2025'):
    pass

def zurueck_zum_hauptmenue():
    bring_hauptmenue_to_front()
    root.destroy()





def speichern_unter():
    if df_global is None:
        messagebox.showerror("Fehler", "Keine Tabelle geladen.")
        return
    df_save = df_global.copy()
    pruefungsergebnisse = []
    for idx, entry in enumerate(eintrag_widgets):
        val = entry.get()
        df_save.at[idx, 'Dein Wert'] = val
        try:
            ref_str = str(df_global.iloc[idx]['Referenzwert'])
            match = re.search(r"[-+]?\d*\.?\d+", ref_str)
            if not match:
                pruefungsergebnisse.append("Kein Referenzwert")
                continue
            referenz = float(match.group())
            if val.strip() == "":
                pruefungsergebnisse.append("Kein Wert")
                continue
            try:
                wert = float(val)
            except ValueError:
                pruefungsergebnisse.append("Ungültige Eingabe")
                continue
            kategorie = str(df_global.iloc[idx].get('Kategorie', '')).strip().lower()
            naehrstoff = str(df_global.iloc[idx].get('Nährstoff', '')).strip().lower()
            if kategorie == "richtwert":
                tol = 0.01
                if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                    pruefungsergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    pruefungsergebnisse.append("Zu niedrig")
                else:
                    pruefungsergebnisse.append("Zu hoch")
            elif kategorie == "schätzwert":
                tol = 0.05
                if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                    pruefungsergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    pruefungsergebnisse.append("Zu niedrig")
                else:
                    pruefungsergebnisse.append("Zu hoch")
            elif kategorie == "empfohlene zufuhr":
                if "gesättigte fettsäuren" in naehrstoff:
                    if wert <= referenz:
                        pruefungsergebnisse.append("Im Rahmen")
                    else:
                        pruefungsergebnisse.append("Zu hoch")
                else:
                    tol = 0.10
                    if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                        pruefungsergebnisse.append("Im Rahmen")
                    elif wert < referenz * (1 - tol):
                        pruefungsergebnisse.append("Zu niedrig")
                    else:
                        pruefungsergebnisse.append("Zu hoch")
            else:
                tol = 0.01
                if referenz * (1 - tol) <= wert <= referenz * (1 + tol):
                    pruefungsergebnisse.append("Im Rahmen")
                elif wert < referenz * (1 - tol):
                    pruefungsergebnisse.append("Zu niedrig")
                else:
                    pruefungsergebnisse.append("Zu hoch")
        except Exception:
            pruefungsergebnisse.append("Fehler in Zeile")
    df_save['Prüfung'] = pruefungsergebnisse
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


button_frame = tk.Frame(root)
button_frame.grid(row=GRID_LAST_ROW, column=0, columnspan=3, sticky="sew", padx=0, pady=0)
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)

btn_pruefen = tb.Button(button_frame, text="Prüfen", command=pruefe_werte)
btn_pruefen.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
btn_speichern = tb.Button(button_frame, text="Speichern unter", command=speichern_unter)
btn_speichern.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
btn_hauptmenue = tb.Button(button_frame, text="Verlassen", command=zurueck_zum_hauptmenue)
btn_hauptmenue.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

root.mainloop()
