import streamlit as st
import json
import os

# ------------------------
# CARREGAR USUÁRIOS
# ------------------------
def carregar_usuarios():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def salvar_usuarios(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = carregar_usuarios()

# ------------------------
# LOGIN
# ------------------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in users and users[user]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.user = user
            st.success("Login OK")
            st.rerun()
        else:
            st.error("Login inválido")

# ------------------------
# APP PRINCIPAL
# ------------------------
else:
    st.title("🚀 Lucro Delivery")

    st.success(f"Bem-vindo, {st.session_state.user}")

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # ------------------------
    # CONTROLE
    # ------------------------
    st.header("📦 Controle de Entregas")

    valor = st.number_input("Valor (R$)", min_value=0.0)
    custo = st.number_input("Custo (R$)", min_value=0.0)

    if "dados" not in st.session_state:
        st.session_state.dados = []

    if st.button("Adicionar entrega"):
        lucro = valor - custo
        st.session_state.dados.append({
            "valor": valor,
            "custo": custo,
            "lucro": lucro
        })

    # ------------------------
    # RESUMO
    # ------------------------
    if st.session_state.dados:
        total = sum(d["valor"] for d in st.session_state.dados)
        lucro_total = sum(d["lucro"] for d in st.session_state.dados)

        st.subheader("📊 Resumo")
        st.write(f"Faturamento: R$ {total:.2f}")
        st.write(f"Lucro: R$ {lucro_total:.2f}")

        st.dataframe(st.session_state.dados)

    # ------------------------
    # PRO
    # ------------------------
    st.header("💎 Versão PRO")

    if users[st.session_state.user]["pro"]:
        st.success("Você é PRO 🎉")
        st.line_chart([d["lucro"] for d in st.session_state.dados])
    else:
        st.warning("Acesso básico")

        if st.button("Pagar R$ 9,90"):
            # SIMULA PAGAMENTO
            users[st.session_state.user]["pro"] = True
            salvar_usuarios(users)
            st.success("PRO ativado!")
            st.rerun()

    # ------------------------
    # ADMIN - GERAR LOGIN
    # ------------------------
    if st.session_state.user == "admin":
        st.header("🛠 Gerar login")

        novo_user = st.text_input("Novo usuário")
        nova_senha = st.text_input("Senha do usuário")

        if st.button("Criar usuário"):
            if novo_user in users:
                st.error("Usuário já existe")
            else:
                users[novo_user] = {
                    "senha": nova_senha,
                    "pro": False
                }
                salvar_usuarios(users)
                st.success("Usuário criado!")
