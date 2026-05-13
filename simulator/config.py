# simulator/config.py
import os
from dotenv import load_dotenv

load_dotenv()

#Event Hub connection
JSE_CONNECTION_STRING = os.getenv("JSE_EVENTHUB_CONNECTION_STRING")
JSE_EVENTHUB_NAME     = os.getenv("JSE_EVENTHUB_NAME", "equities-stream")

CRYPTO_CONNECTION_STRING = os.getenv("CRYPTO_EVENTHUB_CONNECTION_STRING")
CRYPTO_EVENTHUB_NAME     = os.getenv("CRYPTO_EVENTHUB_NAME", "crypto-equities")

# JSE Instruments
# Each instrument has:
#   base_price : realistic ZAR starting price
#   volatility : daily σ for GBM model (higher = more volatile)
#   sector     : for enrichment join in Stream Analytics

JSE_INSTRUMENTS = {
    "JSE:SOL": {"base_price": 23550, "volatility": 0.018, "sector": "Energy",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:NPN": {"base_price": 38200, "volatility": 0.022, "sector": "Technology",  "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:FSR": {"base_price": 7840,  "volatility": 0.014, "sector": "Banking",     "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:SBK": {"base_price": 19600, "volatility": 0.013, "sector": "Banking",     "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:NED": {"base_price": 14200, "volatility": 0.013, "sector": "Banking",     "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:ABG": {"base_price": 17800, "volatility": 0.015, "sector": "Banking",     "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:SHP": {"base_price": 28900, "volatility": 0.012, "sector": "Retail",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:WHL": {"base_price": 6150,  "volatility": 0.016, "sector": "Retail",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:MTN": {"base_price": 9870,  "volatility": 0.019, "sector": "Telecoms",    "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:VOD": {"base_price": 12300, "volatility": 0.014, "sector": "Telecoms",    "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:ANG": {"base_price": 44100, "volatility": 0.025, "sector": "Mining",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:IMP": {"base_price": 11200, "volatility": 0.028, "sector": "Mining",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:BHP": {"base_price": 52300, "volatility": 0.021, "sector": "Mining",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:GLN": {"base_price": 9340,  "volatility": 0.023, "sector": "Mining",      "exchange": "JSE", "asset_class": "EQUITY"},
    "JSE:CPI": {"base_price": 168000,"volatility": 0.017, "sector": "Banking",     "exchange": "JSE", "asset_class": "EQUITY"},
}

# Crypto Instruments
CRYPTO_INSTRUMENTS = {
    "BTC-ZAR":  {"base_price": 1_620_000, "volatility": 0.045, "sector": "Crypto", "exchange": "VALR", "asset_class": "CRYPTO"},
    "ETH-ZAR":  {"base_price": 85_000,    "volatility": 0.042, "sector": "Crypto", "exchange": "VALR", "asset_class": "CRYPTO"},
    "SOL-ZAR":  {"base_price": 27_500,    "volatility": 0.055, "sector": "Crypto", "exchange": "VALR", "asset_class": "CRYPTO"},
    "XRP-ZAR":  {"base_price": 1_140,     "volatility": 0.038, "sector": "Crypto", "exchange": "LUNO", "asset_class": "CRYPTO"},
    "ADA-ZAR":  {"base_price": 870,       "volatility": 0.041, "sector": "Crypto", "exchange": "LUNO", "asset_class": "CRYPTO"},
    "USDT-ZAR": {"base_price": 18_200,    "volatility": 0.002, "sector": "Stable", "exchange": "VALR", "asset_class": "CRYPTO"},
    "LINK-ZAR": {"base_price": 4_250,     "volatility": 0.048, "sector": "Crypto", "exchange": "VALR", "asset_class": "CRYPTO"},
}

# Streaming behaviour probabilities and parameters
DUPLICATE_PROBABILITY  = 0.03   # 3%  chance of resending a previous event
LATE_ARRIVAL_PROBABILITY = 0.04 # 4%  chance of delaying send by 35 seconds
OUT_OF_ORDER_PROBABILITY = 0.05 # 5%  chance of backdating event_ts by 30s
BURST_INTERVAL_SECONDS = 60     # trigger a burst every ~60 seconds
BURST_EVENT_COUNT      = 20     # send 20 events rapidly during a burst
BURST_SLEEP_SECONDS    = 0.05   # sleep between burst events

#Normal throughput
MIN_SLEEP_SECONDS = 0.1
MAX_SLEEP_SECONDS = 2.0