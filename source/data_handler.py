# data_handler.py

import ccxt
import pandas as pd


# ### ИЗМЕНЕНО: Явно указано, что timeframe используется
def fetch_data_ccxt(ticker, start_date, timeframe='1d'):
    """
    Получает OHLCV данные для тикера с биржи Binance.
    """
    exchange = ccxt.binance({
        'rateLimit': 1200,
        'enableRateLimit': True,
        # Опционально: можно добавить таймаут, если интернет медленный
        # 'options': {
        #     'adjustForTimeDifference': True,
        #     'recvWindow': 10000,
        # },
    })

    try:
        since = exchange.parse8601(f"{start_date}T00:00:00Z")

        all_ohlcv = []
        # ### ИЗМЕНЕНО: В лог выводится выбранный таймфрейм
        print(f"Fetching '{ticker}' data from Binance on timeframe '{timeframe}' starting from {start_date}...")

        # ### ВАЖНО: Загрузка большого количества мелких свечей может занять время!
        # CCXT загружает данные порциями.
        while True:
            # ### ИЗМЕНЕНО: timeframe передается в запрос
            ohlcv = exchange.fetch_ohlcv(ticker, timeframe, since, limit=1000)
            if not ohlcv:
                break

            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
            print(f"Loaded {len(ohlcv)} more candles, up to {exchange.iso8601(ohlcv[-1][0])}")

        if not all_ohlcv:
            print(f"Couldn't load data for ticker {ticker}. Maybe it doesn't exist on Binance?")
            return None

        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        print(f"Data loaded successfully. Total candles: {len(df)}")
        return df

    except ccxt.NetworkError as e:
        print(f"CCXT Network Error: {e}. Check your connection or exchange status.")
        return None
    except ccxt.ExchangeError as e:
        print(f"CCXT Exchange Error: {e}. The ticker/timeframe might not be supported.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None