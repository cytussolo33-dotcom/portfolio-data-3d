import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Lucro Delivery PRO", layout="centered")

# ===== LOGIN SIMPLES =====
USER = "admin"
PASS = "1234"

if "logado" not in st.session_state:
    st.session_state.logado = False

def login():
    st.title("🔐 Login - Lucro Delivery")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == USER and password == PASS:
            st.session_state.logado = True
        else:
            st.error("Login inválido")

if not st.session_state.logado:
    login()
    st.stop()

# ===== TÍTULO =====
st.title("🚀 Controle de Entregas PRO")

# ===== DADOS =====
file = "dados.csv"

if os.path.exists(file):
    df = pd.read_csv(file)
else:
    df = pd.DataFrame(columns=["data", "valor", "custo", "lucro"])

# ===== INPUT =====
st.subheader("📦 Nova entrega")

valor = st.number_input("💰 Valor da entrega", min_value=0.0, format="%.2f")
custo = st.number_input("⛽ Custo", min_value=0.0, format="%.2f")

if st.button("➕ Adicionar entrega"):
    lucro = valor - custo
    nova_linha = pd.DataFrame([{
        "data": datetime.now().strftime("%d/%m %H:%M"),
        "valor": valor,
        "custo": custo,
        "lucro": lucro
    }])

    df = pd.concat([df, nova_linha], ignore_index=True)
    df.to_csv(file, index=False)

    st.success("Entrega adicionada!")

# ===== RESUMO =====
st.subheader("📊 Resumo")

total_entregas = len(df)
faturamento = df["valor"].sum()
lucro_total = df["lucro"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📦 Entregas", total_entregas)
col2.metric("💰 Faturamento", f"R$ {faturamento:.2f}")
col3.metric("🟢 Lucro", f"R$ {lucro_total:.2f}")

# ===== HISTÓRICO =====
st.subheader("📜 Histórico")
st.dataframe(df)

# ===== GRÁFICO =====
st.subheader("📈 Evolução do lucro")

if not df.empty:
    st.line_chart(df["lucro"])

# ===== PLANO PRO =====
st.subheader("💎 Versão PRO")

st.info("""
🔥 Vantagens:
- Salvar histórico
- Ver gráficos
- Controle completo
- Futuras automações
""")

# ===== PAGAMENTO (SIMULADO) =====
st.markdown("### 💳 Desbloquear PRO")

if st.button("💰 Pagar R$ 9,90 (Simulação)"):
    st.success("Pagamento aprovado! (simulado)")
    st.balloons()

st.caption("💡 Para ganhar dinheiro de verdade, conecte com Stripe ou Mercado Pago")

# ===== LOGOUT =====
if st.button("🚪 Sair"):
    st.session_state.logado = False
