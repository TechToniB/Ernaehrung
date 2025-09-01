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
    output_path = "Gesunde Ernährung/Quellen/Nährstoffe in X/lebensmittel-naehrstoffe.de/Gefilterte_Kategorien.xlsx"
    filtered_df.to_excel(output_path, index=False)

    # Spaltenbreiten anpassen
    from openpyxl import load_workbook
    wb = load_workbook(output_path)
    ws = wb.active
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column].width = adjusted_width
    wb.save(output_path)

    # Kategorien, die nicht aufgenommen wurden, ausgeben
    alle_kategorien = set(df['Kategorie_gesamt'].dropna())
    nicht_aufgenommen = alle_kategorien - set(ziel_kategorien)
    print(f"Gefilterte Tabelle wurde als '{output_path}' gespeichert und die Spaltenbreiten angepasst.")
    print("\nKategorien, die NICHT aufgenommen wurden:")
    for k in sorted(nicht_aufgenommen):
        print(k)
else:
    print("Die Spalte 'Kategorie_gesamt' wurde nicht gefunden.")

# Alle Kategorien
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

# Nicht aufgenommene Kategorien
# Eier
# Fisch, Meeresfische
# Fleisch und Innereien
# Fleischwaren, Wurstwaren
# Frischkäse und Quark
# Kalb
# Käse
# Milch, Milchprodukte
# Muscheln, Garnelen, Weichtiere und Meeresfrüchte
# Rind
# Saucen, Würzmittel
# Schaf, Lamm
# Schwein
# Säfte, Obstsäfte, Gemüsesäfte, Nektar
# Wild, weitere Tierarten