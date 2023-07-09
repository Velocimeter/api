# -*- coding: utf-8 -*-
from multicall import Call
from app.fantom_multicall import FantomMulticall as Multicall
from app.token_prices_set import TokenPrices

from web3.constants import ADDRESS_ZERO

from app.assets import Token


class Apr:
    """Apr model."""

    @classmethod
    def calculateAprs(self, pair_address, gauge_address):
        """Loads a gauge from cache, of from chain if not found."""
        if pair_address is None or gauge_address is None:
            return None

        return self.from_chain(pair_address, gauge_address)

    @classmethod
    def from_chain(self, pair_address, gauge_address):
        """Fetches pair/pool gauge data from chain."""
        gauge_address = gauge_address.lower()

        rewards_list_lenght = Call(
            gauge_address,
            "rewardsListLength()(uint256)",
            [["rewards_list_lenght"], None],
        )()

        rewards_data = []

        for idx in range(0, rewards_list_lenght):
            reward_token_addy = Call(
                gauge_address,
                ["rewards(uint256)(address)", idx],
                [["reward_token_addy"], None],
            )()
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

        aprsCaclculated = self._update_apr(rewards_data, pair_address)

        return aprsCaclculated

    @classmethod
    def _update_apr(self, rewards_data, pair_address):
        """Updates the aprs for the pair."""
        # Avoid circular import...
        from app.pairs.model import Pair

        pair = Pair.get(Pair.address == pair_address)

        aprs = []

        for reward in rewards_data:
            token = Token.find(reward["address"])

            if not TokenPrices.is_in_token_prices_set(token.address):
                token._update_price()
                TokenPrices.update_token_prices_set(token.address)

            underlying_token_address = token.check_if_token_is_option()
            if underlying_token_address and underlying_token_address != ADDRESS_ZERO:
                discount = token.check_option_discount()
                ve_discount = token.check_option_ve_discount()
                ratio = ve_discount / discount
                max_token_price = token.price * ratio

                min_apr = reward["reward"] * (token.price) / pair.tvl * 100 * 365
                max_apr = reward["reward"] * (max_token_price) / pair.tvl * 100 * 365

                aprs.append(
                    {
                        "symbol": token.symbol,
                        "logo": token.logoURI,
                        "min_apr": min_apr,
                        "max_apr": max_apr,
                    }
                )
            apr = reward["reward"] * (token.price) / pair.tvl * 100 * 365
            aprs.append(
                {
                    "symbol": token.symbol,
                    "logo": token.logoURI,
                    "apr": apr,
                }
            )

        return aprs
