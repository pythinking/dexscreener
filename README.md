# API Wrapper for [Dexscreener.com](https://docs.dexscreener.com/)

###### Pull requests GREATLY encouraged!

[![Downloads](https://static.pepy.tech/badge/dexscreener/week)](https://pepy.tech/project/dexscreener)
[![Downloads](https://static.pepy.tech/badge/dexscreener/month)](https://pepy.tech/project/dexscreener)
[![Downloads](https://pepy.tech/badge/dexscreener)](https://pepy.tech/project/dexscreener)

---

# DexScreener API

Welcome to the **DexScreener API**! This project provides a Flask-based API wrapper for interacting with the [DexScreener](https://dexscreener.com) platform, enabling you to retrieve data about token pairs, token profiles, boosted tokens, orders, and more.

---

## Features

- **Token Profiles**: Get detailed information about tokens, including metadata and boosted tokens.
- **Pair Information**: Retrieve details about token pairs across chains.
- **Orders Data**: Fetch paid order details for specific tokens.
- **Data Filtering**: Filter token pair data based on liquidity, volume, transactions, and more.
- **Asynchronous Support**: Async endpoints for scalable and efficient API consumption.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the API server:
   ```bash
   python main.py
   ```

The server will be available at `http://0.0.0.0:5000`.

---

## Endpoints

### 1. `/filter` [GET]
Filter token pairs by parameters like liquidity, volume, and transactions.

**Query Parameters:**
- `pair`: Token pair to search, e.g., `BTC/USDT` (default: `SOL/USDC`).
- `liquidity`: Minimum liquidity (in USD) required.
- `fdv`: Minimum fully diluted valuation (FDV) required.
- `volume`: Minimum 24-hour volume (in USD) required.
- `txns`: Minimum 24-hour transactions required.

**Example Request:**
```bash
http://localhost:5000/filter?pair=BTC/USDT&liquidity=10000&fdv=500000&volume=1000&txns=20
```

---

### 2. `/pair-list` [GET]
Fetch details for multiple token pairs.

**Query Parameters:**
- `chain`: Blockchain ID (default: `bsc`).
- `addresses`: Comma-separated list of token pair addresses (up to 30).

**Example Request:**
```bash
http://localhost:5000/pair-list?addresses=0x7213a321F1855CF1779f42c0CD85d3D95291D34C
```

---

### 3. `/pair-info` [GET]
Fetch detailed information about a specific token pair.

**Query Parameters:**
- `chain`: Blockchain ID (default: `bsc`).
- `address`: Token pair address (required).

**Example Request:**
```bash
http://localhost:5000/pair-info?address=0x7213a321F1855CF1779f42c0CD85d3D95291D34C
```

---

### 4. `/search-pairs` [GET]
Search for token pairs based on a query.

**Query Parameters:**
- `query`: Search term (e.g., token address or pair like `WBTC/USDC`).

**Example Request:**
```bash
http://localhost:5000/search-pairs?query=0x7213a321F1855CF1779f42c0CD85d3D95291D34C
```

---

### 5. `/orders` [GET]
Fetch orders paid for a specific token.

**Query Parameters:**
- `blockchain`: Blockchain ID (default: `solana`).
- `address`: Token address (required).

**Example Request:**
```bash
http://localhost:5000/orders?address=A55XjvzRU4KtR3Lrys8PpLZQvPojPqvnv5bJVHMYy3Jv
```

---

### 6. `/most-active-tokens` [GET]
List the most active tokens.

**Example Request:**
```bash
http://localhost:5000/most-active-tokens
```

---

### 7. `/boosted-tokens` [GET]
Retrieve the latest boosted tokens.

**Example Request:**
```bash
http://localhost:5000/boosted-tokens
```

---

### 8. `/token-profiles` [GET]
Get the latest token profiles.

**Example Request:**
```bash
http://localhost:5000/token-profiles
```

---

## Parameter Descriptions (from `client.py`)

### General Parameters

1. **`chain`**: Refers to the blockchain network (e.g., `bsc`, `ethereum`, `solana`). Defaults to `bsc` for pair-related queries.
2. **`address`**: Unique identifier of the token or token pair. Required for specific pair and token-related queries.
3. **`query`**: Used in the search API to filter pairs by name, symbol, or token address (e.g., `WBTC`, `WBTC/USDC`).

### `/filter` Parameters
- **`pair`**: Specific trading pair like `BTC/USDT`. Defaults to `SOL/USDC`.
- **`liquidity`**: USD value representing minimum required liquidity.
- **`fdv`**: Fully diluted valuation threshold for filtering pairs.
- **`volume`**: Minimum trading volume in the past 24 hours.
- **`txns`**: Total number of buy/sell transactions in the last 24 hours.

### `/pair-list` Parameters
- **`addresses`**: A comma-separated list of token addresses (maximum: 30).

---

### Example CURL Commands

#### 1. Filter Token Pairs
```bash
curl "http://localhost:5000/filter?pair=BTC/USDT&liquidity=10000&fdv=500000&volume=1000&txns=20"
```

#### 2. Fetch Multiple Pairs
```bash
curl "http://localhost:5000/pair-list?addresses=0x7213a321F1855CF1779f42c0CD85d3D95291D34C"
```

#### 3. Fetch Pair Information
```bash
curl "http://localhost:5000/pair-info?address=0x7213a321F1855CF1779f42c0CD85d3D95291D34C"
```

#### 4. Search Token Pairs
```bash
curl "http://localhost:5000/search-pairs?query=0x7213a321F1855CF1779f42c0CD85d3D95291D34C"
```

#### 5. Fetch Orders Paid
```bash
curl "http://localhost:5000/orders?address=A55XjvzRU4KtR3Lrys8PpLZQvPojPqvnv5bJVHMYy3Jv"
```

#### 6. Fetch Most Active Tokens
```bash
curl "http://localhost:5000/most-active-tokens"
```

#### 7. Fetch Boosted Tokens
```bash
curl "http://localhost:5000/boosted-tokens"
```

#### 8. Fetch Token Profiles
```bash
curl "http://localhost:5000/token-profiles"
```

---

## Contribution Guidelines

1. Fork the repository and create a new branch.
2. Make changes and ensure proper documentation.
3. Test changes locally before pushing.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Feel free to share any further suggestions or questions!

## License

This repo is forked from [dexscreener](https://github.com/nixonjoshua98/dexscreener) and is licensed under the MIT License.