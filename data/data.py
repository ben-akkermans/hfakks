
import os
import numpy as np
import pandas as pd

from datetime import datetime

import yfinance as yf



class dataManager:
    def __init__(self):
        self.headers = []

    def getPrices(self, tickers=[], start_date="2020-01-01", end_date=None):

        if end_date is None:
            end_date = datetime.today()

        # Fetch historical price data for the specified stocks
        data = yf.download(tickers, start=start_date, end=end_date)

        return data
