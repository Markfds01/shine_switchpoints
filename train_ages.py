import pickle
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


from model_weekly import weekly_switchpoints_model
from plots import plot_daily_pH_training, plot_daily_switchpoints, plot_weekly_switchpoints
from utils_ages import load_data_ages
from model_daily import daily_admissions_model, daily_switchpoints_model


def train_daily_model_ages(region, start_date='2020-06-29', end_date='2020-12-01',
                      burn=4000, draws=5000, n_chains=4, verbose=False):
    
    cases_per_age, hospitalized_per_age = load_data_ages(region, start_date, end_date)

    pH = []
    admissions_lambda = {}

    for edad in cases_per_age['grupo_edad'].unique():
        if edad == 'NC':
            continue
    
        print(f' edad es {edad}')
        cases_edad = cases_per_age[cases_per_age['grupo_edad']==edad]
        cases = cases_edad['num_casos']

        hospitalized_edad = hospitalized_per_age[hospitalized_per_age['grupo_edad']==edad]
        hospitalized = hospitalized_edad['num_hosp']
        print(f' numero maximo de hospitalizados es {hospitalized.max()}')

        

        with daily_admissions_model(cases, hospitalized) as model:
            # Sample from the posterior
            idata = pm.sample(draws=draws, tune=burn, chains=n_chains, 
                            return_inferencedata=True, target_accept=0.95, idata_kwargs={"log_likelihood": True})
            
            # Generate posterior predictive samples
            idata.extend(pm.sample_posterior_predictive(idata))
            print(f'data keys are : {idata.posterior_predictive.data_vars}')


            if verbose:
                az.summary(idata)
                az.plot_trace(idata)

                data = {
                    'admissions': idata.posterior_predictive['admissions'].stack(sample=('chain', 'draw')).to_numpy(),
                    'hospitalized': idata.observed_data['admissions'].to_numpy()
                }


                plot_daily_pH_training(data, start_date, end_date,region, edad)

            mean_pH = float(idata.posterior.pH.stack(sample=('chain', 'draw')).mean())
            mean_admission_lambda = float(idata.posterior.admissions_lambda.stack(sample=('chain', 'draw')).mean())
            pH.append(mean_pH)
            admissions_lambda[edad] = mean_admission_lambda
            with open(f'results/train_daily_{region}_{edad}.pickle', 'wb') as file:
                pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)

    return pH, admissions_lambda


def estimate_daily_switchpoints_ages(region, admissions_lambda_dict, start_date='2020-07-01',
                                end_date='2021-09-15', burn=4000, draws=5000, n_chains=4,
                                verbose=False, n_switchpoints=1):
    if region == 'Italy':
        start_date = '2020-09-01'
    print('HE ENTRADO AL PROGRAMA')
    cases_per_age, hospitalized_per_age = load_data_ages(region, start_date, end_date)
    print('\n HE CARGADO LOS DATOS')
    dict_init_values = {
        'rate' : np.array(np.linspace(3, 10, n_switchpoints + 1)),
        'sigma' : None,
        'admissions' : None
    }

    for i,edad in enumerate(cases_per_age['grupo_edad'].unique()):
        if edad == 'NC':
            continue
        admissions_lambda = admissions_lambda_dict[edad]
        print(f' edad es {edad}')
        cases_edad = cases_per_age[cases_per_age['grupo_edad']==edad]
        cases = cases_edad['num_casos']
        hospitalized_edad = hospitalized_per_age[hospitalized_per_age['grupo_edad']==edad]
        hospitalized = hospitalized_edad['num_hosp']

        with daily_switchpoints_model(cases, hospitalized, admissions_lambda, n_switchpoints) as model:
            
            idata = pm.sample(draws=draws, tune=burn, chains=n_chains,
                            return_inferencedata=True, target_accept=0.99, idata_kwargs={"log_likelihood": True},initvals=dict_init_values)
            idata.extend(pm.sample_posterior_predictive(idata))

            if verbose:
                az.summary(idata)
                fig = az.plot_trace(idata)
                plt.savefig(f'plots/trace_plot_{region}.png')

                data = {
                    'admissions': idata.posterior_predictive['admissions'].stack(sample=('chain', 'draw')).to_numpy(),
                    'hospitalized': idata.observed_data['admissions'].to_numpy()
                }

                plot_daily_switchpoints(data, start_date, end_date, idata, n_switchpoints, region, edad)


            with open(f'results/fixed_switchpoints_daily_{n_switchpoints}_{region}_{edad}.pickle', 'wb') as file:
                pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)
        # Create a DataFrame from the list