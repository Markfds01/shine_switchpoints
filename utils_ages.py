from datetime import timedelta
import pandas as pd


def load_data_ages(region, start_date, end_date, aggregate_week=False, deaths=False):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if len(region) == 2 or region == 'Spain': # Spanish provinces
        cases_per_age, hospitalized = load_spanish_ages(region, start_date, end_date, aggregate_week, deaths)
    else: # European countries
        raise Exception("Not in Spain")

    return cases_per_age, hospitalized


def load_spanish_ages(region, start_date, end_date, aggregate_week, deaths):
    # Subset provinces
    if region == 'CT':
        cases_per_age, pred = load_CT_ages(start_date, end_date, aggregate_week, deaths)
        return cases_per_age, pred
    provinces = pd.read_csv('data/provinces_iso.csv')
    if region == 'Spain':
        provinces = provinces['province_iso']
    else:
        if region not in provinces['ccaa_iso'].values:
            raise Exception('region not found')

        provinces = provinces.loc[provinces['ccaa_iso'] == region]['province_iso']

    # Load data
    data = pd.read_csv('data/casos_hosp_uci_def_sexo_edad_provres.csv')
    data = data[data.provincia_iso.isin(provinces)]
    data['fecha'] = pd.to_datetime(data['fecha'])
    data = data.groupby(['fecha','grupo_edad']).sum(['num_casos', 'num_hosp', 'num_def'])
    
    # Extract values
    data = data.loc[start_date:end_date]
    if aggregate_week:
        data['num_casos'] = data.groupby('grupo_edad')['num_casos'].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
        data['num_hosp'] = data.groupby('grupo_edad')['num_hosp'].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
    data = data.reset_index()
    cases_per_age = data[['num_casos', 'grupo_edad']]
    if not deaths:
        pred = data[['num_hosp','grupo_edad']]
    else:
        pred = data[['num_def','grupo_edad']]

    return cases_per_age, pred

def load_CT_ages(start_date, end_date, aggregate_week, deaths):
    # Load data
    data = pd.read_csv('data/dades_covid_2022.csv')
    data.rename(columns={
    'DATA': 'fecha',
    'GRUP_EDAT': 'grupo_edad',
    'CASOS_CONFIRMAT': 'num_casos',
    'INGRESSOS_TOTAL': 'num_hosp'
    }, inplace=True)
    data['fecha'] = pd.to_datetime(data['fecha'])
    data = data[(data['fecha'] >= start_date) & (data['fecha'] <= end_date)]    

    data = data.groupby(['fecha','grupo_edad']).sum(['num_casos', 'num_hosp'])

    # Extract values
    if aggregate_week:
        data['num_casos'] = data['num_casos'].rolling(window=7, min_periods=1).mean()
        data['num_hosp'] = data['num_hosp'].rolling(window=7, min_periods=1).mean()
    data = data.reset_index()
    cases_per_age = data[['num_casos', 'grupo_edad']] 

    if not deaths:
        pred = data[['num_hosp','grupo_edad']]
    else:
        raise Exception('Not deaths implemented for CT')

    return cases_per_age, pred