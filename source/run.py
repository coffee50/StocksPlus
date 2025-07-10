import os
from datetime import datetime
from data_handler import fetch_data
from strategy import MovingAverageCrossStrategy
from simulator import run_simulation, generate_report


def get_user_input():
    tickers_str = input("Ticker (ex: ETH-USD): ")
    tickers = [ticker.strip().upper() for ticker in tickers_str.split(',')]

    while True:
        start_date = input("Start date YYYY-MM-DD: ")
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Wrong date format.")

    while True:
        try:
            initial_deposit = float(input("Deposit, $: "))
            if initial_deposit > 0:
                break
            else:
                print("Should be above zero.")
        except ValueError:
            print("Enter a number.")

    return tickers, start_date, initial_deposit


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
    tickers, start_date, initial_deposit = get_user_input()

    historical_data = fetch_data(tickers, start_date)

    if historical_data is None or historical_data.empty:
        print("Couldn't get data ticker.")
        return

    strategy = MovingAverageCrossStrategy(short_window=20, long_window=50)

    print("\nStarting simulation...")
    portfolio_history, trade_log = run_simulation(
        data=historical_data,
        strategy=strategy,
        initial_deposit=initial_deposit,
        tickers=tickers
    )

    if portfolio_history is None:
        print("Couldn't start simulation.")
        return
    print("\nReporting...")
    output_dir = create_output_directory()
    generate_report(
        portfolio_history=portfolio_history,
        trade_log=trade_log,
        data=historical_data,
        initial_deposit=initial_deposit,
        output_dir=output_dir,
        tickers=tickers  # Передаем тикеры для отчета
    )

    print(f"\nSaved all perflogs to {output_dir}")


if __name__ == "__main__":
    main()