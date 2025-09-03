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

def open_script(script_name, window_title=None, dark_mode=False):
	# Öffnet das gewünschte Python-Skript in einem neuen Prozess, aber nur wenn es noch nicht läuft
	script_path = os.path.join(os.path.dirname(__file__), script_name)
	# Prüfen, ob das Fenster schon existiert und ggf. wiederherstellen
	if window_title and bring_window_to_front(window_title):
		return
	# Prüfen, ob das Skript bereits läuft (Prozess)
	for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
		try:
			if script_path in proc.info['cmdline']:
				return
		except Exception:
			continue
	# Wenn nicht gefunden, dann starten
	cmd = [sys.executable, script_path]
	if dark_mode:
		cmd.append('--dark')
	subprocess.Popen(cmd)

# --- Hauptmenü-Logik ---
def main():
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

    print(f"[DEBUG] Lade Theme: {themename}")
    try:
        root = tb.Window(themename=themename)
    except Exception as e:
        print(f"[ERROR] Theme konnte nicht geladen werden: {e}")
        root = tk.Tk()
    root.title('MeinErnaehrungsHauptmenue2025')
    root.geometry('400x300')
    if fullscreen:
        root.attributes('-fullscreen', True)

    var_dark = tk.BooleanVar(value=dark_mode)
    var_fullscreen = tk.BooleanVar(value=fullscreen)
    var_theme = tk.StringVar(value=themename)
    btn_style = "darkly.TButton" if "dark" in themename else "TButton"

    label = tb.Label(root, text="Bitte wählen Sie eine Funktion:", font=("Arial", 14))
    if fullscreen:
        label.pack(side='top', pady=40)
    else:
        label.pack(pady=20)

    IMPORT_TITLE = 'RechnerImportFenster2025'
    NAEHRSTOFFE_TITLE = 'RechnerNaehrstoffeFenster2025'

    def open_settings():
        settings_win = tb.Toplevel(root)
        settings_win.overrideredirect(True)
        win_w, win_h = 300, 240
        settings_win.update_idletasks()
        screen_w = settings_win.winfo_screenwidth()
        screen_h = settings_win.winfo_screenheight()
        x = (screen_w // 2) - (win_w // 2)
        y = (screen_h // 2) - (win_h // 2)
        settings_win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        settings_win.grab_set()

        frame_top = tk.Frame(settings_win, bg="#111", height=32)
        frame_top.pack(fill="x", side="top")
        label_title = tk.Label(frame_top, text="Einstellungen", bg="#111", fg="white", font=("Arial", 12, "bold"))
        label_title.pack(side="top", pady=4)

        cb_dark = tb.Checkbutton(
            settings_win,
            text="Dark Mode aktivieren",
            variable=var_dark,
            bootstyle="primary-round-toggle" if var_dark.get() else "round-toggle"
        )
        cb_dark.pack(pady=6)

        def update_dark_style(*args):
            cb_dark.configure(bootstyle="primary-round-toggle" if var_dark.get() else "round-toggle")
        var_dark.trace_add('write', update_dark_style)

        cb_full = tb.Checkbutton(settings_win, text="Vollbildmodus aktivieren", variable=var_fullscreen, bootstyle="round-toggle")
        cb_full.pack(pady=6)

        # Theme-Auswahl
        label_theme = tb.Label(settings_win, text="Theme auswählen:")
        label_theme.pack(pady=(10, 0))
        theme_combo = tb.Combobox(settings_win, values=available_themes, textvariable=var_theme, state="readonly")
        theme_combo.pack(pady=4)

        def save_settings():
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'dark_mode': var_dark.get(),
                    'fullscreen': var_fullscreen.get(),
                    'themename': var_theme.get()
                }, f)
            settings_win.destroy()
            root.destroy()
            subprocess.Popen([sys.executable, os.path.abspath(__file__)])

        btn_save = tb.Button(settings_win, text="Speichern", command=save_settings, style=btn_style)
        btn_save.pack(pady=10)

    # Füge diese Zeile zu deiner Button-Liste hinzu (vor "Einstellungen"):
    button_list = [
        ("Rechner Import", lambda: open_script('Rechner Import.py', window_title=IMPORT_TITLE, dark_mode=dark_mode)),
        ("Rechner Nahrungsmittel in Nährstoffe", lambda: open_script('Rechner Nahrungsmittel in Nährstoffe.py', window_title=NAEHRSTOFFE_TITLE, dark_mode=dark_mode)),
        ("Gerichte", lambda: open_script('Rechner Rezepte.py', window_title="RechnerRezepteFenster2025", dark_mode=dark_mode)),
        ("Saisonkalender", lambda: open_script('Zusammenführung der Saisonkalender.py', window_title="Saisonkalender Tabelle", dark_mode=dark_mode)),  # <-- NEU
        ("Einstellungen", open_settings),
        ("Beenden", root.destroy)
    ]

    if fullscreen:
        btn_frame = tk.Frame(root, bg='red')
        btn_frame.pack(side='top', expand=True, fill='both')
        for text, cmd in button_list:
            try:
                btn = tb.Button(btn_frame, text=text, command=cmd, style=btn_style)
                btn.pack(fill='x', pady=10)
                print(f"[DEBUG] Button erzeugt: {text}")
            except Exception as e:
                print(f"[ERROR] Button '{text}' konnte nicht erzeugt werden: {e}")
    else:
        for text, cmd in button_list:
            try:
                btn = tb.Button(root, text=text, command=cmd, style=btn_style)
                btn.pack(pady=10, fill='x', padx=40)
                print(f"[DEBUG] Button erzeugt: {text}")
            except Exception as e:
                print(f"[ERROR] Button '{text}' konnte nicht erzeugt werden: {e}")

    root.mainloop()

# Nur main() und Aufruf am Ende sollen übrig bleiben

if __name__ == "__main__":
	main()