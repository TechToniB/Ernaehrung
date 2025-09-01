

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
root.geometry('700x500')

# Layout: Dropdown und Mengeneingabe nebeneinander
frame_top = ttk.Frame(root)
frame_top.pack(padx=10, pady=5, fill='x')

ttk.Label(frame_top, text='Lebensmittel auswählen:').pack(side='left', padx=(0,5))
combo = ttk.Combobox(frame_top, values=lebensmittel_liste, state='readonly', width=40)
combo.pack(side='left', padx=(0,10))

ttk.Label(frame_top, text='Menge (g):').pack(side='left', padx=(0,5))
menge_var = tk.StringVar(value='100')
menge_entry = ttk.Entry(frame_top, textvariable=menge_var, width=8)
menge_entry.pack(side='left')

# Größeres Textfeld
textfeld = tk.Text(root, width=80, height=25, state='disabled', wrap='word')
textfeld.pack(padx=10, pady=10, fill='both', expand=True)

# --- KORREKTE FUNKTION: zeige_naehrstoffe ---
def zeige_naehrstoffe():
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
	# Nur Spalten anzeigen, deren Wert eine Zahl ist (keine Kategorien oder Textwerte)
	spalten = df.columns[2:]
	infos = []
	max_spaltenname = 0
	werte_liste = []
	# Sammle alle passenden Spalten und Werte
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
		# Dopplungen filtern: Wenn ein Wert mehrfach vorkommt und der Spaltenname eine längere Version eines anderen ist, nur den kürzesten anzeigen
		import re
		filtered = []
		werte_dict = {}
		for spalte, wert in werte_liste:
			if pd.isna(wert):
				continue
			wert_str = str(wert)
			# Finde alle bisherigen Namen mit gleichem Wert
			if wert_str not in werte_dict:
				werte_dict[wert_str] = [spalte]
			else:
				werte_dict[wert_str].append(spalte)
		# Für jeden Wert nur den kürzesten Namen behalten
		for wert_str, spalten_namen in werte_dict.items():
			kuerzester = min(spalten_namen, key=len)
			filtered.append((kuerzester, float(wert_str)))
		if filtered:
			max_spaltenname = max(len(str(s[0])) for s in filtered)
			max_wert = max(len(f"{s[1]:.2f}") for s in filtered)
			max_berechnet = max(len(f"{s[1]/100*menge:.2f}") for s in filtered)
			sep = '   '  # Mehr Abstand zwischen den Spalten
			header = f"{'Nährstoff'.ljust(max_spaltenname)}{sep}{sep}{'pro 100g'.rjust(max_wert)}{sep}{sep}{'für Menge'.rjust(max_berechnet)}"
			infos.append(header)
			infos.append('-' * len(header))
			for spalte, wert in filtered:
				berechnet = wert / 100 * menge
				infos.append(f"{spalte.ljust(max_spaltenname)}{sep}{f'{wert:.2f}'.rjust(max_wert)}{sep}{f'{berechnet:.2f}'.rjust(max_berechnet)}")
	if infos:
		textfeld.config(state='normal')
		textfeld.delete('1.0', tk.END)
		textfeld.insert(tk.END, '\n'.join(infos))
		textfeld.config(state='disabled')
	else:
		textfeld.config(state='normal')
		textfeld.delete('1.0', tk.END)
		textfeld.insert(tk.END, 'Keine Nährstoffdaten vorhanden.')
		textfeld.config(state='disabled')

# Button nach Funktionsdefinition
btn = ttk.Button(root, text='Nährstoffe anzeigen', command=zeige_naehrstoffe)
btn.pack(padx=10, pady=5)

root.mainloop()

# --- GUI erstellen ---
root = tk.Tk()
root.title('Nährstoffanzeige')