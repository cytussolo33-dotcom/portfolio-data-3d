import streamlit as st
import mercadopago
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# ==============================
# CONFIG
# ==============================
ACCESS_TOKEN = st.secrets["MP_TOKEN"]
WEBHOOK_URL = st.secrets["WEBHOOK_URL"]

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# FIREBASE (CORRIGIDO)
# ==============================
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)

db = firestore.client()

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

    user_ref = db.collection("users").document(email)
    user = user_ref.get()

    if user.exists:
        data = user.to_dict()

        if data["senha"] == hash_senha(senha):
            st.session_state["logado"] = True
            st.session_state["email"] = email
            st.session_state["pro"] = data.get("pro", False)
            st.success("Login feito!")
        else:
            st.error("Senha incorreta")
    else:
        user_ref.set({
            "senha": hash_senha(senha),
            "pro": False
        })
        st.success("Conta criada!")

# ==============================
# AREA LOGADA
# ==============================
if st.session_state["logado"]:

    st.write(f"👤 {st.session_state['email']}")

    user = db.collection("users").document(st.session_state["email"]).get()
    if user.exists:
        st.session_state["pro"] = user.to_dict().get("pro", False)

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
                    "email": "test_user_123@test.com"  # evita erro de credencial
                },
                "notification_url": WEBHOOK_URL
            }

            res = sdk.payment().create(pagamento)

            if res["status"] == 201:
                data = res["response"]
                td = data["point_of_interaction"]["transaction_data"]

                st.image(f"data:image/png;base64,{td['qr_code_base64']}")
                st.code(td["qr_code"])
                st.info("Após pagar, o acesso será liberado automaticamente.")
            else:
                st.error("Erro ao gerar pagamento")
                st.write(res)
