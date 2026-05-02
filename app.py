import streamlit as st
import json
import os
from datetime import date

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Controle PRO", layout="centered")

# =========================
# USERS
# =========================
def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

users = load_users()

# =========================
# LOGIN
# =========================
st.title("🔐 Login")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar conta"):
    if email not in users:
        users[email] = {
            "senha": senha,
            "pro": False,
            "dados": []
        }
        save_users(users)
        st.success("Conta criada!")
    else:
        if users[email]["senha"] == senha:
            st.session_state["logado"] = True
            st.session_state["email"] = email
            st.success("Login feito!")
        else:
            st.error("Senha errada")

# =========================
# APP
# =========================
if st.session_state.get("logado"):

    user = users[st.session_state["email"]]

    st.markdown("---")
    st.title("📊 Controle diário")

    ganho = st.number_input("💰 Quanto ganhou hoje?", 0.0)
    gasto = st.number_input("💸 Quanto gastou?", 0.0)

    lucro = ganho - gasto
    st.success(f"Lucro: R$ {lucro:.2f}")

    if st.button("💾 Salvar dia"):
        user["dados"].append({
            "data": str(date.today()),
            "ganho": ganho,
            "gasto": gasto,
            "lucro": lucro
        })
        save_users(users)
        st.success("Dia salvo!")

    # =========================
    # FREE
    # =========================
    if not user["pro"]:
        st.warning("Plano grátis limitado")

        st.markdown("## 🚀 Liberar PRO")
        st.write("✔ Histórico completo")
        st.write("✔ Gráficos")
        st.write("✔ Análise inteligente")

        st.link_button("💳 Assinar PRO", "SEU_LINK_MERCADOPAGO_AQUI")

    # =========================
    # PRO
    # =========================
    if user["pro"]:

        st.markdown("## 📈 Histórico")

        dados = user["dados"]

        if dados:
            import pandas as pd

            df = pd.DataFrame(dados)

            st.dataframe(df)

            st.markdown("### 📊 Gráfico de lucro")
            st.line_chart(df["lucro"])

            # IA simples
            st.markdown("### 🤖 Análise inteligente")

            media = df["lucro"].mean()

            if lucro < media:
                st.warning("Hoje foi abaixo da média. Reveja gastos.")
            else:
                st.success("Hoje foi acima da média. Continue assim!")

        else:
            st.info("Sem dados ainda.")
