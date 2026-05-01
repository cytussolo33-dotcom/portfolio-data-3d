import streamlit as st
import mercadopago

# =========================
# 🔑 MERCADO PAGO
# =========================
MP_TOKEN = "SEU_TOKEN_AQUI"  # ⚠️ troca depois
sdk = mercadopago.SDK(MP_TOKEN)

st.title("💎 Acesso PRO")

# =========================
# 🔐 LOGIN SIMPLES (LOCAL)
# =========================
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["pro"] = False

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar"):
    # login fake (sem banco)
    st.session_state["logado"] = True
    st.session_state["email"] = email
    st.success("Login feito!")

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
                st.session_state["pro"] = True
                st.success("🎉 PRO liberado!")
                st.rerun()
            else:
                st.warning(f"Status: {status}")
