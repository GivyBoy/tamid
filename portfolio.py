import threading
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import statsmodels.api as sm
import matplotlib.pyplot as plt
from optimized_potfolio import MVO
from dataclasses import dataclass

TRADING_DAYS_PER_YEAR = 252

@dataclass()
class stock:
    name: str
    date: str
    short: bool


class ReturnValueThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    def run(self):
        if self._target is None:
            return  # could alternatively raise an exception, depends on the use case
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as exc:
            print(f'{type(exc).__name__}: {exc}', file=sys.stderr)  # properly handle the exception

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self.result


class Portfolio:

    def __init__(self, stocks):

        self.rate = 0.04
        self.window = 14
        self.alpha = 0.95
        self.scalar = 0.25
        self.spx = yf.download("^GSPC", '2020-10-01')[["Adj Close"]]
        self.spx = self.spx.pct_change()
        self.spx *= self._vol_scalar(self.scalar, self.spx)
        self.stocks = []

        for val in stocks:
            val = stock(val, stocks[val][0], stocks[val][1])
            self.stocks.append(val)

        thread = ReturnValueThread(target=self._get_data)
        thread.start()
        self.data = thread.join()
        self.rets = self.data.pct_change()
        # self.rets = np.log(1+self.rets)
        self.mvo = MVO(self.rets).opt_port()
        self.mvo *= self._vol_scalar(self.scalar, self.mvo)
        self._short()
        self.portfolio = self._create_portfolio()
        self.portfolio *= self._vol_scalar(self.scalar, self.portfolio)
        self.drawdown = self._drawdown(self.portfolio)
        self.mvo_dd = self._drawdown(self.mvo)
        self.rolling_sharpe_ratio = self._rolling_sharpe_ratio(self.portfolio)
        self.rolling_mvo_sharpe = self._rolling_sharpe_ratio(self.mvo)
        self.sharpe_ratio = self._sharpe_ratio(self.portfolio.portfolio_returns)
        self.mvo_sharpe_ratio = self._sharpe_ratio(self.mvo.portfolio_returns)
        self.sortino_ratio = self._sortino_ratio(self.portfolio.portfolio_returns)
        self.mvo_sortino_ratio = self._sortino_ratio(self.mvo.portfolio_returns)
        self.alpha_regressions = self._alpha_regressions(self.spx["Adj Close"], self.mvo.portfolio_returns)
        self.beta = self._get_beta(self.portfolio)
        self.mvo_beta = self._get_beta(self.mvo)
        self.spx_beta = self._get_beta(self.spx)
        self.info_ratio = self._info_ratio()
        self.vol = self._vol(self.portfolio)
        self.mvo_vol = self._vol(self.mvo)
        self.var = self._var(self.portfolio)
        self.mvo_var = self._var(self.mvo)
        self.cvar = self._cvar(self.portfolio)
        self.mvo_cvar = self._cvar(self.mvo)

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

    def _get_beta(self, returns):
        r = returns.copy()
        r['spx'] = self.spx['Adj Close']

        cov = r.rolling(self.window).cov().unstack()[r.columns[0]]['spx']
        cov = cov.to_frame('portfolio_returns').dropna()
        var = self.spx.rolling(self.window).var().dropna()

        betas = cov.portfolio_returns / var['Adj Close']
        betas = betas.to_frame('betas')

        return betas

    def _drawdown(self, returns):

        wealth_index = (1+returns).cumprod()
        previous_peaks = wealth_index.cummax()

        return (wealth_index - previous_peaks)/previous_peaks

    def _rolling_sharpe_ratio(self, returns):

        vol = self._vol(returns)
        mean_rets = returns.rolling(self.window).mean()

        return ((mean_rets) / vol) * np.sqrt(TRADING_DAYS_PER_YEAR)

    # def sortino_ratio(self, portfolio, rate=0.03):
    #
    #     vol = self.vol(portfolio[portfolio < 0]) * np.sqrt(252)
    #     mean_rets = portfolio.rolling(14).mean()
    #
    #     return (mean_rets - rate) / vol

    def _sharpe_ratio(self, strategy_returns: pd.Series) -> float:
        """ Compute annualized Sharpe Ratio for any strategy or security time-series of daily returns.

        Args:
            strategy_returns (pd.Series): time-series of daily returns.

        Returns:
            float: annualized Sharpe Ratio.
        """

        return strategy_returns.mean() / strategy_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    def _sortino_ratio(self, strategy_returns: pd.Series) -> float:
        """ Compute annualized Sortino Ratio for any strategy or security time-series of daily returns.
            This is the Sharpe Ratio, but with downside returns volatility.

        Args:
            strategy_returns (pd.Series): time-series of daily returns.

        Returns:
            float: annualized Sharpe Ratio.
        """

        return strategy_returns.mean() / strategy_returns[strategy_returns < 0].std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    def _alpha_regressions(self, benchmark_returns: pd.Series, strategy_returns: pd.Series) -> pd.Series:

        benchmark_returns = benchmark_returns.dropna()
        strategy_returns = strategy_returns.dropna()

        benchmark_returns.name = "SPY"
        strategy_returns.name = "MVO"

        indices = benchmark_returns.index.intersection(strategy_returns.index)

        benchmark_returns = benchmark_returns.loc[indices]
        strategy_returns = strategy_returns.loc[indices]

        # Add constant to benchmark returns
        benchmark_returns_const = sm.add_constant(benchmark_returns)

        # Construct OLS regression
        model = sm.OLS(strategy_returns, benchmark_returns_const)
        reg = model.fit()

        # ------------------------------ Store regression data in summary DataFrame ------------------------------

        reg_summary = pd.DataFrame({f'{strategy_returns.name} ~ {benchmark_returns.name}':
            {
                'Portfolio Alpha': reg.params[0]*252,
                'Alpha T-Stat': reg.tvalues[0],
                'Portfolio Beta': reg.params[1],
                'Beta T-Stat': reg.tvalues[1]
            }
        })

        reg_summary = reg_summary.reindex(index=['Portfolio Alpha', 'Alpha T-Stat', 'Portfolio Beta', 'Beta T-Stat'])

        return reg_summary

    def _info_ratio(self):

        spx_rets = self.spx["Adj Close"].rolling(self.window).mean()
        mean_rets = self.portfolio.portfolio_returns.rolling(self.window).mean()
        difference = mean_rets - spx_rets
        vol = difference.rolling(self.window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)

        return difference / vol

    def _vol(self, returns):
        return returns.rolling(self.window).std().dropna() * np.sqrt(TRADING_DAYS_PER_YEAR)

    def _var(self, returns):
        return np.percentile(returns, 100 * (1 - self.alpha))

    def _cvar(self, returns):
        # Call out to our existing function
        var = self._var(returns)
        val = self.portfolio.copy().fillna(0.0)

        return np.nanmean(returns[val < var])

    def _vol_scalar(self, scalar: int, returns: pd.DataFrame):
        return scalar/(returns.std()*np.sqrt(TRADING_DAYS_PER_YEAR))

    def plot_var(self, returns, var, cvar, title: str):

        # Plot only the observations > VaR on the main histogram so the plot comes out
        # nicely and doesn't overlap.
        plt.figure(figsize=(14, 8))
        plt.hist(returns[returns > var], bins=20)
        plt.hist(returns[returns < var], bins=10)
        plt.axvline(var, color='red', linestyle='solid')
        plt.axvline(cvar, color='red', linestyle='dashed')
        plt.legend(['VaR for Specified Alpha as a Return',
                    'CVaR for Specified Alpha as a Return',
                    'Historical Returns Distribution',
                    'Returns < VaR'])
        if title:
            plt.title(f'{title} Historical VaR and CVaR')
        else:
            plt.title(f'Historical VaR and CVaR')
        plt.xlabel('Return')
        plt.ylabel('Observation Frequency')

