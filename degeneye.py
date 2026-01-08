import os
import json
import time
import threading
import websocket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable not set!")

# CoinCap WebSocket endpoint
WS_URL = "wss://ws.coincap.io/prices?assets=bitcoin,ethereum"

# Shared variables for prices
prices = {"bitcoin": None, "ethereum": None}

# =========================
# WEBSOCKET HANDLER
# =========================
def on_message(ws, message):
    try:
        data = json.loads(message)
        for coin, price in data.items():
            prices[coin] = float(price)
        # Optional: print for debugging
        # print("Updated prices:", prices)
    except Exception as e:
        print("❌ WS message error:", e)

def on_open(ws):
    print("✅ CoinCap WebSocket connected")

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"⚠️ WebSocket closed: {close_status_code} - {close_msg}")

def start_websocket():
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_message=on_message,
                on_open=on_open,
                on_error=on_error,
                on_close=on_close,
            )
            ws.run_forever()
        except Exception as e:
            print("❌ WS crashed, reconnecting in 5s...", e)
            time.sleep(5)

# =========================
# TELEGRAM COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👁️ DegenEye is online.\nUse /price to get live BTC & ETH prices."
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc = prices.get("bitcoin")
    eth = prices.get("ethereum")
    if btc and eth:
        await update.message.reply_text(f"📈 BTC: ${btc}\n📈 ETH: ${eth}")
    else:
        await update.message.reply_text("⏳ Prices not available yet, try again in a few seconds.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is alive.")

# =========================
# MAIN FUNCTION
# =========================
def main():
    # Start WebSocket in a background thread
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    # Telegram bot setup
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("ping", ping))

    print("🤖 DegenEye bot running with CoinCap WebSocket...")
    app.run_polling()

if __name__ == "__main__":
    main()
