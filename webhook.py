from flask import Flask, request
import mercadopago
import os
import json

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# BANCO JSON
# ==============================
def carregar_usuarios():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar_usuarios(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# ==============================
# WEBHOOK
# ==============================
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("📩 Webhook recebido:", data)

        # valida evento
        if data and data.get("type") == "payment":

            payment_id = data["data"]["id"]
            payment = sdk.payment().get(payment_id)

            if payment["status"] != 200:
                print("❌ Erro ao buscar pagamento")
                return "erro", 400

            info = payment["response"]
            status = info.get("status")

            print("💰 Status do pagamento:", status)

            # só libera se aprovado
            if status == "approved":

                email = info["payer"]["email"]
                print("📧 Email:", email)

                users = carregar_usuarios()

                # cria usuário se não existir
                if email not in users:
                    users[email] = {
                        "senha": "",
                        "pro": True
                    }
                else:
                    users[email]["pro"] = True

                salvar_usuarios(users)

                print(f"🔥 {email} virou PRO!")

        return "OK", 200

    except Exception as e:
        print("❌ ERRO NO WEBHOOK:", str(e))
        return "erro", 500

# ==============================
# START
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
