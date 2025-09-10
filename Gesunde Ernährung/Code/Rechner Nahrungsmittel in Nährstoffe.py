# Button-Funktion zum Addieren aller Werte mit gleichem Namen in der Ausgabe
def addiere_werte_in_ausgabe():
	# Schaltet das Textfeld auf editierbar
	textfeld.config(state='normal')
	# Lese den aktuellen Inhalt des Ausgabefelds
	content = textfeld.get('1.0', tk.END)
	import re
	summen = {}
	# Durchsuche jede Zeile nach dem Muster: Nährstoff   Wert1   Wert2
	for line in content.splitlines():
		match = re.match(r'^(\w[\w\s\-]*)\s+\S+\s+(\S+)$', line)
		if match:
			name = match.group(1).strip()
			try:
				wert = float(match.group(2).replace(',', '.'))
				# Summiere alle Werte mit gleichem Namen
				if name in summen:
					summen[name] += wert
				else:
					summen[name] = wert
			except ValueError:
				continue
	# Schreibe die Summen unter die bisherige Ausgabe
	if summen:
		textfeld.insert(tk.END, '\n--- Summen aller Nährstoffe ---\n')
		max_name = max(len(n) for n in summen.keys())
		max_wert = max(len(f"{v:.2f}") for v in summen.values())
		for name, wert in summen.items():
			textfeld.insert(tk.END, f"{name.ljust(max_name)}   {str(f'{wert:.2f}').rjust(max_wert)}\n")
	else:
		textfeld.insert(tk.END, '\nKeine summierbaren Werte gefunden.\n')
	# Setze das Textfeld wieder auf nicht editierbar
	textfeld.config(state='disabled')
# Funktion zum Leeren des Ausgabefelds
def clear_output():
	# Setzt das Textfeld zurück (löscht alle Ausgaben)
	textfeld.config(state='normal')
	textfeld.delete('1.0', tk.END)
	textfeld.config(state='disabled')
	# Summen-Button wieder einblenden
	if not btn_sum.winfo_ismapped():
		btn_sum.pack(side='left', padx=(0, 10))
from tkinter import filedialog
def speichere_ergebnisse():
    # Hole den aktuellen Inhalt des Ausgabefelds
    textfeld.config(state='normal')
    inhalt = textfeld.get('1.0', tk.END).strip()
    textfeld.config(state='disabled')
    if not inhalt:
        messagebox.showinfo('Hinweis', 'Keine Ausgabedaten zum Speichern.')
        return

    # Erstelle einen Dateinamen, der die gewählten Lebensmittel enthält
    lebensmittel_namen = []
    for frame in auswahl_frames:
        children = frame.winfo_children()
        for child in children:
            if isinstance(child, tb.Combobox):
                name = child.get()
                if name and name not in lebensmittel_namen:
                    lebensmittel_namen.append(name)
    lebensmittel_kurz = lebensmittel_namen[:3]
    lebensmittel_str = "_".join([n.replace(" ", "_") for n in lebensmittel_kurz])
    if lebensmittel_str:
        default_filename = f"Naehrwerte_Ausgabe_{lebensmittel_str}.txt"
    else:
        default_filename = "Naehrwerte_Ausgabe.txt"

    save_path = filedialog.asksaveasfilename(
        defaultextension='.txt',
        filetypes=[('Textdateien', '*.txt'), ('Alle Dateien', '*.*')],
        initialfile=default_filename,
        title='Speicherort für Ergebnisse wählen'
    )
    if not save_path:
        return
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(inhalt + '\n')
        messagebox.showinfo('Gespeichert', f'Ergebnisse gespeichert unter:\n{save_path}')
    except Exception as e:
        messagebox.showerror('Fehler', f'Fehler beim Speichern:\n{e}')


import pandas as pd
import os
import sys
import argparse
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
import platform
try:
	import win32gui
	import win32con
except ImportError:
	win32gui = None
	win32con = None
import json


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



# Excel-Datei laden mit Fehlerbehandlung
try:
	# Bestimme den Pfad zur Excel-Datei relativ zum Skript
	excel_path = os.path.join(
		os.path.dirname(__file__),
		'..', 'Quellen', 'Nährstoffe in X', 'lebensmittel-naehrstoffe.de', 'Gefilterte_Kategorien_zusammengefuegt.xlsx'
	)
	# Lese die Excel-Datei mit pandas ein
	df = pd.read_excel(excel_path)
except Exception as e:
	print(f"Fehler beim Laden der Excel-Datei: {e}")
	messagebox.showerror('Fehler', f'Excel-Datei konnte nicht geladen werden:\n{e}')
	sys.exit(1)

