import yfinance as yf
import numpy as np
import pandas as pd

N_PORTFOLIOS = 100
N_DAYS = 252
RISKY_ASSETS = ['META', 'TSLA', 'TWTR', 'MSFT']
RISKY_ASSETS.sort()
START_DATE = '2018-01-01'
END_DATE = '2018-12-31'

def getReturns(tickers=RISKY_ASSETS,startDate=START_DATE, endDate=END_DATE):
    print(tickers)
    prices_df = yf.download(tickers, start=startDate,
                            end=endDate, adjusted=True)
    print(f'Downloaded {prices_df.shape[0]} rows of data.')

    returns_df = prices_df['Adj Close'].pct_change().dropna()
    return returns_df

def getEfficientFrontier(tickers, returns_df, n_portfolios=N_PORTFOLIOS):
    n_assets = len(tickers)
    avg_returns = returns_df.mean() * N_DAYS
    cov_mat = returns_df.cov() * N_DAYS
    np.random.seed(42)
    weights = np.random.random(size=(n_portfolios, n_assets))
    weights /=  np.sum(weights, axis=1)[:, np.newaxis]
    portf_rtns = np.dot(weights, avg_returns)

    portf_vol = []
    for i in range(0, len(weights)):
        portf_vol.append(np.sqrt(np.dot(weights[i].T,
                                        np.dot(cov_mat, weights[i]))))
    portf_vol = np.array(portf_vol)
    portf_sharpe_ratio = portf_rtns / portf_vol
    portf_results_df = pd.DataFrame({'retornos': portf_rtns,
                                 'volatilidade': portf_vol,
                                 'indice_de_sharpe': portf_sharpe_ratio})
    N_POINTS = 100
    portf_vol_ef = []
    indices_to_skip = []

    portf_rtns_ef = np.linspace(portf_results_df.retornos.min(),
                                portf_results_df.retornos.max(),
                                N_POINTS)
    portf_rtns_ef = np.round(portf_rtns_ef, 2)
    portf_rtns = np.round(portf_rtns, 2)

    for point_index in range(N_POINTS):
        if portf_rtns_ef[point_index] not in portf_rtns:
            indices_to_skip.append(point_index)
            continue
        matched_ind = np.where(portf_rtns == portf_rtns_ef[point_index])
        portf_vol_ef.append(np.min(portf_vol[matched_ind]))

    portf_rtns_ef = np.delete(portf_rtns_ef, indices_to_skip)

    max_sharpe_ind = np.argmax(portf_results_df.indice_de_sharpe)
    max_sharpe_portf = portf_results_df.loc[max_sharpe_ind]

    min_vol_ind = np.argmin(portf_results_df.volatilidade)
    min_vol_portf = portf_results_df.loc[min_vol_ind]

    return portf_results_df, portf_rtns_ef, portf_rtns, max_sharpe_portf, min_vol_portf, weights