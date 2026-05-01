import streamlit as st
import mercadopago
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# 🔑 MERCADO PAGO
# =========================
MP_TOKEN = "SEU_TOKEN_AQUI"
sdk = mercadopago.SDK(MP_TOKEN)

# =========================
# 🔥 FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")  # ✅ corrigido
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("💎 Acesso PRO")

# =========================
# 🔐 LOGIN
# =========================
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar"):
    if email == "" or senha == "":
        st.warning("Preencha tudo")
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
    if "payment_id" in st.session_state:
        if st.button("Verificar pagamento"):
            result = sdk.payment().get(st.session_state["payment_id"])
            status = result["response"]["status"]

            if status == "approved":
                db.collection("users").document(st.session_state["email"]).update({
                    "pro": True
                })

                st.session_state["pro"] = True
                st.success("🎉 PRO liberado!")
                st.rerun()
            else:
                st.warning(f"Status: {status}")
