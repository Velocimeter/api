require('dotenv').config()

const config = {
  testnet: process.env.TESTNET,

  web3: {
    provider: process.env.PROVIDER,
  },

  tokenLists: process.env.TOKENLISTS.toString().split('|').filter(Boolean),

  weth: {
    name: 'WETH',
    address: '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
    symbol: 'WETH',
    decimals: 18,
    chainId: 42161,
    logoURI: 'https://arbiscan.io/token/images/weth_28.png',
  },
  usdc: {
    name: 'USDC',
    address: '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', // updated to fantom
    symbol: 'USDC',
    decimals: 6,
    chainId: 42161,
    logoURI: 'https://assets.spookyswap.finance/tokens/USDC.png',
  },
  agg: {
    name: 'AGG',
    address: '0x10663b695b8f75647bD3FF0ff609e16D35BbD1eC',
    symbol: 'AGG',
    decimals: 18,
    chainId: 42161,
    logoURI: 'https://assets.spookyswap.finance/tokens/USDC.png',
  },
}

module.exports = config
