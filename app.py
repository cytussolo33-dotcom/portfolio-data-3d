import streamlit as st
import json
import os
import requests
import hashlib
import uuid

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Lucro PRO", layout="centered")

MP_TOKEN = st.secrets.get("MP_ACCESS_TOKEN")

if not MP_TOKEN:
    st.error("Erro de configuração")
    st.stop()

# ========================
# STYLE
# ========================
st.markdown("""
<style>
button {
    border-radius: 12px !important;
    height: 50px;
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ========================
# BANCO
# ========================
DB_FILE = "users.json"

def carregar():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def salvar(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

# ========================
# SESSION
# ========================
if "user" not in st.session_state:
    st.session_state.user = None

if "payment_id" not in st.session_state:
    st.session_state.payment_id = None

# ========================
# LOGIN
# ========================
if not st.session_state.user:

    st.title("📱 Lucro PRO")
    st.markdown("Controle seu dinheiro de forma inteligente")

    email = st.text_input("📧 Email")
    senha = st.text_input("🔒 Senha", type="password")

    if st.button("Entrar"):
        if not email or not senha:
            st.warning("Preencha tudo")
            st.stop()

        users = carregar()
        senha_hash = hash_senha(senha)

        if email in users:
            if users[email]["senha"] == senha_hash:
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Senha incorreta")
        else:
            users[email] = {
                "senha": senha_hash,
                "pro": False,
                "dados": []
            }
            salvar(users)
            st.success("Conta criada 🚀")
            st.session_state.user = email
            st.rerun()

    st.stop()

# ========================
# APP
# ========================
email = st.session_state.user
users = carregar()
user = users[email]

st.title("💰 Seu Lucro")
st.caption(email)

# ========================
# INPUT
# ========================
col1, col2 = st.columns(2)

with col1:
    ganho = st.number_input("💰 Ganho", min_value=0.0)

with col2:
    gasto = st.number_input("💸 Gasto", min_value=0.0)

lucro = ganho - gasto

st.markdown("### Resultado")

if lucro >= 0:
    st.success(f"🟢 R$ {lucro:.2f}")
else:
    st.error(f"🔴 R$ {lucro:.2f}")

if st.button("Salvar hoje"):
    user["dados"].append(lucro)
    salvar(users)
    st.success("Salvo ✔")

# ========================
# MÉTRICAS AVANÇADAS
# ========================
if user["dados"]:
    dados = user["dados"]

    total = sum(dados)
    media = total / len(dados)
    melhor = max(dados)
    pior = min(dados)
    dias = len(dados)

    projecao = media * 30

    st.divider()
    st.markdown("## 📊 Análise avançada")

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    c1.metric("💰 Total", f"R$ {total:.2f}")
    c2.metric("📈 Média diária", f"R$ {media:.2f}")
    c3.metric("🔥 Melhor dia", f"R$ {melhor:.2f}")
    c4.metric("📉 Pior dia", f"R$ {pior:.2f}")

    st.metric("📅 Dias trabalhados", dias)
    st.metric("🚀 Projeção mensal", f"R$ {projecao:.2f}")

# ========================
# PRO
# ========================
st.divider()

if user.get("pro"):
    st.success("🚀 PRO desbloqueado")

    if user["dados"]:
        st.line_chart(user["dados"])
    else:
        st.info("Sem dados ainda")

else:
    st.warning("Versão grátis")

    st.markdown("### 🔓 Desbloquear PRO")
    st.markdown("Acesso completo por **R$9,90**")

    if st.button("Pagar com PIX 💳"):

        r = requests.post(
            "https://api.mercadopago.com/v1/payments",
            headers={
                "Authorization": f"Bearer {MP_TOKEN}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": str(uuid.uuid4())
            },
            json={
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {"email": email},
                "external_reference": email
            }
        )

        pagamento = r.json()

        if "id" in pagamento:
            st.session_state.payment_id = pagamento["id"]

            data = pagamento["point_of_interaction"]["transaction_data"]

            st.image(f"data:image/png;base64,{data['qr_code_base64']}")
            st.code(data["qr_code"])
            st.success("Pague o PIX")

    if st.session_state.payment_id:

        if st.button("Já paguei ✔"):

            r = requests.get(
                f"https://api.mercadopago.com/v1/payments/{st.session_state.payment_id}",
                headers={"Authorization": f"Bearer {MP_TOKEN}"}
            )

            status = r.json().get("status")

            if status == "approved":
                users[email]["pro"] = True
                salvar(users)

                st.success("🎉 PRO liberado!")
                st.balloons()
                st.rerun()

# ========================
# LOGOUT
# ========================
st.divider()

if st.button("Sair"):
    st.session_state.user = None
    st.session_state.payment_id = None
    st.rerun()
