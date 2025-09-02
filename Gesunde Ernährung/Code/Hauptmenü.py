import tkinter as tk
import ttkbootstrap as tb
import subprocess
import os
import sys
import psutil
import json

import json

def open_script(script_name):
	# Öffnet das gewünschte Python-Skript in einem neuen Prozess, aber nur wenn es noch nicht läuft
	script_path = os.path.join(os.path.dirname(__file__), script_name)

	# Prüfen, ob das Skript bereits läuft
	for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
		try:
			cmdline = proc.info['cmdline']
			if cmdline and script_path in cmdline:
				return  # Bereits laufend, nichts tun
		except (psutil.NoSuchProcess, psutil.AccessDenied):
			continue

	# Lese Dark Mode Einstellung
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
	dark_mode = False
	if os.path.exists(settings_path):
		try:
			with open(settings_path, 'r', encoding='utf-8') as f:
				settings = json.load(f)
				dark_mode = settings.get('dark_mode', False)
		except Exception:
			pass

	# Übergib dark_mode als Argument
	args = [sys.executable, script_path]
	if dark_mode:
		args.append('--dark')
	subprocess.Popen(args)

def main():
	# Lese Dark Mode Einstellung
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
	dark_mode = False
	if os.path.exists(settings_path):
		try:
			with open(settings_path, 'r', encoding='utf-8') as f:
				settings = json.load(f)
				dark_mode = settings.get('dark_mode', False)
		except Exception:
			pass

	themename = "darkly" if dark_mode else "flatly"
	root = tb.Window(themename=themename)
	root.title('Hauptmenü')
	root.geometry('400x300')

	label = tb.Label(root, text="Bitte wählen Sie eine Funktion:", font=("Arial", 14))
	label.pack(pady=20)

	# Button Style für Dark Mode
	btn_style = "darkly.TButton" if dark_mode else "TButton"

	# Button für Rechner Import
	btn_import = tb.Button(root, text="Rechner Import",
		command=lambda: open_script('Rechner Import.py'), style=btn_style)
	btn_import.pack(pady=10, fill='x', padx=40)

	# Button für Rechner Nahrungsmittel in Nährstoffe
	btn_naehrstoffe = tb.Button(root, text="Rechner Nahrungsmittel in Nährstoffe",
		command=lambda: open_script('Rechner Nahrungsmittel in Nährstoffe.py'), style=btn_style)
	btn_naehrstoffe.pack(pady=10, fill='x', padx=40)

	# Einstellungs-Menü als eigenes Fenster
	def open_settings():
		settings_win = tb.Toplevel(root)
		settings_win.title("Einstellungen")
		settings_win.geometry("300x150")
		settings_win.grab_set()

		var_dark = tk.BooleanVar(value=dark_mode)

		def save_settings():
			with open(settings_path, 'w', encoding='utf-8') as f:
				json.dump({'dark_mode': var_dark.get()}, f)
			settings_win.destroy()
			root.destroy()
			# Starte das Hauptmenü als neuen Prozess, um Probleme mit Tkinter zu vermeiden
			import subprocess, sys
			subprocess.Popen([sys.executable, os.path.abspath(__file__)])

		cb_dark = tb.Checkbutton(settings_win, text="Dark Mode aktivieren", variable=var_dark, bootstyle="dark-round-toggle" if dark_mode else "round-toggle")
		cb_dark.pack(pady=20)
		btn_save = tb.Button(settings_win, text="Speichern", command=save_settings, style=btn_style)
		btn_save.pack(pady=10)

	btn_settings = tb.Button(root, text="Einstellungen", command=open_settings, style=btn_style)
	btn_settings.pack(pady=10, fill='x', padx=40)

	root.mainloop()

if __name__ == "__main__":
	main()