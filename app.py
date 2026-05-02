import streamlit as st
import json
import os

# ========================
# BANCO DE DADOS
# ========================

def carregar():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)

# ========================
# SESSÃO
# ========================

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.email = None

# ========================
# LOGIN
# ========================

st.title("🔐 Login")

email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar / Criar conta"):
    users = carregar()

    if email in users:
        if users[email]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.email = email
            st.success("Login feito!")
        else:
            st.error("Senha errada")
    else:
        users[email] = {
            "senha": senha,
            "pro": False,
            "dados": []
        }
        salvar(users)
        st.session_state.logado = True
        st.session_state.email = email
        st.success("Conta criada!")

# ========================
# APP PRINCIPAL
# ========================

if st.session_state.logado:

    users = carregar()
    user = users[st.session_state.email]

    st.write(f"👤 Usuário: {st.session_state.email}")

    st.title("📊 Controle diário")

    ganho = st.number_input("Quanto ganhou hoje?", 0.0)
    gasto = st.number_input("Quanto gastou?", 0.0)

    lucro = ganho - gasto

    st.success(f"Lucro: R$ {lucro:.2f}")

    if st.button("Salvar dia"):
        user["dados"].append(lucro)
        salvar(users)
        st.success("Dia salvo!")

    # ========================
    # PRO
    # ========================

    if user["pro"]:
        st.success("🚀 Você é PRO!")

        st.subheader("📈 Histórico")
        st.line_chart(user["dados"])

    else:
        st.warning("Plano grátis")

        st.subheader("🚀 Liberar PRO")

        st.write("✔ Histórico completo")
        st.write("✔ Gráficos")
        st.write("✔ Uso ilimitado")

        # SIMULAÇÃO DE PAGAMENTO
        if st.button("💳 Ativar PRO (teste)"):
            user["pro"] = True
            salvar(users)
            st.success("PRO ativado! Recarregue a página 🔄")
