import streamlit as st
import mercadopago
import json
import os

# 🔑 COLE SEU TOKEN AQUI (com aspas)
MP_TOKEN = "APP_USR-3208236820348419-043015-a94d2bb3e00c239cf241711284a86683-1591849347"

sdk = mercadopago.SDK(MP_TOKEN)

st.title("💎 Acesso PRO")

# =========================
# 📂 Banco simples (arquivo)
# =========================
DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# =========================
# 🔐 Login / Cadastro
# =========================
menu = st.radio("Escolha:", ["Login", "Cadastro"])

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if menu == "Cadastro":
    if st.button("Criar conta"):
        if email in users:
            st.warning("Usuário já existe")
        else:
            users[email] = {"senha": senha, "pro": False}
            save_users(users)
            st.success("Conta criada!")

if menu == "Login":
    if st.button("Entrar"):
        if email in users and users[email]["senha"] == senha:
            st.session_state["logado"] = True
            st.session_state["email"] = email
            st.success("Login feito!")
        else:
            st.error("Email ou senha incorretos")

# =========================
# 💎 Área PRO + Pagamento
# =========================
if "logado" in st.session_state and st.session_state["logado"]:
    user = users[st.session_state["email"]]

    st.write(f"👤 Logado como: {st.session_state['email']}")

    if user["pro"]:
        st.success("🚀 Você é PRO!")
        st.write("Conteúdo exclusivo liberado aqui 👑")

    else:
        st.warning("Você ainda não é PRO")

        if st.button("💳 Gerar PIX"):
            pagamento = {
                "transaction_amount": 9.90,
                "description": "Acesso PRO",
                "payment_method_id": "pix",
                "payer": {"email": st.session_state["email"]}
            }

            res = sdk.payment().create(pagamento)
            
            if "response" not in res:
                st.error("Erro ao criar pagamento")
                st.write(res)
            else:
                data = res["response"]

                st.session_state["payment_id"] = data["id"]

                qr = data["point_of_interaction"]["transaction_data"]["qr_code_base64"]
                copia = data["point_of_interaction"]["transaction_data"]["qr_code"]

                st.image(f"data:image/png;base64,{qr}")
                st.code(copia)

                st.info("Pague o PIX e depois clique em verificar")

        # 🔍 Verificar pagamento
        if "payment_id" in st.session_state:
            if st.button("🔍 Verificar pagamento"):
                result = sdk.payment().get(st.session_state["payment_id"])
                status = result["response"]["status"]

                if status == "approved":
                    users[st.session_state["email"]]["pro"] = True
                    save_users(users)

                    st.success("🎉 PRO liberado!")
                    st.rerun()
                else:
                    st.warning(f"Status: {status}")
