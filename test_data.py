import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)

# Number of trades
num_trades = 10000

# List of S&P 500 companies' tickers (sample)
tickers = ['MSFT','AAPL','NVDA','GOOG','GOOGL','AMZN','META','BRK.B','LLY','TSLA','AVGO','JPM','WMT','V','XOM','UNH','MA','ORCL','PG','COST','JNJ','HD','MRK','BAC','NFLX','ABBV','CVX','AMD','KO','CRM','ADBE','QCOM','PEP','TMUS','LIN','WFC','EA','YUM','CTVA','FAST','GLW','FANG','LULU','CNC','GEHC','GIS','IT','NDAQ','KVUE','SYY','HPQ','EXC','BKR','CTSH','MLM','DD','BIIB','EXR','XYL','HWM','DFS','VMC','ON','VST','LVS','GRMN','ADM','ED','LYB','ROK','DAL','EFX','CSGP','PPG','HIG','TRGP','HAL','CDW','XEL','VICI','ANSS','DVN','AVB','MTD','DG','RMD','TSCO','WAB','EIX','HPE','CBRE','NTAP','IRM','WTW','TTWO','EBAY','BRO','FTV','TROW','CHD','EQR','WDC','AWK','FITB','MTB','RJF','WEC','IFF','FSLR','ROL','GPN','KEYS','DOV','DECK','BR','TER','WST','VLTO','CAH','NVR','DLTR','AXON','DTE','ETR','PTC','FE','CCL','STT','INVH','PHM','ZBH','LYV','STE','TYL','STX','VTR','SBAC','ARE','HUBB','WRB','GDDY','PPL','ES',
'AVY','DRI','HOLX','ATO','J','BAX','MOH','EXPD','LH','SWKS','COO','NTRS','WAT','HRL','L','CLX','LUV','TXT','JBHT','NRG','BLDR','MAA','CFG','EG','EQT','PKG','ZBRA','FDS','EXPE','MRO','BG','FOX','FOXA','DGX','UAL','GEN','NWS','NWSA','IP','IEX','CE','MAS','AKAM','DOC','AMCR','PODD','TRMB','ENPH','CAG','MGM','CPB','SNA','UDR','WRK','JBL','KEY','LNT','NDSN','KIM','INCY','RVTY','NI','CF','AES','SWK','PNR','HST','VTRS','EVRG','DVA','JNPR','JKHY','AOS','LW','ALB','SJM','BEN','POOL','CPT','QRVO','REG','TECH','KMX','EMN','LKQ','RL','EPAM','UHS','IPG','TAP','APA','CRL','CTLT','CHRW','ALLE','FFIV','TFX','HII','WYNN','WBA','BXP','TPR','MOS','PNW','SOLV','GNRC','AIZ','HSIC','FRT','BBWI','PAYC','CZR','HAS','MTCH','BIO','PARA','NCLH','DAY','MKTX','GL','AAL','BWA','MHK','FMC','IVZ','ETSY']

# Generate random trade data
data = []
start_date = datetime(2021, 1, 1)
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
