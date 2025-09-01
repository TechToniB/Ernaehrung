import pandas as pd

# Pfad zur Excel-Datei
excel_path = "Gesunde Ernährung/Quellen/Nährstoffe in X/lebensmittel-naehrstoffe.de/Gesamttabelle.xlsx"

# Excel-Datei einlesen (nur die erste Zeile/Spaltennamen)
df = pd.read_excel(excel_path, engine="openpyxl")

# Nur die Werte der Spalte 'Kategorie_gesamt' ausgeben
if 'Kategorie_gesamt' in df.columns:
    # Eindeutige Werte (ohne nan) sammeln und sortieren
    unique_vals = set(df['Kategorie_gesamt'].dropna())
    print("Eindeutige Werte der Spalte 'Kategorie_gesamt':")
    for val in sorted(unique_vals):
        print(val)
else:
    print("Die Spalte 'Kategorie_gesamt' wurde nicht gefunden.")
# Algen
# Brot, Brötchen, Brotwaren
# Chips, gesalzene Snacks
# Eier
# Exotische Früchte
# Fette, Butter, Margarine
# Fisch, Meeresfische
# Fleisch und Innereien
# Fleischwaren, Wurstwaren
# Frischkäse und Quark
# Früchstück, Cerealien, Flocken, Flakes
# Früchte
# Früchte getrocknet
# Geflügel
# Gekochte Früchte, Konserven
# Gemüse
# Getreide, Getreideprodukte
# Gewürze
# Hülsenfrüchte
# Joghurt, Sauermilchprodukte
# Kaffee
# Kakao, Schokolade
# Kalb
# Kartoffeln, Kartoffelprodukte
# Kräuter
# Kuchen, süsse Backwaren
# Käse
# Mehle und Stärke
# Milch, Milchprodukte
# Muscheln, Garnelen, Weichtiere und Meeresfrüchte
# Nüsse, Samen und Ölfrüchte
# Pilze
# Rind
# Salate
# Saucen, Würzmittel
# Schaf, Lamm
# Schwein
# Soja und Tofu
# Säfte, Obstsäfte, Gemüsesäfte, Nektar
# Süssspeisen, süsse Brotaufstriche, Pudding
# Wild, weitere Tierarten
# Öle