#!/usr/bin/env python3
"""
Created on Sat Dec 18 20:40:33 2021

@author: eduardoaraujo
"""
import sys
import numpy as np 
import pandas as pd 
import streamlit as st
import plotly.graph_objects as go
import sys
sys.path.append('../')
from preprocess import get_forecast_to_plot
from vis import add_logo, plot_time_series_by_week, plot_for_altair, plot_error_bar


states = {'RJ': 'Rio de Janeiro', 'ES': 'Espírito Santo', 'PR': 'Paraná', 'CE': 'Ceará',
               'MA': 'Maranhão', 'MG': 'Minas Gerais', 'SC': 'Santa Catarina', 'PE': 'Pernambuco', 
               'PB': 'Paraíba', 'RN': 'Rio Grande do Norte', 'PI': 'Piauí', 'AL': 'Alagoas',
               'SE': 'Sergipe', 'SP': 'São Paulo', 'RS': 'Rio Grande do Sul','PA': 'Pará',
               'AP': 'Amapá', 'RR': 'Roraima', 'RO': 'Rondônia', 'AM': 'Amazonas', 'AC': 'Acre',
               'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'GO': 'Goiás', 'TO': 'Tocantins',
               'DF': 'Distrito Federal', 'BA': 'Bahia'
               }

cities_to_geo = {   'Maceió': 2704302, # Maceio
                    'Salvador': 2927408, # Salvador
                    'Fortaleza': 2304400, # Fortaleza
                    'São Luís': 2111300, # são luis
                    'João Pessoa': 2507507, # João Pessoa
                    'Recife': 2611606,  # Recife
                    'Teresina': 2211001, # Teresina 
                    'Aracaju':2800308, # Aracaju 
                    'Natal': 2408102 # Natal
                     }

state_to_cities = {    
    'RJ': [None],
    'ES': [None], 
    'PR': [None],
    'CE': ['Fortaleza'],
    'MA': ['São Luís'], 
    'MG': [None], 
    'SC': [None], 
    'PE': ['Recife'],    
    'PB': ['João Pessoa'], 
    'RN': ['Natal'], 
    'PI': ['Teresina'], 
    'AL': ['Maceió'],
    'SE': ['Sergipe'],
    'SP': [None], 
    'RS': [None],
    'PA': [None],
    'AP': [None], 
    'RR': [None],
    'RO': [None], 
    'AM': [None], 
    'AC': [None],
    'MT': [None], 
    'MS': [None], 
    'GO': [None],
    'TO': [None],
    'DF': [None], 
    'BA': ['Salvador']
    
}



st.set_page_config(page_title='Forecast Models', 
                    page_icon=":chart:", 
                    layout="wide"
                    #menu_items={'Get help': "",
                    #            'Report a bug': "",
     #}
)

st.title('Comparing forecast models')

add_logo("./figures/logo_mosqlimate.png")

option_state = st.sidebar.selectbox(
    "Select the state:",
    states.keys(),
    index = 3
)


geocodes_state = {'CE': [2302503, 2313401, 2313302, 2307601, 2311405, 2307650, 2305407,
       2302602, 2312908, 2304400] }

option_city = st.sidebar.selectbox(
   'Select a city:',
    state_to_cities[option_state])


st.subheader(f'{option_state} - {option_city}')

if option_city != None:
    st.write('''
             The plot below shows the number of new cases by epidemiological week over the years in this city.
             ''')
    
    fig = plot_time_series_by_week(cities_to_geo[option_city])

    st.plotly_chart(fig)

    st.subheader(f'Forecast of dengue new cases')

    df, df_for = get_forecast_to_plot(cities_to_geo[option_city])

    st.altair_chart(plot_for_altair(df, df_for), theme = None)

    st.markdown('Select a error metric below:' )
    
    st.altair_chart(plot_error_bar(df, df_for), theme = None)

    st.markdown("""
                In the selection field above: 
                - MAE: Mean Absolute Error;
                - MSE: Mean Squared Error;
                - RMSE: Root Mean Squared Error;
                - MSLE: Mean Squared Logarithmic Error. 
                """)
    
    st.markdown("Select the model in the select box below to see details of the model.")

    col1, col2 = st.columns(2)

    with col1:

        info_model = st.selectbox(
        "More info about a model?",
        ("NN and NN cluster", "RF and RF cluster"))

    if info_model == "NN and NN cluster":

        st.subheader(f"Info about the {info_model} model:")

        st.markdown(
        """
        
        It's a deep learning model with three lstm layers (the first is bidirectional) interspersed with dropout layers and a dense layer in the output. 
        This model computes the number of new cases in the next four weeks based on the last four weeks of data (cases and climate variables).
        The confidence interval of the predictions is computed using dropout and making multiple predictions to compute the ci of them.

        The diference 
        between the NN cluster and NN is that the NN cluster use as input also de data of other cities determined by a hierarquical clusterization
        of the time series of dengue cases of the cities in the state.

        """
        ) 


    if info_model == "RF and RF cluster":

        st.subheader(f"Info about the {info_model} model:")

        st.markdown(
        """
        
        It's implemented a random forest regressor model that based on the last four weeks of data (cases and climate variables) computes the cases in the fourth week ahead.
        For this reason in this model the predictions for multiple times are obtained in a rolling window fashion, i.e., the historical data window is moved forward one week at a time, predicting the next fourth week at each step. 
        The confidence interval of the predictions are computed using the conformal prediction.
        
        The diference between the RF cluster and RF is that the RF cluster use as input also de data of other cities determined by a hierarquical clusterization
        of the time series of dengue cases of the cities in the state.

        """
        ) 

    





