from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Global variables to hold the data
daily_profit_loss_data = None
monthly_profit_loss_data = None
profit_loss_by_share_data = None
current_balance = None

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
    global daily_profit_loss_data, monthly_profit_loss_data, profit_loss_by_share_data, current_balance
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        df = pd.read_csv(file)
        print(df.columns)  # Print the column names for debugging
        daily_profit_loss, monthly_profit_loss, profit_loss_by_share, current_balance = calculate_profit_loss(df)
        daily_profit_loss_data = daily_profit_loss.to_dict(orient='records')
        monthly_profit_loss_data = monthly_profit_loss.to_dict(orient='records')
        profit_loss_by_share_data = profit_loss_by_share.to_dict(orient='records')
        return redirect(url_for('home'))
    return 'File not uploaded'

@app.route('/home')
def home():
    global daily_profit_loss_data, current_balance
    return render_template('home.html', 
                           profit_loss_data=daily_profit_loss_data,
                           current_balance=current_balance)

@app.route('/monthly')
def monthly():
    global monthly_profit_loss_data
    return render_template('monthly.html', 
                           monthly_profit_loss_data=monthly_profit_loss_data)

@app.route('/shares')
def shares():
    global profit_loss_by_share_data
    return render_template('shares.html', 
                           profit_loss_by_share_data=profit_loss_by_share_data)

if __name__ == '__main__':
    app.run(debug=True)
