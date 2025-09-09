import tkinter as tk
import subprocess
import os
import sys
import psutil
import json
import ttkbootstrap as tb
import platform

# Cross-platform window focus/restore (Tkinter only)
def bring_window_to_front(window_title=None, root=None):
    if root is not None:
        try:
            root.deiconify()
            root.lift()
            root.focus_force()
            return True
        except Exception:
            return False
    return False

def open_script(script_name, window_title=None, dark_mode=False):
    # Öffnet das gewünschte Python-Skript in einem neuen Prozess, aber nur wenn es noch nicht läuft
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), script_name))
    # Prüfen, ob das Skript bereits läuft (Prozess)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if isinstance(cmdline, list):
                for arg in cmdline:
                    if os.path.abspath(arg) == script_path:
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
        # Cross-platform fullscreen
        root.attributes('-fullscreen', True)
        # Remove window border only on Windows
        if platform.system() == "Windows":
            root.overrideredirect(True)

    var_dark = tk.BooleanVar(value=dark_mode)
    var_fullscreen = tk.BooleanVar(value=fullscreen)
    var_theme = tk.StringVar(value=themename)
    dark_themes = {"darkly", "cyborg", "superhero", "solar", "vapor"}
    btn_style = "darkly.TButton" if themename in dark_themes else "TButton"

    label = tb.Label(root, text="Bitte wählen Sie eine Funktion:", font=("Arial", 14))
    if fullscreen:
        label.pack(side='top', pady=40)
    else:
        label.pack(pady=20)

    IMPORT_TITLE = 'RechnerImportFenster2025'
    NAEHRSTOFFE_TITLE = 'RechnerNaehrstoffeFenster2025'

    def open_settings():
        settings_win = tk.Toplevel(root)
        # Remove window border only on Windows
        if platform.system() == "Windows":
            settings_win.overrideredirect(True)
        win_w, win_h = 400, 250
        settings_win.update_idletasks()
        screen_w = settings_win.winfo_screenwidth()
        screen_h = settings_win.winfo_screenheight()
        x = (screen_w // 2) - (win_w // 2)
        y = (screen_h // 2) - (win_h // 2)
        settings_win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        settings_win.resizable(False, False)
        settings_win.grab_set()

        # Rahmen-Frame für die Einstellungen
        frame_border = tb.Frame(settings_win, borderwidth=3, relief="groove", padding=10)
        frame_border.pack(expand=True, fill="both", padx=18, pady=18)

        cb_full = tb.Checkbutton(frame_border, text="Vollbildmodus aktivieren", variable=var_fullscreen)
        cb_full.pack(pady=6)

        # Theme-Name zu Modus (Dark/Light) zuordnen
        theme_modes = {
            "darkly": " (Dark)",
            "superhero": " (Dark)",
            "cyborg": " (Dark)",
            "solar": " (Dark)",
            "vapor": " (Dark)",
            "flatly": " (Light)",
            "journal": " (Light)",
            "litera": " (Light)",
            "lumen": " (Light)",
            "minty": " (Light)",
            "morph": " (Light)",
            "pulse": " (Light)",
            "sandstone": " (Light)",
            "united": " (Light)",
            "yeti": " (Light)"
        }

        # Theme-Auswahl
        label_theme = tb.Label(frame_border, text="Theme auswählen:")
        label_theme.pack(pady=(10, 0))
        theme_names = [name + theme_modes.get(name, "") for name in available_themes]
        theme_combo = tb.Combobox(frame_border, values=theme_names, textvariable=var_theme, state="readonly")
        theme_combo.pack(pady=4)

        def save_settings():
            selected_theme = theme_combo.get().split(" (")[0]
            selected_theme = theme_combo.get().split()[0]
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'dark_mode': 'dark' in selected_theme,
                    'fullscreen': var_fullscreen.get(),
                    'themename': selected_theme
                }, f)
            settings_win.destroy()
            def restart_app():
                subprocess.Popen([sys.executable, os.path.abspath(__file__)])
                root.destroy()
            root.after(100, restart_app)

        # Button-Frame für Speichern und Zurück (im Rahmen)
        btn_frame = tb.Frame(frame_border)
        btn_frame.pack(pady=10)
        btn_save = tb.Button(btn_frame, text="Speichern", command=save_settings, style=btn_style)
        btn_save.pack(side="left", padx=(0, 10))
        btn_back = tb.Button(btn_frame, text="Zurück", command=settings_win.destroy, style=btn_style)
        btn_back.pack(side="left")

    # Füge diese Zeile zu deiner Button-Liste hinzu (vor "Einstellungen"):
    button_list = [
        ("Rechner Import", lambda: open_script('Rechner Import.py', window_title=IMPORT_TITLE, dark_mode=dark_mode)),
        ("Rechner Nahrungsmittel in Nährstoffe", lambda: open_script('Rechner Nahrungsmittel in Nährstoffe.py', window_title=NAEHRSTOFFE_TITLE, dark_mode=dark_mode)),
        ("Gerichte", lambda: open_script('Rechner Rezepte.py', window_title="RechnerRezepteFenster2025", dark_mode=dark_mode)),
        ("Saisonkalender", lambda: open_script('Zusammenführung der Saisonkalender.py', window_title="Saisonkalender Tabelle", dark_mode=dark_mode)),  # <-- NEU
        ("Saisonkalender Monatsauswahl", lambda: open_script('Saisonkalender_Monatsauswahl.py', window_title="Saisonkalender Monatsauswahl", dark_mode=dark_mode)),
        ("Einstellungen", open_settings),
        ("Beenden", root.destroy)
    ]
    if fullscreen:
        btn_frame = tk.Frame(root)
        btn_frame.pack(side='top', expand=True, fill='both')
        for text, cmd in button_list:
            try:
                btn = tb.Button(btn_frame, text=text, command=cmd, style=btn_style)
                btn.pack(fill='x', pady=10)
                print(f"[DEBUG] Button erzeugt: {text}")
            except Exception as e:
                print(f"[ERROR] Button '{text}' konnte nicht erzeugt werden: {e}")
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