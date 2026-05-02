import streamlit as st
import mercadopago
import json
import os
import hashlib
import time

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

if not ACCESS_TOKEN:
    st.error("❌ MP_ACCESS_TOKEN não configurado!")
    st.stop()

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

if "pagamento_gerado" not in st.session_state:
    st.session_state["pagamento_gerado"] = False

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

    # atualiza status PRO
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

        # botão único (evita spam)
        if not st.session_state["pagamento_gerado"]:
            if st.button("💳 Virar PRO"):

                pagamento = {
                    "transaction_amount": 9.90,
                    "description": "Plano PRO",
                    "payment_method_id": "pix",
                    "payer": {
                        "email": st.session_state["email"]
                    },
                    "external_reference": st.session_state["email"],
                    "notification_url": WEBHOOK_URL
                }

                try:
                    res = sdk.payment().create(pagamento)

                    if res["status"] == 201:
                        data = res["response"]
                        td = data["point_of_interaction"]["transaction_data"]

                        st.session_state["qr"] = td["qr_code_base64"]
                        st.session_state["pix"] = td["qr_code"]
                        st.session_state["pagamento_gerado"] = True

                    else:
                        st.error("Erro ao gerar pagamento")
                        st.write(res)

                except Exception as e:
                    st.error("Erro no pagamento")
                    st.write(str(e))

        # mostra QR persistente
        if st.session_state["pagamento_gerado"]:
            st.image(f"data:image/png;base64,{st.session_state['qr']}")
            st.code(st.session_state["pix"])

            st.info("Pague o PIX. Após pagar, aguarde alguns segundos e clique abaixo.")

            if st.button("🔄 Já paguei / Atualizar"):
                time.sleep(2)
                st.rerun()
