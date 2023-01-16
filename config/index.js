require('dotenv').config()

const config = {
  testnet: process.env.TESTNET,

  web3: {
    provider: process.env.PROVIDER
  },

  tokenLists: process.env.TOKENLISTS.toString().split('|').filter(Boolean),

  weth: {
    chainId: 10,
    name: 'Wrapped ETH',
    symbol: 'WETH',
    address: '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83', // updated to fantom
    decimals: 18,
    logoURI: 'https://weth.io/img/weth_favi.png'
  },
  usdc: {
    chainId: 10,
    name: 'USD Coin',
    symbol: 'USDC',
    address: '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75', // updated to fantom
    decimals: 6,
    logoURI: 'https://assets.spookyswap.finance/tokens/USDC.png'
  }
}

module.exports = config
