import streamlit as st
import json
import os
import requests
import hashlib
import uuid

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Controle Financeiro PRO", layout="centered")

MP_TOKEN = st.secrets.get("MP_ACCESS_TOKEN")

if not MP_TOKEN:
    st.error("Token do Mercado Pago não configurado")
    st.stop()

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

    st.title("🔐 Login")

    email = st.text_input("Email", key="email")
    senha = st.text_input("Senha", type="password", key="senha")

    if st.button("Entrar / Criar conta"):
        if not email or not senha:
            st.warning("Preencha todos os campos")
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
            st.success("Conta criada!")
            st.session_state.user = email
            st.rerun()

    st.stop()

# ========================
# APP
# ========================
email = st.session_state.user
users = carregar()

if email not in users:
    st.session_state.user = None
    st.rerun()

user = users[email]

st.title("💰 Controle Financeiro")
st.write(f"👤 {email}")

# ========================
# CONTROLE
# ========================
st.subheader("📊 Seu dia")

ganho = st.number_input("💰 Ganho", min_value=0.0)
gasto = st.number_input("💸 Gasto", min_value=0.0)

lucro = ganho - gasto

if lucro >= 0:
    st.success(f"Lucro: R$ {lucro:.2f}")
else:
    st.error(f"Prejuízo: R$ {lucro:.2f}")

if st.button("💾 Salvar dia"):
    user["dados"].append(lucro)
    users[email] = user
    salvar(users)
    st.success("Dia salvo!")

# ========================
# PRO
# ========================
st.markdown("---")

if user.get("pro"):
    st.success("🚀 PRO ativo")

    if user["dados"]:
        st.line_chart(user["dados"])
    else:
        st.info("Sem histórico ainda")

else:
    st.warning("Plano grátis")

    st.markdown("## 🚀 Liberar PRO")
    st.markdown("💎 Acesso completo por apenas **R$9,90**")

    # ========================
    # GERAR PIX
    # ========================
    if st.button("💳 Gerar PIX"):

        try:
            response = requests.post(
                "https://api.mercadopago.com/v1/payments",
                headers={
                    "Authorization": f"Bearer {MP_TOKEN}",
                    "Content-Type": "application/json",
                    "X-Idempotency-Key": f"{email}-{uuid.uuid4()}"
                },
                json={
                    "transaction_amount": 9.90,
                    "description": "Plano PRO",
                    "payment_method_id": "pix",
                    "payer": {"email": email},
                    "external_reference": email
                },
                timeout=15
            )

            pagamento = response.json()

            if "id" not in pagamento:
                st.error("Erro ao gerar pagamento")
                st.write(pagamento)
            else:
                st.session_state.payment_id = pagamento["id"]

                data = pagamento["point_of_interaction"]["transaction_data"]

                st.image(f"data:image/png;base64,{data['qr_code_base64']}")
                st.code(data["qr_code"])

                st.success("PIX gerado!")
                st.info("Após pagar, clique em verificar")

        except Exception as e:
            st.error("Erro ao gerar PIX")
            st.write(str(e))

    # ========================
    # VERIFICAR PAGAMENTO
    # ========================
    if st.session_state.payment_id:

        if st.button("✅ Já paguei, verificar"):

            try:
                response = requests.get(
                    f"https://api.mercadopago.com/v1/payments/{st.session_state.payment_id}",
                    headers={"Authorization": f"Bearer {MP_TOKEN}"},
                    timeout=10
                )

                payment = response.json()
                status = payment.get("status")

                if status == "approved":
                    users[email]["pro"] = True
                    salvar(users)

                    st.success("🚀 PRO ativado!")
                    st.balloons()
                    st.rerun()

                elif status == "pending":
                    st.warning("Pagamento ainda pendente")

                else:
                    st.error("Pagamento não aprovado")

            except Exception as e:
                st.error("Erro ao verificar pagamento")
                st.write(str(e))

# ========================
# LOGOUT
# ========================
st.markdown("---")

if st.button("Sair"):
    st.session_state.user = None
    st.session_state.payment_id = None
    st.rerun()
