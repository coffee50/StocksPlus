# run.py

import os
from datetime import datetime
from data_handler import fetch_data_ccxt
from bot import MovingAverageCrossStrategy
from simulator import run_simulation
from plot_gen import generate_report


# ... (функция get_user_input остается без изменений) ...
def get_user_input():
    ticker = input("Ticker (ex: ETH/USDT): ").strip().upper()

    while True:
        start_date = input("Start date YYYY-MM-DD: ")
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Wrong date format.")

    timeframe_options = {
        '1': '15m', '2': '30m', '3': '1h',
        '4': '4h', '5': '12h', '6': '1d'
    }
    print("\nSelect timeframe:")
    for key, value in timeframe_options.items():
        print(f"  {key}: {value}")

    while True:
        choice = input(f"Enter number (1-{len(timeframe_options)}): ")
        if choice in timeframe_options:
            timeframe = timeframe_options[choice]
            break
        else:
            print("Invalid choice. Please try again.")

    while True:
        try:
            initial_deposit = float(input("\nDeposit, $: "))
            if initial_deposit > 0:
                break
            else:
                print("Should be above zero.")
        except ValueError:
            print("Enter a number.")

    return ticker, start_date, initial_deposit, timeframe


# ... (функция create_output_directory остается без изменений) ...
def create_output_directory():
    base_dir = "outputs"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    today_str = datetime.now().strftime('%d-%m-%Y')
    run_num = 1
    while True:
        output_dir = os.path.join(base_dir, f"run{run_num}_{today_str}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            return output_dir
        run_num += 1


def main():
    # ### ИЗМЕНЕНО: Переименовываем для ясности
    run_timestamp_start = datetime.now()

    ticker, start_date, initial_deposit, timeframe = get_user_input()

    historical_data = fetch_data_ccxt(ticker, start_date, timeframe=timeframe)

    if historical_data is None or historical_data.empty:
        print("Couldn't get data for the ticker.")
        return

    strategy = MovingAverageCrossStrategy(short_window=20, long_window=50)

    print("\nStarting simulation...")
    portfolio_history, trade_log = run_simulation(
        data=historical_data,
        strategy=strategy,
        initial_deposit=initial_deposit,
        ticker=ticker
    )

    if portfolio_history is None:
        print("Couldn't start simulation.")
        return

    print("\nReporting...")

    # ### НОВОЕ: Замеряем время окончания перед созданием отчета
    run_timestamp_end = datetime.now()
    output_dir = create_output_directory()

    # ### ИЗМЕНЕНО: Передаем время начала и конца
    generate_report(
        portfolio_history=portfolio_history,
        trade_log=trade_log,
        data=historical_data,
        initial_deposit=initial_deposit,
        output_dir=output_dir,
        ticker=ticker,
        run_timestamp_start=run_timestamp_start,
        run_timestamp_end=run_timestamp_end
    )

    print(f"\nSaved all perflogs to {output_dir}")


if __name__ == "__main__":
    main()