import os
import pandas as pd
import numpy as np
import yfinance as yf
import talib as ta
import logging
from datetime import datetime, timedelta
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get real-time data from Yahoo Finance
def get_real_time_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d', interval='1m')
        if data.isnull().values.any():
            logging.warning(f'Missing data detected for symbol {symbol}.')
        return data
    except Exception as e:
        logging.error(f"Error fetching real-time data for symbol {symbol}: {e}")
    return pd.DataFrame()

def fetch_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'symbol': symbol,
            'sector': info.get('sector', 'N/A'),
            'marketCap': info.get('marketCap', 'N/A'),
            'forwardPE': info.get('forwardPE', 'N/A'),
            'debtToEquity': info.get('debtToEquity', 'N/A'),
            'sharpeRatio': info.get('sharpeRatio', 'N/A'),
            'trailingPegRatio': info.get('trailingPegRatio', 'N/A'),
        }
    except Exception as e:
        logging.error(f"Error fetching fundamentals for symbol {symbol}: {e}")
    return {}

def apply_strategy(data):
    if data.empty:
        logging.warning("Empty data, skipping strategy application.")
        return data

    # Calculate MACD
    data['macd'], data['macd_signal'], data['macd_hist'] = ta.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    
    # Calculate Moving Averages
    data['50ma'] = ta.SMA(data['Close'], timeperiod=50)
    data['100ma'] = ta.SMA(data['Close'], timeperiod=100)
    data['200ma'] = ta.SMA(data['Close'], timeperiod=200)
    
    # Calculate VWAP
    data['vwap'] = (data['Volume'] * (data['High'] + data['Low'] + data['Close']) / 3).cumsum() / data['Volume'].cumsum()
    
    # Calculate RSI
    data['rsi'] = ta.RSI(data['Close'], timeperiod=14)
    
    # Calculate Bollinger Bands
    data['upper_band'], data['middle_band'], data['lower_band'] = ta.BBANDS(data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    
    # Calculate Stochastic Oscillator
    data['slowk'], data['slowd'] = ta.STOCH(data['High'], data['Low'], data['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    
    # Calculate On Balance Volume
    data['obv'] = ta.OBV(data['Close'], data['Volume'])
    
    # Calculate Percentage Price Oscillator
    data['ppo'] = ta.PPO(data['Close'], fastperiod=12, slowperiod=26, matype=0)
    
    # Calculate Parabolic SAR
    data['psar'] = ta.SAR(data['High'], data['Low'], acceleration=0.02, maximum=0.2)
    
    # Calculate Average Directional Index
    data['adx'] = ta.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
    
    # Calculate volatility (using Bollinger Bands width)
    data['volatility'] = (data['upper_band'] - data['lower_band']) / data['middle_band']
    
    # Entry Signal: MACD crossover and other conditions
    data['signal'] = np.where(
        (data['macd'] > data['macd_signal']) & 
        (data['Close'] > data['50ma']) & 
        (data['Close'] > data['100ma']) & 
        (data['Close'] > data['200ma']) & 
        (data['Volume'] > data['Volume'].rolling(20).mean()) & 
        (data['Close'] > data['vwap']) & 
        (data['rsi'] < 70) &  # Avoid buying in overbought conditions
        (data['volatility'] < 0.1),  # Avoid very volatile stocks
        1, 0)
    
    return data

def add_dynamic_stop_loss(data, initial_stop_loss_pct=0.05):
    data['dynamic_stop_loss'] = data['Close'] * (1 - initial_stop_loss_pct)
    highest_close = data['Close'].cummax()
    data['dynamic_stop_loss'] = highest_close * (1 - initial_stop_loss_pct)
    return data

def position_sizing(portfolio_value, volatility, stop_loss_pct, risk_pct_per_trade=0.01):
    risk_per_trade = portfolio_value * risk_pct_per_trade
    position_size = risk_per_trade / (volatility * stop_loss_pct)
    return int(position_size)

def continuous_monitoring(symbols, portfolio):
    while True:
        for symbol in symbols:
            try:
                data = get_real_time_data(symbol)
                data = apply_strategy(data)
                data = add_dynamic_stop_loss(data)

                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    for i in range(len(portfolio)):
                        stock = portfolio[i]
                        if current_price <= stock['dynamic_stop_loss']:
                            logging.info(f"Sell signal triggered for {stock['symbol']} at {current_price} (stop-loss)")
                            portfolio.pop(i)
                            break
                        elif current_price >= stock['take_profit_price']:
                            logging.info(f"Sell signal triggered for {stock['symbol']} at {current_price} (take-profit)")
                            portfolio.pop(i)
                            break

            except Exception as e:
                logging.error(f"Error during continuous monitoring for symbol {symbol}: {e}")
        
        time.sleep(60)  # Check every minute

def display_key_financial_data(symbols):
    financial_data = []
    for symbol in symbols:
        data = fetch_fundamentals(symbol)
        if data:
            financial_data.append(data)

    df = pd.DataFrame(financial_data)
    return df

# Create Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Key Financial Data"),
            dcc.Dropdown(
                id='symbol-dropdown',
                options=[{'label': symbol, 'value': symbol} for symbol in ['AAPL', 'MSFT', 'GOOG']],
                value=['AAPL', 'MSFT', 'GOOG'],
                multi=True
            ),
            dbc.Table(id='financial-data-table')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H2("Real-Time Data"),
            dcc.Dropdown(
                id='realtime-symbol-dropdown',
                options=[{'label': symbol, 'value': symbol} for symbol in ['AAPL', 'MSFT', 'GOOG']],
                value='AAPL'
            ),
            dcc.Graph(id='realtime-price-graph'),
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # in milliseconds
                n_intervals=0
            )
        ])
    ])
])

@app.callback(
    Output('financial-data-table', 'children'),
    [Input('symbol-dropdown', 'value')]
)
def update_table(selected_symbols):
    df = display_key_financial_data(selected_symbols)
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    return table

@app.callback(
    Output('realtime-price-graph', 'figure'),
    [Input('interval-component', 'n_intervals'), Input('realtime-symbol-dropdown', 'value')]
)
def update_graph(n, selected_symbol):
    df = get_real_time_data(selected_symbol)
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='candlestick'
    ))
    fig.update_layout(title=f'Real-Time Price Data for {selected_symbol}', xaxis_title='Time', yaxis_title='Price')
    return fig

if __name__ == "__main__":
    symbols = ['AAPL', 'MSFT', 'GOOG']  # Define the symbols you want to monitor
    portfolio = []
    
    app.run_server(debug=True, use_reloader=False)
