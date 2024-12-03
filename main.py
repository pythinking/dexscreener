from flask import Flask, request, jsonify, send_from_directory
import requests
from dexscreener import DexscreenerClient
from dexscreener.models import TokenPair, TokenInfo, OrderInfo
import json
from web3 import Web3

# Flask Application
app = Flask(__name__, static_folder="public")


# Uniswap V2 Pair contract ABI
PAIR_ABI = json.loads('''
[
    {
        "constant": true,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "price0CumulativeLast",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "price1CumulativeLast",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
''')

# Default node URLs for different chains
CHAIN_PROVIDERS = {
    "ethereum": "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
    "solana": "https://api.mainnet-beta.solana.com",
    "arbitrum": "https://endpoints.omniatech.io/v1/arbitrum/sepolia/public",
}




def fetch_pair_data(pair_address, node_url):
    """
    Fetch data from a Uniswap V2 pair contract.

    Args:
        pair_address (str): The address of the pair contract.
        node_url (str): The Ethereum node HTTP URL.

    Returns:
        dict: A dictionary containing the pair data.
    """
    web3 = Web3(Web3.HTTPProvider(node_url))

    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the blockchain node.")

    pair_contract = web3.eth.contract(address=pair_address, abi=PAIR_ABI)

    token0_address = pair_contract.functions.token0().call()
    token1_address = pair_contract.functions.token1().call()

    reserves = pair_contract.functions.getReserves().call()
    reserve0 = reserves[0]
    reserve1 = reserves[1]
    block_timestamp_last = reserves[2]

    price0_cumulative_last = pair_contract.functions.price0CumulativeLast().call()
    price1_cumulative_last = pair_contract.functions.price1CumulativeLast().call()

    return {
        "token0_address": token0_address,
        "token1_address": token1_address,
        "reserve0": reserve0,
        "reserve1": reserve1,
        "block_timestamp_last": block_timestamp_last,
        "price0_cumulative_last": price0_cumulative_last,
        "price1_cumulative_last": price1_cumulative_last,
    }





class DexscreenerAPI:
    def __init__(self):
        self.client = DexscreenerClient()

    # Fetch Data
    def fetch_data(self, pair="SOL/USDC"):
        url = f"https://api.dexscreener.com/latest/dex/search?q={pair}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("pairs", [])
        else:
            raise Exception(f"Error fetching data: {response.status_code}")

    # Filter Data
    def filter_data(self, data, filters):
        return [
            pair for pair in data
            if pair.get("liquidity", {}).get("usd", 0) >= filters.get("liquidity", 0)
            and pair.get("fdv", 0) >= filters.get("fdv", 0)
            and pair.get("volume", {}).get("h24", 0) >= filters.get("volume", 0)
            and (pair.get("txns", {}).get("h24", {}).get("buys", 0) +
                 pair.get("txns", {}).get("h24", {}).get("sells", 0)) >= filters.get("transactions", 0)
        ]

    # Format Data as Text
    def format_data_as_text(self, data):
        return "\n".join([
            f"""
                DEX: {pair.get('dexId', 'N/A')}
                Pair Address: {pair.get('pairAddress', 'N/A')}
                Base Token: {pair.get('baseToken', {}).get('name', 'N/A')} ({pair.get('baseToken', {}).get('symbol', 'N/A')})
                Quote Token: {pair.get('quoteToken', {}).get('name', 'N/A')} ({pair.get('quoteToken', {}).get('symbol', 'N/A')})
                Price (USD): ${pair.get('priceUsd', 'N/A')}
                24H Volume (USD): ${pair.get('volume', {}).get('h24', 0):,.2f}
                Liquidity (USD): ${pair.get('liquidity', {}).get('usd', 0):,.2f}
                24H Transactions: {pair.get('txns', {}).get('h24', {}).get('buys', 0) + pair.get('txns', {}).get('h24', {}).get('sells', 0)}
                URL: {pair.get('url', 'N/A')}
                --------------------------------
            """
            for pair in data
        ])


# Instantiate API Helper
dex_api = DexscreenerAPI()


