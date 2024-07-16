#import altair as alt
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import geopandas as gpd
from folium import plugins
# from streamlit_folium import folium_static

# Interface do Streamlit
st.set_page_config(
    page_title="REDD APD/AUD",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# with open('assets/style.css') as f:
# css = f.read()
# st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

with st.container():
    st.subheader(
        "Verifique qual a área de APD e AUD de sua propriedade com base na área de Reserva Legal e outras informações do seu CAR")
    st.title("Primeiros passos para o REDD+: APD e AUD")
    st.write(
        "")
    st.write("#### O que são APD e AUD?")
    st.write("Os créditos de carbono REDD+ (Reducing Emissions from Deforestation and Forest Degradation) são ativos no mercado volunetário de carbono bastante consolidado e seu valor está baseado na equivalência de uma tonelada de CO2 não emitida para a atmosfera a partir da conservação por um período de 40 anos de uma floresta nativa já existente. Nessa modalidade de projeto, seu esforço é focado em manter as florestas nativas e conter o desmatamento."
             )
    st.write("Sob o contexto de REDD+, existem dois tipos de desmatamento evitado. O primeiro é o 'desmatamento planejado evitado', conhecido pela sigla APD (Avoided Planned Deforestation), aplicado em áreas que poderiam ter sido desmatadas legalmente, mas onde se optou por não realizar o desmatamento. Um exemplo seria um proprietário de imóvel rural no Brasil (produtor ou empresa) que possui excedente de vegetação nativa e decide mantê-la. O segundo é o AUD (Avoided Unplanned Deforestation), esses projetos protegem principalmente áreas que poderiam sofrer desmatamento ilegal, como Unidades de Conservação, Reservas Legais ou outras áreas onde a supressão da vegetação não é permitida."
             )
    st.image('streamlit\\fontes\\redd.jpg', caption='exemplo')
