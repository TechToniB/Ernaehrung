# Button-Funktion zum Addieren aller Werte mit gleichem Namen in der Ausgabe
def addiere_werte_in_ausgabe():
	textfeld.config(state='normal')
	content = textfeld.get('1.0', tk.END)
	import re
	summen = {}
	# Zeilen mit Muster: Nährstoff   Wert1   Wert2
	for line in content.splitlines():
		match = re.match(r'^(\w[\w\s\-]*)\s+\S+\s+(\S+)$', line)
		if match:
			name = match.group(1).strip()
			try:
				wert = float(match.group(2).replace(',', '.'))
				if name in summen:
					summen[name] += wert
				else:
					summen[name] = wert
			except ValueError:
				continue
	if summen:
		textfeld.insert(tk.END, '\n--- Summen aller Nährstoffe ---\n')
		max_name = max(len(n) for n in summen.keys())
		max_wert = max(len(f"{v:.2f}") for v in summen.values())
		for name, wert in summen.items():
			textfeld.insert(tk.END, f"{name.ljust(max_name)}   {str(f'{wert:.2f}').rjust(max_wert)}\n")
	else:
		textfeld.insert(tk.END, '\nKeine summierbaren Werte gefunden.\n')
	textfeld.config(state='disabled')
# Funktion zum Leeren des Ausgabefelds
def clear_output():
	textfeld.config(state='normal')
	textfeld.delete('1.0', tk.END)
	textfeld.config(state='disabled')
from tkinter import filedialog
# Funktion zum Speichern der Ergebnisse in eine Datei

def speichere_ergebnisse():
	# Sammle alle Auswahlen aus den Auswahl-Frames
	alle_ergebnisse = []
	for frame in auswahl_frames:
		children = frame.winfo_children()
		combo = None
		menge_entry = None
		for child in children:
			if isinstance(child, ttk.Combobox):
				combo = child
			if isinstance(child, ttk.Entry):
				menge_entry = child
		if combo is None or menge_entry is None:
			continue
		auswahl = combo.get()
		menge_str = menge_entry.get()
		try:
			menge = float(menge_str.replace(',', '.'))
			if menge <= 0:
				continue
		except Exception:
			continue
		if not auswahl:
			continue
		zeile = df[df['Lebensmittel'] == auswahl]
		if zeile.empty:
			continue
		spalten = df.columns[2:]
		werte_liste = []
		for spalte in spalten:
			wert = zeile.iloc[0][spalte]
			if pd.notna(wert):
				try:
					if isinstance(wert, (int, float)) and not isinstance(wert, bool):
						werte_liste.append((spalte, float(wert)))
					else:
						float_wert = float(str(wert).replace(',', '.'))
						werte_liste.append((spalte, float_wert))
				except (ValueError, TypeError):
					continue
		if not werte_liste:
			continue
		# Dopplungen filtern wie in der Anzeige
		import re
		filtered = []
		werte_dict = {}
		for spalte, wert in werte_liste:
			if pd.isna(wert):
				continue
			wert_str = str(wert)
			if wert_str not in werte_dict:
				werte_dict[wert_str] = [spalte]
			else:
				werte_dict[wert_str].append(spalte)
		for wert_str, spalten_namen in werte_dict.items():
			kuerzester = min(spalten_namen, key=len)
			filtered.append((kuerzester, float(wert_str)))
		# Nur Spalte 3 (berechneter Wert für Menge) speichern
		ergebnis_liste = []
		for spalte, wert in filtered:
			berechnet = wert / 100 * menge
			ergebnis_liste.append(f"{spalte}: {berechnet:.2f}")
		if ergebnis_liste:
			alle_ergebnisse.append(f"{auswahl} ({menge}g):\n" + '\n'.join(ergebnis_liste) + '\n')
	if not alle_ergebnisse:
		messagebox.showinfo('Hinweis', 'Keine berechneten Werte zum Speichern.')
		return
	# Dialog zum Auswählen des Speicherorts
	default_filename = "Naehrwerte_Auswahl.txt"
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
			for block in alle_ergebnisse:
				f.write(block + '\n')
		messagebox.showinfo('Gespeichert', f'Ergebnisse gespeichert unter:\n{save_path}')
	except Exception as e:
		messagebox.showerror('Fehler', f'Fehler beim Speichern:\n{e}')


import pandas as pd
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys

