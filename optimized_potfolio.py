import pandas as pd
import numpy as np
from scipy.optimize import minimize
from matplotlib import rcParams
rcParams['figure.figsize'] = 12, 10

TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.04


class MVO:
    def __init__(self, log_returns):
        self.log_rets = log_returns
        self.cols = None

    def check_sum(self, weight):
        return np.sum(weight) - 1

    def get_ret_vol_sr(self, weight, cols):
        weights = np.array(weight)
        ret = np.sum(self.log_rets.loc[:, cols].mean() * weights) * TRADING_DAYS_PER_YEAR
        vol = np.sqrt(np.dot(weights.T, np.dot(self.log_rets.loc[:, cols].cov() * TRADING_DAYS_PER_YEAR, weights)))
        sr = (ret - (RISK_FREE_RATE/TRADING_DAYS_PER_YEAR)) / vol
        return np.array([ret, vol, sr])

    def neg_sharpe(self, weight, cols):
        return self.get_ret_vol_sr(weight, cols)[2] * -1

    def opt_port(self):
        cons = ({'type': 'eq', 'fun': self.check_sum})
        index = self.log_rets.index
        portfolio_val = []
        prev = 0

        for row in range(1, len(self.log_rets)):
            vals = []
            cols = []

            for col in self.log_rets.columns:
                val = self.log_rets[col][index[row]]
                if not (pd.isna(val)):
                    vals.append(val)
                    cols.append(col)

            init_guess = weights.x if prev == len(cols) else [1 / len(cols) for _ in range(len(cols))]
            bounds = [(0, 1) for _ in range(len(cols))]
            weights = minimize(self.neg_sharpe, init_guess, cols, method='SLSQP', bounds=bounds, constraints=cons)
            port_val = round(np.dot(vals, weights.x), 4)
            portfolio_val.append(port_val)
            prev = len(cols)

        return pd.DataFrame(portfolio_val, columns=["portfolio_returns"], index=index[1:])