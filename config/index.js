require('dotenv').config()

const config = {
  testnet: process.env.TESTNET,

  web3: {
    provider: process.env.PROVIDER
  },

  tokenLists: process.env.TOKENLISTS.toString().split('|').filter(Boolean),

  weth: {
    name: 'DAI',
    address: '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
    symbol: 'DAI',
    decimals: 18,
    chainId: 42161,
    logoURI:
      'https://cryptologos.cc/logos/multi-collateral-dai-dai-logo.svg?v=010'
  },
  usdc: {
    name: 'USDC',
    address: '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', // updated to fantom
    symbol: 'USDC',
    decimals: 6,
    chainId: 42161,
    logoURI: 'https://assets.spookyswap.finance/tokens/USDC.png'
  },
  usdc: {
    name: 'AGG',
    address: '0x10663b695b8f75647bD3FF0ff609e16D35BbD1eC', // updated to fantom
    symbol: 'AGG',
    decimals: 6,
    chainId: 42161,
    logoURI: 'https://assets.spookyswap.finance/tokens/USDC.png'
  }
}

module.exports = config
