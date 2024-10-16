# from dydx3.constants import API_HOST_MAINNET, API_HOST_GOERLI
from decouple import config

# constants.py

# Toggle for trading only specific pairs
TRADE_SPECIFIC_PAIRS = False  # Set to False to ignore specific pairs

# List of specific pairs to trade (up to 10)
SPECIFIC_PAIRS = [
    "ATOM-USD",
    "MATIC-USD",
    
    
    # Add up to 10 pairs here
]

# For gathering tesnet data or live market data for cointegration calculation
MARKET_DATA_MODE = "TESTNET" # vs "MAINNET"

# Close all open positions and orders
ABORT_ALL_POSITIONS = False 

# Find Cointegrated Pairs
FIND_COINTEGRATED = False

# Manage Exits
MANAGE_EXITS = True

# Place Trades
PLACE_TRADES = True

# Resolution
RESOLUTION = "1HOUR"

# Stats Window
WINDOW = 21

# Thresholds - Opening
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 2.35
USD_PER_TRADE = 50
USD_MIN_COLLATERAL = 100

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True

# Endpoint for Account Queries on Testnet
INDEXER_ENDPOINT_TESTNET = "https://indexer.v4testnet.dydx.exchange"
INDEXER_ENDPOINT_MAINNET = "https://indexer.dydx.trade"
INDEXER_ACCOUNT_ENDPOINT = INDEXER_ENDPOINT_TESTNET

# Environment Variables
DYDX_ADDRESS = config("DYDX_ADDRESS")
SECRET_PHRASE = config("SECRET_PHRASE")
MNEMONIC = (SECRET_PHRASE)
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")
