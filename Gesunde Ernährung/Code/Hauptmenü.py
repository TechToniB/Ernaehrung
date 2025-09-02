

import tkinter as tk
import subprocess
import os
import sys
import psutil
import json
import ttkbootstrap as tb
try:
	import win32gui
	import win32con
except ImportError:
	win32gui = None
	win32con = None



def bring_window_to_front(window_title):
	if win32gui is None:
		return False
	found = False
	def enumHandler(hwnd, lParam):
		nonlocal found
		if win32gui.IsWindowVisible(hwnd):
			if window_title in win32gui.GetWindowText(hwnd):
				win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
				win32gui.SetForegroundWindow(hwnd)
				found = True
	win32gui.EnumWindows(enumHandler, None)
	return found

def open_script(script_name, window_title=None):
	# Öffnet das gewünschte Python-Skript in einem neuen Prozess, aber nur wenn es noch nicht läuft
	script_path = os.path.join(os.path.dirname(__file__), script_name)
	# Prüfen, ob das Fenster schon existiert und ggf. wiederherstellen
	if window_title and bring_window_to_front(window_title):
		return
	# Prüfen, ob das Skript bereits läuft (Prozess)
	for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
		try:
			cmdline = proc.info['cmdline']
			if cmdline and any(os.path.basename(script_path) == os.path.basename(arg) for arg in cmdline):
				return  # Bereits laufend, nichts tun
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			continue
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
	dark_mode = False
	if os.path.exists(settings_path):
		try:
			with open(settings_path, 'r', encoding='utf-8') as f:
				settings = json.load(f)
				dark_mode = settings.get('dark_mode', False)
		except Exception as e:
			import logging
			logging.exception("Error reading settings.json")
	# Übergib dark_mode als Argument
	args = [sys.executable, script_path]
	if dark_mode:
		args.append('--dark')
	subprocess.Popen(args)

def main():
	# Lese Einstellungen
	settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
	dark_mode = False
	fullscreen = False
	if os.path.exists(settings_path):
		try:
			with open(settings_path, 'r', encoding='utf-8') as f:
				settings = json.load(f)
				dark_mode = settings.get('dark_mode', False)
				fullscreen = settings.get('fullscreen', False)
		except Exception:
			pass

	themename = "darkly" if dark_mode else "flatly"
	# Eindeutiger Fenstertitel für das Hauptmenü
	HAUPTMENUE_TITLE = 'MeinErnaehrungsHauptmenue2025'
	root = tb.Window(themename=themename)
	root.title(HAUPTMENUE_TITLE)
	root.geometry('400x300')
	if fullscreen:
		root.attributes('-fullscreen', True)

	# BooleanVars für Einstellungen
	var_dark = tk.BooleanVar(value=dark_mode)
	var_fullscreen = tk.BooleanVar(value=fullscreen)

	label = tb.Label(root, text="Bitte wählen Sie eine Funktion:", font=("Arial", 14))
	label.pack(pady=20)

	# Button Style für Dark Mode
	btn_style = "darkly.TButton" if dark_mode else "TButton"

	# Button für Rechner Import
	# Eindeutige Fenstertitel für die Rechner
	IMPORT_TITLE = 'RechnerImportFenster2025'
	NAEHRSTOFFE_TITLE = 'RechnerNaehrstoffeFenster2025'

	btn_import = tb.Button(root, text="Rechner Import",
		command=lambda: open_script('Rechner Import.py', window_title=IMPORT_TITLE), style=btn_style)
	btn_import.pack(pady=10, fill='x', padx=40)

	btn_naehrstoffe = tb.Button(root, text="Rechner Nahrungsmittel in Nährstoffe",
		command=lambda: open_script('Rechner Nahrungsmittel in Nährstoffe.py', window_title=NAEHRSTOFFE_TITLE), style=btn_style)
	btn_naehrstoffe.pack(pady=10, fill='x', padx=40)

	# Einstellungs-Menü als eigenes Fenster
	def open_settings():
		settings_win = tb.Toplevel(root)
		settings_win.title("Einstellungen")
		settings_win.geometry("300x180")
		settings_win.grab_set()


		# Dark Mode Checkbutton: bei Aktivierung blau hinterlegt (primary-round-toggle)
		cb_dark = tb.Checkbutton(
			settings_win,
			text="Dark Mode aktivieren",
			variable=var_dark,
			bootstyle="primary-round-toggle" if var_dark.get() else "round-toggle"
		)
		cb_dark.pack(pady=10)

		# Callback, um Stil dynamisch zu ändern
		def update_dark_style(*args):
			cb_dark.configure(bootstyle="primary-round-toggle" if var_dark.get() else "round-toggle")
		var_dark.trace_add('write', update_dark_style)

		cb_full = tb.Checkbutton(settings_win, text="Vollbildmodus aktivieren", variable=var_fullscreen, bootstyle="round-toggle")
		cb_full.pack(pady=10)


		def save_settings():
			with open(settings_path, 'w', encoding='utf-8') as f:
				json.dump({'dark_mode': var_dark.get(), 'fullscreen': var_fullscreen.get()}, f)
			settings_win.destroy()
			root.destroy()
			subprocess.Popen([sys.executable, os.path.abspath(__file__)])

		btn_save = tb.Button(settings_win, text="Speichern", command=save_settings, style=btn_style)
		btn_save.pack(pady=10)

	btn_settings = tb.Button(root, text="Einstellungen", command=open_settings, style=btn_style)
	btn_settings.pack(pady=10, fill='x', padx=40)


	# Beenden-Button
	btn_exit = tb.Button(root, text="Beenden", command=root.destroy, style=btn_style)
	btn_exit.pack(pady=10, fill='x', padx=40)

	root.mainloop()

if __name__ == "__main__":
	main()