import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
WS_BASE_URL = os.getenv("WS_BASE_URL", "ws://localhost:8000")

DEFAULT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
    "DOGEUSDT", "SOLUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT"
]