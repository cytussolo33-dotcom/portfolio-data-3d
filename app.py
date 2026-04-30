import streamlit as st
import mercadopago

# 🔑 COLE SEU TOKEN DE PRODUÇÃO AQUI
MP_TOKEN = "APP_USR-COLE_SEU_TOKEN_AQUI"

sdk = mercadopago.SDK(MP_TOKEN)

st.title("💎 Acesso PRO")

# controle simples
if "pro" not in st.session_state:
    st.session_state["pro"] = False

# se já for PRO
if st.session_state["pro"]:
    st.success("Você é PRO 🚀")

# se não for PRO
else:
    email = st.text_input("Digite seu e-mail")

    if st.button("💳 Gerar PIX"):
        if not email:
            st.warning("Digite um e-mail primeiro")
        else:
            pagamento = {
                "transaction_amount": 9.90,
                "description": "Lucro Delivery PRO",
                "payment_method_id": "pix",
                "payer": {"email": email}
            }

            try:
                res = sdk.payment().create(pagamento)

                # DEBUG seguro
                if "response" not in res:
                    st.error("Erro ao criar pagamento")
                    st.write(res)
                else:
                    data = res["response"]

                    if "id" not in data:
                        st.error("Erro no pagamento")
                        st.write(data)
                    else:
                        st.session_state["payment_id"] = data["id"]

                        qr_code = data["point_of_interaction"]["transaction_data"]["qr_code_base64"]
                        qr_text = data["point_of_interaction"]["transaction_data"]["qr_code"]

                        st.image(f"data:image/png;base64,{qr_code}")
                        st.code(qr_text)

                        st.info("📱 Pague o PIX e depois clique em verificar pagamento")

            except Exception as e:
                st.error(f"Erro geral: {e}")

# verificar pagamento
if "payment_id" in st.session_state:
    if st.button("🔄 Verificar pagamento"):
        try:
            result = sdk.payment().get(st.session_state["payment_id"])

            if "response" not in result:
                st.error("Erro ao verificar pagamento")
                st.write(result)
            else:
                status = result["response"].get("status")

                if status == "approved":
                    st.session_state["pro"] = True
                    st.success("Pagamento aprovado! PRO liberado 🚀")
                    st.rerun()
                else:
                    st.warning(f"Status atual: {status}")

        except Exception as e:
            st.error(f"Erro ao verificar: {e}")
