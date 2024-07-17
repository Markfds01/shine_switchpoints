import concurrent.futures
from parser import parse_args
from train import train_daily_model, estimate_daily_switchpoints
from train_deaths import train_deaths_model, estimate_deaths_switchpoints

if __name__ == "__main__":
    args = parse_args()

    if not args.deaths:
        # Hospitalization
        pH, admissions_lambda = train_daily_model(args.region, verbose=True)
        print(f' pH es {pH}, admissions_lambda es {admissions_lambda}\n')
        #estimate_daily_switchpoints(region=args.region, admissions_lambda=admissions_lambda,
                                    #n_switchpoints=args.n_switchpoints)
    else:
        # Deaths
        pD, deaths_lambda = train_deaths_model(args.region)
        estimate_deaths_switchpoints(region=args.region, deaths_lambda=deaths_lambda,
                                     n_switchpoints=args.n_switchpoints)