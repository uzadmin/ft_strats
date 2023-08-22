from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
#from technical.indicators import accumulation_distribution
from technical.util import resample_to_interval, resampled_merge
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy
from technical.indicators import ichimoku
# from freqtrade.vendor.qtpylib.indicators import stoch

class Ichimoku_v1(IStrategy):

    minimal_roi = {
        "0": 10,
        "43200": 7.5
    }

    ticker_interval = '4h' #3m

    # startup_candle_count: int = 2

    # trailing stoploss
    stoploss = -1
    trailing_stop = True
    trailing_stop_positive = 0.35
    trailing_stop_positive_offset = 0.50
    trailing_only_offset_is_reached = True

    def informative_pairs(self):
        return [
            ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        ichi = ichimoku(dataframe, conversion_line_period=20, base_line_periods=60, laggin_span=120, displacement=30)
        # dataframe['chikou_span'] = ichi['chikou_span']
        dataframe['tenkan'] = ichi['tenkan_sen']
        dataframe['kijun'] = ichi['kijun_sen']
        dataframe['senkou_a'] = ichi['senkou_span_a']
        dataframe['senkou_b'] = ichi['senkou_span_b']
        dataframe['cloud_green'] = ichi['cloud_green']
        dataframe['cloud_red'] = ichi['cloud_red']

        # dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['senkou_a'], dataframe['senkou_b'])) &
                (dataframe['close'] > dataframe['senkou_a']) &
                (dataframe['close'] > dataframe['senkou_b']) &
                (dataframe['cloud_green'] == True)
            ),
            'buy'] = 1

        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['close'], dataframe['senkou_a'])) &
                (dataframe['tenkan'] > dataframe['kijun']) &
                (dataframe['close'] > dataframe['tenkan']) &
                (dataframe['cloud_green'] == True)

            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['senkou_b'], dataframe['senkou_a'])) &
                (dataframe['close'] < dataframe['senkou_a']) &
                (dataframe['close'] < dataframe['senkou_b']) &
                (dataframe['cloud_red'] == True)
            ),
            'sell'] = 1

        return dataframe