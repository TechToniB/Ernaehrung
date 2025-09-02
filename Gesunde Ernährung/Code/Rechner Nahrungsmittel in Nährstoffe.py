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
	# Gehe alle Auswahl-Frames durch und sammle die Ergebnisse
	alle_ergebnisse = []
	for frame in auswahl_frames:
		children = frame.winfo_children()
		combo = None
		menge_entry = None
		# Finde das Dropdown und das Mengenfeld im Frame
		for child in children:
			# Prüfe auf AutocompleteCombobox und tb.Entry
			if isinstance(child, AutocompleteCombobox):
				combo = child
			if isinstance(child, tb.Entry):
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
		# Filtere die Zeile für das gewählte Lebensmittel
		zeile = df[df['Lebensmittel'] == auswahl]
		if zeile.empty:
			continue
		spalten = df.columns[2:]
		werte_liste = []
		# Sammle alle Nährstoffwerte
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
		# Berechne die Werte für die gewählte Menge
		ergebnis_liste = []
		for spalte, wert in filtered:
			berechnet = wert / 100 * menge
			ergebnis_liste.append(f"{spalte}: {berechnet:.2f}")
		if ergebnis_liste:
			alle_ergebnisse.append(f"{auswahl} ({menge}g):\n" + '\n'.join(ergebnis_liste) + '\n')
	if not alle_ergebnisse:
		messagebox.showinfo('Hinweis', 'Keine berechneten Werte zum Speichern.')
		return
	# Summen wie im Summen-Button berechnen
	# Wir sammeln alle Zeilen aus alle_ergebnisse, die wie eine Nährstoffzeile aussehen
	import re
	summen = {}
	for block in alle_ergebnisse:
		for line in block.splitlines():
			match = re.match(r'^(\w[\w\s\-]*)[:]?\s+([\d\.,]+)$', line)
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
	# Erstelle einen Dateinamen, der die gewählten Lebensmittel enthält
	lebensmittel_namen = []
	for frame in auswahl_frames:
		children = frame.winfo_children()
		for child in children:
			if isinstance(child, AutocompleteCombobox):
				name = child.get()
				if name and name not in lebensmittel_namen:
					lebensmittel_namen.append(name)
	# Nur die ersten 3 Namen für den Dateinamen verwenden, um ihn nicht zu lang zu machen
	lebensmittel_kurz = lebensmittel_namen[:3]
	lebensmittel_str = "_".join([n.replace(" ", "_") for n in lebensmittel_kurz])
	if lebensmittel_str:
		default_filename = f"Naehrwerte_Auswahl_{lebensmittel_str}.txt"
	else:
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
			# Summen anhängen, falls vorhanden
			if summen:
				f.write('\n--- Summen aller Nährstoffe ---\n')
				max_name = max(len(n) for n in summen.keys())
				max_wert = max(len(f"{v:.2f}") for v in summen.values())
				for name, wert in summen.items():
					f.write(f"{name.ljust(max_name)}   {str(f'{wert:.2f}').rjust(max_wert)}\n")
		messagebox.showinfo('Gespeichert', f'Ergebnisse gespeichert unter:\n{save_path}')
	except Exception as e:
		messagebox.showerror('Fehler', f'Fehler beim Speichern:\n{e}')


import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox
import sys
# Importiere ttkbootstrap (nur für Theme, nicht für Combobox)
import ttkbootstrap as tb


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

# --- GUI erstellen ---
root = tb.Window(themename="flatly")
root.title('Nährstoffanzeige')
# Fenstergröße anpassen
root.geometry('800x550')


# --- Dynamische Auswahlfelder in eigenem Container ---
auswahl_frames = []
auswahl_container = tb.Frame(root)
auswahl_container.pack(padx=10, pady=(10, 0), fill='x')

