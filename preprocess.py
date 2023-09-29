import pickle
import aiohttp
import asyncio
import requests 
import pandas as pd
from datetime import datetime 

def load_nn(city, label, ini_date = '2021-12-26', end_date= '2023-07-02', doenca = 'dengue'):
    '''
    This function loads the prediction from the deep learning model saved in a pkl.

    Parameters
    ----------
    city: int
        Ibge code of the city. It is used to find and open the data file. 
    label: str
        Indicate which prediction will be loaded, by now accepts two values: `single` or `cluster` .
        It is used to find and open the data file.
    ini_date: str
        Start of the predictions returned. Format: YYYY-mm-dd.
    ini_date: str
        End of the predictions returned. Format: YYYY-mm-dd.
    ini_date: str
        Indicate which prediction will be loaded, by now accepts only: `dengue`.
        It is used to find and open the data file. 

    Returns
    -------
    pd.DataFrame 
        A dataframe with the predictions  
        
    '''
    
    data_nn = pickle.load(open(f'./data/predictions/lstm_{city}_{doenca}_{label}.pkl', 'rb'))
    
    
    df_nn = pd.DataFrame()

    ini_index = data_nn['indice'].index(datetime.strptime(ini_date, '%Y-%m-%d'))
    end_index = data_nn['indice'].index(datetime.strptime(end_date, '%Y-%m-%d')) + 1 

    df_nn['dates'] = data_nn['indice'][ini_index:end_index]
    df_nn['target'] = data_nn['target'][ini_index - 7: end_index - 7, -1] * data_nn['factor']
    df_nn['preds']  = (data_nn['pred'].iloc[ini_index - 7: end_index - 7,-1] * data_nn['factor']).values
    df_nn['lb']  = (data_nn['lb'].iloc[ini_index - 7: end_index - 7,-1] * data_nn['factor']).values
    df_nn['ub']  = (data_nn['ub'].iloc[ini_index - 7: end_index - 7,-1] * data_nn['factor']).values
    
    df_nn.set_index('dates', inplace = True)
    
    df_nn.index = pd.to_datetime(df_nn.index)

    return df_nn 


def load_ml(city, label,  ini_date = '2021-12-26', end_date= '2023-07-02', doenca = 'dengue'):
    '''
    This function loads the prediction from the random forest model saved in a pkl.

    Parameters
    ----------
    city: int
        Ibge code of the city. It is used to find and open the data file. 
    label: str
        Indicate which prediction will be loaded, by now accepts two values: `single` or `cluster` .
        It is used to find and open the data file.
    ini_date: str
        Start of the predictions returned. Format: YYYY-mm-dd.
    ini_date: str
        End of the predictions returned. Format: YYYY-mm-dd.
    ini_date: str
        Indicate which prediction will be loaded, by now accepts only: `dengue`.
        It is used to find and open the data file. 

    Returns
    -------
    pd.DataFrame 
        A dataframe with the predictions  
        
    '''

    data_ml = pickle.load(open(f'./data/predictions/rf_{city}_{doenca}_{label}_predictions.pkl', 'rb'))
    
    df_ml = pd.DataFrame()

    df_ml['dates'] = data_ml['dates']
    df_ml['target'] = data_ml['target']
    df_ml['preds'] = data_ml['preds']
    df_ml['lb'] = data_ml['preds25']
    df_ml['ub'] = data_ml['preds975']

    df_ml.dates = pd.to_datetime(df_ml.dates)

    df_ml = df_ml.loc[(df_ml.dates >= ini_date) & (df_ml.dates <= end_date)]
    
    df_ml.set_index('dates', inplace = True)
    
    return df_ml

def join_preds(city):
    '''
    This function will join the predictions of the different models in a single dataframe. 
    This step is necessary to create the forecast plot later.

    Parameters
    ----------
    city: int
        Ibge code of the city. It is used to find and open the data file.  

    Returns
    -------
    pd.DataFrame 
        A dataframe with the predictions  
        
    '''
    
    df_ml_single = load_ml(city, label = 'single')
    
    df_nn_single = load_nn(city, label = 'single')

    df_single = df_ml_single.join(df_nn_single, how = 'outer', rsuffix='_nn')
    
    df_ml_cluster = load_ml(city, label = 'cluster')
    
    df_nn_cluster = load_nn(city, label = 'cluster')

    df_cluster = df_ml_cluster.join(df_nn_cluster, how = 'outer', rsuffix='_nn')
    
    df_end = df_single.join(df_cluster, how = 'outer', rsuffix='_cluster')
    
    return df_end


