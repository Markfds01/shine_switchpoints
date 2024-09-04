import numpy as np
import pymc as pm
import pytensor


def daily_admissions_model(cases, observed_admissions):

    delay_matrix_0 = make_delay_matrix(len(cases), len(cases), 0)

    with pm.Model() as model:
        # priors
        ph = pm.Uniform(name='pH', lower=0, upper=1)
        admissions_lambda = pm.Uniform(name='admissions_lambda', lower=0.1, upper=20)
        sigma = pm.Uniform(name='sigma', lower=1, upper=100)

        # trainning
        new_hospitalized = ph * cases
        admissions = delay_cases(new_hospitalized, admissions_lambda, delay_matrix_0)
        pm.NegativeBinomial(name='admissions', mu=admissions, alpha=sigma,
                            observed=observed_admissions)

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


def daily_switchpoints_model(cases, observed_admissions, admissions_lambda, n_switchpoints, estimate_sw = False):

    delay_matrix_0 = make_delay_matrix(len(cases), len(cases), 0)

    with pm.Model() as model:

        def build_switch():
            value = rates[n_switchpoints]
            for idx in range(0, n_switchpoints):
                weight = pm.math.sigmoid(2 * (points - switchpoints[idx]))
                value = weight * rates[n_switchpoints - idx - 1] + (1 - weight) * value
            return value/100

        points = np.arange(0, len(cases))
        if not estimate_sw:
            switchpoints = np.array([164, 257, 354, 469])  # Fixed switchpoints
            n_switchpoints = len(switchpoints)
        else:
            switchpoints = pm.Uniform('switchpoint', lower=30, upper=len(points), shape=(n_switchpoints,),
                                  transform=pm.distributions.transforms.Ordered())
            
        rates = pm.Gamma('rate', alpha=7.5, beta=1.0, shape=(n_switchpoints+1,),
                          transform=pm.distributions.transforms.Ordered())
        #pm.Uniform('rate', lower=0, upper=1, shape=(n_switchpoints+1,))

        rate = build_switch()
        sigma = pm.Uniform(name='sigma', lower=1, upper=100)

        # trainning
        new_hospitalized = rate * cases
        admissions = delay_cases(new_hospitalized, admissions_lambda, delay_matrix_0)
        pm.NegativeBinomial(name='admissions', mu=admissions, alpha=sigma,
                            observed=observed_admissions)

    return model