# Excel-Datei laden mit Fehlerausgabe
try:
	excel_path = os.path.join(
		os.path.dirname(__file__),
		'..', 'Quellen', 'Nährstoffe in X', 'lebensmittel-naehrstoffe.de', 'Gefilterte_Kategorien_zusammengefuegt.xlsx'
	)
	df = pd.read_excel(excel_path)
except Exception as e:
	print(f"Fehler beim Laden der Excel-Datei: {e}")
	messagebox.showerror('Fehler', f'Excel-Datei konnte nicht geladen werden:\n{e}')
	sys.exit(1)

# Lebensmittel-Liste für Dropdown
try:
	lebensmittel_liste = df['Lebensmittel'].dropna().unique().tolist()
	if not lebensmittel_liste:
		raise ValueError('Keine Lebensmittel gefunden!')
except Exception as e:
	print(f"Fehler beim Erstellen der Lebensmittel-Liste: {e}")
	messagebox.showerror('Fehler', f'Keine Lebensmittel gefunden:\n{e}')
	sys.exit(1)

# --- GUI erstellen ---
root = tk.Tk()
root.title('Nährstoffanzeige')

# Fenstergröße anpassen
root.geometry('800x550')


# --- Dynamische Auswahlfelder in eigenem Container ---
auswahl_frames = []
auswahl_container = ttk.Frame(root)
auswahl_container.pack(padx=10, pady=(10, 0), fill='x')

def add_auswahl_frame(first=False):
	frame = ttk.Frame(auswahl_container)
	frame.pack(padx=0, pady=2, fill='x')
	auswahl_frames.append(frame)

	ttk.Label(frame, text='Lebensmittel auswählen:').pack(side='left', padx=(0,5))
	combo = ttk.Combobox(frame, values=lebensmittel_liste, state='readonly', width=40)
	combo.pack(side='left', padx=(0,10))

	ttk.Label(frame, text='Menge (g):').pack(side='left', padx=(0,5))
	menge_var = tk.StringVar(value='100')
	menge_entry = ttk.Entry(frame, textvariable=menge_var, width=8)
	menge_entry.pack(side='left')

	btn = ttk.Button(frame, text='Nährstoffe anzeigen', command=lambda: zeige_naehrstoffe(combo, menge_var))
	btn.pack(side='left', padx=(10,0))

	# + Button nur beim ersten Frame
	if first:
		btn_add = ttk.Button(frame, text='+', width=2, command=add_auswahl_frame)
		btn_add.pack(side='left', padx=(10,0))

	if len(auswahl_frames) > 1:
		btn_remove = ttk.Button(frame, text='–', width=2, command=lambda: remove_auswahl_frame(frame))
		btn_remove.pack(side='left', padx=(5,0))

def remove_auswahl_frame(frame):
	frame.destroy()
	auswahl_frames.remove(frame)

add_auswahl_frame(first=True)


# Größeres Textfeld
textfeld = tk.Text(root, width=80, height=25, state='disabled', wrap='word')
textfeld.pack(padx=10, pady=10, fill='both', expand=True)

