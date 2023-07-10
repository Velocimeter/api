# -*- coding: utf-8 -*-

import math
import json

from multicall import Call
from app.fantom_multicall import FantomMulticall as Multicall
from app.token_prices_set import TokenPrices
from walrus import (
    Model,
    TextField,
    IntegerField,
    BooleanField,
    FloatField,
    ListField,
)
from web3.constants import ADDRESS_ZERO

from app.assets import Token
from app.gauges import Gauge
from app.settings import (
    LOGGER,
    CACHE,
    FACTORY_ADDRESS,
    VOTER_ADDRESS,
    DEFAULT_TOKEN_ADDRESS,
    OPTION_TOKEN_ADDRESS,
)


class Pair(Model):
    """Liquidity pool pairs model."""

    __database__ = CACHE

    DAY_IN_SECONDS = 24 * 60 * 60

    address = TextField(primary_key=True)
    symbol = TextField()
    decimals = IntegerField()
    stable = BooleanField()
    total_supply = FloatField()
    reserve0 = FloatField()
    reserve1 = FloatField()
    token0_address = TextField(index=True)
    token1_address = TextField(index=True)
    gauge_address = TextField(index=True)
    tvl = FloatField(default=0)
    aprs = ListField()
    # apr = FloatField(default=0)
    # oblotr_apr = FloatField(default=0)

    # TODO: Backwards compat. Remove once no longer needed...
    isStable = BooleanField()
    totalSupply = FloatField()

    def token_price(self):
        """LP token price.

        Uses: https://blog.alphaventuredao.io/fair-lp-token-pricing/
        """
        token0_price = Token.find(self.token0).chain_price_in_stables()
        token1_price = Token.find(self.token1).chain_price_in_stables()

        if token0_price == 0 or token1_price == 0:
            return 0

        sqrtK = math.sqrt(self.reserve0 * self.reserve1)
        sqrtP = math.sqrt(token0_price * token1_price)

        return 2 * ((sqrtK * sqrtP) / self.totalSupply)

    def syncup_gauge(self):
        """Fetches own gauges data from chain."""
        if self.gauge_address in (ADDRESS_ZERO, None):
            return

        gauge = Gauge.from_chain(self.gauge_address)
        self._update_apr(self.gauge_address)

        return gauge

    def _update_apr(self, gauge_address):
        """Updates the aprs for the pair."""

        rewards_list_lenght_data = Call(
            gauge_address,
            ["rewardsListLength()(uint256)"],
            [["rewards_list_lenght", None]],
        )()

        rewards_data = []

        is_option_emissions = self._is_option_emission(gauge_address)

        for idx in range(0, rewards_list_lenght_data["rewards_list_lenght"]):
            reward_token_addy_call = Call(
                gauge_address,
                ["rewards(uint256)(address)", idx],
                [["reward_token_addy", None]],
            )()
            reward_token_addy = reward_token_addy_call["reward_token_addy"]
            if is_option_emissions and reward_token_addy == DEFAULT_TOKEN_ADDRESS:
                reward_token = Token.find(OPTION_TOKEN_ADDRESS)
            else:
                reward_token = Token.find(reward_token_addy)
            if not TokenPrices.is_in_token_prices_set(reward_token_addy):
                reward_token._update_price()
                TokenPrices.update_token_prices_set(reward_token_addy)

            reward_token_data = Multicall(
                [
                    Call(
                        gauge_address,
                        ["rewardRate(address)(uint256)", reward_token_addy],
                        [["reward_rate", None]],
                    ),
                    Call(
                        gauge_address,
                        ["left(address)(uint256)", reward_token_addy],
                        [["left", None]],
                    ),
                ]
            )()

            if reward_token_data["left"] == 0:
                reward_token_data["reward"] = 0
            else:
                reward_token_data["reward"] = (
                    reward_token_data["reward_rate"]
                    / 10**reward_token.decimals
                    * self.DAY_IN_SECONDS
                )

            data = {**reward_token_data, **reward_token._data}

            rewards_data.append(data)

        aprs = []

        for reward in rewards_data:
            token = Token.find(reward["address"])

            if not TokenPrices.is_in_token_prices_set(token.address):
                token._update_price()
                TokenPrices.update_token_prices_set(token.address)

            underlying_token_address = token.check_if_token_is_option(token.address)
            if underlying_token_address and underlying_token_address != ADDRESS_ZERO:
                discount = token.check_option_discount(token.address)
                ve_discount = token.check_option_ve_discount(token.address)
                # devide 1 / (ve_discount / discount) to get the ratio bc discounts are asian discounts
                ratio = discount / ve_discount
                max_token_price = token.price * ratio

                min_apr = reward["reward"] * (token.price) / self.tvl * 100 * 365
                max_apr = reward["reward"] * (max_token_price) / self.tvl * 100 * 365

                aprs.append(
                    {
                        "symbol": token.symbol,
                        "logo": token.logoURI,
                        "min_apr": min_apr,
                        "max_apr": max_apr,
                    }
                )
            else:
                apr = reward["reward"] * (token.price) / self.tvl * 100 * 365
                aprs.append(
                    {
                        "symbol": token.symbol,
                        "logo": token.logoURI,
                        "apr": apr,
                    }
                )

        for aprDict in aprs:
            self.aprs.append(json.dumps(aprDict))
        print(self.aprs)
        self.save()

    def _is_option_emission(self, gauge_address):
        """Checks if the pool is an option emission pool."""

        minter_role = Call(OPTION_TOKEN_ADDRESS, ["MINTER_ROLE()(bytes32)"])()

        check_data_multicall = Multicall(
            [
                Call(
                    OPTION_TOKEN_ADDRESS,
                    [
                        "hasRole(bytes32,address)(bool)",
                        minter_role,
                        gauge_address,
                    ],
                    [["has_role", None]],
                ),
                Call(
                    gauge_address,
                    ["oFlow()(address)"],
                    [["option", None]],
                ),
            ]
        )

        check_data = check_data_multicall()

        return check_data["has_role"] and check_data["option"] != ADDRESS_ZERO

    @classmethod
    def find(cls, address):
        """Loads a token from cache, of from chain if not found."""
        if address is None:
            return None

        try:
            return cls.load(address.lower())
        except KeyError:
            return cls.from_chain(address.lower())

    @classmethod
    def chain_addresses(cls):
        """Fetches pairs/pools from chain."""
        pairs_count = Call(FACTORY_ADDRESS, "allPairsLength()(uint256)")()
        # arr = []
        # for idx in range(0, pairs_count):
        #     arr.append(Call(FACTORY_ADDRESS, ['allPairs(uint256)(address)', idx])())

        pairs_multi = Multicall(
            [
                Call(
                    FACTORY_ADDRESS, ["allPairs(uint256)(address)", idx], [[idx, None]]
                )
                for idx in range(0, pairs_count)
            ]
        )

        return list(pairs_multi().values())

    @classmethod
    def from_chain(cls, address):
        """Fetches pair/pool data from chain."""
        address = address.lower()

        pair_multi = Multicall(
            [
                Call(
                    address,
                    "getReserves()(uint256,uint256)",
                    [["reserve0", None], ["reserve1", None]],
                ),
                Call(address, "token0()(address)", [["token0_address", None]]),
                Call(address, "token1()(address)", [["token1_address", None]]),
                Call(address, "totalSupply()(uint256)", [["total_supply", None]]),
                Call(address, "symbol()(string)", [["symbol", None]]),
                Call(address, "decimals()(uint8)", [["decimals", None]]),
                Call(address, "stable()(bool)", [["stable", None]]),
                Call(
                    VOTER_ADDRESS,
                    ["gauges(address)(address)", address],
                    [["gauge_address", None]],
                ),
            ]
        )

        data = pair_multi()

        data["address"] = address
        data["total_supply"] = data["total_supply"] / (10 ** data["decimals"])

        _token0 = Token.find(data["token0_address"])
        if not TokenPrices.is_in_token_prices_set(_token0.address):
            _token0._update_price()
            TokenPrices.update_token_prices_set(_token0.address)

        _token1 = Token.find(data["token1_address"])
        if not TokenPrices.is_in_token_prices_set(_token1.address):
            _token1._update_price()
            TokenPrices.update_token_prices_set(_token1.address)

        token0 = _token0
        token1 = _token1

        data["reserve0"] = data["reserve0"] / (10**token0.decimals)
        data["reserve1"] = data["reserve1"] / (10**token1.decimals)

        if data.get("gauge_address") in (ADDRESS_ZERO, None):
            data["gauge_address"] = None
        else:
            data["gauge_address"] = data["gauge_address"].lower()

        data["tvl"] = cls._tvl(data, token0, token1)

        # TODO: Remove once no longer needed...
        data["isStable"] = data["stable"]
        data["totalSupply"] = data["total_supply"]

        # Cleanup old data...
        cls.query_delete(cls.address == address.lower())

        pair = cls.create(**data)
        LOGGER.debug("Fetched %s:%s.", cls.__name__, pair.address)

        pair.syncup_gauge()

        return pair

    @classmethod
    def _tvl(cls, pool_data, token0, token1):
        """Returns the TVL of the pool."""
        tvl = 0

        if token0.price and token0.price != 0:
            tvl += pool_data["reserve0"] * token0.price

        if token1.price and token1.price != 0:
            tvl += pool_data["reserve1"] * token1.price

        if tvl != 0 and (token0.price == 0 or token1.price == 0):
            tvl = tvl * 2

        return tvl
