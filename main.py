import concurrent.futures
from parser import parse_args
from train import train_daily_model, estimate_daily_switchpoints
from train_deaths import train_deaths_model, estimate_deaths_switchpoints
from train_ages import train_daily_model_ages, estimate_daily_switchpoints_ages

if __name__ == "__main__":
    args = parse_args()

    if not args.deaths:
        if args.ages:
            pH_array, admissions_lambda_dict = train_daily_model_ages(args.region, verbose=True)
            print(f' pH es {pH_array}, admissions_lambda es {admissions_lambda_dict}\n')
            estimate_daily_switchpoints_ages(region=args.region, admissions_lambda_dict=admissions_lambda_dict,
                                        n_switchpoints=args.n_switchpoints,verbose=True)
        # Hospitalization
        else:
            pH, admissions_lambda = train_daily_model(args.region, verbose=True)
            print(f' pH es {pH}, admissions_lambda es {admissions_lambda}\n')
            estimate_daily_switchpoints(region=args.region, admissions_lambda=admissions_lambda,
                                        n_switchpoints=args.n_switchpoints,verbose=True)
    else:
        # Deaths
        pD, deaths_lambda = train_deaths_model(args.region)
        estimate_deaths_switchpoints(region=args.region, deaths_lambda=deaths_lambda,
                                     n_switchpoints=args.n_switchpoints)