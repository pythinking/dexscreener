// Fetch data from Dexscreener for Solana pools
export async function fetchDexScreenerData(contractAddress) {
    try {
        const response = await fetch(`https://api.dexscreener.com/latest/dex/pairs/solana/${contractAddress}`);
        const data = await response.json();
        if (data.pair) {
            return {
                token0: data.pair.baseToken.name || "Unknown Token",
                token1: data.pair.quoteToken.name || "Unknown Token",
                ratio: parseFloat(data.pair.priceNative), // Ratio in native token
                liquidityUSD: parseFloat(data.pair.liquidity.usd), // Total USD Liquidity
                volume24h: parseFloat(data.pair.volume.h24), // 24h volume
                url: data.pair.url, // DexScreener link
            };
        } else {
            throw new Error("No pair data found");
        }
    } catch (error) {
        console.error("Error fetching DexScreener data:", error);
        return null;
    }
}
