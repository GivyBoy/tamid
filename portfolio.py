import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

from dataclasses import dataclass


@dataclass()
class stock:
    name: str
    date: str
    short: False


class Portfolio:

    def __init__(self, stocks):

        self.rate = 0.03
        self.window = 14
        self.alpha = 0.95
        self.spx = yf.download("^GSPC", '2020-10-01')[["Adj Close"]]
        self.spx = self.spx.pct_change().dropna()
        self.stocks = []

        for val in stocks:
            val = stock(val, stocks[val][0], stocks[val][1])
            self.stocks.append(val)

        self.rets = self._get_data().pct_change()
        self._short()
        self.portfolio = self._create_portfolio()
        self.drawdown = self._drawdown()
        self.sharpe_ratio = self._sharpe_ratio()
        self.beta = self._get_beta()
        self.info_ratio = self._info_ratio()
        self.vol = self._vol()
        self.var = self._var()
        self.cvar = self._cvar()

    def _get_data(self) -> pd.DataFrame:
        for idx, val in enumerate(self.stocks):

            if idx == 0:
                data = yf.download(val.name, val.date)[["Adj Close"]]
            else:
                stock_data = yf.download(val.name, val.date)[["Adj Close"]]
                data = pd.concat([data, stock_data], axis=1)

        data.columns = [f"{val.name.upper()}" for idx, val in enumerate(self.stocks)]

        return data

    def _short(self):

        for val in self.stocks:
            if val.short:
                self.rets[val.name] *= -1

    def _create_portfolio(self) -> pd.DataFrame:

        index = self.rets.index
        portfolio_val = []

        for i in range(1, len(self.rets)):
            vals = []

            for j in self.rets.columns:
                val = self.rets[j][index[i]]
                if not (pd.isna(val)):
                    vals.append(val)

            weights = [1 / len(vals) for _ in vals]
            port_val = round(np.dot(vals, weights), 4)
            portfolio_val.append(port_val)

        portfolio = pd.DataFrame(portfolio_val, columns=["portfolio_returns"], index=index[1:])

        return portfolio

    def _get_beta(self):
        r = self.portfolio.copy()
        r['spx'] = self.spx['Adj Close']

        cov = r.rolling(self.window).cov().unstack()[self.portfolio.columns[0]]['spx']
        cov = cov.to_frame('portfolio_returns').dropna()
        var = self.spx.rolling(self.window).var().dropna()

        betas = cov.portfolio_returns / var['Adj Close']
        betas = betas.to_frame('betas')

        return betas

    def _drawdown(self):

        wealth_index = (1+self.portfolio).cumprod()
        previous_peaks = wealth_index.cummax()
        # drawdown = (wealth_index - previous_peaks)/previous_peaks

        return (wealth_index - previous_peaks)/previous_peaks

    def _sharpe_ratio(self):

        vol = self._vol()
        mean_rets = self.portfolio.rolling(self.window).mean()

        return (mean_rets - self.rate) / vol

    # def sortino_ratio(self, portfolio, rate=0.03):
    #
    #     vol = self.vol(portfolio[portfolio < 0]) * np.sqrt(252)
    #     mean_rets = portfolio.rolling(14).mean()
    #
    #     return (mean_rets - rate) / vol

    def _info_ratio(self):

        spx_rets = self.spx["Adj Close"].rolling(self.window).mean()
        mean_rets = self.portfolio.portfolio_returns.rolling(self.window).mean()
        difference = mean_rets - spx_rets
        vol = difference.rolling(self.window).std() * np.sqrt(252)

        return difference / vol

    def _vol(self):
        return self.portfolio.rolling(self.window).std().dropna() * np.sqrt(252)

    def _var(self):
        return np.percentile(self.portfolio, 100 * (1 - self.alpha))

    def _cvar(self):
        # Call out to our existing function
        var = self._var()
        returns = self.portfolio.copy().fillna(0.0)

        return np.nanmean(returns[returns < var])

    def _plot_var(self):

        # Plot only the observations > VaR on the main histogram so the plot comes out
        # nicely and doesn't overlap.
        plt.figure(figsize=(14, 8))
        plt.hist(self.portfolio[self.portfolio > self.var], bins=20)
        plt.hist(self.portfolio[self.portfolio < self.var], bins=10)
        plt.axvline(self.var, color='red', linestyle='solid')
        plt.axvline(self.cvar, color='red', linestyle='dashed')
        plt.legend(['VaR for Specified Alpha as a Return',
                    'CVaR for Specified Alpha as a Return',
                    'Historical Returns Distribution',
                    'Returns < VaR'])
        plt.title('Historical VaR and CVaR')
        plt.xlabel('Return')
        plt.ylabel('Observation Frequency')

