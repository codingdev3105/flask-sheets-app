import re
from datetime import datetime
from sheets_outils import connect_to_sheet
from rapidfuzz import process




SHEET_ID = "1HJ0Caotw7JKrtmR0f-ReRFWgtJu6fmvSGJIV901XTUw"
# --- Fonction pour découper le message ---
def split_message(message: str):
    return [line.strip() for line in message.strip().split("\n") if line.strip()]

# --- Recherche intelligente (équivalent de Fuse.js) ---
def find_best_match(input_text, list_items, key=None):
    """
    input_text : texte à comparer
    list_items : liste d'objets ou de strings
    key        : si list_items est une liste de dicts, préciser la clé
    """
    if not input_text or not list_items:
        return None

    # Normaliser le texte
    def normalize(text):
        return (
            text.lower()
            .replace(" ", "")
            .replace("-", "")
            .replace("_", "")
        )

    input_norm = normalize(input_text)

    if not list_items:
        return None
    if isinstance(list_items[0], dict) and key:
        choices = [normalize(str(item[key])) for item in list_items]
        match, score = process.extractOne(input_norm, choices)
        if score >= 70:  # seuil ajustable
            return next(item for item in list_items if normalize(str(item[key])) == match)
    else:
        choices = [normalize(str(item)) for item in list_items]
        match, score = process.extractOne(input_norm, choices)
        if score >= 70:
            return list_items[choices.index(match)]

    return None

# --- Fonction pour parser le message ---
def parse_commande(message, wilayas):
    lignes = split_message(message)

    # Initialisation
    name = ""
    tels = []
    wilaya = ""
    commune = ""
    typedenvoi = ""
    adresse = ""
    station = ""
    produit_lines = []
    prix = 0
    livraison = 0
    total = 0
    reference = ""

    for idx, line in enumerate(lignes):
        line = line.strip()

        # Nom
        if idx == 0 and line:
            name = line

        # Téléphones
        elif idx == 1 and re.search(r"\d", line):
            phones = re.findall(r"(?:\+213|0)(\d{9})", line)
            if phones:
                tels.extend([int(p) for p in phones])

        # Wilaya
        elif idx == 2 and line:
            match = find_best_match(line, wilayas, key="nom wilaya")
            if match:
                wilaya = match["nom wilaya"]

        # Commune
        elif idx == 3 and line:
            commune = line
            adresse = commune

        # Type d’envoi
        elif idx == 4 and line:
            if "domicile" in line.lower():
                typedenvoi = "domicile"
            elif "bureau" in line.lower():
                typedenvoi = "bureau"

        # Produit (peut être sur plusieurs lignes)
        elif not re.search(r"(prix|livr|total|^r\d+)", line, re.I) and line and idx >= 5:
            produit_lines.append(line)

        # Prix
        elif "prix" in line.lower():
            match = re.search(r"\d+", line)
            if match:
                prix = int(match.group())

        # Livraison
        elif "livr" in line.lower():
            match = re.search(r"\d+", line)
            if match:
                livraison = int(match.group())

        # Total
        elif "total" in line.lower():
            match = re.search(r"\d+", line)
            if match:
                total = int(match.group())

        # Référence
        elif re.match(r"^r\d+", line, re.I):
            match = re.search(r"\d+", line)
            if match:
                reference = int(match.group())

    # Fusion des lignes produit
    produit = " ".join(produit_lines).strip()

    # Vérification stricte
    if (
        not name
        or not tels
        or not wilaya
        or not commune
        or not typedenvoi
        or not produit
        or prix == 0
        or livraison == 0
        or total == 0
    ):
        return None

    return {
        "name": name,
        "tel1": tels[0] if len(tels) > 0 else None,
        "tel2": tels[1] if len(tels) > 1 else None,
        "wilaya": wilaya,
        "commune": commune,
        "typedenvoi": typedenvoi,
        "adresse": adresse,
        "produit": produit,
        "prix": prix,
        "livraison": livraison,
        "total": total,
        "reference": reference,
        "station": station,
    }







def GetCommunesFromSheet(code_wilaya):
    SHEET_ID = "1HJ0Caotw7JKrtmR0f-ReRFWgtJu6fmvSGJIV901XTUw"    
    WORKSHEET_NAME = "code communes"        
    sheet = connect_to_sheet(SHEET_ID, WORKSHEET_NAME)
 
    data = sheet.get_all_records()
    communes = [row for row in data if row["Code de la wilaya"] == code_wilaya]
    return communes


def chercher_wilaya_par_nom(nom, wilayas):
    for w in wilayas:
        if w["nom wilaya"].lower() == nom.lower():
            return w
    return None



def InsererCommande(message,wilayas,stations):

    if not message:
        raise ValueError("Message vide fourni.")
    

    try :

        # Parser le message
        commande = parse_commande(message, wilayas)
        if not commande:
            raise ValueError("Commande non valide.")

        # Modification sur la commande
        selected_wilaya = chercher_wilaya_par_nom(commande['wilaya'], wilayas) 
        if selected_wilaya :
            commande['wilaya'] = selected_wilaya['code wilaya']
            if commande['typedenvoi'] == 'domicile' : 
                communes = GetCommunesFromSheet(selected_wilaya['code wilaya'])
                selected_commune = find_best_match(commande['commune'], communes, key='Nom de la commune')
                if selected_commune : 
                    commande['commune'] = selected_commune['Nom de la commune']
                    commande['adresse'] = selected_commune['Nom de la commune']
                    commande['typedenvoi'] = None
                else:
                    raise ValueError("Commune introuvable parmis les communes trouvées.")
                    
            elif commande['typedenvoi'] == 'bureau' : 
                selected_station = find_best_match(commande['commune'], stations, key='Nom de la station') 
                if selected_station :
                    commande['station'] = selected_station['Code de la station']
                    commande['commune'] = selected_station['Nom de la station']
                    commande['adresse'] = selected_station['Nom de la station']
                commande['typedenvoi'] = 'OUI'
        else :
            raise ValueError("Wilaya introuvable parmis les wilayas trouvées.")

        # Inserer la commande dans google sheet 'commandes'       
        TOTAL_COLS = 17  

        # Préparer la ligne
        row = [
            datetime.now().strftime("%d-%m-%Y %H:%M"),
            commande.get('reference', ""),
            commande.get('name', ""),
            commande.get('tel1', ""),
            commande.get('tel2', ""),
            commande.get('adresse', ""),
            commande.get('commune', ""),
            commande.get('total', ""),
            commande.get('wilaya', ""),
            commande.get('produit', ""),
            "",  # remarque
            "",  # poids
            "",  # pick up
            "",  # Echange
            commande.get('typedenvoi', ""),
            "",  # colonne vide
            commande.get('station', "")
        ]

        # Compléter si jamais il manque des colonnes
        while len(row) < TOTAL_COLS:
            row.append("")

        # Connexion
        sheet_commandes = connect_to_sheet(SHEET_ID, "commandes")

        # Trouver la dernière ligne
        last_row = len(sheet_commandes.get_all_values()) + 1  

        # Insérer à la fin
        sheet_commandes.insert_row(row, last_row, value_input_option="USER_ENTERED")



    except Exception as e:
        print("❌ Erreur :", str(e))
        raise


# if __name__ == "__main__":
#     message = """yahia hanani 
#                 0665622919 
#                 alger
#                 alger centre
#                 bureau
#                 maya grenat 36
#                 prix 2900 da
#                 livr 600 da
#                 total 3500 da
#                 r125
#     """
#     InsererCommande(message)

