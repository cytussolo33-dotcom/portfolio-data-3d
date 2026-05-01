import streamlit as st
import requests

# 🔑 COLOQUE SEU TOKEN AQUI
ACCESS_TOKEN = "SEU_ACCESS_TOKEN_AQUI"

# 📦 Estado inicial
if "logado" not in st.session_state:
    st.session_state.logado = False
if "entregas" not in st.session_state:
    st.session_state.entregas = []
if "pro" not in st.session_state:
    st.session_state.pro = False

# 🔐 LOGIN SIMPLES
if not st.session_state.logado:
    st.title("🔐 Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar / Criar"):
        if email and senha:
            st.session_state.logado = True
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Preencha os dados")

    st.stop()

# 🚀 APP PRINCIPAL
st.title("📦 Entregas PRO")
st.caption("Controle suas entregas e maximize seu lucro 💰")

# 🎯 META
meta = st.number_input("Quanto quer ganhar hoje (R$)", min_value=0.0, step=10.0)

# ➕ NOVA ENTREGA
st.subheader("📦 Nova Entrega")
valor = st.number_input("Valor da entrega", min_value=0.0, step=1.0)
custo = st.number_input("Custo", min_value=0.0, step=1.0)

# 🔒 Limite grátis
limite = 5
if not st.session_state.pro and len(st.session_state.entregas) >= limite:
    st.warning("⚠️ Plano grátis limitado a 5 entregas")
else:
    if st.button("Adicionar entrega"):
        st.session_state.entregas.append((valor, custo))
        st.success("Entrega adicionada!")

# 📋 LISTA
st.subheader("📋 Entregas")

if st.session_state.entregas:
    for i, (v, c) in enumerate(st.session_state.entregas):
        st.write(f"{i+1}. 💰 {v} | 💸 {c}")
else:
    st.info("Sem entregas ainda")

# 📊 RESUMO
st.subheader("📊 Resumo")

total = sum(v for v, c in st.session_state.entregas)
custos = sum(c for v, c in st.session_state.entregas)
lucro = total - custos

st.write(f"💰 Total: R$ {total:.2f}")
st.write(f"💸 Custos: R$ {custos:.2f}")
st.write(f"🟢 Lucro: R$ {lucro:.2f}")

if meta > 0:
    restante = meta - lucro
    if restante > 0:
        st.warning(f"⚠️ Faltam R$ {restante:.2f} para sua meta")
    else:
        st.success("🎉 Meta batida!")

if st.button("🗑 Limpar tudo"):
    st.session_state.entregas = []
    st.rerun()

# 💳 PAGAMENTO MERCADO PAGO
def criar_pagamento():
    url = "https://api.mercadopago.com/v1/payments"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "transaction_amount": 9.90,
        "description": "Entregas PRO - Versão Premium",
        "payment_method_id": "pix",
        "payer": {
            "email": "teste@gmail.com"
        }
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 💎 PRO
st.subheader("💎 Versão PRO")

if st.session_state.pro:
    st.success("🚀 Você é PRO!")
else:
    st.warning("⚠️ Plano grátis limitado a 5 entregas")

    if st.button("💳 Virar PRO (R$9,90)"):
        pagamento = criar_pagamento()

        if "id" in pagamento:
            st.success("Pagamento criado!")

            # 🧠 guarda id sem quebrar
            st.session_state.payment_id = pagamento.get("id", None)

            # 📲 QR Code PIX
            if "point_of_interaction" in pagamento:
                dados = pagamento["point_of_interaction"]["transaction_data"]

                st.subheader("📲 Pague com PIX")

                st.image(f"data:image/png;base64,{dados['qr_code_base64']}")
                st.code(dados["qr_code"])

                st.info("Após pagar, recarregue a página")

        else:
            st.error("Erro ao gerar pagamento")
            st.write(pagamento)

# 🔄 ATIVAR PRO MANUAL (teste)
if st.button("✅ Já paguei (ativar PRO)"):
    st.session_state.pro = True
    st.success("PRO ativado!")
    st.rerun()
