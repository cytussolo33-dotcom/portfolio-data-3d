import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Lucro Delivery PRO", layout="centered")

# ================= LOGIN =================
usuarios = {
    "admin": "1234",
    "cytus": "1234"
}

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Lucro Delivery PRO")

    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in usuarios and usuarios[user] == password:
            st.session_state.logado = True
            st.session_state.usuario = user
            st.rerun()
        else:
            st.error("Login inválido")

    st.stop()

# ================= APP =================

st.title("🚀 Controle de Entregas PRO")

arquivo = f"dados_{st.session_state.usuario}.csv"

# Criar arquivo se não existir
if not os.path.exists(arquivo):
    df = pd.DataFrame(columns=["data", "valor", "custo", "lucro"])
    df.to_csv(arquivo, index=False)

df = pd.read_csv(arquivo)

# INPUTS
valor = st.number_input("💰 Valor da entrega", min_value=0.0)
custo = st.number_input("⛽ Custo", min_value=0.0)

if st.button("➕ Adicionar entrega"):
    lucro = valor - custo
    nova = pd.DataFrame([{
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "valor": valor,
        "custo": custo,
        "lucro": lucro
    }])
    df = pd.concat([df, nova], ignore_index=True)
    df.to_csv(arquivo, index=False)
    st.success("Entrega salva!")
    st.rerun()

# ================= MÉTRICAS =================

st.subheader("📊 Resumo")

st.metric("📦 Entregas", len(df))
st.metric("💰 Faturamento", f"R$ {df['valor'].sum():.2f}")
st.metric("🟢 Lucro", f"R$ {df['lucro'].sum():.2f}")

# ================= HISTÓRICO =================

st.subheader("📋 Histórico")
st.dataframe(df)

# ================= GRÁFICO =================

st.subheader("📈 Evolução do Lucro")

if not df.empty:
    df["acumulado"] = df["lucro"].cumsum()
    st.line_chart(df["acumulado"])

# ================= SAIR =================

if st.button("🚪 Sair"):
    st.session_state.logado = False
    st.rerun()
