import yfinance as yf
import pandas as pd

def evaluate_stock(ticker):
    """
    Evaluates whether a stock is a worthwhile investment based on criteria:
    - Low volatility (beta < 1)
    - Positive growth potential (positive revenue/earnings growth, reasonable P/E ratio)
    - Dividend payments (if applicable)
    """
    # Fetch stock data from Yahoo Finance
    stock = yf.Ticker(ticker)
    info = stock.info
    
    try:
        # Fetch relevant data
        beta = info.get('beta', None)
        pe_ratio = info.get('trailingPE', None)
        dividend_yield = info.get('dividendYield', None)
        revenue_growth = info.get('revenueGrowth', None)
        earnings_growth = info.get('earningsGrowth', None)

        # Criteria Check
        is_low_risk = beta is not None and beta < 1
        has_growth_potential = (revenue_growth is not None and revenue_growth > 0) or (earnings_growth is not None and earnings_growth > 0)
        pays_dividends = dividend_yield is not None and dividend_yield > 0

        # Evaluation Logic
        if is_low_risk and has_growth_potential:
            if pays_dividends:
                result = f"Low risk, Growth potential, Pays dividends (Yield: {dividend_yield:.2%})"
            else:
                result = "Low risk, Growth potential, Does not pay dividends"
        else:
            result = "Not a suitable investment based on current criteria."
        
        return {
            'Ticker': ticker,
            'Beta': beta,
            'PE Ratio': pe_ratio,
            'Revenue Growth': revenue_growth,
            'Earnings Growth': earnings_growth,
            'Dividend Yield': dividend_yield,
            'Evaluation': result
        }
    
    except Exception as e:
        return {'Ticker': ticker, 'Error': str(e)}

def evaluate_multiple_stocks(tickers):
    """
    Evaluates a list of stocks and returns the results as a DataFrame.
    """
    results = []
    for ticker in tickers:
        result = evaluate_stock(ticker)
        results.append(result)
    return pd.DataFrame(results)

def export_to_excel(dataframe, file_name='investment_evaluation.xlsx'):
    """
    Exports the evaluation results to an Excel file.
    """
    dataframe.to_excel(file_name, index=False)
    print(f"Results exported to {file_name}")

# List of stock tickers to evaluate
tickers = ['DOC','FPH','FSLR','KIM','LFT','CNDT','CIO','CCSI']

# Evaluate stocks and export results to Excel
df = evaluate_multiple_stocks(tickers)
export_to_excel(df)
