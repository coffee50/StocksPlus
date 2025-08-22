# plot_gen.py

import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


# ### ИЗМЕНЕНО: Функция теперь принимает время начала и конца
def generate_report(portfolio_history, trade_log, data, initial_deposit, output_dir, ticker,
                    run_timestamp_start: datetime, run_timestamp_end: datetime):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- Расчеты ---
    final_value = portfolio_history['value'].iloc[-1]
    profit = final_value - initial_deposit
    profit_percent = (profit / initial_deposit) * 100

    # ### НОВОЕ: Расчет продолжительности
    duration = run_timestamp_end - run_timestamp_start
    duration_seconds = duration.total_seconds()
    minutes = int(duration_seconds // 60)
    seconds = duration_seconds % 60
    duration_str = f"{minutes}m {seconds:.1f}s"  # Форматируем как "Xm Y.Zs"

    # --- Текстовый отчет ---
    log_path = os.path.join(output_dir, "trade_log.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"--- Trading Report for {ticker} ---\n")
        f.write(f"Run Time: {run_timestamp_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {duration_str}\n\n")  # Добавляем продолжительность
        f.write(f"Initial Deposit: ${initial_deposit:,.2f}\n")
        f.write(f"Final Value:     ${final_value:,.2f}\n")
        f.write(f"Total Profit:    ${profit:,.2f} ({profit_percent:.2f}%)\n\n")
        f.write("--- Trade Log ---\n")
        if not trade_log.empty:
            f.write(trade_log.to_string())
        else:
            f.write("No orders were executed.")
    print(f"Saved text report to {log_path}")

    # --- Интерактивный график ---
    chart_path = os.path.join(output_dir, "perf_report.html")

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.05, row_heights=[0.7, 0.3]
    )

    # ... (графики без изменений) ...
    fig.add_trace(
        go.Scatter(x=data.index, y=data['Close'], name=f'Price {ticker}', line=dict(color='#80cbc4', width=1.5)), row=1,
        col=1)
    if not trade_log.empty:
        buys = trade_log[trade_log['action'] == 'BUY']
        sells = trade_log[trade_log['action'] == 'SELL']
        fig.add_trace(go.Scatter(x=buys['date'], y=buys['price'], name='Buy Orders', mode='markers',
                                 marker=dict(color='lime', size=10, symbol='triangle-up')), row=1, col=1)
        fig.add_trace(go.Scatter(x=sells['date'], y=sells['price'], name='Sell Orders', mode='markers',
                                 marker=dict(color='red', size=10, symbol='triangle-down')), row=1, col=1)
    fig.add_trace(go.Scatter(x=portfolio_history['date'], y=portfolio_history['value'], name='Portfolio Value',
                             line=dict(color='white', width=1.5)), row=2, col=1)

    # ### ИЗМЕНЕНО: Объединяем всю информацию в один блок аннотации
    # Используем <hr> (горизонтальная линия) для разделения блоков
    # И приглушенный цвет для метаданных
    summary_text_html = (
        f"Initial Deposit: <span style='color:#FFD700'>${initial_deposit:,.2f}</span><br>"
        f"Final Value:     <span style='color:#FFD700'>${final_value:,.2f}</span><br>"
        f"Total Profit:    <span style='color:#FFD700'>${profit:,.2f} ({profit_percent:.2f}%)</span><br>"
        f"<span style='color:rgba(255, 255, 255, 0.7)'>Run Time: {run_timestamp_start.strftime('%Y-%m-%d %H:%M:%S')}</span><br>"
        f"<span style='color:rgba(255, 255, 255, 0.7)'>Duration: {duration_str}</span>"
    )

    fig.add_annotation(dict(
        text=summary_text_html, align='left', showarrow=False, xref='paper', yref='paper',
        x=0.02, y=0.98, xanchor='left', yanchor='top', bordercolor="gray", borderwidth=1,
        bgcolor="rgba(28, 28, 28, 0.85)"
    ))

    # ### УДАЛЕНО: Вторая аннотация для временной метки больше не нужна.

    # Обновление макета (без изменений)
    fig.update_layout(
        title_text=f"<b>Trading Report for {ticker}</b>", title_x=0.5,
        template='plotly_dark', height=800, xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis1_title='Price, $', yaxis2_title='Portfolio Value, $',
        xaxis2_title='Date'
    )

    fig.write_html(chart_path)
    print(f"Interactive chart saved to {chart_path}")