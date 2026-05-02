from flask import Flask, request
import json
import os
import requests

app = Flask(__name__)

def carregar():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    try:
        if "data" in data:
            payment_id = data["data"]["id"]

            url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
            headers = {"Authorization": f"Bearer {os.environ.get('MP_ACCESS_TOKEN')}"}

            r = requests.get(url, headers=headers)
            payment = r.json()

            if payment["status"] == "approved":

                email = payment["external_reference"]

                users = carregar()

                if email in users:
                    users[email]["pro"] = True
                    salvar(users)
                    print("PRO liberado:", email)

    except Exception as e:
        print("Erro:", str(e))

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
