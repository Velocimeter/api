# -*- coding: utf-8 -*-
from typing import List, Optional, Dict

from web3 import Web3

from multicall import Call, Multicall
from multicall.constants import GAS_LIMIT, MULTICALL3_ADDRESSES, w3
from multicall.utils import chain_id

# i need to extend constants to add the multicall address for my network and override MultiCall class to use my multicall address

GNOSIS_MULTICALL3_ADDRESS: Dict[int, str] = {
    100: "0xca11bde05977b3631167028862be2a173976ca11",
}

UPDATED_MULTICALL3_ADDRESSES = {**MULTICALL3_ADDRESSES, **GNOSIS_MULTICALL3_ADDRESS}


class GnosisMulticall(Multicall):
    def __init__(
        self,
        calls: List[Call],
        block_id: Optional[int] = None,
        require_success: bool = True,
        gas_limit: int = GAS_LIMIT,
        _w3: Web3 = w3,
    ) -> None:
        self.calls = calls
        self.block_id = block_id
        self.require_success = require_success
        self.gas_limit = gas_limit
        self.w3 = _w3
        self.chainid = chain_id(self.w3)
        if require_success is True:
            multicall_map = (
                MULTICALL3_ADDRESSES
                if self.chainid in MULTICALL3_ADDRESSES
                else UPDATED_MULTICALL3_ADDRESSES
            )
            self.multicall_sig = "aggregate((address,bytes)[])(uint256,bytes[])"
        else:
            multicall_map = (
                MULTICALL3_ADDRESSES
                if self.chainid in MULTICALL3_ADDRESSES
                else UPDATED_MULTICALL3_ADDRESSES
            )
            self.multicall_sig = "tryBlockAndAggregate(bool,(address,bytes)[])(uint256,uint256,(bool,bytes)[])"
        self.multicall_address = multicall_map[self.chainid]
