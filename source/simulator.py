# simulator.py
import pandas as pd

# ### ИЗМЕНЕНО: Упрощенный вызов, так как мы работаем с одним тикером
def run_simulation(data, strategy, initial_deposit, ticker, commission_rate=0.001):
    cash = initial_deposit
    position_quantity = 0.0
    portfolio_history = []
    trade_log = []

    # ### ИЗМЕНЕНО: 'data' - это уже DataFrame для нужного тикера
    # ticker_data = data.xs(main_ticker, axis=1, level=1) # Эта строка больше не нужна
    signals = strategy.generate_signals(data)

    for date, row in data.iterrows():
        current_price = row['Close']
        current_portfolio_value = cash + (position_quantity * current_price)
        portfolio_history.append({'date': date, 'value': current_portfolio_value})

        signal = signals.loc[date]

        if pd.isna(current_price):
            continue

        if signal == 1.0 and cash > 0:
            investment_amount = cash / (1 + commission_rate)
            quantity_to_buy = investment_amount / current_price
            position_quantity = quantity_to_buy
            cost = cash
            cash = 0
            trade_log.append({
                'date': date, 'ticker': ticker, 'action': 'BUY',
                'quantity': quantity_to_buy, 'price': current_price, 'cost': cost
            })

        elif signal == -1.0 and position_quantity > 0:
            sale_value_gross = position_quantity * current_price
            commission = sale_value_gross * commission_rate
            sale_value_net = sale_value_gross - commission
            cash = sale_value_net
            quantity_to_sell = position_quantity
            position_quantity = 0
            trade_log.append({
                'date': date, 'ticker': ticker, 'action': 'SELL',
                'quantity': quantity_to_sell, 'price': current_price, 'cost': sale_value_gross
            })

    return pd.DataFrame(portfolio_history), pd.DataFrame(trade_log)