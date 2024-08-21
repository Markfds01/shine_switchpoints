import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def plot_daily_pH_training(data, start_date, end_date,region = None):
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

    plt.savefig(f'plots/fit_{region}.png')


def plot_daily_switchpoints(data, start_date, end_date, trace, n_switchpoints,region = None):
    print('\n Im plotting switchpoints')
    posterior_quantile = np.percentile(data['admissions'], [2.5, 25, 50, 75, 97.5], axis=1)
    wave_labels = ['Before 2º wave', '2º wave', '3º wave', '4º wave']


    dates = pd.date_range(start_date, end_date).strftime('%y-%m-%d')
    plot_dates = [dates[i] for i in range(0, len(posterior_quantile[2, :]), 21)]

    plt.figure(figsize=(12, 10))
    # Data
    plt.plot(
        dates, posterior_quantile[2, :],
        color='#448FA3', label='posterior median', lw=3
    )

    plt.fill_between(
        dates, posterior_quantile[0, :], posterior_quantile[4, :],
        color='#68C5DB', label='95% quantile', alpha=.2
    )

    plt.plot(
        dates, data['hospitalized'], '.', color = '#02182B',
        alpha=0.6, markersize=4, label='Observed admissions')

    # Switchpoints with CI
    switchpoints = np.array([164, 257, 354])  # Fixed switchpoints

    for idx in range(n_switchpoints):
        x_position = dates[int(switchpoints[idx])]
        plt.vlines(x_position, data['hospitalized'].min(), posterior_quantile[4, :].max(), color='#42E2B8')
         # Determine the position to place the wave label
        if idx == 0:
            # For the first segment (before the first switchpoint)
            text_x_position = (0 + switchpoints[idx]) / 2
        else:
        # For subsequent segments
            text_x_position = (int(switchpoints[idx-1]) + switchpoints[idx]) / 2

        plt.text(text_x_position, posterior_quantile[4, :].max(), wave_labels[idx], 
             horizontalalignment='center', verticalalignment='bottom', fontsize=12, color='black',fontweight = 'bold')
        
    text_x_position = (int(switchpoints[len(switchpoints)-1]) + len(dates)) / 2

    plt.text(text_x_position, posterior_quantile[4, :].max(), wave_labels[len(switchpoints)], 
             horizontalalignment='center', verticalalignment='bottom', fontsize=12, color='black',fontweight = 'bold')

    plt.xticks(plot_dates, rotation = 45)
    plt.ylabel('Daily number of admissions', fontsize='large',fontweight = 'bold')
    plt.xlabel('Day', fontsize='large',fontweight = 'bold')

    fontsize = 'medium'
    plt.legend(loc='upper left', fontsize=fontsize)
     # Making spines bold
    for spine in plt.gca().spines.values():
        spine.set_linewidth(2)  # Adjust the width for desired boldness
    for label in plt.gca().get_xticklabels():
        label.set_fontweight('bold')
    for label in plt.gca().get_yticklabels():
        label.set_fontweight('bold')
    plt.savefig(f'plots/fit_{region}_fixed_switchpoints_dades.png')



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