def get_forecast_to_plot(city): 
    '''
    This function return the dataframe necessary to create the altair plot.

    Parameters
    ----------
    city: int
        Ibge code of the city. It is used to find and open the data file.  

    Returns
    -------
    df: pd.DataFrame 
        A dataframe with the data of new cases

    df: pd.DataFrame 
        A dataframe with the predictions 
        
    '''

    df_e = join_preds(city)
    df_e = df_e.reset_index()

    df_plot = pd.melt(df_e, id_vars=['dates'], value_vars = ['preds', 'preds_nn', 'preds_cluster', 'preds_nn_cluster'], 
       var_name = 'model', value_name = 'predictions')

    df_plot['model'] = df_plot['model'].replace(
    {'preds': 'RF', 'preds_nn': 'DL', 'preds_cluster': 'RF - cluster', 'preds_nn_cluster': 'DL - cluster'})

    df_lower = pd.melt(df_e, id_vars=['dates'], value_vars = df_e.columns[df_e.columns.str.startswith('lb')], 
       var_name = 'model', value_name = 'lower')

    df_lower['model'] = df_lower['model'].replace(
    {'lb': 'RF', 'lb_nn': 'DL', 'lb_cluster': 'RF - cluster', 'lb_nn_cluster': 'DL - cluster'})

    df_upper = pd.melt(df_e, id_vars=['dates'], value_vars = df_e.columns[df_e.columns.str.startswith('ub')], 
       var_name = 'model', value_name = 'upper')

    df_upper['model'] = df_upper['model'].replace(
    {'ub': 'RF', 'ub_nn': 'DL', 'ub_cluster': 'RF - cluster', 'ub_nn_cluster': 'DL - cluster'})

    df_for = (df_plot.merge(df_lower, left_on = ['dates', 'model'], right_on = ['dates', 'model'])).merge(df_upper, left_on = ['dates', 'model'], right_on = ['dates', 'model'])

    df = df_e[['dates', 'target']]
    df['legend'] = 'Data'   

    return df, df_for



async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

async def retry(session, url, max_retries=3):
    for attempt in range(max_retries + 1):
        try:
            return await fetch_data(session, url)
        except Exception as e:
            if attempt < max_retries:
                delay = 2 ** attempt
                await asyncio.sleep(delay/10)
            else:
                return await retry(session, url)

async def get_data_from_API(city):
    '''
    This function returns the data of the column historico alerta (available in the API) for a specific city.

    Parameters
    ----------
    city: int
        Ibge code of the city. 

    Returns
    -------
    request data (in json)
        
    '''
    
    res = []
    tasks = []
    
    historico_alerta_api = "https://api.mosqlimate.org/api/datastore/historico_alerta/"
    filters = "disease=%s&start=%s&end=%s&geocode=%i" % ("dengue", "2010-01-01", "2023-12-30", city)

    
    pagination = f"?page=1&per_page=100&"
    url = historico_alerta_api + pagination + filters
    
    resp = requests.get(historico_alerta_api + pagination + filters)
    last_page = resp.json()["pagination"]['total_pages']
    
    resp = resp.json()
    
    #tasks.append(resp)
    
    res.extend(resp['items'])

    async with aiohttp.ClientSession() as session:
        for i in range(2, last_page+1):
            pagination = f"?page={i}&per_page=100&"
            url = historico_alerta_api + pagination + filters
            data = retry(session, url)
            tasks.append(data)

        results = await asyncio.gather(*tasks)

    for result in results:
        res.extend(result["items"])

    return res

def get_dengue_data(city):
    '''
    This function transforms the output of the function get_data_from_API in a pandas DataFrame.

    Parameters
    ----------
    city: int
        Ibge code of the city. 

    Returns
    -------
    pd.DataFrame
        
    '''

    res = asyncio.run(get_data_from_API(city))

    df = pd.DataFrame(res)

    df.set_index('data_iniSE', inplace = True)
    
    df.index = pd.to_datetime(df.index)

    return df.sort_index() 




    


