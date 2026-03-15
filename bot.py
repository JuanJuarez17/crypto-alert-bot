import os
import time
import requests
from twilio.rest import Client

# ── Configuración ─────────────────────────────────────────────────
BINANCE_API_KEY    = os.environ.get("BINANCE_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM        = os.environ.get("TWILIO_FROM")   # whatsapp:+14155238886
TWILIO_TO          = os.environ.get("TWILIO_TO")     # whatsapp:+54XXXXXXXXXX

# ── Niveles de alerta ─────────────────────────────────────────────
ALERTAS = {
    "SOLUSDT": {
        "take_profit": 91.87,
        "stop_loss":   84.00,
        "entrada":     87.95,
    },
    "BTCUSDT": {
        "take_profit": 72500.0,
        "stop_loss":   69000.0,
        "entrada":     70590.02,
    },
}

# ── Estado para no spamear el mismo mensaje ────────────────────────
alertas_enviadas = {symbol: set() for symbol in ALERTAS}

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])

def send_whatsapp(mensaje):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body=mensaje
    )
    print(f"[WS enviado] {mensaje}")

def calcular_pnl(precio_actual, entrada, monto):
    pnl = (precio_actual - entrada) / entrada * monto
    pct = (precio_actual - entrada) / entrada * 100
    return pnl, pct

def verificar_alertas():
    for symbol, niveles in ALERTAS.items():
        try:
            precio = get_price(symbol)
            nombre = symbol.replace("USDT", "")
            montos = {"SOL": 29.99, "BTC": 5.65}
            monto  = montos.get(nombre, 0)
            pnl, pct = calcular_pnl(precio, niveles["entrada"], monto)
            print(f"[{nombre}] Precio: ${precio:,.2f} | P&L: ${pnl:+.2f} ({pct:+.1f}%)")

            # ── Take Profit ──
            if precio >= niveles["take_profit"] and "tp" not in alertas_enviadas[symbol]:
                msg = (
                    f"🟢 *{nombre} — TAKE PROFIT ALCANZADO*\n"
                    f"Precio actual: ${precio:,.2f}\n"
                    f"Target: ${niveles['take_profit']:,.2f}\n"
                    f"P&L estimado: ${pnl:+.2f} ({pct:+.1f}%)\n\n"
                    f"✅ La orden OCO debería haberse ejecutado.\n"
                    f"Verificá en Binance y cerrá si no se ejecutó."
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("tp")

            # ── Stop Loss ──
            elif precio <= niveles["stop_loss"] and "sl" not in alertas_enviadas[symbol]:
                msg = (
                    f"🔴 *{nombre} — STOP LOSS ALCANZADO*\n"
                    f"Precio actual: ${precio:,.2f}\n"
                    f"Stop: ${niveles['stop_loss']:,.2f}\n"
                    f"P&L estimado: ${pnl:+.2f} ({pct:+.1f}%)\n\n"
                    f"⚠️ La orden OCO debería haberse ejecutado.\n"
                    f"Verificá en Binance y cerrá si no se ejecutó."
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("sl")

            # ── Alerta previa: 1% antes del stop ──
            elif precio <= (niveles["stop_loss"] * 1.01) and "sl_warning" not in alertas_enviadas[symbol]:
                msg = (
                    f"⚠️ *{nombre} — CERCA DEL STOP LOSS*\n"
                    f"Precio actual: ${precio:,.2f}\n"
                    f"Stop Loss en: ${niveles['stop_loss']:,.2f}\n"
                    f"Diferencia: ${precio - niveles['stop_loss']:,.2f}\n\n"
                    f"Mantené la calma, la OCO está activa."
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("sl_warning")

        except Exception as e:
            print(f"[ERROR {symbol}] {e}")

def main():
    print("🤖 Bot de alertas cripto iniciado...")
    send_whatsapp(
        "🤖 *Bot de alertas activado*\n\n"
        "Monitoreando:\n"
        f"• SOL | TP: $91.87 | SL: $84.00\n"
        f"• BTC | TP: $72,500 | SL: $69,000\n\n"
        "Te avisaré cuando se alcance algún nivel. 🚀"
    )
    while True:
        verificar_alertas()
        time.sleep(60)  # Chequea cada 60 segundos

if __name__ == "__main__":
    main()
