import yfinance as yf

def fetch_stock_data(symbols):
    stock_data = {}

    for symbol in symbols:
        stock = yf.Ticker(symbol)
        data = stock.info
        stock_data[symbol] = data
    
    return stock_data

def main():
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]  # Add more symbols as needed

    try:
        stock_data = fetch_stock_data(symbols)
        for symbol, data in stock_data.items():
            print(f"Data for {symbol}:")
            print(f"Name: {data['shortName']}")
            print(f"Market Cap: {data['marketCap']}")
            print(f"Previous Close: {data['previousClose']}")
            print(f"Open: {data['open']}")
            print(f"52 Week High: {data['fiftyTwoWeekHigh']}")
            print(f"52 Week Low: {data['fiftyTwoWeekLow']}")
            print(f"Dividend Yield: {data.get('dividendYield', 'N/A')}")
            print(f"PE Ratio: {data.get('trailingPE', 'N/A')}")
            print()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
