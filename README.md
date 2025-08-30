# entropy-aquarium
entropy-aquarium
## Client-only Kiosk
- File: visualization/kiosk_client.html
- Run locally: `python -m http.server 8000` → open http://127.0.0.1:8000/visualization/kiosk_client.html
- Sources: Synthetic, Wikipedia Recent Changes (SSE), Bitstamp BTCUSD (WS), Binance BTC (WS), Coingecko BTC (HTTP), User Interaction
- Uniform update rate via RateAdapter (change with `?hz=15`)