# Angepasste Funktion für mehrere Auswahlen
def zeige_naehrstoffe(combo, menge_var):
	auswahl = combo.get()
	menge_str = menge_var.get()
	try:
		menge = float(menge_str.replace(',', '.'))
		if menge <= 0:
			raise ValueError
	except Exception:
		messagebox.showinfo('Hinweis', 'Bitte eine gültige Menge eingeben.')
		return
	if not auswahl:
		messagebox.showinfo('Hinweis', 'Bitte ein Lebensmittel auswählen.')
		return
	zeile = df[df['Lebensmittel'] == auswahl]
	if zeile.empty:
		messagebox.showinfo('Hinweis', 'Keine Daten gefunden.')
		return
	spalten = df.columns[2:]
	infos = []
	max_spaltenname = 0
	werte_liste = []
	for spalte in spalten:
		wert = zeile.iloc[0][spalte]
		if pd.notna(wert):
			try:
				if isinstance(wert, (int, float)) and not isinstance(wert, bool):
					werte_liste.append((spalte, float(wert)))
				else:
					float_wert = float(str(wert).replace(',', '.'))
					werte_liste.append((spalte, float_wert))
			except (ValueError, TypeError):
				continue
	if werte_liste:
		import re
		filtered = []
		werte_dict = {}
		for spalte, wert in werte_liste:
			if pd.isna(wert):
				continue
			wert_str = str(wert)
			if wert_str not in werte_dict:
				werte_dict[wert_str] = [spalte]
			else:
				werte_dict[wert_str].append(spalte)
		for wert_str, spalten_namen in werte_dict.items():
			kuerzester = min(spalten_namen, key=len)
			filtered.append((kuerzester, float(wert_str)))
		if filtered:
			sep = '   '
			max_spaltenname = max(len(str(s[0])) for s in filtered)
			max_wert = max(len(f"{s[1]:.2f}") for s in filtered)
			max_berechnet = max(len(f"{s[1]/100*menge:.2f}") for s in filtered)
			header = f"{'Nährstoff'.ljust(max_spaltenname)}{sep}{'pro 100g'.rjust(max_wert)}{sep}{'für Menge'.rjust(max_berechnet)}"
			infos.append(header)
			infos.append('-' * len(header))
			for spalte, wert in filtered:
				berechnet = wert / 100 * menge
				infos.append(f"{spalte.ljust(max_spaltenname)}{sep}{f'{wert:.2f}'.rjust(max_wert)}{sep}{f'{berechnet:.2f}'.rjust(max_berechnet)}")
	if infos:
		# Ausgabe für mehrere Auswahlen anhängen
		textfeld.config(state='normal')
		textfeld.insert(tk.END, f"\n{auswahl} ({menge}g):\n")
		textfeld.insert(tk.END, '\n'.join(infos) + '\n')
		textfeld.config(state='disabled')
	else:
		textfeld.config(state='normal')
		textfeld.insert(tk.END, f"\n{auswahl} ({menge}g): Keine Nährstoffdaten vorhanden.\n")
		textfeld.config(state='disabled')
		textfeld.delete('1.0', tk.END)
		textfeld.insert(tk.END, 'Keine Nährstoffdaten vorhanden.')
		textfeld.config(state='disabled')


# Buttons nebeneinander in einem Frame
frame_buttons = ttk.Frame(root)
frame_buttons.pack(padx=10, pady=5)
btn_save = ttk.Button(frame_buttons, text='Ergebnisse speichern', command=speichere_ergebnisse)
btn_save.pack(side='left', padx=(0, 10))
# Clear-Button
btn_clear = ttk.Button(frame_buttons, text='Ausgabe leeren', command=clear_output)
btn_clear.pack(side='left', padx=(0, 10))
# Summen-Button
btn_sum = ttk.Button(frame_buttons, text='Summen berechnen', command=addiere_werte_in_ausgabe)
btn_sum.pack(side='left', padx=(0, 10))

root.mainloop()

# --- GUI erstellen ---
root = tk.Tk()

# --- Dynamische Auswahlfelder in eigenem Container ---
auswahl_frames = []
auswahl_container = ttk.Frame(root)
auswahl_container.pack(padx=10, pady=(10, 0), fill='x')

def add_auswahl_frame(first=False):
	frame = ttk.Frame(auswahl_container)
	frame.pack(padx=0, pady=2, fill='x')
	auswahl_frames.append(frame)

	ttk.Label(frame, text='Lebensmittel auswählen:').pack(side='left', padx=(0,5))
	combo = ttk.Combobox(frame, values=lebensmittel_liste, state='readonly', width=40)
	combo.pack(side='left', padx=(0,10))

	ttk.Label(frame, text='Menge (g):').pack(side='left', padx=(0,5))
	menge_var = tk.StringVar(value='100')
	menge_entry = ttk.Entry(frame, textvariable=menge_var, width=8)
	menge_entry.pack(side='left')

	btn = ttk.Button(frame, text='Nährstoffe anzeigen', command=lambda: zeige_naehrstoffe(combo, menge_var))
	btn.pack(side='left', padx=(10,0))

	# + Button nur beim ersten Frame
	if first:
		btn_add = ttk.Button(frame, text='+', width=2, command=add_auswahl_frame)
		btn_add.pack(side='left', padx=(10,0))

	if len(auswahl_frames) > 1:
		btn_remove = ttk.Button(frame, text='–', width=2, command=lambda: remove_auswahl_frame(frame))
		btn_remove.pack(side='left', padx=(5,0))

def remove_auswahl_frame(frame):
	frame.destroy()
	auswahl_frames.remove(frame)

add_auswahl_frame(first=True)