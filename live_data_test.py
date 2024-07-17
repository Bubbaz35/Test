import yfinance as yf

def get_live_price(ticker: str) -> float:
  """
  Downloads 1 day of data for the given ticker symbol and retrieves the latest closing price.

  Args:
      ticker (str): The ticker symbol of the stock.

  Returns:
      float: The latest closing price of the stock, or None if an error occurs.
  """
  try:
    data = yf.download(ticker, period="1d")
    if data.empty:
      print(f"Invalid ticker or failed to retrieve data for {ticker}")
      return None
    live_price = data["Close"].tail(1).values[0]
    return live_price
  except (yf.DownloadError, KeyError) as e:
    print(f"Error fetching data for {ticker}: {e}")
    return None

# Define the list of ticker symbols
tickers = ["MSFT", "META", "TSLA", "F"]

# Use list comprehension to retrieve prices
prices = [get_live_price(ticker) for ticker in tickers]

# Print the results
for ticker, price in zip(tickers, prices):
  if price:
    print(f"Live price of {ticker}: ${price:.2f}")
  else:
    print(f"Failed to retrieve live price for {ticker}.")
