import streamlit as st
import pandas as pd

st.set_page_config(page_title="Lucro Delivery", layout="wide")

# =========================
# 🔐 LOGIN SIMPLES
# =========================
USER = "admin"
PASS = "1234"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🚀 Lucro Delivery")
    st.caption("Descubra quanto você ganha de verdade")

    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == USER and password == PASS:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Login inválido")

# =========================
# 📦 SISTEMA PRINCIPAL
# =========================
else:
    st.title("📦 Controle de Entregas")

    col1, col2 = st.columns(2)

    valor = col1.number_input("💰 Valor da entrega (R$)", min_value=0.0)
    custo = col2.number_input("⛽ Custo (combustível etc)", min_value=0.0)

    if st.button("➕ Adicionar entrega"):
        lucro = valor - custo

        if "dados" not in st.session_state:
            st.session_state.dados = []

        st.session_state.dados.append({
            "Valor": valor,
            "Custo": custo,
            "Lucro": lucro
        })

    # =========================
    # 📊 DADOS
    # =========================
    if "dados" in st.session_state and len(st.session_state.dados) > 0:
        df = pd.DataFrame(st.session_state.dados)

        st.subheader("📊 Resumo Geral")

        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Entregas", len(df))
        c2.metric("💰 Faturamento", f"R$ {df['Valor'].sum():.2f}")
        c3.metric("🟢 Lucro Total", f"R$ {df['Lucro'].sum():.2f}")

        st.dataframe(df, use_container_width=True)

        st.subheader("📈 Evolução do Lucro")
        st.line_chart(df["Lucro"])

    else:
        st.info("Adicione entregas para ver os resultados")

    # =========================
    # 📤 EXPORTAR (PRO)
    # =========================
    if "dados" in st.session_state:
        df = pd.DataFrame(st.session_state.dados)
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Baixar relatório CSV",
            csv,
            "relatorio.csv",
            "text/csv"
        )

    # =========================
    # 🔓 SAIR
    # =========================
    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()
