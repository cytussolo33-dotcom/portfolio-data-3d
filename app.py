import streamlit as st
import mercadopago
import hashlib
import json
import os

# ==============================
# CONFIG
# ==============================
ACCESS_TOKEN = st.secrets["MP_TOKEN"]
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

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
        json.dump(data, f)

# ==============================
# SEGURANÇA
# ==============================
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ==============================
# SESSION
# ==============================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "email" not in st.session_state:
    st.session_state["email"] = None

if "pro" not in st.session_state:
    st.session_state["pro"] = False

# ==============================
# LOGIN
# ==============================
st.title("💰 SaaS Entregas PRO")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

users = carregar_usuarios()

if st.button("Entrar / Criar conta"):

    if email in users:
        if users[email]["senha"] == hash_senha(senha):
            st.session_state["logado"] = True
            st.session_state["email"] = email
            st.session_state["pro"] = users[email].get("pro", False)
            st.success("Login feito!")
        else:
            st.error("Senha incorreta")
    else:
        users[email] = {
            "senha": hash_senha(senha),
            "pro": False
        }
        salvar_usuarios(users)
        st.success("Conta criada!")

# ==============================
# AREA LOGADA
# ==============================
if st.session_state["logado"]:

    st.write(f"👤 {st.session_state['email']}")

    users = carregar_usuarios()
    st.session_state["pro"] = users[st.session_state["email"]]["pro"]

    if st.session_state["pro"]:
        st.success("🚀 PRO ativo")

        st.subheader("📊 Painel")
        st.write("💰 Total: R$ 200")
        st.write("💸 Custos: R$ 30")
        st.write("🟢 Lucro: R$ 170")

    else:
        st.warning("Plano grátis limitado")

        if st.button("💳 Virar PRO"):

            pagamento = {
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {
                    "email": st.session_state["email"]
                },
                "notification_url": WEBHOOK_URL
            }

            res = sdk.payment().create(pagamento)

            if res["status"] == 201:
                data = res["response"]
                td = data["point_of_interaction"]["transaction_data"]

                st.image(f"data:image/png;base64,{td['qr_code_base64']}")
                st.code(td["qr_code"])
                st.info("Pague o PIX e depois atualize a página.")
            else:
                st.error("Erro ao gerar pagamento")
                st.write(res)
