import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Charger les variables d'environnement depuis .env (en local)
load_dotenv()

def connect_to_sheet(sheet_id: str, worksheet_name: str = "Sheet1"):
    # Scopes requis pour Google Sheets + Drive
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Construire le dictionnaire de credentials à partir des variables d'environnement
    google_creds = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        # ⚠️ très important : remettre les sauts de ligne dans la clé privée
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
    }

    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    
    return worksheet


if __name__ == "__main__":
    # ⚠️ à remplacer par ton ID de Google Sheet
    SHEET_ID = "1HJ0Caotw7JKrtmR0f-ReRFWgtJu6fmvSGJIV901XTUw"
    WORKSHEET_NAME = "code wilayas"

    sheet = connect_to_sheet(SHEET_ID, WORKSHEET_NAME)

    # Exemple : lecture des données
    data = sheet.get_all_records()
    print("Extrait de données :", data[:5])

    # Exemple : ajout d'une ligne
    # sheet.append_row(["Ali", "Produit X", 3])
    print("Connexion réussie ")
    # import requests

    # url = "https://app.noest-dz.com/api/public/get/trackings/info"

    # payload = {
    #     "api_token": "TWJhktoMHmCgprsgKejtDEiH4u9j2ehryTZ",
    #     "user_guid": "N5JXNIKQ",
    #     "trackings": ["N5J-35C-11446627"]
    # }

    # response = requests.post(url, json=payload)

    # if response.status_code == 200:
    #     data = response.json()
    #     print(data)
    # else:
    #     print("Erreur:", response.status_code, response.text)

