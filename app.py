from flask import Flask, jsonify, render_template
import pandas as pd
import requests

app = Flask(__name__)

# Function to get exchange rates (called once)
def get_exchange_rates():
    try:
        # Make the request to get all rates for EUR
        url = f"https://api.exchangeratesapi.io/v1/latest?access_key=b2404051663928f7afe34c2fdf9f93ce"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data['rates']  # Return the full rates dictionary
        else:
            print(f"Failed to get exchange rates. Status code: {response.status_code}")
            return {}  # Return an empty dictionary in case of error
    except Exception as e:
        print(f"Exception occurred during getting exchange rates: {e}")
        return {}

# Function to convert a value to EUR using pre-fetched rates
def convert_to_eur(value, currency, rates):
    if currency == 'EUR':  # No conversion needed
        return value
    # Get the conversion rate from the rates dictionary
    eur_rate = rates.get(currency)
    if eur_rate:
        return value / eur_rate  # Convert value to EUR
    else:
        print(f"Error: Conversion rate for {currency} not found.")
        return value  # Fallback to original value if rate is not found


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio_data():
    try:
        # Get the exchange rates only once
        exchange_rates = get_exchange_rates()

        # Load portfolio data from Excel
        file_path = 'portfolio_analysis_with_dates.xlsx'
        df = pd.read_excel(file_path)

        # Combine duplicate tickers
        df_combined = df.groupby(['Ticker', 'Stock_Name', 'Sector', 'Currency', 'Sell_Signal']).agg({
            'Shares': 'sum',
            'Purchase_Price': 'mean',
            'Transaction_Cost': 'sum',
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

        # Convert values to EUR for statistics using pre-fetched rates
        total_value = sum([convert_to_eur(row['Value'], row['Currency'], exchange_rates) for _, row in df_combined.iterrows()])
        total_profit_loss = sum([convert_to_eur(row['Profit_Loss'], row['Currency'], exchange_rates) for _, row in df_combined.iterrows()])
        total_dividends = sum([convert_to_eur(row['Dividends'], row['Currency'], exchange_rates) for _, row in df_combined.iterrows()])

        # Portfolio growth calculation
        total_invested = sum([row['Purchase_Price'] * row['Shares'] for _, row in df_combined.iterrows()])
        portfolio_growth = (total_value - total_invested) / total_invested * 100

        # Average ROI
        average_roi = df_combined['ROI'].mean()

        stats = {
            'total_value': total_value,
            'total_profit_loss': total_profit_loss,
            'average_roi': average_roi,
            'total_dividends': total_dividends,
            'portfolio_growth': portfolio_growth
        }

        # Convert the dataframe to JSON
        portfolio_data = df_combined.to_dict(orient='records')

        return jsonify({
            'portfolio': portfolio_data,
            'stats': stats
        })

    except Exception as e:
        print(f"Error reading portfolio data: {e}")
        return jsonify({'error': 'Failed to load portfolio data'}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)