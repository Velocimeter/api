# -*- coding: utf-8 -*-
from multicall import Call
from app.fantom_multicall import FantomMulticall as Multicall

from app.settings import (
    LOGGER,
    VOTER_ADDRESS,
)


class KilledGaugesStore:
    """Saves killed gauges addresses"""

    killedGauges = []

    @classmethod
    def killed_gauges(cls, pair_address):
        """Returns list of killed gauges for pair if any"""
        result = []
        for killed_gauge in cls.killedGauges:
            if killed_gauge["pair_address"] == pair_address:
                result.append(killed_gauge["gauge_address"])
        if len(result) == 0:
            return False
        return result

    @classmethod
    def update_killed_gauges_list(cls):
        """Updates all killed gauges addresses and pairs for it"""
        dead_gauges_count = Call(VOTER_ADDRESS, "killedGaugesLength()(uint256)")()

        dead_gauges_multi = Multicall(
            [
                Call(
                    VOTER_ADDRESS,
                    ["killedGauges(uint256)(address)", idx],
                    [[idx, None]],
                )
                for idx in range(0, dead_gauges_count)
            ]
        )

        dead_gauges_addresses = list(dead_gauges_multi().values())

        pairs_of_killed_gauges_calls = []

        for dead_gauge_address in dead_gauges_addresses:
            pairs_of_killed_gauges_calls.append(
                Call(dead_gauge_address, ["stake()(address)"], [["pair", None]])
            )

        pairs_of_killed_gauges_multi = Multicall(pairs_of_killed_gauges_calls)()

        pairs_of_killed_gauges = list(pairs_of_killed_gauges_multi.values())

        for i, pair in enumerate(pairs_of_killed_gauges):
            if pair is not None:
                result = {
                    "pair_address": pair.lower(),
                    "gauge_address": dead_gauges_addresses[i],
                }
                cls.killedGauges.append(result)

        print("Killed gauges: ", cls.killedGauges)
        LOGGER.info("Got the list of killed gauges")
