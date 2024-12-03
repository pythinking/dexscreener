

export async function fetchTokenData(contractAddress) {
    try {
        const url = `https://api.dexscreener.com/latest/dex/tokens/${contractAddress}`;
        console.log('url', url)

        const response = await fetch(url);
        const data = await response.json();

        if (data.pairs && data.pairs.length > 0) {

            console.log('data', data)

            return data.pairs.map(pair => ({
                chainId: pair.chainId,
                dexId: pair.dexId,
                pairAddress: pair.pairAddress,
                labels: pair.labels,
                boosts: pair.boosts ? {
                    active: pair.boosts.active,
                } : null,
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
                liquidityUSD: pair.liquidity ? parseFloat(pair.liquidity.usd) : 0,
                liquidityBase: pair.liquidity ? parseFloat(pair.liquidity.base) : 0,
                liquidityQuote: pair.liquidity ? parseFloat(pair.liquidity.quote) : 0,
                marketCap: parseFloat(pair.marketCap),
                fdv: parseFloat(pair.fdv),
                pairCreatedAt: pair.pairCreatedAt,
                boosts: {
                    active: pair.boosts.active,
                },
                info: {
                    imageUrl: pair.info?.imageUrl || '',
                    websites: pair.info?.websites || [],
                    socials: pair.info?.socials || [],
                },
                volume24h: parseFloat(pair.volume?.h24) || 0,
                txns24h: pair.txns?.h24 || 0,
                priceChange24h: pair.priceChange?.h24 || 0,
                url: pair.url,
            }));
        } else {
            throw new Error("No pair data found");
        }
    } catch (error) {
        console.error("Error fetching DexScreener data:", error);
        return null;
    }
}


export async function fetchPairDataFromSubgraph(pairAddress) {
    const query = `
        {
          pairs(where: { id: "${pairAddress}" }) {
            id
            reserve0
            reserve1
            token0 {
              id
              symbol
              name
            }
            token1 {
              id
              symbol
              name
            }
            volumeUSD
            liquidityUSD
            reserveUSD
            token0Price
            token1Price
          }
        }
    `;

    const url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"; // Replace with your subgraph

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });

        const result = await response.json();
        if (result.data && result.data.pairs && result.data.pairs.length > 0) {
            return result.data.pairs[0];
        } else {
            throw new Error("Pair not found in subgraph");
        }
    } catch (error) {
        console.error("Error fetching data from subgraph:", error);
        return null;
    }
}
