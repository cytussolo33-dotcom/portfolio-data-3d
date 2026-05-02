import streamlit as st
import json
import os
import requests
import time

# ========================
# CONFIG
# ========================
MP_TOKEN = os.environ.get("MP_ACCESS_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL do Render

# ========================
# BANCO SIMPLES
# ========================
def carregar():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

# ========================
# LOGIN
# ========================
if "user" not in st.session_state:
    st.session_state.user = None

st.title("📊 Controle PRO")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar conta"):
    users = carregar()

    if email not in users:
        users[email] = {"senha": senha, "pro": False}
        salvar(users)
        st.success("Conta criada!")

    if users[email]["senha"] == senha:
        st.session_state.user = email
        st.success("Login feito!")

# ========================
# APP
# ========================
if st.session_state.user:

    email = st.session_state.user
    users = carregar()

    st.write(f"👤 {email}")

    ganho = st.number_input("💰 Ganho", 0.0)
    gasto = st.number_input("💸 Gasto", 0.0)

    lucro = ganho - gasto
    st.success(f"Lucro: R$ {lucro:.2f}")

    if st.button("Salvar dia"):
        st.success("Salvo!")

    # ========================
    # PRO STATUS
    # ========================
    if users[email].get("pro"):
        st.success("🚀 Você é PRO!")
        st.write("Histórico completo liberado")
    else:
        st.warning("Plano grátis")

        # ========================
        # GERAR PIX
        # ========================
        if st.button("💳 Gerar PIX"):

            url = "https://api.mercadopago.com/v1/payments"

            headers = {
                "Authorization": f"Bearer {MP_TOKEN}",
                "Content-Type": "application/json"
            }

            body = {
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {
                    "email": email
                },
                "external_reference": email,
                "notification_url": WEBHOOK_URL
            }

            r = requests.post(url, json=body, headers=headers)
            pagamento = r.json()

            try:
                qr = pagamento["point_of_interaction"]["transaction_data"]["qr_code"]
                qr_img = pagamento["point_of_interaction"]["transaction_data"]["qr_code_base64"]

                st.image(f"data:image/png;base64,{qr_img}")
                st.code(qr)

                st.info("Após pagar, clique em verificar")

                st.session_state.payment_id = pagamento["id"]

            except:
                st.error("Erro ao gerar pagamento")

        # ========================
        # VERIFICAR PAGAMENTO (ANTI BUG)
        # ========================
        if "payment_id" in st.session_state:

            if st.button("✅ Já paguei, verificar"):

                url = f"https://api.mercadopago.com/v1/payments/{st.session_state.payment_id}"

                headers = {
                    "Authorization": f"Bearer {MP_TOKEN}"
                }

                r = requests.get(url, headers=headers)
                payment = r.json()

                if payment.get("status") == "approved":

                    users[email]["pro"] = True
                    salvar(users)

                    st.success("🚀 PRO ativado!")
                    time.sleep(2)
                    st.rerun()

                else:
                    st.warning("Pagamento ainda não confirmado")
