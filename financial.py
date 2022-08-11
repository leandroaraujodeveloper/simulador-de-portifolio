import yfinance as yf
import numpy as np
import pandas as pd

N_PORTFOLIOS = 10 # done
N_DAYS = 252 # todo
RISKY_ASSETS = ['FB', 'TSLA', 'TWTR', 'MSFT'] # todo
RISKY_ASSETS.sort()
START_DATE = '2018-01-01' # done
END_DATE = '2018-12-31' # done

def getReturns(startDate=START_DATE, endDate=END_DATE):
    

    prices_df = yf.download(RISKY_ASSETS, start=startDate, 
                            end=endDate, adjusted=True)
    print(f'Downloaded {prices_df.shape[0]} rows of data.')

    prices_df['Adj Close'].plot(title='Stock prices of the considered assets');

    returns_df = prices_df['Adj Close'].pct_change().dropna()
    return returns_df
    
def getEfficientFrontier(returns_df, n_portfolios=N_PORTFOLIOS):
    n_assets = len(RISKY_ASSETS)
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
    return portf_results_df