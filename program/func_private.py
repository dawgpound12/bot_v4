from dydx_v4_client import MAX_CLIENT_ID, Order, OrderFlags
from dydx_v4_client.node.market import Market
from constants import DYDX_ADDRESS
from func_utils import format_number
import random
import time
import json

# Cancel Order
async def cancel_order(client, order_id):
    try:
        order = await get_order(client, order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found.")
        
        market = Market((await client.indexer.markets.get_perpetual_markets(order["ticker"]))["markets"][order["ticker"]])
        market_order_id = market.order_id(
            DYDX_ADDRESS,
            0,
            random.randint(0, MAX_CLIENT_ID),
            OrderFlags.SHORT_TERM
        )
        current_block = await client.node.latest_block_height()
        good_til_block = current_block + 1 + 10
        await client.node.cancel_order(
            client.wallet,
            market_order_id,
            good_til_block=good_til_block
        )
        print(f"Attempted to cancel order for: {order['ticker']}. Please check the dashboard to ensure it was canceled.")
    except Exception as e:
        print(f"Error canceling order: {e}")

# Get Order
async def get_order(client, order_id):
    try:
        return await client.indexer_account.account.get_order(order_id)
    except Exception as e:
        print(f"Error fetching order {order_id}: {e}")
        return None

# Get Account (Restored for other imports)
async def get_account(client):
    """
    Fetch account details (used in other parts of the bot)
    """
    try:
        account = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
        return account["subaccount"]
    except Exception as e:
        print(f"Error fetching account info: {e}")
        return None

# Get Account Balance (Restored)
async def get_account_balance(client):
    """
    Fetch and display account balance from dYdX
    """
    try:
        account = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
        balance = account["subaccount"]["balance"]
        print(f"Account Balance: {balance}")
        return balance
    except Exception as e:
        print(f"Error fetching account balance: {e}")
        return None

# Get Open Positions
async def get_open_positions(client):
    try:
        response = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
        return response["subaccount"]["openPerpetualPositions"]
    except Exception as e:
        print(f"Error fetching open positions: {e}")
        return {}

# Check if Positions are Open
async def is_open_positions(client, market):
    try:
        time.sleep(0.2)
        response = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
        open_positions = response["subaccount"]["openPerpetualPositions"]
        return market in open_positions.keys()
    except Exception as e:
        print(f"Error checking open positions for {market}: {e}")
        return False

# Place Market Order
async def place_market_order(client, market, side, size, price, reduce_only):
    try:
        ticker = market
        current_block = await client.node.latest_block_height()
        market_data = Market((await client.indexer.markets.get_perpetual_markets(market))["markets"][market])
        market_order_id = market_data.order_id(
            DYDX_ADDRESS,
            0,
            random.randint(0, MAX_CLIENT_ID),
            OrderFlags.SHORT_TERM
        )
        good_til_block = current_block + 1 + 10

        # Set Time In Force
        time_in_force = Order.TIME_IN_FORCE_IOC  # Immediate or Cancel

        # Place Market Order
        order = await client.node.place_order(
            client.wallet,
            market_data.order(
                market_order_id,
                side=Order.Side.SIDE_BUY if side == "BUY" else Order.Side.SIDE_SELL,
                size=float(size),
                price=float(price),
                time_in_force=time_in_force,
                reduce_only=reduce_only,
                good_til_block=good_til_block
            ),
        )

        # Fetch recent orders to confirm placement
        time.sleep(1.5)
        orders = await client.indexer_account.account.get_subaccount_orders(
            DYDX_ADDRESS,
            0,
            ticker,
            return_latest_orders="true",
        )

        # Get latest order id
        order_id = ""
        for o in orders:
            client_id = int(o["clientId"])
            clob_pair_id = int(o["clobPairId"])
            if client_id == market_order_id.client_id and clob_pair_id == market_order_id.clob_pair_id:
                order_id = o["id"]
                break

        if order_id == "":
            raise ValueError("Order placement failed: Unable to detect order in recent orders")

        print(f"Order placed successfully: {order_id}")
        return {"status": "success", "order_id": order_id}

    except Exception as e:
        print(f"Error placing order: {e}")
        return {"status": "failed", "error": str(e)}

# Cancel All Open Orders
async def cancel_all_orders(client):
    try:
        orders = await client.indexer_account.account.get_subaccount_orders(DYDX_ADDRESS, 0, status="OPEN")
        if len(orders) > 0:
            for order in orders:
                await cancel_order(client, order["id"])
                print(f"Order {order['id']} canceled.")
        else:
            print("No open orders found.")
    except Exception as e:
        print(f"Error canceling open orders: {e}")

# Abort All Open Positions
async def abort_all_positions(client):
    try:
        # Cancel all open orders
        await cancel_all_orders(client)

        # Fetch all available markets
        markets_response = await client.indexer.markets.get_perpetual_markets()
        if not markets_response or "markets" not in markets_response:
            raise ValueError("Markets data is missing or invalid.")
        markets = markets_response["markets"]

        # Fetch all open positions
        positions = await get_open_positions(client)

        if len(positions) > 0:
            for item in positions.keys():
                pos = positions[item]
                market = pos["market"]
                side = "BUY" if pos["side"] == "SHORT" else "SELL"
                price = float(pos["entryPrice"])

                # Ensure market exists
                if market not in markets:
                    print(f"Market data for {market} not found.")
                    continue

                tick_size = markets[market]["tickSize"]
                accept_price = price * 1.7 if side == "BUY" else price * 0.3  # Ensure order fills
                accept_price = format_number(accept_price, tick_size)

                # Place market order to close position
                result = await place_market_order(client, market, side, pos["sumOpen"], accept_price, True)

                if result["status"] == "failed":
                    print(f"Error closing position for {market}: {result['error']}")
                else:
                    print(f"Closed position for {market}: {result['order_id']}")

            # Clear saved agents after aborting all positions
            with open("bot_agents.json", "w") as f:
                json.dump([], f)
        else:
            print("No open positions found.")
    except Exception as e:
        print(f"Error aborting all positions: {e}")

# Check Order Status
async def check_order_status(client, order_id):
    try:
        if order_id:  # Ensure order_id is valid and not None
            order = await get_order(client, order_id)
            if "status" in order:
                return order["status"]
            else:
                raise ValueError(f"Order status not found for order ID: {order_id}")
        else:
            raise ValueError("Invalid order_id provided")
    except Exception as e:
        print(f"Error checking order status for {order_id}: {e}")
        return "UNKNOWN"