# Lebensmittel-Liste für Dropdown-Menüs erstellen
try:
	lebensmittel_liste = df['Lebensmittel'].dropna().unique().tolist()
	if not lebensmittel_liste:
		raise ValueError('Keine Lebensmittel gefunden!')
except Exception as e:
	print(f"Fehler beim Erstellen der Lebensmittel-Liste: {e}")
	messagebox.showerror('Fehler', f'Keine Lebensmittel gefunden:\n{e}')
	sys.exit(1)






NAEHRSTOFFE_TITLE = 'RechnerNaehrstoffeFenster2025'

try:
	root = tb.Window(themename=themename)
except Exception:
	root = tk.Tk()
root.title(NAEHRSTOFFE_TITLE)
root.geometry('800x550')
if fullscreen:
	root.attributes('-fullscreen', True)
	# Remove window border only on Windows
	if platform.system() == "Windows":
		root.overrideredirect(True)  # Entfernt die Fensterleiste im Vollbildmodus
		# Remove menu only if it exists
		try:
			root.config(menu=tk.Menu(root))
		except Exception:
			pass
root.lift()
root.focus_force()


# --- Hauptfenster --- (ab hier ersetzen!)

# --- Dynamische Auswahlfelder in eigenem Container ---
auswahl_frames = []
auswahl_container = tb.Frame(root)
auswahl_container.pack(padx=10, pady=(10, 0), fill='x')

def add_auswahl_frame(first=False):
    frame = tb.Frame(auswahl_container)
    frame.pack(padx=0, pady=2, fill='x')
    auswahl_frames.append(frame)

    # Dropdown für Lebensmittel mit Suchfunktion (dynamische Filterung)
    tb.Label(frame, text='Lebensmittel auswählen:').pack(side='left', padx=(0,5))
    combo_var = tk.StringVar()
    combo = tb.Combobox(frame, textvariable=combo_var, values=lebensmittel_liste, width=40)
    combo.pack(side='left', padx=(0,5))

    # Dynamische Filterung beim Tippen
    def on_keyrelease(event):
        value = combo_var.get().lower()
        if value == '':
            combo['values'] = lebensmittel_liste
        else:
            filtered = [item for item in lebensmittel_liste if value in item.lower()]
            combo['values'] = filtered
    combo.bind('<KeyRelease>', on_keyrelease)

    # Eingabefeld für Menge
    tb.Label(frame, text='Menge (g):').pack(side='left', padx=(0,5))
    menge_var = tk.StringVar(value='100')
    menge_entry = tb.Entry(frame, textvariable=menge_var, width=8)
    menge_entry.pack(side='left')

    # Button für diese Auswahl
    btn = tb.Button(frame, text='Nährstoffe anzeigen', command=lambda: zeige_naehrstoffe(combo, menge_var))
    btn.pack(side='left', padx=(10,0))

    # + Button jetzt rechts neben "Nährstoffe anzeigen"
    if first:
        btn_add = tb.Button(frame, text='+', width=2, command=add_auswahl_frame)
        btn_add.pack(side='left', padx=(10,0))

    # Entfernen-Button für weitere Auswahlfelder
    if len(auswahl_frames) > 1:
        btn_remove = tb.Button(frame, text='–', width=2, command=lambda: remove_auswahl_frame(frame))
        btn_remove.pack(side='left', padx=(5,0))

def remove_auswahl_frame(frame):
    frame.destroy()
    auswahl_frames.remove(frame)

# Nur das erste Auswahlfeld wird initial hinzugefügt
add_auswahl_frame(first=True)

# --- Textfeld für die Ausgabe ---
textfeld = tk.Text(root, width=80, height=20, state='disabled', wrap='word')
textfeld.pack(padx=10, pady=10, fill='both', expand=True)

# --- Buttons ganz unten nebeneinander ---
frame_buttons_unten = tb.Frame(root)
frame_buttons_unten.pack(side='bottom', fill='x', padx=10, pady=10)

btn_save = tb.Button(frame_buttons_unten, text='Ergebnisse speichern', command=speichere_ergebnisse)
btn_save.pack(side='left', padx=(0, 10))
btn_clear = tb.Button(frame_buttons_unten, text='Ausgabe leeren', command=clear_output)
btn_clear.pack(side='left', padx=(0, 10))

def sum_button_action():
    addiere_werte_in_ausgabe()
    btn_sum.pack_forget()

btn_sum = tb.Button(frame_buttons_unten, text='Summen berechnen', command=sum_button_action)
btn_sum.pack(side='left', padx=(0, 10))