# Funktion zum Hinzufügen eines neuen Auswahlfeldes (Dropdown + Menge + Buttons)
def add_auswahl_frame(first=False):
	frame = tb.Frame(auswahl_container)
	frame.pack(padx=0, pady=2, fill='x')
	auswahl_frames.append(frame)


	# Dropdown für Lebensmittel mit Suchfunktion (dynamische Filterung)
	tb.Label(frame, text='Lebensmittel auswählen:').pack(side='left', padx=(0,5))
	combo_var = tk.StringVar()
	combo = tb.Combobox(frame, textvariable=combo_var, values=lebensmittel_liste, width=40)
	combo.pack(side='left', padx=(0,10))

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

	# + Button nur beim ersten Frame
	if first:
		btn_add = tb.Button(frame, text='+', width=2, command=add_auswahl_frame)
		btn_add.pack(side='left', padx=(10,0))

	# Entfernen-Button für weitere Auswahlfelder
	if len(auswahl_frames) > 1:
		btn_remove = tb.Button(frame, text='–', width=2, command=lambda: remove_auswahl_frame(frame))
		btn_remove.pack(side='left', padx=(5,0))

# Funktion zum Entfernen eines Auswahlfeldes
def remove_auswahl_frame(frame):
	frame.destroy()
	auswahl_frames.remove(frame)

# Füge das erste Auswahlfeld hinzu
add_auswahl_frame(first=True)


# Größeres Textfeld für die Ausgabe
textfeld = tk.Text(root, width=80, height=25, state='disabled', wrap='word')
textfeld.pack(padx=10, pady=10, fill='both', expand=True)

# Angepasste Funktion für mehrere Auswahlen
def zeige_naehrstoffe(combo, menge_var):
	# Lese die Auswahl und Menge aus dem jeweiligen Frame
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
	# Filtere die Zeile für das gewählte Lebensmittel
	zeile = df[df['Lebensmittel'] == auswahl]
	if zeile.empty:
		messagebox.showinfo('Hinweis', 'Keine Daten gefunden.')
		return
	spalten = df.columns[2:]
	infos = []
	max_spaltenname = 0
	werte_liste = []
	# Sammle alle Nährstoffwerte
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
		# Dopplungen filtern: nur den kürzesten Spaltennamen pro Wert behalten
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
			# Kopfzeile und Werte formatiert ausgeben
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

frame_buttons = tb.Frame(root)
frame_buttons.pack(padx=10, pady=5)
# Button zum Speichern der Ergebnisse
btn_save = tb.Button(frame_buttons, text='Ergebnisse speichern', command=speichere_ergebnisse)
btn_save.pack(side='left', padx=(0, 10))
# Button zum Leeren der Ausgabe
btn_clear = tb.Button(frame_buttons, text='Ausgabe leeren', command=clear_output)
btn_clear.pack(side='left', padx=(0, 10))

# Button zum Berechnen der Summen (wird dynamisch ein-/ausgeblendet)
def sum_button_action():
	addiere_werte_in_ausgabe()
	btn_sum.pack_forget()  # Button ausblenden

btn_sum = tb.Button(frame_buttons, text='Summen berechnen', command=sum_button_action)
btn_sum.pack(side='left', padx=(0, 10))

root.mainloop()

# --- GUI erstellen ---
root = tk.Tk()

# --- Dynamische Auswahlfelder in eigenem Container ---
auswahl_frames = []
auswahl_container = tb.Frame(root)
auswahl_container.pack(padx=10, pady=(10, 0), fill='x')

def add_auswahl_frame(first=False):
	frame = tb.Frame(auswahl_container)
	frame.pack(padx=0, pady=2, fill='x')
	auswahl_frames.append(frame)

	tb.Label(frame, text='Lebensmittel auswählen:').pack(side='left', padx=(0,5))
	# (AutocompleteCombobox wird bereits verwendet)

	tb.Label(frame, text='Menge (g):').pack(side='left', padx=(0,5))
	menge_var = tk.StringVar(value='100')
	menge_entry = tb.Entry(frame, textvariable=menge_var, width=8)
	menge_entry.pack(side='left')

	btn = tb.Button(frame, text='Nährstoffe anzeigen', command=lambda: zeige_naehrstoffe(combo, menge_var))
	btn.pack(side='left', padx=(10,0))

	# + Button nur beim ersten Frame
	if first:
		btn_add = tb.Button(frame, text='+', width=2, command=add_auswahl_frame)
		btn_add.pack(side='left', padx=(10,0))

	if len(auswahl_frames) > 1:
		btn_remove = tb.Button(frame, text='–', width=2, command=lambda: remove_auswahl_frame(frame))
		btn_remove.pack(side='left', padx=(5,0))

def remove_auswahl_frame(frame):
	frame.destroy()
	auswahl_frames.remove(frame)

add_auswahl_frame(first=True)