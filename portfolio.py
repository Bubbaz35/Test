import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load API key from .env file

API_KEY = os.getenv("CURRENCY_API_KEY")
API_URL = "https://api.exchangeratesapi.io/v1/latest?access_key="  # Example API (use your provider)

# Load portfolio data
file_path = 'data/portfolio_data.xlsx'
df = pd.read_excel(file_path)

# Convert date column
df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'])

# Function to fetch stock data
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period='1d')

        # Ensure stock data exists
        if history.empty:
            return None

        info = stock.info
        return {
            'Current_Price': history['Close'].iloc[-1],
            'Stock_Name': info.get('shortName', 'Unknown'),
            'Currency': info.get('currency', 'Unknown'),
            'Sector': info.get('sector', 'Unknown'),
            'PE_Ratio': info.get('trailingPE', np.nan),
            'Dividends': stock.dividends.sum()
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# Fetch stock data in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(get_stock_info, df['Ticker']))

# Update dataframe with fetched data
for key in ['Current_Price', 'Stock_Name', 'Currency', 'Sector', 'PE_Ratio', 'Dividends']:
    df[key] = [res[key] if res else np.nan for res in results]

# Calculate financial metrics
df['Total_Cost'] = df['Shares'] * df['Purchase_Price'] + df['Transaction_Cost']
df['Current_Value'] = df['Shares'] * df['Current_Price']
df['Total_Return'] = (((df['Current_Value'] - df['Total_Cost']) / df['Total_Cost']) * 100).round(2)

# Save results
output_path = 'data/portfolio_analysis.xlsx'
df.to_excel(output_path, index=False)

print(f"Portfolio analysis saved to {output_path}")
