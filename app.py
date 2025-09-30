from flask import Flask, render_template, request, redirect, url_for, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheets_outils import connect_to_sheet
from parese_commande import InsererCommande

app = Flask(__name__)

# --- Connexion Google Sheets ---
SHEET_ID = "1HJ0Caotw7JKrtmR0f-ReRFWgtJu6fmvSGJIV901XTUw"  
WORKSHEET_NAME = "commandes"         

sheet = connect_to_sheet(SHEET_ID, WORKSHEET_NAME)

def GetWilayaFromSheet() :
    sheet = connect_to_sheet(SHEET_ID, "code wilayas")  
    data = sheet.get_all_records()
    return data

def GetStationsFromSheet():
    sheet = connect_to_sheet(SHEET_ID, "code stations")
    values = sheet.get("A:B")  # récupère uniquement colonnes A et B
    headers, rows = values[0], values[1:]
    data = [dict(zip(headers, row)) for row in rows]
    return data


# Recuperer les wilayas et les stations from google sheet
wilayas = GetWilayaFromSheet()
stations = GetStationsFromSheet()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/manuel", methods=["GET", "POST"])
def manuel():
    if request.method == "POST":
        client_name = request.form.get("client")
        produit = request.form.get("produit")
        quantite = request.form.get("quantite")
        sheet.append_row([client_name, produit, quantite])
        return redirect(url_for("afficher"))
    return render_template("manuel.html")


@app.route("/auto", methods=["GET", "POST"])
def auto():
    message = None
    status = None  # "success" ou "error"

    if request.method == "POST":
        raw_data = request.form.get("data")

        try:
            
            if not wilayas:
                raise ValueError("Wilaya introuvable depuis google sheet.")
            
            if not stations:
                raise ValueError("Station introuvable depuis google sheet.")
            
            InsererCommande(raw_data , wilayas ,stations)
            message = "✅ La commande a été insérée avec succès."
            status = "success"
        except Exception as e:
            message = f"❌ Erreur lors de l'insertion : {str(e)}"
            status = "error"

    return render_template("auto.html", message=message, status=status)



@app.route("/afficher")
def afficher():
    page = int(request.args.get("page", 1))  # num de page dans l'URL ?page=2
    per_page = 7

    commandes = sheet.get_all_records()
    total = len(commandes)

    # Découper la liste
    start = (page - 1) * per_page
    end = start + per_page
    commandes_page = commandes[start:end]

    return render_template(
        "afficher.html",
        commandes=commandes_page,
        page=page,
        total=total,
        per_page=per_page
    )



if __name__ == "__main__":
    app.run(debug=True)
