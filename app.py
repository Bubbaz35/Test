from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Assume df is your DataFrame
df = pd.read_csv('sample_algo_trades.csv')

# Route for the home page
@app.route('/')
@app.route('/home')
def home():
    # Calculate current balance and daily profit/loss data
    current_balance = df['Trade Value'].sum()  # Example calculation
    profit_loss_data = df.groupby(df['Timestamp'].str[:10])['Trade Value'].sum().reset_index()
    profit_loss_data.columns = ['Date', 'Profit/Loss']
    profit_loss_data = profit_loss_data.to_dict(orient='records')
    return render_template('home.html', current_balance=current_balance, profit_loss_data=profit_loss_data)

# Route for the monthly statistics page
@app.route('/monthly')
def monthly():
    # Calculate monthly profit/loss data
    df['YearMonth'] = df['Timestamp'].str[:7]
    monthly_profit_loss_data = df.groupby('YearMonth')['Trade Value'].sum().reset_index()
    monthly_profit_loss_data.columns = ['YearMonth', 'Profit/Loss']
    monthly_profit_loss_data = monthly_profit_loss_data.to_dict(orient='records')
    return render_template('monthly.html', monthly_profit_loss_data=monthly_profit_loss_data)

# Route for the performance per share page
@app.route('/shares')
def shares():
    # Calculate profit/loss per share data
    profit_loss_by_share_data = df.groupby('Ticker')['Trade Value'].sum().reset_index()
    profit_loss_by_share_data.columns = ['Ticker', 'Profit/Loss']
    profit_loss_by_share_data['Company'] = profit_loss_by_share_data['Ticker'].map({
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com, Inc.',
        'TSLA': 'Tesla, Inc.',
        'FB': 'Meta Platforms, Inc.',
        'BRK.B': 'Berkshire Hathaway Inc.',
        'JPM': 'JPMorgan Chase & Co.',
        'JNJ': 'Johnson & Johnson',
        'V': 'Visa Inc.'
    })
    profit_loss_by_share_data['Exchange'] = 'NASDAQ'  # Example, replace with actual data
    profit_loss_by_share_data['Sector'] = 'Technology'  # Example, replace with actual data
    profit_loss_by_share_data = profit_loss_by_share_data.to_dict(orient='records')
    return render_template('shares.html', profit_loss_by_share_data=profit_loss_by_share_data)

# Route for ticker details page
@app.route('/ticker/<ticker>')
def ticker_details(ticker):
    data = pd.read_csv('sample_algo_trades.csv')
    ticker_data = data[data['Ticker'] == ticker]

    ticker_data['Profit/Loss'] = ticker_data.apply(
        lambda row: row['Trade Value'] if row['Trade Type'] == 'Sell' else -row['Trade Value'], axis=1)
    
    ticker_data['Cumulative P/L'] = ticker_data['Profit/Loss'].cumsum()

    ticker_data['Profit/Loss'] = ticker_data['Profit/Loss'].apply(lambda x: f"${x:,.2f}")
    ticker_data['Cumulative P/L'] = ticker_data['Cumulative P/L'].apply(lambda x: f"${x:,.2f}")

    # Generate the table HTML
    table_html = ticker_data.to_html(index=False, classes='table table-striped', justify='center', border=0, escape=False)

    # Calculate the performance chart data
    chart_data = ticker_data[['Timestamp', 'Cumulative P/L']]
    chart_data['Timestamp'] = pd.to_datetime(chart_data['Timestamp']).dt.strftime('%Y-%m-%d')
    chart_data.set_index('Timestamp', inplace=True)
    
    # Convert chart data to JSON for the chart
    chart_data_json = chart_data.to_json(orient='split')

    return render_template('ticker_details.html', ticker=ticker, table_html=table_html, chart_data=chart_data_json)
    # Placeholder for live value
    live_value = 0  # Replace with real-time fetching logic if available

    return render_template('ticker_details.html', ticker=ticker, ticker_data=ticker_data, live_value=live_value)

if __name__ == '__main__':
    app.run(debug=True)
