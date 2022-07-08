import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression


class IntervalStrategyHeavy(BaseEstimator):
    def __init__(self):
        self.linreg = LinearRegression()
        self.coef_: float
        self.reg_intercept_: float

        self.bound_intercepts: np.ndarray

        self.data: pd.Series
        self.earliest_date: pd.Timestamp  # parameter for unloading
        self.time_step: pd.Timedelta

        self.diversification: list
        self.trader: Trader

    def fit(self, data,
            diversification=None, main_bounds_quantiles=None, inner_bounds_num=1):
        """ Fit model.

        :param main_bounds_quantiles: 1-dimensional array-like
        :param diversification: 1-dimensional array-like. If None auto.
        :param inner_bound_num:
        :param quantiles:
        :param data: time series of formate pd.Series({time: value})
        :return: self
        """
        if inner_bounds_num is None or inner_bounds_num > 1:
            raise ValueError(f"{inner_bounds_num=} not supported yet. Recommended 1.")


        if diversification is not None:
            if sum(diversification) != 1:
                raise ValueError(
                    "The elements of the diversification argument must be equal to one in total."
                )

        if main_bounds_quantiles is None:
            main_bounds_quantiles = np.array([0.01, 0.1, 0.9, 0.99])
        else:
            main_bounds_quantiles = np.array(main_bounds_quantiles)
        if (main_bounds_quantiles > 1).any():
            raise ValueError(
                "All elements of the argument main_bounds_quantiles must be no more than one."
            )

        data = data.sort_index()
        self.earliest_date = data.index[0]
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
        self.bound_intercepts = np.sort(df.no_trend.quantile(main_bounds_quantiles).values)
        self._set_inner_bounds(df["no_trend"],
                               main_bounds_quantiles,
                               inner_bounds_num)

        if diversification is None:
            if self.coef_ < 0:
                diversification = [0.66, 0.34]
            else:
                diversification = [1]
        else:
            diversification = list(diversification)

        self.diversification = diversification
        self.trader = Trader(diversification_stack=reversed(diversification))
        return self

    def trade(self, current_values, trading_limit, buyer, seller,
              auto_fit=False, missing_data=None, current_date=None) -> float:
        """ A method for a one-time buy or sell.

        :param current_values: numpy.ndarray.
        Values with maximum discretization after the last averaging for which the solution is calculated
        :param trading_limit:
        :param buyer: signature: (amount_to_buy) -> (buys_number, amount_spent_with_commission).
        The amount_to_buy is the amount for which several items are bought (with commission)
        :param seller: signature: (selling_items_number) -> total_revenue.
        selling_items_number is number or None if you need to sell everything
        total_revenue is revenue minus commissions by selling but without income tax.
        :param auto_fit:
        :return:
        """
        if auto_fit:
            raise ValueError(f"{auto_fit=} not supported yet.")

        data_tail_copy = self.data.tail(1).copy()
        try:
            if missing_data is not None:
                self.add_data(missing_data)

            if current_date is not None:
                next_date = self.data.index[-1] + self.time_step
                if (self.data.index[-1] != current_date) or (next_date != current_date):
                    raise ValueError(
                        f"The current_date argument can only have values {self.data.index[-1]} and {next_date}."
                    )
            else:
                current_date = self.data.index[-1]
            self.data[current_date] = current_values.mean()
        except ValueError:
            self.data = self.data[self.data.index <= data_tail_copy.index[0]]
            self.data[data_tail_copy.index[0]] = data_tail_copy[0]
            raise

        current_countdown = np.count_nonzero(self.data) - 1

        return self._sell(current_countdown, current_values[-1], trading_limit, seller) + \
               self._buy(current_countdown, current_values[-1], trading_limit, buyer)

    def soft_sell(self):
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

    def get_last_date(self):
        return self.data.iloc[-1]

    def set_diversification(self, shares):
        """
        :param shares:
        :return: True if the replacement was successful
        """
        if self.diversification == list(shares):
            return True
        if self.soft_sell():
            self.trader.set_new_diversification_stack(reversed(shares))
            self.diversification = list(shares)
            return True
        return False

    def _sell(self, current_countdown, current_recent_value, trading_limit, seller) -> float:
        if self.data.index[-1] == self.trader.last_sell_date or \
                self.data.index[-1] == self.trader.last_buy_date:
            return 0

        value_of_lower_hot_bound = self._line(current_countdown, self.bound_intercepts[0])
        if current_recent_value <= value_of_lower_hot_bound:
            return self._sell_all(value_of_lower_hot_bound, seller)

        if self.coef_ < 0:
            revenue = self._greedy_sell(current_countdown, current_recent_value, seller)
        else:
            revenue = self._lazy_sell(current_countdown, current_recent_value, seller)

        return revenue

    def _sell_all(self, sell_bound_intercept, seller) -> float:
        revenue = seller(None)
        self.trader.remember_sells(None, self.data.index[-1], sell_bound_intercept)
        return revenue

    def _greedy_sell(self, current_countdown, current_recent_value, seller) -> float:
        revenue = 0

        # first condition
        # TODO: maybe it is more optimal
        sell_bound = self._get_next_upper_bound_value_after_recent_buy(current_countdown)
        while current_recent_value >= sell_bound:
            current_bound_intercept = \
                self._compute_current_bound_intercept(current_countdown, current_recent_value)
            revenue += self._sell_items_recent_buy(current_bound_intercept, seller)
            sell_bound = self._get_next_upper_bound_value_after_recent_buy(current_countdown)

        # second condition
        if (self.data.iloc[-3] < self.data.iloc[-2]) and (self.data.iloc[-2] > self.data.iloc[-1]): # peak
            while current_countdown >= self.trader.get_recent_buy()[4]:
                current_bound_intercept = \
                    self._compute_current_bound_intercept(current_countdown, current_recent_value)
                revenue += self._sell_items_recent_buy(current_bound_intercept, seller)

        return revenue

    def _sell_items_recent_buy(self, current_bound_intercept, seller) -> float:
        revenue = seller(self.trader.get_recent_buy()[2])
        self.trader.remember_sells(1, self.data.iloc[-1], current_bound_intercept)
        return revenue

    def _compute_current_bound_intercept(self, current_countdown, current_recent_value):
        bound_values = self._line(current_countdown, self.bound_intercepts)
        min_diff_arg = np.abs(bound_values - current_recent_value).argmin()
        return self.bound_intercepts[min_diff_arg]

    def _lazy_sell(self, current_countdown, current_recent_value, seller) -> float:
        bound_values = self._get_all_bound_values_higher_recent_buy(current_countdown)
        bounds = \
            self.bound_intercepts[(current_recent_value <= bound_values) & (bound_values < self.data.iloc[-2])]
        if bounds.size:
            return self._sell_all(bounds.min(), seller)
        return 0

    def _get_all_bound_values_higher_recent_buy(self, current_countdown):
        bounds = self.bound_intercepts[self.bound_intercepts > self.trader.get_recent_buy()[1]]
        return self._line(current_countdown, bounds)

    def _get_next_upper_bound_value_after_recent_buy(self, current_countdown):
        return self._get_all_bound_values_higher_recent_buy(current_countdown).min()

    def _buy(self, current_countdown, current_recent_value, trading_limit, buyer) -> float:
        if self.data.index[-1] == self.trader.last_sell_date or \
                self.data.index[-1] == self.trader.last_buy_date:
            return 0

        free_shares_num = self.trader.get_stack_size()

        if free_shares_num == 0:
            return 0

        total_shares_num = len(self.diversification)
        if free_shares_num != total_shares_num:
            bound_values = self._get_all_bound_values_below_recent_buy(current_countdown)[1:]
        else:
            bound_values = self._line(current_countdown, self.bound_intercepts[1:-2])

        if bound_values.size == 0:
            return 0

        if self.coef_ < 0:
            crucial = self.data.iloc[-1]    # lazy buy
        else:
            crucial = current_recent_value  # greedy buy

        if not (crucial >= bound_values > self.data[-2]).any():
            return 0

        if free_shares_num == 1:
            amount_to_buy = trading_limit - self.trader.get_all_funds_spent()
        else:
            amount_to_buy = self.trader.get_stack_top() * trading_limit

        buys_number, amount_spent_with_commission = buyer(amount_to_buy)

        current_bound_intercept = \
            self._compute_current_bound_intercept(current_countdown, current_recent_value)
        next_higher_bound_intercept = \
            self.bound_intercepts[self.bound_intercepts > current_bound_intercept].min()
        self.trader.remember_buy(
            (
                current_bound_intercept,
                buys_number,
                amount_spent_with_commission,
                ((amount_spent_with_commission / buys_number) - next_higher_bound_intercept) / self.coef_,
            ),
            self.data.index[-1],
        )

        return -amount_spent_with_commission

    def _get_all_bound_values_below_recent_buy(self, current_countdown):
        bounds = self.bound_intercepts[self.bound_intercepts < self.trader.get_recent_buy()[1]]
        return self._line(current_countdown, bounds)

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
        full_series = pd.concat([self.data.iloc[[-1]], data])
        return ((full_series[1:] - full_series[:-1]) == self.time_step).all()

    def _line(self, x, bias):
        """x and bias array or scalar regardless"""
        return self.coef_ * x + bias


