import streamlit as st

st.set_page_config(page_title="Controle de Entregas", page_icon="📦")

st.title("💎 Acesso PRO")

# =========================
# 🔐 LOGIN SIMPLES
# =========================
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar"):
    st.session_state["logado"] = True
    st.session_state["email"] = email
    st.session_state["pro"] = False
    st.success("Login simples ativado!")

# =========================
# 📦 APP PRINCIPAL
# =========================
if st.session_state.get("logado"):

    st.write(f"👤 {st.session_state['email']}")

    st.subheader("📦 Controle de Entregas")

    valor = st.number_input("Valor da entrega (R$)", min_value=0.0, step=1.0)
    custo = st.number_input("Custo (R$)", min_value=0.0, step=1.0)

    if "entregas" not in st.session_state:
        st.session_state.entregas = []

    if st.button("Adicionar entrega"):
        st.session_state.entregas.append({
            "valor": valor,
            "custo": custo
        })
        st.success("Entrega adicionada!")

    # =========================
    # 📋 LISTA
    # =========================
    st.subheader("📋 Entregas")

    if st.session_state.entregas:
        for i, e in enumerate(st.session_state.entregas):
            st.write(f"{i+1}. Valor: R$ {e['valor']} | Custo: R$ {e['custo']}")
    else:
        st.info("Sem dados ainda")

    # =========================
    # 📊 RESUMO
    # =========================
    st.subheader("📊 Resumo")

    if st.session_state.entregas:
        total = sum(e["valor"] for e in st.session_state.entregas)
        custo_total = sum(e["custo"] for e in st.session_state.entregas)
        lucro = total - custo_total

        st.write(f"💰 Total recebido: R$ {total:.2f}")
        st.write(f"💸 Total gasto: R$ {custo_total:.2f}")
        st.write(f"🟢 Lucro: R$ {lucro:.2f}")

    # =========================
    # 🗑️ LIMPAR
    # =========================
    if st.button("🗑️ Limpar tudo"):
        st.session_state.entregas = []
        st.warning("Dados apagados!")

    # =========================
    # 💎 PRO (FAKE)
    # =========================
    st.subheader("💎 Versão PRO")

    if st.session_state.get("pro"):
        st.success("🚀 Você é PRO!")
    else:
        st.warning("Você não é PRO")

        if st.button("Ativar PRO"):
            st.session_state["pro"] = True
            st.success("Agora você é PRO 😎")
