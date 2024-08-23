import pickle
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt


from model_weekly import weekly_switchpoints_model
from plots import plot_daily_pH_training, plot_daily_switchpoints, plot_weekly_switchpoints
from utils import load_data
from model_daily import daily_admissions_model, daily_switchpoints_model


def train_daily_model(region, start_date='2020-06-29', end_date='2020-12-01',
                      burn=4000, draws=5000, n_chains=4, verbose=False):
    
    cases, hospitalized = load_data(region, start_date, end_date)
    

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


            plot_daily_pH_training(data, start_date, end_date,region)

    with open(f'results/train_daily_{region}.pickle', 'wb') as file:
        pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)

    return float(idata.posterior.pH.stack(sample=('chain', 'draw')).mean()), \
        float(idata.posterior.admissions_lambda.stack(sample=('chain', 'draw')).mean())


def estimate_daily_switchpoints(region, admissions_lambda, start_date='2020-07-01',
                                end_date='2021-09-15', burn=4000, draws=5000, n_chains=4,
                                verbose=False, n_switchpoints=1, estimate_sw = False):
    if region == 'Italy':
        start_date = '2020-09-01'
    print('HE ENTRADO AL PROGRAMA')
    cases, hospitalized = load_data(region, start_date, end_date)
    print('\n HE CARGADO LOS DATOS')
    if not estimate_sw:
        dict_init_values = {
            'rate' : np.array(np.linspace(3, 10, n_switchpoints + 1)),
            'sigma' : None,
            'admissions' : None
        }
    else:
        dict_init_values = {
            'switchpoint' : np.array(np.linspace(100, 500, n_switchpoints)),
            'rate' : np.array(np.linspace(3, 10, n_switchpoints + 1)),
            'sigma' : None,
            'admissions' : None
        }
    with daily_switchpoints_model(cases, hospitalized, admissions_lambda, n_switchpoints, estimate_sw= estimate_sw) as model:
        
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

            plot_daily_switchpoints(data, start_date, end_date, idata, n_switchpoints, region, estimate_sw=estimate_sw)
    if not estimate_sw:
        with open(f'results/fixed_switchpoints_daily_{n_switchpoints}_{region}.pickle', 'wb') as file:
            pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        with open(f'results/non_fixed_switchpoints_daily_{n_switchpoints}_{region}.pickle', 'wb') as file:
            pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)

def estimate_weekly_switchpoints(region, start_date='2020-07-01', end_date='2022-03-27',
                                 burn=2000, draws=5000, n_chains=4, verbose=False,
                                 n_switchpoints=1):

    cases, hospitalized = load_data(region, start_date, end_date, True)

    with weekly_switchpoints_model(cases, hospitalized, n_switchpoints) as model:
        idata = pm.sample(draws=draws, tune=burn, chains=n_chains,
                          idata_kwargs={"log_likelihood": True})

        pm.sample_posterior_predictive(idata, extend_inferencedata=True)

        if verbose:
            az.summary(idata)
            az.plot_trace(idata)

            data = {
                'admissions': idata.posterior['posterior_predictive']
                .stack(sample=('chain', 'draw'))['admissions'].to_numpy(),
                'hospitalized': idata.posterior['observed_data']['admissions'].to_numpy()
            }

            plot_weekly_switchpoints(data, start_date, end_date, idata, n_switchpoints)

    with open(f'results/switchpoints_weekly_{n_switchpoints}_{region}.pickle', 'wb') as file:
        pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)
