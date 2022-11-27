import pandas
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from portfolio import Portfolio
plt.style.use('seaborn-whitegrid')

tamid = {'FTAI': ['2021-02-01', False],
        'AMT': ['2021-02-01', False],
        'NEE': ['2020-10-01', False],
        'TDOC': ['2020-10-01', False],
        'INTC': ['2020-10-01', False],
        'FISV': ['2020-10-01', False],
        'DAL': ['2021-02-01', False],
        'ISRG': ['2021-02-01', False],
        'GOOS': ['2021-02-01', False],
        'TXN': ['2021-02-01', False],
        'TSM': ['2021-10-01', False],
        'MHK': ['2021-10-01', False],
        'ACLS': ['2021-10-01', False],
        'EPD': ['2021-10-01', False],
        'PLYM': ['2021-10-01', False],
        'ED': ['2022-04-01', True]
         }

st.set_option('deprecation.showPyplotGlobalUse', False)

st.markdown("<h1 style='text-align: center; color: #40b6e4;'> TAMID at Miami's Portfolio Tracker </h1>",
            unsafe_allow_html=True
            )

TAMID = Portfolio(tamid)
cum_rets = ((1+TAMID.portfolio).cumprod() - 1) * 100
mvo_cum_rets = ((1+TAMID.mvo).cumprod() - 1) * 100
spx_rets = ((1+TAMID.spx).cumprod() - 1) * 100

