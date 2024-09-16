from degiroapi import DeGiro

class DegiroUserAgent(DeGiro):
  """Subclass of DeGiro that sets a custom User-Agent header."""

  def __init__(self):
    super().__init__()
    self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"

  def __request(self, method, url, headers={}, **kwargs):
    """Overrides the __request method to set the User-Agent header."""
    headers.setdefault('User-Agent', self.user_agent)
    return super().__request__(method, url, headers=headers, **kwargs)

def get_stock_data(degiro, ticker):
  """Fetches real-time stock data for a given ticker."""
  products = degiro.search_products(ticker)
  if not products:
    print(f"No product found for ticker {ticker}")
    return None
  product_id = products[0]['id']
  stock_data = degiro.real_time_price(product_id, degiroapi.Interval.Type.One_Day)
  return stock_data

def main():
  username = 'bubbaz35'
  password = 'Ozhmgptb35%'

  # Create an instance of DegiroUserAgent
  degiro = DegiroUserAgent()

  # Setting the base URL for the Irish portal
  degiro.__BASE_URL = "https://trader.degiro.ie"
  degiro.__LOGIN_URL = f"{degiro.__BASE_URL}/login/secure/login"

  try:
    degiro.login(username, password)
    print("Logged in successfully.")
  except Exception as e:
    print(f"An error occurred: {e}")

  try:
    # Replace 'YOUR_ACCOUNT_ID' with the actual ID from DeGiro
    portfolio = degiro.getdata(degiro.Data.Type.PORTFOLIO, True, account_id='YOUR_ACCOUNT_ID')
    print("Portfolio data:", portfolio)
  except Exception as e:
    print(f"An error occurred while retrieving the portfolio: {e}")

  # List of major stocks to fetch data for
  tickers = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'FB']  # Apple, Alphabet (Google), Amazon, Microsoft, Facebook

  # Fetch and print key data for each stock
  for ticker in tickers:
    stock_data = get_stock_data(degiro, ticker)
    if stock_data:
      print(f"Data for {ticker}:")
      print(stock_data)
    else:
      print(f"Failed to get data for {ticker}")

  degiro.logout()

if __name__ == "__main__":
  main()
