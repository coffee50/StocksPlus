import pandas as pd
import matplotlib.pyplot as plt
import os


def run_simulation(data, strategy, initial_deposit, tickers, commission_rate=0.001):
    # 0.1% комиссия
    if len(tickers) > 1:
        print("Using first ticker ",
              tickers[0])

    main_ticker = tickers[0]

    if main_ticker not in data['Close'].columns:
        print(f"No ticker data for {main_ticker}")
        return None, None

    cash = initial_deposit
    position_quantity = 0.0
    portfolio_history = []
    trade_log = []

    ticker_data = data.xs(main_ticker, axis=1, level=1)
    signals = strategy.generate_signals(ticker_data)

    for date, row in ticker_data.iterrows():
        current_price = row['Close']
        current_portfolio_value = cash + (position_quantity * current_price)
        portfolio_history.append({'date': date, 'value': current_portfolio_value})

        signal = signals.loc[date]

        if pd.isna(current_price):
            continue

        if signal == 1.0 and cash > 0:  # сигнал на покупку
            # расчет стоимость с учетом комиссии
            investment_amount = cash / (1 + commission_rate)
            quantity_to_buy = investment_amount / current_price

            position_quantity = quantity_to_buy
            cost = cash  # полная стоимость списания
            cash = 0
            trade_log.append({
                'date': date, 'ticker': main_ticker, 'action': 'BUY',
                'quantity': quantity_to_buy, 'price': current_price,
                'cost': cost
            })

        elif signal == -1.0 and position_quantity > 0:  # сигнал на продажу
            sale_value_gross = position_quantity * current_price
            commission = sale_value_gross * commission_rate
            sale_value_net = sale_value_gross - commission  # и минус комиссия

            cash = sale_value_net
            quantity_to_sell = position_quantity
            position_quantity = 0
            trade_log.append({
                'date': date, 'ticker': main_ticker, 'action': 'SELL',
                'quantity': quantity_to_sell, 'price': current_price,
                'cost': sale_value_gross  # показать грязную сумму
            })

    return pd.DataFrame(portfolio_history), pd.DataFrame(trade_log)


def generate_report(portfolio_history, trade_log, data, initial_deposit, output_dir, tickers):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    main_ticker = tickers[0]
    ticker_data = data.xs(main_ticker, axis=1, level=1)

    # сохранение отчета о сделках в txt файл
    log_path = os.path.join(output_dir, "trade_log.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Trading report for {main_ticker}\n")
        f.write(f"Started with ${initial_deposit:,.2f}\n")
        final_value = portfolio_history['value'].iloc[-1]
        f.write(f"Ended with ${final_value:,.2f}\n")
        profit = final_value - initial_deposit
        profit_percent = (profit / initial_deposit) * 100
        f.write(f"Profit is ${profit:,.2f} ({profit_percent:.2f}%)\n\n")

        if not trade_log.empty:
            f.write(trade_log.to_string())
        else:
            f.write("No orders were done.")

    print(f"Saved report to {log_path}")

    # создание и сохранение графика с двумя областями
    chart_path = os.path.join(output_dir, "perf.png")
    plt.style.use('dark_background')
    # фигура с двумя графиками (2 строки, 1 колонка)
    # sharex=True связывает их оси X. height_ratios дает верхнему графику больше места
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(16, 10),
        sharex=True,
        gridspec_kw={'height_ratios': [2, 1]}
    )

    fig.suptitle(f'Trading report for {main_ticker}', fontsize=16)

    # верхний график это граф цены
    ax1.plot(ticker_data.index, ticker_data['Close'], label=f'Price {main_ticker}', color='#80cbc4', linewidth=1)
    ax1.set_ylabel('Price, $')
    ax1.legend()
    ax1.grid(True, alpha=0.2)

    # нижний график это портфолио
    ax2.plot(portfolio_history['date'], portfolio_history['value'], label='Assets', color='white', linewidth=1)
    ax2.set_ylabel('Assets, $')
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.grid(True, alpha=0.2)

    summary_text = (
        f"Initial deposit: ${initial_deposit:,.2f}     |     "
        f"Final assets: ${final_value:,.2f}     |     "
        f"Profit: ${profit:,.2f} ({profit_percent:.2f}%)"
    )

    fig.text(
        0.5, 0.016, summary_text,
        ha='center',  # горизонтальное выравнивание по центру
        va='bottom',
        fontsize=12,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#1c1c1c', alpha=0.9, edgecolor='gray')
    )

    # переделать это говно
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])

    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Perfchart saved to {chart_path}")
