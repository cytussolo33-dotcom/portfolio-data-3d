import streamlit as st

st.set_page_config(page_title="Lucro do Entregador", page_icon="💰")

st.title("💰 Controle de Lucro do Entregador")

# =========================
# 🔐 LOGIN SIMPLES
# =========================
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar"):
    st.session_state["logado"] = True
    st.session_state["email"] = email
    st.session_state["pro"] = False
    st.success("Login ativado!")

# =========================
# 📦 APP PRINCIPAL
# =========================
if st.session_state.get("logado"):

    st.write(f"👤 {st.session_state['email']}")

    # =========================
    # 🎯 META
    # =========================
    st.subheader("🎯 Meta do Dia")
    meta = st.number_input("Quanto quer ganhar hoje (R$)", 0.0)

    # =========================
    # 📦 ENTREGAS
    # =========================
    st.subheader("📦 Nova Entrega")

    valor = st.number_input("Valor da entrega", 0.0)
    custo = st.number_input("Custo", 0.0)

    if "entregas" not in st.session_state:
        st.session_state.entregas = []

    # =========================
    # 🚫 LIMITE GRÁTIS
    # =========================
    if not st.session_state.get("pro") and len(st.session_state.entregas) >= 5:
        st.warning("🚫 Limite grátis atingido!")
        st.info("Vire PRO para continuar usando sem limites 👇")
    else:
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
            st.write(f"{i+1}. 💵 {e['valor']} | 💸 {e['custo']}")
    else:
        st.info("Sem entregas ainda")

    # =========================
    # 📊 RESUMO
    # =========================
    st.subheader("📊 Resumo")

    if st.session_state.entregas:
        total = sum(e["valor"] for e in st.session_state.entregas)
        custo_total = sum(e["custo"] for e in st.session_state.entregas)
        lucro = total - custo_total

        st.write(f"💰 Total: R$ {total:.2f}")
        st.write(f"💸 Custos: R$ {custo_total:.2f}")
        st.write(f"🟢 Lucro: R$ {lucro:.2f}")

        if meta > 0:
            falta = meta - lucro
            if falta > 0:
                st.warning(f"⚠️ Faltam R$ {falta:.2f} para sua meta")
            else:
                st.success("🎉 Meta batida!")

    # =========================
    # 🗑️ LIMPAR
    # =========================
    if st.button("🗑️ Limpar tudo"):
        st.session_state.entregas = []

    # =========================
    # 💎 PRO (ESTRUTURA PRONTA)
    # =========================
    st.subheader("💎 Versão PRO")

    if st.session_state.get("pro"):
        st.success("🚀 Você é PRO!")
    else:
        st.warning("Plano grátis: até 5 entregas")

        st.markdown("### 💎 Vantagens:")
        st.write("- Entregas ilimitadas")
        st.write("- Sem bloqueio")
        st.write("- Futuras melhorias")

        st.markdown("### 💳 Pagamento")

        st.info("🔒 Pagamento em teste (simulação)")

        # =========================
        # 🔥 SIMULAÇÃO DE PAGAMENTO
        # =========================
        if st.button("💳 Simular pagamento"):
            st.session_state["pagamento_aprovado"] = True

        # =========================
        # 🔓 LIBERAÇÃO AUTOMÁTICA
        # =========================
        if st.session_state.get("pagamento_aprovado"):
            st.session_state["pro"] = True
            st.success("🎉 Pagamento aprovado! PRO liberado automaticamente.")
            st.rerun()
