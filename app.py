from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def format_currency(value, symbol='$'):
    return f"{symbol}{value:,.2f}"

def calculate_profit_loss(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date

    # Calculate trade value and profit/loss
    df['Trade Value'] = df['Shares Traded'] * df['Price per Share']
    df['Profit/Loss'] = df.apply(lambda row: row['Trade Value'] if row['Trade Type'] == 'Sell' else -row['Trade Value'], axis=1)

    # Calculate daily profit/loss
    daily_profit_loss = df.groupby('Date')['Profit/Loss'].sum().reset_index()
    daily_profit_loss['Profit/Loss'] = daily_profit_loss['Profit/Loss'].apply(lambda x: format_currency(x))

    # Calculate monthly statistics
    df['YearMonth'] = df['Timestamp'].dt.to_period('M')
    monthly_profit_loss = df.groupby('YearMonth')['Profit/Loss'].sum().reset_index()
    monthly_profit_loss['YearMonth'] = monthly_profit_loss['YearMonth'].astype(str)
    monthly_profit_loss['Profit/Loss'] = monthly_profit_loss['Profit/Loss'].apply(lambda x: format_currency(x))

    # Calculate profit/loss by share
    profit_loss_by_share = df.groupby('Ticker')['Profit/Loss'].sum().reset_index()
    profit_loss_by_share['Profit/Loss'] = profit_loss_by_share['Profit/Loss'].apply(lambda x: format_currency(x))

    # Calculate current balance
    current_balance = df['Profit/Loss'].sum()
    current_balance = format_currency(current_balance)

    return daily_profit_loss, monthly_profit_loss, profit_loss_by_share, current_balance

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        df = pd.read_csv(file)
        print(df.columns)  # Print the column names for debugging
        daily_profit_loss, monthly_profit_loss, profit_loss_by_share, current_balance = calculate_profit_loss(df)
        daily_profit_loss_dict = daily_profit_loss.to_dict(orient='records')
        monthly_profit_loss_dict = monthly_profit_loss.to_dict(orient='records')
        profit_loss_by_share_dict = profit_loss_by_share.to_dict(orient='records')
        return render_template('results.html', 
                               profit_loss_data=daily_profit_loss_dict, 
                               monthly_profit_loss_data=monthly_profit_loss_dict,
                               profit_loss_by_share_data=profit_loss_by_share_dict,
                               current_balance=current_balance)
    return 'File not uploaded'

if __name__ == '__main__':
    app.run(debug=True)
