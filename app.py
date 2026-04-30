import mercadopago
import base64

MP_TOKEN = "SEU_TOKEN_AQUI"

sdk = mercadopago.SDK(MP_TOKEN)

st.header("💎 Acesso PRO")

if usuario_info.get("pro"):
    st.success("Você é PRO 🚀")
else:
    email = st.text_input("Digite seu e-mail")

    if st.button("💳 Gerar PIX"):
        pagamento = {
            "transaction_amount": 9.90,
            "description": "Lucro Delivery PRO",
            "payment_method_id": "pix",
            "payer": {
                "email": email
            }
        }

        res = sdk.payment().create(pagamento)
        data = res["response"]

        st.session_state["payment_id"] = data["id"]

        qr_code = data["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        qr_text = data["point_of_interaction"]["transaction_data"]["qr_code"]

        st.image(f"data:image/png;base64,{qr_code}")
        st.code(qr_text)

        st.info("📱 Pague o PIX e depois clique em verificar pagamento")

# =====================
# VERIFICAR PAGAMENTO
# =====================

if "payment_id" in st.session_state:
    if st.button("🔄 Verificar pagamento"):
        result = sdk.payment().get(st.session_state["payment_id"])
        status = result["response"]["status"]

        if status == "approved":
            usuarios[user]["pro"] = True
            salvar_usuarios(usuarios)
            st.success("Pagamento aprovado! PRO liberado 🚀")
            st.rerun()
        else:
            st.warning("Pagamento ainda não identificado")
