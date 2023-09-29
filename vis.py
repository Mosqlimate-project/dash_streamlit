import io
import json
import base64
import numpy as np
import pandas as pd
import altair as alt
from PIL import Image
import streamlit as st
import geopandas as gpd
from epiweeks import Week 
import plotly.express as px
#from dotenv import load_dotenv
import plotly.graph_objects as go
from preprocess import get_dengue_data
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_squared_log_error as msle

#load_dotenv()

PATH_TO_CASES  = '/Users/eduardoaraujo/Documents/Github/paper-dengue-sc/data/cases'


def add_logo(filename):
    '''
    This function was created to add the logo figure in the sidebar of the streamlit pages.

    Parameters
    ----------
    filename: str
        The path where the figure is saved. 
    '''

    file = open(filename, "rb")

    contents = file.read()
    img_str = base64.b64encode(contents).decode("utf-8")
    buffer = io.BytesIO()
    file.close()
    img_data = base64.b64decode(img_str)
    img = Image.open(io.BytesIO(img_data))
    resized_img = img.resize((200, 200))  # x, y
    resized_img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url('data:image/png;base64,{img_b64}');
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 60px 20px;
            }}
            [data-testid="stSidebarNav"]::before {{
                content: "Mosqlimate";
                margin-left: 90px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def plot_heatmap_single(agravo = 'dengue'):
    '''
    This function creates a heatmap of Brazil's dengue incidence by quarter and state.

    Parameters
    ----------
    agravo: str
        Name of the disease. It is used to find and open the data file. 

    Returns
    -------
    altair fig 
        
    '''

    df_end= pd.read_csv(f'./data/{agravo}_br_2010-2022_quarter.csv')
    df_end.set_index('data_iniSE', inplace = True)
    df_end.index = pd.to_datetime(df_end.index)

    # Some minor adjustments in the dataframe to show the states in y-axis agg by region 
    df_end['order'] = np.nan
    df_end.loc[df_end.regiao == 'Sudeste', 'order'] = 1
    df_end.loc[df_end.regiao == 'Sul', 'order'] = 2
    df_end.loc[df_end.regiao == 'Nordeste', 'order'] = 3
    df_end.loc[df_end.regiao == 'Norte', 'order'] = 4
    df_end.loc[df_end.regiao == 'Centro-Oeste', 'order'] = 5

    # create the select box
    regiao_radio = alt.binding_radio(options=np.append([None],df_end['regiao'].unique()),labels=['All'], name="Selecione")
    selection = alt.selection_single(fields=['regiao'], bind=regiao_radio)

    # select the color scheme
    if agravo=='dengue':
        title = 'Dengue'
        color_scheme = 'viridis'

    if agravo == 'chik':
        title='Chikungunya'
        color_scheme = 'orangered'

    # create the base plot 

    points = alt.Chart(data= df_end, width=650, height=500, title=title).mark_rect(filled=True).encode(
    x= alt.X('trimestre-tick', type='nominal', title='Quarter', sort = alt.SortField('trimestre', order='ascending'),
                
                # this condition is use to highlight the name of the first two quarters by year. 
                axis=alt.Axis(
            labelColor=alt.condition(f"datum.value[0] < 3",  alt.value('black'), alt.value('grey')))     
                ),
        y = alt.Y('UF', title='State', sort = alt.SortField('order', order='ascending')), #, sort = alt.SortField("MediaPercentualDesocupapdo", order = "ascending")
        tooltip = [ alt.Tooltip(field = 'UF', title = 'State', type = "nominal"),
                    alt.Tooltip(field = "trimestre-tick", title = 'Quarter', type = "nominal"),
                    alt.Tooltip(field = "inc", title = 'Incidence by 100k notified', type = "quantitative")],
        color=alt.condition(selection, 
                            alt.Color('inc:Q', scale=alt.Scale(scheme=color_scheme),#, domain=[-20, 20]
                            legend=alt.Legend(direction='vertical', orient='left', legendY=30, title = None)),
                            alt.value('lightgray'))
    ).add_selection(
        selection
    )
    
    return points


def plot_map():

    '''
    This function creates a choropleth map animation of Brazil's dengue incidence by quarter and state.

    Returns
    -------
    plotly animation 

    '''
    
    # baixando os dados com as localizações geográficas 
    
    ufs = gpd.read_file('./data/shapefile_BR/states.shp')
    ufs = ufs[['ADM1_NAME','geometry']]
    ufs['UF'] = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE',
           'DF', 'ES', 'GO', 'MA',
           'MT', 'MS', 'MG', 'PA',
           'PB', 'PR', 'PE', 'PI', 'RJ',
           'RN', 'RS', 'RO', 'RR',
           'SC', 'SP', 'SE', 'TO']

    ufs.index = ufs.UF

    ufs.drop(['ADM1_NAME', 'UF'], axis = 1, inplace = True)
    ufs_json = json.loads(ufs.to_json())

    
    # baixando os dados com as incidências por trimestre
    agravo = 'dengue'
    df_end = pd.read_csv(f'./data/{agravo}_br_2010-2022_quarter.csv', usecols = ['data_iniSE', 'casos', 'inc', 'UF', 'trimestre']) 
    df_end.data_iniSE = pd.to_datetime(df_end.data_iniSE)

    df_end['trimestre_tick'] = df_end.trimestre.astype(str).str[:4] + '-' + df_end.trimestre.astype(str).str[-2:]

    #df_end = df_end.set_index(['UF', 'data_iniSE']).groupby([pd.Grouper(level='UF'), 
    #            pd.Grouper(level='data_iniSE', freq='Y')]
    #          ).sum().reset_index()

    df_end['year'] = df_end['data_iniSE'].dt.year

    #df = df_end.loc[df_end.year == 2023]

    fig = px.choropleth(df_end, geojson=ufs_json, locations='UF', color='inc',
                               color_continuous_scale="viridis",
                               range_color=(0, max(df_end.inc)),
                                animation_frame='trimestre_tick',
                                projection ="airy", 
                                width=500,
                               height =600                       )

    fig.update_geos(
        visible=False, fitbounds="locations")
    fig.update_layout( 
                     coloraxis_colorbar=dict(len = 0.5, thickness = 20,  y =0.7 ),
                      margin={"r":0, "t":0, "l":0,"b":0, "autoexpand": True})
    
    
    return fig 


def plot_time_series_by_week(city):
    '''
    This function creates a multi-line time series plot, where each line represents the number of 
    new cases by week in a specific year. This function gets the data from the mosqlimate API.

    Parameters
    ----------
    city: int
        The ibge code of the city (7 digit).

    Returns
    -------
    plotly figure

    '''

    
    #df = pd.read_parquet(f'{PATH_TO_CASES}/{state}_dengue.parquet',
    #                columns = ['casos', 'municipio_geocodigo'])

    df = get_dengue_data(city)
     
    df['week'] = [int(str(Week.fromdate(i))[-2:]) for i in df.index]

    fig = go.Figure()

    colors = ['#DA16FF', '#FB0D0D', '#1CA71C', '#2E91E5', '#E15F99','#511CFB','#EB663B','#750D86','#222A2A', 
            '#00A08B', '#862A16', '#778AAE', '#1616A7', "#2ED9FF"] 

    title = f"Cases notified by week"

    fig.update_layout(width=700, height=500, title={
                'text': title,
                'y': 0.85,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                xaxis_title='Week',
                yaxis_title=f'New cases',
                template='plotly_white')

    for year in np.arange(2010, 2024):
        
        df_slice = df.loc[df.index.year == year]

        df_slice = df_slice.sort_values(by = 'week')
        
        fig.add_trace(go.Scatter(x=df_slice.week, y=df_slice.casos, name = f'{year}',
                                line=dict(color=colors[year-2010])))

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', zeroline=False,
                            showline=True, linewidth=1, linecolor='black', mirror=True)

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', zeroline=False,
                            showline=True, linewidth=1, linecolor='black', mirror=True)
    
    return fig 
    

