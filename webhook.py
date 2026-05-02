from flask import Flask, request
import mercadopago
import os
import json

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# BANCO JSON (igual ao app)
# ==============================
def carregar_usuarios():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar_usuarios(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

# ==============================
# WEBHOOK
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if data and data.get("type") == "payment":

        payment_id = data["data"]["id"]
        payment = sdk.payment().get(payment_id)
        info = payment["response"]

        if info["status"] == "approved":

            email = info["payer"]["email"]

            users = carregar_usuarios()

            if email in users:
                users[email]["pro"] = True
                salvar_usuarios(users)
                print(f"🔥 {email} virou PRO!")

    return "OK", 200

if __name__ == "__main__":
    app.run()
