import os
import json
import threading
import websocket
import requests

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("8548653359:AAGiyAqDzt1NkoZpyZVgpkjskuLARFtYjp0")  # Railway ENV VAR
CHAT_CACHE = set()

# Example WebSocket (Binance BTC/USDT)
WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

latest_price = None

# =========================
# WEBSOCKET HANDLER
# =========================

def on_ws_message(ws, message):
    global latest_price
    data = json.loads(message)
    latest_price = float(data["p"])

def on_ws_open(ws):
    print("✅ WebSocket connected")

def on_ws_error(ws, error):
    print("❌ WebSocket error:", error)

def start_websocket():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_message=on_ws_message,
        on_open=on_ws_open,
        on_error=on_ws_error
    )
    ws.run_forever()

# =========================
# TELEGRAM COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_CACHE.add(update.effective_chat.id)
    await update.message.reply_text(
        "👁️ DegenEye is online.\nUse /price to get live BTC price."
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if latest_price:
        await update.message.reply_text(
            f"📈 BTC/USDT (live): ${latest_price}"
        )
    else:
        await update.message.reply_text(
            "⏳ Price not available yet, try again."
        )

# =========================
# MAIN
# =========================

def main():
    # Start WebSocket in background thread
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    # Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    print("🤖 DegenEye bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()