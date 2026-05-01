import streamlit as st
import mercadopago

# =========================
# 🔑 CONFIG
# =========================
MP_TOKEN = "SEU_TOKEN_AQUI"
sdk = mercadopago.SDK(MP_TOKEN)

LIMITE_FREE = 5

st.set_page_config(page_title="Controle de Entregas", page_icon="📦")

# =========================
# 🔐 LOGIN SIMPLES
# =========================
st.title("🔐 Login")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar"):
    st.session_state["logado"] = True
    st.session_state["email"] = email
    st.session_state["pro"] = False
    st.success("Login feito!")

# =========================
# 📦 APP
# =========================
if st.session_state.get("logado"):

    st.title("📦 Controle de Entregas")

    st.write(f"👤 {st.session_state['email']}")

    # Inicializa dados
    if "entregas" not in st.session_state:
        st.session_state["entregas"] = []

    # =========================
    # 🎯 META
    # =========================
    meta = st.number_input("Quanto quer ganhar hoje (R$)", min_value=0.0)

    # =========================
    # ➕ NOVA ENTREGA
    # =========================
    st.subheader("📦 Nova Entrega")

    valor = st.number_input("Valor da entrega", min_value=0.0)
    custo = st.number_input("Custo", min_value=0.0)

    if st.button("Adicionar entrega"):

        # 🚫 BLOQUEIO FREE
        if not st.session_state.get("pro") and len(st.session_state["entregas"]) >= LIMITE_FREE:
            st.error("🚫 Limite grátis atingido! Vire PRO 🚀")
        else:
            st.session_state["entregas"].append({
                "valor": valor,
                "custo": custo
            })
            st.success("Entrega adicionada!")

    # =========================
    # 📋 LISTA
    # =========================
    st.subheader("📋 Entregas")

    if len(st.session_state["entregas"]) == 0:
        st.info("Sem entregas ainda")
    else:
        for i, e in enumerate(st.session_state["entregas"]):
            st.write(f"{i+1}. 💰 {e['valor']} | 💸 {e['custo']}")

    # =========================
    # 📊 RESUMO
    # =========================
    st.subheader("📊 Resumo")

    total = sum(e["valor"] for e in st.session_state["entregas"])
    custos = sum(e["custo"] for e in st.session_state["entregas"])
    lucro = total - custos

    st.write(f"💰 Total: R$ {total}")
    st.write(f"💸 Custos: R$ {custos}")
    st.write(f"🟢 Lucro: R$ {lucro}")

    if meta > 0:
        falta = meta - lucro
        if falta > 0:
            st.warning(f"⚠️ Faltam R$ {falta:.2f} para sua meta")
        else:
            st.success("🎉 Meta atingida!")

    if st.button("🗑️ Limpar tudo"):
        st.session_state["entregas"] = []

    # =========================
    # 💎 PRO
    # =========================
    st.subheader("💎 Versão PRO")

    if st.session_state.get("pro"):
        st.success("🚀 Você é PRO!")
    else:
        st.warning(f"Plano grátis: até {LIMITE_FREE} entregas")

        # =========================
        # 💳 PAGAMENTO PIX
        # =========================
        if st.button("💳 Virar PRO (R$9,90)"):

            pagamento = {
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {
                    "email": st.session_state["email"]
                }
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

            if st.button("✅ Já paguei"):

                result = sdk.payment().get(st.session_state["payment_id"])
                status = result["response"]["status"]

                if status == "approved":
                    st.session_state["pro"] = True
                    st.success("🚀 Agora você é PRO!")
                    st.rerun()
                else:
                    st.warning(f"Status: {status}")
