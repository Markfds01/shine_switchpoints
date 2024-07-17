import pickle
import pymc as pm
import arviz as az
from plots import plot_daily_pD_training, plot_deaths_switchpoints
from utils import load_data
from model_deaths import daily_deaths_model, deaths_switchpoints_model


def train_deaths_model(region, start_date='2020-06-29', end_date='2020-12-01',
                       burn=2000, draws=5000, n_chains=4, verbose=False):
    cases, deaths = load_data(region, start_date, end_date, deaths=True)

    with daily_deaths_model(cases, deaths) as model:
        idata = pm.sample(draws=draws, tune=burn, chains=n_chains,
                          idata_kwargs={"log_likelihood": True})
        pm.sample_posterior_predictive(idata, extend_inferencedata=True)

        if verbose:
            az.summary(idata)
            az.plot_trace(idata)

            data = {
                'deaths_estimated': idata.posterior['posterior_predictive']
                .stack(sample=('chain', 'draw'))['deaths'].to_numpy(),
                'deaths_observed': idata.posterior['observed_data']['deaths'].to_numpy()
            }

            plot_daily_pD_training(data, start_date, end_date)

    with open(f'results/train_deaths_{region}.pickle', 'wb') as file:
        pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)

    return float(idata.posterior.pD.stack(sample=('chain', 'draw')).mean()), \
        float(idata.posterior.deaths_lambda.stack(sample=('chain', 'draw')).mean())


def estimate_deaths_switchpoints(region, deaths_lambda, start_date='2020-07-01',
                                 end_date='2022-03-27', burn=2000, draws=5000, n_chains=4,
                                 verbose=False, n_switchpoints=1):

    cases, deaths = load_data(region, start_date, end_date, deaths=True)

    with deaths_switchpoints_model(cases, deaths, deaths_lambda, n_switchpoints) as model:
        idata = pm.sample(draws=draws, tune=burn, chains=n_chains,
                          idata_kwargs={"log_likelihood": True})
        pm.sample_posterior_predictive(idata, extend_inferencedata=True)

        if verbose:
            az.summary(idata)
            az.plot_trace(idata)

            data = {
                'deaths_estimated': idata.posterior['posterior_predictive']
                .stack(sample=('chain', 'draw'))['deaths'].to_numpy(),
                'deaths_observed': idata.posterior['observed_data']['deaths'].to_numpy()
            }

            plot_deaths_switchpoints(data, start_date, end_date, idata, n_switchpoints)

    with open(f'results/switchpoints_deaths_{n_switchpoints}_{region}.pickle', 'wb') as file:
        pickle.dump(idata, file, protocol=pickle.HIGHEST_PROTOCOL)