def plot_for_altair(df, df_for):
    '''
    This function creates a multi-line time series plot, where each line represents a forecast curve and 
    the black dot represents the real data.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with the real data. It must have three columns: dates, target, and legend
    
    df_for: pd.DataFrame
        A dataframe with the forecast curves. It must have five columns: dates, predictions, lower (lower bound
        of the ci of the predictions), upper (upper bound of the ci of the predictions),
        and model (information of the name of the model that the predictions refers to)

    Returns
    -------
    altair figure

    '''

    # here is loaded the element that allows the selection by the mouse
    highlight = alt.selection_point(on='mouseover', value = 'DL', fields=['model'], nearest=True)

    width = 400 # width of the plots
    height = 300

    # here is loaded the data points (black)
    data = alt.Chart(df).mark_circle(size = 60).encode(
        x='dates:T',
        y='target:Q',
        color=alt.value('black'),
        opacity=alt.Opacity('legend', legend=alt.Legend(title=None)),

        #size = alt.value(3)
        tooltip = 'target:Q'
    ).properties(
        width=width,
        height = height
    )


    # here is created the base element for the time series 
    base = alt.Chart(df_for, title="Forecast of dengue new cases").encode(
    x=alt.X('dates:T').title('Date'),
        y=alt.Y('predictions:Q').title('New cases'),
        color='model:N'
    ).add_params(
        highlight
    ).properties(
        width=width
    )

    points = base.mark_circle().encode(
        opacity=alt.value(0)
    ).add_params(
        highlight
    )


    # here we create the multine plot and use the alt.condition to highlight only one curve
    lines = base.mark_line().encode(
        #size=alt.condition(~highlight, alt.value(1), alt.value(3))
        color=alt.condition(highlight, alt.Color('model:N'), alt.value('lightgray')),
        tooltip = ['model:N', 'predictions']
        
    )

    # here we define the plot of the right figure
    timeseries = base.mark_line().encode(
        color=alt.Color('model:N')
    ).transform_filter(
        highlight # this function transform filter will just filter the element 
        #in hightlight from the column model N of the df_for (defined in the base element)
    )

    # here we create the area that represent the confidence interval of the predicitions
    timeseries_conf = base.mark_area(
        opacity=0.5
    ).encode(
        x='dates:T',
        y='lower:Q',
        y2='upper:Q'
    ).transform_filter(
        highlight
    )

    # here we concatenate the layers, the + put one layer above the other
    # the | put them syde by syde (as columns), and & put them side by side as lines
    final = points + lines + data | timeseries + timeseries_conf + data

    return final


