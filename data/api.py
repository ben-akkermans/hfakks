import os
import numpy as np
import pandas as pd
import investpy
import investiny as ip
import yfinance as yf

import investpy

class api:
    def __init__(self):
        self.headers = []

    def investpyStock(self):
        df = investpy.get_stock_historical_data(
            stock='MSFT',
            country='United States',
            from_date='01/01/2012',
            to_date='11/07/2022'
        )
        print(df.head())

    def investinyStock(self):
        from investiny import historical_data

        data = historical_data(investing_id=6408, from_date="09/01/2022",
                               to_date="10/01/2022")  # Returns AAPL historical data as JSON (without date)

        print(data)

# api = api()
#
# api.investpyStock()

msft = yf.Ticker("MSFT")
# get stock info

df = msft.history(period="1mo")

print(df)
