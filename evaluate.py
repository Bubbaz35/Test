import yfinance as yf
import pandas as pd

def evaluate_stock(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        'Ticker': ticker,
        'Beta': info.get('beta', None),
        'PE Ratio': info.get('trailingPE', None),
        'Revenue Growth': info.get('revenueGrowth', None),
        'Earnings Growth': info.get('earningsGrowth', None),
        'Dividend Yield': info.get('dividendYield', None)
    }

tickers = ['AAPL', 'MSFT', 'TSLA']
df = pd.DataFrame([evaluate_stock(t) for t in tickers])
df.to_excel('data/evaluation_results.xlsx', index=False)
