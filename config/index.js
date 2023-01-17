require("dotenv").config();

const config = {
  testnet: process.env.TESTNET,

  web3: {
    provider: process.env.PROVIDER,
  },

  tokenLists: process.env.TOKENLISTS.toString().split("|").filter(Boolean),

  weth: {
    name: "FAKE DAI",
    address: "0xE65A051E0ae02eB66a11c73B2BA14021B5aadAEE",
    symbol: "DAI",
    decimals: 18,
    chainId: 421613,
    logoURI:
      "https://cryptologos.cc/logos/multi-collateral-dai-dai-logo.svg?v=010",
  },
  usdc: {
    name: "FAKE USD Coin",
    address: "0x658e6B62e7ab1d2B29a08F85f8442edEed562b48", // updated to fantom
    symbol: "USDC",
    decimals: 6,
    chainId: 421613,
    logoURI: "https://assets.spookyswap.finance/tokens/USDC.png",
  },
};

module.exports = config;
