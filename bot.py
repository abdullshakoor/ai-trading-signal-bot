import requests
import pandas as pd

def get_binance_data(symbol="BTCUSDT", interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def calculate_indicators(df):
    df['ema_fast'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=21, adjust=False).mean()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def generate_signal():
    df = get_binance_data()
    df = calculate_indicators(df)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    fast_ema = latest['ema_fast']
    slow_ema = latest['ema_slow']
    rsi = latest['rsi']
    price = latest['close']
    
    signal = "NEUTRAL"
    if prev['ema_fast'] <= prev['ema_slow'] and fast_ema > slow_ema and rsi > 50:
        signal = "BUY"
    elif prev['ema_fast'] >= prev['ema_slow'] and fast_ema < slow_ema and rsi < 50:
        signal = "SELL"
        
    print("=========================================", flush=True)
    print(f"PAIR: BTC/USDT", flush=True)
    print(f"PRICE: ${price:.2f}", flush=True)
    print(f"EMA 9: {fast_ema:.2f} | EMA 21: {slow_ema:.2f}", flush=True)
    print(f"RSI (14): {rsi:.2f}", flush=True)
    print(f"SIGNAL: {signal}", flush=True)
    print("=========================================", flush=True)

if __name__ == "__main__":
    generate_signal()
  
