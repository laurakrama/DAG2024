import geopandas as gpd
import folium
import streamlit as st
from datetime import datetime, date
import pandas as pd

# Carregar os dados de desmatamento
desmatamento_path = '.streamlit/fontes/desmatamento_Ruropolis.geojson'
desmatamento_gdf = gpd.read_file(desmatamento_path)
municipio = gpd.read_file('.streamlit/fontes/municipio_Ruropolis.geojson')
car = gpd.read_file('.streamlit/fontes/areaImovel_amostra.geojson')

# Converter a coluna de data para o tipo datetime
desmatamento_gdf['image_date'] = pd.to_datetime(
    desmatamento_gdf['image_date'], format='mixed')

# Definir as categorias específicas e agrupar as demais como 'sem categoria'
categorias_especificas = ['desmatamento por degradação progressiva',
                          'corte raso com vegetação', 'corte raso com solo exposto']
desmatamento_gdf.loc[~desmatamento_gdf['sub_class'].isin(
    categorias_especificas), 'sub_class'] = 'sem categoria'

# Função para filtrar dados


def filtrar_dados(data_inicio, data_fim, tamanho_min, tamanho_max, tipos):
    # Convertemos as datas de entrada para datetime para a comparação correta
    if isinstance(data_inicio, date):
        data_inicio = datetime.combine(data_inicio, datetime.min.time())
    if isinstance(data_fim, date):
        data_fim = datetime.combine(data_fim, datetime.max.time())

    mask = (
        (desmatamento_gdf['image_date'] >= data_inicio) &
        (desmatamento_gdf['image_date'] <= data_fim) &
        (desmatamento_gdf['area_km'] >= tamanho_min) &
        (desmatamento_gdf['area_km'] <= tamanho_max) &
        (desmatamento_gdf['sub_class'].isin(tipos))
    )
    return desmatamento_gdf[mask]


# Interface do Streamlit
st.set_page_config(
    page_title="Análise Desmatamento",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Layout do Streamlit
st.title('Desmatamento em Rurópolis-PA')

# Filtros
st.sidebar.header('Filtros')

# Valor total desmatado
total_desmatado = desmatamento_gdf['area_km'].sum()
st.sidebar.metric('Valor Total Desmatado (km²)', total_desmatado)

# Obter data mínima e máxima da coluna image_date
data_minima = desmatamento_gdf['image_date'].min().date()
data_maxima = desmatamento_gdf['image_date'].max().date()

# Filtro de Data
data_inicio = st.sidebar.date_input('Data de Início', data_minima)
data_fim = st.sidebar.date_input('Data de Fim', data_maxima)

# Obter área mínima e máxima da coluna area_km
area_minima = desmatamento_gdf['area_km'].min()
area_maxima = desmatamento_gdf['area_km'].max()

# Filtro de Tamanho
tamanho_min, tamanho_max = st.sidebar.slider(
    'Tamanho (km²)', area_minima, area_maxima, (area_minima, area_maxima))

# Categorias de Desmatamento
categorias_filtros = categorias_especificas + ['sem categoria']

# Filtro de Tipo de Desmatamento
tipos_desmatamento = desmatamento_gdf['sub_class'].unique().tolist()
tipos_selecionados = st.sidebar.multiselect(
    'Tipo de Desmatamento', categorias_filtros, default=categorias_filtros)

# Aplicar filtros
dados_filtrados = filtrar_dados(
    data_inicio, data_fim, tamanho_min, tamanho_max, tipos_selecionados)

# Converter colunas Timestamp para str antes de passar para o GeoJson
dados_filtrados['image_date'] = dados_filtrados['image_date'].dt.strftime(
    '%Y-%m-%d')

# Seleção do código do imóvel
codigo = st.selectbox('Selecione o código do imóvel',
                      car['cod_imovel'].unique(), index=None)
car_selecionado = car[car['cod_imovel'] == codigo]


# Criação do mapa
mapa = folium.Map(location=[-4.099316770129531, -
                  54.911051766333834], zoom_start=9)

# Adicionar hotspots ao mapa
folium.GeoJson(
    dados_filtrados,
    style_function=lambda feature: {
        'fillColor': 'red',
        'color': 'red',
        'weight': 1,
        'fillOpacity': 0.7
    }
).add_to(mapa)

folium.GeoJson(municipio, name='Rurópolis',
               style_function=lambda x: {'color': 'black', 'fillOpacity': 0, 'weight': 2}).add_to(mapa)

folium.GeoJson(car_selecionado, name='CAR Selecionado',
               style_function=lambda x: {'color': 'purple', 'fillOpacity': 0, 'weight': 2}).add_to(mapa)

# Adicionar controle de camadas
folium.LayerControl().add_to(mapa)

# Salvar o mapa como HTML
mapa.save('mapa_hotspots.html')

# Exibir o mapa no Streamlit
st.components.v1.html(open('mapa_hotspots.html', 'r').read(), height=600)
