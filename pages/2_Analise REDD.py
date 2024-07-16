import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.express as px
from fiona.crs import from_epsg

crs_original = 'EPSG:4674'  # SIRGAS 2000

# Definir o sistema de coordenadas desejado para cálculos em metros
crs_meter = from_epsg(32722)  # SIRGAS 2000 UTM Zone 22S - Pará

# Funções de recorte e cálculo
def calcular_apd(limite, reserva_legal, vegetacao_nativa):
    recorte_vegetacao = gpd.overlay(vegetacao_nativa, limite, how='intersection')
    apd = gpd.overlay(recorte_vegetacao, reserva_legal, how='difference')
    return apd.to_crs(crs_meter)

def calcular_aud(limite, reserva_legal, vegetacao_nativa):
    recorte_vegetacao = gpd.overlay(vegetacao_nativa, limite, how='intersection')
    aud = gpd.overlay(limite, reserva_legal, how='intersection')
    aud = gpd.overlay(aud, recorte_vegetacao, how='intersection')
    return aud.to_crs(crs_meter)

# Interface do Streamlit
st.set_page_config(
    page_title="Análise REDD",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.container():
    # Carregar os dados geoespaciais
    limite_imovel_original = gpd.read_file('streamlit/fontes/areaImovel_amostra.geojson', crs=crs_original)
    reserva_legal_original = gpd.read_file('streamlit/fontes/reservaLegal_amostra.geojson', crs=crs_original)
    vegetacao_nativa_original = gpd.read_file('streamlit/fontes/vegetacaoNativa_amostra.geojson', crs=crs_original)

    # Seleção do código do imóvel
    codigo = st.selectbox('Selecione o código do imóvel', limite_imovel_original['cod_imovel'].unique())

    # Filtrar o limite do imóvel selecionado (sistema de coordenadas original)
    limite_selecionado_original = limite_imovel_original[limite_imovel_original['cod_imovel'] == codigo]

    # Filtrar a reserva legal correspondente (sistema de coordenadas original)
    reserva_selecionada_original = reserva_legal_original[reserva_legal_original['cod_imovel'] == codigo]

    # Filtrar a vegetação nativa correspondente (sistema de coordenadas original)
    vegetacao_selecionada_original = vegetacao_nativa_original[vegetacao_nativa_original['cod_imovel'] == codigo]

    # Calcular APD e AUD no sistema de coordenadas original
    apd_original = calcular_apd(limite_selecionado_original, reserva_selecionada_original, vegetacao_selecionada_original)
    aud_original = calcular_aud(limite_selecionado_original, reserva_selecionada_original, vegetacao_selecionada_original)

    # Criar mapa Folium com dados no sistema de coordenadas original
    m = folium.Map(location=[limite_selecionado_original.geometry.centroid.y.values[0], limite_selecionado_original.geometry.centroid.x.values[0]], zoom_start=12)

    # Adicionar camadas ao mapa com estilo personalizado
    folium.GeoJson(limite_selecionado_original, name='Limite do Imóvel',
                   style_function=lambda x: {'color': 'black', 'fillOpacity': 0, 'weight': 2}).add_to(m)
    folium.GeoJson(reserva_selecionada_original, name='Reserva Legal',
                   style_function=lambda x: {'color': '#FFA500', 'fillColor': '#FFA500', 'fillOpacity': 0.5}).add_to(m)
    folium.GeoJson(vegetacao_selecionada_original, name='Vegetação Nativa',
                   style_function=lambda x: {'color': 'green', 'fillColor': 'green', 'fillOpacity': 0.5},overlay=False).add_to(m)
    folium.GeoJson(apd_original, name='APD',
                   style_function=lambda x: {'color': '#FF69B4', 'fillOpacity': 0.5}).add_to(m)
    folium.GeoJson(aud_original, name='AUD',
                   style_function=lambda x: {'color': '#800080', 'fillOpacity': 0.5}).add_to(m)

    # Adicionar controle de camadas
    folium.LayerControl().add_to(m)

    # Calcular áreas no sistema de coordenadas SIRGAS 2000 UTM Zone 22S
    limite_selecionado_sirgas = limite_selecionado_original.to_crs(crs_meter)
    reserva_selecionada_sirgas = reserva_selecionada_original.to_crs(crs_meter)
    vegetacao_selecionada_sirgas = vegetacao_selecionada_original.to_crs(crs_meter)
    apd_sirgas = apd_original.to_crs(crs_meter)
    aud_sirgas = aud_original.to_crs(crs_meter)

    total_area_sirgas = limite_selecionado_sirgas.geometry.area.sum() / 10**6
    apd_area_sirgas = apd_sirgas.geometry.area.sum() / 10**6
    aud_area_sirgas = aud_sirgas.geometry.area.sum() / 10**6

    # Criar gráfico de pizza interativo
    fig = px.pie(values=[apd_area_sirgas, aud_area_sirgas, total_area_sirgas - apd_area_sirgas - aud_area_sirgas],
                names=['APD', 'AUD', 'Inviabilidade para REDD'],
                title='Áreas potenciais para REDD+')

    # Layout do Streamlit
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader('Mapa')
        st_folium(m, width=800, height=600)


    with col2:
        st.plotly_chart(fig)

        # Mostrar total das áreas abaixo do gráfico
        st.subheader('Total de áreas APD e AUD (km²)')
        st.write(f"APD: {apd_area_sirgas:.2f} km²")
        st.write(f"AUD: {aud_area_sirgas:.2f} km²")
