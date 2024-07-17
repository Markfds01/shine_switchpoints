import numpy as np
import pymc as pm
import pytensor


def daily_deaths_model(cases, observed_deaths):

    delay_matrix_0 = make_delay_matrix(len(cases), len(cases), 0)

    with pm.Model() as model:
        # priors
        pD = pm.Uniform(name='pD', lower=0, upper=1)
        deaths_lambda = pm.Uniform(name='deaths_lambda', lower=0.1, upper=20)
        sigma = pm.Uniform(name='sigma', lower=1, upper=100)

        # trainning
        new_deaths = pD * cases
        deaths = delay_cases(new_deaths, deaths_lambda, delay_matrix_0)
        pm.NegativeBinomial(name='deaths', mu=deaths, alpha=sigma,
                            observed=observed_deaths)

    return model


def make_delay_matrix(n_rows, n_columns, first_value):
    size = max(n_rows, n_columns)
    matrix = np.zeros((size, size))
    for i in range(size):
        diagonal = np.ones(size - i) * (first_value + i)
        matrix += np.diag(diagonal, i)
    return matrix[:n_rows, :n_columns].astype(int)


def delay_cases(input_array, parameter_1, delay_matrix):
    probability = cdf_exponential(np.arange(delay_matrix.shape[0] + 1) - 0.5, parameter_1)
    matrix = pytensor.tensor.triu(probability[delay_matrix])
    return pm.math.dot(input_array, matrix)


def cdf_exponential(x, lam):
    cdf = pm.math.exp(pm.logcdf(pm.Exponential.dist(lam=lam), x))
    return cdf[1:] - cdf[:-1]


def deaths_switchpoints_model(cases, observed_deaths, deaths_lambda, n_switchpoints):

    delay_matrix_0 = make_delay_matrix(len(cases), len(cases), 0)

    with pm.Model() as model:

        def build_switch():
            value = rates[n_switchpoints]
            for idx in range(0, n_switchpoints):
                weight = pm.math.sigmoid(2 * (points - switchpoints[idx]))
                value = weight * rates[n_switchpoints - idx - 1] + (1 - weight) * value
            return value/100

        points = np.arange(0, len(cases))
        switchpoints = pm.Uniform('switchpoint', lower=0, upper=len(points), shape=(n_switchpoints,),
                                  transform=pm.distributions.transforms.univariate_ordered,
                                  initval=np.array(np.linspace(350, 550, n_switchpoints)))
        rates = pm.Gamma('rate', alpha=7.5, beta=1.0, shape=(n_switchpoints+1,),
                         transform=pm.distributions.transforms.univariate_ordered,
                         initval=np.array(np.linspace(3, 10, n_switchpoints + 1)))
        #pm.Uniform('rate', lower=0, upper=1, shape=(n_switchpoints+1,))

        rate = build_switch()
        sigma = pm.Uniform(name='sigma', lower=1, upper=100)

        # trainning
        new_deaths = rate * cases
        deaths = delay_cases(new_deaths, deaths_lambda, delay_matrix_0)
        pm.NegativeBinomial(name='deaths', mu=deaths, alpha=sigma,
                            observed=observed_deaths)

    return model
