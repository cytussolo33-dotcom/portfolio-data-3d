import streamlit as st
import mercadopago

# ==============================
# CONFIG (SEGURO)
# ==============================
ACCESS_TOKEN = st.secrets["MP_TOKEN"]

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ==============================
# SESSION STATE
# ==============================
if "pro" not in st.session_state:
    st.session_state["pro"] = False

if "payment_id" not in st.session_state:
    st.session_state["payment_id"] = None

# ==============================
# FUNÇÕES
# ==============================
def criar_pagamento():
    payment_data = {
        "transaction_amount": 9.90,
        "description": "Entregas PRO - Versão Premium",
        "payment_method_id": "pix",
        "payer": {
            "email": "seuemailreal@gmail.com"
        }
    }

    response = sdk.payment().create(payment_data)

    # 🛡️ proteção contra erro
    if "response" in response:
        return response["response"]
    else:
        return response


def verificar_pagamento(payment_id):
    result = sdk.payment().get(payment_id)

    if "response" in result:
        return result["response"]
    return result

# ==============================
# UI
# ==============================
st.title("📦 Entregas PRO")
st.caption("Controle suas entregas e maximize seu lucro 💰")

# RESUMO (simples)
st.subheader("📊 Resumo")
st.write("💰 Total: R$ 200.00")
st.write("💸 Custos: R$ 30.00")
st.write("🟢 Lucro: R$ 170.00")

st.divider()

# ==============================
# PRO
# ==============================
st.subheader("💎 Versão PRO")

if st.session_state["pro"]:
    st.success("🚀 Você é PRO!")
else:
    st.warning("⚠️ Plano grátis limitado a 5 entregas")

    if st.button("💳 Virar PRO (R$9,90)"):
        data = criar_pagamento()

        if "id" not in data:
            st.error("Erro ao gerar pagamento 😢")
            st.write(data)
        else:
            st.session_state["payment_id"] = data["id"]

            st.success("Pagamento gerado!")

            # 📲 QR PIX
            try:
                dados = data["point_of_interaction"]["transaction_data"]

                st.subheader("📲 Pague com PIX")
                st.image(f"data:image/png;base64,{dados['qr_code_base64']}")
                st.code(dados["qr_code"])
            except:
                st.warning("QR não disponível")

            # 🔗 Link
            try:
                link = data["transaction_details"]["external_resource_url"]
                st.write("🔗 Link de pagamento:")
                st.write(link)
            except:
                pass

# ==============================
# VERIFICAR PAGAMENTO
# ==============================
if st.session_state["payment_id"]:
    if st.button("✅ Já paguei (verificar)"):
        status = verificar_pagamento(st.session_state["payment_id"])

        if status.get("status") == "approved":
            st.success("🎉 PRO ativado!")
            st.session_state["pro"] = True
            st.rerun()
        else:
            st.warning(f"Status: {status.get('status')}")
