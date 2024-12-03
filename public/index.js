import { fetchTokenData } from './fetchPoolData.js';

const initializeDashboard = () => {

        let tokensData = [];

        const actionSelector = document.getElementById('actionSelector');
        const filterForm = document.getElementById('filterForm');
        const sortForm = document.getElementById('sortForm');
        const aiForm = document.getElementById('aiForm');

        actionSelector.addEventListener('change', async (e) => {
            const selectedAction = e.target.value;

            // Esconder todos os formulários inicialmente
            filterForm.classList.add('hidden');
            sortForm.classList.add('hidden');
            aiForm.classList.add('hidden');

            if (selectedAction === 'market') {
                // Mostrar formulário de filtros
                filterForm.classList.remove('hidden');
                filterForm.dispatchEvent(new Event('submit'));
            } else if (selectedAction === 'Boosted Tokens') {
                sortForm.classList.remove('hidden');
                const response = await fetch('/boosted-tokens');
                const tokens = await response.json();
                tokensData = tokens;
                renderBoostedTokens(tokens);
            } else if (selectedAction === 'Tokens Profiles') {
                const response = await fetch('/token-profiles');
                console.log('response', response)
                const profiles = await response.json();
                renderTokenProfiles(profiles);
            } else if (selectedAction === 'Most Active Tokens') {
                const response = await fetch('/most-active-tokens');
                const activeTokens = await response.json();
                renderMostActiveTokens(activeTokens);
            } else if (selectedAction === 'automatize') {
                aiForm.classList.remove('hidden');
                document.getElementById('results').innerHTML = '';
            } else if (selectedAction === 'support') {
                renderSupportContent();
            }
        });


        filterForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const filters = {
                liquidity: parseFloat(document.getElementById('minLiquidity').value),
                fdv: parseFloat(document.getElementById('minFdv').value),
                volume: parseFloat(document.getElementById('minVolume24h').value),
                transactions: parseFloat(document.getElementById('minTransactions24h').value),
            };

            const response = await fetch(`/filter?liquidity=${filters.liquidity}&fdv=${filters.fdv}&volume=${filters.volume}&txns=${filters.transactions}`);
            const data = await response.json();
            tokensData = data;

            renderMarketAnalyzeCards(data);
            
        });

        sortForm.addEventListener('change', () => {
            const sortBy = document.getElementById('sortBy').value;

            console.log('sortBy', sortBy, tokensData);

            


            const sortedData = [...tokensData].sort((a, b) => {
                if (sortBy === 'price') {
                    return parseFloat(b.totalAmount || 0) - parseFloat(a.totalAmount || 0);
                } else if (sortBy === 'links') {
                    return parseFloat(b.links || 0) - parseFloat(a.links || 0);
                } else if (sortBy === 'name') {
                    return (a.description || '').localeCompare(b.description || '');
                }
            });
            renderBoostedTokens(sortedData);
        });

        aiForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const aiModel = document.getElementById('aiModel').value;
            const trainingData = document.getElementById('trainingData').value;
            // Implementar lógica de automação com IA aqui
            alert(`Running automation with model: ${aiModel} and training data: ${trainingData}`);
        });

        

        function renderMarketAnalyzeCards(tokens) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Limpar resultados anteriores

            tokens.forEach(token => {
                const baseToken = token.baseToken || {};
                const quoteToken = token.quoteToken || {};
                const priceUsd = token.priceUsd || 'N/A';
                const priceNative = token.priceNative || 'N/A';
                const fdv = token.fdv || 'N/A';
                const liquidity = token.liquidity?.usd || 0;
                const volume24h = token.volume?.h24 || 0;
                const marketCap = token.marketCap || 'N/A';
                const pairCreatedAt = new Date(token.pairCreatedAt).toLocaleString() || 'N/A';
                const priceChange = token.priceChange || {};
                const socials = token.info?.socials || [];
                const url = token.url || '#';

                const card = document.createElement('div');
                card.className = 'card-analize';
                card.innerHTML = `
                    <img src="${token.info?.header || 'https://via.placeholder.com/150'}" alt="${baseToken.name || 'Unknown'}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px;">
                    <h3>${baseToken.name || 'Unknown Token'} (${baseToken.symbol || 'N/A'})</h3>
                    <p><strong>Price (USD):</strong> $${priceUsd}</p>
                    <p><strong>Price (Native):</strong> ${priceNative}</p>
                    <p><strong>FDV:</strong> $${Number(fdv).toLocaleString()}</p>
                    <p><strong>Market Cap:</strong> $${Number(marketCap).toLocaleString()}</p>
                    <p><strong>Liquidity (USD):</strong> $${Number(liquidity).toLocaleString()}</p>
                    <p><strong>24H Volume (USD):</strong> $${Number(volume24h).toLocaleString()}</p>
                    <p><strong>Pair Created:</strong> ${pairCreatedAt}</p>
                    <p><strong>Price Changes:</strong> 
                        <ul style="list-style-type: none; padding: 0;">
                            <li><strong>1H:</strong> ${priceChange.h1 || 'N/A'}%</li>
                            <li><strong>6H:</strong> ${priceChange.h6 || 'N/A'}%</li>
                            <li><strong>24H:</strong> ${priceChange.h24 || 'N/A'}%</li>
                        </ul>
                    </p>
                    <p><strong>Socials:</strong> 
                        ${socials.map(social => `<a href="${social.url}" target="_blank">${social.type || 'Social Link'}</a>`).join(', ') || 'No socials available'}
                    </p>
                      <div class="card-footer">
                        <a href="${url}" target="_blank">View on DexScreener</a>
                    </div>
                    
                `;

                resultsDiv.appendChild(card);
            });
        }


        async function renderBoostedTokens(tokens) {
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Limpar resultados anteriores
        
            for (const token of tokens) {
                const description = token.description || "No description available";
                const contract = token.tokenAddress || "Unknown contract address";
                const header = token.header || 'https://via.placeholder.com/900x300';
                const price = token.totalAmount ? `$${token.totalAmount}` : "N/A";
        
                let pairData = null;
                let pairDataSubgraph = null;
        
                // Buscar dados dos pares usando o endereço do contrato
                if (contract) {
                    try {
                        const fetchedPairs = await fetchTokenData(contract);
                        if (fetchedPairs && fetchedPairs.length > 0) {
                            pairData = fetchedPairs[0]; // Usar o primeiro par como exemplo
                        }

                       
                        
                    } catch (error) {
                        console.error(`Failed to fetch pair data for contract: ${contract}`, error);
                    }
                }
        
                const name = pairData?.baseToken?.name || description;
                const boots = pairData?.boosts?.active ? pairData?.boosts?.active : 'N/A';
                const pairAddress = pairData.pairAddress || "Unknown pair address";

        
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <img src="${header}" alt="${name}">
                    <h2 class="name">${name}</h2>
                    <div class="price-container">
                        <p class="price">Price: ${price}</p>
                        <p class="price">Boosts: ${boots}</p>  
                    </div> 
                    <div class="card-content">
                        <p class="description">${description.length > 500 ? `${description.substring(0, 500)}...` : description}</p>
                        <span id="expand-btn" class="expand-btn">Expand</span>
                        <p><strong>Contract:</strong> 
                            <a href="https://explorer.solana.com/address/${contract}" target="_blank">
                                ${contract.substring(0, 4)}...${contract.substring(contract.length - 6)}
                            </a>
                        </p>
                        <p><strong>Pairs:</strong> 
                            <a href="https://explorer.solana.com/address/${pairAddress}" target="_blank">
                                ${pairAddress.substring(0, 4)}...${pairAddress.substring(pairAddress.length - 6)}
                            </a>
                        </p>
                        <p><strong>Market Cap:</strong> $${pairData?.marketCap?.toLocaleString() || 'N/A'}</p>
                        <p><strong>FDV:</strong> $${pairData?.fdv?.toLocaleString() || 'N/A'}</p>
                        <p><strong>Liquidity (USD):</strong> $${pairData?.liquidityUSD?.toLocaleString() || 'N/A'}</p>
                        <p><strong>Volume (24h):</strong> $${pairData?.volume24h?.toLocaleString() || 'N/A'}</p>
                        <p><strong>Base Token:</strong> ${pairData?.baseToken?.name || 'N/A'} (${pairData?.baseToken?.symbol || 'N/A'})</p>
                        <p><strong>Quote Token:</strong> ${pairData?.quoteToken?.name || 'N/A'} (${pairData?.quoteToken?.symbol || 'N/A'})</p>

                        <p><strong>Token 0:</strong> ${pairDataSubgraph?.token0.symbol || 'N/A'} (${pairDataSubgraph?.reserve0 || 'N/A'})</p>
                        <p><strong>Token 1:</strong> ${pairDataSubgraph?.token1.symbol || 'N/A'} (${pairDataSubgraph?.reserve1 || 'N/A'})</p>
                        <p><strong>Liquidity (USD):</strong> $${pairDataSubgraph?.liquidityUSD?.toLocaleString() || 'N/A'}</p>
                        <p><strong>Volume (USD):</strong> $${pairDataSubgraph?.volumeUSD?.toLocaleString() || 'N/A'}</p>
                        <p><strong>Token 0 Price:</strong> $${pairDataSubgraph?.token0Price || 'N/A'}</p>
                        <p><strong>Token 1 Price:</strong> $${pairDataSubgraph?.token1Price || 'N/A'}</p>
                    </div>
                    <div class="card-footer">
                        <a href="${pairData?.url || '#'}" target="_blank" class="btn-dexscreener">View on DexScreener</a>
                        <a href="https://explorer.solana.com/address/${contract}" target="_blank" class="btn-contract">Contract</a>
                        ${pairData?.info?.socials?.map(social => `
                            <a href="${social.url}" target="_blank" class="btn-social">
                                <img src="https://icons.getbootstrap.com/icons/${social.type}.svg" alt="${social.type}" class="btn-icon">
                            </a>`).join('')}
                    </div>
                `;
        
                // Funcionalidade para Expandir e Mostrar Modal
                card.querySelector('.expand-btn').addEventListener('click', () => {
                    createModal({
                        title: name,
                        imgSrc: header,
                        description,
                        contractAddress: contract,
                        marketCap: pairData?.marketCap,
                        fdv: pairData?.fdv,
                        liquidityUSD: pairData?.liquidityUSD,
                        volume24h: pairData?.volume24h,
                        baseToken: pairData?.baseToken,
                        quoteToken: pairData?.quoteToken,
                        socials: pairData?.info?.socials || [],
                        websites: pairData?.info?.websites || []
                    });
                });
        
                resultsDiv.appendChild(card);
            }
        }
        

        function createModal({ title, imgSrc, description, contractAddress, socials, websites }) {
            // Remove existing modals
            document.querySelectorAll('.modal, .modal-backdrop').forEach(el => el.remove());
        
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            document.body.appendChild(backdrop);
        
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <button class="close-btn">&times;</button>
                    <h3>${title}</h3>
                    <img src="${imgSrc}" alt="${title}" style="max-width: 100%; border-radius: 10px; margin: 10px 0;">
                    <p>${description}</p>
                    <p><strong>Contract:</strong> 
                        <a href="https://explorer.solana.com/address/${contractAddress}" target="_blank">${contractAddress}</a>
                    </p>
                    <div class="social-links">
                        ${socials.map(social => `
                            <a href="${social.url}" target="_blank">${social.type.toUpperCase()}</a>
                        `).join('')}
                    </div>
                    <div class="website-links">
                        ${websites.map(site => `
                            <p><a href="${site.url}" target="_blank">${site.label}</a></p>
                        `).join('')}
                    </div>
                </div>
            `;
        
            // Close modal
            modal.querySelector('.close-btn').addEventListener('click', () => {
                modal.remove();
                backdrop.remove();
            });
        
            backdrop.addEventListener('click', () => {
                modal.remove();
                backdrop.remove();
            });
        
            document.body.appendChild(modal);
        }
        
        

        function renderSupportContent() {
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 20px;">
                        <!-- Primeira Row -->
                        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px;">
                            <h2>Support</h2>
                            <p>Please refer to the README for more information:</p>
                            <a href="https://github.com/pythinking/dexscreener/blob/main/README.md" target="_blank">Dexscreener README</a>
                        </div>
                        
                        <!-- Segunda Row -->
                        <div style="display: flex; gap: 20px;">
                            <!-- Coluna da esquerda: Console do curl -->
                            <div style="flex: 1; background-color: #1e1e1e; color: #dcdcdc; padding: 15px; border-radius: 8px; font-family: monospace;">
                                <h3 style="color: #ffffff;">Curl Command</h3>
                                <pre id="curlCommand"></pre>
                            </div>
                            
                            <!-- Coluna da direita: JSON Data -->
                            <div style="flex: 1; background-color: #f4f4f4; padding: 15px; border-radius: 8px;">
                                <h3>Generated JSON Data</h3>
                                <pre id="jsonData" style="overflow-x: auto; white-space: pre-wrap;"></pre>
                            </div>
                        </div>
                    </div>
                `;

                // Adicionar o JSON gerado das ações anteriores
                const jsonDataDiv = document.getElementById('jsonData');
                if (tokensData.length > 0) {
                    jsonDataDiv.textContent = JSON.stringify(tokensData, null, 2);
                } else {
                    jsonDataDiv.textContent = 'No data available. Please perform "Market Analyze" or "Memecoins" actions first.';
                }

                // Adicionar o comando curl
                const curlCommandDiv = document.getElementById('curlCommand');
                const exampleEndpoint = "/api/example"; // Substitua com o endpoint real utilizado
                const curlCommand = tokensData.length > 0 
                    ? `curl -X GET "${window.location.origin}${exampleEndpoint}" -H "Accept: application/json"`
                    : 'No endpoint executed yet.';
                curlCommandDiv.textContent = curlCommand;
            }


        function renderTokenProfiles(profiles) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Limpar resultados anteriores

            profiles.forEach(profile => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <img src="${profile.header || 'https://via.placeholder.com/150'}" alt="${profile.description || 'No description'}" style="width: 100%; height: 150px; object-fit: cover;">
                    <h3>${profile.description || 'Unknown Profile'}</h3>
                    <p><strong>Chain:</strong> ${profile.chainId}</p>
                    <p><strong>Token Address:</strong> ${profile.tokenAddress}</p>
                    <div class="card-footer">
                        <a href="${profile.url}" target="_blank">View on DexScreener</a>
                        ${profile.links.map(link => `<a href="${link.url}" target="_blank">${link.label || link.type || 'Link'}</a>`).join(', ')}
                    </div>
                `;
                resultsDiv.appendChild(card);
            });
        }


        function renderMostActiveTokens(activeTokens) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Limpar resultados anteriores

            activeTokens.forEach(token => {
                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <img src="${token.header || 'https://via.placeholder.com/150'}" alt="${token.description || 'No description'}" style="width: 100%; height: 150px; object-fit: cover;">
                    <h3>${token.description || 'No description available'}</h3>
                    <p><strong>Chain:</strong> ${token.chainId}</p>
                    <p><strong>Total Amount:</strong> ${token.totalAmount}</p>
                    <div class="card-footer">
                        <a href="${token.url}" target="_blank">View on DexScreener</a>
                        ${token.links.map(link => `<a href="${link.url}" target="_blank">${link.label || link.type || 'Link'}</a>`).join(', ')}
                    </div>
                `;
                resultsDiv.appendChild(card);
            });
        }



        // Inicializar ação padrão
        actionSelector.dispatchEvent(new Event('change'));
};


        

initializeDashboard();
