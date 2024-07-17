import numpy as np
import pymc as pm


def weekly_switchpoints_model(cases, observed_admissions, n_switchpoints):

    with pm.Model() as model:

        def build_switch():
            value = rates[n_switchpoints]
            for idx in range(0, n_switchpoints):
                weight = pm.math.sigmoid(2 * (points - switchpoints[idx]))
                value = weight * rates[n_switchpoints - idx - 1] + (1 - weight) * value
            return value

        points = np.arange(0, len(cases))
        switchpoints = pm.Uniform('switchpoint', lower=0, upper=len(points), shape=(n_switchpoints,),
                                  transform=pm.distributions.transforms.univariate_ordered,
                                  initval=np.array([50, 100]))
        rates = pm.Uniform('rate', lower=0, upper=1, shape=(n_switchpoints+1,))

        rate = build_switch()

        # trainning
        pm.Binomial("admissions", p=rate, n=cases, observed=observed_admissions)

    return model
