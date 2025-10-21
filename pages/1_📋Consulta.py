from supabase import create_client, Client
import streamlit as st
import pandas as pd
import io

# 🔐 Credenciais do Supabase via Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração para modo wide
st.set_page_config(page_title="Consulta de Impostos", page_icon="📊", layout="wide")

# Exibir imagem no topo
st.image('teste.svg', width=400)

# Buscar dados do Supabase
response = supabase.table("tabela").select("*").execute()
dados = pd.DataFrame(response.data)

st.title("Impostos Cadastrados")
st.divider()

if dados.empty:
    st.warning("Nenhum registro encontrado no banco de dados.")
else:
    # Criar filtros lado a lado
    col1, col2 = st.columns(2)

    # Filtro por código_conta
    codigo_opcoes = sorted(dados['codigo_conta'].dropna().unique())
    codigo_filtro = col1.selectbox("Filtrar por Código/Conta", ["Todos"] + list(codigo_opcoes))

    # Filtro por nome_imposto
    imposto_opcoes = sorted(dados['nome_imposto'].dropna().unique())
    imposto_filtro = col2.selectbox("Filtrar por Nome do Imposto", ["Todos"] + list(imposto_opcoes))

    # Aplicar filtros
    dados_filtrados = dados.copy()
    if codigo_filtro != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['codigo_conta'] == codigo_filtro]
    if imposto_filtro != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['nome_imposto'] == imposto_filtro]

    # Exibir tabela com largura total e altura maior
    st.dataframe(dados_filtrados, use_container_width=True, height=600)

    # Botão para download do Excel filtrado
    buffer = io.BytesIO()
    dados_filtrados.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📩 Baixar Excel Filtrado",
        data=buffer,
        file_name="impostos_filtrados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
