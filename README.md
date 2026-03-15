# Crypto Alert Bot — BNB & BTC

Bot que monitorea precios en Binance y envía alertas por WhatsApp via Twilio.

## Variables de entorno requeridas en Railway

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| BINANCE_API_KEY | Tu API Key de Binance | abc123... |
| TWILIO_ACCOUNT_SID | Account SID de Twilio | ACxxxxxxx |
| TWILIO_AUTH_TOKEN | Auth Token de Twilio | xxxxxxx |
| TWILIO_FROM | Número Twilio WhatsApp | whatsapp:+14155238886 |
| TWILIO_TO | Tu número de WhatsApp | whatsapp:+54911XXXXXXXX |

## Alertas configuradas

- **BNB**: Take Profit $665 | Stop Loss $641 | Aviso previo $647
- **BTC**: Take Profit $72,500 | Stop Loss $69,000 | Aviso previo $69,690

## Frecuencia de chequeo
Cada 60 segundos.
