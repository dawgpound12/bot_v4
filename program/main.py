import asyncio
import time
from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES, MANAGE_EXITS
from func_connections import connect_dydx
from func_private import abort_all_positions, place_market_order, get_open_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pairs import manage_trade_exits
from func_messaging import send_message

# MAIN FUNCTION
async def main():

    send_message("Bot launch successful")

    try:
        print("Connecting to Client...")
        client = await connect_dydx()
    except Exception as e:
        print("Error connecting to client: ", e)
        send_message(f"Failed to connect to client {e}")
        exit(1)

    if ABORT_ALL_POSITIONS:
        try:
            print("Closing open positions...")
            await abort_all_positions(client)
        except Exception as e:
            print("Error closing all positions: ", e)
            send_message(f"Error closing all positions {e}")
            exit(1)

    if FIND_COINTEGRATED:
        try:
            print("Fetching token market prices...")
            df_market_prices = await construct_market_prices(client)
            print(df_market_prices)
        except Exception as e:
            print("Error constructing market prices: ", e)
            send_message(f"Error constructing market prices {e}")
            exit(1)

        try:
            print("Storing cointegrated pairs...")
            stores_result = store_cointegration_results(df_market_prices)
            if stores_result != "saved":
                print("Error saving cointegrated pairs")
                exit(1)
        except Exception as e:
            print("Error saving cointegrated pairs: ", e)
            send_message(f"Error saving cointegrated pairs {e}")
            exit(1)

    while True:
        if MANAGE_EXITS:
            try:
                print("Managing exits...")
                await manage_trade_exits(client)
                time.sleep(1)
            except Exception as e:
                print("Error managing exiting positions: ", e)
                send_message(f"Error managing exiting positions {e}")
                exit(1)

        if PLACE_TRADES:
            try:
                print("Finding trading opportunities...")
                await open_positions(client)
            except Exception as e:
                print("Error trading pairs: ", e)
                send_message(f"Error opening trades {e}")
                exit(1)

asyncio.run(main())
