from flask import Flask, request
import mercadopago
import os
import json

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise Exception("MP_ACCESS_TOKEN não configurado")

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# BANCO
# ==============================
def carregar_usuarios():
    if not os.path.exists("users.json"):
        return {}
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_usuarios(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

# ==============================
# WEBHOOK
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if not data:
        return "no data", 400

    if data.get("type") == "payment":

        payment_id = data["data"]["id"]

        payment = sdk.payment().get(payment_id)
        info = payment["response"]

        print("📦 Pagamento recebido:", info)

        if info.get("status") == "approved":

            email = info.get("external_reference")

            if not email:
                return "no email", 200

            users = carregar_usuarios()

            if email in users:
                users[email]["pro"] = True
                salvar_usuarios(users)

                print(f"🔥 {email} virou PRO!")

    return "OK", 200

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
