import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def plot_daily_pH_training(data, start_date, end_date,region = None,edad = None):
    posterior_quantile = np.percentile(data['admissions'], [2.5, 25, 50, 75, 97.5], axis=1)
    dates = pd.date_range(start_date, end_date).strftime('%m-%d')
    plot_dates = [dates[i] for i in range(0, len(posterior_quantile[2, :]), 21)]

    plt.figure()
    plt.plot(
        dates, posterior_quantile[2, :],
        color='b', label='posterior median', lw=2
    )

    plt.fill_between(
        dates, posterior_quantile[0, :], posterior_quantile[4, :],
        color='b', label='95% quantile', alpha=.2
    )

    plt.plot(
        dates, data['hospitalized'],
        '--o', color='k', markersize=3,
        label='Observed admissions', alpha=.8
    )

    plt.xticks(plot_dates)
    plt.ylabel('Daily number of admissions', fontsize='large')
    plt.xlabel('Day', fontsize='large')

    fontsize = 'medium'
    plt.legend(loc='upper left', fontsize=fontsize)

    plt.savefig(f'plots/fit_{region}_{edad}.png')


def plot_daily_switchpoints(data, start_date, end_date, trace, n_switchpoints, region = None, edad = None):
    print('\n Im plotting switchpoints')
    posterior_quantile = np.percentile(data['admissions'], [2.5, 25, 50, 75, 97.5], axis=1)

    dates = pd.date_range(start_date, end_date).strftime('%y-%m-%d')
    plot_dates = [dates[i] for i in range(0, len(posterior_quantile[2, :]), 21)]

    plt.figure()
    # Data
    plt.plot(
        dates, posterior_quantile[2, :],
        color='b', label='posterior median', lw=2
    )

    plt.fill_between(
        dates, posterior_quantile[0, :], posterior_quantile[4, :],
        color='b', label='95% quantile', alpha=.2
    )

    plt.plot(
        dates, data['hospitalized'], '.',
        alpha=0.6, markersize=3, label='Observed admissions')

    # Switchpoints with CI
    for idx in range(n_switchpoints):
        values = trace.posterior.quantile((.025, .5, .975), dim=('chain', 'draw'))
        point = values['switchpoint'].values[:, idx]
        plt.vlines(dates[int(point[1])],
                   data['hospitalized'].min(), data['hospitalized'].max(), color='C1')

        plt.fill_betweenx(
            y=[data['hospitalized'].min(), data['hospitalized'].max()],
            x1=dates[int(point[0])],
            x2=dates[int(point[2])],
            alpha=0.5,
            color="C1",
        )

    plt.xticks(plot_dates)
    plt.ylabel('Daily number of admissions', fontsize='large')
    plt.xlabel('Day', fontsize='large')

    fontsize = 'medium'
    plt.legend(loc='upper left', fontsize=fontsize)
    plt.savefig(f'plots/fit_{region}_switchpoints_{edad}.png')



def plot_weekly_switchpoints(data, start_date, end_date, trace, n_switchpoints):
    posterior_quantile = np.percentile(data['admissions'], [2.5, 25, 50, 75, 97.5], axis=1)

    dates = pd.date_range(start_date, end_date, freq='W').strftime('%y-%m-%d')
    plot_dates = [dates[i] for i in range(0, len(posterior_quantile[2, :]), 6)]

    plt.figure()
    # Data
    plt.plot(
        dates, posterior_quantile[2, :],
        color='b', label='posterior median', lw=2
    )

    plt.fill_between(
        dates, posterior_quantile[0, :], posterior_quantile[4, :],
        color='b', label='95% quantile', alpha=.2
    )

    plt.plot(
        dates, data['hospitalized'], '.',
        alpha=0.6, markersize=3, label='Observed admissions')

    # Switchpoints with CI
    for idx in range(n_switchpoints):
        values = trace.posterior.quantile((.025, .5, .975), dim=('chain', 'draw'))
        point = values['switchpoint'].values[:, idx]
        plt.vlines(dates[int(point[1])],
                   data['hospitalized'].min(), data['hospitalized'].max(), color='C1')

        plt.fill_betweenx(
            y=[data['hospitalized'].min(), data['hospitalized'].max()],
            x1=dates[int(point[0])],
            x2=dates[int(point[2])],
            alpha=0.5,
            color="C1",
        )

    plt.xticks(plot_dates)
    plt.ylabel('Weekly number of admissions', fontsize='large')
    plt.xlabel('Week', fontsize='large')

    fontsize = 'medium'
    plt.legend(loc='upper left', fontsize=fontsize)

def plot_daily_pD_training(data, start_date, end_date):
    posterior_quantile = np.percentile(data['deaths_estimated'], [2.5, 25, 50, 75, 97.5], axis=1)

    dates = pd.date_range(start_date, end_date).strftime('%m-%d')
    plot_dates = [dates[i] for i in range(0, len(posterior_quantile[2, :]), 21)]

    plt.figure()
    plt.plot(
        dates, posterior_quantile[2, :],
        color='b', label='posterior median', lw=2
    )

    plt.fill_between(
        dates, posterior_quantile[0, :], posterior_quantile[4, :],
        color='b', label='95% quantile', alpha=.2
    )

    plt.plot(
        dates, data['deaths_observed'],
        '--o', color='k', markersize=3,
        label='Observed admissions', alpha=.8
    )

    plt.xticks(plot_dates)
    plt.ylabel('Daily number of deaths', fontsize='large')
    plt.xlabel('Day', fontsize='large')

    fontsize = 'medium'
    plt.legend(loc='upper left', fontsize=fontsize)


def plot_deaths_switchpoints(data, start_date, end_date, trace, n_switchpoints):
    posterior_quantile = np.percentile(data['deaths_estimated'], [2.5, 25, 50, 75, 97.5], axis=1)

    dates = pd.date_range(start_date, end_date).strftime('%y-%m-%d')
    plot_dates = [dates[i] for i in range(0, len(posterior_quantile[2, :]), 21)]

    plt.figure()
    # Data
    plt.plot(
        dates, posterior_quantile[2, :],
        color='b', label='posterior median', lw=2
    )

    plt.fill_between(
        dates, posterior_quantile[0, :], posterior_quantile[4, :],
        color='b', label='95% quantile', alpha=.2
    )

    plt.plot(
        dates, data['deaths_observed'], '.',
        alpha=0.6, markersize=3, label='Observed admissions')

    # Switchpoints with CI
    for idx in range(n_switchpoints):
        values = trace.posterior.quantile((.025, .5, .975), dim=('chain', 'draw'))
        point = values['switchpoint'].values[:, idx]
        plt.vlines(dates[int(point[1])],
                   data['deaths_observed'].min(), data['deaths_observed'].max(), color='C1')

        plt.fill_betweenx(
            y=[data['deaths_observed'].min(), data['deaths_observed'].max()],
            x1=dates[int(point[0])],
            x2=dates[int(point[2])],
            alpha=0.5,
            color="C1",
        )

    plt.xticks(plot_dates)
    plt.ylabel('Daily number of deaths', fontsize='large')
    plt.xlabel('Day', fontsize='large')

    fontsize = 'medium'
    plt.legend(loc='upper left', fontsize=fontsize)
