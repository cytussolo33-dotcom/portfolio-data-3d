import streamlit as st
import mercadopago

# ==============================
# CONFIG
# ==============================
ACCESS_TOKEN = st.secrets["MP_TOKEN"]
sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# SESSION
# ==============================
if "pro" not in st.session_state:
    st.session_state["pro"] = False

if "payment_id" not in st.session_state:
    st.session_state["payment_id"] = None

# ==============================
# FUNÇÕES
# ==============================
def criar_pagamento(email):
    payment_data = {
        "transaction_amount": 9.90,
        "description": "Entregas PRO",
        "payment_method_id": "pix",
        "payer": {"email": email}
    }

    response = sdk.payment().create(payment_data)
    return response.get("response", response)


def verificar_pagamento(payment_id):
    result = sdk.payment().get(payment_id)
    return result.get("response", result)

# ==============================
# LOGIN SIMPLES
# ==============================
st.title("📦 Entregas PRO")

email = st.text_input("📧 Seu email")

if not email:
    st.warning("Digite seu email para continuar")
    st.stop()

# ==============================
# PRO STATUS
# ==============================
st.subheader("💎 Plano PRO")

if st.session_state["pro"]:
    st.success("🚀 PRO ativo")

else:
    st.warning("Plano grátis limitado")

    # GERAR PAGAMENTO
    if st.button("💳 Virar PRO (R$9,90)"):
        data = criar_pagamento(email)

        if "id" not in data:
            st.error("Erro ao gerar pagamento")
            st.write(data)
        else:
            st.session_state["payment_id"] = data["id"]

            st.success("Pagamento gerado!")

            try:
                td = data["point_of_interaction"]["transaction_data"]

                st.subheader("📲 Pague com PIX")
                st.image(f"data:image/png;base64,{td['qr_code_base64']}")
                st.code(td["qr_code"])
            except:
                st.warning("QR não disponível")

# ==============================
# VERIFICAÇÃO AUTOMÁTICA (SIMPLES)
# ==============================
if st.session_state["payment_id"]:

    status = verificar_pagamento(st.session_state["payment_id"])

    if status.get("status") == "approved":
        st.session_state["pro"] = True
        st.success("🎉 Pagamento aprovado! PRO liberado!")
        st.rerun()

    else:
        st.info(f"⏳ Aguardando pagamento... ({status.get('status')})")
