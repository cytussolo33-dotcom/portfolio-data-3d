import streamlit as st
import json

# =========================
# 🔥 FIREBASE (seguro)
# =========================
db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if "firebase_key" in st.secrets:
        if not firebase_admin._apps:
            firebase_dict = json.loads(st.secrets["firebase_key"])
            cred = credentials.Certificate(firebase_dict)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
    else:
        st.warning("Firebase não configurado")

except Exception as e:
    st.warning("Erro no Firebase - rodando sem banco")

# =========================
# 🔑 MERCADO PAGO (seguro)
# =========================
try:
    import mercadopago
    MP_TOKEN = st.secrets.get("MP_TOKEN", "")

    if MP_TOKEN:
        sdk = mercadopago.SDK(MP_TOKEN)
    else:
        sdk = None
        st.warning("Mercado Pago não configurado")

except:
    sdk = None

st.title("💎 Acesso PRO")

# =========================
# 🔐 LOGIN
# =========================
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar"):

    if db is None:
        st.error("Banco não conectado")
    else:
        user_ref = db.collection("users").document(email)
        user = user_ref.get()

        if user.exists:
            data = user.to_dict()
            if data["senha"] == senha:
                st.session_state["logado"] = True
                st.session_state["email"] = email
                st.session_state["pro"] = data.get("pro", False)
                st.success("Login feito!")
            else:
                st.error("Senha errada")
        else:
            user_ref.set({
                "senha": senha,
                "pro": False
            })
            st.success("Conta criada!")

# =========================
# 💎 AREA PRO
# =========================
if st.session_state.get("logado"):

    st.write(f"👤 {st.session_state['email']}")

    if st.session_state.get("pro"):
        st.success("🚀 Você é PRO!")
    else:
        st.warning("Você não é PRO")

        if sdk is None:
            st.error("Pagamento não disponível")
        else:
            if st.button("💳 Gerar PIX"):
                pagamento = {
                    "transaction_amount": 9.90,
                    "description": "Acesso PRO",
                    "payment_method_id": "pix",
                    "payer": {"email": st.session_state["email"]}
                }

                res = sdk.payment().create(pagamento)
                data = res["response"]

                st.session_state["payment_id"] = data["id"]

                qr = data["point_of_interaction"]["transaction_data"]["qr_code_base64"]
                copia = data["point_of_interaction"]["transaction_data"]["qr_code"]

                st.image(f"data:image/png;base64,{qr}")
                st.code(copia)

    # =========================
    # 🔎 VERIFICAR PAGAMENTO
    # =========================
    if "payment_id" in st.session_state and sdk:
        if st.button("Verificar pagamento"):
            result = sdk.payment().get(st.session_state["payment_id"])
            status = result["response"]["status"]

            if status == "approved" and db:
                db.collection("users").document(st.session_state["email"]).update({
                    "pro": True
                })

                st.session_state["pro"] = True
                st.success("🎉 PRO liberado!")
                st.rerun()
            else:
                st.warning(f"Status: {status}")
