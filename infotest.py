import yfinance as yf

msft = yf.Ticker("MSFT")

# get all stock info
msft.info

print(msft.info)