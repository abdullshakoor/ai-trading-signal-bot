import os
import requests
import pandas as pd

# =========================
# MARKET SETTINGS
# =========================
SYMBOL = "BTCUSDT"
INTERVAL = "1m"
LIMIT = 100

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_market_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "buy_volume", "buy_quote_volume", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df


def make_signal(df):
    df["EMA9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["close"].ewm(span=21, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    last = df.iloc[-1]
    price = last["close"]
    ema9 = last["EMA9"]
    ema21 = last["EMA21"]
    rsi = last["RSI"]

    if ema9 > ema21 and 50 < rsi < 70:
        return "BUY", price, rsi

    if ema9 < ema21 and 30 < rsi < 50:
        return "SELL", price, rsi

    return "WAIT", price, rsi


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Warning: BOT_TOKEN or CHAT_ID is missing in GitHub Secrets.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload, timeout=10)


def main():
    print("Checking AI Trading Signal...")
    try:
        df = get_market_data()
        signal, price, rsi = make_signal(df)

        print(f"Signal: {signal} | Price: {price:.2f} | RSI: {rsi:.2f}")

        if signal in ["BUY", "SELL"]:
            message = (
                "📊 TRADING SIGNAL\n\n"
                f"💹 Pair: {SYMBOL}\n"
                f"📈 Signal: {signal}\n"
                f"💰 Price: {price:.2f}\n"
                f"📊 RSI: {rsi:.2f}\n"
                f"⏱ Timeframe: {INTERVAL}\n\n"
                "⚠️ Signal only — trade at your own risk."
            )
            send_telegram(message)
            print("Telegram alert sent successfully!")
        else:
            print("No actionable signal (Market is WAIT). Exiting run.")

    except Exception as e:
        print("Error during execution:", e)


if __name__ == "__main__":
    main()
    
