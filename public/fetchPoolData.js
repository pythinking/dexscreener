// Fetch data from Dexscreener for Solana pools
export async function fetchTokenData(contractAddress) {
    try {
        const url = `https://api.dexscreener.com/latest/dex/tokens/${contractAddress}`;
        console.log('url', url);
        const response = await fetch(url);
        const data = await response.json();

        console.log('data', data);

        if (data.pairs && data.pairs.length > 0) {
            const pair = data.pairs[0];
            return {
                chainId: pair.chainId,
                dexId: pair.dexId,
                pairAddress: pair.pairAddress,
                labels: pair.labels,
                baseToken: {
                    name: pair.baseToken.name,
                    symbol: pair.baseToken.symbol,
                    address: pair.baseToken.address,
                },
                quoteToken: {
                    name: pair.quoteToken.name,
                    symbol: pair.quoteToken.symbol,
                    address: pair.quoteToken.address,
                },
                priceUsd: parseFloat(pair.priceUsd),
                priceNative: parseFloat(pair.priceNative),
                liquidityUSD: parseFloat(pair.liquidity.usd),
                liquidityBase: parseFloat(pair.liquidity.base),
                liquidityQuote: parseFloat(pair.liquidity.quote),
                marketCap: parseFloat(pair.marketCap),
                fdv: parseFloat(pair.fdv),
                pairCreatedAt: pair.pairCreatedAt,
                boosts: {
                    active: pair.boosts.active,
                },
                info: {
                    imageUrl: pair.info.imageUrl,
                    websites: pair.info.websites,
                    socials: pair.info.socials,
                },
                volume24h: parseFloat(pair.volume?.h24) || 0,
                txns24h: pair.txns?.h24 || 0,
                priceChange24h: pair.priceChange?.h24 || 0,
                url: pair.url,
            };
        } else {
            throw new Error("No pair data found");
        }
    } catch (error) {
        console.error("Error fetching DexScreener data:", error);
        return null;
    }
}

// Fetch data from Dexscreener for Solana pools
export async function fetchDexScreenerData(contractAddress) {
    try {
        const url = `https://api.dexscreener.com/latest/dex/pairs/solana/${contractAddress}`;
        console.log('url', url);
        const response = await fetch(url);
        const data = await response.json();

        console.log('data', data);

        if (data.pairs && data.pairs.length > 0) {
            const pair = data.pairs[0];
            return {
                baseToken: {
                    name: pair.baseToken.name,
                    symbol: pair.baseToken.symbol,
                    address: pair.baseToken.address,
                },
                quoteToken: {
                    name: pair.quoteToken.name,
                    symbol: pair.quoteToken.symbol,
                    address: pair.quoteToken.address,
                },
                priceUsd: parseFloat(pair.priceUsd),
                priceNative: parseFloat(pair.priceNative),
                volume24h: parseFloat(pair.volume?.h24) || 0,
                liquidityUSD: parseFloat(pair.liquidity.usd),
                marketCap: parseFloat(pair.marketCap),
                fdv: parseFloat(pair.fdv),
                pairCreatedAt: pair.pairCreatedAt,
                boosts: {
                    active: pair.boosts.active,
                },
                info: {
                    imageUrl: pair.info.imageUrl,
                    websites: pair.info.websites,
                    socials: pair.info.socials,
                },
                txns24h: pair.txns?.h24 || 0,
                priceChange24h: pair.priceChange?.h24 || 0,
                url: pair.url,
            };
        } else {
            throw new Error("No pair data found");
        }
    } catch (error) {
        console.error("Error fetching DexScreener data:", error);
        return null;
    }
}

