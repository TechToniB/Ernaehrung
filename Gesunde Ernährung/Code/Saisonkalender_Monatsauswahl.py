import os
import importlib.util
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
    if spec is None or spec.loader is None:
        return {}
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
                # Bestimme die ersten und letzten Monate der Verfügbarkeit
                verfuegbare_monate = [idx for idx, wert in enumerate(werte) if wert in erlaubte_werte]
                if verfuegbare_monate:
                    erster_monat = MONATE[min(verfuegbare_monate)]
                    letzter_monat = MONATE[max(verfuegbare_monate)]
                else:
                    erster_monat = ""
                    letzter_monat = ""
                for idx, wert in enumerate(werte):
                    if wert in erlaubte_werte:
                        monat = MONATE[idx]
                        if name not in produkte:
                            produkte[name] = {"Monate": {}, "Verfuegbar_von": erster_monat, "Verfuegbar_bis": letzter_monat}
                        if monat not in produkte[name]["Monate"]:
                            produkte[name]["Monate"][monat] = set()
                        produkte[name]["Monate"][monat].add(laden)
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

        # Gemeinsamer horizontaler Frame für Dropdown, Suchleiste und Kontrollkästchen
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", pady=10)

        label = ttk.Label(top_frame, text="Monat auswählen:")
        label.pack(side="left", padx=5)
        self.monat_var = tk.StringVar(value=MONATE[0])
        self.monat_dropdown = ttk.Combobox(top_frame, values=MONATE, textvariable=self.monat_var, state="readonly")
        self.monat_dropdown.pack(side="left", padx=5)
        self.monat_dropdown.bind("<<ComboboxSelected>>", self.zeige_produkte)

        such_label = ttk.Label(top_frame, text="Suche Produkt:")
        such_label.pack(side="left", padx=5)
        self.such_var = tk.StringVar()
        self.such_entry = ttk.Entry(top_frame, textvariable=self.such_var)
        self.such_entry.pack(side="left", padx=5)
        self.such_entry.bind('<KeyRelease>', self.zeige_produkte)

        self.show_extra_columns = tk.BooleanVar(value=False)
        cb = ttk.Checkbutton(top_frame, text="Zeige Verfügbarkeits-Spalten", variable=self.show_extra_columns, command=self.update_tree_columns)
        cb.pack(side="left", padx=5)

        # Zurück-Button unten rechts
        frame_verlassen = tk.Frame(self.root)
        frame_verlassen.pack(side='bottom', anchor='se', padx=10, pady=10, fill='x')
        btn_verlassen = ttk.Button(frame_verlassen, text='Zurück', command=self.zurueck_zum_hauptmenue)
        btn_verlassen.pack(anchor='e', side='right')

        # Treeview initial nur mit 2 Spalten
        self.tree = ttk.Treeview(self.root, columns=("Produkt", "Laden"), show="headings")
        self.tree.heading("Produkt", text="Produkt")
        self.tree.heading("Laden", text="Verfügbar bei")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.zeige_produkte()

    def update_tree_columns(self):
        # Spalten dynamisch anpassen
        if self.show_extra_columns.get():
            new_cols = ("Produkt", "Laden", "Verfügbar von", "Verfügbar bis")
        else:
            new_cols = ("Produkt", "Laden")
        self.tree.config(columns=new_cols)
        for col in new_cols:
            self.tree.heading(col, text=col)
        self.zeige_produkte()

    def zeige_produkte(self, event=None):
        monat = self.monat_var.get()
        suchtext = self.such_var.get().strip().lower()
        # Tabelle leeren
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Produkte für den Monat finden und nach Suchtext filtern
        show_extra = self.show_extra_columns.get() if hasattr(self, 'show_extra_columns') else False
        for produkt, daten in self.produkte.items():
            monate_dict = daten["Monate"]
            if monat in monate_dict:
                if suchtext and suchtext not in produkt.lower():
                    continue
                laden = ", ".join(sorted(monate_dict[monat]))
                if show_extra:
                    verfuegbar_von = daten["Verfuegbar_von"]
                    verfuegbar_bis = daten["Verfuegbar_bis"]
                    self.tree.insert("", "end", values=(produkt, laden, verfuegbar_von, verfuegbar_bis))
                else:
                    self.tree.insert("", "end", values=(produkt, laden))
        self.root.update_idletasks()

    def bring_hauptmenue_to_front(self, window_title='MeinErnaehrungsHauptmenue2025'):
        import sys
        if sys.platform.startswith('win') and win32gui is not None and win32con is not None:
            def enumHandler(hwnd, lParam):
                if win32gui is not None and hasattr(win32gui, 'IsWindowVisible') and win32gui.IsWindowVisible(hwnd):
                    if hasattr(win32gui, 'GetWindowText') and window_title in win32gui.GetWindowText(hwnd):
                        if hasattr(win32gui, 'ShowWindow') and win32con is not None and hasattr(win32con, 'SW_RESTORE'):
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        if hasattr(win32gui, 'SetForegroundWindow'):
                            win32gui.SetForegroundWindow(hwnd)
            if hasattr(win32gui, 'EnumWindows'):
                win32gui.EnumWindows(enumHandler, None)

    def zurueck_zum_hauptmenue(self):
        import sys
        if sys.platform.startswith('win') and win32gui is not None and win32con is not None:
            self.bring_hauptmenue_to_front()
        self.root.destroy()

if __name__ == "__main__":
    dark_mode, fullscreen, themename = lade_settings()
    app = MonatsauswahlApp(dark_mode=dark_mode, fullscreen=fullscreen, themename=themename)
    app.root.mainloop()