class Trader:
    """Remembers current deals."""

    def __init__(self,
                 last_buy_date: pd.Timestamp = None,
                 last_sell_date: pd.Timestamp = None,
                 last_sell_bound: float = None,
                 diversification_stack=None):
        self.last_buy_date = last_buy_date
        self.last_sell_date = last_sell_date
        self.last_sell_bound = last_sell_bound

        self.diversification_stack = list(diversification_stack)
        self.current_deals = pd.DataFrame(
            columns=["bound_intercept", "buys_num", "total_buy_amount_with_commission", "last_profit_countdown"],
            index=pd.Index([], name="diversification_coeff"),
            dtype=np.float_
        )

    def get_recent_buy(self):
        recent_buy = self.current_deals.tail(1)
        return np.array([recent_buy.index[0], *recent_buy.values[0]])

    def get_stack_size(self):
        return len(self.diversification_stack)

    def get_all_funds_spent(self):
        return self.current_deals.total_buy_amount_with_commission.sum()

    def get_stack_top(self):
        return self.diversification_stack[-1]

    def remember_buy(self, info, current_date):
        """
        :param info: 4 element array
        :return: False if there is no way to remember the buy. True if the buy was remembered
        """
        if self.diversification_stack:
            share = self.diversification_stack.pop()
            self.current_deals.loc[share] = info
            self.last_buy_date = current_date
            return True
        return False

    def remember_sells(self, sell_shares_num, current_date, sell_bound_intercept):
        """

        :param sell_shares_num: if None then maximum number
        :param current_date:
        :return: Returns information on the recent buys or an empty form if there were no buys.
        """
        if sell_shares_num is None:
            sell_shares_num = self.current_deals.index.size

        recent_buy = self._forget_recent_buys(sell_shares_num)
        if not recent_buy.empty:
            self.last_sell_date = current_date
            self.last_sell_bound = sell_bound_intercept
        return recent_buy

    def set_new_diversification_stack(self, diversification_stack):
        """

        :param diversification_stack:
        :return: False if the stack is not released from work.
        """
        diversification_stack = list(diversification_stack)
        if sum(diversification_stack) != 1:
            raise ValueError(
                "The elements of the diversification argument must be equal to one in total."
            )

        if sum(self.diversification_stack) != 1:
            return False

        self.diversification_stack = diversification_stack
        return True

    def _forget_recent_buys(self, amount):
        """
        :param amount: amount of buys
        :return: Empty DataFrame if there is nothing to forget
        """
        tail = self.current_deals.tail(amount)
        if tail.empty:
            return tail
        self.diversification_stack.extend(reversed(tail.index))
        self.current_deals = self.current_deals.iloc[:-amount]
        return tail