# --- Hauptmenü-Button ---
def bring_hauptmenue_to_front(window_title='MeinErnaehrungsHauptmenue2025'):
	if win32gui is None:
		# On Linux/Mac, just pass (no window focus possible)
		return
	def enumHandler(hwnd, lParam):
		if win32gui is not None and win32con is not None and win32gui.IsWindowVisible(hwnd):
			if window_title in win32gui.GetWindowText(hwnd):
				win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
				win32gui.SetForegroundWindow(hwnd)
	if win32gui is not None and win32con is not None:
		win32gui.EnumWindows(enumHandler, None)

def zurueck_zum_hauptmenue():
    bring_hauptmenue_to_front()
    root.destroy()

btn_hauptmenue = tb.Button(frame_buttons_unten, text='Verlassen', command=zurueck_zum_hauptmenue)
btn_hauptmenue.pack(side='right', padx=(0, 10))


# --- Menüleiste nur anzeigen, wenn nicht fullscreen ---
if not fullscreen:
	menue_leiste = tb.Menu(root)

	# --- Datei-Menü ---
	def datei_oeffnen():
		pass  # Hier kann die Funktion zum Öffnen einer Datei implementiert werden

	def datei_speichern():
		speichere_ergebnisse()

	def beenden():
		root.quit()

	datei_menu = tb.Menu(menue_leiste, tearoff=0)
	datei_menu.add_command(label="Öffnen", command=datei_oeffnen)
	datei_menu.add_command(label="Speichern", command=datei_speichern)
	datei_menu.add_separator()
	datei_menu.add_command(label="Beenden", command=beenden)
	menue_leiste.add_cascade(label="Datei", menu=datei_menu)

	# --- Hilfe-Menü ---
	def hilfe_anzeigen():
		messagebox.showinfo("Hilfe", "Hier könnte Ihre Hilfe stehen.")

	hilfe_menu = tb.Menu(menue_leiste, tearoff=0)
	hilfe_menu.add_command(label="Inhalt", command=hilfe_anzeigen)
	menue_leiste.add_cascade(label="Hilfe", menu=hilfe_menu)

	# Menüleiste anwenden
	root.config(menu=menue_leiste)


# --- Hauptmenü-Button ---
def bring_hauptmenue_to_front(window_title='MeinErnaehrungsHauptmenue2025'):
	if win32gui is None:
		# On Linux/Mac, just pass (no window focus possible)
		return
	def enumHandler(hwnd, lParam):
		if win32gui is not None and win32con is not None and win32gui.IsWindowVisible(hwnd):
			if window_title in win32gui.GetWindowText(hwnd):
				win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
				win32gui.SetForegroundWindow(hwnd)
	if win32gui is not None and win32con is not None:
		win32gui.EnumWindows(enumHandler, None)

def zurueck_zum_hauptmenue():
    # Hauptmenü-Fenster wiederherstellen und in den Vordergrund bringen (ohne PowerShell, mit pywin32)
    bring_hauptmenue_to_front()
    root.destroy()

def zeige_naehrstoffe(combo, menge_var):
	lebensmittel = combo.get()
	try:
		menge = float(menge_var.get().replace(',', '.'))
	except Exception:
		menge = 100.0
	if not lebensmittel or lebensmittel not in df['Lebensmittel'].values:
		messagebox.showwarning("Hinweis", "Bitte ein gültiges Lebensmittel auswählen.")
		return
	zeile = df[df['Lebensmittel'] == lebensmittel]
	if zeile.empty:
		messagebox.showwarning("Hinweis", "Keine Daten für dieses Lebensmittel gefunden.")
		return
	spalten = df.columns[2:]
	ergebnis_liste = []
	used_names = set()
	def base_name(name):
		# Nur der Teil vor erstem '_' oder erstem ' (' oder erstem ':'
		for sep in ['_', ' (', ':']:
			if sep in name:
				return name.split(sep)[0].strip()
		return name.strip()
	for spalte in spalten:
		spaltenname = str(spalte).strip()
		base = base_name(spaltenname)
		if base in used_names:
			continue
		wert = zeile.iloc[0][spalte]
		if pd.notna(wert):
			try:
				wert = float(str(wert).replace(',', '.'))
				berechnet = wert / 100 * menge
				ergebnis_liste.append(f"{spaltenname}: {berechnet:.2f}")
				used_names.add(base)
			except Exception:
				continue
	# Schreibe ins Textfeld
	textfeld.config(state='normal')
	textfeld.insert(tk.END, f"{lebensmittel} ({menge}g):\n")
	for zeile in ergebnis_liste:
		textfeld.insert(tk.END, zeile + "\n")
	textfeld.insert(tk.END, "\n")
	textfeld.config(state='disabled')

# --- Hauptfenster anzeigen ---
root.mainloop()

