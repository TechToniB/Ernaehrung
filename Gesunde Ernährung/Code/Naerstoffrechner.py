#Liste der Nährstoffe und Tages Nährstoffe
Eiweiß_Protein=0
Tages_Eiweiß_Protein=0
Fett=0
Tages_Fett=0
Kohlenhydrate=0
Tages_Kohlenhydrate=0
Omega_3_Fettsäuren=0
Tages_Omega_3_Fettsäuren=0
Natrium_Chorid=0
Tages_Natrium_Chorid=0
Kalium=0
Tages_Kalium=0
Kalzium=0
Tages_Kalzium=0
Phosphor=0
Tages_Phosphor=0
Magnesium=0
Tages_Magnesium=0
Eisen=0
Tages_Eisen=0
Jod=0
Tages_Jod=0
Selen=0
Tages_Selen=0
Zink=0
Tages_Zink=0
Viatmin_A=0
Tages_Viatmin_A=0
Vitamin_B1=0
Tages_Vitamin_B1=0
Vitamin_B2=0
Tages_Vitamin_B2=0
Niacin=0
Tages_Niacin=0
Pathotensäure=0
Tages_Pathotensäure=0
Vitamin_B6=0
Tages_Vitamin_B6=0
Biotin=0
Tages_Biotin=0
Folsäure=0
Tages_Folsäure=0
Vitamin_B12=0
Tages_Vitamin_B12=0
Vitamin_C=0
Tages_Vitamin_C=0
Vitamin_D=0
Tages_Vitamin_D=0
Vitamin_E=0
Tages_Vitamin_E=0
Vitamin_K=0
Tages_Vitamin_K=0

#Andere Variabeln (müssen eigentlich 0 aber Test)
#Verwendete Menge in gramm
Verwendete_Menge=200

#Zutaten/Produkte Brauchen werte für nährstoffe
zutaten_produkte = ['Kartoffeln']

#Zu Machen!
#Verwendete Zutaten aus Gerichte
#Ist zutat verfügbar aus Kalender
#Verwendete Menge aus Gerichte
#Gerichte in zutaten unterteilen
#Loop für alle Zutaten

#[0]ist der 1. Eintrag der liste hier Kartoffeln
#Eiweiß_Protein ist 2 (Gramm)
(zutaten_produkte[0]) = Eiweiß_Protein=2; Kohlenhydrate=390
#Wert durch 100*Verwendete_Menge
Eiweiß_Protein=Eiweiß_Protein/100*Verwendete_Menge
Kohlenhydrate=Kohlenhydrate/100*Verwendete_Menge
#Tages Wert ist der vorherige Tages Wert + Produkt Wert (Eiweiß_Protein)
Tages_Eiweiß_Protein=Tages_Eiweiß_Protein+Eiweiß_Protein
Tages_Kohlenhydrate=Tages_Kohlenhydrate+Kohlenhydrate
#Produkt wert wieder auf 0 setzen für den nächsten loop 
Eiweiß_Protein=0
Kohlenhydrate=0
#Ausgabe der werte als Test
print(Tages_Eiweiß_Protein,Eiweiß_Protein,Verwendete_Menge,Tages_Kohlenhydrate)