# Static Files
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


# Endpoints
@app.route("/filter", methods=["GET"])
def filter_pairs():
    try:
        pair = request.args.get("pair", "SOL/USDC")
        filters = {
            "liquidity": float(request.args.get("liquidity", 0)),
            "fdv": float(request.args.get("fdv", 0)),
            "volume": float(request.args.get("volume", 0)),
            "transactions": int(request.args.get("txns", 0)),
        }

        raw_data = dex_api.fetch_data(pair)
        filtered_data = dex_api.filter_data(raw_data, filters)

        if request.args.get("format") == "text":
            return dex_api.format_data_as_text(filtered_data), 200, {"Content-Type": "text/plain"}
        else:
            return jsonify(filtered_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/token-profiles", methods=["GET"])
def token_profiles():
    try:
        profiles_ = dex_api.client.get_latest_token_profiles()
        token_info_list = [profile.to_dict() for profile in profiles_]
        return jsonify(token_info_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/boosted-tokens", methods=["GET"])
def boosted_tokens():
    try:
        boosted_tokens = dex_api.client.get_latest_boosted_tokens()
        return jsonify([token.to_dict() for token in boosted_tokens]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/most-active-tokens", methods=["GET"])
def most_active_tokens():
    try:
        active_tokens = dex_api.client.get_tokens_most_active()
        active_tokens_list = [token.to_dict() for token in active_tokens]
        return jsonify(active_tokens_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/orders", methods=["GET"])
def orders():
    try:
        blockchain = request.args.get("blockchain", "solana")
        address = request.args.get("address")
        if not address:
            return jsonify({"error": "Missing required parameter: address"}), 400

        orders = dex_api.client.get_orders_paid_of_token(blockchain, address)
        # Convert OrderInfo objects to dictionaries for JSON serialization
        orders_list = [order.to_dict() for order in orders]
        return jsonify(orders_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search-pairs", methods=["GET"])
def search_pairs():
    try:
        query = request.args.get("query")
        if not query:
            return jsonify({"error": "Missing required parameter: query"}), 400

        pairs = dex_api.client.search_pairs(query)
        serialized_pairs = [pair.to_dict() if hasattr(pair, 'to_dict') else pair for pair in pairs]  
        return jsonify(serialized_pairs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/pair-info", methods=["GET"])
def pair_info():
    try:
        chain = request.args.get("chain", "bsc")
        address = request.args.get("address")
        if not address:
            return jsonify({"error": "Missing required parameter: address"}), 400

        pair = dex_api.client.get_token_pair(chain, address)
        if pair:
            return jsonify(pair.to_dict() if hasattr(pair, 'to_dict') else pair), 200
        else:
            return jsonify({"error": "Pair not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route("/pair-list", methods=["GET"])
def pair_list():
    try:
        chain = request.args.get("chain", "bsc")
        addresses = request.args.getlist("addresses")
        if not addresses:
            return jsonify({"error": "Missing required parameter: addresses"}), 400

        pairs = dex_api.client.get_token_pair_list(chain, addresses)
        return jsonify([pair.to_dict() if hasattr(pair, 'to_dict') else pair for pair in pairs]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route("/pair-contract", methods=["GET"])
def pair_data_contract():
    """
    Fetch pair data from a contract based on the specified chain and address.
    """
    try:
        # Retrieve query parameters
        chain = request.args.get("chain", "solana").lower()
        addresses = request.args.getlist("addresses")

        if not addresses:
            return jsonify({"error": "Missing required parameter: addresses"}), 400

        # Determine the node URL for the selected chain
        node_url = CHAIN_PROVIDERS.get(chain)
        if not node_url:
            return jsonify({"error": f"Unsupported chain: {chain}"}), 400

        results = []
        for address in addresses:
            try:
                pair_data = fetch_pair_data(address, node_url)
                if pair_data:
                    results.append(pair_data)
            except Exception as e:
                print(f"Error fetching data for address {address}: {e}")

        if not results:
            return jsonify({"error": "No data found for provided addresses"}), 404

        return jsonify(results), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
