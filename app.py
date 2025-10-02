from flask import Flask, render_template, request, redirect, url_for, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheets_outils import connect_to_sheet  # Gardez-le si vous l'utilisez ailleurs, mais on passe à une connexion unique
from parese_commande import InsererCommande
import os

app = Flask(__name__)

# --- Connexion Google Sheets (optimisée : une seule authentification) ---
SHEET_ID = "1HJ0Caotw7JKrtmR0f-ReRFWgtJu6fmvSGJIV901XTUw"

spreadsheet = connect_to_sheet(SHEET_ID)


# Référencez les worksheets une fois (plus besoin de connect_to_sheet multiple)
sheet_commandes = spreadsheet.worksheet("commandes")
sheet_wilayas = spreadsheet.worksheet("code wilayas")
sheet_stations = spreadsheet.worksheet("code stations")

def GetWilayaFromSheet():
    data = sheet_wilayas.get_all_records()
    return data

def GetStationsFromSheet():
    values = sheet_stations.get("A:B")  # récupère uniquement colonnes A et B
    headers, rows = values[0], values[1:]
    data = [dict(zip(headers, row)) for row in rows]
    return data

# Récupérez les wilayas et les stations from google sheet (chargé une fois au démarrage)
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
        sheet_commandes.append_row([client_name, produit, quantite])  # Utilisez sheet_commandes optimisé
        return redirect(url_for("afficher"))
    return render_template("manuel.html")

# --- Route Flask ---
@app.route("/auto", methods=["GET", "POST"])
def auto():
    message = None
    status = None  # "success" ou "error"
    print("hello from auto 4")
    if request.method == "POST":
        raw_data = request.form.get("data")
        print(raw_data)
        try:
            # Lazy loading : import seulement si POST
            from parese_commande import InsererCommande
            if not wilayas:
                raise ValueError("Wilaya introuvable depuis google sheet.")
            if not stations:
                raise ValueError("Station introuvable depuis google sheet.")
            
            InsererCommande(raw_data, wilayas, stations)
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

    commandes = sheet_commandes.get_all_records()  # Utilisez sheet_commandes optimisé
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False pour prod/Render