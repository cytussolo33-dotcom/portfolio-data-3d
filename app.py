import streamlit as st
import mercadopago
import json
import os
import hashlib

# ==============================
# CONFIG
# ==============================
def get_secret(key, default=None):
    try:
        return st.secrets[key]
    except Exception:
        return default

ACCESS_TOKEN = get_secret("MP_ACCESS_TOKEN")
WEBHOOK_URL = get_secret("WEBHOOK_URL")

DEV_MODE = True  # desligar depois

if not ACCESS_TOKEN:
    st.error("❌ MP_ACCESS_TOKEN não configurado!")
    st.stop()

if not WEBHOOK_URL:
    st.warning("⚠️ WEBHOOK_URL não configurado — PRO não será automático")

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# BANCO (JSON)
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

if st.button("Entrar / Criar conta"):
    users = carregar_usuarios()

    if email in users:
        if users[email]["senha"] == hash_senha(senha):
            st.session_state["logado"] = True
            st.session_state["email"] = email
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

    # sempre atualiza do JSON
    if st.session_state["email"] in users:
        st.session_state["pro"] = users[st.session_state["email"]].get("pro", False)

    # ==============================
    # 🚀 PRO
    # ==============================
    if st.session_state["pro"]:
        st.success("🚀 PRO ativo")

        st.subheader("📊 Painel")
        st.write("💰 Total: R$ 200")
        st.write("💸 Custos: R$ 30")
        st.write("🟢 Lucro: R$ 170")

    # ==============================
    # 💳 FREE
    # ==============================
    else:
        st.warning("Plano grátis limitado")

        # 🔓 DEV
        if DEV_MODE:
            if st.button("🔓 Liberar PRO (DEV)"):
                users[st.session_state["email"]]["pro"] = True
                salvar_usuarios(users)
                st.success("🔥 PRO liberado")
                st.rerun()

        # 💳 PAGAMENTO
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

            try:
                res = sdk.payment().create(pagamento)

                if res["status"] == 201:
                    data = res["response"]
                    td = data["point_of_interaction"]["transaction_data"]

                    st.image(f"data:image/png;base64,{td['qr_code_base64']}")
                    st.code(td["qr_code"])
                    st.info("Pague o PIX e depois atualize a página para liberar o PRO.")
                else:
                    st.error("Erro ao gerar pagamento")
                    st.write(res)

            except Exception as e:
                st.error("Erro no pagamento")
                st.write(str(e))
