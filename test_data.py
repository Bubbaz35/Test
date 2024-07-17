import pandas as pd
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)

# Number of trades
num_trades = 10000

# List of S&P 500 companies' tickers (sample)
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'BRK.B', 'JPM', 'JNJ', 'V']

# Starting balance
starting_balance = 10000
current_balance = starting_balance

# Initialize stock holdings
holdings = {ticker: {'shares': 0, 'avg_price': 0} for ticker in tickers}

# Generate random trade data
data = []
start_date = datetime(2022, 1, 1)
forced_loss_month = 6  # Ensure June has a loss
loss_made = False

for i in range(1, num_trades + 1):
    trade_id = i
    timestamp = start_date + timedelta(minutes=random.randint(0, 525600))  # Random minute in 2023
    ticker = random.choice(tickers)
    trade_type = 'Buy'
    shares_traded = random.randint(10, 500)
    price_per_share = round(random.uniform(100, 700), 2)
    trade_value = round(shares_traded * price_per_share, 2)
    profit_loss_flag = ''
    profit_loss_amount = 0.0

    # Check holdings for potential forced sales (5% loss or 8% profit)
    for t, h in holdings.items():
        if h['shares'] > 0:
            current_market_price = round(random.uniform(100, 700), 2)
            # Sell at 5% loss
            if current_market_price < 0.90 * h['avg_price']:
                trade_type = 'Sell'
                shares_traded = h['shares']
                price_per_share = current_market_price
                trade_value = round(shares_traded * price_per_share, 2)
                current_balance += trade_value
                profit_loss_amount = trade_value - (h['shares'] * h['avg_price'])
                profit_loss_flag = 'Loss'
                holdings[t]['shares'] = 0
                holdings[t]['avg_price'] = 0
                data.append([trade_id, timestamp, t, trade_type, shares_traded, price_per_share, trade_value, f"${current_balance:,.2f}", profit_loss_flag, profit_loss_amount])
                trade_id += 1
            # Sell at 8% profit
            elif current_market_price > 1.03 * h['avg_price']:
                trade_type = 'Sell'
                shares_traded = h['shares']
                price_per_share = current_market_price
                trade_value = round(shares_traded * price_per_share, 2)
                current_balance += trade_value
                profit_loss_amount = trade_value - (h['shares'] * h['avg_price'])
                profit_loss_flag = 'Profit'
                holdings[t]['shares'] = 0
                holdings[t]['avg_price'] = 0
                data.append([trade_id, timestamp, t, trade_type, shares_traded, price_per_share, trade_value, f"${current_balance:,.2f}", profit_loss_flag, profit_loss_amount])
                trade_id += 1

    # Ensure we have some trades with a loss
    if random.random() < 0.1 or (timestamp.month == forced_loss_month and not loss_made):
        if holdings[ticker]['shares'] > 0:
            trade_type = 'Sell'
            shares_traded = holdings[ticker]['shares']
            price_per_share = round(random.uniform(100, 3500), 2) * 0.90  # 10% lower than the buy price to simulate loss
            trade_value = round(shares_traded * price_per_share, 2)
            profit_loss_amount = trade_value - (holdings[ticker]['shares'] * holdings[ticker]['avg_price'])
            profit_loss_flag = 'Loss'
            current_balance += trade_value
            holdings[ticker]['shares'] = 0
            holdings[ticker]['avg_price'] = 0
            data.append([trade_id, timestamp, ticker, trade_type, shares_traded, price_per_share, trade_value, f"${current_balance:,.2f}", profit_loss_flag, profit_loss_amount])
            trade_id += 1
            if timestamp.month == forced_loss_month:
                loss_made = True

    # Check if balance is sufficient for the purchase
    if trade_type == 'Buy' and current_balance < trade_value:
        # Sell shares for profit if balance is too low to buy new shares
        for t, h in holdings.items():
            if h['shares'] > 0:
                current_market_price = round(random.uniform(100, 3500), 2)
                if current_market_price > h['avg_price']:
                    trade_type = 'Sell'
                    shares_traded = h['shares']
                    price_per_share = current_market_price
                    trade_value = round(shares_traded * price_per_share, 2)
                    current_balance += trade_value
                    profit_loss_amount = trade_value - (h['shares'] * h['avg_price'])
                    profit_loss_flag = 'Profit'
                    holdings[t]['shares'] = 0
                    holdings[t]['avg_price'] = 0
                    data.append([trade_id, timestamp, t, trade_type, shares_traded, price_per_share, trade_value, f"${current_balance:,.2f}", profit_loss_flag, profit_loss_amount])
                    trade_id += 1

    if trade_type == 'Buy':
        # Execute buy trade if balance is sufficient
        if current_balance >= trade_value:
            current_balance -= trade_value
            if holdings[ticker]['shares'] == 0:
                holdings[ticker]['avg_price'] = price_per_share
            else:
                # Update average price
                total_shares = holdings[ticker]['shares'] + shares_traded
                holdings[ticker]['avg_price'] = (
                    holdings[ticker]['avg_price'] * holdings[ticker]['shares'] + price_per_share * shares_traded
                ) / total_shares
            holdings[ticker]['shares'] += shares_traded
        else:
            # Skip this trade if balance is insufficient
            continue

    # Append trade data
    if trade_type == 'Buy':
        data.append([trade_id, timestamp, ticker, trade_type, shares_traded, price_per_share, trade_value, f"${current_balance:,.2f}", '', 0.0])
    else:
        data.append([trade_id, timestamp, ticker, trade_type, shares_traded, price_per_share, trade_value, f"${current_balance:,.2f}", profit_loss_flag, profit_loss_amount])

# Create DataFrame
columns = ['Trade ID', 'Timestamp', 'Ticker', 'Trade Type', 'Shares Traded', 'Price per Share', 'Trade Value', 'Balance', 'Profit/Loss', 'Profit/Loss Amount']
df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv('sample_algo_trades.csv', index=False)

print(f"Generated {len(data)} trades.")
