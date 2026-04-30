import streamlit as st
import mercadopago

MP_TOKEN = "APP_USR-3208236820348419-043015-a94d2bb3e00c239cf241711284a86683-1591849347

sdk = mercadopago.SDK(MP_TOKEN)

st.title("💎 Acesso PRO")

if "pro" not in st.session_state:
    st.session_state["pro"] = False

if st.session_state["pro"]:
    st.success("Você é PRO 🚀")
else:
    email = st.text_input("Digite seu e-mail")

    if st.button("💳 Gerar PIX"):
        if email:
            pagamento = {
                "transaction_amount": 9.90,
                "description": "Lucro Delivery PRO",
                "payment_method_id": "pix",
                "payer": {"email": email}
            }

            res = sdk.payment().create(pagamento)
            data = res["response"]

            st.session_state["payment_id"] = data["id"]

            qr = data["point_of_interaction"]["transaction_data"]["qr_code_base64"]
            copia = data["point_of_interaction"]["transaction_data"]["qr_code"]

            st.image(f"data:image/png;base64,{qr}")
            st.code(copia)

if "payment_id" in st.session_state:
    if st.button("Verificar pagamento"):
        result = sdk.payment().get(st.session_state["payment_id"])
        status = result["response"]["status"]

        if status == "approved":
            st.session_state["pro"] = True
            st.success("PRO liberado 🚀")
