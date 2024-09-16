import yfinance as yf
import pandas as pd
import numpy as np

# Load portfolio data from an Excel file
file_path = 'portfolio_data.xlsx'  # Replace with your actual file path
df = pd.read_excel(file_path)

# Convert 'Purchase_Date' to datetime
df['Purchase_Date'] = pd.to_datetime(df['Purchase_Date'])

# Fetch current market prices, currency, stock name, sector, P/E ratio, and dividends
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period='1d')['Close'].iloc[0]
        currency = stock.info.get('currency', 'Unknown')
        name = stock.info.get('shortName', 'Unknown')
        sector = stock.info.get('sector', 'Unknown')
        pe_ratio = stock.info.get('trailingPE', np.nan)
        dividends = stock.dividends.sum()
        return price, currency, name, sector, pe_ratio, dividends
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return np.nan, 'Unknown', 'Unknown', 'Unknown', np.nan, 0.0

# Apply the function to the DataFrame
df[['Current_Price', 'Currency', 'Stock_Name', 'Sector', 'PE_Ratio', 'Dividends']] = df['Ticker'].apply(lambda x: pd.Series(get_stock_info(x)))
df.dropna(inplace=True)  # Remove rows with failed data fetch

# Calculate financial metrics rounded to 4 decimal places
df['Value'] = df['Shares'] * df['Current_Price']
df['Total_Return'] = (((df['Current_Price'] + df['Dividends']) - df['Purchase_Price']) / df['Purchase_Price'] * 100).round(4)
df['Profit_Loss'] = (((df['Current_Price'] - df['Purchase_Price']) * df['Shares']) - df['Transaction_Cost']).round(4)
df['ROI'] = (df['Profit_Loss'] / (df['Purchase_Price'] * df['Shares'] + df['Transaction_Cost']) * 100).round(4)

# Historical data for additional metrics
def get_historical_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)['Close']

# Calculate daily returns and volatility, rounded to 4 decimal places
df['Daily_Return'] = df['Ticker'].apply(lambda x: get_historical_data(x, '1y').pct_change().mean()).round(4)
df['Volatility'] = df['Ticker'].apply(lambda x: get_historical_data(x, '1y').pct_change().std()).round(4)
risk_free_rate = 0.01  # Example risk-free rate
df['Sharpe_Ratio'] = ((df['Daily_Return'] - risk_free_rate) / df['Volatility']).round(4)

# Portfolio value
portfolio_value = df['Value'].sum()

# Diversification analysis with automatic sector classification
sector_df = df.groupby('Sector')['Value'].sum().reset_index()
sector_df['Percentage'] = (sector_df['Value'] / portfolio_value * 100).round(4)

# Benchmarking against S&P 500
sp500 = yf.Ticker("^GSPC")
sp500_return = sp500.history(period='1y')['Close'].pct_change().mean() * 100

df['Outperform_SP500'] = df['Total_Return'] > sp500_return.round(4)

# Sell signal based on multiple factors (e.g., ROI and P/E Ratio)
roi_threshold = 20  # User-defined ROI threshold for sell signal
pe_ratio_threshold = 25  # Example P/E ratio threshold
df['Sell_Signal'] = ((df['ROI'] > roi_threshold) | (df['PE_Ratio'] > pe_ratio_threshold)) & (df['Outperform_SP500'])

# Reorder the columns
df = df[['Ticker', 'Stock_Name', 'Sector', 'Shares', 'Sell_Signal', 'Purchase_Price', 'Transaction_Cost', 'Purchase_Date',
         'Current_Price', 'Currency', 'PE_Ratio', 'Dividends', 'Value', 'Total_Return', 'Profit_Loss',
         'ROI', 'Daily_Return', 'Volatility', 'Sharpe_Ratio', 'Outperform_SP500']]

# Save results to an Excel file
with pd.ExcelWriter('portfolio_analysis_with_dates.xlsx') as writer:
    df.to_excel(writer, sheet_name='Portfolio', index=False)
    sector_df.to_excel(writer, sheet_name='Sector Allocation', index=False)
    # Save portfolio value summary
    summary_df = pd.DataFrame({'Metric': ['Portfolio Value', 'S&P 500 Return (%)'], 'Value': [portfolio_value, sp500_return.round(4)]})
    summary_df.to_excel(writer, sheet_name='Summary', index=False)

print("Portfolio analysis with dates has been saved to 'portfolio_analysis_with_dates.xlsx'.")
