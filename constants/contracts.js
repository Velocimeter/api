const abis = require('./abis')

module.exports.FACTORY_ADDRESS = '0xA2db791281CdeeBb1EEDc78a34989df2Bfd479bE'
module.exports.FACTORY_ABI = abis.factoryABI

module.exports.ROUTER_ADDRESS = '0x07d2FCFa095d52652cBC664F105F2d9Fb3799a47'
module.exports.ROUTER_ABI = abis.routerABI

module.exports.GAUGES_ADDRESS = '0x29C487a354D11315059204Df4F7d8AB1aa008ebb' // apparently this has to be the voter contract not gauge WTF
module.exports.GAUGES_ABI = abis.gaugesABI

module.exports.ERC20_ABI = abis.erc20ABI
module.exports.PAIR_ABI = abis.pairABI
module.exports.GAUGE_ABI = abis.gaugeABI
module.exports.BRIBE_ABI = abis.bribeABI
module.exports.TOKEN_ABI = abis.tokenABI

module.exports.MULTICALL_ADDRESS = '0xcA11bde05977b3631167028862bE2a173976CA11' // WTF is this and how do we make it work??
// 0x2DC0E2aa608532Da689e89e237dF582B783E552C

//remember to update multicall also in front end
