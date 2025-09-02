import tkinter as tk
import ttkbootstrap as tb
import subprocess
import os

def open_script(script_name):
	# Öffnet das gewünschte Python-Skript in einem neuen Prozess
	script_path = os.path.join(os.path.dirname(__file__), script_name)
	subprocess.Popen(['C:/Users/hoetting.y/Dokumente/Ernaehrung-1/.venv/Scripts/python.exe', script_path])

def main():
	root = tb.Window(themename="flatly")
	root.title('Hauptmenü')
	root.geometry('400x250')

	label = tb.Label(root, text="Bitte wählen Sie eine Funktion:", font=("Arial", 14))
	label.pack(pady=20)

	# Button für Rechner Import

	btn_import = tb.Button(root, text="Rechner Import",
		command=lambda: open_script('Rechner Import.py'))
	btn_import.pack(pady=10, fill='x', padx=40)

	# Button für Rechner Nahrungsmittel in Nährstoffe
	btn_naehrstoffe = tb.Button(root, text="Rechner Nahrungsmittel in Nährstoffe",
		command=lambda: open_script('Rechner Nahrungsmittel in Nährstoffe.py'))
	btn_naehrstoffe.pack(pady=10, fill='x', padx=40)

	# Hier können weitere Buttons/Funktionen einfach ergänzt werden

	root.mainloop()

if __name__ == "__main__":
	main()