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

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

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

        # Suchleiste
        such_frame = tk.Frame(self.root)
        such_frame.pack(pady=5)
        such_label = ttk.Label(such_frame, text="Suche Produkt:")
        such_label.pack(side="left")
        self.such_var = tk.StringVar()
        self.such_entry = ttk.Entry(such_frame, textvariable=self.such_var)
        self.such_entry.pack(side="left", padx=5)
        self.such_entry.bind('<KeyRelease>', self.zeige_produkte)

        self.tree = ttk.Treeview(self.root, columns=("Produkt", "Laden"), show="headings")
        self.tree.heading("Produkt", text="Produkt")
        self.tree.heading("Laden", text="Verfügbar bei")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Zurück-Button unten rechts
        frame_verlassen = tk.Frame(self.root)
        frame_verlassen.pack(side='bottom', anchor='se', padx=10, pady=10, fill='x')
        btn_verlassen = ttk.Button(frame_verlassen, text='Zurück', command=self.zurueck_zum_hauptmenue)
        btn_verlassen.pack(anchor='e', side='right')

        self.zeige_produkte()

    def zeige_produkte(self, event=None):
        monat = self.monat_var.get()
        suchtext = self.such_var.get().strip().lower()
        # Tabelle leeren
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Produkte für den Monat finden und nach Suchtext filtern
        for produkt, monate_dict in self.produkte.items():
            if monat in monate_dict:
                if suchtext and suchtext not in produkt.lower():
                    continue
                laden = ", ".join(sorted(monate_dict[monat]))
                self.tree.insert("", "end", values=(produkt, laden))
        self.root.update_idletasks()

    def bring_hauptmenue_to_front(self, window_title='MeinErnaehrungsHauptmenue2025'):
        if win32gui is None:
            return
        def enumHandler(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):
                if window_title in win32gui.GetWindowText(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
        win32gui.EnumWindows(enumHandler, None)

    def zurueck_zum_hauptmenue(self):
        self.bring_hauptmenue_to_front()
        self.root.destroy()

if __name__ == "__main__":
    dark_mode, fullscreen, themename = lade_settings()
    app = MonatsauswahlApp(dark_mode=dark_mode, fullscreen=fullscreen, themename=themename)
    app.root.mainloop()
