import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar os dados
df = pd.read_csv('AB_NYC_2019.csv')

# Função para precificação sugerida com base na localização
def sugere_preco(bairro, tipo_quarto):
    media_preco = df[(df['neighbourhood'] == bairro) & (df['room_type'] == tipo_quarto)]['price'].mean()
    return round(media_preco, 2)

# Interface do Anfitrião
st.title("Ferramenta de Precificação para Anfitriões")
bairro = st.selectbox("Selecione o Bairro", df['neighbourhood'].unique())
tipo_quarto = st.selectbox("Selecione o Tipo de Quarto", df['room_type'].unique())

preco_sugerido = sugere_preco(bairro, tipo_quarto)
st.write(f"Preço sugerido para {tipo_quarto} em {bairro}: ${preco_sugerido}")

# Interface do Turista
st.title("Busca de Imóveis para Turistas")
preco_max = st.slider("Selecione o Preço Máximo", 0, 500, 150)
df_filtered = df[df['price'] <= preco_max]

# Criar o mapa interativo
fig = px.scatter_mapbox(df_filtered, lat="latitude", lon="longitude", hover_name="name", hover_data=["price", "neighbourhood"], color="price", zoom=10, height=600)
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig)