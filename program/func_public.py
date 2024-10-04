from dydx_v4_client import MAX_CLIENT_ID, Order, OrderFlags
from dydx_v4_client.node.market import Market
from dydx_v4_client.indexer.rest.constants import OrderType
from constants import DYDX_ADDRESS
from func_utils import format_number
import random
import time
import json

# Cancel Order
async def cancel_order(client, order_id):
    order = await get_order(client, order_id)
    ticker = order["ticker"]
    market = Market((await client.indexer.markets.get_perpetual_markets())["markets"][ticker])
    market_order_id = market.order_id(DYDX_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM)
    current_block = await client.node.latest_block_height()
    good_til_block = current_block + 1 + 10
    await client.node.cancel_order(
        client.wallet,
        market_order_id,
        good_til_block=good_til_block
    )
    print(f"Attempted to cancel order for: {order['ticker']}. Please check the dashboard to ensure canceled.")

# Get Order
async def get_order(client, order_id):
    return await client.indexer_account.orders.get_order_by_id(order_id)

# Get Account
async def get_account(client):
    account = await client.indexer_account.accounts.get_by_address(DYDX_ADDRESS)
    return account["account"]

# Get Open Positions
async def get_open_positions(client):
    response = await client.indexer_account.positions.get_positions_by_account(DYDX_ADDRESS)
    return response["positions"]

# Check if Positions are Open
async def is_open_positions(client, market):
    time.sleep(0.2)
    response = await client.indexer_account.positions.get_positions_by_account(DYDX_ADDRESS)
    open_positions = response["positions"]
    return any(pos['market'] == market for pos in open_positions)

# Place Market Order
async def place_market_order(client, market, side, size, price, reduce_only):
    try:
        size = float(size)
        price = float(price)

        ticker = market
        current_block = await client.node.latest_block_height()
        market = Market((await client.indexer.markets.get_perpetual_markets())["markets"][market])
        market_order_id = market.order_id(DYDX_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM)
        good_til_block = current_block + 1 + 10

        # Place Market Order
        order = await client.node.place_order(
            client.wallet,
            market.order(
                market_order_id,
                order_type=OrderType.MARKET,
                side=Order.Side.SIDE_BUY if side == "BUY" else Order.Side.SIDE_SELL,
                size=size,
                price=price,
                time_in_force=Order.TIME_IN_FORCE_UNSPECIFIED,
                reduce_only=reduce_only,
                good_til_block=good_til_block
            ),
        )
        return order

    except Exception as e:
        print(f"Error placing market order: {e}")
        return None

# Cancel all open orders
async def cancel_all_orders(client):
    orders = await client.indexer_account.orders.get_orders_by_account(DYDX_ADDRESS)
    if len(orders) > 0:
        for order in orders:
            await cancel_order(client, order["id"])
            print(f"Order {order['id']} canceled.")

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
            price = float(pos["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            result = await place_market_order(client, market, side, pos["openSize"], accept_price, True)

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
        # Correct method call to get candles from the public API.
        candles = await client.public.get_market_candles(
            market=market,
            resolution="1HOUR",
            limit=100
        )
        return candles["candles"]
    except Exception as e:
        print(f"Error fetching candles for {market}: {e}")
        return []
    
# Check Order Status
async def check_order_status(client, order_id):
    order = await get_order(client, order_id)
    if "status" in order:
        return order["status"]
    return "UNKNOWN"
