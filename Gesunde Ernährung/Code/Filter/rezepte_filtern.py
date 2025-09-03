import re
import pandas as pd

# Einlesen der Excel-Datei
input_path = r'c:/Users/hoetting.y/Dokumente/Ernaehrung-1/Gesunde Ernährung/Quellen/Scraper/rezepte.xlsx'
try:
    df = pd.read_excel(input_path)
    # Filtere Zeilen, bei denen in Spalte C (Index 2) NICHT "Fehler" steht
    filtered_df = df[df.iloc[:, 2] != 'Fehler'].copy()  # .copy() hinzufügen

    # Spalte "Menge" in zwei neue Spalten aufteilen
    def split_menge_einheit(menge_str):
        match = re.match(r"^\s*([\d.,/]+)\s*([a-zA-ZäöüÄÖÜµ]*)", str(menge_str))
        if match:
            return pd.Series([match.group(1), match.group(2)])
        else:
            return pd.Series([menge_str, None])

    # Prüfen, ob Spalte "Menge" existiert
    if 'Menge' in filtered_df.columns:
        filtered_df[['Menge_Zahl', 'Menge_Einheit']] = filtered_df['Menge'].apply(split_menge_einheit)
        filtered_df = filtered_df.drop(columns=['Menge'])

    output_path = r'c:/Users/hoetting.y/Dokumente/Ernaehrung-1/Gesunde Ernährung/Quellen/Scraper/rezepte_gefiltert.xlsx'
    filtered_df.to_excel(output_path, index=False)
    print(f'Gefilterte Datei gespeichert als: {output_path}')
except Exception as e:
    print(f'Fehler beim Verarbeiten der Datei: {e}')
