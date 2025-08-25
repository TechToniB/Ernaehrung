#Impoert Pandas sind Wundervoll
# Pandas Importieren =)
import pandas as pd
# Excel Datei Einlesen
df = pd.read_excel('/home/no/Dokumente/Ernaehrung/Gesunde Ernährung/Quellen/DGE Ist Wundervoll/GibMirAlles.xlsx')
# Daten Filtern
filtered_Y = df[
    (df['Bevölkerungsgruppe'] == '25 bis unter 51 Jahre') &
    (df['Geschlecht'] == 'Männlich')
]
filtered_A = df[
    (df['Bevölkerungsgruppe'] == '25 bis unter 51 Jahre') &
    (df['Geschlecht'] == 'Weiblich')
]
# Nur die Spalten Nährstoff, Referenzwert, Einheit und Kategorie ausgeben als Excel Datei
filtered_Y[['Nährstoff', 'Referenzwert', 'Einheit', 'Kategorie']].to_excel(
    '/home/no/Dokumente/Ernaehrung/Gesunde Ernährung/Filter/Yves_Filter.xlsx', index=False)
filtered_A[['Nährstoff', 'Referenzwert', 'Einheit', 'Kategorie']].to_excel(
    '/home/no/Dokumente/Ernaehrung/Gesunde Ernährung/Filter/Antonia_Filter.xlsx', index=False)
