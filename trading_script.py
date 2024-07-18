import os
import pandas as pd
import numpy as np
import talib as ta
from degiroapi import DeGiro
from degiroapi.product import Product
import logging
from datetime import datetime, timedelta
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Secure login using access tokens
DEGIRO_USER = os.getenv('DEGIRO_USER')
DEGIRO_PASS = os.getenv('DEGIRO_PASS')

def generate_access_token(user, password):
    degiro = DeGiro()
    degiro.login(user, password)
    return degiro

degiro = generate_access_token(DEGIRO_USER, DEGIRO_PASS)

def get_real_time_data(product_id):
    try:
        data = degiro.real_time_price(product_id, interval="One_Day")['data']
        df = pd.DataFrame(data)
        df.columns = ['timestamp', 'close', 'high', 'low', 'open', 'volume']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        if df.isnull().values.any():
            logging.warning(f'Missing data detected for product_id {product_id}.')
        return df
    except KeyError as e:
        logging.error(f"KeyError fetching real-time data: {e}")
    except ConnectionError as e:
        logging.error(f"ConnectionError fetching real-time data: {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching real-time data: {e}")
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
    
    # Calculate Stochastic Oscillator
    data['slowk'], data['slowd'] = ta.STOCH(data['high'], data['low'], data['close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    
    # Calculate On Balance Volume
    data['obv'] = ta.OBV(data['close'], data['volume'])
    
    # Calculate Percentage Price Oscillator
    data['ppo'] = ta.PPO(data['close'], fastperiod=12, slowperiod=26, matype=0)
    
    # Calculate Parabolic SAR
    data['psar'] = ta.SAR(data['high'], data['low'], acceleration=0.02, maximum=0.2)
    
    # Calculate Average Directional Index
    data['adx'] = ta.ADX(data['high'], data['low'], data['close'], timeperiod=14)
    
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
        if available_funds < (quantity * get_real_time_data(product_id)['close'].iloc[-1]):
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

def add_dynamic_stop_loss(data, initial_stop_loss_pct=0.05):
    data['dynamic_stop_loss'] = data['close'] * (1 - initial_stop_loss_pct)
    highest_close = data['close'].cummax()
    data['dynamic_stop_loss'] = highest_close * (1 - initial_stop_loss_pct)
    return data

def position_sizing(portfolio_value, volatility, stop_loss_pct, risk_pct_per_trade=0.01):
    risk_per_trade = portfolio_value * risk_pct_per_trade
    position_size = risk_per_trade / (volatility * stop_loss_pct)
    return int(position_size)

def check_portfolio_diversification(portfolio, sector):
    sectors = [stock['sector'] for stock in portfolio]
    sector_count = sectors.count(sector)
    return sector_count < 3  # Allow up to 3 stocks from the same sector

def continuous_monitoring(symbols_usa, portfolio):
    while True:
        for symbol_usa in symbols_usa:
            try:
                products = degiro.search_products(symbol_usa)
                product_id_usa = products[0]['id']
                data_usa = get_real_time_data(product_id_usa)
                data_usa = apply_strategy(data_usa)
                data_usa = add_dynamic_stop_loss(data_usa)

                if not data_usa.empty:
                    current_price = data_usa['close'].iloc[-1]
                    for i in range(len(portfolio)):
                        stock = portfolio[i]
                        if current_price <= stock['dynamic_stop_loss']:
                            if execute_sell_order(product_id_usa, stock['quantity']):
                                portfolio.pop(i)
                                break
                        elif current_price >= stock['take_profit_price']:
                            if execute_sell_order(product_id_usa, stock['quantity']):
                                portfolio.pop(i)
                                break

            except KeyError as e:
                logging.error(f"KeyError during continuous monitoring: {e}")
            except ConnectionError as e:
                logging.error(f"ConnectionError during continuous monitoring: {e}")
            except Exception as e:
                logging.error(f"Unexpected error during continuous monitoring: {e}")
        
        time.sleep(60)  # Check every minute

def main():
    interval = 'P1D'
    duration = '1D'
    symbols_usa = ['AAPL', 'MSFT', 'GOOG']
    portfolio = []
    buy_order_count = 0
    daily_buy_limit = 50

    for symbol_usa in symbols_usa:
        try:
            if buy_order_count >= daily_buy_limit:
                logging.info("Daily buy limit reached. Exiting.")
                break

            products = degiro.search_products(symbol_usa)
            product_id_usa = products[0]['id']
            data_usa = get_real_time_data(product_id_usa)
            data_usa = apply_strategy(data_usa)
            data_usa = add_dynamic_stop_loss(data_usa)
            
            if not data_usa.empty and data_usa['signal'].iloc[-1] == 1:
                ratios_usa = degiro.product_info(product_id_usa)
                if check_portfolio_diversification(portfolio, ratios_usa['sector']):
                    position_size = position_sizing(100000, data_usa['volatility'].iloc[-1], 0.05)
                    if execute_buy_order(product_id_usa, position_size):
                        buy_order_count += 1
                        ratios_usa['quantity'] = position_size
                        ratios_usa['dynamic_stop_loss'] = data_usa['dynamic_stop_loss'].iloc[-1]
                        ratios_usa['take_profit_price'] = data_usa['close'].iloc[-1] * 1.1  # Example take-profit at 10% gain
                        portfolio.append(ratios_usa)
                    
                    continuous_monitoring(symbols_usa, portfolio)

        except KeyError as e:
            logging.error(f"KeyError processing USA market: {e}")
        except ConnectionError as e:
            logging.error(f"ConnectionError processing USA market: {e}")
        except Exception as e:
            logging.error(f"Unexpected error processing USA market: {e}")

if __name__ == "__main__":
    main()
