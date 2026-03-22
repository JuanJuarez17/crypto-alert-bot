import os
import time
import requests
from twilio.rest import Client

# ── Configuración ─────────────────────────────────────────────────
BINANCE_API_KEY    = os.environ.get("BINANCE_API_KEY")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM        = os.environ.get("TWILIO_FROM")
TWILIO_TO          = os.environ.get("TWILIO_TO")

# ── Niveles de alerta ─────────────────────────────────────────────
ALERTAS = {
    "BTCUSDT": {
        "take_profit": 78338.0,
        "stop_loss":   61900.0,
        "entrada":     68120.10,
        "monto":       44.9593,
    },
    "XRPUSDT": {
        "take_profit": 1.665,
        "stop_loss":   1.251,
        "entrada":     1.3884,
        "monto":       24.9912,
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
            pnl, pct = calcular_pnl(precio, niveles["entrada"], niveles["monto"])
            print(f"[{nombre}] Precio: ${precio:,.4f} | P&L: ${pnl:+.2f} ({pct:+.1f}%)")

            # ── Take Profit ──
            if precio >= niveles["take_profit"] and "tp" not in alertas_enviadas[symbol]:
                msg = (
                    f"🟢 *{nombre} — TAKE PROFIT ALCANZADO*\n"
                    f"Precio actual: ${precio:,.4f}\n"
                    f"Target: ${niveles['take_profit']:,.4f}\n"
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
                    f"Precio actual: ${precio:,.4f}\n"
                    f"Stop: ${niveles['stop_loss']:,.4f}\n"
                    f"P&L estimado: ${pnl:+.2f} ({pct:+.1f}%)\n\n"
                    f"⚠️ La orden OCO debería haberse ejecutado.\n"
                    f"Verificá en Binance y cerrá si no se ejecutó."
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("sl")

            # ── Alerta previa: 5% antes del stop (mediano plazo) ──
            elif precio <= (niveles["stop_loss"] * 1.05) and "sl_warning" not in alertas_enviadas[symbol]:
                msg = (
                    f"⚠️ *{nombre} — CERCA DEL STOP LOSS*\n"
                    f"Precio actual: ${precio:,.4f}\n"
                    f"Stop Loss en: ${niveles['stop_loss']:,.4f}\n"
                    f"Diferencia: ${precio - niveles['stop_loss']:,.4f}\n\n"
                    f"Recordá: esta es una estrategia de mediano plazo.\n"
                    f"Mantené la calma, la OCO está activa."
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("sl_warning")

            # ── Alerta de progreso: cada 5% de avance hacia el TP ──
            elif pct >= 5.0 and "progress_5" not in alertas_enviadas[symbol]:
                msg = (
                    f"📈 *{nombre} — PROGRESO +5%*\n"
                    f"Precio actual: ${precio:,.4f}\n"
                    f"P&L estimado: ${pnl:+.2f} ({pct:+.1f}%)\n"
                    f"Take Profit en: ${niveles['take_profit']:,.4f}\n\n"
                    f"Vas bien, mantené la posición. 💪"
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("progress_5")

            elif pct >= 10.0 and "progress_10" not in alertas_enviadas[symbol]:
                msg = (
                    f"🚀 *{nombre} — PROGRESO +10%*\n"
                    f"Precio actual: ${precio:,.4f}\n"
                    f"P&L estimado: ${pnl:+.2f} ({pct:+.1f}%)\n"
                    f"Take Profit en: ${niveles['take_profit']:,.4f}\n\n"
                    f"Excelente, casi llegás al objetivo! 🎯"
                )
                send_whatsapp(msg)
                alertas_enviadas[symbol].add("progress_10")

        except Exception as e:
            print(f"[ERROR {symbol}] {e}")

def main():
    print("🤖 Bot de alertas cripto iniciado...")
    send_whatsapp(
        "🤖 *Bot de alertas activado — Mediano Plazo*\n\n"
        "Monitoreando:\n"
        f"• BTC | Entrada: $68,120 | TP: $78,338 (+15%) | SL: $61,900 (-9.1%)\n"
        f"• XRP | Entrada: $1.3884 | TP: $1.665 (+19.9%) | SL: $1.251 (-9.9%)\n\n"
        "Alertas configuradas:\n"
        "📈 Progreso a +5% y +10%\n"
        "⚠️ Aviso cuando falte 5% para el stop\n"
        "🟢 Take Profit alcanzado\n"
        "🔴 Stop Loss alcanzado\n\n"
        "Plazo estimado: 3 a 5 semanas. 💪"
    )
    while True:
        verificar_alertas()
        time.sleep(60)

if __name__ == "__main__":
    main()
