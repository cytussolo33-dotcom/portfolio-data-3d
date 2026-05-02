from flask import Flask, request
import mercadopago
import os

app = Flask(__name__)

# pega o token do Render (Environment Variables)
sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if data and data.get("type") == "payment":

        payment_id = data["data"]["id"]
        payment = sdk.payment().get(payment_id)

        info = payment["response"]

        if info["status"] == "approved":

            email = info["payer"]["email"]

            with open("pro_users.txt", "a") as f:
                f.write(email + "\n")

    return "OK", 200
