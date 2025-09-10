import os
import importlib.util
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
MONATE = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

def lade_variablen(pfad):
    # Lädt alle Variablen aus einer Python-Datei als dict
    spec = importlib.util.spec_from_file_location("modul", pfad)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec or loader from {pfad}")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return {k: v for k, v in vars(modul).items() if isinstance(v, list) and len(v) == 12}

def filtere_monate(liste, erlaubte_werte):
    return [monat for monat, wert in zip(MONATE, liste) if wert in erlaubte_werte]

def erstelle_tabelle(variablen, erlaubte_werte):
    daten = []
    for name, werte in variablen.items():
        monate = filtere_monate(werte, erlaubte_werte)
        if monate:
            daten.append({"Gemüse/Obst": name, "Monate": ", ".join(monate)})
    df = pd.DataFrame(daten)
    return df

def lade_kalender(dateiname, erlaubte_werte):
    pfad = os.path.join(ORDNER, dateiname)
    variablen = lade_variablen(pfad)
    return erstelle_tabelle(variablen, erlaubte_werte)

def lade_alle_kalender():
    dfs = []
    for fname in os.listdir(ORDNER):
        if fname.endswith("_Saison_Kalender.py"):
            if "REWE" in fname.upper():
                erlaubte_werte = ["1", "2", "3"]
            elif "EDEKA" in fname.upper():
                erlaubte_werte = ["1"]
            else:
                continue
            try:
                variablen = lade_variablen(os.path.join(ORDNER, fname))
                df = erstelle_tabelle(variablen, erlaubte_werte)
                df["Kalender"] = fname.replace("_Saison_Kalender.py", "")
                dfs.append(df)
            except Exception:
                continue
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame(columns=["Gemüse/Obst", "Monate", "Kalender"])

def bring_hauptmenue_to_front(window_title='MeinErnaehrungsHauptmenue2025'):
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

class SaisonApp:
    def __init__(self, dark_mode=False, fullscreen=False, themename="flatly"):
        # Theme wählen
        if tb:
            self.root = tb.Window(themename=themename)
        else:
            self.root = tk.Tk()
        self.root.title("Saisonkalender Tabelle")
        self.root.geometry("600x500")
        if fullscreen:
            self.root.attributes('-fullscreen', True)
        self.df = None

        self.option = tk.StringVar(value="REWE")
        ttk.Label(self.root, text="Wähle Kalender:").pack(pady=5)
        ttk.Radiobutton(self.root, text="REWE", variable=self.option, value="REWE", command=self.zeige_tabelle).pack()
        ttk.Radiobutton(self.root, text="EDEKA", variable=self.option, value="EDEKA", command=self.zeige_tabelle).pack()
        ttk.Radiobutton(self.root, text="Alle", variable=self.option, value="ALLE", command=self.zeige_tabelle).pack()

        self.tree = ttk.Treeview(self.root, columns=("Gemüse/Obst", "Monate"), show="headings")
        self.tree.heading("Gemüse/Obst", text="Gemüse/Obst")
        self.tree.heading("Monate", text="Monate")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        ttk.Button(self.root, text="Als Excel speichern", command=self.speichern).pack(pady=5)

        # Zurück-Button unten rechts
        frame_verlassen = tk.Frame(self.root)
        frame_verlassen.pack(side='bottom', anchor='se', padx=10, pady=10, fill='x')
        btn_verlassen = ttk.Button(frame_verlassen, text='Zurück', command=self.zurueck_zum_hauptmenue)
        btn_verlassen.pack(anchor='e', side='right')

        self.zeige_tabelle()

    def zeige_tabelle(self):
        kalender = self.option.get()
        if kalender == "REWE":
            fname = "REWE_Saison_Kalender.py"
            erlaubte_werte = ["1", "2", "3"]
            self.df = lade_kalender(fname, erlaubte_werte)
        elif kalender == "EDEKA":
            fname = "EDEKA_Saison_Kalender.py"
            erlaubte_werte = ["1"]
            self.df = lade_kalender(fname, erlaubte_werte)
        else:  # ALLE
            self.df = lade_alle_kalender()

        # Tabelle leeren
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Spalten und Überschriften komplett zurücksetzen
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        self.tree["displaycolumns"] = ()
        self.tree["columns"] = ()

        # Neue Spalten setzen
        if kalender == "ALLE":
            new_cols = ("Gemüse/Obst", "Monate", "Kalender")
        else:
            new_cols = ("Gemüse/Obst", "Monate")
        self.tree["columns"] = new_cols
        self.tree["displaycolumns"] = new_cols
        for col in new_cols:
            self.tree.heading(col, text=col)

        # Neue Daten einfügen
        for _, row in self.df.iterrows():
            if kalender == "ALLE":
                self.tree.insert("", "end", values=(row["Gemüse/Obst"], row["Monate"], row["Kalender"]))
            else:
                self.tree.insert("", "end", values=(row["Gemüse/Obst"], row["Monate"]))

        # Nach dem Einfügen der Daten explizit das Fenster und Treeview updaten
        self.root.update_idletasks()

        # Spaltenbreiten automatisch anpassen (besonders wichtig im Vollbildmodus)
        total_width = self.tree.winfo_width()
        num_cols = len(self.tree["columns"])
        if num_cols > 0 and total_width > 0:
            col_width = int(total_width / num_cols)
            for col in self.tree["columns"]:
                self.tree.column(col, width=col_width)

    def speichern(self):
        if self.df is None or self.df.empty:
            messagebox.showinfo("Hinweis", "Keine Daten zum Speichern.")
            return
        pfad = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel-Datei", "*.xlsx")])
        if pfad:
            try:
                self.df.to_excel(pfad, index=False)
                messagebox.showinfo("Erfolg", f"Datei gespeichert: {pfad}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def zurueck_zum_hauptmenue(self):
        import sys
        if sys.platform.startswith('win') and win32gui is not None and win32con is not None:
            bring_hauptmenue_to_front()
        self.root.destroy()

if __name__ == "__main__":
    dark_mode, fullscreen, themename = lade_settings()
    app = SaisonApp(dark_mode=dark_mode, fullscreen=fullscreen, themename=themename)
    app.root.mainloop()