def plot_error_bar(df, df_for):
    '''
    This function creates a multi-line time series plot, where each line represents a forecast curve and 
    the black dot represents the real data.

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe with the real data. It must have three columns: dates, target, and legend
    
    df_for: pd.DataFrame
        A dataframe with the forecast curves. It must have five columns: dates, predictions, lower (lower bound
        of the ci of the predictions), upper (upper bound of the ci of the predictions),
        and model (information on the name of the model that the predictions refer to). The model's name must be
        'RF', 'RF - cluster', 'DL', and 'DL - cluster'. Otherwise, the function will return an error. 

    Returns
    -------
    altair figure

    '''
    
    records = []

    for model in ['RF', 'RF - cluster', 'DL', 'DL - cluster']:
        
        records.append([model, mse(df.target.values, df_for.loc[df_for.model == model]["predictions"].values ), 'MSE'])
        records.append([model, mse(df.target.values, df_for.loc[df_for.model == model]["predictions"].values, squared = False ), 'RMSE'])
        records.append([model, msle(df.target.values, df_for.loc[df_for.model == model]["predictions"].values ), 'MSLE'])
        records.append([model, mae(df.target.values, df_for.loc[df_for.model == model]["predictions"].values ), 'MAE'])
        

    df_erro = pd.DataFrame(records
    , 
        columns=['model', 'erro', 'metric'])
    
    input_dropdown = alt.binding_select(options=['MAE','MSE', 'RMSE', 'MSLE'], name='Error metric: ')
    
    selection = alt.selection_point(fields=['metric'], bind=input_dropdown)

    final = alt.Chart(df_erro).mark_bar().encode(
        x=alt.X('erro:Q').title('Erro'),
        y=alt.Y('model:N').title('Model'),
        color='model:N'
    ).add_params(
        selection
    ).transform_filter(
        selection
    ).properties(
        width=500,
        height = 200
    )

    return final 