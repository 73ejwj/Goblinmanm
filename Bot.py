import requests, pandas as pd, time
from telegram import Bot

# 🔑 Replace these with your real keys
TWELVE_DATA_API_KEY = 'e53d4613f55a49ffa9bbd1f286bcf96c'
TELEGRAM_BOT_TOKEN = '7402049168:AAHHqn160fbAKHpYrQLMzG3B3Rh7z6I-Jjw'
TELEGRAM_CHAT_ID = 6793389809

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_candles(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=30&apikey={TWELVE_DATA_API_KEY}"
    res = requests.get(url).json()
    if 'values' not in res:
        return None
    df = pd.DataFrame(res['values'])
    df['close'] = df['close'].astype(float)
    return df

def check_rsi_signal(df):
    df['RSI'] = calculate_rsi(df['close'])
    rsi = df['RSI'].iloc[-1]
    if rsi < 30: return "BUY"
    if rsi > 70: return "SELL"
    return None

def send_signal(symbol, signal):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"{signal} signal for {symbol} (RSI)")

def run_bot():
    last_signal = {}
    symbols = ["EUR/USD", "GBP/USD", "USD/JPY"]
    while True:
        for sym in symbols:
            df = get_candles(sym)
            if df is None or len(df) < 15:
                continue
            sig = check_rsi_signal(df)
            if sig and last_signal.get(sym) != sig:
                send_signal(sym, sig)
                last_signal[sym] = sig
        time.sleep(60)

run_bot()
