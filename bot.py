import json
import urllib.request
import time

SYMBOL = "BTCUSDT"
INTERVAL = "5m"

def get_prices():
    url = (
        "https://api.binance.com/api/v3/klines"
        f"?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
    )

    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode())

    return [float(candle[4]) for candle in data]


def ema(prices, period):
    multiplier = 2 / (period + 1)
    value = sum(prices[:period]) / period

    for price in prices[period:]:
        value = (price - value) * multiplier + value

    return value


def rsi(prices, period=14):
    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def get_signal():
    prices = get_prices()

    current = prices[-1]
    fast_ema = ema(prices, 9)
    slow_ema = ema(prices, 21)
    current_rsi = rsi(prices)

    if fast_ema > slow_ema and current_rsi > 50:
        signal = "BUY"
    elif fast_ema < slow_ema and current_rsi < 50:
        signal = "SELL"
    else:
        signal = "WAIT"

    print("\n===== AI TRADING SIGNAL =====")
    print("Pair:", SYMBOL)
    print("Timeframe:", INTERVAL)
    print("Price:", current)
    print("EMA 9:", round(fast_ema, 2))
    print("EMA 21:", round(slow_ema, 2))
    print("RSI:", round(current_rsi, 2))
    print("SIGNAL:", signal)
    print("=============================\n")


if __name__ == "__main__":
    while True:
        try:
            get_signal()
        except Exception as error:
            print("Error:", error)

        time.sleep(300)
