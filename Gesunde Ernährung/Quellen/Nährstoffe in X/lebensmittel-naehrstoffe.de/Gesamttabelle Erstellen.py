#kannst du alle Excel Tabellen in dem "lebensmittel-naehrstoffe.de" Ordner zu einer Gesamttabelle Zusamenfassen so das wenn in der Spalte "Lebensmittel" das selbe steht die werte aus den anderen Tabellen in der gleichen Zeile aufgelistet werden? 
import pandas as pd
import glob
import os
from openpyxl.utils import get_column_letter

# Ordnerpfad anpassen
folder = os.path.dirname(__file__)

# Nur Excel-Dateien (xlsx, xls, xlsm) einlesen
excel_files = glob.glob(os.path.join(folder, "*.xlsx"))

# Alle Tabellen einlesen
dfs = []
for file in excel_files:
    try:
        df = pd.read_excel(file)
    except Exception as e:
        print(f"Fehler beim Einlesen von {file}: {e}")
        continue
    # Spalten umbenennen, außer "Lebensmittel" und "Kategorie"
    for col in df.columns:
        if col not in ["Lebensmittel", "Kategorie"]:
            df = df.rename(columns={col: f"{col}_{os.path.splitext(os.path.basename(file))[0]}"})
        elif col == "Kategorie":
            # Kategorie-Spalte umbenennen, damit sie beim Merge nicht überschrieben wird
            df = df.rename(columns={col: f"{col}_{os.path.splitext(os.path.basename(file))[0]}"})
    dfs.append(df)

# Tabellen anhand der Spalte "Lebensmittel" zusammenführen
from functools import reduce
gesamt = reduce(lambda left, right: pd.merge(left, right, on="Lebensmittel", how="outer"), dfs)

# Alle Kategorie-Spalten zusammenführen
kategorie_cols = [col for col in gesamt.columns if col.startswith("Kategorie")]
gesamt["Kategorie_gesamt"] = gesamt[kategorie_cols].apply(
    lambda row: ", ".join(sorted(set(str(x) for x in row if pd.notna(x) and str(x).strip() != ""))), axis=1
)
gesamt = gesamt.drop(columns=kategorie_cols)

# Kategorie_gesamt als 2. Spalte einfügen
cols = list(gesamt.columns)
cols.insert(1, cols.pop(cols.index("Kategorie_gesamt")))
gesamt = gesamt[cols]

# Ergebnis speichern und Spaltenbreiten anpassen
output_path = os.path.join(folder, "Gesamttabelle.xlsx")
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    gesamt.to_excel(writer, index=False)
    worksheet = writer.sheets['Sheet1']
    for i, col in enumerate(gesamt.columns, 1):
        max_length = max(
            gesamt[col].astype(str).map(len).max(),
            len(col)
        )
        col_letter = get_column_letter(i)
        worksheet.column_dimensions[col_letter].width = max_length + 2

print("Gesamttabelle wurde erstellt.")