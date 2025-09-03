import pandas as pd

# Einlesen der Excel-Datei
input_path = '../../Filter/rezepte.xlsx'
try:
	df = pd.read_excel(r'c:/Users/hoetting.y/Dokumente/Ernaehrung-1/Gesunde Ernährung/Quellen/Scraper/rezepte.xlsx')
	filtered_df = df[df.iloc[:, 2] != 'Keine Zutaten gefunden']
	output_path = r'c:/Users/hoetting.y/Dokumente/Ernaehrung-1/Gesunde Ernährung/Quellen/Scraper/rezepte_gefiltert.xlsx'
	filtered_df.to_excel(output_path, index=False)
	print(f'Gefilterte Datei gespeichert als: {output_path}')
except Exception as e:
	print(f'Fehler beim Verarbeiten der Datei: {e}')
