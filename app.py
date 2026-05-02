import streamlit as st
import json
import os
import requests
import hashlib
import uuid

# ========================
# CONFIG
# ========================
MP_TOKEN = st.secrets["MP_ACCESS_TOKEN"]

st.set_page_config(page_title="Controle Financeiro PRO")

# ========================
# BANCO
# ========================
def carregar():
    if not os.path.exists("users.json"):
        return {}
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def salvar(data):
    with open("users.json", "w") as f:
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

    email = st.text_input("Email", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar / Criar conta"):
        if not email or not senha:
            st.warning("Preencha email e senha")
            st.stop()

        users = carregar()

        if email in users:
            if users[email]["senha"] == hash_senha(senha):
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Senha incorreta")
        else:
            users[email] = {
                "senha": hash_senha(senha),
                "pro": False,
                "dados": []
            }
            salvar(users)
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
            url = "https://api.mercadopago.com/v1/payments"

            headers = {
                "Authorization": f"Bearer {MP_TOKEN}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": str(uuid.uuid4())
            }

            body = {
                "transaction_amount": 9.90,
                "description": "Plano PRO",
                "payment_method_id": "pix",
                "payer": {"email": email},
                "external_reference": email
            }

            r = requests.post(url, json=body, headers=headers)
            pagamento = r.json()

            if "id" not in pagamento:
                st.error("Erro ao gerar pagamento")
                st.write(pagamento)
            else:
                st.session_state.payment_id = pagamento["id"]

                qr = pagamento["point_of_interaction"]["transaction_data"]["qr_code"]
                qr_img = pagamento["point_of_interaction"]["transaction_data"]["qr_code_base64"]

                st.image(f"data:image/png;base64,{qr_img}")
                st.code(qr)

                st.success("PIX gerado com sucesso")
                st.info("Pague e clique em verificar")

        except Exception as e:
            st.error("Erro ao conectar com pagamento")
            st.write(str(e))

    # ========================
    # VERIFICAR PAGAMENTO
    # ========================
    if st.session_state.payment_id:

        if st.button("✅ Já paguei, verificar"):

            try:
                url = f"https://api.mercadopago.com/v1/payments/{st.session_state.payment_id}"

                headers = {
                    "Authorization": f"Bearer {MP_TOKEN}"
                }

                r = requests.get(url, headers=headers)
                payment = r.json()

                status = payment.get("status")
                st.write("Status:", status)

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
