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




class BlockchainContractManager:
    def __init__(self, chain_providers, abi):
        """
        Initialize the BlockchainContractManager with chain providers and ABI.

        Args:
            chain_providers (dict): A dictionary of chain names and their node URLs.
            abi (list): The ABI for the contract interactions.
        """
        self.chain_providers = chain_providers
        self.abi = abi
        self.web3_connections = {}
        self.connected_chains = {}

        # Establish and verify connections to all chains
        self._initialize_connections()

    def _initialize_connections(self):
        """
        Initialize Web3 connections for all provided chains.
        """
        for chain, node_url in self.chain_providers.items():
            if "solana" in chain.lower():
                self.connected_chains[chain] = self._check_solana_connection(node_url)
                
                if self.connected_chains[chain]:
                    print(f"🔗 Connected to {chain} node.")
                else:
                    print(f"❌ Failed to connect to {chain} node.")
            else:
                web3 = Web3(Web3.HTTPProvider(node_url))
                if web3.is_connected():
                    self.web3_connections[chain] = web3
                    self.connected_chains[chain] = True
                    print(f"🔗 Connected to {chain} node.")
                else:
                    self.connected_chains[chain] = False
                    print(f"❌ Failed to connect to {chain} node.")

    def _check_solana_connection(self, node_url):
        """
        Check connection to a Solana node by sending a JSON-RPC request.

        Args:
            node_url (str): The Solana node URL.

        Returns:
            bool: True if connected, False otherwise.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getHealth"
        }
        try:
            response = requests.post(node_url, json=payload, timeout=5)            
            return response.status_code == 200 and response.json().get("result") == "ok"
        except Exception as e:
            print(f"Error connecting to Solana node at {node_url}: {e}")
            return False

    def is_chain_connected(self, chain):
        """
        Check if a specific chain is connected.

        Args:
            chain (str): The blockchain name.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.connected_chains.get(chain.lower(), False)
    


    def call_contract_function(self, chain, pair_address, function_name, *args):
        """
        Call a specific function from a contract on Ethereum-like chains.

        Args:
            chain (str): The blockchain name.
            pair_address (str): The address of the contract.
            function_name (str): The name of the function to call.
            *args: Arguments to pass to the contract function.

        Returns:
            Any: The result of the function call.
        """
        chain = chain.lower()
        if not self.is_chain_connected(chain):
            raise ConnectionError(f"Not connected to the blockchain node for chain: {chain}")

        try:
            # Use pre-established Web3 connection
            web3 = self.web3_connections.get(chain)
            if not web3:
                raise ValueError(f"No connection found for chain: {chain}")

            # Initialize the contract
            contract = web3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=self.abi
            )

            # Call the specified function
            contract_function = getattr(contract.functions, function_name)
            result = contract_function(*args).call()
            return result
        except Exception as e:
            raise ValueError(f"Error calling function {function_name} on chain {chain} and address {pair_address}: {e}")



    

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
# Instantiate the BlockchainContractManager
contract_manager = BlockchainContractManager(CHAIN_PROVIDERS, PAIR_ABI)



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
    Call a specific function from a contract or return SOL balance for Solana accounts by default.
    """
    try:
        chain = request.args.get("chain", "ethereum").lower()
        address = request.args.get("address")
        function_name = request.args.get("function")
        args = request.args.getlist("args")  # Pass arguments as list

        if not address:
            return jsonify({"error": "Missing required parameter: address"}), 400

        if chain not in CHAIN_PROVIDERS:
            return jsonify({"error": f"Unsupported chain: {chain}"}), 400

        if chain == "solana" and not function_name:
            # Return SOL balance by default for Solana accounts
            node_url = CHAIN_PROVIDERS.get(chain)
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            }
            response = requests.post(node_url, json=payload, timeout=10)
            if response.status_code != 200:
                return jsonify({"error": f"Failed to fetch balance: {response.text}"}), 500
            
            data = response.json()
            if not data.get("result"):
                return jsonify({"error": "No balance information available"}), 404

            sol_balance = data["result"]["value"] / 1_000_000_000  # Convert lamports to SOL
            return jsonify({"address": address, "sol_balance": sol_balance}), 200

        # For Ethereum-like chains or specific functions, call the contract function
        converted_args = [int(arg) if arg.isdigit() else arg for arg in args]
        result = contract_manager.call_contract_function(chain, address, function_name, *converted_args)

        return jsonify({"address": address, "function": function_name, "result": result}), 200

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
