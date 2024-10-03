from decouple import config
from dydx_v4_client import MAX_CLIENT_ID  # Import MAX_CLIENT_ID from dydx_v4_client

# For gathering testnet data or live market data for cointegration calculation
MARKET_DATA_MODE = "TESTNET"  # Options: "TESTNET" or "MAINNET"

# Close all open positions and orders
ABORT_ALL_POSITIONS = True

# Find Cointegrated Pairs
FIND_COINTEGRATED = True

# Manage Exits
MANAGE_EXITS = True

# Place Trades
PLACE_TRADES = True

# Resolution for market data
RESOLUTION = "1HOUR"

# Stats Window
WINDOW = 21  # Rolling window for cointegration

# Thresholds - Opening
MAX_HALF_LIFE = 15  # Maximum half-life for a cointegrated pair
ZSCORE_THRESH = 1.49  # Z-score threshold for opening trades
USD_PER_TRADE = 50  # Amount in USD per trade
USD_MIN_COLLATERAL = 150  # Minimum collateral to ensure sufficient funds

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True  # Close positions when z-score crosses

# Endpoint for Account Queries on Testnet and Mainnet
INDEXER_ENDPOINT_TESTNET = "https://indexer.v4testnet.dydx.exchange"
INDEXER_ENDPOINT_MAINNET = "https://indexer.dydx.exchange"
INDEXER_ACCOUNT_ENDPOINT = INDEXER_ENDPOINT_TESTNET  # Set this to MAINNET for live environment

#TIMEOUTS
API_TIMEOUT = 10  # Timeout for API requests
GRPC_RETRY_ATTEMPTS = 5  # Number of retry attempts for gRPC connection
GRPC_RETRY_DELAY = 2  # Delay between retries in seconds


# gRPC Endpoints for Testnet and Mainnet
GRPC_ENDPOINT_TESTNET = "grpc.testnet.dydx.exchange:443"
GRPC_ENDPOINT_MAINNET = "grpc.mainnet.dydx.exchange:443"
INDEXER_GRPC_ENDPOINT_TESTNET = "indexer.testnet.dydx.exchange:443"
INDEXER_GRPC_ENDPOINT_MAINNET = "indexer.mainnet.dydx.exchange:443"


# Environment Variables loaded via config
DYDX_ADDRESS = config("DYDX_ADDRESS")  # Address for your dYdX account
SECRET_PHRASE = config("SECRET_PHRASE")  # Your secret phrase for the wallet
MNEMONIC = SECRET_PHRASE  # Use the secret phrase as mnemonic
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")  # Token for Telegram bot integration
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")  # Telegram chat ID for notifications
