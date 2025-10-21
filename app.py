from supabase import create_client, Client
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import re
import io

# 🔐 Credenciais do Supabase via Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração da página
st.set_page_config(page_title="Cadastro de Impostos", page_icon="🛠️", layout="centered")

# Usuários e senhas
USERS = {
    "admin": "senha_admin123",
    "financeiro": "senha_financeiro456"
}

# Estado de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usuario = None

# Oculta sidebar se não logado
if not st.session_state.logged_in:
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

# Tela de login
if not st.session_state.logged_in:
    st.title("Acesso Restrito")
    usuario = st.text_input("Usuário:")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if usuario in USERS and senha == USERS[usuario]:
            st.session_state.logged_in = True
            st.session_state.usuario = usuario
            st.success(f"Acesso liberado para {usuario}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# Conteúdo protegido
if st.session_state.logged_in:
    st.markdown(f"🔐 Logado como **{st.session_state.usuario}**")

    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.session_state.usuario = None
        st.rerun()

    # Funções Supabase
    def load_data():
        response = supabase.table("tabela").select("*").execute()
        return pd.DataFrame(response.data)

    def insert_row(row):
        return supabase.table("tabela").insert(row).execute()

    def update_data(df):
        for row in df.to_dict(orient="records"):
            supabase.table("tabela").upsert(row).execute()

    data = load_data()

    # Dados fixos
    codigo_conta = {
        "1 - 2300390": "2300390", "2 - 2300391": "2300391", "3 - 2300393": "2300393",
        "4 - 2300394": "2300394", "5 - 2300395": "2300395", "6 - 2300396": "2300396",
        "7 - 2300397": "2300397", "8 - 2360020": "2360020", "9 - 2360022": "2360022",
        "10 - 2360023": "2360023", "11 - 2360024": "2360024", "12 - 2360028": "2360028",
        "13 - 1280349": "1280349", "14 - 6102005": "6102005", "15 - 6114000": "6114000"
    }

    nomes_impostos = [
        "IPI a recolher", "ISS retido", "GNRE ANTECIPADO", "Taxas", "Parcelamento CP",
        "ICMS a recolher", "ICMS ST", "Outros impostos", "Cofins a recolher", "PIS a recolher",
        "ISS prestado", "ICMS PROPRIO", "ICMS FECAP PROPRIO", "ICMS ST INTERNO", "ICMS FECAP ST",
        "ICMS ST", "ICMS ANTECIPADO", "GUIA PARCELAMENTO", "TAXA VIGILANCIA", "ISS RETIDO",
        "TAXA FISCALIZAÇÃO", "ICMS FECAP", "GARE ICMS", "GARE ICMS ST INTERNO", "TAXA",
        "GUIA MIT", "ICMS", "ICMS FECP Antecipado", "ICMS DIFAL", "FECAP PROPRIO", "FECAP ST",
        "PARCELAMENTO"
    ]

    menu = st.sidebar.selectbox("Menu", ["Cadastrar Imposto", "Registros Cadastrados"])

    def validar_numero(valor):
        return bool(re.match(r'^\d+(,\d{1,2})?$', valor))

    def to_float(val):
        return float(val.replace(",", ".")) if validar_numero(val) else None

    # Cadastro
    if menu == "Cadastrar Imposto":
        st.title("Cadastro de Imposto")
        codigo_conta_sel = st.selectbox("Código do Imposto / Conta", [""] + list(codigo_conta.keys()))
        nome_imposto = st.selectbox("Nome do Imposto", [""] + nomes_impostos)
        valor = st.text_input("Valor", "")

        if st.button("Salvar"):
            valor_convertido = to_float(valor)
            if not codigo_conta_sel or not nome_imposto or valor_convertido is None:
                st.error("Preencha todos os campos obrigatórios com valores válidos.")
            else:
                hora_brasilia = datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")
                new_row = {
                    "codigo_conta": codigo_conta_sel,
                    "nome_imposto": nome_imposto,
                    "valor": int(valor_convertido),  # ✅ Garantindo int
                    "ultima_edicao_por": st.session_state.usuario,
                    "ultima_edicao_em": hora_brasilia
                }
                try:
                    insert_row(new_row)
                    st.success("Registro salvo com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")

    # Registros
    elif menu == "Registros Cadastrados":
        st.title("Registros Cadastrados")
        filtro_conta = st.selectbox("Filtrar por Código/Conta", ["Todos"] + list(codigo_conta.keys()))

        df_filtrado = data.copy()
        if filtro_conta != "Todos":
            df_filtrado = df_filtrado[df_filtrado["codigo_conta"] == filtro_conta]

        colunas_visiveis = ["codigo_conta", "nome_imposto", "valor"]
        edited_data = st.experimental_data_editor(df_filtrado[colunas_visiveis], use_container_width=True, num_rows="dynamic")

        if st.button("Salvar Alterações"):
            hora_brasilia = datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")
            edited_data["ultima_edicao_por"] = st.session_state.usuario
            edited_data["ultima_edicao_em"] = hora_brasilia
            update_data(edited_data)
            st.success("Alterações salvas com sucesso!")

        output = io.BytesIO()
        edited_data.to_excel(output, index=False)
        st.download_button(
            label="📥 Baixar Excel",
            data=output.getvalue(),
            file_name="impostos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
