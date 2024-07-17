from datetime import timedelta
import pandas as pd


def load_data(region, start_date, end_date, aggregate_week=False, deaths=False):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if len(region) == 2 or region == 'Spain': # Spanish provinces
        cases, hospitalized = load_spanish(region, start_date, end_date, aggregate_week, deaths)
    else: # European countries
        cases, hospitalized = load_owid(region, start_date, end_date,  aggregate_week, deaths)

    return cases, hospitalized


def load_spanish(region, start_date, end_date, aggregate_week, deaths):
    # Subset provinces
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
    data = data.groupby('fecha').sum(['num_casos', 'num_hosp', 'num_def'])

    # Extract values
    data = data.loc[start_date:end_date]
    if aggregate_week:
        data = data.groupby(pd.Grouper(freq='W-MON'))[['num_casos', 'num_hosp', 'num_def']].sum()

    cases = data['num_casos']
    if not deaths:
        pred = data['num_hosp']
    else:
        pred = data['num_def']

    return cases, pred


def load_ecdc(region, start_date, end_date, aggregate_week, deaths):
    if deaths:
        exit('Death estimation not implemented for european countries')

    # Load cases
    cases = pd.read_csv('data/ECDC/cases/data.csv')
    cases = cases.loc[cases['countriesAndTerritories'] == region]
    cases['date'] = pd.to_datetime(cases['dateRep'], dayfirst=True)
    cases = cases.set_index('date').sort_index()

    # Extract values
    cases = cases.loc[start_date:end_date]
    if aggregate_week:
        cases = cases.groupby(pd.Grouper(freq='W-MON'))[['cases']].sum()

    # Load hospitalizations
    hospitalizations = pd.read_csv('data/ECDC/hospitalization/data.csv')
    hospitalizations = hospitalizations.loc[hospitalizations['country'] == region]
    hospitalizations = hospitalizations.loc[hospitalizations['indicator'] == 'Daily hospital occupancy']
    hospitalizations['date'] = pd.to_datetime(hospitalizations['date'])
    hospitalizations = hospitalizations.set_index('date').sort_index()

    hospitalizations = hospitalizations.loc[start_date:end_date]
    if aggregate_week:
        hospitalizations = hospitalizations.groupby(pd.Grouper(freq='W-MON'))[['cases']].sum()

    cases = cases['cases']
    hospitalizations = hospitalizations['value']

    return cases, hospitalizations


def load_owid(region, start_date, end_date, aggregate_week, deaths):
    # Load cases
    data = pd.read_csv('data/OWID/new_cases.csv')
    data = pd.melt(data, id_vars=['date'], var_name='country', value_name='cases')
    data = data.loc[data['country'] == region]
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').sort_index()
    data = data.loc[start_date:end_date]
    cases = data['cases']

    # Load hospitalizations
    data = pd.read_csv('data/OWID/covid-hospitalizations.csv')
    data = data.loc[data['entity'] == region]
    data = data.loc[data['indicator'] == 'Weekly new hospital admissions']
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').sort_index()

    end_date_hosp = end_date + timedelta(days=7)

    data = data.loc[start_date:end_date_hosp, ['value']]
    data = (data.reindex(pd.date_range(start_date, end_date_hosp, freq='D'))
            .rename_axis('date')
            .interpolate())
    data['hospitalization'] = data['value'].diff()
    data['hospitalization'][0] = 0

    values = []
    for line, (index, row) in enumerate(data.iterrows()):
        if line < 7:
            values.append(row['hospitalization'] + data['value'][0]/7)
        else:
            values.append(row['hospitalization'] + values[line - 7])

    data['test'] = list(pd.Series(values)[::-1].rolling(window=7).sum()[::-1])
    data['daily'] = values
    data = data.loc[start_date:end_date]

    hospitalization = data['daily']

    return cases, hospitalization

