import os
import importlib.util
import pandas as pd
import tkinter as tk
from tkinter import ttk
import json

try:
    import ttkbootstrap as tb
except ImportError:
    tb = None

ORDNER = os.path.join(os.path.dirname(__file__), "Saisonklaender")
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

# Hilfsfunktion zum Laden der Variablen aus Kalenderdateien
def lade_variablen(pfad):
    spec = importlib.util.spec_from_file_location("modul", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return {k: v for k, v in vars(modul).items() if isinstance(v, list) and len(v) == 12}

def lade_kalenderdaten():
    produkte = {}
    for fname in os.listdir(ORDNER):
        if fname.endswith("_Saison_Kalender.py"):
            pfad = os.path.join(ORDNER, fname)
            laden = "REWE" if "REWE" in fname.upper() else "EDEKA"
            erlaubte_werte = ["1", "2", "3"] if laden == "REWE" else ["1"]
            variablen = lade_variablen(pfad)
            for name, werte in variablen.items():
                for idx, wert in enumerate(werte):
                    if wert in erlaubte_werte:
                        monat = MONATE[idx]
                        if name not in produkte:
                            produkte[name] = {}
                        if monat not in produkte[name]:
                            produkte[name][monat] = set()
                        produkte[name][monat].add(laden)
    return produkte

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

class MonatsauswahlApp:
    def __init__(self, dark_mode=False, fullscreen=False, themename="flatly"):
        if tb:
            self.root = tb.Window(themename=themename)
        else:
            self.root = tk.Tk()
        self.root.title("Saisonkalender Monatsauswahl")
        self.root.geometry("600x500")
        if fullscreen:
            self.root.attributes('-fullscreen', True)
        self.produkte = lade_kalenderdaten()

        label = ttk.Label(self.root, text="Monat auswählen:")
        label.pack(pady=10)
        self.monat_var = tk.StringVar(value=MONATE[0])
        self.monat_dropdown = ttk.Combobox(self.root, values=MONATE, textvariable=self.monat_var, state="readonly")
        self.monat_dropdown.pack(pady=5)
        self.monat_dropdown.bind("<<ComboboxSelected>>", self.zeige_produkte)

        self.tree = ttk.Treeview(self.root, columns=("Produkt", "Laden"), show="headings")
        self.tree.heading("Produkt", text="Produkt")
        self.tree.heading("Laden", text="Verfügbar bei")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Zurück-Button unten rechts
        frame_verlassen = tk.Frame(self.root)
        frame_verlassen.pack(side='bottom', anchor='se', padx=10, pady=10, fill='x')
        btn_verlassen = ttk.Button(frame_verlassen, text='Zurück', command=self.root.destroy)
        btn_verlassen.pack(anchor='e', side='right')

        self.zeige_produkte()

    def zeige_produkte(self, event=None):
        monat = self.monat_var.get()
        # Tabelle leeren
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Produkte für den Monat finden
        for produkt, monate_dict in self.produkte.items():
            if monat in monate_dict:
                laden = ", ".join(sorted(monate_dict[monat]))
                self.tree.insert("", "end", values=(produkt, laden))
        self.root.update_idletasks()

if __name__ == "__main__":
    dark_mode, fullscreen, themename = lade_settings()
    app = MonatsauswahlApp(dark_mode=dark_mode, fullscreen=fullscreen, themename=themename)
    app.root.mainloop()
