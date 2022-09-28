import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import yfinance as yf
import streamlit as st
from datetime import datetime
from portfolio import Portfolio


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
        'PLYM': ['2021-10-01', False]
         }

st.set_option('deprecation.showPyplotGlobalUse', False)

st.markdown("<h1 style='text-align: center; color: #40b6e4;'> TAMID at Miami Portfolio Tracker </h1>",
            unsafe_allow_html=True
            )

st.markdown("<p style='font-size: 18px;'> This web application features the TAMID at Miami's portfolio of stock "
            "pitches, dating back to the fall of 2020. The new Quant Group embarked on this project, under direction "
            "from the Director of Fund (Marcus Stevens), so that the members of TAMID (especially those from the fund) "
            "can get some real time feedback on the fruits of their labor. </p>"
            "<br>"
            "<p style='font-size: 18px;'>Hello, I'm gonna add the rest of the graphs VERY soon</p>",
            unsafe_allow_html=True
            )

with st.spinner("Loading..."):
    time.sleep(10)

TAMID = Portfolio(tamid)
cum_rets = ((1+TAMID.portfolio).cumprod() - 1) * 100

with st.sidebar:
    with st.markdown("Hello"):
        st.write("Our portfolio consists of: ")
        # for val in TAMID.stocks:
        #     st.write(f"Ticker: {val.name}; Date added: {val.date}; Short: {'Yes' if val.short == True else 'No'}")

st.write(f"Firstly, let's take a look at our portfolio's value since its creation in October 2020. Our PnL since "
         f"inception  is **{round(cum_rets.portfolio_returns[-1], 2)}**%. Below shows the day-over-day change of the"
         f" portfolio's value")

difference = cum_rets.portfolio_returns[-2] - cum_rets.portfolio_returns[-1]
delta = -1*round(difference, 2) if (cum_rets.portfolio_returns[-2] < 0 and cum_rets.portfolio_returns[-1] < 0) \
        else round(difference, 2)
st.metric(label="Portfolio DoD Change", value=f"{round(cum_rets.portfolio_returns[-1], 2)}%",
          delta=f"{delta}%")

plt.figure(figsize=(12, 8))
plt.plot(cum_rets)
plt.title("TAMID's Cumulative Returns")
plt.xlabel('Date')
plt.ylabel('Returns (%)')
plt.legend(["Portfolio Returns"], bbox_to_anchor=(1, 1))
plt.tight_layout()
st.pyplot()
