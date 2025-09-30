import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet(sheet_id: str, worksheet_name: str = "Sheet1"):

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    
    return worksheet



if __name__ == "__main__":
    SHEET_ID = "1HJ0Caotw7JKrtmR0f-ReRFWgtJu6fmvSGJIV901XTUw"   # ⚠️ remplace par le tien
    WORKSHEET_NAME = "code communes"        # ou "Feuille1" si en français
    
    sheet = connect_to_sheet(SHEET_ID, WORKSHEET_NAME)
 
    # data = sheet.get_all_records()
    # communes = [row for row in data if row["Code de la wilaya"] == 43]
    # print(communes)

    # Ajouter une ligne
    # sheet.append_row(["Ali", "Produit X", 3])
