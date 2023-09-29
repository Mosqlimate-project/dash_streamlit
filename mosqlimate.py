#!/usr/bin/env python3
"""
Created on Sat Dec 18 20:40:33 2021

@author: eduardoaraujo
"""

#from PIL import Image
import streamlit as st
from vis import add_logo, plot_map, plot_heatmap_single

st.set_page_config(page_title='Data', layout="wide")

st.title('Data Exploration') 

add_logo("./figures/logo_mosqlimate.png")

#st.altair_chart(plot_heatmap(), theme=None, use_container_width=True)

html = '''
<div style="text-align: center"> <font face="sans-serif"> <h2><strong>Dengue incidence by year and quarter</strong></h2> </font> </div>
'''
st.components.v1.html(html, height = 47)                  
#st.subheader('Incidence by year and quarter')

col1, col2 = st.columns(2)

with col1:
    st.altair_chart(plot_heatmap_single('dengue'), theme=None)

with col2:
    st.plotly_chart(plot_map())
    #st.altair_chart(plot_heatmap_single('chik'), theme=None, use_container_width=True)
