import pandas as pd
import numpy as np
import talib as ta
import yfinance as yf
from degiroapi import DeGiro
from degiroapi.product import Product
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize DeGiro API
degiro = DeGiro()
degiro.login("your_username", "your_password")

def get_stock_data(product_id, interval, duration):
    try:
        data = degiro.real_time_price(product_id, interval, duration)['data']
        df = pd.DataFrame(data)
        df.columns = ['timestamp', 'close', 'high', 'low', 'open', 'volume']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        if df.isnull().values.any():
            logging.warning(f'Missing data detected for product_id {product_id}.')
        return df
    except KeyError as e:
        logging.error(f"KeyError fetching stock data: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError fetching stock data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching stock data: {e}")
    return pd.DataFrame()

def apply_strategy(data):
    if data.empty:
        logging.warning("Empty data, skipping strategy application.")
        return data
    
    # Calculate MACD
    data['macd'], data['macd_signal'], data['macd_hist'] = ta.MACD(data['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    # Calculate Moving Averages
    data['50ma'] = ta.SMA(data['close'], timeperiod=50)
    data['100ma'] = ta.SMA(data['close'], timeperiod=100)
    data['200ma'] = ta.SMA(data['close'], timeperiod=200)
    
    # Calculate VWAP
    data['vwap'] = (data['volume'] * (data['high'] + data['low'] + data['close']) / 3).cumsum() / data['volume'].cumsum()
    
    # Calculate RSI
    data['rsi'] = ta.RSI(data['close'], timeperiod=14)
    
    # Calculate Bollinger Bands
    data['upper_band'], data['middle_band'], data['lower_band'] = ta.BBANDS(data['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    # Calculate volatility (using Bollinger Bands width)
    data['volatility'] = (data['upper_band'] - data['lower_band']) / data['middle_band']
    
    # Entry Signal: MACD crossover and other conditions
    data['signal'] = np.where(
        (data['macd'] > data['macd_signal']) & 
        (data['close'] > data['50ma']) & 
        (data['close'] > data['100ma']) & 
        (data['close'] > data['200ma']) & 
        (data['volume'] > data['volume'].rolling(20).mean()) & 
        (data['close'] > data['vwap']) & 
        (data['rsi'] < 70) &  # Avoid buying in overbought conditions
        (data['volatility'] < 0.1),  # Avoid very volatile stocks
        1, 0)
    
    return data

def execute_buy_order(product_id, quantity):
    try:
        funds = degiro.getdata(degiro.Data.Type.CASHFUNDS)
        available_funds = next((f['value'] for f in funds['cashFunds'] if f['currencyCode'] == 'USD'), 0)
        if available_funds < (quantity * get_stock_data(product_id, 'P1D', '1D')['close'].iloc[-1]):
            logging.error(f"Insufficient funds to buy {quantity} shares of product_id {product_id}")
            return False

        if not degiro.is_market_open():
            logging.error("Market is closed, unable to place order.")
            return False
        
        result = degiro.buy_order(product_id, quantity)
        if result['status'] == 'rejected':
            logging.error(f"Buy order rejected for product_id {product_id}, quantity {quantity}")
            return False
        
        logging.info(f"Buy order executed for product_id {product_id}, quantity {quantity}")
        return True
    except KeyError as e:
        logging.error(f"KeyError executing buy order: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError executing buy order: {e}")
    except Exception as e:
        logging.error(f"Unexpected error executing buy order: {e}")
    return False

def execute_sell_order(product_id, quantity):
    try:
        result = degiro.sell_order(product_id, quantity)
        if result['status'] == 'rejected':
            logging.error(f"Sell order rejected for product_id {product_id}, quantity {quantity}")
            return False
        
        logging.info(f"Sell order executed for product_id {product_id}, quantity {quantity}")
        return True
    except KeyError as e:
        logging.error(f"KeyError executing sell order: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError executing sell order: {e}")
    except Exception as e:
        logging.error(f"Unexpected error executing sell order: {e}")
    return False

def execute_trades(data, product_id):
    for i in range(len(data)):
        if data['signal'].iloc[i] == 1:
            if execute_buy_order(product_id, 10):
                logging.info(f"Buy signal triggered for product_id {product_id} at index {i}")
        elif data['signal'].iloc[i] == -1:
            if execute_sell_order(product_id, 10):
                logging.info(f"Sell signal triggered for product_id {product_id} at index {i}")

def fetch_fundamentals(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        ratios = {
            'pe_ratio': info.get('trailingPE', None),
            'de_ratio': info.get('debtToEquity', None),
            'sharpe_ratio': info.get('sharpeRatio', None),
            'sector': info.get('sector', None)
        }
        return ratios
    except KeyError as e:
        logging.error(f"KeyError fetching fundamentals for {symbol}: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError fetching fundamentals for {symbol}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching fundamentals for {symbol}: {e}")
    return {}

def is_stock_undervalued(ratios):
    return (ratios['pe_ratio'] is not None and ratios['pe_ratio'] < 15) and \
           (ratios['de_ratio'] is not None and ratios['de_ratio'] < 0.5) and \
           (ratios['sharpe_ratio'] is not None and ratios['sharpe_ratio'] > 1)

def add_dynamic_stop_loss(data, initial_stop_loss_pct=0.05):
    data['dynamic_stop_loss'] = data['close'] * (1 - initial_stop_loss_pct)
    highest_close = data['close'].cummax()
    data['dynamic_stop_loss'] = highest_close * (1 - initial_stop_loss_pct)
    return data

def check_portfolio_diversification(portfolio, sector):
    sectors = [stock['sector'] for stock in portfolio]
    sector_count = sectors.count(sector)
    return sector_count < 3  # Allow up to 3 stocks from the same sector

def fetch_and_apply_strategy(symbol, product_id, interval, duration, portfolio):
    data = get_stock_data(product_id, interval, duration)
    data = apply_strategy(data)

    if not data.empty and data['signal'].iloc[-1] == 1:
        ratios = fetch_fundamentals(symbol)
        if is_stock_undervalued(ratios) and check_portfolio_diversification(portfolio, ratios['sector']):
            return True
    return False

def main():
    markets = {
        'FTSE 100': 'FTSE100',
        'Nikkei 225': 'N225'
    }
    
    symbol_usa = 'AAPL'
    interval = 'P1D'  # Daily interval
    duration = '1Y'  # 1 Year
    max_buy_orders = 50
    buy_order_count = 0

    signals = []
    portfolio = []

    for market_name, symbol in markets.items():
        try:
            products = degiro.search_products(symbol)
            product_id = products[0]['id']
            valid_signal = fetch_and_apply_strategy(symbol, product_id, interval, duration, portfolio)
            if valid_signal:
                signals.append((symbol, product_id))
        except KeyError as e:
            logging.error(f"KeyError processing market {market_name}: {e}")
        except ConnectionError as e:
            logging.error(f"ConnectionError processing market {market_name}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error processing market {market_name}: {e}")

    if signals and buy_order_count < max_buy_orders:
        try:
            products = degiro.search_products(symbol_usa)
            product_id_usa = products[0]['id']
            data_usa = get_stock_data(product_id_usa, interval, duration)
            data_usa = apply_strategy(data_usa)
            data_usa = add_dynamic_stop_loss(data_usa)
            
            if not data_usa.empty and data_usa['signal'].iloc[-1] == 1:
                ratios_usa = fetch_fundamentals(symbol_usa)
                if is_stock_undervalued(ratios_usa) and check_portfolio_diversification(portfolio, ratios_usa['sector']):
                    if execute_buy_order(product_id_usa, 10):
                        buy_order_count += 1
                        portfolio.append(ratios_usa)
                    
                    for i in range(len(data_usa)):
                        current_price = data_usa['close'].iloc[i]
                        if current_price <= data_usa['dynamic_stop_loss'].iloc[i]:
                            if execute_sell_order(product_id_usa, 10):
                                break

        except KeyError as e:
            logging.error(f"KeyError processing USA market: {e}")
        except ConnectionError as e:
            logging.error(f"ConnectionError processing USA market: {e}")
        except Exception as e:
            logging.error(f"Unexpected error processing USA market: {e}")

if __name__ == "__main__":
    main()
