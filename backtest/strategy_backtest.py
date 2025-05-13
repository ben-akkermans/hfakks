import sys
sys.path.append('src')

import os
import numpy as np
import pandas as pd
from datetime import datetime
import math
import matplotlib.pyplot as plt

import yfinance as yf

from data.data import DataManager

dm = DataManager()

class strategyBacktester:
    def __init__(self, tickers, start_date, end_date=None):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date

    def get_prices_returns(self):
        self.prices = dm.get_prices(self.tickers, self.start_date, self.end_date)
        self.close_df = self.prices.xs('Adj Close',axis=1,level=0).loc[self.start_date:self.end_date]
        self.pct_returns = self.close_df.pct_change()
        self.log_returns = np.log(self.close_df / self.close_df.shift(1)).fillna(0)

    def set_weights(self, signal):
        self.weights = signal.loc[self.start_date:self.end_date]

    def calc_strat_returns(self):
        self.strategy_returns = pd.DataFrame(index=self.weights.index)

        self.asset_pct_rets = self.weights * self.pct_returns
        self.asset_log_rets = self.weights * self.log_returns

        self.strategy_rets = self.asset_pct_rets.sum(axis=1)
        self.strategy_log_rets = np.log(1 + self.strategy_rets)
        self.strategy_cum_rets = self.strategy_log_rets.cumsum()

    def calculate_stats(self):
        # Annualization factor assuming daily data (252 trading days)
        ann_factor = np.sqrt(252)

        # Calculate relevant stats
        total_return = np.exp(self.strategy_cum_rets.iloc[-1]) - 1
        annualized_return = np.exp(self.strategy_log_rets.mean() * 252) - 1
        volatility = self.strategy_log_rets.std() * ann_factor
        sharpe_ratio = (self.strategy_log_rets.mean() / self.strategy_log_rets.std()) * ann_factor
        max_drawdown = self.calculate_max_drawdown(self.strategy_cum_rets)
        value_at_risk = np.percentile(self.strategy_log_rets, 5)
        conditional_var = self.strategy_log_rets[self.strategy_log_rets <= value_at_risk].mean()
        skewness = self.strategy_log_rets.skew()

        # Create a stats DataFrame
        stats = pd.DataFrame({
            'Total Return': [total_return],
            'Annualized Return': [annualized_return],
            'Volatility': [volatility],
            'Sharpe Ratio': [sharpe_ratio],
            'Max Drawdown': [max_drawdown],
            'Value at Risk (5%)': [value_at_risk],
            'Conditional VaR (5%)': [conditional_var],
            'Skewness': [skewness]
        })

        print("\nBacktest Statistics:")
        print(stats.to_string(index=False))

    def calculate_max_drawdown(self, cum_rets):
        cum_max = cum_rets.cummax()
        drawdown = cum_rets - cum_max
        max_drawdown = drawdown.min()
        return max_drawdown

    def plot_results(self):
        # Cumulative return plot
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))

        # Plot cumulative return
        axs[0, 0].plot(self.strategy_cum_rets, label='Cumulative Return')
        axs[0, 0].set_title('Cumulative Return')
        axs[0, 0].legend()

        # Plot rolling 3-month Sharpe Ratio (Information Ratio)
        rolling_ir = self.strategy_log_rets.rolling(63).mean() / self.strategy_log_rets.rolling(63).std()
        axs[0, 1].plot(rolling_ir, label='Rolling 3-Month IR')
        axs[0, 1].set_title('Rolling 3-Month Information Ratio')
        axs[0, 1].legend()

        # Plot return by asset
        axs[1, 0].plot(self.asset_pct_rets.cumsum(), label=self.tickers)
        axs[1, 0].set_title('Return by Asset')
        axs[1, 0].legend()

        # Plot drawdown
        cum_max = self.strategy_cum_rets.cummax()
        drawdown = self.strategy_cum_rets - cum_max
        axs[1, 1].plot(drawdown, label='Drawdown')
        axs[1, 1].set_title('Drawdown')
        axs[1, 1].legend()

        plt.tight_layout()
        plt.show()

    def run_backtest(self):
        # Perform the full backtest
        self.get_prices_returns()
        self.calc_strat_returns()
        self.calculate_stats()  # Calculate and print backtest statistics
        self.plot_results()  # Plot the results



