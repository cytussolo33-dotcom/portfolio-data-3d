import streamlit as st
import mercadopago
import json
import os
import hashlib

# =========================
# CONFIG
# =========================
ACCESS_TOKEN = st.secrets["MP_ACCESS_TOKEN"]
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

sdk = mercadopago.SDK(ACCESS_TOKEN)

# =========================
# BANCO
# =========================
def carregar():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# =========================
# SESSION
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.email = ""

# =========================
# LOGIN
# =========================
if not st.session_state.logado:

    st.title("🔐 Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar / Criar conta"):
        users = carregar()

        if email in users:
            if users[email]["senha"] == hash_senha(senha):
                st.session_state.logado = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error("Senha incorreta")
        else:
            users[email] = {
                "senha": hash_senha(senha),
                "pro": False,
                "dados": []
            }
            salvar(users)
            st.session_state.logado = True
            st.session_state.email = email
            st.rerun()

    st.stop()

# =========================
# APP
# =========================
users = carregar()
email = st.session_state.email

if email not in users:
    st.session_state.logado = False
    st.rerun()

user = users[email]

st.title("💰 Controle PRO")
st.write(f"👤 {email}")

# =========================
# CONTROLE
# =========================
ganho = st.number_input("💰 Ganho", 0.0)
gasto = st.number_input("💸 Gasto", 0.0)

lucro = ganho - gasto
st.success(f"Lucro: R$ {lucro:.2f}")

if st.button("💾 Salvar"):
    user["dados"].append(lucro)
    users[email] = user
    salvar(users)
    st.success("Salvo!")

# =========================
# PRO
# =========================
if user.get("pro"):
    st.success("🚀 PRO ativo")

    if user["dados"]:
        st.line_chart(user["dados"])
else:
    st.warning("Plano grátis")

    st.markdown("## 🚀 Virar PRO")

    if st.button("💳 Pagar com PIX"):
        pagamento = {
            "transaction_amount": 9.90,
            "description": "Plano PRO",
            "payment_method_id": "pix",
            "payer": {"email": email},
            "external_reference": email,
            "notification_url": WEBHOOK_URL
        }

        res = sdk.payment().create(pagamento)

        if res["status"] == 201:
            data = res["response"]["point_of_interaction"]["transaction_data"]

            st.image(f"data:image/png;base64,{data['qr_code_base64']}")
            st.code(data["qr_code"])
            st.info("Pague o PIX e aguarde. Depois atualize a página.")
        else:
            st.error("Erro ao gerar pagamento")
            st.write(res)
