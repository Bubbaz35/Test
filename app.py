from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import yfinance as yf

app = Flask(__name__)

# Load the DataFrame
df = pd.read_csv('sample_algo_trades.csv')

# Ensure the DataFrame has the necessary columns
required_columns = ['Ticker', 'Company', 'Exchange', 'Sector', 'Profit/Loss Amount', 'Trade Value', 'Timestamp']
for col in required_columns:
    if col not in df.columns:
        df[col] = None  # Add the column with None values if it doesn't exist

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
    profit_loss_by_share_data = df.groupby('Ticker').agg(
        Company=('Company', 'first'),
        Exchange=('Exchange', 'first'),
        Sector=('Sector', 'first'),
        Profit_Loss=('Profit/Loss Amount', 'sum')
    ).reset_index()

    # Manually map company names and other details if necessary
    company_mapping = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com, Inc.',
        'TSLA': 'Tesla, Inc.',
        'META': 'Meta Platforms, Inc.',
        'BRK.B': 'Berkshire Hathaway Inc.',
        'JPM': 'JPMorgan Chase & Co.',
        'JNJ': 'Johnson & Johnson',
        'V': 'Visa Inc.'
    }
    profit_loss_by_share_data['Company'] = profit_loss_by_share_data['Ticker'].map(company_mapping)
    profit_loss_by_share_data['Exchange'] = profit_loss_by_share_data['Exchange'].fillna('NASDAQ')  # Example, replace with actual data
    profit_loss_by_share_data['Sector'] = profit_loss_by_share_data['Sector'].fillna('Technology')  # Example, replace with actual data
    profit_loss_by_share_data = profit_loss_by_share_data.to_dict(orient='records')

    return render_template('shares.html', profit_loss_by_share_data=profit_loss_by_share_data)

# Route for ticker details page
@app.route('/ticker/<ticker>')
def ticker_details(ticker):
    # Load the trades data
    df = pd.read_csv('sample_algo_trades.csv')

    # Filter trades for the specified ticker
    trades = df[df['Ticker'] == ticker].to_dict(orient='records')

    # Fetch live stock price using yfinance
    stock = yf.Ticker(ticker)
    history = stock.history(period='1d')
    if not history.empty:
        live_price = history['Close'][0]
    else:
        live_price = 'N/A'  # Or handle this case as you see fit

    return render_template('ticker_details.html', ticker=ticker, trades=trades, live_price=live_price)

if __name__ == '__main__':
    app.run(debug=True)
