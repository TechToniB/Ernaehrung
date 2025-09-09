import pandas as pd

# Pfad zur Excel-Datei
excel_path = "Gesunde Ernährung/Quellen/Nährstoffe in X/lebensmittel-naehrstoffe.de/Gesamttabelle.xlsx"

# Excel-Datei einlesen (nur die erste Zeile/Spaltennamen)
df = pd.read_excel(excel_path, engine="openpyxl")

# Neue Excel-Tabelle mit gefilterten Kategorien erstellen
ziel_kategorien = [
    "Algen",
    "Brot, Brötchen, Brotwaren",
    "Chips, gesalzene Snacks",
    "Exotische Früchte",
    "Fette, Butter, Margarine",
    "Früchstück, Cerealien, Flocken, Flakes",
    "Früchte",
    "Früchte getrocknet",
    "Geflügel",
    "Gekochte Früchte, Konserven",
    "Gemüse",
    "Getreide, Getreideprodukte",
    "Gewürze",
    "Hülsenfrüchte",
    "Joghurt, Sauermilchprodukte",
    "Kaffee",
    "Kakao, Schokolade",
    "Kartoffeln, Kartoffelprodukte",
    "Kräuter",
    "Kuchen, süsse Backwaren",
    "Mehle und Stärke",
    "Nüsse, Samen und Ölfrüchte",
    "Pilze",
    "Salate",
    "Soja und Tofu",
    "Süssspeisen, süsse Brotaufstriche, Pudding",
    "Öle"
]

if 'Kategorie_gesamt' in df.columns:
    filtered_df = df[df['Kategorie_gesamt'].isin(ziel_kategorien)]
    filtered_df.to_excel("Gesunde Ernährung/Quellen/Nährstoffe in X/lebensmittel-naehrstoffe.de/Vegan Gefilterte Kategorien.xlsx", index=False)
    print("Gefilterte Tabelle wurde als 'Gesunde Ernährung/Quellen/Nährstoffe in X/lebensmittel-naehrstoffe.de/Vegan Gefilterte Kategorien.xlsx' gespeichert.")
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