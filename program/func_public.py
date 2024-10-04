from dydx_v4_client import MAX_CLIENT_ID, OrderFlags
from dydx_v4_client.node.market import Market
from dydx_v4_client.indexer.rest.constants import OrderType
from v4_proto.dydxprotocol.clob.order_pb2 import Order
from constants import DYDX_ADDRESS
from func_utils import format_number  # Import only the functions required
from func_private import cancel_order, get_open_positions, place_market_order  # Importing from func_private
import random
import time
import json

# Abort all open positions
async def abort_all_positions(client):
    await cancel_all_orders(client)

    # Get markets for reference of tick size
    markets = await get_markets(client)

    # Get all open positions
    positions = await get_open_positions(client)

    if len(positions) > 0:
        for pos in positions:
            market = pos["market"]
            side = "BUY" if pos["side"] == "SHORT" else "SELL"
            price = float(pos["entryPrice"])  # Ensure entryPrice is converted to float
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            # Explicitly convert size to float before sending
            result = await place_market_order(client, market, side, float(pos["openSize"]), accept_price, True)

            if result is None:
                print(f"Error closing position for {market}")
            else:
                print(f"Closed position for {market}")

        # Clear saved agents after aborting all positions
        with open("bot_agents.json", "w") as f:
            json.dump([], f)

# Get Markets
async def get_markets(client):
    """ Function to get all available markets from the indexer. """
    try:
        markets = await client.indexer.markets.get_perpetual_markets()
        return markets
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return {}

# Get Recent Candles
async def get_candles_recent(client, market):
    """ Function to fetch recent candle data for a specific market. """
    try:
        # Use the correct method to get candles from the indexer
        response = await client.indexer.markets.get_perpetual_market_candles(
            market=market,
            resolution="1HOUR",
            limit=100
        )
        candles = response["candles"]
        return candles
    except Exception as e:
        print(f"Error fetching candles for {market}: {e}")
        return []

# Cancel all open orders (using cancel_order from func_private)
async def cancel_all_orders(client):
    orders = await client.indexer_account.orders.get_orders_by_account(DYDX_ADDRESS)
    if len(orders) > 0:
        for order in orders:
            await cancel_order(client, order["id"])
            print(f"Order {order['id']} canceled.")
