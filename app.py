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
    # 🎯 META DIÁRIA
    # =========================
    st.subheader("🎯 Meta do Dia")
    meta = st.number_input("Quanto você quer ganhar hoje (R$)", min_value=0.0, step=10.0)

    # =========================
    # 📦 ENTREGAS
    # =========================
    st.subheader("📦 Registrar Entrega")

    valor = st.number_input("Valor da entrega (R$)", min_value=0.0, step=1.0)
    custo = st.number_input("Custo (R$)", min_value=0.0, step=1.0)

    if "entregas" not in st.session_state:
        st.session_state.entregas = []

    # =========================
    # 🚫 LIMITE GRÁTIS
    # =========================
    if not st.session_state.get("pro") and len(st.session_state.entregas) >= 5:
        st.warning("🚫 Limite grátis atingido! Vire PRO para continuar.")
        st.stop()

    if st.button("Adicionar entrega"):
        st.session_state.entregas.append({
            "valor": valor,
            "custo": custo
        })
        st.success("Entrega adicionada!")

    # =========================
    # 📋 LISTA
    # =========================
    st.subheader("📋 Suas Entregas")

    if st.session_state.entregas:
        for i, e in enumerate(st.session_state.entregas):
            st.write(f"{i+1}. 💵 {e['valor']} | 💸 {e['custo']}")
    else:
        st.info("Nenhuma entrega ainda")

    # =========================
    # 📊 RESUMO
    # =========================
    st.subheader("📊 Resumo do Dia")

    if st.session_state.entregas:
        total = sum(e["valor"] for e in st.session_state.entregas)
        custo_total = sum(e["custo"] for e in st.session_state.entregas)
        lucro = total - custo_total

        st.write(f"💰 Total recebido: R$ {total:.2f}")
        st.write(f"💸 Total gasto: R$ {custo_total:.2f}")
        st.write(f"🟢 Lucro: R$ {lucro:.2f}")

        # =========================
        # 🎯 META
        # =========================
        if meta > 0:
            falta = meta - lucro

            if falta > 0:
                st.warning(f"⚠️ Faltam R$ {falta:.2f} para bater sua meta!")
            else:
                st.success("🎉 Meta batida! Pode descansar 😎")

    # =========================
    # 🗑️ LIMPAR
    # =========================
    if st.button("🗑️ Limpar tudo"):
        st.session_state.entregas = []
        st.warning("Dados apagados!")

    # =========================
    # 💎 PRO
    # =========================
    st.subheader("💎 Versão PRO")

    if st.session_state.get("pro"):
        st.success("🚀 Você é PRO! Sem limites.")
    else:
        st.warning("Plano grátis: até 5 entregas por dia")

        st.markdown("### 💎 Vantagens do PRO:")
        st.write("- Entregas ilimitadas")
        st.write("- Sem bloqueio")
        st.write("- Futuras funções extras")

        if st.button("🔥 Quero ser PRO"):
            st.session_state["pro"] = True
            st.success("PRO ativado (modo teste)")
