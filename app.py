from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def calculate_profit_loss(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date

    # Calculate daily profit/loss
    df['Trade Value'] = df.apply(lambda row: row['Shares Traded'] * row['Price per Share'], axis=1)
    df['Profit/Loss'] = df.apply(lambda row: row['Trade Value'] if row['Trade Type'] == 'Sell' else -row['Trade Value'], axis=1)
    daily_profit_loss = df.groupby('Date')['Profit/Loss'].sum().reset_index()

    # Calculate monthly profit/loss
    df['YearMonth'] = df['Timestamp'].dt.to_period('M')
    monthly_profit_loss = df.groupby('YearMonth')['Profit/Loss'].sum().reset_index()
    monthly_profit_loss['YearMonth'] = monthly_profit_loss['YearMonth'].astype(str)
    
    return daily_profit_loss, monthly_profit_loss

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    file = request.files['file']
    df = pd.read_csv(file)

    daily_profit_loss, monthly_profit_loss = calculate_profit_loss(df)

    profit_loss_data = daily_profit_loss.to_dict(orient='records')
    monthly_profit_loss_data = monthly_profit_loss.to_dict(orient='records')

    return render_template('results.html', profit_loss_data=profit_loss_data, monthly_profit_loss_data=monthly_profit_loss_data)

if __name__ == '__main__':
    app.run(debug=True)
