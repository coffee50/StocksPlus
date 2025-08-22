# bot.py

import pandas as pd

class MovingAverageCrossStrategy:
    def __init__(self, short_window=20, long_window=50):
        self.short_window = short_window
        self.long_window = long_window
        self.name = f"MA_Cross_{short_window}_{long_window}"

    def generate_signals(self, data):
        # 1 (купить), -1 (продать), 0 (держать)
        if 'Close' not in data.columns:
            raise ValueError("В данных отсутствует столбец 'Close'")

        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0
        signals['short_mavg'] = data['Close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['Close'].rolling(window=self.long_window, min_periods=1, center=False).mean()
        # сигнал когда короткая MA пересекает длинную MA
        # сигнал 1.0 когда короткая больше длинной
        signals['positions'] = 0.0
        signals['positions'][self.short_window:] = (signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:])
        # фактический сигнал на сделку - разница между позицией сегодня и вчера
        signals['signal'] = signals['positions'].diff()

        return signals['signal']
