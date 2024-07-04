import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)

# Number of trades
num_trades = 1000

# List of S&P 500 companies' tickers (sample)
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'FB', 'BRK.B', 'JPM', 'JNJ', 'V']

# Generate random trade data
data = []
start_date = datetime(2023, 1, 1)
for i in range(1, num_trades + 1):
    trade_id = i
    timestamp = start_date + timedelta(minutes=random.randint(0, 525600))  # Random minute in 2023
    ticker = random.choice(tickers)
    trade_type = random.choice(['Buy', 'Sell'])
    shares_traded = random.randint(10, 500)
    price_per_share = round(random.uniform(100, 3500), 2)
    trade_value = round(shares_traded * price_per_share, 2)
    data.append([trade_id, timestamp, ticker, trade_type, shares_traded, price_per_share, trade_value])

# Create DataFrame
columns = ['Trade ID', 'Timestamp', 'Ticker', 'Trade Type', 'Shares Traded', 'Price per Share', 'Trade Value']
df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv('sample_algo_trades.csv', index=False)
