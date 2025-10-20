import streamlit as st
import pandas as pd
import io

# Configuração para modo wide
st.set_page_config(page_title="Impostos", page_icon="📊", layout="wide")

# Exibir imagem no topo
st.image('teste.svg', width=400)

# Ler CSV
dados = pd.read_csv("impostos.csv")

st.title("Impostos Cadastrados")
st.divider()

# Criar filtros lado a lado
col1, col2 = st.columns(2)

# Filtro por código_conta
codigo_opcoes = sorted(dados['codigo_conta'].dropna().unique())
codigo_filtro = col1.selectbox("Filtrar por Código/Conta", ["Todos"] + list(codigo_opcoes))

# Filtro por competência
competencia_opcoes = sorted(dados['competencia'].dropna().unique())
competencia_filtro = col2.selectbox("Filtrar por Competência", ["Todos"] + list(competencia_opcoes))

# Aplicar filtros
dados_filtrados = dados.copy()
if codigo_filtro != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['codigo_conta'] == codigo_filtro]
if competencia_filtro != "Todos":
    dados_filtrados = dados_filtrados[dados_filtrados['competencia'] == competencia_filtro]

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