with st.sidebar:
    with st.markdown("Hello"):
        st.markdown("<h1 style='text-align: center; color: #40b6e4;'> TAMID at Miami </h1> <br>",
                    unsafe_allow_html=True
                    )
    with st.markdown("Hello"):
        st.write(
            "This web application features TAMID at Miami's portfolio of stock "
            "pitches, dating back to the fall of 2020. The new Quant Group embarked on this project, under direction "
            "from the Director of Fund (Marcus Stevens), so that the members of TAMID (especially those from the fund) "
            "can get some real time feedback on the fruits of their labor."
        )

    with st.markdown("Hello"):
        st.markdown("<br>",
                    unsafe_allow_html=True
                    )

    with st.expander("See stocks"):
        with st.markdown("Hello"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("Name")
                for val in TAMID.stocks:
                        st.write(f"{val.name}")

            with col2:
                st.write("Date Added")
                for val in TAMID.stocks:
                        st.write(f"{val.date}")

            with col3:
                st.write("Bet")
                for val in TAMID.stocks:
                        st.write(f"{'Short' if val.short == True else 'Long'}")


st.write(f"Firstly, let's take a look at our portfolio's value since its creation in October 2020. Our PnL since "
         f"inception, using a naive implementation is **{round(cum_rets.portfolio_returns[-1], 2)}**%, whereas our"
         f" optimized (MVO) portfolio returned **{round(mvo_cum_rets.portfolio_returns[-1], 2)}**%. Below shows the "
         f"day-over-day change of the portfolio's value, in addition to an underwater/drawdown plot which shows the"
         f" periods in which the portfolio's returns were negative from a local maxima")

difference = cum_rets.portfolio_returns[-2] - cum_rets.portfolio_returns[-1]
delta = -1*round(difference, 2) if (cum_rets.portfolio_returns[-2] < 0 and cum_rets.portfolio_returns[-1] < 0) \
        else round(difference, 2)

mvo_difference = mvo_cum_rets.portfolio_returns[-2] - mvo_cum_rets.portfolio_returns[-1]
mvo_delta = -1*round(mvo_difference, 2) if (mvo_cum_rets.portfolio_returns[-2] < 0 and
                                            mvo_cum_rets.portfolio_returns[-1] < 0) else round(mvo_difference, 2)

col1, col2, col3, col4 = st.columns(4)
col2.metric(label="Naive Portfolio", value=f"{round(cum_rets.portfolio_returns[-1], 2)}%",
          delta=f"{delta}%")

col3.metric(label="MVO Portfolio", value=f"{round(mvo_cum_rets.portfolio_returns[-1], 2)}%",
          delta=f"{mvo_delta}%")

plt.figure(figsize=(12, 8))
plt.plot(cum_rets)
plt.plot(mvo_cum_rets)
plt.plot(spx_rets)
plt.title("TAMID's Cumulative Returns")
plt.xlabel('Date')
plt.ylabel('Returns (%)')
plt.legend(["Naive Portfolio", "MVO Portfolio", "S&P500"], bbox_to_anchor=(1, 1))
plt.tight_layout()
st.pyplot()

plt.plot(TAMID.drawdown, color='red', linewidth=0.8)
plt.plot(TAMID.mvo_dd, color='b', linewidth=0.8)
plt.title("TAMID's Drawdowns")
plt.xlabel('Date')
plt.ylabel('Returns (%)')
plt.fill_between(TAMID.drawdown.index, TAMID.drawdown.portfolio_returns, color='r', alpha=0.4)
plt.fill_between(TAMID.mvo_dd.index, TAMID.mvo_dd.portfolio_returns, color='b', alpha=0.4)
plt.legend(["Naive Portfolio", "MVO"], loc="lower left")
plt.tight_layout()
st.pyplot()

st.write(f"Next up, we have the portfolio's rolling standard deviation. The standard deviation (annualized) of the a"
         f" portfolio is typically referred to as its volatility")

vol = TAMID.vol * 100
mvo_vol = TAMID.mvo_vol * 100
# spx_vol = TAMID.spx.rolling(TAMID.window).std().dropna() * np.sqrt(252) * 100
# plt.figure(figsize=(12, 8))
plt.plot(vol)
plt.plot(mvo_vol)
# plt.plot(spx_vol)
plt.title("TAMID's Rolling Volatilty")
plt.xlabel('Date')
plt.ylabel('Volatility (%)')
plt.legend(["Naive", "MVO"], bbox_to_anchor=(1, 1))
plt.tight_layout()
st.pyplot()

st.write(f"We will now look at the rolling beta of the portfolio. Simply put, beta measures how volatile a stock is, "
         f"relative to the market. A stock with a beta of 1 will move in tandem with the market (S&P500), "
         f"since the market itself has a beta of one")
# plt.figure(figsize=(12, 8))
plt.plot(TAMID.beta)
plt.plot(TAMID.mvo_beta)
plt.plot(TAMID.spx_beta)
plt.title("TAMID's Rolling Beta")
plt.xlabel('Date')
plt.ylabel('Beta')
plt.legend(["Naive", "MVO", "S&P500"], bbox_to_anchor=(1, 1))
plt.tight_layout()
st.pyplot()

st.markdown("<h2 style='text-align: center; color: #40b6e4;'> Profitability Metrics </h2>",
            unsafe_allow_html=True
            )

st.write("Sharpe Ratio is known as the risk adjusted returns. It measures the returns in excess of the risk-free rate"
         " per unit of risk")

plt.plot(TAMID.sharpe_ratio)
plt.plot(TAMID.mvo_sharpe)
plt.title("TAMID's Rolling Sharpe Ratio")
plt.xlabel('Date')
plt.ylabel('Sharpe Ratio')
plt.legend(["Naive Sharpe Ratio", "MVO Sharpe Ratio"], bbox_to_anchor=(1, 1))
plt.tight_layout()
st.pyplot()

st.write("The Information ratio is similar to the Sharpe Ratio, but it measures excess returns beyond that of "
         "a specified benchmark (eg the S&P) instead of the risk-free rate")

plt.plot(TAMID.info_ratio)
plt.title("TAMID's Rolling Information Ratio")
plt.xlabel('Date')
plt.ylabel('Information Ratio')
plt.legend(["Information Ratio"], bbox_to_anchor=(1, 1))
plt.tight_layout()
st.pyplot()

st.markdown("<h2 style='text-align: center; color: #40b6e4;'> Risk Management Metrics </h2>",
            unsafe_allow_html=True
            )

st.write(f"VaR (Value at Risk) measures the amount of potential loss that could happen in an investment portfolio over"
         f" a specified period of time (ie the risk). For example, if the 95% one-month VaR is 1 million, there is "
         f"95% confidence that over the next month the portfolio will not lose more than 1 million. The daily VaR of "
         f"the TAMID portfolio is **{round(TAMID.var * 100, 2)}**%")

st.write(f"CVaR (aka Expected Shortfall) quantifies the amount of tail risk an investment portfolio has. CVaR is"
         f" derived by taking a weighted average of the “extreme” losses in the tail of the distribution of possible"
         f" returns, beyond the value at risk (VaR) cutoff point. For example, a one-day 95% CVaR of 1 million means"
         f" that the expected loss of the worst 5% scenarios over a one-day period is 1 million. The daily CVaR of"
         f" the TAMID portfolio is **{round(TAMID.cvar * 100, 2)}**%")


TAMID.plot_var(TAMID.portfolio, TAMID.var, TAMID.cvar, None)
st.pyplot()

# TAMID.plot_var(TAMID.mvo, TAMID.mvo_var, TAMID.mvo_cvar, "MVO")
# st.pyplot()
