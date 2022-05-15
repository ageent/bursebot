import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression

class IntervalStrategyHeavy:
    def __init__(self):
        self.linreg = LinearRegression()
        self.coef_ = None
        self.reg_intercept_ = None

        self.bound_intercepts = ()

        self.data = pd.Series()
        self.time_step = pd.Timedelta("1")

    def fit(self, data, main_borders_quantiles=None, inner_bounds_num=None, broker_commission=0.003):
        """ Fit model.

        :param inner_bound_num:
        :param quantiles:
        :param data: time series of formate pd.Series({time: value})
        :return: self
        """
        if main_borders_quantiles is None:
            main_borders_quantiles = np.array([0.01, 0.1, 0.9, 0.99])

        data = data.sort_index()
        self.time_step = (data.index[1:] - data.index[:-1]).min()
        data_index = pd.date_range(data.index.min(), data.index.max(), freq=self.time_step)
        self.data = pd.Series(0, index=data_index)
        self.data[data.index] = data.values

        df = pd.DataFrame(data)
        df.rename({df.columns[0]: "target"}, inplace=True)
        df["x"] = np.arange(df.index.size)

        self.linreg.fit(df[["x"]], df.taget)
        self.coef_ = self.linreg.coef_[0]
        self.reg_intercept_ = self.linreg.intercept_

        df["no_trend"] = df.target - self.linreg.predict(df[["x"]])
        self.bound_intercepts = np.sort(df.no_trend.quantile(main_borders_quantiles).values)
        self._set_inner_bounds(df["no_trend"],
                               main_borders_quantiles,
                               inner_bounds_num,
                               broker_commission)
        return self

    def trade(self,current_values, fund, buyer, seller,
              auto_fit=True, diversification=(0.5, 0.5), missing_data=None, current_date=None):
        """ A method for a one-time buy or sell.

        :param fund:
        :param buyer: signature: (amount_to_buy) -> (buys_number, change_from_buying).
        The amount of_to_buy is the amount for which several items are bought
        :param seller: signature: (selling_items_number) -> (items_sold_number, total_revenue).
        _total_revenue_ is revenue minus commissions but without income tax.
        :param auto_fit:
        :param diversification:
        :return:
        """
        ...

    def add_data(self, missing_data):
        missing_data = missing_data[missing_data.index > self.data.index[-1]].sort_index()
        if not missing_data.empty:
            if not self._is_matching_step(missing_data):
                raise ValueError(
                    f"A step equal to {self.time_step} is not observed for the missing_data argument."
                )
            self.data = pd.concat([self.data, missing_data])
            return True
        return False

    def solve(self, current_values,
              missing_data=None, current_date=None):
        """Trade only on the main borders

        :param current_values: numpy.ndarray. Values after the last averaging for which the solution is calculated
        :param previous_step_value: the value in the previous step
        :return: "buy", "sell", "inaction"
        """
        if missing_data is not None:
            self.add_data(missing_data)

        if current_date is not None:
            next_date = self.data.index[-1] + self.time_step
            if (self.data.index[-1] != current_date) or (next_date != current_date):
                raise ValueError(
                    f"The current_date argument can only have values {self.data.index[-1]} and {next_date}."
                )
            self.data[current_date] = current_values.mean()

    def _set_inner_bounds(self, series_without_trend, main_borders_quantiles, inner_bounds_num, broker_commission):
        if inner_bounds_num is None:
            self._select_inner_bounds(series_without_trend, main_borders_quantiles, broker_commission)
        else:
            if inner_bounds_num == 0:
                inner_borders = []
            elif inner_bounds_num == 1:
                inner_borders = [self.reg_intercept_]
            else:
                inner_quantiles = np.linspace(main_borders_quantiles[1],
                                              main_borders_quantiles[2],
                                              inner_bounds_num + 2)[1:-1]
                inner_borders = series_without_trend.quantile(inner_quantiles).values

            self.bound_intercepts = np.sort(np.concatenate([inner_borders, self.bound_intercepts]))

    def _select_inner_bounds(self, series_without_trend, main_borders_quantiles, broker_commission):
        ...

    def _is_matching_step(self, data):
        full_series = pd.concat([self.data[[-1]], data])
        return ((full_series[1:] - full_series[:-1]) == self.time_step).all()

    def _line(self, x, bias=0):
        return self.coef_ * x + self.reg_intercept_ + bias