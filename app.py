from flask import Flask, jsonify, render_template
import pandas as pd
import requests
import time

app = Flask(__name__)

# Cache to store exchange rates and the time they were last updated
exchange_rate_cache = {
    'rates': None,
    'last_updated': 0
}

# Function to get exchange rates (called once)
def get_exchange_rates():
    current_time = time.time()
    one_day_in_seconds = 86400  # 24 hours in seconds

    # If rates are cached and they are not older than one day, return the cached rates
    if exchange_rate_cache['rates'] and (current_time - exchange_rate_cache['last_updated'] < one_day_in_seconds):
        return exchange_rate_cache['rates']

    try:
        url = f"https://api.exchangeratesapi.io/v1/latest?access_key=b2404051663928f7afe34c2fdf9f93ce"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            exchange_rate_cache['rates'] = data['rates']
            exchange_rate_cache['last_updated'] = current_time  # Update the last updated time
            return data['rates']
        else:
            print(f"Failed to get exchange rates. Status code: {response.status_code}")
            return exchange_rate_cache['rates'] or {}  # Return cached rates or empty dict if failed
    except Exception as e:
        print(f"Exception occurred during getting exchange rates: {e}")
        return exchange_rate_cache['rates'] or {}  # Return cached rates or empty dict if failed


# Function to convert a value to EUR based on the currency and exchange rates
def convert_to_eur(value, currency, exchange_rates):
    if currency == 'EUR':
        return value
    return value / exchange_rates.get(currency, 1)

# Portfolio route to get portfolio data and statistics
@app.route('/api/portfolio', methods=['GET'])
def get_portfolio_data():
    try:
        exchange_rates = get_exchange_rates()
        file_path = 'portfolio_analysis_with_dates.xlsx'
        df = pd.read_excel(file_path)

        # Combine duplicate tickers
        df_combined = df.groupby(['Ticker', 'Stock_Name', 'Sector', 'Currency', 'Sell_Signal']).agg({
            'Shares': 'sum',
            'Purchase_Price': 'mean',
            'Current_Price': 'mean',
            'PE_Ratio': 'mean',
            'Dividends': 'sum',
            'Value': 'sum',
            'Total_Return': 'mean',
            'Profit_Loss': 'sum',
            'ROI': 'mean',
            'Daily_Return': 'mean',
            'Volatility': 'mean',
            'Sharpe_Ratio': 'mean',
            'Outperform_SP500': 'first'
        }).reset_index()

        total_value = sum([convert_to_eur(row['Value'], row['Currency'], exchange_rates) for _, row in df_combined.iterrows()])
        total_invested = sum([row['Purchase_Price'] * row['Shares'] for _, row in df_combined.iterrows()])
        total_profit_loss = sum([convert_to_eur(row['Profit_Loss'], row['Currency'], exchange_rates) for _, row in df_combined.iterrows()])
        total_dividends = sum([convert_to_eur(row['Dividends'], row['Currency'], exchange_rates) for _, row in df_combined.iterrows()])
        
        portfolio_growth = (total_value - total_invested) / total_invested * 100
        average_roi = df_combined['ROI'].mean()

        stats = {
            'total_value': total_value,
            'total_invested': total_invested,  # Original value of the portfolio
            'total_profit_loss': total_profit_loss,
            'average_roi': average_roi,
            'total_dividends': total_dividends,
            'portfolio_growth': portfolio_growth
        }

        portfolio_data = df_combined.to_dict(orient='records')

        return jsonify({
            'portfolio': portfolio_data,
            'stats': stats
        })

    except Exception as e:
        print(f"Error reading portfolio data: {e}")
        return jsonify({'error': 'Failed to load portfolio data'}), 500

# Home route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)