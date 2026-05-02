from flask import Flask, request
import mercadopago

app = Flask(__name__)

sdk = mercadopago.SDK("APP_USR-4942813099956982-050118-47ab93b27d9acf41b0390203733dad02-3369029229")

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    if data.get("type") == "payment":

        payment_id = data["data"]["id"]
        payment = sdk.payment().get(payment_id)

        info = payment["response"]

        if info["status"] == "approved":

            email = info["payer"]["email"]

            with open("pro_users.txt", "a") as f:
                f.write(email + "\n")

    return "OK", 200

app.run(host="0.0.0.0", port=10000)
