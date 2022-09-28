import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

st.markdown("<p style='font-size: 20px;'> This web application features the TAMID at Miami's portfolio of stock "
            "pitches, dating back to the fall of 2020. The new Quant Group embarked on this project, under direction "
            "from the Director of Fund (Marcus Stevens), so that the members of TAMID (especially those from the fund) "
            "can get some real time feedback on the fruits of their labor. </p>"
            "<br>"
            "<p style='font-size: 20px;'>Hello, I'm gonna add the rest of the graphs VERY soon</p>",
            unsafe_allow_html=True
            )

TAMID = Portfolio(tamid)

plt.figure(figsize=(12, 8))
plt.plot((1+TAMID.portfolio).cumprod())
plt.title("TAMID's Cumulative Returns")
plt.xlabel('Date')
plt.ylabel('Returns (%)')
plt.legend("Returns")
# plt.tight_layout()
st.pyplot()
