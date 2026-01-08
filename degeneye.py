import os
import json
import time
import threading
import websocket
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable not set!")

# Example WebSocket: Binance BTC/USDT trade stream
WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

latest_price = None  # Shared variable for WebSocket updates

# =========================
# WEBSOCKET HANDLER
# =========================
def on_ws_message(ws, message):
    global latest_price
    try:
        data = json.loads(message)
        latest_price = float(data.get("p", 0))
    except Exception as e:
        print("Error parsing WS message:", e)

def on_ws_open(ws):
    print("✅ WebSocket connected")

def on_ws_error(ws, error):
    print("❌ WebSocket error:", error)

def on_ws_close(ws, close_status_code, close_msg):
    print(f"⚠️ WebSocket closed: {close_status_code} - {close_msg}")

def start_websocket():
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_message=on_ws_message,
                on_open=on_ws_open,
                on_error=on_ws_error,
                on_close=on_ws_close,
            )
            ws.run_forever()
        except Exception as e:
            print("WebSocket crashed, reconnecting in 5s...", e)
            time.sleep(5)

# =========================
# TELEGRAM COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👁️ DegenEye is online.\nUse /price to get live BTC price."
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if latest_price:
        await update.message.reply_text(f"📈 BTC/USDT (live): ${latest_price}")
    else:
        await update.message.reply_text("⏳ Price not available yet, try again.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot is alive.")

# =========================
# MAIN
# =========================
def main():
    # Start WebSocket in a background daemon thread
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    # Build Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("ping", ping))

    print("🤖 DegenEye bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
